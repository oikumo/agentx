from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GameServer")

@mcp.tool()
def get_games_by_year(year: int) -> str:
    """
    Get games by year

    Args:
        year: Year required

    Returns:
        Games of the year
    """
    return "Darksouls"


if __name__ == "__main__":
    print("> game mcp server")
    mcp.run(transport="stdio")
