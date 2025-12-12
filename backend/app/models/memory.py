from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from app.models.user import User

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSON, nullable=True)
    embedding_id = Column(String) # ID in Vector DB
    
    # Universal Memory Fields
    source_llm = Column(String, default="user") # "user", "chatgpt", "claude", "gemini"
    model_name = Column(String, nullable=True) # e.g. "gpt-4", "claude-3-opus"
    importance_score = Column(Float, default=0.0)
    status = Column(String, default="approved") # "pending", "approved", "merged", "discarded", "archived"
    
    # Inbox Visibility: Should this show up in the inbox?
    show_in_inbox = Column(Boolean, default=True)
    
    task_type = Column(String, nullable=True) # "general", "code", "summary"
    version = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="memories")
