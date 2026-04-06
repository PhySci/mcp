from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import configargparse
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import PlainTextResponse

from db import get_pg_connector

logger = logging.getLogger(__name__)


def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        force=True,
    )


mcp = FastMCP(
    name="postgres_mcp",
    instructions="Provides tools for interaction with PostgresDB")


@mcp.tool(tags={"db"})
def get_all_tables() -> List[str]:
    """
    Returns list of tables in the DB
    """
    logger.info("Call get_all_tables tool")
    query = """
          SELECT table_name AS tn
          FROM information_schema.tables
          WHERE table_schema = 'public';
          """
    pg_connector = get_pg_connector()
    res = pg_connector.fetch_all(query)
    logger.info("get_all_tables tool: %s", repr(res))
    return [el["tn"] for el in res]


@mcp.tool(tags={"db"})
def get_table_columns(table_name: str) -> str:
    """
    Returns list of columns in the given table
    """
    query = """
          SELECT column_name, data_type, is_nullable
          FROM information_schema.columns
          WHERE table_name = %s;
          """
    pg_connector = get_pg_connector()
    res = pg_connector.fetch_all(query, (table_name,))

    columns = [{
        "name": el["column_name"],
        "type": el["data_type"],
        "is_nullable": el["is_nullable"]
        } for el in res]
    return columns

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    return PlainTextResponse("OK")


def get_args():
    _default_ini = Path(__file__).resolve().parent.parent / "env" / "local.ini"
    parser = configargparse.ArgumentParser(
        default_config_files=[str(_default_ini)],
    )
    parser.add_argument("-t",
                        dest="transport",
                        default="stdio",
                        help="MCP transport")

    parser.add_argument("--db_host",
                        default="localhost",
                        env_var="DB_HOST",
                        help="Database host")

    parser.add_argument("--db_port",
                        default=5432,
                        env_var="DB_PORT",
                        help="Database port")

    parser.add_argument("--db_user",
                        default="postgres",
                        env_var="DB_USER",
                        help="Database user")

    parser.add_argument("--db_password",
                        default="postgres",
                        env_var="DB_PASSWORD",
                        help="Database password")

    parser.add_argument("--db_name",
                        default="postgres",
                        env_var="DB_NAME",
                        help="Database name")

    parser.add_argument(
        "--log_file",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "logs" / "mccp.log",
        help="Path to application log file",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    setup_logging(args.log_file)
    logger.info(
        "Starting MCP server (transport=%s, log_file=%s)",
        args.transport,
        args.log_file,
    )
    db_params = {
        "host": args.db_host,
        "port": args.db_port,
        "user": args.db_user,
        "password": args.db_password,
        "dbname": args.db_name,
    }
    _ = get_pg_connector(db_params)
    mcp.run(transport=args.transport)
