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
    




from elasticsearch_dsl import Q
from itertools import chain
import concurrent.futures
from django.utils.timezone import localtime
from django.db.models import Q as modelsQ, F
from rest_framework.decorators import api_view
from rest_framework.response import Response
@api_view(['GET'])
def elasticsearch2(request):
    print(f"\033[96m{'-' * 100}\033[0m")

    # ------------------- 1. Query Params -------------------
    query_raw = request.GET.get('q', '')
    location = request.GET.get('location', '')
    verified = request.GET.get('verified', 'False')
    assured = request.GET.get('assured', 'False')
    rated_high = request.GET.get('rated_high', 'False')
    open_now = request.GET.get('open_now', 'False')

    # ------------------- 2. Metadata & City Check -------------------
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_cc_meta = executor.submit(CC_Check_and_add_metadata, location, query_raw)

        try:
            city_obj = City.objects.get(city_name=location)
        except City.DoesNotExist:
            return Response(f'Sorry, we don\'t have any results for {location} city')

        # ------------------- 3. Preprocess Query -------------------
        stopwords = {"the", "a", "an", "and", "of", "on", "at", "in", "for"}
        query = " ".join(word for word in query_raw.split() if word.lower() not in stopwords)

        # ------------------- 4. Strict Search -------------------
        name_query = Q("bool", should=[
            Q("match_phrase", **{"name.raw": {"query": query_raw, "boost": 5}}),
            Q("match", **{"name.raw": {
                "query": query,
                "operator": "and",
                "prefix_length": 2,
                "fuzziness": "AUTO",
                "boost": 3
            }}),
            Q("match", **{"name": {
                "query": query,
                "prefix_length": 1,
                "fuzziness": "AUTO",
                "minimum_should_match": "70%",
                "boost": 2
            }})
        ])
        keywords_query = Q("multi_match", query=query, fields=["keywords"], fuzziness="1", prefix_length=5, minimum_should_match="2<70%")
        name_results = BuisnessDocument.search().query(name_query).highlight("name").execute()

        if name_results:
            print("\033[92mStrict Match Results from Name:\033[0m")
            strict_results = name_results
        else:
            print("\033[93mNo Name Matches. Using Keywords instead:\033[0m")
            strict_results = BuisnessDocument.search().query(keywords_query).highlight("keywords").execute()

        strict_ids = {hit.meta.id for hit in strict_results}

        # ------------------- 5. Relaxed Search -------------------
        relaxed_query = Q("bool", should=[
            Q("match_phrase", name=query),
            Q("multi_match", query=query, fields=["name", "keywords"], minimum_should_match="50%", fuzziness="1", max_expansions=2, prefix_length=2)
        ])
        relaxed_results = BuisnessDocument.search().query(relaxed_query).highlight("name", "keywords").execute()
        relaxed_filtered = [r for r in relaxed_results if r.meta.id not in strict_ids]

        # ------------------- 6. Enrichment -------------------
        def enrich_with_highlights(results, reason):
            enriched = {}
            for r in results:
                matches = []
                if hasattr(r.meta, 'highlight'):
                    matches = list(r.meta.highlight.to_dict().values())
                    matches = [phrase for sublist in matches for phrase in sublist]
                enriched[r.meta.id] = {
                    "matched_phrases": matches,
                    "reason": reason
                }
            return enriched

        strict_enriched = enrich_with_highlights(strict_results, "Exact or near-exact keyword match")
        relaxed_enriched = enrich_with_highlights(relaxed_filtered, "Partial or related keyword match")

        # ------------------- 7. Convert to Querysets -------------------
        strict_queryset = BuisnessDocument.search().filter("ids", values=list(strict_enriched.keys())).to_queryset().filter(city=city_obj)
        relaxed_only_ids = [id for id in relaxed_enriched.keys() if id not in strict_enriched]
        relaxed_queryset = BuisnessDocument.search().filter("ids", values=relaxed_only_ids).to_queryset().filter(city=city_obj)

        # ------------------- 8. Product/Service/Category Search -------------------
        search_query = Q("bool", should=[
            Q("multi_match", query=query, fields=["name", "category"], fuzziness="2", prefix_length=1, minimum_should_match="1<75%"),
            Q("multi_match", query=query, fields=["cat_name"], fuzziness="2", prefix_length=1, minimum_should_match="1<75%")
        ])
        excluded_ids = list(strict_enriched.keys()) + list(relaxed_enriched.keys())
        product_query = ProductDocument.search().query(search_query).exclude("ids", values=excluded_ids).to_queryset()
        service_query = ServiceDocument.search().query(search_query).exclude("ids", values=excluded_ids).to_queryset()
        bdcats = BDesCatDocument.search().query(search_query).exclude("ids", values=excluded_ids).to_queryset()
        bgcats = BGenCatDocument.search().query(search_query).exclude("ids", values=excluded_ids).to_queryset()

        # ------------------- 9. Update Search Counts for Docs -------------------
        if product_query.count() != 0:
            executor.submit(update_search_count_products, product_query)
        if service_query.count() != 0:
            executor.submit(update_search_count_services, service_query)

        # ------------------- 10. Merge Other Businesses (Excluding Duplicates) -------------------
        # Get business IDs from documents
        product_buisness_ids = set(product_query.values_list('buisness', flat=True).distinct())
        service_buisness_ids = set(service_query.values_list('buisness', flat=True).distinct())
        bdcats_buisness_ids = set(bdcats.values_list('buisness', flat=True).distinct())
        bgcats_buisness_ids = set(bgcats.values_list('buisness', flat=True).distinct())

        # Already included in strict and relaxed
        existing_business_ids = set(strict_queryset.values_list('id', flat=True)) | set(relaxed_queryset.values_list('id', flat=True))

        # Filter only new ones
        final_other_biz_ids = (product_buisness_ids | service_buisness_ids | bdcats_buisness_ids | bgcats_buisness_ids) - existing_business_ids

        from_other_docs = Buisnesses.objects.filter(
            id__in=final_other_biz_ids,
            city=city_obj
        )

        # ------------------- 11. Apply Filters -------------------
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

        strict_queryset = strict_queryset.filter(filters)
        relaxed_queryset = relaxed_queryset.filter(filters)
        from_other_docs = from_other_docs.filter(filters)

        # ------------------- 12. Attach Match Info -------------------
        def attach_matched_info(queryset, enriched_dict):
            for obj in queryset:
                matched_data = enriched_dict.get(str(obj.id), {})
                obj.matched_info = matched_data
            return queryset

        strict_queryset = attach_matched_info(strict_queryset, strict_enriched)
        relaxed_queryset = attach_matched_info(relaxed_queryset, relaxed_enriched)

        # ------------------- 13. Sort Results -------------------
        if rated_high == 'True':
            strict_queryset = sorted(strict_queryset, key=lambda x: (x.search_priority, x.rating), reverse=True)
            relaxed_queryset = sorted(relaxed_queryset, key=lambda x: (x.search_priority, x.rating), reverse=True)
            from_other_docs = sorted(from_other_docs, key=lambda x: (x.search_priority, x.rating), reverse=True)
        else:
            strict_queryset = sorted(strict_queryset, key=lambda x: x.search_priority, reverse=True)
            relaxed_queryset = sorted(relaxed_queryset, key=lambda x: x.search_priority, reverse=True)
            from_other_docs = sorted(from_other_docs, key=lambda x: x.search_priority, reverse=True)

        # ------------------- 14. Metadata -------------------
        metadata = future_cc_meta.result()

        # ------------------- 15. Serializer -------------------
        class ExtendedBuisnessSerializerMini(BuisnessesSerializerMini):
            def to_representation(self, instance):
                rep = super().to_representation(instance)
                if hasattr(instance, 'matched_info'):
                    rep['matched_info'] = instance.matched_info
                return rep

        # ------------------- 16. Final Response -------------------
        return Response({
            "metadata": metadata,
            "exact_matches": ExtendedBuisnessSerializerMini(strict_queryset, many=True).data,
            "related_matches": ExtendedBuisnessSerializerMini(relaxed_queryset, many=True).data,
            "others": ExtendedBuisnessSerializerMini(from_other_docs, many=True).data,
        })





