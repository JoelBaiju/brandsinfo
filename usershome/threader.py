# from elasticsearch import Elasticsearch

# es = Elasticsearch(["http://your-ec2-ip:9200"])

# # Create an index
# index_body = {
#     "settings": {
#         "number_of_shards": 1,
#         "number_of_replicas": 1
#     },
#     "mappings": {
#         "properties": {
#             "name": {"type": "text"},
#             "description": {"type": "text"},
#             "category": {"type": "keyword"}
#         }
#     }
# }

# es.indices.create(index="my_index", body=index_body)



from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product 

# Define a shared Elasticsearch index
products_index = Index('search_index')  # Change the name as needed

@registry.register_document
class ProductDocument(Document):
    name = fields.TextField()
    description = fields.TextField()
    
    class Index:
        name = 'search_index'

    class Django:
        model = Product  # Connect to SQL table

# @registry.register_document
# class TechnicianDocument(Document):
#     name = fields.TextField()
#     skills = fields.TextField()
    
#     class Index:
#         name = 'search_index'

#     class Django:
#         model = Technician  # Connect to SQL table
