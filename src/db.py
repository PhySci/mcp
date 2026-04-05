"""PostgreSQL connectivity for the MCP server."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator, Dict
import logging

import psycopg
from psycopg import Connection
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row


_pg_connector = None
_logger = logging.getLogger(__name__)

class PostgresConnector:
    """
    PostgreSQL connector. ``params`` is passed to ``psycopg.connect`` (either
    keyword-style arguments such as ``host``, ``port``, ``user``, ``password``,
    ``dbname``, or a ``conninfo`` URI string among the keys).
    """

    def __init__(self, params: dict[str, Any]) -> None:
        if not params:
            raise ValueError("params must not be empty")
        self._params = dict(params)

    @property
    def dsn(self) -> str:
        """Connection string derived from ``params`` (may include secrets)."""
        return make_conninfo(**self._params)

    @contextmanager
    def connection(self, *, autocommit: bool = False) -> Iterator[Connection[Any]]:
        """
        Context-managed connection: commit on success, rollback on error.
        Use autocommit=True for read-only SELECT workloads.
        """
        conn = psycopg.connect(**self._params, autocommit=autocommit)
        try:
            yield conn
            if not autocommit:
                conn.commit()
        except Exception:
            if not autocommit:
                conn.rollback()
            raise
        finally:
            conn.close()

    def fetch_all(
        self,
        sql: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
        *,
        as_dicts: bool = True,
    ) -> list[dict[str, Any]] | list[tuple[Any, ...]]:
        """SELECT: return all rows."""
        _logger.debug("Get SQL request: %s", sql)
        row_factory = dict_row if as_dicts else None
        with self.connection(autocommit=True) as conn:
            with conn.cursor(row_factory=row_factory) as cur:
                cur.execute(sql, params or ())
                rows = cur.fetchall()
        _logger.debug("Raw response: %s", repr(rows))
        return list(rows)

    def fetch_one(
        self,
        sql: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
        *,
        as_dict: bool = True,
    ) -> dict[str, Any] | tuple[Any, ...] | None:
        """SELECT: return one row or None."""
        row_factory = dict_row if as_dict else None
        with self.connection(autocommit=True) as conn:
            with conn.cursor(row_factory=row_factory) as cur:
                cur.execute(sql, params or ())
                return cur.fetchone()

    def execute(
        self,
        sql: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
    ) -> None:
        """INSERT/UPDATE/DELETE with no result rows."""
        with self.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params or ())


def get_pg_connector(db_params: Dict = {}):
    global _pg_connector
    if _pg_connector is None:
        if len(db_params) == 0:
            raise ValueError("DB params are required to init Postgres connection")
        _pg_connector = PostgresConnector(db_params)
    return _pg_connector
