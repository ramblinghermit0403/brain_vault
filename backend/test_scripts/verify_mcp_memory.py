import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.memory import Memory
from mcp_server import save_memory

async def run_test():
    print("--- Verifying MCP Memory Saving ---")
    db = SessionLocal()
    
    try:
        # 1. Setup User with Auto-Approve = True
        user = db.query(User).first()
        if not user:
            print("No user found, skipping.")
            return

        print(f"User: {user.email}")
        
        # Ensure Settings are Auto-Approve=True
        current_settings = user.settings or {}
        if isinstance(current_settings, str):
            import json
            current_settings = json.loads(current_settings)
            
        current_settings["auto_approve"] = True
        user.settings = current_settings
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "settings")
        db.commit()
        
        # 2. Call MCP save_memory
        print("Saving memory via MCP (Auto-Approve=True)...")
        res = await save_memory("MCP Test Memory Auto-Approve", source="mcp_test", tags=["test"])
        print(f"Result: {res}")
        
        if "(Status: approved)" in res:
            print("SUCCESS: Memory auto-approved.")
        else:
            print(f"FAILURE: Memory NOT auto-approved. Result: {res}")
            
        # Verify Ingestion (Check if valid ID returned)
        
        # 3. Disable Auto-Approve
        print("\n--- Testing Auto-Approve = False ---")
        current_settings["auto_approve"] = False
        user.settings = current_settings
        flag_modified(user, "settings")
        db.commit()
        
        print("Saving memory via MCP (Auto-Approve=False)...")
        res = await save_memory("MCP Test Memory Pending", source="mcp_test")
        print(f"Result: {res}")
        
        if "(Status: pending)" in res:
             print("SUCCESS: Memory is pending.")
        else:
             print(f"FAILURE: Memory status incorrect. Result: {res}")

    finally:
        db.close()
        print("\nTest Complete.")

if __name__ == "__main__":
    asyncio.run(run_test())
