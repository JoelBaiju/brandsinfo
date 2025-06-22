import json
import random

# Load the JSON data from file
with open('usershome/Reviews/review_data_translated.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
import random

def get_random_review(business_type: str, sentiment: str, tier: str) -> str:
    business_key = f"{business_type}_based"

    try:
        if tier == "all":
            reviews_list = data["all_plans"][business_key][sentiment]

        elif tier == "tier1":
            if sentiment == "medium":
                # Merge tier1 general medium with all_plans medium
                reviews_list = (
                    data["all_plans"][business_key]["medium"]
                    + data["free_tier"]["medium"]
                )
            else:
                # For good/bad just fallback to normal all_plans
                reviews_list = data["all_plans"][business_key][sentiment]

        else:
            return "Invalid tier. Use 'all' or 'tier1'."

        if not reviews_list:
            return f"No reviews found for {business_type} - {sentiment} - {tier}."

        return random.choice(reviews_list)

    except Exception as e:
        return f"Error: {str(e)}"





from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json



class getEgReviews(APIView):
    def get(self, request):
        id = request.data.get('id')
       
        try:
            reviews_data = get_random_review("service","good","all")
            return Response(reviews_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


