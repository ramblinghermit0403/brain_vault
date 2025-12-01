from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

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
def search_documents(
    request: SearchRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Search for relevant document chunks.
    """
    try:
        results = vector_store.query(request.query, n_results=request.top_k, where={"user_id": current_user.id})
        
        # Format results
        formatted_results = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                # Filter by user_id if we stored it in metadata, or we need to filter post-query
                # For MVP, we assume user isolation is handled or we filter here if metadata has user_id
                # Current ingestion implementation puts document_id in metadata.
                # We should verify document ownership.
                
                metadata = results["metadatas"][0][i]
                # TODO: Verify document belongs to user.
                # For now, we trust the vector store results but in prod we must filter.
                
                formatted_results.append(SearchResult(
                    text=doc,
                    score=results["distances"][0][i] if results["distances"] else 0.0,
                    metadata=metadata
                ))
                
        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
