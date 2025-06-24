# Import necessary modules and classes
from elasticsearch_dsl import Q
from itertools import chain
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from ..models import *  
from ..serializers import *  
from django.db.models import Q as modelsQ
from django.db.models import F
import concurrent.futures
from ..Views.sitemap_view import CC_Check_and_add_metadata
from ..Tools_Utils.utils import *
from .e_search_documents import *
from bAdmin.serializers import *
import itertools
from brandsinfo.settings import COHERE_API_KEYS


from sarvamai import SarvamAI
from brandsinfo.settings import SARVAM_API_KEY
import ast
import cohere


api_key_cycle = itertools.cycle(COHERE_API_KEYS)

co = cohere.Client(api_key=next(api_key_cycle))


MAGENTA = "\033[95m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"
WHITE = "\033[97m"
RESET = "\033[0m"


def print_queryset(label, queryset, color):
    print(f'\n\n\n{color}{label}{RESET}\n\n\n')
    for doc in queryset:
        # If using Django queryset wrapped from Elasticsearch, access `meta.id` for document ID
        try:
            print(f"{color}ID: {doc.meta.id}, Source: {doc.to_dict()}{RESET}")
        except Exception as e:
            print(f"{color}[Error reading doc: {e}]{RESET}")






client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


COHERE_API_KEY = "yOEglpyAXjyljpPkCXdK6dQjf7aBsoxMEUWUYLWp"  # Replace with your actual key

co = cohere.Client(api_key=COHERE_API_KEY)



    # Your task:
    # - Return only the indexes of groups that are **highly relevant** to the **semantic intent** of the user’s query.
    # - Exclude matches that are only **partially related**, **contextually different**, or belong to **different domains**.
    # - Retain only results that directly and clearly relate to the **core meaning** and **domain context** of the query.
    # - Avoid matches that only share similar words but do not fulfill the same **intent** as the query.

import json
import time

def call_cohere_filter_api(matched_phrases, query):
    prompt = f"""
        You are an intelligent filtering AI.

        The user has searched for: "{query}"

        You are given a list of matched phrase groups. Each group contains phrases (strings) that matched with the query. Your task is to:

        - Return a list of indexes (0-based) of groups that are **truly related** to the query’s meaning and real-world intent.
        - Reject groups that:
        - Share generic structure (e.g., 'service', 'consultant') but belong to unrelated domains.
        - Have keyword overlap but serve different real-world needs.

        Here are the matched phrase groups:
        {json.dumps(matched_phrases, indent=2)}

        Only output a valid JSON list like: [0, 2, 4]
        Do not explain. Just return the list.
        """

    for attempt in range(3):
        try:
            response = co.chat(
                model="command-a-03-2025",
                message=prompt,
                temperature=0.3,  # low temp = precise selection
                max_tokens=100,
            )

            raw_output = response.text.strip()
            print("Cohere raw output:", raw_output)

            json_start = raw_output.find("[")
            json_end = raw_output.rfind("]")
            if json_start == -1 or json_end == -1:
                raise ValueError("Missing brackets for list in response.")

            json_text = raw_output[json_start:json_end + 1]
            parsed_indexes = json.loads(json_text)

            if not isinstance(parsed_indexes, list) or not all(isinstance(i, int) for i in parsed_indexes):
                raise ValueError("Returned value is not a list of integers.")

            return parsed_indexes

        except Exception as e:
            print(f"[Attempt {attempt + 1}] Error calling Cohere filter:", e)
            time.sleep(0.5)

    return []



def call_sarvam_filter_api(matched_phrases, query):
    prompt = f"""
        You are an intelligent filter tasked with identifying groups that are semantically aligned with the user's search query.

        Given:
        - A list of result groups, each with:
            - doc_type
            - id
            - matched_text: list of snippets that matched the query
        - The user's search query: "{query}"

        Your task:
        - Return only the indexes of groups where the **matched_text belongs to the same semantic domain and real-world context** as the query.
        - Reject groups that:
            - Share generic structure or words (like "consultant", "service", etc.) but differ in **topic/domain**.
            - Match partially but belong to **unrelated areas of application or user intent**.

        Here are the matched texts:  
        {matched_phrases}

        Respond with a list of integer indexes only.
        """
    try:
        response = client.chat.completions(
            messages=[
                {"role": "system", "content": "You're a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return ast.literal_eval(response.choices[0].message.content)

    except Exception as e:
        print("Error communicating with Sarvam AI:", e)
        return []






def retrieve_es_matches(query):
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["name", "category", "keywords"], fuzziness="AUTO", prefix_length=1, minimum_should_match="1<75%"),
        Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO", prefix_length=1, minimum_should_match="1<75%")
    ])

    def extract_matches(hits, doc_type):
        results = []
        for hit in hits:
            matched_fields = getattr(hit.meta, "highlight", {})
            matched_terms = []
            for field, fragments in matched_fields.items():
                for fragment in fragments:
                    cleaned = fragment.replace("<em>", "").replace("</em>", "")
                    matched_terms.append(cleaned)
            results.append({
                "doc_type": doc_type,
                "id": hit.meta.id,
                "matched_text": matched_terms
            })
        return results

    product_hits = ProductDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("name", "keywords").execute()
    service_hits = ServiceDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("name", "keywords").execute()
    business_hits = BuisnessDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("name", "keywords").execute()
    bdcats_hits = BDesCatDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("cat_name").execute()
    bgcats_hits = BGenCatDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("cat_name").execute()

    return (
        extract_matches(product_hits, "products") +
        extract_matches(service_hits, "services") +
        extract_matches(business_hits, "businesses") +
        extract_matches(bdcats_hits, "bdcats") +
        extract_matches(bgcats_hits, "bgcats")
    )




