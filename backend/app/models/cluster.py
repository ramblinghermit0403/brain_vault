from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, Float
from sqlalchemy.sql import func
from app.db.base import Base

class MemoryCluster(Base):
    __tablename__ = "memory_clusters"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # We store the IDs of memories in this cluster as a JSON list
    memory_ids = Column(JSON, nullable=False) 
    
    # The proposed centroid or representative text
    representative_text = Column(String, nullable=True)
    
    avg_similarity = Column(Float, default=0.0)
    status = Column(String, default="pending") # "pending", "merged", "dismissed"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
