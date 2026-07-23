"""
reporting/connection.py
-------------------------
pyodbc connection factory for the reporting package — mirrors
db/connection.py in the sibling schwab_market_data / Sales Analytics ETL
projects, but lives here since the rest of this project talks to SQL
Server exclusively via Spark's JDBC path, not pyodbc.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

import pyodbc

from core.config import SqlConfig

log = logging.getLogger(__name__)


class SqlConnectionFactory:
    def __init__(self, config: SqlConfig) -> None:
        self._cfg = config

    @property
    def _connection_string(self) -> str:
        c = self._cfg
        return (
            f"DRIVER={{{c.driver}}};"
            f"SERVER={c.server};"
            f"DATABASE={c.database};"
            f"UID={c.username};"
            f"PWD={c.password};"
            f"TrustServerCertificate={c.trust_cert};"
        )

    @contextmanager
    def connect(self) -> Generator[pyodbc.Connection, None, None]:
        conn = pyodbc.connect(self._connection_string)
        try:
            yield conn
        finally:
            conn.close()
