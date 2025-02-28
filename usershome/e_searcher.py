


# this secation active




# from django_elasticsearch_dsl import Document, Index, fields
# from django_elasticsearch_dsl.registries import registry
# from .models import *

# # # Define a shared Elasticsearch index
# products_index = Index('search_index')  # Change the name as needed

# @registry.register_document
# class ProductDocument(Document):
#     name = fields.TextField()
#     description = fields.TextField()
    
#     class Index:
#         name = 'search_index'

#     class Django:
#         model = Products


























# -----------------------------------------------------------------------------------------








# ignore






# from elasticsearch_dsl import analyzer, tokenizer

# # Define Edge NGram Tokenizer and Analyzer
# edge_ngram_tokenizer = tokenizer(
#     "edge_ngram_tokenizer", "edge_ngram", min_gram=2, max_gram=10, token_chars=["letter", "digit"]
# )

# edge_ngram_analyzer = analyzer(
#     "edge_ngram_analyzer",
#     tokenizer="edge_ngram_tokenizer"
# )

# # Define Elasticsearch Index
# products_index = Index("search_index")

# @products_index.settings(
#     number_of_shards=1,
#     number_of_replicas=0,
#     analysis={
#         "tokenizer": {
#             "edge_ngram_tokenizer": edge_ngram_tokenizer
#         },
#         "analyzer": {
#             "edge_ngram_analyzer": edge_ngram_analyzer
#         }
#     }
# )
# @registry.register_document
# class ProductDocument(Document):
#     name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
#     description = fields.TextField()

#     class Index:
#         name = "search_index"

#     class Django:
#         model = Products







































# ---------------------------------------------------------------












# this setion active
        
        
# @registry.register_document
# class ServiceDocument(Document):
#     name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
    
#     class Index:
#         name = 'search_index'

#     class Django:
#         model = Services  # Connect to SQL table
    
    
         
# @registry.register_document
# class BuisnessDocument(Document):
#     name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
    
#     class Index:
#         name = 'search_index'

#     class Django:
#         model = Buisnesses  # Connect to SQL table
    
    
     
# @registry.register_document
# class BDesCatDocument(Document):
#     name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
    
#     class Index:
#         name = 'search_index'

#     class Django:
#         model = Buisness_Descriptive_cats
        


     
# @registry.register_document
# class PSubCatsDocument(Document):
#     name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
    
#     class Index:
#         name = 'search_index'

#     class Django:
#         model = Product_linked_sub_category  # Connect to SQL table
    
    
    
    
    
    

    