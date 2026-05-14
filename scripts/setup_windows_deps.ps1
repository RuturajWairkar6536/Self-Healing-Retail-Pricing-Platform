# =====================================================================
# Windows Infrastructure Setup Script
# Description: Installs Docker Desktop, Minikube, Helm, and WSL.
# Run this script as Administrator.
# =====================================================================

Write-Host "Starting Installation of Windows Infrastructure Dependencies..." -ForegroundColor Cyan

# 1. Check for winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget is not installed. Please install App Installer from Microsoft Store." -ForegroundColor Red
    exit 1
}

# 2. Install WSL (Ubuntu) for Ansible
Write-Host "Checking WSL..." -ForegroundColor Yellow
$wsl_status = wsl --status 2>&1
if ($wsl_status -match "has no installed distributions" -or $wsl_status -match "is not recognized") {
    Write-Host "Installing WSL (Ubuntu default)... This may require a reboot." -ForegroundColor Green
    wsl --install -d Ubuntu
} else {
    Write-Host "WSL appears to be installed." -ForegroundColor Green
}

# 3. Install Docker Desktop
Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow
winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements

# 4. Install Minikube
Write-Host "Installing Minikube..." -ForegroundColor Yellow
winget install -e --id Kubernetes.minikube --accept-package-agreements --accept-source-agreements

# 5. Install Helm
Write-Host "Installing Helm..." -ForegroundColor Yellow
winget install -e --id Helm.Helm --accept-package-agreements --accept-source-agreements

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "IMPORTANT: You may need to RESTART your computer for Docker and WSL changes to take effect." -ForegroundColor Red
Write-Host "After restarting, open Docker Desktop to accept the terms and ensure the engine starts." -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
