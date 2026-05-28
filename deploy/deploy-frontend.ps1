# deploy-frontend.ps1
# Builds the Angular frontend for production and outputs to a deployable folder.
# The output folder can be pointed to directly by IIS or copied to the server.

param(
    [string]$OutputPath = "..\deploy\wwwroot",      # Where IIS points to
    [string]$ApiUrl = "http://localhost/api",       # URL for the IIS-proxied backend
    [string]$BaseHref = "/"                          # Base href for Angular router
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendDir = "$ScriptDir\..\frontend"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Studying App — Frontend Build" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verify npm / Angular CLI
Push-Location $FrontendDir

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
}

# Create production environment file with IIS API URL
$EnvContent = @"
export const environment = {
  production: true,
  apiUrl: '$ApiUrl',
};
"@

Set-Content -Path "src\environments\environment.prod.ts" -Value $EnvContent
Set-Content -Path "src\environments\environment.ts" -Value $EnvContent

Write-Host "[OK] API URL set to: $ApiUrl" -ForegroundColor Green
Write-Host ""

# Build for production
Write-Host "Building Angular app (production)..." -ForegroundColor Cyan
npm run build -- --configuration production --base-href "$BaseHref" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Build failed" -ForegroundColor Red
    Pop-Location
    exit 1
}

# Copy to IIS wwwroot folder
$DistDir = "dist\studying-app\browser"
$OutAbsolute = Resolve-Path $OutputPath -ErrorAction SilentlyContinue
if (-not $OutAbsolute) {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
    $OutAbsolute = Resolve-Path $OutputPath
}

Write-Host ""
Write-Host "Copying to: $OutAbsolute" -ForegroundColor Cyan
if (Test-Path $OutAbsolute) {
    Remove-Item "$OutAbsolute\*" -Recurse -Force -ErrorAction SilentlyContinue
}
Copy-Item "$DistDir\*" $OutAbsolute -Recurse -Force

# Copy IIS web.config for Angular SPA routing
Copy-Item "$ScriptDir\web.config" $OutAbsolute -Force

Pop-Location

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Frontend built successfully!" -ForegroundColor Green
Write-Host "  Output:    $OutAbsolute" -ForegroundColor White
Write-Host "  API URL:   $ApiUrl" -ForegroundColor White
Write-Host ""
Write-Host "  Point IIS to: $OutAbsolute" -ForegroundColor DarkGray
Write-Host "============================================" -ForegroundColor Cyan
