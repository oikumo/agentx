from mcp.server.fastmcp import FastMCP

mcp = FastMCP("knowledge_base")

INVENTARIO = {
    "laptop-pro": {"precio": 1200, "stock": 5},
    "teclado-mecanico": {"precio": 89, "stock": 0},
}

@mcp.tool()
def listar_productos() -> str:
    """Lista todos los SKUs disponibles en el inventario"""
    skus = ", ".join(INVENTARIO.keys())
    return f"SKUs disponibles: {skus}"

@mcp.tool()
def consultar_producto(sku: str) -> str:
    """
    Consulta precio y stock de un producto.

    Args:
        sku: El identificador del producto. Úsalo exactamente como aparece en listar_productos.
    """
    producto = INVENTARIO.get(sku)
    if not producto:
        return f"Producto '{sku}' no encontrado"
    return f"SKU: {sku} | Precio: ${producto['precio']} | Stock: {producto['stock']}"

def main() -> None:
    mcp.run(transport="stdio")
    # mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
