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
            Q("multi_match", query=query, fields=["name", "category" ,"keywords"], fuzziness="AUTO", max_expansions=3, prefix_length=2),
            Q("multi_match", query=query, fields=["cat_name"], fuzziness="AUTO", max_expansions=3, prefix_length=2)
        ])
        
        try:
            city_obj = City.objects.get(city_name=location)
        except City.DoesNotExist:
            return Response(f'Sorry, we dont have any results for {location} city')

    
        products = ProductDocument.search().query(search_query).to_queryset()
        services = ServiceDocument.search().query(search_query).to_queryset()
        buisnesses_direct = BuisnessDocument.search().query(search_query).to_queryset()
        bdcats = BDesCatDocument.search().query(search_query).to_queryset()
        bgcats = BGenCatDocument.search().query(search_query).to_queryset()
        
        
        
        if products.count()!=0:
            executor.submit(update_search_count_products , products)
        if services.count()!=0:
            executor.submit(update_search_count_services , services)



        print('keyword',query)
        print('products',products)
        print('services',services)
        print('b_direct',buisnesses_direct)
        print('bdcats',bdcats)
        print('bgcats',bgcats)

        product_buisness_ids = products.values_list('buisness', flat=True).distinct()
        service_buisness_ids = services.values_list('buisness', flat=True).distinct()
        bdcats_buisness_ids = bdcats.values_list('buisness', flat=True).distinct()
        bgcats_buisness_ids = bgcats.values_list('buisness', flat=True).distinct()
        
        
        
        unique_buisness_ids = set(chain(product_buisness_ids, service_buisness_ids, bdcats_buisness_ids,bgcats_buisness_ids))


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
        if buisnesses_direct.count()!=0:
            executor.submit(update_search_count_buisnesses , buisnesses_direct)
            combined_queryset = buisnesses_direct          
        else:
            executor.submit(update_search_count_buisnesses , buisnesses)
            combined_queryset = buisnesses
            # executor.submit(update_search_count_buisnesses , buisnesses_direct)

        
        # combined_queryset = list(chain(buisnesses_direct, buisnesses))       i dont wanted to combine them if data in buisenesses_direct is not empty then i will use it only
        
        
        unique_combined_queryset = list(set(combined_queryset)) 
        
      
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
    print(bdcats_docs)

    # Extract keywords from documents
    keywords = set()
   
    for doc in bdcats_docs:
        keywords.add(doc.dcat.cat_name)
    
    for doc in chain(product_docs, service_docs, business_docs):
        keywords.add(doc.name.lower())
    
  
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





















