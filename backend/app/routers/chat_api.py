from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from pydantic import BaseModel
from datetime import datetime

from app.api import deps
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.services.agent_service import agent_service
from app.services.llm_service import llm_service
from app.db.session import AsyncSessionLocal

router = APIRouter()

async def update_chat_title_task(session_id: int, context: str):
    """
    Background task to update chat session title using LLM.
    """
    async with AsyncSessionLocal() as db:
        try:
            # Generate title
            title = await llm_service.generate_chat_title(context)
            
            # Update session
            result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
            session = result.scalars().first()
            if session:
                session.title = title
                session.updated_at = datetime.utcnow()
                await db.commit()
                print(f"Updated title for session {session_id} to: {title}")
        except Exception as e:
            print(f"Background Title Update Failed: {e}")


# Schemas
class ChatSessionCreate(BaseModel):
    title: str = "New Chat"

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Source(BaseModel):
    title: str
    id: str | None = None

class ChatMessageCreate(BaseModel):
    content: str
    model: str = "gpt-3.5-turbo" # Default
    temperature: float = 0.7
    max_tokens: int = 2048
    
class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime
    sources: List[Source] = [] # List of source objects
    
    class Config:
        from_attributes = True


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    session_in: ChatSessionCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Create a new chat session."""
    session = ChatSession(
        user_id=current_user.id,
        title=session_in.title
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """List user's chat sessions."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/sessions/{session_id}/message", response_model=ChatMessageResponse)
async def send_message(
    session_id: int,
    message_in: ChatMessageCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Send a message to the agent."""
    # 1. Verify Session Ownership
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # 2. Process with Agent (This automatically saves User and AI message to DB via SQLChatMessageHistory)
    # Note: AgentService handles db saves internally for messages.
    
    # Process with Agent
    response = await agent_service.process_message(
        session_id=session_id,
        user_id=current_user.id,
        message=message_in.content,
        model=message_in.model,
        temperature=message_in.temperature,
        max_tokens=message_in.max_tokens
    )
    
    response_text = response.get("output", "")
    sources = response.get("sources", [])
    
    # Update Session Timestamp
    session.updated_at = datetime.utcnow()
    await db.commit()

    # Background Title Generation (only if title is default)
    if session.title == "New Chat":
        context = f"User: {message_in.content}\nAI: {response_text}"
        background_tasks.add_task(update_chat_title_task, session_id, context)
    
    return ChatMessageResponse(
        id=0, # Placeholder
        role="assistant",
        content=response_text,
        created_at=datetime.utcnow(),
        sources=sources
    )


@router.get("/sessions/{session_id}/history", response_model=List[ChatMessageResponse])
async def get_history(
    session_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """Get message history."""
    # Verify
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id))
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    return result.scalars().all()


@router.delete("/sessions", status_code=204, response_class=Response)
async def delete_sessions(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """Delete all chat sessions for the current user."""
    # Get all session IDs
    result = await db.execute(select(ChatSession.id).where(ChatSession.user_id == current_user.id))
    session_ids = result.scalars().all()
    
    if session_ids:
         # Delete messages for these sessions
        await db.execute(
            delete(ChatMessage).where(ChatMessage.session_id.in_(session_ids))
        )
        # Delete sessions
        await db.execute(
            delete(ChatSession).where(ChatSession.user_id == current_user.id)
        )
        await db.commit()
    
    return Response(status_code=204)