# @api_view(['GET'])
# def elasticsearch2(request):    
#     print(f"\033[96m{"-" * 100}\033[0m")

#     query = request.GET.get('q', '')
#     location = request.GET.get('location', '')
#     verified = request.GET.get('verified', 'False')
#     assured = request.GET.get('assured', 'False')
#     rated_high = request.GET.get('rated_high', 'False')
#     open_now = request.GET.get('open_now', 'False')

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future_cc_meta = executor.submit(CC_Check_and_add_metadata, location, query)

#         try:
#             city_obj = City.objects.get(city_name=location)
#         except City.DoesNotExist:
#             return Response(f'Sorry, we don\'t have any results for {location} city')

#         strict_query = Q("multi_match", query=query, fields=["name", "keywords"], minimum_should_match="2<70%", fuzziness="1", max_expansions=2, prefix_length=2)
#         strict_results = BuisnessDocument.search().query(strict_query).highlight("name", "keywords").execute()
#         print("\033[92mStrict Match Results:\033[0m", strict_results)
#         strict_ids = {hit.meta.id for hit in strict_results}

#         relaxed_query = Q("bool", should=[
#             Q("match_phrase", name=query),
#             Q("multi_match", query=query, fields=["name", "keywords"], minimum_should_match="50%", fuzziness="1", max_expansions=2, prefix_length=2)
#         ])
#         relaxed_results = BuisnessDocument.search().query(relaxed_query).highlight("name", "keywords").execute()
#         print("\033[93mRelaxed Match Results:\033[0m", relaxed_results)
#         relaxed_filtered = [r for r in relaxed_results if r.meta.id not in strict_ids]

