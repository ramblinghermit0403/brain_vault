import asyncio
from mcp_server import mcp

async def verify():
    print("Verifying MCP Server...")
    
    # Check if tools are registered
    # FastMCP stores tools in ._tool_manager or similar, but let's check the public API if possible
    # Or just check if the functions are decorated
    
    tools = [t.name for t in mcp._tool_manager.list_tools()]
    print(f"Registered Tools: {tools}")
    
    expected_tools = ["search_memory", "save_memory", "get_document"]
    missing = [t for t in expected_tools if t not in tools]
    
    if missing:
        print(f"FAILED: Missing tools: {missing}")
        exit(1)
    
    print("SUCCESS: All tools registered.")

if __name__ == "__main__":
    asyncio.run(verify())
