from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.models.document import Chunk

from app.api import deps
from app.models.user import User
from app.services.vector_store import vector_store

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResult(BaseModel):
    text: str
    score: float
    metadata: Any

@router.post("/search", response_model=List[SearchResult])
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Search for relevant document chunks with re-ranking based on feedback.
    """
    try:
        # 1. Vector Search
        results = vector_store.query(request.query, n_results=request.top_k, where={"user_id": current_user.id})
        
        if not results["ids"] or not results["ids"][0]:
            return []
            
        # 2. Fetch Rich Metadata from DB (Chunks)
        top_ids = results["ids"][0]
        distances = results["distances"][0] if results["distances"] else [0.0] * len(top_ids)
        
        # Create map of embedding_id -> distance/score
        # vector_store returns distance (smaller is better usually for euclidean, or 1-sim for cosine?)
        # Chromadb default is l2? or cosine? 
        # Assuming distance, convert to similarity score: 1 - distance (approx) or 1 / (1 + dist)
        # For simplicity, let's treat distance as "inverse score".
        
        # Async fetch
        query = select(Chunk).where(Chunk.embedding_id.in_(top_ids))
        db_res = await db.execute(query)
        chunks = db_res.scalars().all()
        chunk_map = {c.embedding_id: c for c in chunks}
        
        formatted_results = []
        
        for i, emb_id in enumerate(top_ids):
            chunk = chunk_map.get(emb_id)
            distance = distances[i]
            base_score = max(0, 1 - distance) # Simple conversion
            
            if chunk:
                # 3. Apply Re-ranking modifiers
                feedback_mod = 1 + (chunk.feedback_score or 0.0)
                trust_mod = chunk.trust_score or 0.5
                
                final_score = base_score * feedback_mod * (0.5 + trust_mod) # tuning
                
                # Enrich response
                meta = results["metadatas"][0][i]
                meta["summary"] = chunk.summary
                meta["generated_qas"] = chunk.generated_qas
                meta["trust_score"] = chunk.trust_score
                
                formatted_results.append(SearchResult(
                    text=chunk.text, # Return DB text which is reliable
                    score=final_score,
                    metadata=meta
                ))
            else:
                # Fallback if DB sync issue
                formatted_results.append(SearchResult(
                    text=results["documents"][0][i],
                    score=base_score,
                    metadata=results["metadatas"][0][i]
                ))
                
        # Sort by final score desc
        formatted_results.sort(key=lambda x: x.score, reverse=True)
        
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
