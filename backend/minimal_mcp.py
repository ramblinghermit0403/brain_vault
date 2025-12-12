from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Minimal")

@mcp.tool()
async def ping() -> str:
    return "pong"

if __name__ == "__main__":
    mcp.run()
