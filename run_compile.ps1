<#
.SYNOPSIS
    Byte-compiles all project source files (main.py, core, db, analytics,
    cli, spark_session, tests) to catch syntax errors without running
    anything — no JDK/SQL Server connection required.
.EXAMPLE
    .\run_compile.ps1
#>

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& .\.venv\Scripts\python.exe -m compileall -q main.py report_main.py core db analytics cli spark_session reporting tests
exit $LASTEXITCODE
