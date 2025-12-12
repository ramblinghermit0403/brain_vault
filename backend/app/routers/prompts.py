from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.services.vector_store import vector_store
from app.services.ingestion import ingestion_service

router = APIRouter()

class PromptGenerationRequest(BaseModel):
    query: str
    template_id: str = "standard"
    context_size: int = 2000 # Token limit for context
    include_pii: bool = False

class PromptGenerationResponse(BaseModel):
    prompt: str
    context_used: List[str]
    token_count: int

@router.post("/generate", response_model=PromptGenerationResponse)
@router.post("/generate", response_model=PromptGenerationResponse)
async def generate_prompt(
    request: PromptGenerationRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Generate a polished prompt with retrieved context.
    """
    # 1. Retrieve Context
    # We use a higher top_k to get enough candidates, then filter/truncate
    results = vector_store.query(request.query, n_results=10, where={"user_id": current_user.id})
    
    retrieved_texts = []
    if results["documents"]:
        retrieved_texts = results["documents"][0]
        
    # 2. Compact Context (Token Budgeting)
    selected_context = []
    current_tokens = 0
    
    for text in retrieved_texts:
        tokens = ingestion_service.count_tokens(text)
        if current_tokens + tokens > request.context_size:
            break
        selected_context.append(text)
        current_tokens += tokens
        
    context_str = "\n\n---\n\n".join(selected_context)
    
    # 3. Apply Template
    if request.template_id == "code":
        template = f"""You are an expert coding assistant. Use the following context to answer the user's request.

CONTEXT:
{context_str}

USER REQUEST:
{request.query}

INSTRUCTIONS:
- Provide clear, efficient code.
- Explain your reasoning.
"""
    elif request.template_id == "summary":
        template = f"""Please summarize the following information based on the user's query.

CONTEXT:
{context_str}

QUERY:
{request.query}
"""
    else: # Standard
        template = f"""Use the following memory context to answer the question.

MEMORY CONTEXT:
{context_str}

QUESTION:
{request.query}
"""

    total_tokens = ingestion_service.count_tokens(template)

    return PromptGenerationResponse(
        prompt=template,
        context_used=selected_context,
        token_count=total_tokens
    )
