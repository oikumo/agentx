from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-server-products")

INVENTORY = {
    "laptop-pro": {"price": 1200, "stock": 5},
    "teclado-mecanico": {"price": 89, "stock": 0},
}


@mcp.tool()
def get_products() -> str:
    """Lists all SKUs available in the inventory"""
    skus = ", ".join(INVENTORY.keys())
    return f"SKUs: {skus}"


@mcp.tool()
def get_product_by_sku(sku: str) -> str:
    """
    Queries the price and stock of a product.

    Args:
        sku: The product identifier. Use it exactly as it appears in get_products.
    """
    product = INVENTORY.get(sku)
    if not product:
        return f"Product '{sku}' not found"
    return f"SKU: {sku} | Price: ${product['price']} | Stock: {product['stock']}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
    # mcp.run(transport="streamable-http")
