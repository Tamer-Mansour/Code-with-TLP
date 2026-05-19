# PowerShell wrapper for the Makefile.
# Use this if you don't have `make` on PATH.
#
#   .\make.ps1            -> help
#   .\make.ps1 install
#   .\make.ps1 test
#   .\make.ps1 run
#   .\make.ps1 bootstrap

param(
    [Parameter(Position = 0)]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
$ROOT = $PSScriptRoot
$BACKEND = Join-Path $ROOT "backend"
$VENV = Join-Path $BACKEND ".venv"
$PY = Join-Path $VENV "Scripts\python.exe"
$UVICORN = Join-Path $VENV "Scripts\uvicorn.exe"
$PORT = if ($env:PORT) { $env:PORT } else { "8000" }
$HOSTADDR = if ($env:HOST) { $env:HOST } else { "0.0.0.0" }

function Run-Help {
    Write-Host "Studying App — targets" -ForegroundColor Cyan
    Write-Host ""
    @"
  .\make.ps1 install      Create venv and install backend dependencies
  .\make.ps1 env          Copy backend/.env.example to backend/.env if missing
  .\make.ps1 runners      Build the Docker sandbox images (Python/Node/Java/C#)
  .\make.ps1 seed         Run the database seed
  .\make.ps1 run          Start FastAPI server on ${HOSTADDR}:${PORT} with reload
  .\make.ps1 run-prod     Start FastAPI server without reload
  .\make.ps1 test         Run the pytest suite
  .\make.ps1 test-cov     Run pytest with coverage report
  .\make.ps1 health       Curl /health
  .\make.ps1 swagger      Open Swagger UI in your default browser
  .\make.ps1 freeze       List installed packages
  .\make.ps1 bootstrap    install + env + seed (no Docker required)
  .\make.ps1 all          bootstrap + runners (full setup, Docker required)
  .\make.ps1 clean        Remove venv, caches, and the SQLite database
"@
}

function Ensure-Venv {
    if (-not (Test-Path $PY)) {
        throw "venv not found at $VENV. Run '.\make.ps1 install' first."
    }
}

function Run-Install {
    Write-Host "=== Creating virtualenv ===" -ForegroundColor Cyan
    if (-not (Test-Path $VENV)) { python -m venv $VENV }
    Write-Host "=== Upgrading pip ===" -ForegroundColor Cyan
    & $PY -m pip install --upgrade pip
    Write-Host "=== Installing requirements ===" -ForegroundColor Cyan
    & $PY -m pip install -r (Join-Path $BACKEND "requirements.txt")
    Write-Host "=== Install complete ===" -ForegroundColor Green
}

function Run-Env {
    $envFile = Join-Path $BACKEND ".env"
    $example = Join-Path $BACKEND ".env.example"
    if (-not (Test-Path $envFile)) {
        Copy-Item $example $envFile
        Write-Host "Created backend\.env" -ForegroundColor Green
    } else {
        Write-Host "backend\.env already exists"
    }
}

function Run-Runners {
    & (Join-Path $BACKEND "docker\runners\build-all.ps1")
}

function Run-Seed {
    Ensure-Venv
    Push-Location $BACKEND
    try { & $PY -m app.seed } finally { Pop-Location }
}

function Run-Serve($prod = $false) {
    Ensure-Venv
    Push-Location $BACKEND
    try {
        $reloadFlag = if ($prod) { @() } else { @("--reload") }
        & $UVICORN app.main:app @reloadFlag --host $HOSTADDR --port $PORT
    } finally { Pop-Location }
}

function Run-Tests($withCov = $false) {
    Ensure-Venv
    Push-Location $BACKEND
    try {
        if ($withCov) {
            & $PY -m pytest --cov=app --cov-report=term-missing --cov-report=html
        } else {
            & $PY -m pytest -v
        }
    } finally { Pop-Location }
}

function Run-Health {
    try { Invoke-RestMethod "http://localhost:$PORT/health" | ConvertTo-Json -Depth 10 }
    catch { Write-Warning "Server not reachable on port $PORT — start it with '.\make.ps1 run'" }
}

function Run-Swagger {
    Start-Process "http://localhost:$PORT/docs"
}

function Run-Freeze {
    Ensure-Venv
    & $PY -m pip freeze
}

function Run-Clean {
    foreach ($p in @(
        $VENV,
        (Join-Path $BACKEND ".pytest_cache"),
        (Join-Path $BACKEND "htmlcov"),
        (Join-Path $BACKEND "studying_app.db")
    )) {
        if (Test-Path $p) {
            Remove-Item -Recurse -Force $p
            Write-Host "Removed $p"
        }
    }
    Write-Host "=== Clean complete ===" -ForegroundColor Green
}

switch ($Target.ToLower()) {
    "help"      { Run-Help }
    "install"   { Run-Install }
    "env"       { Run-Env }
    "runners"   { Run-Runners }
    "seed"      { Run-Seed }
    "run"       { Run-Serve }
    "run-prod"  { Run-Serve -prod $true }
    "test"      { Run-Tests }
    "test-cov"  { Run-Tests -withCov $true }
    "health"    { Run-Health }
    "swagger"   { Run-Swagger }
    "freeze"    { Run-Freeze }
    "bootstrap" { Run-Install; Run-Env; Run-Seed }
    "all"       { Run-Install; Run-Env; Run-Seed; Run-Runners }
    "clean"     { Run-Clean }
    default     {
        Write-Warning "Unknown target: $Target"
        Run-Help
        exit 1
    }
}
