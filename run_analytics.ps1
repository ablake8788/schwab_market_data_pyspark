<#
.SYNOPSIS
    Runs the Spark analytics job — rolling moving averages, Bollinger Bands,
    and z-score anomaly flags over dbo.SchwabQuotesHistory (main.py).
    Requires JDK 17 on PATH/JAVA_HOME; spark.jars.packages fetches the
    mssql-jdbc driver from Maven Central on first run (needs internet).
.EXAMPLE
    .\run_analytics.ps1 -Symbols AAPL,MSFT -Start 2026-01-01 -End 2026-07-01
.EXAMPLE
    .\run_analytics.ps1 -Symbols AAPL -Start 2026-01-01 -End 2026-07-01 -Window 20 -WriteBack -WriteMode overwrite
#>

param(
    [Parameter(Mandatory = $true)] [string] $Symbols,
    [Parameter(Mandatory = $true)] [string] $Start,
    [Parameter(Mandatory = $true)] [string] $End,
    [int] $Window = 20,
    [double] $NumStd = 2.0,
    [double] $ZThreshold = 2.0,
    [switch] $WriteBack,
    [ValidateSet("append", "overwrite")] [string] $WriteMode = "append",
    [string] $LogDir
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pyArgs = @(
    "main.py",
    "--symbols", $Symbols,
    "--start", $Start,
    "--end", $End,
    "--window", $Window,
    "--num-std", $NumStd,
    "--z-threshold", $ZThreshold,
    "--write-mode", $WriteMode
)
if ($WriteBack) { $pyArgs += "--write-back" }
if ($LogDir) { $pyArgs += @("--log-dir", $LogDir) }

& .\.venv\Scripts\python.exe @pyArgs
exit $LASTEXITCODE
