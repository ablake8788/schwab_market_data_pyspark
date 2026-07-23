"""
cli/report_args.py
--------------------
Command-line argument definition and parsing for report_main.py.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ReportCliArgs:
    """Typed result of CLI argument parsing."""
    output: Path
    send_email: bool
    top_anomalies: int
    chart_symbols: int
    chart_bars: int
    no_charts: bool
    log_dir: Optional[Path]


def parse_report_args(argv=None) -> ReportCliArgs:
    parser = argparse.ArgumentParser(
        description="Build a Bollinger Bands / Z-Score summary report (.docx) "
                     "from dbo.SchwabQuotesHistory_SparkBollinger / _SparkZScore, "
                     "optionally emailing it.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
  # Build the report only, no email:
  python report_main.py

  # Build and email it (uses [email] section in the .ini):
  python report_main.py --send-email
""",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports") / "schwab_analytics_summary.docx",
        metavar="PATH",
        help="Output .docx path (default: reports/schwab_analytics_summary.docx)",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Email the generated report using the [email] section of the .ini",
    )
    parser.add_argument(
        "--top-anomalies",
        type=int,
        default=15,
        metavar="N",
        help="Number of most-extreme anomalies to list (default: 15)",
    )
    parser.add_argument(
        "--chart-symbols",
        type=int,
        default=3,
        metavar="N",
        help="Number of most-anomalous symbols to chart individually (default: 3)",
    )
    parser.add_argument(
        "--chart-bars",
        type=int,
        default=300,
        metavar="N",
        help="Number of most-recent bars per symbol chart (default: 300)",
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip chart generation entirely (tables only, faster)",
    )
    parser.add_argument(
        "--log-dir",
        metavar="DIR",
        type=Path,
        help="Directory for rotating log files (default: ./logs)",
    )

    ns = parser.parse_args(argv)
    return ReportCliArgs(
        output=ns.output,
        send_email=ns.send_email,
        top_anomalies=ns.top_anomalies,
        chart_symbols=ns.chart_symbols,
        chart_bars=ns.chart_bars,
        no_charts=ns.no_charts,
        log_dir=ns.log_dir,
    )
