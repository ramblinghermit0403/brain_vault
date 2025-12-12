from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MemoryBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None

class MemoryCreate(MemoryBase):
    pass

class MemoryUpdate(MemoryBase):
    pass

from typing import Union

class MemoryInDBBase(MemoryBase):
    id: Union[int, str]
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    type: str = "memory"
    status: str = "approved"
    task_type: Optional[str] = None
    source: Optional[str] = "manually_created"

    class Config:
        from_attributes = True

class Memory(MemoryInDBBase):
    pass
