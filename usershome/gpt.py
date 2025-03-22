from openai import OpenAI
from brandsinfo.settings import OPENAI_API_KEY

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Sitemap_Links, City, Descriptive_cats, Buisnesses
import json
import re














client = OpenAI(api_key=OPENAI_API_KEY)


def generate_metadata(prompt):
   

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        # model="text-embedding-3-small",
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_text = completion.choices[0].message.content.strip()

    # Use regex to extract valid JSON only
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not match:
        raise ValueError("Invalid JSON response received.")

    json_text = match.group(0)  # Extract matched JSON

    # Parse JSON safely
    try:
        metadata = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON: {e}")
    

    meta_title = metadata.get("meta_title", "")
    meta_description = metadata.get("meta_description", "")
    meta_keywords = metadata.get("meta_keywords", "")

    print(meta_title, meta_description, meta_keywords)

    return  metadata



def generate_metadata_for_CC(category , city):
    

    prompt = f"""
    Generate SEO metadata for a business listing page on **BrandsInfo**. The page features businesses in **{category}** within **{city}**.

    ### **Output Format (strictly follow):**
    - **Meta Title** (≤ 60 characters): Must include **category** and **city**.
    - **Meta Description** (≤ 160 characters): Summarize services naturally and SEO-optimized.
    - **Meta Keywords**: Comma-separated, highly relevant search terms.

    ### **Return JSON Format:**
    ```json
    {{
        "meta_title": "<Generated Meta Title>",
        "meta_description": "<Generated Meta Description>",
        "meta_keywords": "<Comma-separated keywords>"
    }}
    """
    
    return generate_metadata(prompt)















def generate_metadata_for_SB(city,general_category,buisness_name,descriptive_category,description):

    
    prompt = f"""
        Generate SEO metadata for a business in **{city}**.

        ### **Business Details:**  
        - **Name:** {buisness_name}  
        - **Category:** {general_category} ({descriptive_category})  
        - **Description:** {description}  

        ### **Output Format (strictly follow):**  
        - **Meta Title** (≤ 60 characters): Include **business name, category, city**.  
        - **Meta Description** (≤ 160 characters): Summarize services, SEO-optimized.  
        - **Meta Keywords**: Comma-separated, highly relevant search terms.  

        ### **Return JSON Format:**  
        ```json
        {{
            "meta_title": "<Generated Meta Title>",
            "meta_description": "<Generated Meta Description>",
            "meta_keywords": "<Comma-separated keywords>"
        }}


        """
    return generate_metadata(prompt)














