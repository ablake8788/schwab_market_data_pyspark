<#
.SYNOPSIS
    Builds a standalone Windows executable (dist\schwab_market_data_pyspark.exe)
    from schwab_market_data_pyspark.spec using PyInstaller. Requires
    pyinstaller in .venv (pip install pyinstaller).

    The EXE still requires a separately installed JDK 17 (Temurin
    recommended) and winutils.exe/hadoop.dll on HADOOP_HOME on the machine
    that runs it — PyInstaller bundles the Python side only, never the JVM.
.EXAMPLE
    .\run_build_exe.ps1
#>

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

& .\.venv\Scripts\python.exe -m PyInstaller --clean schwab_market_data_pyspark.spec
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (!(Test-Path ".\dist")) {
    New-Item -ItemType Directory -Path ".\dist" | Out-Null
}

if (Test-Path ".\schwab_market_data_pyspark.ini") {
    Copy-Item ".\schwab_market_data_pyspark.ini" ".\dist\schwab_market_data_pyspark.ini" -Force
}

Write-Host "Build complete. EXE is in .\dist"
exit $LASTEXITCODE
