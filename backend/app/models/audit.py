from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String, nullable=False)
    action = Column(String, nullable=False) # "save_memory", "approve_memory", "connect_llm"
    target_id = Column(String, nullable=True) # ID of memory/client
    details = Column(Text, nullable=True) # JSON string of details
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
