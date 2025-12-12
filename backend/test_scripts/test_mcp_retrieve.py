import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from mcp_server import retrieve_context
from app.db.session import SessionLocal

async def test_retrieve():
    print("Testing MCP Retrieve Context...")
    # Query for the memory we just created or general context
    query = "Direct MCP Test"
    print(f"Query: '{query}'")
    
    try:
        result = await retrieve_context(query)
        print("\n--- Retrieval Result ---")
        print(result)
        print("------------------------")
        
        if "Direct MCP Test Memory" in result:
            print("✅ Success: Retrieved expected memory content.")
        else:
            print("⚠️ Warning: Did not find the exact expected string. Check vector store indexing.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_retrieve())