def filter_matches_with_ai(all_matches, query):
    def extract_matched_phrases(data):
        return [item.get("matched_text", []) for item in data]

    matched_phrases = extract_matched_phrases(all_matches)
    trimmed = [group[:5] for group in matched_phrases[:50]]

    try:
        ai_response = call_cohere_filter_api(
            matched_phrases=json.dumps(trimmed, ensure_ascii=False),
            query=query
        )
        return ai_response
    except Exception as e:
        print("AI Filtering failed:", e)
        return []




def get_filtered_objects_from_indexes(all_matches, filtered_indexes):
    doc_id_map = {"products": [], "services": [], "businesses": [], "bdcats": [], "bgcats": []}

    for i in filtered_indexes:
        if i < len(all_matches):
            match = all_matches[i]
            doc_type = match.get("doc_type")
            doc_id = match.get("id")
            if doc_type and doc_id:
                doc_id_map[doc_type].append(doc_id)

    return {
        "products": ProductDocument.search().query(Q("ids", values=doc_id_map["products"])).to_queryset(),
        "services": ServiceDocument.search().query(Q("ids", values=doc_id_map["services"])).to_queryset(),
        "businesses": BuisnessDocument.search().query(Q("ids", values=doc_id_map["businesses"])).to_queryset(),
        "bdcats": BDesCatDocument.search().query(Q("ids", values=doc_id_map["bdcats"])).to_queryset(),
        "bgcats": BGenCatDocument.search().query(Q("ids", values=doc_id_map["bgcats"])).to_queryset()
    }






class paginator(PageNumberPagination):
    page_size = 16
    page_size_query_param = 'page_size'
    max_page_size = 1000

class Pageing_assistant:
    def __init__(self,queryset,serializer):
        self.queryset=queryset
        self.serializer=serializer
        self.paginator=paginator()
        
    def get_page(self,request):
        page=self.paginator.paginate_queryset(self.queryset,request)
        if page is not None:
            serializer=self.serializer(page,many=True)
            return self.paginator.get_paginated_response(serializer.data)
        return Response({'error':'No results found'},status=status.HTTP_404_NOT_FOUND)
    









# from .search_resulst_cacher import get_cached_search_response,cache_search_response



from rest_framework.decorators import api_view
from rest_framework.response import Response
from elasticsearch_dsl import Q
from itertools import chain
from django.db.models import Q as modelsQ, F
from django.utils.timezone import localtime
import concurrent.futures

@api_view(['GET'])
def elasticsearch2(request):
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')
    verified = request.GET.get('verified', 'False')
    assured = request.GET.get('assured', 'False')
    rated_high = request.GET.get('rated_high', 'False')
    open_now = request.GET.get('open_now', 'False')

    filters_dict = {
        "assured": assured,
        "verified": verified,
        "rated_high": rated_high,
        "open_now": open_now
    }


    # cached = get_cached_search_response(query, location,filters_dict)
    # if cached:
    #     return cached

    # 2. Run metadata fetch in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_meta = executor.submit(CC_Check_and_add_metadata, location, query)

        # 3. Retrieve ES matches
        all_matches = retrieve_es_matches(query)

        # 4. Filter with AI
        filtered_indexes = filter_matches_with_ai(all_matches, query)

        # 5. Extract final matched objects
        filtered_objects = get_filtered_objects_from_indexes(all_matches, filtered_indexes)

        # 6. Fetch business location object
        try:
            city_obj = City.objects.get(city_name=location)
        except City.DoesNotExist:
            return Response(f'Sorry, we don’t have results for {location}')

        # 7. Gather and filter businesses
        products = filtered_objects['products']
        services = filtered_objects['services']
        buisnesses_direct = filtered_objects['businesses'].filter(city=city_obj)
        bdcats = filtered_objects['bdcats']
        bgcats = filtered_objects['bgcats']

        # Update search count
        if products.exists():
            executor.submit(update_search_count_products, products)
        if services.exists():
            executor.submit(update_search_count_services, services)

        product_buisness_ids = products.values_list('buisness', flat=True).distinct()
        service_buisness_ids = services.values_list('buisness', flat=True).distinct()
        bdcats_buisness_ids = bdcats.values_list('buisness', flat=True).distinct()
        bgcats_buisness_ids = bgcats.values_list('buisness', flat=True).distinct()

        unique_buisness_ids = set(chain(
            product_buisness_ids,
            service_buisness_ids,
            bdcats_buisness_ids,
            bgcats_buisness_ids
        ))

        buisnesses = Buisnesses.objects.filter(id__in=unique_buisness_ids, city=city_obj)

        # Apply filters
        filters = modelsQ()
        if assured == 'True':
            filters &= modelsQ(assured=True)
        if verified == 'True':
            filters &= modelsQ(verified=True)
        if open_now == 'True':
            now = localtime()
            filters &= (
                modelsQ(opens_at__lte=now, closes_at__gte=now) |
                modelsQ(opens_at__gt=F('closes_at'), opens_at__lte=now) |
                modelsQ(opens_at__gt=F('closes_at'), closes_at__gte=now)
            )

        buisnesses = buisnesses.filter(filters)
        buisnesses_direct = buisnesses_direct.filter(filters)

        # Merge and sort
        combined_queryset = list(chain(buisnesses_direct, buisnesses))
        executor.submit(update_search_count_buisnesses, combined_queryset)

        unique_combined_queryset = list(set(combined_queryset))
        unique_combined_queryset = sorted(
            unique_combined_queryset,
            key=lambda x: (x.search_priority, x.rating if rated_high == 'True' else 0),
            reverse=True
        )

        # Pagination + metadata
        pageing_assistant = Pageing_assistant(unique_combined_queryset, BuisnessesSerializerMini)
        response = pageing_assistant.get_page(request)
        response.data['metadata'] = future_meta.result()

        # 8. Cache the response
        # cache_search_response(query, location,filters_dict, response.data)

        return response




















































