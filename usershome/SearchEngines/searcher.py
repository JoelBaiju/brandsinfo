import Levenshtein
from django.db import connection

def find_closest(modelname, user_input, max_results=5):
   
    valid_tables = ["usershome_product_sub_category","usershome_general_cats","City"]  

    if modelname not in valid_tables:
        raise ValueError("Invalid table name!")

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT id, cat_name FROM {modelname}")  # Fetch only needed columns
        products = cursor.fetchall()

    # Compute Levenshtein distances
    distances = [
        (product[0], product[1], Levenshtein.distance(user_input.lower(), product[1].lower()))
        for product in products
    ]

    # Sort by distance (lower is better)
    distances.sort(key=lambda x: x[2])

    # Return closest matches
    return [{"id": prod[0], "name": prod[1]} for prod in distances[:max_results]]