#         def enrich_with_highlights(results, reason):
#             enriched = {}
#             for r in results:
#                 matches = []
#                 if hasattr(r.meta, 'highlight'):
#                     matches = list(r.meta.highlight.to_dict().values())
#                     matches = [phrase for sublist in matches for phrase in sublist]
#                 enriched[r.meta.id] = {
#                     "matched_phrases": matches,
#                     "reason": reason
#                 }
#             return enriched

#         strict_enriched = enrich_with_highlights(strict_results, "Exact or near-exact keyword match")
#         relaxed_enriched = enrich_with_highlights(relaxed_filtered, "Partial or related keyword match")

#         strict_queryset = BuisnessDocument.search().filter("ids", values=list(strict_enriched.keys())).to_queryset().filter(city=city_obj)
#         relaxed_queryset = BuisnessDocument.search().filter("ids", values=list(relaxed_enriched.keys())).to_queryset().filter(city=city_obj)

#         product_query = ProductDocument.search().query(strict_query).to_queryset()
#         print("\033[96mProducts Found:\033[0m", product_query)
#         service_query = ServiceDocument.search().query(strict_query).to_queryset()
#         print("\033[93mServices Found:\033[0m", service_query)
#         bdcats = BDesCatDocument.search().query(Q("term", cat_name__raw=query)).to_queryset()
#         print("\033[94mBD Categories Found:\033[0m", bdcats)
#         bgcats = BGenCatDocument.search().query(strict_query).to_queryset()
#         print("\033[91mBG Categories Found:\033[0m", bgcats)

#         if product_query.count() != 0:
#             executor.submit(update_search_count_products, product_query)
#         if service_query.count() != 0:
#             executor.submit(update_search_count_services, service_query)

#         product_buisness_ids = product_query.values_list('buisness', flat=True).distinct()
#         service_buisness_ids = service_query.values_list('buisness', flat=True).distinct()
#         bdcats_buisness_ids = bdcats.values_list('buisness', flat=True).distinct()
#         bgcats_buisness_ids = bgcats.values_list('buisness', flat=True).distinct()

#         from_other_docs = Buisnesses.objects.filter(
#             id__in=set(chain(product_buisness_ids, service_buisness_ids, bdcats_buisness_ids, bgcats_buisness_ids)),
#             city=city_obj
#         )
#         print("\033[96mFrom Other Docs (Products/Services/Cats):\033[0m", from_other_docs)

