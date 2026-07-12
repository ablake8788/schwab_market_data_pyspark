"""
analytics/bollinger.py
------------------------
Bollinger Bands built on top of the MovingAvg/RollingStd columns that
moving_stats.add_moving_stats() already added.
"""

from __future__ import annotations

import pyspark.sql.functions as F
from pyspark.sql import DataFrame


def add_bollinger_bands(df: DataFrame, num_std: float) -> DataFrame:
    """Requires MovingAvg and RollingStd columns (see moving_stats.py)."""
    return df.withColumn(
        "UpperBand", F.col("MovingAvg") + F.lit(num_std) * F.col("RollingStd")
    ).withColumn(
        "LowerBand", F.col("MovingAvg") - F.lit(num_std) * F.col("RollingStd")
    )
