from mcp.server.fastmcp import FastMCP
import inspect

print("Attributes of FastMCP:")
for attr in dir(FastMCP):
    if not attr.startswith("_"):
        print(attr)

try:
    mcp = FastMCP("test")
    print("\nInstance Attributes:")
    for attr in dir(mcp):
        if not attr.startswith("_"):
            print(attr)
except:
    pass
