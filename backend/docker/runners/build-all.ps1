# Build all runner images. Run from backend/ directory.
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "Building python runner..." -ForegroundColor Cyan
docker build -t studying-runner-python:latest "$here/python"

Write-Host "Building node runner..." -ForegroundColor Cyan
docker build -t studying-runner-node:latest "$here/node"

Write-Host "Building java runner..." -ForegroundColor Cyan
docker build -t studying-runner-java:latest "$here/java"

Write-Host "Building csharp runner..." -ForegroundColor Cyan
docker build -t studying-runner-csharp:latest "$here/csharp"

Write-Host "All runner images built." -ForegroundColor Green