# from .search_resulst_cacher import get_cached_search_response,cache_search_response

# @api_view(['GET'])
# def elasticsearch2(request):
#     print(f"\033[96m{['-'  for i in range(0,100)]}\033[0m")

#     query       = request.GET.get('q', '')
#     location    = request.GET.get('location', '')
#     verified    = request.GET.get('verified' , 'False')
#     assured     = request.GET.get('assured' , 'False')
#     rated_high  = request.GET.get('rated_high' , 'False')
#     open_now    = request.GET.get('open_now' , 'False')


#     response = get_cached_search_response(query, location) 
#     cache_search_response(query, location, fresh_data.data)  # Cache it
 

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_cc_meta = executor.submit(CC_Check_and_add_metadata , location , query)

#         search_query = Q("bool", should=[
#             Q("multi_match",
#             query=query,
#             fields=["name", "category", "keywords"],
#             fuzziness="AUTO",
#             prefix_length=1,
#             minimum_should_match="1<75%"
#             ),
#             Q("multi_match",
#             query=query,
#             fields=["cat_name"],
#             fuzziness="AUTO",
#             prefix_length=1,
#             minimum_should_match="1<75%")
#         ])

#         try:
#             city_obj = City.objects.get(city_name=location)
#         except City.DoesNotExist:
#             return Response(f'Sorry, we dont have any results for {location} city')

#         product_hits = ProductDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("name", "keywords").execute()
#         service_hits = ServiceDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("name", "keywords").execute()
#         business_hits = BuisnessDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("name", "keywords").execute()
#         bdcats_hits = BDesCatDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("cat_name").execute()
#         bgcats_hits = BGenCatDocument.search().query(search_query).highlight_options(pre_tags="<em>", post_tags="</em>").highlight("cat_name").execute()

#         def extract_matches(hits, doc_type):
#             results = []
#             for hit in hits:
#                 matched_fields = getattr(hit.meta, "highlight", {})
#                 matched_terms = []
#                 for field, fragments in matched_fields.items():
#                     for fragment in fragments:
#                         cleaned = fragment.replace("<em>", "").replace("</em>", "")
#                         matched_terms.append(cleaned)
#                 results.append({
#                     "doc_type": doc_type,
#                     "id": hit.meta.id,
#                     "matched_text": matched_terms
#                 })
#             return results

#         def extract_matched_phrases(data):
#             return [item.get("matched_text", []) for item in data]

#         matches_product = extract_matches(product_hits, "products")
#         matches_service = extract_matches(service_hits, "services")
#         matches_business = extract_matches(business_hits, "businesses")
#         matches_bdcat = extract_matches(bdcats_hits, "bdcats")
#         matches_bgcat = extract_matches(bgcats_hits, "bgcats")

#         print(f"{CYAN}matches_product{RESET}", matches_product)
#         print(f"{YELLOW}matches_service{RESET}", matches_service)
#         print(f"{GREEN}matches_business{RESET}", matches_business)
#         print(f"{BLUE}matches_bdcat{RESET}", matches_bdcat)
#         print(f"{MAGENTA}matches_bgcat{RESET}", matches_bgcat)

#         all_matches = matches_product + matches_service + matches_business + matches_bdcat + matches_bgcat

#         matched_phrases = extract_matched_phrases(all_matches)

#         # Limit length before passing to Sarvam
#         MAX_GROUPS = 50
#         MAX_PHRASES_PER_GROUP = 5
#         trimmed_phrases = [group[:MAX_PHRASES_PER_GROUP] for group in matched_phrases[:MAX_GROUPS]]

#         import json
#         try:
#             # sarvam_response = call_sarvam_filter_api(
#             #     matched_phrases=json.dumps(trimmed_phrases, ensure_ascii=False),
#             #     query=query
#             # )
#             sarvam_response = call_cohere_filter_api(
#                 matched_phrases=json.dumps(trimmed_phrases, ensure_ascii=False),
#                 query=query
#             )
#         except Exception as e:
#             print("Error communicating with Sarvam AI:", str(e))
#             sarvam_response = []

