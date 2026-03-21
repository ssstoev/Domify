from embeddings import embed, client
from qdrant_client.models import Filter, FieldCondition, Range, NamedVector

def find_listings(query: str, max_price: int = None, top_k: int = 5):
    query_vector = embed(query)
    
    # Optional: filter by price alongside semantic search
    filters = None
    if max_price:
        filters = Filter(must=[
            FieldCondition(key="price", range=Range(lte=max_price))
        ])
    
    results = client.query_points(
        collection_name="listings",
        query=query_vector,
        query_filter=filters,
        limit=top_k
    )
    return results.points

# Example
results = find_listings("Необзаведен апартамент в квартал Овча Купел")
print(results)