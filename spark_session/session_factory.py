"""
spark_session/session_factory.py
---------------------------------
Builds and configures the single SparkSession used for a run.

Design pattern: Factory Method — mirrors db.connection.SqlConnectionFactory
in the sibling schwab_market_data project. This is the only place Spark
confs (JDBC package coordinates, shuffle partitions, timezone) are set.
"""

from __future__ import annotations

import logging
import os
import sys

from pyspark.sql import SparkSession

from core.config import SparkConfig
from core.logging_setup import traced

log = logging.getLogger(__name__)


class SparkSessionFactory:
    def __init__(self, config: SparkConfig) -> None:
        self._cfg = config

    @traced
    def create(self) -> SparkSession:
        # Must be set before the JVM gateway launches, or the Python worker
        # Spark spawns can end up on a different interpreter than this venv
        # (observed as "Python worker failed to connect back" / socket
        # accept timeout on Windows when left to the OS default).
        os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
        os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)

        spark = (
            SparkSession.builder
            .appName(self._cfg.app_name)
            .master(self._cfg.master)
            .config("spark.jars.packages", self._cfg.jdbc_package)
            .config("spark.sql.shuffle.partitions", str(self._cfg.shuffle_partitions))
            .config("spark.sql.session.timeZone", "UTC")
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("WARN")
        log.info("SparkSession created — app=%s master=%s", self._cfg.app_name, self._cfg.master)
        return spark
