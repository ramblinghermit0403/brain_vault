import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Add backend directory to path
sys.path.append(os.getcwd())
load_dotenv(os.path.join(os.getcwd(), 'backend', '.env'))

from app.core.config import settings

async def check_data():
    url = settings.DATABASE_URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
    
    print(f"Checking DB: {url.split('@')[1] if '@' in url else url}")
    engine = create_async_engine(url)
    
    async with engine.begin() as conn:
        print("Checking Users...")
        result = await conn.execute(text("SELECT count(*) FROM users;"))
        user_count = result.scalar()
        print(f"Total Users: {user_count}")
        
        print("Checking Memories...")
        result = await conn.execute(text("SELECT count(*) FROM memories;"))
        mem_count = result.scalar()
        print(f"Total Memories: {mem_count}")
        
        if mem_count > 0:
            print("Listing first 5 memories status:")
            result = await conn.execute(text("SELECT id, title, status, user_id FROM memories LIMIT 5;"))
            for row in result:
                print(row)

    await engine.dispose()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_data())
