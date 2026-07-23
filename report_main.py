"""
report_main.py
----------------
Entry point — Composition Root for the summary-report job.

Separate from main.py (the Spark analytics job) because this needs no
SparkSession at all — it's a plain pyodbc reader over the *output*
tables main.py already wrote, plus a docx builder and an optional SMTP
sender.

No business logic lives here; it only:
  1. Parses CLI args.
  2. Sets up logging.
  3. Loads config (Singleton) — including the optional [email] section.
  4. Queries the summary data.
  5. Builds the .docx.
  6. Optionally emails it.
"""

from __future__ import annotations

import logging
import os
import sys
import traceback

from cli import parse_report_args
from core import AppConfig, setup_logging
from reporting.connection import SqlConnectionFactory
from reporting.queries import (
    fetch_bollinger_summary,
    fetch_overall_totals,
    fetch_top_anomalies,
    fetch_zscore_summary,
)
from reporting.report_builder import build_summary_docx
from reporting.emailer import send_report_email

log = logging.getLogger(__name__)


def main() -> None:
    # ── 1. CLI args ────────────────────────────
    args = parse_report_args()

    # ── 2. Logging ─────────────────────────────
    setup_logging(args.log_dir)
    log.info("=" * 60)
    log.info("Schwab Analytics Summary Report starting")
    log.info("Python %s | PID %d", sys.version.split()[0], os.getpid())
    log.info("=" * 60)

    try:
        # ── 3. Config (Singleton) ───────────────
        cfg = AppConfig.load()
        log.info("Config loaded from schwab_market_data_pyspark.ini")

        if args.send_email and (cfg.email is None or not cfg.email.enabled):
            print(
                "FATAL: --send-email was passed but no enabled [email] section "
                "was found in schwab_market_data_pyspark.ini"
            )
            sys.exit(1)

        # ── 4. Query ─────────────────────────────
        factory = SqlConnectionFactory(cfg.sql)
        print("Querying dbo.SchwabQuotesHistory_SparkBollinger / _SparkZScore ...")
        with factory.connect() as conn:
            overall = fetch_overall_totals(conn, cfg.sql)
            bollinger_summary = fetch_bollinger_summary(conn, cfg.sql)
            zscore_summary = fetch_zscore_summary(conn, cfg.sql)
            top_anomalies = fetch_top_anomalies(conn, cfg.sql, args.top_anomalies)

        log.info(
            "Fetched summary: symbols=%s totalAnomalies=%s",
            overall.get("SymbolCount"), overall.get("TotalAnomalies"),
        )

        # ── 5. Build docx ────────────────────────
        report_path = build_summary_docx(
            overall, bollinger_summary, zscore_summary, top_anomalies, args.output
        )
        print(f"Report written to {report_path}")
        log.info("Report written to %s", report_path)

        # ── 6. Email (optional) ──────────────────
        if args.send_email:
            print(f"Sending email to {', '.join(cfg.email.to_email)} ...")
            body = (
                f"Schwab Market Data analytics summary attached.\n\n"
                f"Symbols: {overall.get('SymbolCount')}\n"
                f"Date range: {overall.get('MinDate')} - {overall.get('MaxDate')}\n"
                f"Anomalies flagged: {overall.get('TotalAnomalies')}\n"
            )
            send_report_email(cfg.email, report_path, body)
            print("Email sent.")
            log.info("Run complete — report built and emailed.")
        else:
            log.info("Run complete — report built, --send-email not passed.")

    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        print("\nInterrupted.")
        sys.exit(0)

    except Exception as exc:
        log.critical("Unhandled exception: %s\n%s", exc, traceback.format_exc())
        print(f"\nFATAL: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
