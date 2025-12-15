from app.db.base import Base
from app.db.session import engine
from app.models.user import User
from app.models.document import Document
from app.models.memory import Memory
from app.models.client import AIClient
from app.models.history import MemoryHistory
from app.models.audit import AuditLog
from app.models.cluster import MemoryCluster
from app.models.chat import ChatSession, ChatMessage

import asyncio

async def init():
    print("Creating database tables...")
    from app.db.session import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

if __name__ == "__main__":
    asyncio.run(init())
