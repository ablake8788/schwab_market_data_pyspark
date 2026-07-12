# Schwab Market Data — PySpark Analytics

Reads `dbo.SchwabQuotesHistory` (OHLCV bars) from SQL Server — the table
populated by the sibling **schwab_market_data** loader — and computes
rolling moving averages, Bollinger Bands, and z-score anomaly flags using
Spark window functions. Optionally writes results back to SQL Server.

This is a standalone project: it never modifies `schwab_market_data`, and
its own analytics output tables (`SchwabQuotesHistory_SparkBollinger`,
`SchwabQuotesHistory_SparkZScore`) are separate from that project's
SQL-computed analytics tables.

---

## Project structure

```
schwab_market_data_pyspark/
│
├── main.py                        # Entry point — Composition Root
│
├── core/                          # Shared infrastructure
│   ├── config.py                  # AppConfig Singleton + SqlConfig/SparkConfig
│   └── logging_setup.py           # TRACE level, setup_logging(), @traced
│
├── spark_session/
│   └── session_factory.py         # SparkSessionFactory — builds the SparkSession
│
├── db/                             # SQL Server data access via JDBC
│   ├── history_reader.py          # Reads SchwabQuotesHistory as a DataFrame
│   └── analytics_writer.py        # Writes analytics DataFrames back
│
├── analytics/                      # Spark window-function transforms
│   ├── window_specs.py            # Shared rolling WindowSpec
│   ├── moving_stats.py            # Moving average + rolling std
│   ├── bollinger.py               # Bollinger Bands
│   └── zscore.py                  # Rolling z-score anomaly flags
│
├── cli/
│   └── args.py                    # argparse wiring → CliArgs dataclass
│
├── sql/tables/                     # DDL for the two output tables (run once manually)
│
└── logs/                          # Created at runtime
```

---

## Design patterns applied

| Pattern | Module(s) | Purpose |
|---|---|---|
| **Singleton** | `core/config.py` — `AppConfig.load()` | Config loaded once |
| **Value Object** | `SqlConfig`, `SparkConfig`, `CliArgs` | Immutable, frozen dataclasses |
| **Factory Method** | `spark_session/session_factory.py` | Centralises SparkSession + JDBC package config |
| **Repository** | `db/history_reader.py`, `db/analytics_writer.py` | Domain-language interface over JDBC |
| **Decorator** | `core/logging_setup.py` — `@traced` | Entry/exit/exception TRACE logs |
| **Composition Root** | `main.py` | Only place all objects are wired together |

---

## Prerequisites

- **JDK 17** (Temurin recommended) — `java -version` must work.
- **Windows only**: `winutils.exe` / `hadoop.dll` (Hadoop 3.3.x build) on `HADOOP_HOME`.
- **Python 3.11** (PySpark 3.5.x is best-tested up to 3.12).
- No JDBC jar to manage manually — `spark.jars.packages` fetches
  `mssql-jdbc` from Maven Central on first run (needs internet access).

## Configuration

Copy the template and fill in real values:

```bash
cp schwab_market_data_pyspark.ini.template schwab_market_data_pyspark.ini
```

`schwab_market_data_pyspark.ini` is gitignored — never commit it.

## Usage

```bash
# Show analytics without writing back
python main.py --symbols AAPL,MSFT --start 2026-01-01 --end 2026-07-01 --window 20

# Compute and persist to SQL Server
python main.py --symbols AAPL --start 2026-01-01 --end 2026-07-01 --write-back
```

## SQL Server objects expected

Run the scripts under `sql/tables/` once against the target database before
using `--write-back`:

| Object | Purpose |
|---|---|
| `dbo.SchwabQuotesHistory` | Source OHLCV bars (populated by schwab_market_data) |
| `dbo.SchwabQuotesHistory_SparkBollinger` | Bollinger Band output |
| `dbo.SchwabQuotesHistory_SparkZScore` | Z-score anomaly output |
