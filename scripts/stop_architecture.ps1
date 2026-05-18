Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Stopping Smart Pricing Ecosystem Architecture" -ForegroundColor Red
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "1. Stopping Kubernetes Cluster (Minikube)..." -ForegroundColor Yellow
minikube stop

Write-Host "2. Stopping Docker Infrastructure (ELK, Vault, DB, Jenkins)..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.elk.yml -f docker-compose.vault.yml down

Write-Host "3. Killing background port-forwards..." -ForegroundColor Yellow
Stop-Process -Name kubectl -Force -ErrorAction SilentlyContinue

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Architecture is fully shut down and resources are freed!" -ForegroundColor Green
