import asyncio
from mcp_server import save_memory, search_memory

async def test_live():
    print("🧪 Starting Live MCP Test...\n")

    # 1. Test Saving a Memory
    print("1️⃣  Testing save_memory()...")
    save_result = await save_memory(
        text="Antigravity is testing the MCP server integration. It works seamlessly!",
        tags=["test", "mcp", "antigravity"]
    )
    print(f"   Result: {save_result}\n")

    # 2. Test Searching for that Memory
    print("2️⃣  Testing search_memory()...")
    search_result = await search_memory(query="Antigravity MCP test", top_k=1)
    print(f"   Result:\n{search_result}\n")

    print("✅ Live Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_live())
