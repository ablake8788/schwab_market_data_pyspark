from pathlib import Path

import pytest

from cli.args import parse_args


def test_parses_required_args_with_defaults():
    args = parse_args(["--symbols", "AAPL,MSFT", "--start", "2026-01-01", "--end", "2026-07-01"])

    assert args.symbols == ["AAPL", "MSFT"]
    assert args.start == "2026-01-01"
    assert args.end == "2026-07-01"
    assert args.window == 20
    assert args.num_std == 2.0
    assert args.z_threshold == 2.0
    assert args.write_back is False
    assert args.write_mode == "append"
    assert args.log_dir is None


def test_symbols_are_stripped_and_empty_entries_dropped():
    args = parse_args(["--symbols", " AAPL, MSFT ,,TSLA", "--start", "2026-01-01", "--end", "2026-07-01"])

    assert args.symbols == ["AAPL", "MSFT", "TSLA"]


def test_write_back_and_overrides():
    args = parse_args([
        "--symbols", "AAPL",
        "--start", "2026-01-01",
        "--end", "2026-07-01",
        "--window", "50",
        "--num-std", "1.5",
        "--z-threshold", "3.0",
        "--write-back",
        "--write-mode", "overwrite",
        "--log-dir", "custom_logs",
    ])

    assert args.window == 50
    assert args.num_std == 1.5
    assert args.z_threshold == 3.0
    assert args.write_back is True
    assert args.write_mode == "overwrite"
    assert args.log_dir == Path("custom_logs")


def test_missing_required_arg_exits():
    with pytest.raises(SystemExit):
        parse_args(["--start", "2026-01-01", "--end", "2026-07-01"])  # missing --symbols


def test_invalid_write_mode_exits():
    with pytest.raises(SystemExit):
        parse_args([
            "--symbols", "AAPL", "--start", "2026-01-01", "--end", "2026-07-01",
            "--write-mode", "replace",  # not a valid choice for this project
        ])
