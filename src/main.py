from docutils.nodes import description
from fastmcp import FastMCP

mcp = FastMCP(
    name="postgres_mcp",
    instructions="Provides tools for interaction with PostgresDB")

@mcp.tool
def mutiply(a: float, b: float) -> float:
    """
    Multiplies two numbers together
    """


if __name__ == "__main__":
    mcp.run(transport="http")