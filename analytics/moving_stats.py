"""
analytics/moving_stats.py
---------------------------
Adds rolling mean/std columns that both bollinger.py and zscore.py build on.
"""

from __future__ import annotations

import pyspark.sql.functions as F
from pyspark.sql import DataFrame

from analytics.window_specs import rolling_window, row_number_window


def add_moving_stats(df: DataFrame, window_size: int) -> DataFrame:
    """
    Adds:
      MovingAvg   — avg(ClosePrice) over the trailing window
      RollingStd  — sample stddev(ClosePrice) over the trailing window
      RowNum      — 1-based ordinal position of the bar within its symbol
      IsWarmup    — True for the first (window_size - 1) bars of a symbol,
                    where the window is still partially filled and the
                    stats should not be treated as reliable
    """
    w = rolling_window(window_size)
    rn = row_number_window()
    return (
        df.withColumn("MovingAvg", F.avg("ClosePrice").over(w))
        .withColumn("RollingStd", F.stddev_samp("ClosePrice").over(w))
        .withColumn("RowNum", F.row_number().over(rn))
        .withColumn("IsWarmup", F.col("RowNum") < F.lit(window_size))
    )
