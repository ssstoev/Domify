from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from retrieval.hard_constraints import extract_hard_constraints, filter_db_on_hard_constraints
from vector_db.search_embeddings import search_vector_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Without this your browser will throw a CORS error before the request even reaches your backend.
# Need to add it because fasAPI & Vite are on different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vite's default port
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Request / Response Models ---
# create pydantic model for the search request; for a single listing  & for a list of listings
class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5  # how many results to return

class Listing(BaseModel):
    hash_id: str
    title: str
    total_price_eur: float
    size_m2: str
    neighbourhood: str
    score: float  # similarity score from Qdrant

class SearchResponse(BaseModel):
    results: list[Listing]
    total: int

# --- POST Endpoint ---

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        # Step 1: Extract hard constraints from the query
        constraints = extract_hard_constraints(request.query)
        print(f"Extracted hard constraints: \n {constraints} \n")

        # Step 2: Filter RDBMS using constraints → get candidate IDs
        candidate_ids = filter_db_on_hard_constraints(constraints)
        print(f"Found {len(candidate_ids)} that match the constraints \n")

        if not candidate_ids:
            return SearchResponse(results=[], total=0)
        
        # Step 3: Search the vector DB and return results
        raw_results = search_vector_db(request.query, candidate_ids)
        print(f"Successfully searched the vector DB! Found {len(raw_results)} points \n")
        # Step 4: Shape into response
        listings = [
            Listing(
                hash_id=r.payload.get("Hash_id", ""),
                title=r.payload.get("Title", ""),
                total_price_eur=r.payload.get("Price (EUR)", ""),
                size_m2=r.payload.get("Size", ""),
                neighbourhood=r.payload.get("Neighbourhood", ""),
                score=r.score,
            )
            for r in raw_results
        ]
        print(f"Final result contains {len(listings)} points!")
        return SearchResponse(results=listings, total=len(listings))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))