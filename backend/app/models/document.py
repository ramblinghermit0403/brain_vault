from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, index=True)
    content = Column(Text, nullable=True)  # Full text content for memories or extracted text
    source = Column(String, nullable=True)  # filename, URL, or null for memories
    file_type = Column(String, nullable=True)  # pdf, docx, txt, md, or null for memories
    doc_type = Column(String, default="file", nullable=False)  # 'file' or 'memory'
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    user = relationship("User", backref="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    chunk_index = Column(Integer)
    text = Column(Text, nullable=False)
    embedding_id = Column(String) # ID in Vector DB
    metadata_json = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    generated_qas = Column(JSON, nullable=True)
    tokens_count = Column(Integer, nullable=True)
    trust_score = Column(Float, default=0.5)
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    feedback_score = Column(Float, default=0.0)
    entities = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="chunks")
