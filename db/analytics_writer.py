"""
db/analytics_writer.py
------------------------
Writes computed analytics DataFrames back to SQL Server via JDBC.

Design pattern: Repository / Unit-of-Work-ish — every public write goes
through one private _write() so the JDBC option wiring lives in one place
(mirrors quote_repository.save() in the sibling schwab_market_data project).
The target tables (SchwabQuotesHistory_SparkBollinger / _SparkZScore) are
NEW tables distinct from the SQL-computed analytics tables the existing
project already writes — this writer never touches those.
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame

from core.config import SqlConfig
from core.logging_setup import traced
from db._jdbc import jdbc_properties, jdbc_url

log = logging.getLogger(__name__)


class AnalyticsWriter:
    def __init__(self, sql_config: SqlConfig, jdbc_driver_class: str) -> None:
        self._cfg = sql_config
        self._driver_class = jdbc_driver_class

    @traced
    def write_bollinger(self, df: DataFrame, mode: str = "append") -> int:
        return self._write(df, self._cfg.table_bollinger, mode)

    @traced
    def write_zscore(self, df: DataFrame, mode: str = "append") -> int:
        return self._write(df, self._cfg.table_zscore, mode)

    def _write(self, df: DataFrame, table: str, mode: str) -> int:
        row_count = df.count()
        (
            df.write.format("jdbc")
            .option("url", jdbc_url(self._cfg))
            .option("dbtable", table)
            .options(**jdbc_properties(self._cfg, self._driver_class))
            .mode(mode)
            .save()
        )
        log.info("Wrote %d row(s) to %s (mode=%s)", row_count, table, mode)
        return row_count
