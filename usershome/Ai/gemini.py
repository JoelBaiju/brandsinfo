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
from django.conf import settings











api_key_cycle = itertools.cycle(GEMINI_API_KEYS)

def generate_metadata_gemini(prompt):
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


import cohere

api_key_cycle = itertools.cycle(settings.COHERE_API_KEYS)

co = cohere.Client(api_key=next(api_key_cycle))


def generate_metadata_cohere(prompt):
    print("Generating metadata with Cohere...")

    for attempt in range(3):
        try:
            response = co.chat(
                model="command-a-03-2025",
                message=prompt,
                temperature=0.7,
                max_tokens=300,
            )

            response_text = response.text.strip()

            json_start = response_text.find("{")
            json_end = response_text.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("Invalid JSON format in Cohere response.")

            metadata_json = response_text[json_start:json_end + 1]
            metadata = json.loads(metadata_json)

            return {
                "metadata": metadata,
                "usage": response  # This is the full cohere.ChatResponse object
            }

        except Exception as e:
            print(f"[Attempt {attempt + 1}] Cohere metadata generation failed:", e)
            time.sleep(0.5)

    raise ValueError("Cohere failed to generate metadata after multiple attempts.")




from sarvamai import SarvamAI

client = SarvamAI(
    api_subscription_key=settings.SARVAM_API_KEY
)


def generate_metadata_sarvam(prompt):
    print("Generating metadata with Sarvam AI...")

    for attempt in range(3):
        try:
            response = client.chat.completions(
                messages=[
                    {"role": "system", "content": "You generate clean SEO metadata for business listings."},
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = response.choices[0].message.content.strip()

            json_start = response_text.find("{")
            json_end = response_text.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("Invalid JSON format from Sarvam AI.")

            metadata_json = response_text[json_start:json_end + 1]
            metadata = json.loads(metadata_json)

            return {
                "metadata": metadata,
                "usage": response  # OpenAI-compatible client response
            }

        except Exception as e:
            print(f"[Attempt {attempt + 1}] Sarvam metadata generation failed:", e)
            time.sleep(0.5)

    raise ValueError("Sarvam AI failed to generate metadata after multiple attempts.")














def generate_metadata(prompt):
    """
    Controller that tries AI models in order of configured priority until one returns valid metadata.
    """
    model_functions = {
        "gemini": generate_metadata_gemini,
        "cohere": generate_metadata_cohere,
        "sarvam": generate_metadata_sarvam
    }

    for model_name in settings.AI_METADATA_PRIORITY:
        func = model_functions.get(model_name)
        if not func:
            print(f"Model '{model_name}' is not recognized. Skipping.")
            continue

        try:
            print(f"Trying metadata generation with: {model_name}")
            return func(prompt)
        except Exception as e:
            print(f"{model_name} failed with error: {e}")
            continue

    raise ValueError("All metadata generators failed. Please check API services.")











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
    return generate_metadata(prompt)


