#         filters = modelsQ()
#         if assured == 'True':
#             print('Applying assured=True filter')
#             filters &= modelsQ(assured=True)
#         if verified == 'True':
#             print('Applying verified=True filter')
#             filters &= modelsQ(verified=True)
#         if open_now == 'True':
#             now = localtime()
#             print('Applying open_now=True filter for time:', now)
#             filters &= (
#                 modelsQ(opens_at__lte=now, closes_at__gte=now) |
#                 modelsQ(opens_at__gt=F('closes_at'), opens_at__lte=now) |
#                 modelsQ(opens_at__gt=F('closes_at'), closes_at__gte=now)
#             )

#         strict_queryset = strict_queryset.filter(filters)
#         relaxed_queryset = relaxed_queryset.filter(filters)
#         from_other_docs = from_other_docs.filter(filters)

#         print("\033[92mFinal Filtered Strict Matches:\033[0m", strict_queryset)
#         print("\033[93mFinal Filtered Relaxed Matches:\033[0m", relaxed_queryset)
#         print("\033[96mFinal Filtered Others:\033[0m", from_other_docs)

#         executor.submit(update_search_count_buisnesses, list(chain(strict_queryset, relaxed_queryset, from_other_docs)))

#         def attach_matched_info(queryset, enriched_dict):
#             for obj in queryset:
#                 matched_data = enriched_dict.get(str(obj.id), {})
#                 obj.matched_info = matched_data
#             return queryset

#         strict_queryset = attach_matched_info(strict_queryset, strict_enriched)
#         relaxed_queryset = attach_matched_info(relaxed_queryset, relaxed_enriched)

#         if rated_high == 'True':
#             strict_queryset = sorted(strict_queryset, key=lambda x: (x.search_priority, x.rating), reverse=True)
#             relaxed_queryset = sorted(relaxed_queryset, key=lambda x: (x.search_priority, x.rating), reverse=True)
#             from_other_docs = sorted(from_other_docs, key=lambda x: (x.search_priority, x.rating), reverse=True)
#         else:
#             strict_queryset = sorted(strict_queryset, key=lambda x: x.search_priority, reverse=True)
#             relaxed_queryset = sorted(relaxed_queryset, key=lambda x: x.search_priority, reverse=True)
#             from_other_docs = sorted(from_other_docs, key=lambda x: x.search_priority, reverse=True)

#         metadata = future_cc_meta.result()

#         class ExtendedBuisnessSerializerMini(BuisnessesSerializerMini):
#             def to_representation(self, instance):
#                 rep = super().to_representation(instance)
#                 if hasattr(instance, 'matched_info'):
#                     rep['matched_info'] = instance.matched_info
#                 return rep

#         response = Response({
#             "metadata": metadata,
#             "exact_matches": ExtendedBuisnessSerializerMini(strict_queryset, many=True).data,
#             "related_matches": ExtendedBuisnessSerializerMini(relaxed_queryset, many=True).data,
#             "others": ExtendedBuisnessSerializerMini(from_other_docs, many=True).data,
#         })

#         return response








def extract_matches(hits, doc_type):
    results = []
    print(f"📄 Processing {len(hits)} hits for {doc_type}")
    for hit in hits:
        matched_fields = getattr(hit.meta, "highlight", {})
        matched_terms = []
        for field, fragments in matched_fields.items():
            for fragment in fragments:
                cleaned = fragment.replace("<em>", "").replace("</em>", "")
                matched_terms.append(cleaned)
        if matched_terms:
            print(f"✅ {doc_type} [ID {hit.meta.id}] matched: {matched_terms}")
        results.append({
            "doc_type": doc_type,
            "id": hit.meta.id,
            "matched_text": matched_terms
        })
    return results









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
    
    stopwords = {"a", "an", "and", "of", "on", "at", "in", "for"}
    query = "".join(word for word in query.split() if word.lower() not in stopwords and word.strip())
    print(query)


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
