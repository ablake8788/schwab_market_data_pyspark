"""reporting — pyodbc-based summary report generation + email delivery.

Deliberately separate from db/ (which reads/writes via Spark's JDBC path
for the main analytics job). This package is a lightweight consumer of
the *output* tables (SchwabQuotesHistory_SparkBollinger / _SparkZScore)
that doesn't need a SparkSession at all — just plain SQL aggregate queries.
"""
