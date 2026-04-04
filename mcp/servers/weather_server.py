from typing import List
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "Hot as hell"

if __name__ == "__main__":
    print("> weather mcp server streamable-http")
    mcp.run(transport="streamable-http")