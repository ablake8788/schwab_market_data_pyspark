"""
cli/args.py
-----------
Command-line argument definition and parsing.

Kept separate from main() so it can be imported and tested in isolation,
and so the argument schema lives in one obvious place.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CliArgs:
    """Typed result of CLI argument parsing."""
    symbols: list[str]
    start: str
    end: str
    window: int
    num_std: float
    z_threshold: float
    write_back: bool
    write_mode: str
    log_dir: Path | None


def parse_args(argv=None) -> CliArgs:
    """
    Parse and return typed CLI arguments.

    Parameters
    ----------
    argv : list[str] | None
        Argument list (defaults to sys.argv when None).
    """
    parser = argparse.ArgumentParser(
        description="Schwab Market Data PySpark Analytics — rolling stats over "
                     "SchwabQuotesHistory via Spark window functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples
--------
  # Show analytics without writing back:
  python main.py --symbols AAPL,MSFT --start 2026-01-01 --end 2026-07-01 --window 20

  # Compute and persist to SQL Server:
  python main.py --symbols AAPL --start 2026-01-01 --end 2026-07-01 --write-back
""",
    )

    parser.add_argument(
        "--symbols",
        required=True,
        metavar="SYM,SYM,...",
        help="Comma-separated list of ticker symbols",
    )
    parser.add_argument(
        "--start",
        required=True,
        metavar="YYYY-MM-DD",
        help="Start date for the price history window",
    )
    parser.add_argument(
        "--end",
        required=True,
        metavar="YYYY-MM-DD",
        help="End date for the price history window",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=20,
        metavar="N",
        help="Rolling window size in bars (default: 20)",
    )
    parser.add_argument(
        "--num-std",
        type=float,
        default=2.0,
        metavar="X",
        help="Number of standard deviations for Bollinger Bands (default: 2.0)",
    )
    parser.add_argument(
        "--z-threshold",
        type=float,
        default=2.0,
        metavar="X",
        help="Absolute z-score threshold to flag as an anomaly (default: 2.0)",
    )
    parser.add_argument(
        "--write-back",
        action="store_true",
        help="Persist results to SQL Server instead of just printing them",
    )
    parser.add_argument(
        "--write-mode",
        choices=["append", "overwrite"],
        default="append",
        help="JDBC write mode when --write-back is set (default: append)",
    )
    parser.add_argument(
        "--log-dir",
        metavar="DIR",
        type=Path,
        help="Directory for rotating log files (default: ./logs)",
    )

    ns = parser.parse_args(argv)
    symbols = [s.strip() for s in ns.symbols.split(",") if s.strip()]
    return CliArgs(
        symbols=symbols,
        start=ns.start,
        end=ns.end,
        window=ns.window,
        num_std=ns.num_std,
        z_threshold=ns.z_threshold,
        write_back=ns.write_back,
        write_mode=ns.write_mode,
        log_dir=ns.log_dir,
    )
