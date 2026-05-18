Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  Starting Smart Pricing Ecosystem Architecture" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "1. Starting Docker Infrastructure (Vault, Jenkins, ELK, DB)..." -ForegroundColor Yellow
docker-compose -f docker-compose.yml -f docker-compose.elk.yml -f docker-compose.vault.yml up -d jenkins postgres redis vault elasticsearch logstash kibana

Write-Host "2. Starting Kubernetes Cluster..." -ForegroundColor Yellow
minikube start

Write-Host "3. Applying Application Manifests..." -ForegroundColor Yellow
kubectl apply -f k8s/deployments/app-deployments.yaml
kubectl apply -f k8s/services/app-services.yaml

Write-Host "Waiting 20 seconds for pods to boot..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

Write-Host "4. Seeding Database and Machine Learning Model into Pods..." -ForegroundColor Yellow
$api_pods = (kubectl get pods -n spe-platform -l app=pricing-api -o jsonpath="{.items[*].metadata.name}") -split " "
foreach ($pod in $api_pods) {
    if ($pod) {
        Write-Host "   Injecting into $pod..." -ForegroundColor Gray
        kubectl cp data/ "spe-platform/$pod`:/app/data/"
        kubectl cp pricing_model.pkl "spe-platform/$pod`:/app/data/pricing_model.pkl"
        kubectl exec -n spe-platform $pod -- sh -c "mv /app/data/data/* /app/data/ 2>/dev/null"
        kubectl exec -n spe-platform $pod -- sh -c "kill 1"
    }
}

Write-Host "5. Establishing Port Forwards..." -ForegroundColor Yellow
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward svc/admin-dashboard 8503:8503 -n spe-platform --address 127.0.0.1"
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward svc/customer-portal 8504:8504 -n spe-platform --address 127.0.0.1"
Start-Process -NoNewWindow kubectl -ArgumentList "port-forward svc/pricing-api 5001:5001 -n spe-platform --address 127.0.0.1"

Write-Host "6. Syncing Kubernetes Logs to Logstash..." -ForegroundColor Yellow
Start-Process -NoNewWindow powershell -ArgumentList "-Command kubectl exec deployment/pricing-api -n spe-platform -c pricing-api -- tail -f /app/logs/api.log > logs/api.log"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "Architecture Fully Live!" -ForegroundColor Green
Write-Host "Admin Dashboard: http://localhost:8503"
Write-Host "Customer Portal: http://localhost:8504"
Write-Host "Kibana Logs:     http://localhost:5601"
Write-Host "=================================================" -ForegroundColor Cyan
