"""
db/_jdbc.py
-----------
Shared JDBC URL/property helpers used by both the reader and the writer,
so the connection-string assembly lives in exactly one place (same intent
as SqlConnectionFactory in the sibling schwab_market_data project).
"""

from __future__ import annotations

import re

from core.config import SqlConfig

_SYMBOL_RE = re.compile(r"^[A-Za-z0-9.\-]+$")


def jdbc_url(cfg: SqlConfig) -> str:
    return (
        f"jdbc:sqlserver://{cfg.server};databaseName={cfg.database};"
        f"trustServerCertificate={cfg.trust_cert};encrypt=true;"
    )


def jdbc_properties(cfg: SqlConfig, driver_class: str) -> dict:
    return {"user": cfg.username, "password": cfg.password, "driver": driver_class}


def validate_symbols(symbols: list[str]) -> list[str]:
    """
    Reject anything that isn't a plain ticker before it's interpolated into a
    JDBC `dbtable` subquery — Spark's JDBC `dbtable` option does not support
    bind parameters, so this is the injection guard for that string.
    """
    cleaned = [s.strip().upper() for s in symbols if s.strip()]
    for s in cleaned:
        if not _SYMBOL_RE.match(s):
            raise ValueError(f"Invalid symbol: {s!r}")
    if not cleaned:
        raise ValueError("No symbols provided")
    return cleaned