#         print("response list from sarvam", sarvam_response)

#         valid_indexes = [i for i in sarvam_response if i < len(all_matches)]

#         for i in valid_indexes:
#             print(i)
#             print(all_matches[i])

#         doc_id_map = {"products": [], "services": [], "businesses": [], "bdcats": [], "bgcats": []}
#         for i in valid_indexes:
#             match = all_matches[i]
#             doc_type = match.get("doc_type")
#             doc_id = match.get("id")
#             if doc_type and doc_id:
#                 doc_id_map[doc_type].append(doc_id)

#         print("Filtered IDs per document:")
#         for k, v in doc_id_map.items():
#             print(f"{k}: {v}")

#         products = ProductDocument.search().query(Q("ids", values=doc_id_map["products"])).to_queryset()
#         services = ServiceDocument.search().query(Q("ids", values=doc_id_map["services"])).to_queryset()
#         buisnesses_direct = BuisnessDocument.search().query(Q("ids", values=doc_id_map["businesses"])).to_queryset()
#         bdcats = BDesCatDocument.search().query(Q("ids", values=doc_id_map["bdcats"])).to_queryset()
#         bgcats = BGenCatDocument.search().query(Q("ids", values=doc_id_map["bgcats"])).to_queryset()

#         print(f"\n\n\n{MAGENTA}keyword{RESET}\n\n\n")
#         print(f'{MAGENTA}keyword:{query}{RESET}')
#         print(f'\n\n\n{CYAN}products{RESET}\n\n\n')
#         print(f'{CYAN}products:{products}{RESET}')
#         print(f'\n\n\n{YELLOW}services{RESET}\n\n\n')
#         print(f'{YELLOW}services:{services}{RESET}')
#         print(f'\n\n\n{GREEN}b_direct{RESET}\n\n\n')
#         print(f'{GREEN}b_direct:{buisnesses_direct}{RESET}')
#         print(f'\n\n\n{BLUE}bdcats{RESET}\n\n\n')
#         print(f'{BLUE}bdcats:{bdcats}{RESET}')
#         print(f'\n\n\n{RED}bgcats{RESET}\n\n\n')
#         print(f'{RED}bgcats:{bgcats}{RESET}')

#         if products.count() != 0:
#             executor.submit(update_search_count_products, products)
#         if services.count() != 0:
#             executor.submit(update_search_count_services, services)

#         product_buisness_ids = products.values_list('buisness', flat=True).distinct()
#         service_buisness_ids = services.values_list('buisness', flat=True).distinct()
#         bdcats_buisness_ids = bdcats.values_list('buisness', flat=True).distinct()
#         bgcats_buisness_ids = bgcats.values_list('buisness', flat=True).distinct()

#         unique_buisness_ids = set(chain(
#             product_buisness_ids,
#             service_buisness_ids,
#             bdcats_buisness_ids,
#             bgcats_buisness_ids
#         ))

#         buisnesses = Buisnesses.objects.filter(id__in=unique_buisness_ids, city=city_obj)
#         buisnesses_direct = buisnesses_direct.filter(city=city_obj)

#         print(f'\n\n\n{CYAN}buisness filtered by city{RESET}\n\n\n')
#         print('buisnesses filtered by city', buisnesses)
#         print(f'\n\n\n{CYAN}buisness from buisness direct filtered by city{RESET}\n\n\n')
#         print('buisnesses from buisness direct filtered by city', buisnesses_direct)

#         filters = modelsQ()
#         if assured == 'True':
#             print('assured filter applied')
#             filters &= modelsQ(assured=True)
#         if verified == 'True':
#             print('verified filter applied')
#             filters &= modelsQ(verified=True)
#         if open_now == 'True':
#             print('open_now filter applied')
#             now = localtime()
#             filters &= (
#                 modelsQ(opens_at__lte=now, closes_at__gte=now) |
#                 modelsQ(opens_at__gt=F('closes_at'), opens_at__lte=now) |
#                 modelsQ(opens_at__gt=F('closes_at'), closes_at__gte=now)
#             )

#         buisnesses = buisnesses.filter(filters)
#         buisnesses_direct = buisnesses_direct.filter(filters)

#         print('\n\n\nbuisness after final filter\n\n\n')
#         print('buisnesses after final filter', buisnesses)
#         print('\n\n\nbuisnesses from buisness direct after final filter\n\n\n')
#         print('buisnesses from buisness direct after final filter', buisnesses_direct)

#         combined_queryset = list(chain(buisnesses_direct, buisnesses))
#         executor.submit(update_search_count_buisnesses, combined_queryset)

#         unique_combined_queryset = list(set(combined_queryset))
#         unique_combined_queryset = sorted(
#             unique_combined_queryset,
#             key=lambda x: x.search_priority,
#             reverse=True
#         )

#         if rated_high == 'True':
#             unique_combined_queryset = sorted(
#                 unique_combined_queryset,
#                 key=lambda x: (x.search_priority, x.rating),
#                 reverse=True
#             )

