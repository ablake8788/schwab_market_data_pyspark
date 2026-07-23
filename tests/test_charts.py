from datetime import datetime, timedelta

from reporting.charts import build_anomaly_count_chart, build_symbol_chart


def test_build_anomaly_count_chart_creates_png(tmp_path):
    zscore_summary = [
        {"Symbol": "LUNR", "AnomalyCount": 20},
        {"Symbol": "AAPL", "AnomalyCount": 5},
        {"Symbol": "RGTI", "AnomalyCount": 0},
    ]

    out_path = tmp_path / "anomaly_count.png"
    result = build_anomaly_count_chart(zscore_summary, out_path)

    assert result.exists()
    assert result.stat().st_size > 0


def test_build_anomaly_count_chart_handles_empty_input(tmp_path):
    out_path = tmp_path / "anomaly_count.png"
    result = build_anomaly_count_chart([], out_path)

    assert result.exists()


def test_build_symbol_chart_creates_png(tmp_path):
    base = datetime(2026, 1, 1, 9, 30)
    bollinger_rows = [
        {
            "BarDateTime": base + timedelta(minutes=i),
            "ClosePrice": 10.0 + i * 0.1,
            "MovingAvg": 10.0 + i * 0.1,
            "UpperBand": 10.5 + i * 0.1,
            "LowerBand": 9.5 + i * 0.1,
        }
        for i in range(20)
    ]
    anomaly_rows = [
        {"BarDateTime": base + timedelta(minutes=5), "ClosePrice": 10.5},
    ]

    out_path = tmp_path / "LUNR.png"
    result = build_symbol_chart("LUNR", bollinger_rows, anomaly_rows, out_path)

    assert result.exists()
    assert result.stat().st_size > 0


def test_build_symbol_chart_handles_no_anomalies(tmp_path):
    base = datetime(2026, 1, 1, 9, 30)
    bollinger_rows = [
        {
            "BarDateTime": base + timedelta(minutes=i),
            "ClosePrice": 10.0,
            "MovingAvg": 10.0,
            "UpperBand": 10.5,
            "LowerBand": 9.5,
        }
        for i in range(5)
    ]

    out_path = tmp_path / "AAPL.png"
    result = build_symbol_chart("AAPL", bollinger_rows, [], out_path)

    assert result.exists()
