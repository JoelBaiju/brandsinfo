from brandsinfo.settings import GEMINI_API_KEYS

from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Sitemap_Links, City, Descriptive_cats, Buisnesses
import json
import re
import requests
from django.conf import settings  # Import Django settings
import itertools
import time











api_key_cycle = itertools.cycle(GEMINI_API_KEYS)

def generate_metadata(prompt):
    print("Generating metadata with Gemini 2.0 Flash...")

    session = requests.Session()  

    for attempt in range(5): 
        try:
            api_key = next(api_key_cycle)
            print( 'api key ' ,api_key)
            

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            headers = {
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip",  
                "Connection": "keep-alive"  
            }

            response = session.post(url, headers=headers, json=payload, timeout=10)

            if response.status_code == 429:  
                print(f"Rate limit reached for {api_key}. Skipping to next key...")
                time.sleep(0.5) 
                continue  
            
            if response.status_code != 200:
                raise ValueError(f"Error from Gemini API: {response.status_code} - {response.text}")

            response_json = response.json()
            candidates = response_json.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates returned from API.")

            response_text = candidates[0]["content"]["parts"][0]["text"].strip()

            json_start = response_text.find("{")
            json_end = response_text.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("Invalid JSON response received.")

            metadata_json = response_text[json_start:json_end + 1]
            metadata = json.loads(metadata_json)

            # print(metadata.get("meta_title", ""), metadata.get("meta_description", ""), metadata.get("meta_keywords", ""))
            
            return {"metadata": metadata, "usage": response_json}

        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")

    raise ValueError("Failed to fetch metadata after multiple attempts.")




















def generate_metadata_for_CC(category , city):
    prompt = f"""
    Generate high-quality **SEO metadata** for a business listing page on **BrandsInfo**, optimized for **search engine ranking and user engagement**.

    ### **Listing Information:**  
    - **Category:** {category}  
    - **City:** {city}  

    ### **SEO Metadata Guidelines (Follow Strictly):**  
    #### **Meta Title (≤ 60 characters)**  
    - Must include **category and city**.  
    - Use **power words** for clickability.  
    - Prioritize **high-impact keywords**.  

    #### **Meta Description (≤ 160 characters)**  
    - Clearly summarize the services provided.  
    - Naturally include **primary keywords**.  
    - Use action-oriented language for engagement.  

    #### **Meta Keywords (≤ 360 characters)**  
    - Include **highly relevant, high-search-volume terms**.  
    - Use **geo-targeted keywords** for local SEO.  
    - Ensure a **comma-separated format** with no unnecessary words.  

    ### **Output Format (Strict JSON):**  
    ```json
    {{
        "meta_title": "<Generated Meta Title>",
        "meta_description": "<Generated Meta Description>",
        "meta_keywords": "<Comma-separated keywords>"
    }}
    """
    
    return generate_metadata(prompt)











def generate_metadata_for_SB(city, general_category, buisness_name, descriptive_category, description):
    prompt = f"""
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
    return generate_metadata(prompt)


























