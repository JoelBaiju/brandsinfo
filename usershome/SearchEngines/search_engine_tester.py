from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

response = es.explain(
    index="businesses_index",
    id="266",
    query={
        "multi_match": {
            "query": "Marketing-and-Advertising",
            "fields": ["name"],
            "fuzziness": 1,
            "prefix_length": 2
        }
    }
)

import json
print(json.dumps(response.body, indent=2))








# from elasticsearch import Elasticsearch

# es = Elasticsearch("http://localhost:9200")

# # Fetch 5 documents from the index
# results = es.search(index="businesses_index", size=5, query={"match_all": {}})

# # Print IDs
# for doc in results["hits"]["hits"]:
#     print(f"ID: {doc['_id']}, Source: {doc['_source']}")
