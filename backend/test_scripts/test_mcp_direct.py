import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from mcp_server import save_memory, get_db
from app.db.session import SessionLocal
from app.models.memory import Memory

async def test_save():
    print("Simulating MCP Save...")
    result = await save_memory("Direct MCP Test Memory", source="debug_script")
    print(f"Result: {result}")
    
    # Verify in DB
    db = SessionLocal()
    # Check for latest memory
    mem = db.query(Memory).order_by(Memory.id.desc()).first()
    if mem and mem.content == "Direct MCP Test Memory":
        print(f"✅ Verified in DB! ID: {mem.id} | User: {mem.user_id} | Status: {mem.status}")
    else:
        print(f"❌ Not found. Latest memory: {mem.id if mem else 'None'}")
    db.close()

if __name__ == "__main__":
    asyncio.run(test_save())