#         pageing_assistant = Pageing_assistant(unique_combined_queryset, BuisnessesSerializerMini)
#         metadata = future_cc_meta.result()
#         response = pageing_assistant.get_page(request)
#         response.data['metadata'] = metadata
#         return response






























































































































































# @api_view(['GET'])
# def elasticsearch2(request):    

#     print(f"\033[96m{["-"  for i in range(0,100)]}\033[0m")


#     query       = request.GET.get('q', '')
#     location    = request.GET.get('location', '')
#     verified    = request.GET.get('verified' , 'False')
#     assured     = request.GET.get('assured' , 'False')
#     rated_high  = request.GET.get('rated_high' , 'False')
#     open_now    = request.GET.get('open_now' , 'False')


#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_cc_meta = executor.submit(CC_Check_and_add_metadata , location , query)
        
#         # search_query = Q("bool", should=[
#         #     Q("multi_match", query=query, fields=["name", "category" ,"keywords"], fuzziness ="1", max_expansions=3, prefix_length=2,minimum_should_match=2),
#         #     Q("multi_match", query=query, fields=["cat_name"], max_expansions=3,fuzziness ="1", prefix_length=2 ,minimum_should_match=2)
#         # ])
        
#         # search_query = Q("bool", should=[
#         #     Q("multi_match", query=query, fields=["name", "category" ,"keywords"], fuzziness="2", max_expansions=3, prefix_length=2,minimum_should_match = 2), 
#         #     Q("multi_match", query=query, fields=["cat_name"], fuzziness="2", max_expansions=3, prefix_length=2 ,minimum_should_match=2)
#         # ])

#         search_query = Q("bool", should=[
#             Q("multi_match", query=query, fields=["cat_name"], type="phrase", boost=3),  # strong boost if cat_name matches exactly
#             Q("multi_match", query=query, fields=["name^3", "category^2", "keywords"], fuzziness="1", max_expansions=1, prefix_length=2, minimum_should_match="2<75%")
#         ], minimum_should_match=1)

#         # loose_biz_query = Q("bool", should=[
#         #     Q("multi_match", query=query, fields=["name"], fuzziness="AUTO", prefix_length=1, boost=2),
#         #     Q("match_phrase_prefix", name={"query": query, "boost": 1}),
#         #     Q("match", name={"query": query, "operator": "or", "boost": 1})
#         # ], minimum_should_match=1)

#         query_tokens = query.lower().split()

#         should_queries = []

#         # --- Name matching (semi-tight prefix-based with light fuzziness)
#         should_queries.append(
#             Q("match_phrase_prefix", name={"query": query, "boost": 3})
#         )
#         should_queries.append(
#             Q("match", name={
#                 "query": query,
#                 "operator": "and",
#                 "fuzziness": "1",
#                 "prefix_length": 1,
#                 "boost": 2
#             })
#         )

#         # --- Keywords matching (only first word of query compared with beginning of keyword)
#         if query_tokens:
#             first_token = query_tokens[0]

#             should_queries.append(
#                 Q("match_phrase_prefix", keywords={
#                     "query": first_token,
#                     "boost": 3
#                 })
#             )

#             should_queries.append(
#                 Q("match", keywords={
#                     "query": first_token,
#                     "fuzziness": "1",
#                     "operator": "and",
#                     "prefix_length": 1,
#                     "boost": 2
#                 })
#             )

#         # --- Final assembled query
#         loose_biz_query = Q("bool", should=should_queries, minimum_should_match=1)



#         clean_tokens = [word for word in query.split() if len(word) > 3]

#         search_query_for_BD = Q("multi_match" , query=" ".join(clean_tokens) , fields=["name","keywords"]  , prefix_length=3 ,minimum_should_match=2)

#         try:
#             city_obj = City.objects.get(city_name=location)
#         except City.DoesNotExist:
#             return Response(f'Sorry, we dont have any results for {location} city')

    
#         products = ProductDocument.search().query(search_query).to_queryset()
#         services = ServiceDocument.search().query(search_query).to_queryset()
#         buisnesses_direct = BuisnessDocument.search().query(loose_biz_query)
#         bdcats = BDesCatDocument.search().query(search_query).to_queryset()
#         bgcats = BGenCatDocument.search().query(search_query).to_queryset()
        

#         if products.count()!=0:
#             executor.submit(update_search_count_products , products)
#         if services.count()!=0:
#             executor.submit(update_search_count_services , services)

      
#         # Define ANSI color codes
#         MAGENTA = "\033[95m"
#         CYAN = "\033[96m"
#         YELLOW = "\033[93m"
#         GREEN = "\033[92m"
#         BLUE = "\033[94m"
#         RED = "\033[91m"
#         WHITE = "\033[97m"
#         RESET = "\033[0m"

        
#         # print_queryset("b_direct", buisnesses_direct, GREEN)
#         buisnesses_direct = buisnesses_direct.to_queryset()
        
        

#         # Keyword - MAGENTA
#         print(f'\n\n\n{MAGENTA}keyword{RESET}\n\n\n')
#         print(f'{MAGENTA}keyword:{query}{RESET}')

#         # Products - CYAN
#         print(f'\n\n\n{CYAN}products{RESET}\n\n\n')
#         print(f'{CYAN}products:{products}{RESET}')

