# DEPLOY.md
# How to deploy Studying App on Windows Server with IIS

## Architecture

```
Browser ──→ IIS (port 80/443) ──→ Static files (Angular SPA)
                              ──→ Reverse proxy ──→ uvicorn :8000 (FastAPI)
```

---

## Step 1: Install Prerequisites on the Server

### 1a. IIS with required modules
```powershell
# Run as Administrator
Install-WindowsFeature -Name Web-Server, Web-WebServer, Web-Common-Http, Web-Static-Content, Web-Default-Doc, Web-Http-Errors, Web-Http-Redirect, Web-Stat-Compression, Web-Dyn-Compression, Web-Filtering, Web-Basic-Auth

# Download and install URL Rewrite Module
# https://www.iis.net/downloads/microsoft/url-rewrite

# Download and install Application Request Routing (ARR) 3.0
# https://www.iis.net/downloads/microsoft/application-request-routing
```

### 1b. Enable ARR Reverse Proxy
```
1. Open IIS Manager
2. Click the server node (top level)
3. Double-click "Application Request Routing Cache"
4. In the right Actions pane, click "Server Proxy Settings..."
5. Check "Enable proxy"
6. Leave other settings at defaults, click Apply
```

### 1c. Python
```powershell
# Install Python 3.13 from python.org
# Make sure to check "Add to PATH"

# Verify
python --version
```

---

## Step 2: Deploy the Backend

### 2a. Copy the backend folder to the server
```
Copy the entire backend\ folder to C:\Apps\studying-app\backend\
```

### 2b. Set up the Python environment
```powershell
cd C:\Apps\studying-app\backend
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 2c. Configure production settings
```powershell
# Copy the production env template
copy deploy\.env.production backend\.env

# Edit backend\.env — change SECRET_KEY and admin password!
notepad backend\.env
```

### 2d. Install as a Windows Service (stays running after reboot)
```powershell
cd C:\Apps\studying-app\deploy
.\install-service.ps1
```

### 2e. Verify the backend is running
```powershell
curl http://localhost:8000/health
# Should return: {"status":"ok","app":"Studying App",...}
```

---

## Step 3: Deploy the Frontend

### 3a. Build on your dev machine (or on the server if Node.js is installed)
```powershell
cd C:\Users\tamer\Desktop\stdying-app\deploy
.\deploy-frontend.ps1 -ApiUrl "http://localhost/api"
```
This creates `deploy\wwwroot\` with all static files + web.config.

### 3b. If building on the server itself:
```powershell
cd C:\Apps\studying-app
# Install Node.js first (from nodejs.org), then:
copy the entire frontend\ folder to the server
cd deploy
.\deploy-frontend.ps1 -ApiUrl "http://localhost/api"
```

---

## Step 4: Configure IIS

### 4a. Create the IIS Site
```powershell
# Run as Administrator
Import-Module WebAdministration

# Create app pool
New-WebAppPool -Name "StudyingApp"

# Create site pointing to the wwwroot folder
New-Website -Name "StudyingApp" -PhysicalPath "C:\Apps\studying-app\deploy\wwwroot" -ApplicationPool "StudyingApp" -Port 80

# Start the site
Start-Website -Name "StudyingApp"
```

### 4b. Or configure manually in IIS Manager:
```
1. Open IIS Manager (inetmgr)
2. Right-click "Sites" → "Add Website..."
3. Site name: StudyingApp
4. Physical path: C:\Apps\studying-app\deploy\wwwroot
5. Port: 80 (or 443 with HTTPS)
6. Click OK
```

### 4c. Set up HTTPS (optional but recommended)
```
1. Get a certificate (Let's Encrypt via win-acme, or a purchased cert)
2. In IIS, add binding: https, port 443, select your certificate
3. Install "URL Rewrite" redirect rule to force HTTPS
```

---

## Step 5: Verify Everything

```
1. Open http://localhost in a browser
2. You should see the Studying App landing page
3. Register a new account or login
4. Verify the API works (try browsing courses, profile, etc.)
```

### Health checks:
```
# Backend health
http://localhost:8000/health

# Frontend
http://localhost/

# API docs (through proxy)
http://localhost/api/docs
```

---

## Troubleshooting

### Backend won't start
```powershell
# Check the logs
type C:\Apps\studying-app\backend\logs\stdout.log
type C:\Apps\studying-app\backend\logs\stderr.log

# Try running manually to see errors
cd C:\Apps\studying-app\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### API calls return 502 Bad Gateway
```
1. Verify the backend service is running:  Get-Service StudyingApp-Backend
2. Verify uvicorn is listening:           netstat -ano | findstr 8000
3. Check ARR proxy is enabled:            IIS → Server → Application Request Routing Cache → Server Proxy Settings
4. Check URL Rewrite rules are correct:   IIS → Site → URL Rewrite
```

### 403 Forbidden on API calls
```
1. IIS → Site → URL Rewrite → "View Server Variables..."
2. Add HTTP_X_FORWARDED_HOST and HTTP_X_FORWARDED_PROTO to allowed list
3. Restart the IIS site
```

### Frontend routes (like /catalog) return 404
```
Make sure URL Rewrite rules are applied:
IIS → Site → URL Rewrite → "Angular SPA Fallback" rule should be present
```

### Service management commands
```powershell
# Check service status
Get-Service StudyingApp-Backend

# Restart the service
Restart-Service StudyingApp-Backend

# Stop the service
Stop-Service StudyingApp-Backend

# Remove the service entirely
nssm remove StudyingApp-Backend confirm
```
