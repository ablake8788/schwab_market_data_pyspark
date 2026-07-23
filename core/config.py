"""
core/config.py
--------------
Centralised, immutable application configuration.

Design patterns used:
  - Singleton  : AppConfig is instantiated once via AppConfig.load(); subsequent
                 calls return the cached instance.
  - Value Object / dataclass : All fields are read-only after construction.
  - Factory method : AppConfig.load(path) is the only entry point.
"""

from __future__ import annotations

import configparser
import sys
from dataclasses import dataclass
from pathlib import Path


# ──────────────────────────────────────────────
# Path helper
# ──────────────────────────────────────────────
def _base_dir() -> Path:
    if getattr(sys, "frozen", False):           # PyInstaller bundle
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def resource_path(relative: str) -> Path:
    """Resolve a path relative to the project root (script or EXE)."""
    return _base_dir() / relative


# ──────────────────────────────────────────────
# Sub-config value objects
# ──────────────────────────────────────────────
@dataclass(frozen=True)
class SqlConfig:
    driver: str
    server: str
    database: str
    username: str
    password: str
    trust_cert: str
    table_history: str = "dbo.SchwabQuotesHistory"
    table_bollinger: str = "dbo.SchwabQuotesHistory_SparkBollinger"
    table_zscore: str = "dbo.SchwabQuotesHistory_SparkZScore"


@dataclass(frozen=True)
class SparkConfig:
    app_name: str = "schwab_market_data_pyspark"
    master: str = "local[*]"
    jdbc_driver_class: str = "com.microsoft.sqlserver.jdbc.SQLServerDriver"
    jdbc_package: str = "com.microsoft.sqlserver:mssql-jdbc:12.8.1.jre11"
    shuffle_partitions: int = 4
    fetch_size: int = 10000


@dataclass(frozen=True)
class EmailConfig:
    """Optional — only required by report_main.py, not the main analytics job."""
    enabled: bool
    smtp_server: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    from_email: str
    to_email: tuple[str, ...]
    subject: str


# ──────────────────────────────────────────────
# Root config (Singleton)
# ──────────────────────────────────────────────
@dataclass(frozen=True)
class AppConfig:
    sql: SqlConfig
    spark: SparkConfig
    email: "EmailConfig | None" = None

    # class-level cache (not stored on instance to keep frozen=True happy)
    _cache: "AppConfig | None" = None

    @classmethod
    def load(cls, config_file: str = "schwab_market_data_pyspark.ini") -> "AppConfig":
        """
        Factory / Singleton.
        Reads the INI file once and caches the result.  Subsequent calls
        with the same path return the cached instance immediately.
        """
        if cls._cache is not None:
            return cls._cache

        path = resource_path(config_file)
        if not path.exists():
            raise FileNotFoundError(
                f"Config file not found: {path}\n"
                "Copy schwab_market_data_pyspark.ini.template to "
                "schwab_market_data_pyspark.ini and fill in real values."
            )

        parser = configparser.ConfigParser()
        if not parser.read(path):
            raise FileNotFoundError(f"Could not read config file: {path}")

        q = parser["sqlserver"]
        p = parser["spark"] if parser.has_section("spark") else {}

        sql = SqlConfig(
            driver=q["driver"],
            server=q["server"],
            database=q["database"],
            username=q["username"],
            password=q["password"],
            trust_cert=q.get("trust_cert", "yes"),
            table_history=q.get("table_history", "dbo.SchwabQuotesHistory"),
            table_bollinger=q.get("table_bollinger", "dbo.SchwabQuotesHistory_SparkBollinger"),
            table_zscore=q.get("table_zscore", "dbo.SchwabQuotesHistory_SparkZScore"),
        )

        spark = SparkConfig(
            app_name=p.get("app_name", "schwab_market_data_pyspark"),
            master=p.get("master", "local[*]"),
            jdbc_driver_class=p.get(
                "jdbc_driver_class", "com.microsoft.sqlserver.jdbc.SQLServerDriver"
            ),
            jdbc_package=p.get("jdbc_package", "com.microsoft.sqlserver:mssql-jdbc:12.8.1.jre11"),
            shuffle_partitions=int(p.get("shuffle_partitions", 4)),
            fetch_size=int(p.get("fetch_size", 10000)),
        )

        email = None
        email_section = next(
            (s for s in parser.sections() if s.lower() == "email"), None
        )
        if email_section is not None:
            e = parser[email_section]
            email = EmailConfig(
                enabled=e.getboolean("enabled", fallback=False),
                smtp_server=e["smtp_server"],
                smtp_port=int(e.get("smtp_port", 587)),
                smtp_user=e["smtp_user"],
                smtp_password=e["smtp_password"],
                from_email=e.get("from_email", e["smtp_user"]),
                to_email=tuple(
                    addr.strip() for addr in e["to_email"].split(",") if addr.strip()
                ),
                subject=e.get("subject", "Schwab Market Data Analytics Summary"),
            )

        instance = cls(sql=sql, spark=spark, email=email)
        cls._cache = instance      # cache it
        return instance

    @classmethod
    def reset(cls) -> None:
        """Clear cached singleton (useful in unit tests)."""
        cls._cache = None
