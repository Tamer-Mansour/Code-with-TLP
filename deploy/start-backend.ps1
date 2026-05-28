# deploy-backend.ps1
# Starts the FastAPI backend with uvicorn as a background process.
# Run this on the IIS server — keeps the backend alive without a console window.

param(
    [int]$Port = 8000,
    [string]$HostBind = "127.0.0.1",  # Bind to localhost only (IIS proxies to it)
    [int]$Workers = 1                  # Single worker for SQLite
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Studying App — FastAPI Backend" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verify Python venv exists
$PythonExe = "$ScriptDir\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Virtual environment not found at .venv\" -ForegroundColor Red
    Write-Host "        Run: python -m venv .venv && .\.venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Verify .env file
$EnvFile = "$ScriptDir\.env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "[WARN] No .env file found. Copy .env.example and edit it." -ForegroundColor Yellow
}

Write-Host "[OK] Python:  $PythonExe" -ForegroundColor Green
Write-Host "[OK] Port:    $Port" -ForegroundColor Green
Write-Host "[OK] Workers: $Workers" -ForegroundColor Green
Write-Host ""

$Args = @(
    "-m", "uvicorn",
    "app.main:app",
    "--host", $HostBind,
    "--port", $Port,
    "--workers", $Workers,
    "--log-level", "info"
)

Write-Host "Starting uvicorn..." -ForegroundColor Cyan
Write-Host "Backend will be available at http://${HostBind}:${Port}" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor DarkGray
Write-Host ""

try {
    Set-Location $ScriptDir
    & $PythonExe @Args
} catch {
    Write-Host "[ERROR] Failed to start backend: $_" -ForegroundColor Red
    exit 1
}