#         # Services - YELLOW
#         print(f'\n\n\n{YELLOW}services{RESET}\n\n\n')
#         print(f'{YELLOW}services:{services}{RESET}')

#         # b_direct - GREEN
#         print(f'\n\n\n{GREEN}b_direct{RESET}\n\n\n')
#         print(f'{GREEN}b_direct:{buisnesses_direct}{RESET}')

#         # bdcats - BLUE
#         print(f'\n\n\n{BLUE}bdcats{RESET}\n\n\n')
#         print(f'{BLUE}bdcats:{bdcats}{RESET}')

#         # bgcats - RED
#         print(f'\n\n\n{RED}bgcats{RESET}\n\n\n')
#         print(f'{RED}bgcats:{bgcats}{RESET}')


#         product_buisness_ids = products.values_list('buisness', flat=True).distinct()
#         service_buisness_ids = services.values_list('buisness', flat=True).distinct()
#         bdcats_buisness_ids = bdcats.values_list('buisness', flat=True).distinct()
#         bgcats_buisness_ids = bgcats.values_list('buisness', flat=True).distinct()
        
        
        
#         unique_buisness_ids = set(chain(product_buisness_ids, service_buisness_ids, bdcats_buisness_ids,bgcats_buisness_ids))


#         buisnesses = Buisnesses.objects.filter(id__in=unique_buisness_ids, city=city_obj)
#         buisnesses_from_buisness_direct = buisnesses_direct.filter(city =city_obj)




#         print(f'\n\n\n{CYAN}buisness filtered by city{RESET}\n\n\n')
#         print('buisnesses filtered by city',buisnesses)
#         print(f'\n\n\n{YELLOW}buisness filtered by city{RESET}\n\n\n')


#         print(f'\n\n\n{CYAN}buisness from buisness direct before filtered by city{RESET}\n\n\n')
#         print('buisnesses from buisness direct before filtered by city',buisnesses_direct)
#         print(f'\n\n\n{YELLOW}buisness from buisness direct before filtered by city{RESET}\n\n\n')
                

#         print(f'\n\n\n{CYAN}buisness from buisness direct filtered by city{RESET}\n\n\n')
#         print('buisnesses from buisness direct filtered by city',buisnesses_from_buisness_direct)
#         print(f'\n\n\n{YELLOW}buisness from buisness direct filtered by city{RESET}\n\n\n')
        

#         filters = modelsQ()

#         if assured == 'True':
#             print('assured filter applied')
#             filters &= modelsQ(assured=True)

#         if verified == 'True':
#             print('verified filter applied')
#             filters &= modelsQ(verified=True)

#         if open_now == 'True':
#             print('open_now filter applied')
#             now = localtime()
#             print(now)
#             filters &= (
#                 modelsQ(opens_at__lte=now, closes_at__gte=now) |  # Normal case
#                 modelsQ(opens_at__gt=F('closes_at'), opens_at__lte=now) |  # Opens after midnight
#                 modelsQ(opens_at__gt=F('closes_at'), closes_at__gte=now)  # Closes after midnight
#         )
            

#         buisnesses = buisnesses.filter(filters)

        
#         print('\n\n\nbuisness after final filter\n\n\n')
#         print('buisnesses after final filter',buisnesses)
#         print('\n\n\nbuisness after final filter\n\n\n')



#         buisnesses_direct = buisnesses_from_buisness_direct.filter(filters)


         
#         print('\n\n\nbuisnesses from buisness direct after final filter\n\n\n')
#         print('buisnesses from buisnesses direct after final filter',buisnesses_direct)
#         print('\n\n\nbuisnesses from buisness direct after final filter\n\n\n')


        
#         # if buisnesses_direct.count()!=0:
#         #     executor.submit(update_search_count_buisnesses , buisnesses_direct)
#         #     combined_queryset = buisnesses_direct          
#         # else:
#         #     executor.submit(update_search_count_buisnesses , buisnesses)
#         #     combined_queryset = buisnesses
#         #     # executor.submit(update_search_count_buisnesses , buisnesses_direct)

        
#         combined_queryset = list(chain(buisnesses_direct, buisnesses))       #i dont wanted to combine them if data in buisenesses_direct is not empty then i will use it only
#         executor.submit(update_search_count_buisnesses , combined_queryset)
        
        
#         unique_combined_queryset = list(set(combined_queryset)) 
        
      
#         unique_combined_queryset = sorted(
#             unique_combined_queryset, 
#             key=lambda x: (x.search_priority), 
#             reverse=True
#         )

#         if rated_high == 'True':
#              unique_combined_queryset = sorted(
#             unique_combined_queryset, 
#             key=lambda x: (x.search_priority, x.rating), 
#             reverse=True
#             )         

#         pageing_assistant=Pageing_assistant(unique_combined_queryset,BuisnessesSerializerMini)
        
#         metadata = future_cc_meta.result()
#         response = pageing_assistant.get_page(request)
#         response.data['metadata'] = metadata  
#         return response










from rest_framework.decorators import api_view
from rest_framework.response import Response
from elasticsearch_dsl import Q
from itertools import chain

