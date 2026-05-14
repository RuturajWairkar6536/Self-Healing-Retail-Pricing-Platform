# SPE Platform - Quick Reference Commands

## 🚀 Start & Stop

### Start All Services
```bash
# Automated (recommended)
./scripts/devops-setup.sh

# Or manual Docker Compose
docker-compose up -d

# Or manual Kubernetes
minikube start
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml
```

### Stop All Services
```bash
# Docker
docker-compose down

# Kubernetes
kubectl delete namespace spe-platform
```

---

## 🐳 Docker Monitoring (Most Common)

### Quick Health Check
```bash
# One-liner: Check all services
chmod +x scripts/health-check.sh && ./scripts/health-check.sh

# Or manual check
curl http://localhost:5001/health         # Pricing API
curl http://localhost:8503/_stcore/health # Admin
curl http://localhost:8504/_stcore/health # Customer
```

### View Status
```bash
docker ps                          # All running containers
docker-compose ps                  # Compose services status
```

### View Logs
```bash
docker logs pricing-api            # Single container
docker logs -f pricing-api         # Follow logs
docker-compose logs                # All services
docker-compose logs -f pricing-api # Follow specific service
```

### Resource Usage
```bash
docker stats                       # CPU, Memory usage
docker stats --no-stream          # One-time snapshot
```

### Container Details
```bash
docker inspect pricing-api         # Full info
docker exec pricing-api curl localhost:5001/health  # Run command in container
docker exec -it pricing-api bash   # Interactive shell
```

---

## ☸️ Kubernetes Monitoring

### Quick K8s Check
```bash
# Automated
chmod +x scripts/monitor-k8s.sh && ./scripts/monitor-k8s.sh

# Or manual
kubectl get pods -n spe-platform
kubectl get pods -n spe-platform -o wide  # With more details
```

### Pod Details
```bash
kubectl describe pod <pod_name> -n spe-platform
kubectl logs -f pod/<pod_name> -n spe-platform
kubectl exec -it pod/<pod_name> -n spe-platform -- bash
```

### Deployments
```bash
kubectl get deployments -n spe-platform
kubectl rollout status deployment/pricing-api -n spe-platform
kubectl scale deployment/pricing-api --replicas=3 -n spe-platform
```

### Services
```bash
kubectl get services -n spe-platform
kubectl get endpoints -n spe-platform
kubectl port-forward svc/pricing-api 5001:5001 -n spe-platform
```

### Events & Logs
```bash
kubectl get events -n spe-platform --sort-by='.lastTimestamp'
kubectl logs -f deployment/pricing-api -n spe-platform
```

---

## 🔧 Common Tasks

### Restart a Service
```bash
# Docker
docker restart pricing-api

# Kubernetes
kubectl rollout restart deployment/pricing-api -n spe-platform
```

### View Container/Pod Logs
```bash
# Docker - last 50 lines
docker logs --tail=50 pricing-api

# Docker - follow in real-time
docker logs -f pricing-api

# Kubernetes - follow in real-time
kubectl logs -f pod/<pod_name> -n spe-platform
```

### Scale Replicas (K8s)
```bash
# Manual scale
kubectl scale deployment/pricing-api --replicas=5 -n spe-platform

# Check HPA auto-scaling
kubectl get hpa -n spe-platform
```

### Check Resource Usage
```bash
# Docker
docker stats

# Kubernetes
kubectl top pods -n spe-platform
kubectl top nodes
```

### Troubleshoot Pod Issues
```bash
# Pod status
kubectl describe pod <pod_name> -n spe-platform

# Check if ready
kubectl get pod <pod_name> -n spe-platform -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'

# Previous logs if crashed
kubectl logs <pod_name> -n spe-platform --previous
```

---

## 📊 Dashboard Access

| Service | URL |
|---------|-----|
| Pricing API | http://localhost:5001 |
| Admin Dashboard | http://localhost:8503 |
| Customer Portal | http://localhost:8504 |
| Jenkins CI/CD | http://localhost:8080 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

---

## 🆘 Troubleshooting

### Service Not Responding
```bash
# Docker: Check if running
docker ps | grep <service>

# Kubernetes: Check pod status
kubectl get pods -n spe-platform

# Check logs
docker logs <container> | grep -i error
kubectl logs pod/<pod> -n spe-platform | grep -i error
```

### Port Already in Use
```bash
# Find process
lsof -i :5001

# Kill process
kill -9 <PID>
```

### Database Connection Failed
```bash
# Docker: Check DB
docker exec postgres-db pg_isready -U spe_user

# Kubernetes: Check DB pod
kubectl describe pod postgres-db-xyz -n spe-platform
```

