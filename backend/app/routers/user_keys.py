from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.user import User
from app.models.client import AIClient
from app.schemas.client import AIClientCreate, AIClientResponse
from app.core.encryption import encryption_service

router = APIRouter()

@router.get("/llm-keys", response_model=List[AIClientResponse])
async def get_keys(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List connected LLM clients.
    """
    result = await db.execute(select(AIClient).where(AIClient.user_id == current_user.id))
    clients = result.scalars().all()
    return clients

@router.post("/llm-keys", response_model=AIClientResponse)
async def add_key(
    client_in: AIClientCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Add a new LLM provider key.
    """
    # 1. TODO: Validate Key with Provider (MUST 4)
    # For now, we trust the user input, but in production we should hit a "models" endpoint
    
    # 2. Encrypt Key
    encrypted_key = encryption_service.encrypt(client_in.api_key)
    
    client = AIClient(
        user_id=current_user.id,
        provider=client_in.provider,
        encrypted_api_key=encrypted_key,
        permissions=client_in.permissions
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    return client

@router.delete("/llm-keys/{client_id}")
async def delete_key(
    client_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Remove a connected LLM client.
    """
    result = await db.execute(select(AIClient).where(AIClient.id == client_id, AIClient.user_id == current_user.id))
    client = result.scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
        
    await db.delete(client)
    await db.commit()
    return {"status": "success", "message": "Key deleted"}