@api_view(['GET'])
def keyword_suggestions_for_major_suggestions(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({"suggestions": []})

    # Construct search query with fuzzy matching
    # search_query = Q("bool", should=[
    #     Q("match", name={"query": query, "fuzziness": "AUTO"},max_expansions=50, prefix_length=2),
    #     Q("match", category={"query": query, "fuzziness": "AUTO"}),
    #     Q("match", cat_name={"query": query, "fuzziness": "AUTO"})
    # ])
    
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["name", "category"], fuzziness="AUTO", max_expansions=20, prefix_length=2),
        Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO", max_expansions=20, prefix_length=2)
    ])
    
    # Fetch matching documents
    product_docs = ProductDocument.search().query(search_query).source(['name']).to_queryset()
    service_docs = ServiceDocument.search().query(search_query).source(['name']).to_queryset()
    business_docs = BuisnessDocument.search().query(search_query).source(['name']).to_queryset()
    bdcats_docs = BDesCatDocument.search().query(search_query).source(['cat_name']).to_queryset()
    print(bdcats_docs)

    # Extract keywords from documents
    keywords = set()
   
    for doc in bdcats_docs:
        keywords.add(doc.dcat.cat_name)
    
    for doc in chain(product_docs, service_docs, business_docs):
        keywords.add(doc.name)
    
  
    return Response({"suggestions": keywords})







class CustomPagination(PageNumberPagination):
    page_size = 10


@api_view(['GET'])
def keyword_suggestions_for_bdcats(request):
    query = request.GET.get('q', '').strip()
    for_admin = request.GET.get('for_admin', '').strip().lower() == 'true'

    if not query:
        return Response({"count": 0, "results": [] if for_admin else {"suggestions": []}})

    # ElasticSearch query
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", cat_name={"query": query})
    ])

    dcats_docs = DesCatDocument.search().query(search_query).source(['cat_name'])[:100]
    ids = [doc.meta.id for doc in dcats_docs if hasattr(doc, 'cat_name')]

    if for_admin:
        # Return paginated + full serializer data
        queryset = Descriptive_cats.objects.filter(id__in=ids)
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = DescriptiveCatsSerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_dcat_count'] = Descriptive_cats.objects.count()
        paginated_response.data['total_gcat_count'] = General_cats.objects.count()
        return paginated_response    
    
    else:
        # Return simple suggestions
        keywords = [{'cat_name': doc.cat_name, 'id': doc.meta.id} for doc in dcats_docs if hasattr(doc, 'cat_name')]
        return Response({"suggestions": keywords})







@api_view(['GET'])
def keyword_suggestions_for_gcats(request):
    query = request.GET.get('q', '').strip()
    for_admin = request.GET.get('for_admin', '').strip().lower() == 'true'

    if not query:
        return Response({"count": 0, "results": [] if for_admin else {"suggestions": []}})

    # ElasticSearch query
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", cat_name={"query": query})
    ])

    gcats_docs = GenCatDocument.search().query(search_query).source(['cat_name'])[:100]
    ids = [doc.meta.id for doc in gcats_docs if hasattr(doc, 'cat_name')]

    if for_admin:
        queryset = General_cats.objects.filter(id__in=ids).annotate(
            dcats_count=Count('descriptive_cats')
        )
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = GeneralCatsSerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_dcat_count'] = Descriptive_cats.objects.count()
        paginated_response.data['total_gcat_count'] = General_cats.objects.count()
        return paginated_response

    else:
        keywords = [{'name': doc.cat_name, 'id': doc.meta.id} for doc in gcats_docs if hasattr(doc, 'cat_name')]
        return Response({"suggestions": keywords})











@api_view(['GET'])
def keyword_suggestions_for_Product_gcats(request):
    query = request.GET.get('q', '').strip()
    for_admin = request.GET.get('for_admin', '').strip().lower() == 'true'

    if not query:
        return Response({"count": 0, "results": [] if for_admin else {"suggestions": []}})

    # ElasticSearch query
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", cat_name={"query": query})
    ])

    gcats_docs = PGeneralCatsDocument.search().query(search_query).source(['cat_name'])[:100]
    ids = [doc.meta.id for doc in gcats_docs if hasattr(doc, 'cat_name')]

    if for_admin:
        queryset = Product_General_category.objects.filter(id__in=ids).annotate(
            dcats_count=Count('subcats')
        )
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = ProductGeneralCatsSerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_dcat_count'] = Product_Sub_category.objects.count()
        paginated_response.data['total_gcat_count'] = Product_General_category.objects.count()
        return paginated_response

    else:
        keywords = [{'name': doc.cat_name, 'id': doc.meta.id} for doc in gcats_docs if hasattr(doc, 'cat_name')]
        return Response({"suggestions": keywords})























