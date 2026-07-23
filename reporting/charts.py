"""
reporting/charts.py
----------------------
Matplotlib PNG chart generation for the summary report. Pure
presentation logic, same as report_builder.py — takes plain
dicts/lists, writes PNG files, no SQL.

Uses the "Agg" backend explicitly since this runs headless (no display
attached) — the default backend can fail to import cleanly in that case.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def build_anomaly_count_chart(zscore_summary: list[dict], output_path: str | Path) -> Path:
    """
    Horizontal bar chart of anomaly count per symbol, sorted descending —
    the same ordering fetch_zscore_summary() already returns.
    """
    output_path = Path(output_path)
    symbols = [row["Symbol"] for row in zscore_summary]
    counts = [row["AnomalyCount"] or 0 for row in zscore_summary]

    height = max(3.0, 0.28 * len(symbols))
    fig, ax = plt.subplots(figsize=(7.5, height))
    ax.barh(symbols, counts, color="#f59e0b")
    ax.invert_yaxis()  # highest count at the top, matching the table order
    ax.set_xlabel("Anomalies flagged")
    ax.set_title("Anomaly Count by Symbol")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path.resolve()


def build_symbol_chart(
    symbol: str,
    bollinger_rows: list[dict],
    anomaly_rows: list[dict],
    output_path: str | Path,
) -> Path:
    """
    Line chart of ClosePrice/MovingAvg/UpperBand/LowerBand over time for
    one symbol, with anomaly bars marked as red dots on the close-price line.

    bollinger_rows : ordered ascending by BarDateTime — BarDateTime,
        ClosePrice, MovingAvg, UpperBand, LowerBand.
    anomaly_rows : BarDateTime, ClosePrice for bars flagged IsAnomaly=1
        within the same window.
    """
    output_path = Path(output_path)

    dates = [r["BarDateTime"] for r in bollinger_rows]
    close = [float(r["ClosePrice"]) for r in bollinger_rows]
    moving_avg = [float(r["MovingAvg"]) if r["MovingAvg"] is not None else None for r in bollinger_rows]
    upper = [float(r["UpperBand"]) if r["UpperBand"] is not None else None for r in bollinger_rows]
    lower = [float(r["LowerBand"]) if r["LowerBand"] is not None else None for r in bollinger_rows]

    fig, ax = plt.subplots(figsize=(7.5, 3.5))
    ax.plot(dates, close, label="Close", color="#111827", linewidth=1.2)
    ax.plot(dates, moving_avg, label="Moving Avg", color="#8b5cf6", linewidth=1.0, linestyle="--")
    ax.plot(dates, upper, label="Upper Band", color="#14b8a6", linewidth=0.8, alpha=0.8)
    ax.plot(dates, lower, label="Lower Band", color="#14b8a6", linewidth=0.8, alpha=0.8)
    ax.fill_between(dates, lower, upper, color="#14b8a6", alpha=0.08)

    if anomaly_rows:
        anomaly_dates = [r["BarDateTime"] for r in anomaly_rows]
        anomaly_close = [float(r["ClosePrice"]) for r in anomaly_rows]
        ax.scatter(anomaly_dates, anomaly_close, color="#ef4444", s=22, zorder=5, label="Anomaly")

    ax.set_title(f"{symbol} — Close Price, Bollinger Bands & Anomalies")
    ax.set_ylabel("Price")
    ax.legend(loc="upper left", fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    return output_path.resolve()
