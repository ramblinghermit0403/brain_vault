from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.user import User
from app.models.memory import Memory
from app.services.vector_store import vector_store
from app.services.ingestion import ingestion_service
from app.services.websocket import manager
from app.worker import ingest_memory_task
import asyncio
from pydantic import BaseModel

router = APIRouter()

class InboxItem(BaseModel):
    id: str
    content: str
    source: str
    created_at: Any
    status: str
    details: Optional[str] = None
    similarity_score: float = 0.0 
    task_type: Optional[str] = None
    tags: Optional[List[str]] = None
    
class InboxAction(BaseModel):
    action: str # "approve", "discard", "edit", "dismiss"
    payload: Any = None # If edit, new content

@router.get("/", response_model=List[InboxItem])
async def get_inbox(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    List pending memories.
    """
    result = await db.execute(
        select(Memory).where(
            Memory.user_id == current_user.id,
            Memory.show_in_inbox == True
        ).order_by(Memory.created_at.desc())
    )
    memories = result.scalars().all()
    
    results = []
    for mem in memories:
        results.append(InboxItem(
            id=f"mem_{mem.id}",
            content=mem.content,
            source=mem.source_llm or "unknown",
            created_at=mem.created_at,
            status=mem.status,
            details=mem.title,
            task_type=mem.task_type,
            tags=mem.tags
        ))
        
    return results

@router.post("/{memory_id}/action")
async def inbox_action(
    memory_id: str,
    action_in: InboxAction,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Approve, Discard or Edit a pending memory.
    """
    try:
        mem_id_int = int(memory_id.replace("mem_", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.execute(select(Memory).where(
        Memory.id == mem_id_int, 
        Memory.user_id == current_user.id
    ))
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
        
    if action_in.action == "approve":
        memory.status = "approved"
        memory.show_in_inbox = False
        await db.commit()
        await db.refresh(memory)
        
        # ingest logic via Celery
        ingest_memory_task.delay(
            memory.id, 
            current_user.id, 
            memory.content, 
            memory.title,
            memory.tags,
            memory.source_llm
        )
        
        await manager.broadcast({"type": "inbox_update", "id": memory_id, "action": "approve"})
        return {"status": "approved", "id": memory_id}
        
    elif action_in.action == "discard":
        memory.status = "discarded"
        
        # Ensure it's removed from Vector DB
        if memory.embedding_id:
            try:
                vector_store.delete(ids=[memory.embedding_id])
                memory.embedding_id = None
            except:
                pass
                
        await db.commit()
        await manager.broadcast({"type": "inbox_update", "id": memory_id, "action": "discard"})
        return {"status": "discarded", "id": memory_id}
        
    elif action_in.action == "edit":
        if not action_in.payload or "content" not in action_in.payload:
            raise HTTPException(status_code=400, detail="Missing content for edit")
            
        memory.content = action_in.payload["content"]
        memory.status = "approved" 
        
        await db.commit()
        await db.refresh(memory)
        
        await db.commit()
        await db.refresh(memory)
        
        # ingest via Celery
        ingest_memory_task.delay(
            memory.id, 
            current_user.id, 
            memory.content, 
            memory.title,
            memory.tags,
            memory.source_llm
        )
            
        await manager.broadcast({"type": "inbox_update", "id": memory_id, "action": "edit"})
        return {"status": "approved_edited", "id": memory_id}
        
    elif action_in.action == "dismiss":
        # Just hide from inbox
        memory.show_in_inbox = False
        await db.commit()
        await manager.broadcast({"type": "inbox_update", "id": memory_id, "action": "dismiss"})
        return {"status": memory.status, "id": memory_id}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@router.get("/{memory_id}", response_model=InboxItem)
async def get_inbox_item(
    memory_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get a single pending memory.
    """
    try:
        mem_id_int = int(memory_id.replace("mem_", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.execute(select(Memory).where(
        Memory.id == mem_id_int, 
        Memory.user_id == current_user.id
    ))
    memory = result.scalars().first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
        
    return InboxItem(
        id=f"mem_{memory.id}",
        content=memory.content,
        source=memory.source_llm or "unknown",
        created_at=memory.created_at,
        status=memory.status,
        details=memory.title,
        task_type=memory.task_type,
        tags=memory.tags
    )

class InboxUpdate(BaseModel):
    content: str
    title: Optional[str] = None
    tags: Optional[List[str]] = None

@router.put("/{memory_id}")
async def update_inbox_item(
    memory_id: str,
    data: InboxUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update a pending memory content without approving.
    """
    try:
        mem_id_int = int(memory_id.replace("mem_", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.execute(select(Memory).where(
        Memory.id == mem_id_int, 
        Memory.user_id == current_user.id
    ))
    memory = result.scalars().first()
    
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
        
    memory.content = data.content
    if data.title:
        memory.title = data.title
    
    if data.tags is not None:
        memory.tags = data.tags
        
    await db.commit()
    await db.refresh(memory)
    
    # Broadcast update
    await manager.broadcast({"type": "inbox_update", "id": memory_id, "action": "update"})
    
    return {"status": "success", "id": memory_id}
