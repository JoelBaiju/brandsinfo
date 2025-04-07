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




@api_view(['GET'])
def elasticsearch2(request):
    query       = request.GET.get('q', '')
    location    = request.GET.get('location', '')
    verified    = request.GET.get('verified' , 'False')
    assured     = request.GET.get('assured' , 'False')
    rated_high  = request.GET.get('rated_high' , 'False')
    open_now    = request.GET.get('open_now' , 'False')


    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_cc_meta = executor.submit(CC_Check_and_add_metadata , location , query)
        
        search_query = Q("bool", should=[
            Q("multi_match", query=query, fields=["name", "category" ,"keywords"], fuzziness="AUTO", max_expansions=50, prefix_length=2),
            Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO", max_expansions=50, prefix_length=2)
        ])
        
        try:
            city_obj = City.objects.get(city_name=location)
        except City.DoesNotExist:
            return Response(f'Sorry, we dont have any results for {location} city')

    
        products = ProductDocument.search().query(search_query).to_queryset()
        services = ServiceDocument.search().query(search_query).to_queryset()
        buisnesses_direct = BuisnessDocument.search().query(search_query).to_queryset()
        bdcats = BDesCatDocument.search().query(search_query).to_queryset()
        
        if products.count()!=0:
            executor.submit(update_search_count_products , products)
        if services.count()!=0:
            executor.submit(update_search_count_services , services)



        print('keyword',query)
        print('products',products)
        print('services',services)
        print('b_direct',buisnesses_direct)
        

        product_buisness_ids = products.values_list('buisness', flat=True).distinct()
        service_buisness_ids = services.values_list('buisness', flat=True).distinct()
        bdcats_buisness_ids = bdcats.values_list('buisness', flat=True).distinct()

        unique_buisness_ids = set(chain(product_buisness_ids, service_buisness_ids, bdcats_buisness_ids))


        buisnesses = Buisnesses.objects.filter(id__in=unique_buisness_ids, city=city_obj)
        
        
        

        filters = modelsQ()

        if assured == 'True':
            print('assured filter applied')
            filters &= modelsQ(assured=True)

        if verified == 'True':
            print('verified filter applied')
            filters &= modelsQ(verified=True)

        if open_now == 'True':
            print('open_now filter applied')
            now = localtime()
            print(now)
            filters &= (
                modelsQ(opens_at__lte=now, closes_at__gte=now) |  # Normal case
                modelsQ(opens_at__gt=F('closes_at'), opens_at__lte=now) |  # Opens after midnight
                modelsQ(opens_at__gt=F('closes_at'), closes_at__gte=now)  # Closes after midnight
        )
            

        buisnesses = buisnesses.filter(filters)
        buisnesses_direct = buisnesses_direct.filter(filters)
        executor.submit(update_search_count_buisnesses , buisnesses)
        executor.submit(update_search_count_buisnesses , buisnesses_direct)

        
        combined_queryset = list(chain(buisnesses_direct, buisnesses))
        
        unique_combined_queryset = list(set(combined_queryset)) 
        
        # future_tier1_buisnesses = executor.submit(CC_Check_and_add_metadata , location , query)
        # future_tier1_buisnesses = executor.submit(CC_Check_and_add_metadata , location , query)
        # future_tier1_buisnesses = executor.submit(CC_Check_and_add_metadata , location , query)
        
        unique_combined_queryset = sorted(
            unique_combined_queryset, 
            key=lambda x: (x.search_priority), 
            reverse=True
        )

        if rated_high == 'True':
             unique_combined_queryset = sorted(
            unique_combined_queryset, 
            key=lambda x: (x.search_priority, x.rating), 
            reverse=True
            )         

        pageing_assistant=Pageing_assistant(unique_combined_queryset,BuisnessesSerializerMini)
        
        metadata = future_cc_meta.result()
        response = pageing_assistant.get_page(request)
        response.data['metadata'] = metadata  
        return response










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

    # Extract keywords from documents
    keywords = set()
   
    for doc in bdcats_docs:
        keywords.add(doc.dcat.cat_name)
    
    for doc in chain(product_docs, service_docs, business_docs):
        keywords.add(doc.name.lower())
    
  
    return Response({"suggestions": keywords})










@api_view(['GET'])
def keyword_suggestions_for_bdcats(request):
    query = request.GET.get('q', '').strip()
    print('query', query)
    
    if not query:
        return Response({"suggestions": []})

    # Build the Elasticsearch query
    search_query = Q("bool", should=[
    Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO"),
    Q("match_phrase_prefix", cat_name={"query": query})
    ])

    # Search using the Elasticsearch DSL document
    dcats_docs = DesCatDocument.search().query(search_query).source(['cat_name'])
    print('dcats_docs', dcats_docs)
    # Collect suggestions
    keywords = []
    for doc in dcats_docs:
        if hasattr(doc, 'cat_name'):
            keywords.append(
                    {'cat_name' : doc.cat_name ,'id' : doc.meta.id}
                            )

    return Response({"suggestions": list(keywords)})








@api_view(['GET'])
def keyword_suggestions_for_gcats(request):
    query = request.GET.get('q', '').strip()
    print('query', query)
    
    if not query:
        return Response({"suggestions": []})

    search_query = Q("bool", should=[
    Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO"),
    Q("match_phrase_prefix", cat_name={"query": query})
    ])

    gcats_docs = GenCatDocument.search().query(search_query).source(['cat_name'])
    
    keywords = []
    for doc in gcats_docs:
        if hasattr(doc, 'cat_name'):
            keywords.append(
                    {'name' : doc.cat_name ,'id' : doc.meta.id}
                            )

    return Response(list(keywords))
