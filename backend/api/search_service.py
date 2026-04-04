from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# --- Request / Response Models ---
# create pydantic model for the search request; for a single listing  & for a list of listings
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5  # how many results to return

class Listing(BaseModel):
    hash_id: str
    title: str
    price: float
    size: float
    neighborhood: str
    link: str
    score: float  # similarity score from Qdrant

class SearchResponse(BaseModel):
    results: list[Listing]
    total: int

# --- Endpoint ---

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        # Step 1: Extract hard constraints from the query
        constraints = extract_constraints(request.query)

        # Step 2: Filter RDBMS using constraints → get candidate IDs
        candidate_ids = filter_rdbms(constraints)

        if not candidate_ids:
            return SearchResponse(results=[], total=0)

        # Step 3: Embed the user query
        vector = embed_query(request.query)

        # Step 4: Search Qdrant filtered to candidate IDs
        raw_results = vector_search(vector, candidate_ids, top_k=request.top_k)

        # Step 5: Shape into response
        listings = [
            Listing(
                id=r.id,
                score=r.score,
                **r.payload  # title, price, size, neighborhood, link from Qdrant payload
            )
            for r in raw_results
        ]

        return SearchResponse(results=listings, total=len(listings))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))