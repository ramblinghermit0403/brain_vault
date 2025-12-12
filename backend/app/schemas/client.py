from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AIClientCreate(BaseModel):
    provider: str # "openai", "anthropic", "gemini"
    api_key: str
    permissions: Optional[Dict[str, bool]] = {"read": True, "write": False, "auto_save": False}

class AIClientResponse(BaseModel):
    id: int
    provider: str
    created_at: datetime
    permissions: Dict[str, bool]
    # Never return api_key
