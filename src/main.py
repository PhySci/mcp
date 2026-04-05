from typing import List
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse
import argparse

from db import get_pg_connector


mcp = FastMCP(
    name="postgres_mcp",
    instructions="Provides tools for interaction with PostgresDB")


@mcp.tool(tags={"db"})
def get_all_tables() -> List[str]:
    """
    Returns list of tables in the DB
    """
    query = """
          SELECT table_name
          FROM information_schema.tables
          WHERE table_schema = 'public';
          """
    pg_connector = get_pg_connector()
    res = pg_connector.fetch_all(query)
    return [el["table_name"] for el in res]


@mcp.tool(tags={"db"})
def get_all_tables() -> List[str]:
    """
    Returns list of tables in the DB
    """
    query = """
          SELECT table_name
          FROM information_schema.tables
          WHERE table_schema = 'public';
          """
    pg_connector = get_pg_connector()
    res = pg_connector.fetch_all(query)
    return [el["table_name"] for el in res]




@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", dest="transport", default="stdio",
                        help="MCP transport")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = get_args()
    mcp.run(transport=args.transport)
