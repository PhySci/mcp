# Postgres MCP server

An [FastMCP](https://github.com/jlowin/fastmcp)-based MCP server for PostgreSQL metadata (table lists, etc.). Default transport is **stdio** (for Cursor/IDE); with HTTP transport, `GET /health` is available.

**Requirements:** Python 3.14+, [uv](https://github.com/astral-sh/uv), and a running PostgreSQL instance.

## Install

```bash
git clone <url> mccp && cd mccp
uv sync
```

## Database configuration

By default, `env/local.ini` is read (path is relative to the repo root, not the current working directory). Copy the example and set your values:

```ini
db_host=localhost
db_port=5432
db_name=your_db
db_user=postgres
db_password=secret
```

The same settings can be passed via environment variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` or CLI flags `--db_host`, `--db_port`, etc. (see `python src/main.py --help`).

## Run the server

```bash
uv run python src/main.py -t stdio
```

Other FastMCP transports: `-t http`, `-t sse`, and so on. Logs go to a file (default `logs/mccp.log`); override with `--log_file`.

For quick DB checks without MCP, use `uv run python src/r.py` — it uses the same config and calls the tools directly.

## Tests

```bash
uv run python -m unittest src.tests.process_stdio -v
```

These integration tests spawn `src/main.py` as a stdio subprocess; you need a reachable database configured in `env/local.ini`.