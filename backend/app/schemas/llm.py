from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class LLMMemoryCreate(BaseModel):
    content: str
    source_llm: str # "chatgpt", "claude", "extension", etc.
    model_name: Optional[str] = None
    url: Optional[str] = None
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}

class LLMMemoryUpdate(BaseModel):
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None # "approved", "discarded"

class LLMMemoryResponse(BaseModel):
    id: str
    status: str
    created_at: datetime

class ContextRequest(BaseModel):
    query: str
    task_type: Optional[str] = "general" # "code", "creative", "fact-check"
    limit_tokens: Optional[int] = 2000
    compression_level: Optional[str] = "medium" # "low", "medium", "high"

class ContextResponse(BaseModel):
    context_text: str
    snippets: List[str]
    token_count: int
