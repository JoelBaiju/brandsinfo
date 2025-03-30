

# DRF imports
from rest_framework.decorators import api_view
from rest_framework.response import Response



# Local app imports
from .models import *
from .serializers import * 
from brandsinfo.settings import FRONTEND_BASE_URL_FOR_SM , BACKEND_BASE_URL_FOR_SM
from .gemini import generate_metadata_for_SB as gemini_generate_metadata_for_SB
from .gemini import generate_metadata_for_CC as gemini_generate_metadata_for_CC
from django.db import IntegrityError
from .serializers import SiteSaplinksSerializerFull









    
    
# @api_view(['GET'])
# def Site_Map_Generator_ALLATONCE_CC(request):
    
#     cities = City.objects.all()
#     dcats  = Descriptive_cats.objects.all()
    
#     for dcat in dcats:
#         for city in cities:
            
#         #     response = gemini_generate_metadata_for_CC(
#         #     city=city,
#         #     category=dcat,
#         # )
#         # metadata = response['metadata']

#             # meta_title = metadata.get("meta_title", "")
#             # meta_description = metadata.get("meta_description", "")
#             # meta_keywords = metadata.get("meta_keywords", "")

#             sitemap_obj = Sitemap_Links.objects.create(
#                 # meta_title=meta_title,
#                 # meta_description=meta_description,
#                 # meta_keywords=meta_keywords,
#                 city = city,
#                 dcat = dcat
#             )
#             sitemap_obj.cc_combination = True
#             # sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{city}/{dcat}/{sitemap_obj.id}?keywords={meta_keywords}"
#             sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{city}/{dcat}/{sitemap_obj.id}"
#             sitemap_obj.share_link = f"{BACKEND_BASE_URL_FOR_SM}/mapper/{sitemap_obj.id}/"
#             sitemap_obj.save()
        
   
    
#     return Response('Generated and saved successfully') 

@api_view(['GET'])
def Site_Map_Generator_ALLATONCE_CC(request):
    cities = City.objects.all()  
    categories = Descriptive_cats.objects.all()

    new_cities = City.objects.filter(maped=False)
    new_categories = Descriptive_cats.objects.filter(maped=False)

    new_entries = []
    for city in new_cities:
        for category in categories:
            new_entries.append(Sitemap_Links(city=city, dcat=category, cc_combination=True , city_name=city.city_name ,dcat_name=category.cat_name))

    for category in new_categories:
        for city in cities:
            new_entries.append(Sitemap_Links(city=city, dcat=category, cc_combination=True,city_name=city.city_name ,dcat_name=category.cat_name))

    # Bulk create new sitemap links
    Sitemap_Links.objects.bulk_create(new_entries, ignore_conflicts=True)

    # Fetch created objects again with their assigned primary keys
    created_sitemap_links = Sitemap_Links.objects.filter(city__in=new_cities, dcat__in=categories) | Sitemap_Links.objects.filter(city__in=cities, dcat__in=new_categories)

    # Update links with IDs
    for sitemap_obj in created_sitemap_links:
        sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{sitemap_obj.city}/{sitemap_obj.dcat}/{sitemap_obj.id}"
        sitemap_obj.share_link = f"{BACKEND_BASE_URL_FOR_SM}/mapper/{sitemap_obj.id}/"
        sitemap_obj.dcat_name=sitemap_obj.dcat
        sitemap_obj.city_name=sitemap_obj.city

    # Bulk update the links
    Sitemap_Links.objects.bulk_update(created_sitemap_links, ["link", "share_link","dcat_name","city_name"])

    # Mark processed cities and categories
    new_cities.update(maped=True)
    new_categories.update(maped=True)

    return Response({"message": "Sitemap links generated successfully"})









    
    
def CC_Check_and_add_metadata(city , dcat):
    
    sitemap_obj = Sitemap_Links.objects.filter(city_name=city, dcat_name=dcat).first()

    
    if sitemap_obj:
        if sitemap_obj.meta_description:
            print('yess it has data')
            return SiteSaplinksSerializerFull(sitemap_obj).data
        
        else :        
            print('no data , new one added')
            response = gemini_generate_metadata_for_CC(
                city     = city,
                category = dcat,
            )
            metadata = response['metadata']

            sitemap_obj.meta_title         = metadata.get("meta_title", "")
            sitemap_obj.meta_description   = metadata.get("meta_description", "")
            sitemap_obj.meta_keywords      = metadata.get("meta_keywords", "")
            sitemap_obj.cc_combination     = True
            sitemap_obj.link               = f"{FRONTEND_BASE_URL_FOR_SM}/{city}/{dcat}/{sitemap_obj.id}?keywords={sitemap_obj.meta_keywords}"
            sitemap_obj.save()
            
            return SiteSaplinksSerializerFull(sitemap_obj).data
        
    return False

    
    
    
    
    
    
    
    


@api_view(['GET'])
def Site_Map_Generator_ALLATONCE_SB(request):
   
    businesses = Buisnesses.objects.filter(maped=False)



    for buisness in businesses:
        descriptive_category_qset = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
        descriptive_category_str = ", ".join([cat.dcat.cat_name for cat in descriptive_category_qset])
        print(buisness)
        response = gemini_generate_metadata_for_SB(
            buisness_name=buisness.name,
            description=buisness.description,
            general_category=Buisness_General_cats.objects.filter(buisness=buisness)[0],
            descriptive_category=descriptive_category_str,
            city=buisness.city
        )
        metadata = response['metadata']

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
        buisness.maped=True
        buisness.save()

    return Response('Generated and saved successfully')

    
    
    
    
    
    
    
    
def Site_Map_Generator_SB(buisness):
   
    descriptive_category_qset = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
    descriptive_category_str = ", ".join([cat.dcat.cat_name for cat in descriptive_category_qset])

    response = gemini_generate_metadata_for_SB(
        buisness_name=buisness.name,
        description=buisness.description,
        general_category=Buisness_General_cats.objects.filter(buisness=buisness)[0],
        descriptive_category=descriptive_category_str,
        city=buisness.city
    )
    metadata = response['metadata']

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
    # sitemap_obj.link = f"{FRONTEND_BASE_URL_FOR_SM}/{buisness.city}/{buisness.name}{(buisness.landmark) if buisness.landmark is not None else ''}/{sitemap_obj.id}"
    sitemap_obj.share_link = f"{BACKEND_BASE_URL_FOR_SM}/mapper/{sitemap_obj.id}/"
    sitemap_obj.save()
    buisness.maped=True
    buisness.save()

    print( 'Generated and saved successfully')




import json



@api_view(['GET'])
def Site_Map_Generator_SB_single_Test_api(request):
    
    buisness=Buisnesses.objects.get(id=request.GET.get('bid'))

    descriptive_category_qset = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
    descriptive_category_str = ", ".join([cat.dcat.cat_name for cat in descriptive_category_qset])

    response = gemini_generate_metadata_for_SB(
        buisness_name=buisness.name,
        description=buisness.description,
        general_category=Buisness_General_cats.objects.filter(buisness=buisness)[0],
        descriptive_category=descriptive_category_str,
        city=buisness.city
    )
    metadata = response['metadata']
    
    meta_title = metadata.get("meta_title", "")
    meta_description = metadata.get("meta_description", "")
    meta_keywords = metadata.get("meta_keywords", "")


    response_json = response.get('usage')

    return Response( {'m':'Generated and saved successfully',
                      'meta_title':meta_title,
                      'meta_keywords':meta_keywords,
                      'meta_description':meta_description,
                      'response':response_json})

    
    
    
    