@api_view(['GET'])
def keyword_suggestions_for_Product_sub_cats(request):
    query = request.GET.get('q', '').strip()
    for_admin = request.GET.get('for_admin', '').strip().lower() == 'true'

    if not query:
        return Response({"count": 0, "results": [] if for_admin else {"suggestions": []}})

    # ElasticSearch query
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", cat_name={"query": query})
    ])

    dcats_docs = PSubCatsDocument.search().query(search_query).source(['cat_name'])[:100]
    ids = [doc.meta.id for doc in dcats_docs if hasattr(doc, 'cat_name')]

    if for_admin:
        # Return paginated + full serializer data
        queryset = Product_Sub_category.objects.filter(id__in=ids)
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = ProductSubCatsSerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_dcat_count'] = Product_Sub_category.objects.count()
        paginated_response.data['total_gcat_count'] = Product_General_category.objects.count()
        return paginated_response    
    
    else:
        # Return simple suggestions
        keywords = [{'cat_name': doc.cat_name, 'id': doc.meta.id} for doc in dcats_docs if hasattr(doc, 'cat_name')]
        return Response({"suggestions": keywords})









@api_view(['GET'])
def search_users(request):
    query = request.GET.get('q', '').strip()


    # ElasticSearch query
    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["username","first_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", cat_name={"query": query})
    ])

    user_docs = UsersDocument.search().query(search_query).source(['first_name','username'])[:100]
    ids = [doc.meta.id for doc in user_docs if hasattr(doc, 'username')]

   
    queryset = Extended_User.objects.filter(id__in=ids)
    paginator = CustomPagination()
    paginated_qs = paginator.paginate_queryset(queryset, request)
    serializer = UserSerializer(paginated_qs, many=True)
    paginated_response = paginator.get_paginated_response(serializer.data)
    return paginated_response    





from bAdmin.serializers import BuisnessesAdminlistSerializer

@api_view(['GET'])
def search_buisnesses(request):
    query = request.GET.get('q', '').strip()


    # ElasticSearch query
    search_query = Q("multi_match", query=query, fields=["name"], fuzziness="AUTO")

    b_docs = BuisnessDocument.search().query(search_query).source(['name'])[:100]
    ids = [doc.meta.id for doc in b_docs if hasattr(doc, 'name')]

   
    queryset = Buisnesses.objects.filter(id__in=ids)
    paginator = CustomPagination()
    paginated_qs = paginator.paginate_queryset(queryset, request)
    serializer = BuisnessesAdminlistSerializer(paginated_qs, many=True, context={'request': request})
    paginated_response = paginator.get_paginated_response(serializer.data)
    return paginated_response    















@api_view(['GET'])
def keyword_suggestions_for_cities(request):
    query = request.GET.get('q', '').strip()
    for_admin = request.GET.get('for_admin', '').strip().lower() == 'true'

    if not query:
        return Response({"count": 0, "results": [] if for_admin else {"suggestions": []}})

    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["city_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", city_name={"query": query})
    ])

    docs = CityDocument.search().query(search_query).source(['city_name'])[:100]
    ids = [doc.meta.id for doc in docs if hasattr(doc, 'city_name')]

    if for_admin:
        queryset = City.objects.filter(id__in=ids)
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = CitySerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_city_count'] = City.objects.count()
        return paginated_response
    else:
        suggestions = [{'city_name': doc.city_name, 'id': doc.meta.id} for doc in docs]
        return Response({"suggestions": suggestions})


@api_view(['GET'])
def keyword_suggestions_for_localities(request):
    query = request.GET.get('q', '').strip()
    for_admin = request.GET.get('for_admin', '').strip().lower() == 'true'

    if not query:
        return Response({"count": 0, "results": [] if for_admin else {"suggestions": []}})

    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["locality_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", locality_name={"query": query})
    ])

    docs = LocalityDocument.search().query(search_query).source(['locality_name'])[:100]
    ids = [doc.meta.id for doc in docs if hasattr(doc, 'locality_name')]

    if for_admin:
        queryset = Locality.objects.filter(id__in=ids).select_related('city')
        paginator = CustomPagination()
        paginated_qs = paginator.paginate_queryset(queryset, request)
        serializer = LocalitySerializer(paginated_qs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data['total_locality_count'] = Locality.objects.count()
        paginated_response.data['total_city_count'] = City.objects.count()
        return paginated_response
    else:
        suggestions = [{'locality_name': doc.locality_name, 'id': doc.meta.id} for doc in docs]
        return Response({"suggestions": suggestions})






@api_view(['GET'])
def search_cities(request):
    query = request.GET.get('q', '').strip()

    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["city_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", city_name={"query": query})
    ])

    docs = CityDocument.search().query(search_query).source(['city_name'])[:100]
    ids = [doc.meta.id for doc in docs if hasattr(doc, 'city_name')]

    queryset = City.objects.filter(id__in=ids)
    paginator = CustomPagination()
    paginated_qs = paginator.paginate_queryset(queryset, request)
    serializer = CitySerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def search_localities(request):
    query = request.GET.get('q', '').strip()

    search_query = Q("bool", should=[
        Q("multi_match", query=query, fields=["locality_name"], fuzziness="AUTO"),
        Q("match_phrase_prefix", locality_name={"query": query})
    ])

    docs = LocalityDocument.search().query(search_query).source(['locality_name'])[:100]
    ids = [doc.meta.id for doc in docs if hasattr(doc, 'locality_name')]

    queryset = Locality.objects.filter(id__in=ids).select_related('city')
    paginator = CustomPagination()
    paginated_qs = paginator.paginate_queryset(queryset, request)
    serializer = LocalitySerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(serializer.data)
