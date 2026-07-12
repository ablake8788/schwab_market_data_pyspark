"""
db/history_reader.py
---------------------
Reads dbo.SchwabQuotesHistory (the OHLCV table populated by the sibling
schwab_market_data project) as a Spark DataFrame.

Design pattern: Repository — callers ask for rows in domain terms
(symbols + date range) and never see JDBC option dictionaries.
Filtering is pushed down into the SQL subquery rather than done in Spark,
so SQL Server does the row elimination instead of shipping the whole table.
"""

from __future__ import annotations

import logging
import re

from pyspark.sql import DataFrame, SparkSession

from core.config import SqlConfig
from core.logging_setup import traced
from db._jdbc import jdbc_properties, jdbc_url, validate_symbols

log = logging.getLogger(__name__)

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _validate_date(label: str, value: str) -> str:
    if not _DATE_RE.match(value):
        raise ValueError(f"{label} must be YYYY-MM-DD, got {value!r}")
    return value


class HistoryReader:
    def __init__(
        self,
        spark: SparkSession,
        sql_config: SqlConfig,
        jdbc_driver_class: str,
        fetch_size: int = 10000,
    ) -> None:
        self._spark = spark
        self._cfg = sql_config
        self._driver_class = jdbc_driver_class
        self._fetch_size = fetch_size

    @traced
    def read(self, symbols: list[str], start: str, end: str) -> DataFrame:
        clean_symbols = validate_symbols(symbols)
        start = _validate_date("start", start)
        end = _validate_date("end", end)

        symbol_list = ", ".join(f"'{s}'" for s in clean_symbols)
        subquery = (
            f"(SELECT Symbol, BarDateTime, OpenPrice, HighPrice, LowPrice, "
            f"ClosePrice, Volume "
            f"FROM {self._cfg.table_history} "
            f"WHERE Symbol IN ({symbol_list}) "
            f"AND BarDateTime BETWEEN '{start}' AND '{end}') AS src"
        )

        df = (
            self._spark.read.format("jdbc")
            .option("url", jdbc_url(self._cfg))
            .option("dbtable", subquery)
            .options(**jdbc_properties(self._cfg, self._driver_class))
            .option("fetchsize", self._fetch_size)
            .load()
        )
        log.info("Read %s rows for symbols=%s [%s, %s]", df.count(), clean_symbols, start, end)
        return df
