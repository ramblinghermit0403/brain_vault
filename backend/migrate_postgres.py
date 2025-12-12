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

async def migrate():
    url = settings.DATABASE_URL
    print(f"Original URL Schema: {url.split(':')[0]}")
    
    # create_async_engine requires an async driver. 
    # If the URL is just postgresql://, we must switch to postgresql+asyncpg://
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://")
        print("Switched to postgresql+asyncpg:// for async engine.")

    if 'sqlite' in url:
        print("WARNING: Using SQLite. If you expected Postgres, .env is not loaded correctly.")
    
    engine = create_async_engine(url)
    
    async with engine.begin() as conn:
        print("Attempting to add 'name' column to users table...")
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN name TEXT;"))
            print("Successfully added 'name' column.")
        except Exception as e:
            print(f"Column add failed (likely already exists): {e}")

    await engine.dispose()

if __name__ == "__main__":
    # Ensure usage of correct loop policy for Windows if needed
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(migrate())
