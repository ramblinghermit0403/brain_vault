from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class AIClient(Base):
    __tablename__ = "ai_clients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False) # "openai", "anthropic", "google"
    encrypted_api_key = Column(String, nullable=False)
    permissions = Column(JSON, default={}) # {"read": True, "write": False, "auto_save": False}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
