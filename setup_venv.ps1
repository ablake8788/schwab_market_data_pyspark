<#
.SYNOPSIS
    Creates the project's virtual environment and installs dependencies
    from requirements.txt (pyspark, py4j) plus pytest for the lightweight
    non-Spark test suite.
.EXAMPLE
    .\setup_venv.ps1
#>

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (!(Test-Path ".\.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

Write-Host "Installing dependencies from requirements.txt..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe -m pip install pytest

if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Warning "java not found on PATH. JDK 17 (Temurin recommended) is required to run Spark - see README.md Prerequisites."
} else {
    & java -version
}

Write-Host "`nDone. Either call scripts here directly, or activate with:"
Write-Host "  .\.venv\Scripts\activate"
