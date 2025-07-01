# Import necessary modules and classes
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, tokenizer, Q
from ..models import *  
from ..serializers import *  
from ..Tools_Utils.utils import *


index_settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "filter": {
            "english_stop": {
                "type":       "stop",
                "stopwords":  ["_english_"]  # built-in list; you can customize if needed
            }
        },
        "tokenizer": {
            "edge_ngram_tokenizer": {
                "type": "edge_ngram",
                "min_gram": 2,  # avoid 1-gram to reduce noise
                "max_gram": 20,
                "token_chars": ["letter", "digit"]
            }
        },
        "analyzer": {
            "edge_ngram_analyzer": {
                "type": "custom",
                "tokenizer": "edge_ngram_tokenizer",
                "filter": ["lowercase", "english_stop"]
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
        name = 'products_index'
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
        name = 'services_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Services

# Business Document








bdc_index_settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
        "analyzer": {
            "edge_ngram_analyzer": {
                "type": "custom",
                "tokenizer": "edge_ngram_tokenizer",
                "filter": ["lowercase", "stop"]
            },
            "stop_analyzer": {
                "type": "custom",
                "tokenizer": "standard",
                "filter": ["lowercase", "stop"]
            }
        },
        "tokenizer": {
            "edge_ngram_tokenizer": {
                "type": "edge_ngram",
                "min_gram": 2,
                "max_gram": 20,
                "token_chars": ["letter", "digit", "whitespace"]
            }
        },
        "normalizer": {
            "lowercase_normalizer": {
                "type": "custom",
                "filter": ["lowercase"]
            }
        }
    }
}


@registry.register_document
class BuisnessDocument(Document):
    name = fields.TextField(
        analyzer="edge_ngram_analyzer",
        search_analyzer="stop_analyzer",
        fields={
            "raw": fields.KeywordField(normalizer="lowercase_normalizer")
        }
    )

    keywords = fields.ListField(
        fields.TextField(
            analyzer='stop_analyzer',          # Avoid indexing stopwords
            search_analyzer='stop_analyzer',
            fields={
                'raw': fields.KeywordField(normalizer='lowercase_normalizer')
            }
        )
    )

    class Index:
        name = 'businesses_index'
        settings = bdc_index_settings

    class Django:
        model = Buisnesses
        related_models = [Buisness_keywords]

    def prepare_keywords(self, instance):
        return list(instance.buisness_keywords_set.values_list('keyword__keyword', flat=True))

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Buisness_keywords):
            return [related_instance.buisness]
        return []











@registry.register_document
class BDesCatDocument(Document):

    cat_name = fields.TextField(
        analyzer='standard',
        search_analyzer='standard',
        fields={
            'raw': fields.KeywordField(normalizer='lowercase_normalizer')
        }
    )
    class Index:
        name = 'bdcats_index'
        settings = bdc_index_settings  # Use custom index settings

    class Django:
        model = Buisness_Descriptive_cats
        
    
    def prepare_cat_name(self, instance):
        # Fetch the `cat_name` from the related `Descriptive_cats` model
        return instance.dcat.cat_name
    
    
@registry.register_document
class BGenCatDocument(Document):
    cat_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'bgcats_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Buisness_General_cats   
    
    def prepare_cat_name(self, instance):
        return instance.gcat.cat_name
     
    
        


@registry.register_document
class DesCatDocument(Document):
    cat_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
    id = fields.IntegerField()
    class Index:
        name = 'dcats_index'
        settings = index_settings  

    class Django:
        model = Descriptive_cats
        
    
    
    
@registry.register_document
class GenCatDocument(Document):
    cat_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'gcats_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = General_cats
        
    
        
        
        

# Product Subcategories Document
@registry.register_document
class PSubCatsDocument(Document):
    cat_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'pscats_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Product_Sub_category



@registry.register_document
class PGeneralCatsDocument(Document):
    cat_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'pgcats_index'
        settings = index_settings  # Use custom index settings

    class Django:
        model = Product_General_category




@registry.register_document
class UsersDocument(Document):
    username =  fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")
    first_name =  fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'users_index'
        settings = index_settings  

    class Django:
        model = Extended_User














# City Document
@registry.register_document
class CityDocument(Document):
    city_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'cities_index'
        settings = index_settings

    class Django:
        model = City


# Locality Document
@registry.register_document
class LocalityDocument(Document):
    locality_name = fields.TextField(analyzer="edge_ngram_analyzer", search_analyzer="standard")

    class Index:
        name = 'localities_index'
        settings = index_settings

    class Django:
        model = Locality
