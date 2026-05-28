# Run this on the IIS server as Administrator
# iis-setup.ps1

$ErrorActionPreference = "Stop"
$siteName = "codewithtlp"
$sitePath = "C:\inetpub\wwwroot\codewithtlp"
$sourcePath = ".\browser"  # put the browser folder next to this script, or change this

Write-Host "=== 1. Checking IIS ==="
$iis = Get-WindowsFeature -Name Web-Server 2>$null
if (-not $iis -or -not $iis.Installed) {
    Write-Host "Installing IIS..."
    Install-WindowsFeature -Name Web-Server, Web-WebServer, Web-Common-Http, `
        Web-Default-Doc, Web-Dir-Browsing, Web-Http-Errors, Web-Static-Content, `
        Web-Http-Logging, Web-Stat-Compression, Web-Dyn-Compression, `
        Web-Filtering, Web-Basic-Auth, Web-Windows-Auth, Web-Net-Ext45, `
        Web-Asp-Net45, Web-ISAPI-Ext, Web-ISAPI-Filter, Web-Mgmt-Console -IncludeManagementTools
}

Write-Host "=== 2. Stopping Default Web Site ==="
Import-Module WebAdministration
if (Get-IISSite -Name "Default Web Site" -ErrorAction SilentlyContinue) {
    Stop-IISSite -Name "Default Web Site" -ErrorAction SilentlyContinue
    Write-Host "Default site stopped."
}

Write-Host "=== 3. Creating site folder ==="
if (-not (Test-Path $sitePath)) {
    New-Item -ItemType Directory -Path $sitePath -Force
}

Write-Host "=== 4. Copying files ==="
if (Test-Path $sourcePath) {
    Copy-Item -Path "$sourcePath\*" -Destination $sitePath -Recurse -Force
    Write-Host "Files copied from $sourcePath to $sitePath"
} else {
    Write-Host "WARNING: Source '$sourcePath' not found. Copy files manually to: $sitePath"
}

Write-Host "=== 5. Creating IIS Site ==="
Remove-IISSite -Name $siteName -ErrorAction SilentlyContinue
Remove-IISAppPool -Name $siteName -ErrorAction SilentlyContinue

New-IISAppPool -Name $siteName
Set-ItemProperty -Path "IIS:\AppPools\$siteName" -Name managedRuntimeVersion -Value ""

$site = New-IISSite -Name $siteName -PhysicalPath $sitePath `
    -BindingInformation "*:80:" -Protocol http -Force

# Add hostname binding (won't affect IP access since we have the blank one)
New-IISSiteBinding -Name $siteName `
    -BindingInformation "*:80:www.codewithtlp.me" -Protocol http

Start-IISSite -Name $siteName

Write-Host "=== 6. Setting folder permissions ==="
$acl = Get-Acl $sitePath
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "IIS_IUSRS", "ReadAndExecute", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
$acl | Set-Acl $sitePath
Write-Host "IIS_IUSRS added with read access."

Write-Host "=== 7. Check URL Rewrite ==="
$rewriteCheck = Get-WebConfigurationProperty -Filter "system.webServer/rewrite/rules" -PSPath "IIS:\Sites\$siteName" -ErrorAction SilentlyContinue
if (-not $rewriteCheck) {
    Write-Host "WARNING: URL Rewrite module may not be installed!"
    Write-Host "Download from: https://www.iis.net/downloads/microsoft/url-rewrite"
    Write-Host "Then recycle the app pool: Restart-WebAppPool $siteName"
}

Write-Host ""
Write-Host "=== DONE ==="
Write-Host "Test locally: http://localhost/"
Write-Host "Test by IP:   http://172.16.20.5/"
Write-Host ""
Write-Host "Verify index.html exists: $(Test-Path "$sitePath\index.html")"
Write-Host "Verify web.config exists: $(Test-Path "$sitePath\web.config")"
Write-Host ""
