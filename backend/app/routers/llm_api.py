from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api import deps
from app.models.user import User
from app.models.memory import Memory
from app.models.audit import AuditLog
from app.schemas.llm import LLMMemoryCreate, LLMMemoryUpdate, LLMMemoryResponse, ContextRequest, ContextResponse
from app.services.vector_store import vector_store
from app.services.websocket import manager
from app.services.context_builder import context_builder
from app.services.dedupe_job import dedupe_service
from app.services.metadata_extraction import metadata_service
from app.db.session import AsyncSessionLocal
from app.worker import process_memory_metadata_task, dedupe_memory_task, ingest_memory_task
import asyncio

router = APIRouter()

@router.post("/save_memory", response_model=LLMMemoryResponse)
async def save_memory(
    memory_in: LLMMemoryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Allow LLMs/Extensions to save memory. Respects Auto-Approve setting.
    """
    # 1. Determine Status
    auto_approve = True
    user_settings = current_user.settings
    if user_settings:
        if isinstance(user_settings, str):
            import json
            try:
                user_settings = json.loads(user_settings)
            except:
                user_settings = {}
        if isinstance(user_settings, dict):
            auto_approve = user_settings.get("auto_approve", True)
            
    status = "approved" if auto_approve else "pending"
    
    # 2. Determine Inbox Visibility
    # Logic:
    # - If Source is 'user-upload'/'manual', and auto-approved -> Don't show in inbox (it's implicit).
    # - If Source is 'user-upload', and pending -> Show in inbox.
    # - If Source is EXTERNAL (e.g. 'chatgpt', 'mcp'), -> ALWAYS show in inbox so user knows it happened (Notification).
    
    is_external = memory_in.source_llm not in ["user-upload", "user"]
    
    show_in_inbox = True 
    if not is_external and status == "approved":
        show_in_inbox = False # Skip inbox for manual approvals
        
    # 3. Create Memory
    memory = Memory(
        user_id=current_user.id,
        content=memory_in.content,
        title=f"Memory from {memory_in.source_llm}",
        source_llm=memory_in.source_llm,
        model_name=memory_in.model_name,
        status=status,
        tags=memory_in.tags,
        show_in_inbox=show_in_inbox,
        embedding_id=None # Will be updated if ingested
    )
    
    db.add(memory)
    
    # 3. Create Audit Log
    audit = AuditLog(
        actor=memory_in.source_llm,
        action="save_memory",
        details=f"Saved memory from {memory_in.url}",
        target_id=None # Will update after commit
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(memory)
    
    # Update audit with ID
    audit.target_id = str(memory.id)
    db.add(audit)
    await db.commit()
    
    # Ingest if approved via Celery
    if status == "approved":
        ingest_memory_task.delay(
            memory.id,
            current_user.id,
            memory_in.content,
            f"Memory from {memory_in.source_llm}",
            memory_in.tags,
            memory_in.source_llm
        )

    # 4. Trigger Dedupe Job (Background Celery)
    dedupe_memory_task.delay(memory.id)
    
    # 5. Trigger Auto-Tagging (Background Celery)
    process_memory_metadata_task.delay(memory.id, current_user.id)
    
    # 6. Broadcast via Websocket
    await manager.broadcast({
        "type": "new_memory", 
        "data": {
            "id": f"mem_{memory.id}", 
            "status": memory.status,
            "source": memory.source_llm
        }
    })
    
    return LLMMemoryResponse(
        id=f"mem_{memory.id}",
        status=memory.status,
        created_at=memory.created_at
    )

@router.put("/update_memory/{memory_id}", response_model=LLMMemoryResponse)
async def update_memory(
    memory_id: str,
    memory_in: LLMMemoryUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update memory content or status.
    """
    try:
        mem_id_int = int(memory_id.replace("mem_", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")

    result = await db.execute(select(Memory).where(Memory.id == mem_id_int, Memory.user_id == current_user.id))
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    # Update fields
    if memory_in.content:
        # TODO: Create History entry
        memory.content = memory_in.content
        memory.version += 1
        
    if memory_in.status:
        memory.status = memory_in.status
        # If status becomes approved, trigger ingestion
        if memory_in.status == "approved" and not memory.embedding_id:
            # Trigger ingestion (TODO: refactor ingestion to be callable here)
            pass
            
    if memory_in.tags:
        memory.tags = memory_in.tags

    await db.commit()
    await db.refresh(memory)
    
    return LLMMemoryResponse(
        id=f"mem_{memory.id}",
        status=memory.status,
        created_at=memory.created_at
    )

@router.delete("/delete_memory/{memory_id}")
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Soft delete (status=archived) or hard delete? User request said "Soft-delete"
    try:
        mem_id_int = int(memory_id.replace("mem_", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID")
        
    result = await db.execute(select(Memory).where(Memory.id == mem_id_int, Memory.user_id == current_user.id))
    memory = result.scalars().first()
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
        
    memory.status = "archived"
    
    # Remove from Vector DB if exists
    if memory.embedding_id:
        try:
            vector_store.delete(ids=[memory.embedding_id])
            memory.embedding_id = None
        except:
            pass
            
            
    await db.commit()
    return {"status": "success", "message": "Memory archived"}

@router.post("/retrieve_context", response_model=ContextResponse)
async def retrieve_context(
    request: ContextRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    ctx = context_builder.build_context(
        query=request.query,
        user_id=current_user.id,
        limit_tokens=request.limit_tokens or 2000
    )
    
    return ContextResponse(
        context_text=ctx["text"],
        snippets=ctx["snippets"],
        token_count=ctx["token_count"]
    )

# Simple In-Memory Cache for insights (reset on restart is fine)
# Key: user_id, Value: {"insights": [], "timestamp": datetime}
INSIGHTS_CACHE = {}

@router.get("/insights", response_model=List[str])
async def get_insights(
    limit: int = 10,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Generate simplified insights/highlights from recent memories.
    Cached for 1 hour per user.
    """
    # Check Cache
    cache_entry = INSIGHTS_CACHE.get(current_user.id)
    if cache_entry:
        age = datetime.utcnow() - cache_entry["timestamp"]
        if age < timedelta(hours=1):
            ids_in_cache = cache_entry.get("memory_count", 0)
            # If significant new memories added? (Skipping complexity for now)
            return cache_entry["insights"]
            
    # Fetch recent approved memories
    result = await db.execute(select(Memory).where(
        Memory.user_id == current_user.id,
        Memory.status == "approved"
    ).order_by(Memory.created_at.desc()).limit(20))
    memories = result.scalars().all()
    
    if not memories:
        return ["No recent memories to analyze. Add some notes to get started!"]
        
    # Construct Prompt
    # Convert memories to a simple text list
    content_list = []
    for mem in memories:
        content_list.append(f"- {mem.title}: {mem.content[:200]}...") # Truncate for tokens
        
    combined_content = "\n".join(content_list)
    
    # Get API Key
    from app.models.client import AIClient
    from app.core.encryption import encryption_service
    
    # Provider selection logic (reused)
    provider = "gemini"
    result = await db.execute(select(AIClient).where(AIClient.user_id == current_user.id, AIClient.provider == provider))
    client = result.scalars().first()
    if not client:
        provider = "openai"
        result = await db.execute(select(AIClient).where(AIClient.user_id == current_user.id, AIClient.provider == provider))
        client = result.scalars().first()
        
    api_key = None
    if client:
        try:
            api_key = encryption_service.decrypt(client.encrypted_api_key)
        except:
            pass
            
    if not api_key:
        return ["Please configure an AI provider in Settings to see insights."]
        
    # Call LLM
    prompt = f"""Analyze these recent notes and memories from the user:
{combined_content}

Generate 3-5 short, punchy 'Key Highlights' or 'Insights' that summarize what the user has been focusing on or thinking about.
Format: Return ONLY a JSON list of strings. Example: ["started learning vue", "worried about project deadline"]"""

    # Reuse LLM Service
    # We can reuse extract_metadata somewhat, or generate_response. 
    # generate_response expects a query and context.
    # Let's use generate_response with specific system prompt override if possible, 
    # but llm_service.generate_response is chatty.
    # Let's call llm_service.generate_response effectively.
    
    response_text = await llm_service.generate_response(
        query=prompt, 
        context=[], 
        provider=provider, 
        api_key=api_key
    )
    
    # Parse Response (Handle potential markdown wrap)
    clean_text = response_text.replace("```json", "").replace("```", "").strip()
    
    insights = []
    try:
        # Try to find list brackets
        import re
        match = re.search(r'\[.*\]', clean_text, re.DOTALL)
        if match:
            insights = json.loads(match.group())
        else:
             # Split by newlines if not JSON
             lines = clean_text.split('\n')
             insights = [line.strip('- ').strip() for line in lines if line.strip()]
    except:
        insights = ["Could not parse insights."]
        
    # Update Cache
    INSIGHTS_CACHE[current_user.id] = {
        "insights": insights, 
        "timestamp": datetime.utcnow(),
        "memory_count": len(memories)
    }
    
    return insights
