from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import Optional, Dict

from app.api import deps
from app.models.feedback import FeedbackEvent
from app.models.document import Chunk

router = APIRouter()

class FeedbackCreate(BaseModel):
    chunk_id: int
    event_type: str # click, insert, thumbs_up, thumbs_down, dismiss
    context: Optional[Dict] = None
    document_id: Optional[int] = None

@router.post("/", response_model=Dict)
async def submit_feedback(
    feedback_in: FeedbackCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """
    Submit user feedback for a search result (chunk).
    Updates the chunk's feedback_score immediately.
    """
    # 1. Log the event
    event = FeedbackEvent(
        user_id=current_user.id,
        chunk_id=feedback_in.chunk_id,
        document_id=feedback_in.document_id,
        event_type=feedback_in.event_type,
        context=feedback_in.context
    )
    db.add(event)
    
    # 2. Update Chunk Score
    score_map = {
        "click": 0.1,
        "insert": 0.5,
        "thumbs_up": 1.0,
        "thumbs_down": -1.0,
        "dismiss": -0.5
    }
    
    delta = score_map.get(feedback_in.event_type, 0.0)
    
    if delta != 0:
        result = await db.execute(select(Chunk).where(Chunk.id == feedback_in.chunk_id))
        chunk = result.scalars().first()
        if chunk:
            # Simple additive score for now
            chunk.feedback_score = (chunk.feedback_score or 0.0) + delta
            # Optional: Add decay or normalization here? 
            # Keeping it simple as per plan: "Short-term reweighting logic... use feedback_score in ranking"
            db.add(chunk)
            
    await db.commit()
    
    return {"status": "active", "score_delta": delta}
