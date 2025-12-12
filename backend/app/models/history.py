from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base

class MemoryHistory(Base):
    __tablename__ = "memory_history"

    id = Column(Integer, primary_key=True, index=True)
    memory_id = Column(Integer, ForeignKey("memories.id"), nullable=False)
    old_content = Column(Text, nullable=True)
    new_content = Column(Text, nullable=True)
    actor = Column(String, nullable=False) # "user" or client_id/model_name
    actor_type = Column(String, default="user") # "user", "ai"
    change_type = Column(String, nullable=False) # "create", "update", "delete", "merge"
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
