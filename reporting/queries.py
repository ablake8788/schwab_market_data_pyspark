"""
reporting/queries.py
----------------------
Aggregate SQL queries against dbo.SchwabQuotesHistory_SparkBollinger and
dbo.SchwabQuotesHistory_SparkZScore. Pure data-access — returns plain
lists of dicts, no formatting/presentation logic (that's report_builder.py).

IsWarmup rows are excluded throughout: their MovingAvg/RollingStd/bands
aren't fully populated (see analytics/moving_stats.py), so including them
would skew the summary stats.
"""

from __future__ import annotations

import pyodbc

from core.config import SqlConfig


def _rows_as_dicts(cursor: pyodbc.Cursor) -> list[dict]:
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_bollinger_summary(conn: pyodbc.Connection, sql_cfg: SqlConfig) -> list[dict]:
    """Per-symbol bar count, date range, and close-price range."""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            Symbol,
            COUNT(*)          AS BarCount,
            MIN(BarDateTime)  AS MinDate,
            MAX(BarDateTime)  AS MaxDate,
            MIN(ClosePrice)   AS MinClose,
            MAX(ClosePrice)   AS MaxClose,
            AVG(ClosePrice)   AS AvgClose
        FROM {sql_cfg.table_bollinger}
        WHERE IsWarmup = 0
        GROUP BY Symbol
        ORDER BY Symbol
    """)
    return _rows_as_dicts(cursor)


def fetch_zscore_summary(conn: pyodbc.Connection, sql_cfg: SqlConfig) -> list[dict]:
    """Per-symbol bar count, anomaly count, and the most extreme |ZScore|."""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            Symbol,
            COUNT(*)                                          AS BarCount,
            SUM(CASE WHEN IsAnomaly = 1 THEN 1 ELSE 0 END)     AS AnomalyCount,
            MAX(ABS(ZScore))                                   AS MaxAbsZScore
        FROM {sql_cfg.table_zscore}
        WHERE IsWarmup = 0
        GROUP BY Symbol
        ORDER BY AnomalyCount DESC, Symbol
    """)
    return _rows_as_dicts(cursor)


def fetch_top_anomalies(conn: pyodbc.Connection, sql_cfg: SqlConfig, limit: int = 15) -> list[dict]:
    """The most extreme anomalies across all symbols, by |ZScore|."""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT TOP {int(limit)}
            Symbol, BarDateTime, ClosePrice, ZScore
        FROM {sql_cfg.table_zscore}
        WHERE IsAnomaly = 1
        ORDER BY ABS(ZScore) DESC
    """)
    return _rows_as_dicts(cursor)


def fetch_recent_symbol_bollinger(
    conn: pyodbc.Connection, sql_cfg: SqlConfig, symbol: str, limit: int = 300
) -> list[dict]:
    """
    The most recent `limit` non-warmup bars for one symbol, ordered
    ascending by time (chart-ready) — for charts.build_symbol_chart().
    """
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT * FROM (
            SELECT TOP (?) BarDateTime, ClosePrice, MovingAvg, UpperBand, LowerBand
            FROM {sql_cfg.table_bollinger}
            WHERE Symbol = ? AND IsWarmup = 0
            ORDER BY BarDateTime DESC
        ) recent
        ORDER BY BarDateTime ASC
        """,
        (limit, symbol),
    )
    return _rows_as_dicts(cursor)


def fetch_symbol_anomalies_in_range(
    conn: pyodbc.Connection, sql_cfg: SqlConfig, symbol: str, start, end
) -> list[dict]:
    """Anomaly bars for one symbol within [start, end] — to mark on a price chart."""
    cursor = conn.cursor()
    cursor.execute(
        f"""
        SELECT BarDateTime, ClosePrice, ZScore
        FROM {sql_cfg.table_zscore}
        WHERE Symbol = ? AND IsAnomaly = 1 AND BarDateTime BETWEEN ? AND ?
        ORDER BY BarDateTime ASC
        """,
        (symbol, start, end),
    )
    return _rows_as_dicts(cursor)


def fetch_overall_totals(conn: pyodbc.Connection, sql_cfg: SqlConfig) -> dict:
    """Headline totals across both output tables."""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            COUNT(DISTINCT Symbol) AS SymbolCount,
            COUNT(*)               AS TotalBollingerRows,
            MIN(BarDateTime)       AS MinDate,
            MAX(BarDateTime)       AS MaxDate
        FROM {sql_cfg.table_bollinger}
        WHERE IsWarmup = 0
    """)
    totals = _rows_as_dicts(cursor)[0]

    cursor.execute(f"""
        SELECT
            COUNT(*)                                       AS TotalZScoreRows,
            SUM(CASE WHEN IsAnomaly = 1 THEN 1 ELSE 0 END)  AS TotalAnomalies
        FROM {sql_cfg.table_zscore}
        WHERE IsWarmup = 0
    """)
    totals.update(_rows_as_dicts(cursor)[0])
    return totals
