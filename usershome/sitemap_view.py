

# DRF imports
from rest_framework.decorators import api_view
from rest_framework.response import Response



# Local app imports
from .models import *
from .serializers import * 
from brandsinfo.settings import FRONTEND_BASE_URL_FOR_SM , BACKEND_BASE_URL_FOR_SM
from .gpt import generate_metadata_for_CC, generate_metadata_for_SB






    
    
@api_view(['GET'])
def Site_Map_Generator_ALLATONCE_CC(request):
    
    cities = City.objects.all()
    dcats  = Descriptive_cats.objects.all()
    
    
    for dcat in dcats:
        for city in cities:
            
        #     metadata = generate_metadata_for_CC(
        #     city=city,
        #     category=dcat,
        # )

            # meta_title = metadata.get("meta_title", "")
            # meta_description = metadata.get("meta_description", "")
            # meta_keywords = metadata.get("meta_keywords", "")

            sitemap_obj = Sitemap_Links.objects.create(
                # meta_title=meta_title,
                # meta_description=meta_description,
                # meta_keywords=meta_keywords,
                city = city,
                dcat = dcat
            )
            sitemap_obj.cc_combination = True
            # sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{city}/{dcat}/{sitemap_obj.id}?keywords={meta_keywords}"
            sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{city}/{dcat}/{sitemap_obj.id}"
            sitemap_obj.share_link = f"{BACKEND_BASE_URL_FOR_SM}/mapper/{sitemap_obj.id}/"
            sitemap_obj.save()
        
   
    
    return Response('Generated and saved successfully') 




from openai import OpenAI
from brandsinfo.settings import OPENAI_API_KEY


    
    
    
    
    
    
    
    
    
    
    
    


@api_view(['GET'])
def Site_Map_Generator_ALLATONCE_SB(request):
   
    businesses = Buisnesses.objects.all()



    for buisness in businesses:
        descriptive_category_qset = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
        descriptive_category_str = ", ".join([cat.dcat.cat_name for cat in descriptive_category_qset])

        metadata = generate_metadata_for_SB(
            buisness_name=buisness.name,
            description=buisness.description,
            general_category=Buisness_General_cats.objects.get(buisness=buisness),
            descriptive_category=descriptive_category_str,
            city=buisness.city
        )

        meta_title = metadata.get("meta_title", "")
        meta_description = metadata.get("meta_description", "")
        meta_keywords = metadata.get("meta_keywords", "")

        sitemap_obj = Sitemap_Links.objects.create(
            buisness=buisness,
            meta_title=meta_title,
            meta_description=meta_description,
            meta_keywords=meta_keywords
        )
        sitemap_obj.single_buisness = True
        sitemap_obj.City = Buisnesses.city 
        sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{buisness.city}/{buisness.name}{(buisness.landmark) if buisness.landmark is not None else ''}/{sitemap_obj.id}?keywords={meta_keywords}"
        sitemap_obj.share_link = f"{BACKEND_BASE_URL_FOR_SM}/mapper/{sitemap_obj.id}/"
        sitemap_obj.save()

    return Response('Generated and saved successfully')

    
    
    
    
    
    
    
    
def Site_Map_Generator_ALLATONCE_SB_single(buisness):
   
    businesses = Buisnesses.objects.all()



    descriptive_category_qset = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
    descriptive_category_str = ", ".join([cat.dcat.cat_name for cat in descriptive_category_qset])

    # metadata = generate_metadata_for_SB(
    #     buisness_name=buisness.name,
    #     description=buisness.description,
    #     general_category=Buisness_General_cats.objects.filter(buisness=buisness)[0],
    #     descriptive_category=descriptive_category_str,
    #     city=buisness.city
    # )

    # meta_title = metadata.get("meta_title", "")
    # meta_description = metadata.get("meta_description", "")
    # meta_keywords = metadata.get("meta_keywords", "")

    sitemap_obj = Sitemap_Links.objects.create(
        buisness=buisness,
        # meta_title=meta_title,
        # meta_description=meta_description,
        # meta_keywords=meta_keywords
    )
    sitemap_obj.single_buisness = True
    sitemap_obj.City = Buisnesses.city 
    # sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{buisness.city}/{buisness.name}{(buisness.landmark) if buisness.landmark is not None else ''}/{sitemap_obj.id}?keywords={meta_keywords}"
    sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{buisness.city}/{buisness.name}{(buisness.landmark) if buisness.landmark is not None else ''}/{sitemap_obj.id}"
    sitemap_obj.share_link = f"{BACKEND_BASE_URL_FOR_SM}/mapper/{sitemap_obj.id}/"
    sitemap_obj.save()

    print( 'Generated and saved successfully')

    