### Container/Pod Won't Start
```bash
# Docker
docker logs <container> 2>&1 | tail -30

# Kubernetes
kubectl describe pod <pod> -n spe-platform
kubectl logs <pod> -n spe-platform --previous
```

---

## 🎯 Monitoring Scripts (Ready to Use)

Make scripts executable first:
```bash
chmod +x scripts/*.sh
```

### Health Check (All Services)
```bash
./scripts/health-check.sh
```

### Docker Monitoring Dashboard
```bash
./scripts/monitor-docker.sh
```

### Kubernetes Monitoring Dashboard
```bash
./scripts/monitor-k8s.sh
```

---

## 📝 Command Cheat Sheet

```bash
# ===== DOCKER COMPOSE =====
docker-compose up -d              # Start all
docker-compose down               # Stop all
docker-compose restart            # Restart all
docker-compose ps                 # List services
docker-compose logs -f            # View logs
docker-compose build              # Build images
docker-compose exec pricing-api bash  # Shell into service

# ===== DOCKER =====
docker ps                         # List running
docker ps -a                      # List all
docker logs -f <container>        # Follow logs
docker inspect <container>        # Details
docker stats                      # Resource usage
docker restart <container>        # Restart
docker rm <container>             # Remove

# ===== KUBERNETES =====
kubectl get pods -n spe-platform                    # List pods
kubectl describe pod <pod> -n spe-platform          # Pod details
kubectl logs -f pod/<pod> -n spe-platform           # Follow logs
kubectl exec -it pod/<pod> -n spe-platform -- bash  # Shell access
kubectl top pods -n spe-platform                    # Resource usage
kubectl get events -n spe-platform                  # Events
kubectl scale deployment/<name> --replicas=3 -n spe-platform  # Scale
kubectl rollout restart deployment/<name> -n spe-platform     # Restart

# ===== HEALTH CHECKS =====
curl http://localhost:5001/health          # Pricing API
curl http://localhost:8503/_stcore/health  # Admin
curl http://localhost:8504/_stcore/health  # Customer

# ===== JENKINS =====
docker logs -f jenkins                     # Jenkins logs
curl http://localhost:8080/api/json        # Jenkins API
```

---

## 🎓 Examples

### Example 1: Check if All Services are Running
```bash
docker ps --format "table {{.Names}}\t{{.Status}}"

# Output:
# NAMES               STATUS
# pricing-api         Up 5 minutes
# admin-dashboard     Up 5 minutes
# customer-portal     Up 5 minutes
```

### Example 2: Check API Response
```bash
curl http://localhost:5001/products | jq '.'

# Output:
# {
#   "products": [...]
# }
```

### Example 3: View Error Logs
```bash
docker logs pricing-api 2>&1 | grep -i error | head -10
```

### Example 4: Check Kubernetes Pod Health
```bash
kubectl get pods -n spe-platform -o custom-columns=NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status,STATUS:.status.phase

# Output:
# NAME                            READY   STATUS
# pricing-api-xyz1234            True    Running
# admin-dashboard-abc5678        True    Running
# customer-portal-def9012        True    Running
```

### Example 5: Scale Up Pricing API
```bash
kubectl scale deployment/pricing-api --replicas=5 -n spe-platform

# Verify
kubectl get pods -n spe-platform | grep pricing-api
```

---

## 🔔 Set Up Monitoring Dashboard

### Option 1: Terminal Watch (Simple)
```bash
# Watch pods in real-time
kubectl get pods -n spe-platform -w

# Or Docker
watch -n 5 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
```

### Option 2: Multiple Terminals
```bash
# Terminal 1: Docker logs
docker-compose logs -f

# Terminal 2: Resource usage
watch -n 5 'docker stats --no-stream'

# Terminal 3: Pod status (K8s)
watch -n 5 'kubectl get pods -n spe-platform'
```

### Option 3: Automated Monitoring Script
```bash
# Run comprehensive monitoring
while true; do
  clear
  echo "=== SPE Platform Monitoring ==="
  echo "Containers:"
  docker ps --format "table {{.Names}}\t{{.Status}}"
  echo ""
  echo "Resource Usage:"
  docker stats --no-stream | head -5
  sleep 10
done
```

---

## 📞 Quick Help

```bash
# All Dockerfiles
ls -la Dockerfile*

# All Kubernetes files
ls -la k8s/**/*.yaml

# All monitoring scripts
ls -la scripts/

# View full documentation
cat RUNNING_AND_MONITORING.md
cat DEVOPS_GUIDE.md
```

---

**Save this file for quick reference!**
