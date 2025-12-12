from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    source: Optional[str] = None
    tags: Optional[List[str]] = []

class DocumentCreate(DocumentBase):
    pass

class DocumentInDBBase(DocumentBase):
    id: int
    user_id: int
    file_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    pass

class ChunkBase(BaseModel):
    text: str
    chunk_index: int

class ChunkCreate(ChunkBase):
    document_id: int
    embedding_id: Optional[str] = None
    metadata_json: Optional[Any] = None

class Chunk(ChunkBase):
    id: int
    document_id: int

    class Config:
        from_attributes = True
