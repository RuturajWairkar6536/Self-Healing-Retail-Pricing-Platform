# =====================================================================
# Infrastructure Startup Script
# Description: Starts ELK, Vault, Jenkins, Postgres, Redis via Docker Compose.
# =====================================================================

Write-Host "Starting Core Infrastructure..." -ForegroundColor Cyan

# 1. Check if Docker is running
docker info >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker is not running! Please start Docker Desktop and wait for it to initialize." -ForegroundColor Red
    exit 1
}

# 2. Create networks if they don't exist
Write-Host "Setting up Docker networks..." -ForegroundColor Yellow
docker network inspect spe-network >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    docker network create spe-network
}

# 3. Start ELK Stack
Write-Host "Starting ELK Stack..." -ForegroundColor Yellow
docker-compose -f docker-compose.elk.yml up -d

# 4. Start Vault
Write-Host "Starting Hashicorp Vault..." -ForegroundColor Yellow
docker-compose -f docker-compose.vault.yml up -d

# 5. Start Jenkins & Databases
Write-Host "Starting Jenkins, Postgres, and Redis..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml up -d jenkins postgres redis

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "Infrastructure started!" -ForegroundColor Green
Write-Host "Waiting for services to become healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "Seeding secure credentials into Hashicorp Vault..." -ForegroundColor Yellow
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -e VAULT_TOKEN=spe-dev-root vault vault kv put secret/spe/dockerhub username="ruturajwairkar" password="mock_dockerhub_token_xyz123" >$null 2>&1
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -e VAULT_TOKEN=spe-dev-root vault vault kv put secret/spe/kubeconfig kubeconfig="apiVersion: v1`nkind: Config`nclusters: []" >$null 2>&1
docker exec -e VAULT_ADDR=http://127.0.0.1:8200 -e VAULT_TOKEN=spe-dev-root vault vault kv put secret/spe/app reload_token="spe-platform-secure-token-2026" >$null 2>&1

Write-Host "Verify status using 'docker ps'." -ForegroundColor Green
Write-Host "- ELK (Kibana): http://localhost:5601"
Write-Host "- Vault: http://localhost:8200"
Write-Host "- Jenkins: http://localhost:8081"
Write-Host "=====================================================================" -ForegroundColor Cyan
