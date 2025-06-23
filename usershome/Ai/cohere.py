import random
import json
import time
import cohere

COHERE_API_KEY = "yOEglpyAXjyljpPkCXdK6dQjf7aBsoxMEUWUYLWp"  # Replace with your actual key

co = cohere.Client(api_key=COHERE_API_KEY)





def generate_metadata_for_SB(city, general_category, buisness_name, descriptive_category, description):

    prompt=f"""
    Generate **SEO metadata** for a business in **{city}**, focusing on **precise keyword targeting** and **local relevance**.

    ### **Business Information:**
    - **Business Name:** {buisness_name}
    - **Category:** {general_category} ({descriptive_category})
    - **Description:** {description}

    ### **SEO Metadata Guidelines (Strict):**

    #### ✅ Meta Title (≤ 60 characters)
    - Include **business name, service type, and city**.
    - Use strong, high-click-through-rate terms.
    - Avoid generic or repeated words.

    #### ✅ Meta Description (≤ 160 characters)
    - Briefly describe what the business offers.
    - Highlight **key value propositions and location**.
    - Use a friendly, action-driven tone.

    #### ✅ Meta Keywords (≤ 360 characters, comma-separated)
    - Include only **search-relevant keywords** related to:
      - The **services or products** offered
      - The **industry**
    - ❌ Do NOT include:
      - Generic place names (like “India”, “Tamil Nadu”)
      - Business names or owner names
      - Broad keywords like “finance”, “store”, “company”, “best”, “top”, etc.
    - ✅ Focus on **search intent** (e.g., "car repair", "gold loans", "wedding photography").
    - ✅ Use only keywords that a user would type to find this service.

    ### Target Audience
    Based on the above, return the likely **target gender**.

    ⚠️ Only respond with one of these: `"male"`, `"female"`, `"unisex"`

    ### 📦 Output Format (JSON only):
    ```json
    {{
        "meta_title": "<Optimized Meta Title>",
        "meta_description": "<Optimized Meta Description>",
        "meta_keywords": "<Comma-separated clean keywords>",
        "target_gender": "gender"
    }}
    ```
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
