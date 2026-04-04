from mcp.server import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("> add")
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("> multy")
    return a * b

@mcp.tool()
def ok() -> None:
    """print ok"""
    print("> ok")


if __name__ == "__main__":
    print("> math mcp server")
    mcp.run(transport="stdio")
