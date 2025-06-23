


import random
from brandsinfo.settings import GEMINI_API_KEYS,SARVAM_API_KEY

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



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import requests
import itertools
import time


# def generate_reviews(description, category , eg_review):
#     session = requests.Session()

#     prompt = f"""
#     You are an intelligent review generator that creates short, natural, and realistic customer reviews for business listings.

#     ### BUSINESS DETAILS:
#     - Category: {category}
#     - Description: {description}
#     - Sample Review (Inspiration Only): {eg_review}

#     ### YOUR TASK:
#     Generate exactly 1 customer review that:
#     - Is inspired by the tone, meaning, and sentiment of the sample review.
#     - Also makes clear sense based on the business description and category.
#     - Sounds like it was written by a real customer — casual, friendly, or professional based on the type of business.

#     ### RULES (STRICT — DO NOT VIOLATE):
#     1. The review must be **under 50 characters**.
#     2. The review must **feel realistic and relevant to the business**.
#     3. DO NOT mention any location, pricing, offers, or imaginary details.
#     4. DO NOT use placeholders like [company name].
#     5. DO NOT copy the example review. Instead, **blend** its tone with the business type.
#     6. DO NOT generalize — the review should **fit the specific business description.**
#     7. Output MUST be valid JSON in this exact format:

#     ```json
#     {{
#     "reviews": "..."
#     }}"""



#     for attempt in range(5):
#         try:
#             api_key = next(api_key_cycle)
#             url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

#             payload = {"contents": [{"parts": [{"text": prompt}]}]}
#             headers = {
#                 "Content-Type": "application/json",
#                 "Accept-Encoding": "gzip",
#                 "Connection": "keep-alive"
#             }

#             response = session.post(url, headers=headers, json=payload, timeout=10)

#             if response.status_code == 429:
#                 time.sleep(0.5)
#                 continue

#             if response.status_code != 200:
#                 raise ValueError(f"Gemini API Error: {response.status_code} - {response.text}")

#             response_json = response.json()
#             candidates = response_json.get("candidates", [])
#             if not candidates:
#                 raise ValueError("No candidates returned from API.")

#             response_text = candidates[0]["content"]["parts"][0]["text"].strip()
#             json_start = response_text.find("{")
#             json_end = response_text.rfind("}")
#             if json_start == -1 or json_end == -1:
#                 raise ValueError("Invalid JSON format from response.")

#             reviews_json = response_text[json_start:json_end + 1]
#             reviews = json.loads(reviews_json)

#             return {"reviews": reviews, "usage": response_json}

#         except (requests.RequestException, json.JSONDecodeError) as e:
#             print(f"Attempt {attempt + 1} failed: {e}")

#     raise ValueError("Failed to generate reviews after multiple attempts.")












from sarvamai import SarvamAI
import json
import time
import random

# client = SarvamAI(
#     api_subscription_key=SARVAM_API_KEY,  # Replace with your actual key
# )





import cohere

COHERE_API_KEY = "yOEglpyAXjyljpPkCXdK6dQjf7aBsoxMEUWUYLWp"  # Replace with your actual key

co = cohere.Client(api_key=COHERE_API_KEY)



def generate_reviews(description, category, eg_review):
    # Add a variation token to promote diverse generations
    variation_token = f"v{random.randint(10000, 99999)}"

    prompt = f"""
    You are a smart, multilingual review generator that writes short, natural, and realistic customer reviews for business listings.

    ### BUSINESS DETAILS:
    - Category: {category}
    - Description: {description}
    - Sample Review (for tone only): {eg_review}

    ### INSTRUCTIONS:

    1. Understand the business description even if it's in a regional language (e.g., Tamil, Malayalam, etc.), but:
    - **ALWAYS** write the final review in **English only**.
    - Do **not** use any non-English words or phrases in the review.

    2. Check if the business belongs to a **sensitive or experience-restricted industry**:
    - Real estate, land/property sales
    - Hospitals, clinics, doctors, therapists
    - Legal services, law firms, lawyers
    - Financial services: banks, loans, insurance, investments
    - Mental health, psychiatry, or counseling

    If it **is sensitive**:
    - DO NOT mention usage, satisfaction, or outcomes.
    - DO NOT use any words or phrases from the description.
    - DO NOT describe any interaction or service received.
    - RETURN only a **very vague and generic English comment**.

    3. If the business is **not sensitive**:
    - You may use tone/sentiment from the sample review.
    - Keep it natural and short.
    - Blend in the vibe of the description if it helps — but **never copy phrases**.
    - Review must **sound like a real person’s comment**, not AI-generated.

    ### STRICT RULES (DO NOT BREAK):
    - The review must be **realistic**, **natural**, and in **English only**.
    - The review must be **under 50 characters**.
    - DO NOT mention:
    - Locations
    - Prices
    - Time durations
    - Results or benefits
    - That the customer completed or used the service
    - DO NOT fabricate experiences or outcomes.
    - DO NOT repeat phrases from the business description.

    ### OUTPUT FORMAT:
    Output must be a valid JSON in **this exact format**:

    ```json
    {{
    "reviews": "..."
    }}
    """
    for attempt in range(5):
        try:
            response = co.chat(
                model="command-a-03-2025",  # Better than nightly
                message=prompt,
                temperature=0.9,
                max_tokens=100,
            )

            raw_text = response.text.strip()

            json_start = raw_text.find("{")
            json_end = raw_text.rfind("}")
            if json_start == -1 or json_end == -1:
                raise ValueError("Invalid JSON format in Cohere response.")

            json_text = raw_text[json_start:json_end + 1]
            review_data = json.loads(json_text)

            return {
                "reviews": review_data,
                "raw_output": raw_text,
                "api_response": str(response),
                "prompt": prompt
            }

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"[Attempt {attempt + 1}] Cohere response error: {e}")
            time.sleep(0.5)

    raise ValueError("Cohere failed to generate a valid review after multiple attempts.")





from ..models import Buisnesses
def generate_reviews_based_on_buisness(buisness_id,eg_review):
    buisness = Buisnesses.objects.get(id = buisness_id)
    descats = ", ".join([i.dcat.cat_name for i in buisness.buisness_descriptive_cats_set.all()])
    gencats = ", ".join([i.gcat.cat_name for i in buisness.buisness_general_cats_set.all()])
    print(descats)
    print(gencats)

    return generate_reviews( buisness.description , descats+gencats,eg_review)


















def prime_review_generator(bid , r_type , plan):
    id = bid
    biz = Buisnesses.objects.get(id=id)
    b_type = biz.buisness_type
    
    eg_review = get_random_review(business_type=b_type , sentiment=r_type , tier=plan)
    
    try:
        reviews_data =         generate_reviews_based_on_buisness(id,eg_review)
        return reviews_data["reviews"]["reviews"]
            
    except:
        return ''


from ..Reviews.review_models import get_random_review


class GenerateDummyReviews(APIView):
    def post(self, request):
        id = request.data.get('id')
        biz = Buisnesses.objects.get(id=id)
        b_type = biz.buisness_type
        r_type = request.data.get('r_type')
        plan   = request.data.get('plan')


        eg_review = get_random_review(business_type=b_type , sentiment=r_type , tier=plan)
       
        try:
            reviews_data =         generate_reviews_based_on_buisness(id,eg_review)
            return Response({
                
                "review_data":reviews_data["reviews"],
                "eg_review":eg_review,
                "buisness_name":biz.name,
                "buisness_description":biz.description,
                "propmt":reviews_data["prompt"]
                
                }, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


