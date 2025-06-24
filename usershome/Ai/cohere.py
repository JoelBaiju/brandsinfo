import random
import json
import time
import cohere

COHERE_API_KEY = "yOEglpyAXjyljpPkCXdK6dQjf7aBsoxMEUWUYLWp"  # Replace with your actual key

co = cohere.Client(api_key=COHERE_API_KEY)





def generate_metadata_for_SB(city, general_category, buisness_name, descriptive_category, description):

    prompt = f"""
    You are an expert SEO assistant trained to generate clean, non-generic metadata for business listings.

    ### BUSINESS DETAILS:
    - Business Name: {buisness_name}
    - Category: {general_category} ({descriptive_category})
    - City: {city}
    - Description: {description}

    ### STRICT INSTRUCTIONS:

    #### ✅ Meta Title (max 60 characters):
    - Include **service type** and **city**.
    - You may include part of the business name if helpful — not mandatory.
    - No repetition of words or filler text.
    - Must look natural and **click-worthy**.

    #### ✅ Meta Description (max 160 characters):
    - Brief, clear description of what the business offers.
    - Emphasize location or service strengths.
    - Friendly, actionable tone — avoid fluff.

    #### ✅ Meta Keywords (max 8; min 5):
    - ONLY include **specific search-intent keywords** users might type.
    - Must be strictly relevant to what the business offers.
    - ❌ DO NOT include:
    - Business name
    - City, state, or country names
    - Generic category words like "service", "company", "store", "best", "top", etc.
    - ✅ Do include:
    - Real search phrases like “AC repair”, “divorce lawyer”, “Tamil translator”
    - Separate by commas, **no repetition allowed**.

    #### 🎯 Target Gender:
    - Based on the description and offerings, infer the likely target audience gender.
    - Return one of: `"male"`, `"female"`, `"unisex"`

    ### ✅ JSON Output Only:
    Return only valid JSON in this format:
    ```json
    {{
    "meta_title": "<title>",
    "meta_description": "<description>",
    "meta_keywords": "<keyword1, keyword2, ...>",
    "target_gender": "unisex"
    }}
    """
    
    for attempt in range(5):
        try:
            response = co.chat(
                model="command-r7b-12-2024",
                message=prompt,
                temperature=0.8,
                max_tokens=300,
            )

            text = response.text.strip()
            json_start = text.find("{")
            json_end = text.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("No JSON block in response.")

            metadata = json.loads(text[json_start:json_end+1])
            return {
                "metadata": metadata,
                "usage": str(response),
                "raw_output": text,
                "prompt": prompt
            }

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"[Attempt {attempt+1}] Failed to parse Cohere response: {e}")
            time.sleep(0.5)

    raise ValueError("Cohere failed to generate a valid SEO metadata after multiple attempts.")






from ..models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view



@api_view(['GET'])
def Site_Map_Generator_SB_single_Test_api(request):
    buisness = Buisnesses.objects.get(id=request.GET.get('bid'))

    descriptive_category_qset = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
    descriptive_category_str = ", ".join([cat.dcat.cat_name for cat in descriptive_category_qset])

    response = generate_metadata_for_SB(
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
    gender = metadata.get("target_gender")

    keywords_list = [k.strip() for k in meta_keywords.split(',') if k.strip()]
    for kw in keywords_list:
        keyword_obj, _ = Keywords.objects.get_or_create(keyword=kw)
        Buisness_keywords.objects.get_or_create(buisness=buisness, keyword=keyword_obj)

    return Response({
        'm': 'Generated and saved successfully',
        'meta_title': meta_title,
        'meta_keywords': meta_keywords,
        'meta_description': meta_description,
        'response': response.get('usage'),
        'keyword': keywords_list,
        'gender': gender,
        'buisness_description': buisness.description,
        'buisness_name': buisness.name,
        'buisness_dcats': descriptive_category_str,
        'buisness_city': buisness.city.city_name
    })
