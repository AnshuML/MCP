# Run Istedlal MCP Server
# Usage: .\scripts\run.ps1 [stdio|http]

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

$transport = if ($args[0]) { $args[0] } else { "stdio" }
$env:MCP_TRANSPORT = $transport

Write-Host "Starting MCP Server (transport: $transport)..." -ForegroundColor Green
python -m src.main
