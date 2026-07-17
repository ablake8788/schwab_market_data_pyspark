Use PBI_Projects
GO

    -- dbo.SchwabQuotesHistory_SparkBollinger
-- Output table for analytics/bollinger.py, written by db/analytics_writer.py.
-- Distinct from the existing SQL-computed SchwabQuotesAnalyticsBollingerBands*
-- tables in the schwab_market_data project — this one holds Spark-computed results.

IF NOT EXISTS (
    SELECT 1 FROM sys.tables WHERE name = 'SchwabQuotesHistory_SparkBollinger' AND schema_id = SCHEMA_ID('dbo')
)
BEGIN
    CREATE TABLE dbo.SchwabQuotesHistory_SparkBollinger (
        Id           int IDENTITY(1,1) NOT NULL PRIMARY KEY,
        Symbol       nvarchar(20)    NOT NULL,
        BarDateTime  datetime2       NOT NULL,
        ClosePrice   decimal(18,4)   NULL,
        WindowSize   int             NOT NULL,
        NumStdDev    decimal(9,4)    NOT NULL,
        MovingAvg    decimal(18,8)   NULL,
        RollingStd   decimal(18,8)   NULL,
        UpperBand    decimal(18,8)   NULL,
        LowerBand    decimal(18,8)   NULL,
        IsWarmup     bit             NOT NULL,
        LoadDate     datetime2       NOT NULL,
        BatchId      uniqueidentifier NOT NULL
    );

    CREATE INDEX IX_SchwabQuotesHistory_SparkBollinger_Symbol_BarDateTime
        ON dbo.SchwabQuotesHistory_SparkBollinger (Symbol, BarDateTime);
END
