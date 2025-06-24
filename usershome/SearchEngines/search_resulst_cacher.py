import redis
import json

# Initialize Redis (adjust host/port/db as per your server)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
import hashlib
from rest_framework.response import Response

def generate_cache_key(query, location, filters_dict):
    key_data = {
        "query": query.strip().lower(),
        "location": location.strip().lower(),
        "filters": filters_dict
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return "search:" + hashlib.md5(key_str.encode()).hexdigest()



def cache_search_response(query, location, filters_dict, response_data, timeout=3600):
    key = generate_cache_key(query, location, filters_dict)
    redis_client.setex(key, timeout, json.dumps(response_data))






def get_cached_search_response(query, location, filters_dict):
    key = generate_cache_key(query, location, filters_dict)
    cached_data = redis_client.get(key)
    if cached_data:
        try:
            data = json.loads(cached_data)
            return Response(data)
        except json.JSONDecodeError:
            return None
    return None



