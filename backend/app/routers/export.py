from typing import Any
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import json

from app.api import deps
from app.models.user import User
from app.models.memory import Memory
from app.models.document import Document

router = APIRouter()

@router.get("/json")
async def export_json(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result_mem = await db.execute(select(Memory).where(Memory.user_id == current_user.id))
    memories = result_mem.scalars().all()
    
    result_doc = await db.execute(select(Document).where(Document.user_id == current_user.id))
    documents = result_doc.scalars().all()
    
    data = {
        "memories": [
            {
                "id": m.id,
                "title": m.title,
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None
            } for m in memories
        ],
        "documents": [
            {
                "id": d.id,
                "title": d.title,
                "source": d.source,
                "file_type": d.file_type,
                "created_at": d.created_at.isoformat() if d.created_at else None
            } for d in documents
        ]
    }
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=brain_vault_export.json"}
    )

@router.get("/md")
async def export_markdown(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    result_mem = await db.execute(select(Memory).where(Memory.user_id == current_user.id))
    memories = result_mem.scalars().all()
    
    result_doc = await db.execute(select(Document).where(Document.user_id == current_user.id))
    documents = result_doc.scalars().all()
    
    md_content = f"# Brain Vault Export for {current_user.email}\n\n"
    
    md_content += "## Memories\n\n"
    for m in memories:
        md_content += f"### {m.title}\n{m.content}\n\n"
        
    md_content += "## Documents\n\n"
    for d in documents:
        md_content += f"### {d.title}\nSource: {d.source}\n\n"
        # We could add chunk content here if we wanted
        
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=brain_vault_export.md"}
    )
