from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    provider: str = "openai"
    api_key: str
    top_k: int = 5
    filter: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    context: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat_with_llm(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Chat with LLM using retrieved context.
    """
    try:
        # 1. Retrieve context
        where_clause = {"user_id": current_user.id}
        if request.filter:
            # Ensure IDs are integers
            if "document_id" in request.filter:
                try:
                    request.filter["document_id"] = int(request.filter["document_id"])
                except:
                    pass
            if "memory_id" in request.filter:
                try:
                    request.filter["memory_id"] = int(request.filter["memory_id"])
                except:
                    pass
                    
            # ChromaDB requires $and for multiple conditions
            where_clause = {
                "$and": [
                    {"user_id": current_user.id},
                    request.filter
                ]
            }
            
        results = vector_store.query(request.query, n_results=request.top_k, where=where_clause)
        
        context = []
        if results["documents"]:
             context = results["documents"][0]

        # 2. Generate response
        response = await llm_service.generate_response(
            query=request.query,
            context=context,
            provider=request.provider,
            api_key=request.api_key
        )
        
        return ChatResponse(response=response, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
