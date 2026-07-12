"""
analytics/zscore.py
----------------------
Rolling z-score anomaly detection, built on top of the MovingAvg/RollingStd
columns that moving_stats.add_moving_stats() already added.
"""

from __future__ import annotations

import pyspark.sql.functions as F
from pyspark.sql import DataFrame


def add_zscore(df: DataFrame, z_threshold: float) -> DataFrame:
    """
    Requires MovingAvg and RollingStd columns (see moving_stats.py).
    ZScore is null (not zero) when RollingStd is 0 or null — a flat window
    isn't "no anomaly", it's "z-score undefined", and treating it as 0
    would silently hide the fact that the stat can't be computed.
    """
    return df.withColumn(
        "ZScore",
        F.when(
            F.col("RollingStd") > 0,
            (F.col("ClosePrice") - F.col("MovingAvg")) / F.col("RollingStd"),
        ),
    ).withColumn(
        "IsAnomaly",
        F.when(F.col("ZScore").isNotNull(), F.abs(F.col("ZScore")) >= F.lit(z_threshold)).otherwise(
            F.lit(False)
        ),
    )
