<#
.SYNOPSIS
    Builds the Bollinger Bands / Z-Score summary report (.docx) from
    dbo.SchwabQuotesHistory_SparkBollinger / _SparkZScore, optionally
    emailing it via the [email] section of schwab_market_data_pyspark.ini.
    No Spark session needed - pyodbc only.
.EXAMPLE
    .\run_report.ps1
.EXAMPLE
    .\run_report.ps1 -SendEmail
#>

param(
    [string] $Output = "reports\schwab_analytics_summary.docx",
    [switch] $SendEmail,
    [int] $TopAnomalies = 15,
    [string] $LogDir
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pyArgs = @("report_main.py", "--output", $Output, "--top-anomalies", $TopAnomalies)
if ($SendEmail) { $pyArgs += "--send-email" }
if ($LogDir) { $pyArgs += @("--log-dir", $LogDir) }

& .\.venv\Scripts\python.exe @pyArgs
exit $LASTEXITCODE
