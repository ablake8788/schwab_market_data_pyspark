<#
.SYNOPSIS
    Runs the lightweight unit test suite (CLI arg parsing + config loading).
    These tests do not create a SparkSession — no JDK/Spark cluster needed,
    so this runs fast and works in CI.
.EXAMPLE
    .\run_tests.ps1
#>

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& .\.venv\Scripts\python.exe -m pytest tests\ -v
exit $LASTEXITCODE
