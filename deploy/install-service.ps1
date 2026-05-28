# install-service.ps1
# Installs the FastAPI backend as a Windows Service using NSSM.
# NSSM (Non-Sucking Service Manager) keeps uvicorn running 24/7
# and auto-restarts if it crashes.

param(
    [string]$NssmPath = "${env:ProgramFiles}\nssm\nssm.exe",
    [string]$ServiceName = "StudyingApp-Backend",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$ScriptDir = Resolve-Path (Split-Path -Parent $MyInvocation.MyCommand.Path)

# ── Step 1: Download NSSM if not present ──────────────────────
if (-not (Test-Path $NssmPath)) {
    Write-Host "NSSM not found. Downloading..." -ForegroundColor Yellow
    $NssmDir = "${env:ProgramFiles}\nssm"

    if (-not (Test-Path $NssmDir)) {
        New-Item -ItemType Directory -Path $NssmDir -Force | Out-Null
    }

    $NssmZip = "$env:TEMP\nssm.zip"
    # Download NSSM 2.24 (stable)
    Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile $NssmZip

    Expand-Archive -Path $NssmZip -DestinationPath $env:TEMP\nssm-extract -Force
    Copy-Item "$env:TEMP\nssm-extract\nssm-2.24\win64\nssm.exe" $NssmDir -Force
    Remove-Item $NssmZip -Force
    Remove-Item "$env:TEMP\nssm-extract" -Recurse -Force

    Write-Host "[OK] NSSM installed to $NssmDir" -ForegroundColor Green
    $NssmPath = "$NssmDir\nssm.exe"
}

# ── Step 2: Verify backend path ────────────────────────────────
$PythonExe = "$ScriptDir\..\backend\.venv\Scripts\python.exe"
$AppDir = "$ScriptDir\..\backend"

if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python venv not found at: $PythonExe" -ForegroundColor Red
    exit 1
}

# ── Step 3: Remove existing service if present ─────────────────
$Existing = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($Existing) {
    Write-Host "Stopping existing service..." -ForegroundColor Yellow
    & $NssmPath stop $ServiceName 2>$null
    & $NssmPath remove $ServiceName confirm 2>$null
    Write-Host "[OK] Removed old service" -ForegroundColor Green
}

# ── Step 4: Create the NSSM service ────────────────────────────
Write-Host "Installing service: $ServiceName" -ForegroundColor Cyan

# The command that NSSM will run:
#   .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
$UvicornArgs = @(
    "-m", "uvicorn",
    "app.main:app",
    "--host", "127.0.0.1",
    "--port", $Port,
    "--workers", "1",
    "--log-level", "warning"
) -join " "

& $NssmPath install $ServiceName $PythonExe $UvicornArgs
& $NssmPath set $ServiceName AppDirectory $AppDir
& $NssmPath set $ServiceName AppStdout "$AppDir\logs\stdout.log"
& $NssmPath set $ServiceName AppStderr "$AppDir\logs\stderr.log"
& $NssmPath set $ServiceName AppRotateFiles 1
& $NssmPath set $ServiceName AppRotateOnline 1
& $NssmPath set $ServiceName AppRotateSeconds 86400
& $NssmPath set $ServiceName AppRotateBytes 1048576
& $NssmPath set $ServiceName AppExit Default Restart
& $NssmPath set $ServiceName AppRestartDelay 3000
& $NssmPath set $ServiceName Start SERVICE_AUTO_START
& $NssmPath set $ServiceName Description "Studying App — FastAPI backend (uvicorn)"

# Ensure logs directory exists
$LogDir = "$AppDir\logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# ── Step 5: Start the service ──────────────────────────────────
Write-Host "Starting service..." -ForegroundColor Cyan
& $NssmPath start $ServiceName

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Service installed successfully!" -ForegroundColor Green
Write-Host "  Name:     $ServiceName" -ForegroundColor White
Write-Host "  Status:   Running on http://127.0.0.1:$Port" -ForegroundColor White
Write-Host "  Logs:     $AppDir\logs\" -ForegroundColor White
Write-Host ""
Write-Host "  Manage:   services.msc" -ForegroundColor DarkGray
Write-Host "  Stop:     nssm stop $ServiceName" -ForegroundColor DarkGray
Write-Host "  Remove:   nssm remove $ServiceName confirm" -ForegroundColor DarkGray
Write-Host "============================================" -ForegroundColor Cyan
