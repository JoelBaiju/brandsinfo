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
    Generate structured SEO metadata for a website's listing page that lists buisnesses which peoples search for 
    in a particular category in a particular city with the following details :

    Website Name : BrandsInfo
    City: {city}
    Category: {category}

    **Output Format (strict adherence required):**  
    - Meta Title: (Max 60 characters)  
    - Meta Description: (Max 160 characters)  
    - Meta Keywords: (Comma-separated, only highly relevant SEO keywords)

    **Guidelines:**  
    - Strictly make the entire metadata SEO-friendly and in natural language. 
    - The meta title should be concise, engaging, and include the business name , category and city.  
    - The meta description must summarize the services offered while being compelling and SEO-friendly.  
    - The meta keywords should focus on primary search terms for the business, avoiding unnecessary words.  

 
    **Output Format (strict adherence required):**  
    ```json
    {{
        "meta_title": "<Generated Meta Title>",
        "meta_description": "<Generated Meta Description>",
        "meta_keywords": "<Comma-separated keywords>"
    }}
    ```
    
    """

    return generate_metadata(prompt)















def generate_metadata_for_SB(city,general_category,buisness_name,descriptive_category,description):

    prompt = f"""
    Generate structured SEO metadata for a buisness  with the following details:

    City: {city}
    Buisness_name : {buisness_name}
    General category: {general_category}
    Descriptive_category: {descriptive_category}
    Description: {description}

    **Output Format (strict adherence required):**  
    - Meta Title: (Max 60 characters)  
    - Meta Description: (Max 160 characters)  
    - Meta Keywords: (Comma-separated, only highly relevant SEO keywords)

    **Guidelines:**  
    - Strictly make the entire metadata SEO-friendly and in natural language. 
    - The meta title should be concise, engaging, and include the business name , category and city.  
    - The meta description must summarize the services offered while being compelling and SEO-friendly.  
    - The meta keywords should focus on primary search terms for the business, avoiding unnecessary words.  

 
    **Output Format (strict adherence required):**  
    ```json
    {{
        "meta_title": "<Generated Meta Title>",
        "meta_description": "<Generated Meta Description>",
        "meta_keywords": "<Comma-separated keywords>"
    }}
    ```
    
    """
    return generate_metadata(prompt)














