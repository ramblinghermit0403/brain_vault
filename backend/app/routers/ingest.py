from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl

from app.api import deps
from app.models.user import User
from app.models.memory import Memory
from app.services.web_ingestion import web_ingestion
from app.worker import ingest_memory_task, process_memory_metadata_task, dedupe_memory_task
import uuid

router = APIRouter()

class UrlIngestRequest(BaseModel):
    url: HttpUrl
    tags: list[str] = []

@router.post("/url")
async def ingest_url(
    request: UrlIngestRequest,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Ingest a webpage from a URL.
    Fetches content synchronously (API side) but processes embedding/vectorization in Celery.
    """
    url_str = str(request.url)
    
    # 1. Fetch Content (We do this here to fail fast if URL is bad)
    try:
        data = web_ingestion.fetch_url(url_str)
        if not data:
            raise HTTPException(status_code=400, detail="Could not extract content from URL")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch user URL: {str(e)}")

    # 2. Check User Settings for Auto-Approve
    auto_approve = True
    if current_user.settings:
        if isinstance(current_user.settings, dict):
            auto_approve = current_user.settings.get("auto_approve", True)
        elif isinstance(current_user.settings, str):
            import json
            try:
                s = json.loads(current_user.settings)
                auto_approve = s.get("auto_approve", True)
            except:
                pass
                
    initial_status = "approved" if auto_approve else "pending"
    show_in_inbox = True if initial_status == "pending" else False
    
    # 3. Create Memory Record
    memory = Memory(
        title=data["title"],
        content=data["content"],
        source_llm="web", # or 'url-ingest'
        user_id=current_user.id,
        tags=request.tags,
        embedding_id=str(uuid.uuid4()), # Placeholder
        status=initial_status,
        show_in_inbox=show_in_inbox
    )
    db.add(memory)
    await db.commit()
    await db.refresh(memory)
    
    # 4. Dispatch Celery Tasks
    # We always analyze metadata
    process_memory_metadata_task.delay(memory.id, current_user.id)
    
    # Only ingest (embed) if approved
    if initial_status == "approved":
        ingest_memory_task.delay(
            memory_id=memory.id,
            user_id=current_user.id,
            content=memory.content,
            title=memory.title,
            tags=request.tags,
            source="web"
        )
        # Dedupe check
        dedupe_memory_task.delay(memory.id)
        
    return {"status": "success", "memory_id": memory.id, "title": memory.title, "queued": True}
