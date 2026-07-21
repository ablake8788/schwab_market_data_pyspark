<#
.SYNOPSIS
    Runs the SchwabQuotesHistory_SparkBollinger / _SparkZScore DDL scripts
    under sql\tables\ against SQL Server via sqlcmd, once, before using
    --write-back. Requires dbo.SchwabQuotesHistory to already exist
    (populated by the sibling schwab_market_data project).
.EXAMPLE
    # Windows Authentication (trusted connection)
    .\run_sql_ddl.ps1 -Server localhost -Database PBI_Projects
.EXAMPLE
    # SQL Server Authentication
    .\run_sql_ddl.ps1 -Server localhost -Database PBI_Projects -Username sa -Password "..."
#>

param(
    [Parameter(Mandatory = $true)] [string] $Server,
    [Parameter(Mandatory = $true)] [string] $Database,
    [string] $Username,
    [string] $Password
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$scripts = @(
    "sql\tables\SchwabQuotesHistory_SparkBollinger.sql",
    "sql\tables\SchwabQuotesHistory_SparkZScore.sql"
)

foreach ($script in $scripts) {
    Write-Host "Running $script ..."
    if ($Username) {
        sqlcmd -S $Server -d $Database -U $Username -P $Password -i $script
    } else {
        sqlcmd -S $Server -d $Database -E -i $script   # -E = Windows Authentication
    }
    if ($LASTEXITCODE -ne 0) {
        throw "sqlcmd failed on $script (exit code $LASTEXITCODE)"
    }
}

Write-Host "`nAll DDL scripts completed successfully."
