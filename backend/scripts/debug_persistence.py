import asyncio
import sys
import os
import json

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.db.session import AsyncSessionLocal
from app.models.chat import ChatMessage
from sqlalchemy.future import select

async def check_persistence():
    async with AsyncSessionLocal() as db:
        print("--- Checking Last 5 Messages ---")
        result = await db.execute(
            select(ChatMessage)
            .order_by(ChatMessage.created_at.desc())
            .limit(5)
        )
        messages = result.scalars().all()
        
        for msg in messages:
            print(f"\n[ID: {msg.id}] Role: {msg.role}")
            print(f"Content Preview: {msg.content[:50]}...")
            print(f"Meta Info Raw: {msg.meta_info}")
            
            if msg.meta_info:
                try:
                    data = json.loads(msg.meta_info)
                    sources = data.get("sources", [])
                    print(f"Parsed Sources Count: {len(sources)}")
                    if sources:
                        print(f"First Source Title: {sources[0].get('title')}")
                except Exception as e:
                    print(f"JSON Parse Error: {e}")
            else:
                print("No Meta Info")

if __name__ == "__main__":
    try:
        asyncio.run(check_persistence())
    except Exception as e:
        print(f"Error: {e}")
