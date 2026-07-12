"""
analytics/window_specs.py
--------------------------
Single source of truth for the rolling WindowSpec used by every analytics
transform, so moving_stats/bollinger/zscore all walk the same window.
"""

from __future__ import annotations

from pyspark.sql import WindowSpec
from pyspark.sql.window import Window


def rolling_window(window_size: int) -> WindowSpec:
    """
    Per-symbol trailing window of `window_size` bars (current row + prior
    window_size - 1), ordered by bar time. Used with avg/stddev to produce
    a moving average / rolling standard deviation.
    """
    return (
        Window.partitionBy("Symbol")
        .orderBy("BarDateTime")
        .rowsBetween(-(window_size - 1), 0)
    )


def row_number_window() -> WindowSpec:
    """Per-symbol ordinal position, used to flag the warm-up period."""
    return Window.partitionBy("Symbol").orderBy("BarDateTime")
