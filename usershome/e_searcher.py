# Import necessary modules and classes
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer, Q
from itertools import chain
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .models import *  
from .serializers import *  
from django.db.models import Q as modelsQ
from django.db.models import F
import concurrent.futures
from .sitemap_view import CC_Check_and_add_metadata
from .utils import *


# Define Edge NGram Tokenizer and Analyzer
edge_ngram_tokenizer = tokenizer(
    "edge_ngram_tokenizer", type="ngram", min_gram=1, max_gram=20, token_chars=["letter", "digit"]
)

edge_ngram_analyzer = analyzer(
    "edge_ngram_analyzer",
    tokenizer="edge_ngram_tokenizer",
    filter=["lowercase"]
)

# Define a reusable index settings dictionary
index_settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "tokenizer": {
            "edge_ngram_tokenizer": {
                "type": "edge_ngram",
                "min_gram": 1,
                "max_gram": 20,
                "token_chars": ["letter", "digit"]
            }
        },
        "analyzer": {
            "edge_ngram_analyzer": {
                "type": "custom",
                "tokenizer": "edge_ngram_tokenizer",
                "filter": ["lowercase"]
            }
        }
    }
}

# Product Document
@registry.register_document
class ProductDocument(Document):
    name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard"  )
    category = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard"  )
    description = fields.TextField()

    class Index:
        name = 'search_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Products
        
    def prepare_category(self, instance):
        # Fetch the `cat_name` from the related `Descriptive_cats` model
        return instance.sub_cat.cat_name
        
        


# Service Document
@registry.register_document
class ServiceDocument(Document):
    name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'search_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Services

# Business Document
@registry.register_document
class BuisnessDocument(Document):
    name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")


    class Index:
        name = 'search_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Buisnesses

# Business Descriptive Categories Document
@registry.register_document
class BDesCatDocument(Document):
    name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'search_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Buisness_Descriptive_cats
        
    
    def prepare_name(self, instance):
        # Fetch the `cat_name` from the related `Descriptive_cats` model
        return instance.dcat.cat_name
        
        

# Product Subcategories Document
@registry.register_document
class PSubCatsDocument(Document):
    cat_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'search_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Product_Sub_category

















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
            Q("multi_match", query=query, fields=["name", "category"], fuzziness="AUTO", max_expansions=50, prefix_length=2),
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
def keyword_suggestions(request):
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

