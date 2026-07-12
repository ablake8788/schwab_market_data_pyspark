"""
main.py
-------
Application entry point — Composition Root.

All dependencies are wired here and nowhere else.
No business logic lives in this file; it only:
  1. Parses CLI args.
  2. Sets up logging.
  3. Loads config (Singleton).
  4. Constructs and injects all collaborators.
  5. Calls the orchestration sequence.

Design patterns in use across the project
------------------------------------------
| Pattern            | Where                                          |
|--------------------|------------------------------------------------|
| Singleton          | AppConfig.load()                               |
| Factory Method      | SparkSessionFactory.create()                   |
| Repository          | HistoryReader, AnalyticsWriter                 |
| Composition Root    | main.py                                        |
| Decorator           | @traced on all key functions                   |
| Value Object        | SqlConfig, SparkConfig, CliArgs                |
"""

from __future__ import annotations

import logging
import os
import sys
import traceback
import uuid
from datetime import datetime, timezone

from pyspark.sql import functions as F

from cli import parse_args
from core import AppConfig, setup_logging
from db import HistoryReader, AnalyticsWriter
from spark_session import SparkSessionFactory
from analytics import add_moving_stats, add_bollinger_bands, add_zscore

log = logging.getLogger(__name__)


def main() -> None:
    # ── 1. CLI args ────────────────────────────
    args = parse_args()

    # ── 2. Logging ─────────────────────────────
    setup_logging(args.log_dir)
    log.info("=" * 60)
    log.info("Schwab Market Data PySpark Analytics starting")
    log.info("Python %s | PID %d", sys.version.split()[0], os.getpid())
    log.info("=" * 60)

    spark = None
    try:
        # ── 3. Config (Singleton) ───────────────
        cfg = AppConfig.load()
        log.info("Config loaded from schwab_market_data_pyspark.ini")

        # ── 4. Wire dependencies ────────────────
        spark = SparkSessionFactory(cfg.spark).create()
        history_reader = HistoryReader(
            spark, cfg.sql, cfg.spark.jdbc_driver_class, cfg.spark.fetch_size
        )
        analytics_writer = AnalyticsWriter(cfg.sql, cfg.spark.jdbc_driver_class)

        log.info(
            "Symbols=%s  date range: %s → %s  window=%d",
            args.symbols, args.start, args.end, args.window,
        )

        # ── 5. Read ──────────────────────────────
        history_df = history_reader.read(args.symbols, args.start, args.end)

        # ── 6. Compute analytics ────────────────
        stats_df = add_moving_stats(history_df, args.window)
        bollinger_df = add_bollinger_bands(stats_df, args.num_std)
        zscore_df = add_zscore(stats_df, args.z_threshold)

        bollinger_cols = [
            "Symbol", "BarDateTime", "ClosePrice",
            "MovingAvg", "RollingStd", "UpperBand", "LowerBand", "IsWarmup",
        ]
        zscore_cols = [
            "Symbol", "BarDateTime", "ClosePrice",
            "MovingAvg", "RollingStd", "ZScore", "IsAnomaly", "IsWarmup",
        ]

        print("\n=== BOLLINGER BANDS ===")
        bollinger_df.select(*bollinger_cols).orderBy("Symbol", "BarDateTime").show(
            50, truncate=False
        )

        print("\n=== Z-SCORE ANOMALIES ===")
        zscore_df.select(*zscore_cols).orderBy("Symbol", "BarDateTime").show(
            50, truncate=False
        )

        # ── 7. Optionally persist ───────────────
        if args.write_back:
            print(f"\nWriting results to SQL Server (mode={args.write_mode}) …")

            batch_id = str(uuid.uuid4())
            load_date = datetime.now(timezone.utc)

            bollinger_out = (
                bollinger_df.select(*bollinger_cols)
                .withColumn("WindowSize", F.lit(args.window))
                .withColumn("NumStdDev", F.lit(args.num_std))
                .withColumn("LoadDate", F.lit(load_date))
                .withColumn("BatchId", F.lit(batch_id))
            )
            zscore_out = (
                zscore_df.select(*zscore_cols)
                .withColumn("WindowSize", F.lit(args.window))
                .withColumn("ZThreshold", F.lit(args.z_threshold))
                .withColumn("LoadDate", F.lit(load_date))
                .withColumn("BatchId", F.lit(batch_id))
            )

            b_rows = analytics_writer.write_bollinger(bollinger_out, args.write_mode)
            z_rows = analytics_writer.write_zscore(zscore_out, args.write_mode)
            print(f"Bollinger: {b_rows} row(s) written. Z-Score: {z_rows} row(s) written.")
            log.info("Write-back complete. Bollinger=%d ZScore=%d BatchId=%s", b_rows, z_rows, batch_id)

        log.info("Run complete.")

    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        print("\nInterrupted.")
        sys.exit(0)

    except Exception as exc:
        log.critical("Unhandled exception: %s\n%s", exc, traceback.format_exc())
        print(f"\nFATAL: {exc}")
        sys.exit(1)

    finally:
        if spark is not None:
            spark.stop()


if __name__ == "__main__":
    main()
