# SPE Platform - Running & Monitoring Guide (Localhost)

## 🚀 Part 1: Running the Project Locally

### Option A: Automated One-Command Setup ⭐ (Recommended)

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Make script executable
chmod +x scripts/devops-setup.sh

# Run entire setup
./scripts/devops-setup.sh
```

**What it does automatically:**
- ✅ Installs Docker, Docker Compose, kubectl, Ansible, Jenkins
- ✅ Builds all 4 Docker images
- ✅ Starts docker-compose with 6 services
- ✅ Runs health checks
- ✅ Displays all service URLs

**Expected output:**
```
===== SERVICE ENDPOINTS =====
Pricing API:      http://localhost:5001
Admin Dashboard:  http://localhost:8503
Customer Portal:  http://localhost:8504
PostgreSQL:       localhost:5432
Redis:            localhost:6379
Jenkins:          http://localhost:8080

===== NEXT STEPS =====
1. Access the admin dashboard at http://localhost:8503
2. Access the customer portal at http://localhost:8504
3. Check API health: curl http://localhost:5001/health
4. For Kubernetes deployment: ansible-playbook ansible/deploy-k8s.yml
5. View logs: docker-compose logs -f
```

---

### Option B: Manual Docker Compose Setup

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Step 1: Build all Docker images
docker-compose build

# Step 2: Start all services
docker-compose up -d

# Step 3: Verify services are running
docker-compose ps

# Step 4: Wait 10-15 seconds for services to be ready
sleep 15

# Step 5: Test API health
curl http://localhost:5001/health

# Step 6: View logs if needed
docker-compose logs -f
```

---

### Option C: Manual Kubernetes Setup

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Step 1: Start Kubernetes (if using minikube)
minikube start --cpus=4 --memory=8192

# Step 2: Install necessary tools (if not already done)
ansible-playbook -i ansible/hosts.ini ansible/site.yml

# Step 3: Deploy to Kubernetes
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml

# Step 4: Wait for deployments
kubectl get pods -n spe-platform -w

# Step 5: Get service endpoints
kubectl get svc -n spe-platform

# Step 6: Port-forward to access services locally
kubectl port-forward -n spe-platform svc/pricing-api 5001:5001 &
kubectl port-forward -n spe-platform svc/admin-dashboard 8503:8503 &
kubectl port-forward -n spe-platform svc/customer-portal 8504:8504 &
```

---

## 🐳 Part 2: Checking Docker Containers

### View Running Containers

```bash
# List all running containers
docker ps

# Expected output:
# CONTAINER ID   IMAGE                          STATUS                 PORTS
# abc123         spe-platform:pricing-api       Up 2 minutes          0.0.0.0:5001->5001/tcp
# def456         spe-platform:admin            Up 2 minutes          0.0.0.0:8503->8503/tcp
# ghi789         spe-platform:customer         Up 2 minutes          0.0.0.0:8504->8504/tcp
# ...
```

### View All Containers (Including Stopped)

```bash
# List all containers (running + stopped)
docker ps -a

# Get more details
docker ps -a --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

### Check Container Health Status

```bash
# View health status of all containers
docker ps --format "table {{.Names}}\t{{.Status}}"

# Example output:
# NAMES              STATUS
# pricing-api        Up 5 minutes (healthy)
# admin-dashboard    Up 5 minutes (healthy)
# customer-portal    Up 5 minutes (healthy)
# postgres-db        Up 5 minutes (healthy)
# redis-cache        Up 5 minutes
```

### View Container Logs

```bash
# View logs from specific container
docker logs pricing-api

# Follow logs in real-time
docker logs -f pricing-api

# Get last 50 lines
docker logs --tail=50 pricing-api

# View logs with timestamps
docker logs -t pricing-api

# View logs from specific time
docker logs --since 2026-05-13T10:00:00 pricing-api

# View all services logs
docker-compose logs
docker-compose logs -f
docker-compose logs pricing-api
```

### Inspect Container Details

```bash
# Get detailed information about a container
docker inspect pricing-api

# Get just the IP address
docker inspect pricing-api | grep -i ipaddress

# Get environment variables
docker inspect pricing-api -f '{{json .Config.Env}}' | jq

# Get resource usage
docker stats

# Get resource usage for specific container
docker stats pricing-api
```

### Container Status Codes

```bash
# Check exit code (0 = success, non-zero = failed)
docker inspect pricing-api --format='{{.State.ExitCode}}'

# Check if running
docker inspect pricing-api --format='{{.State.Running}}'

# Check restart count
docker inspect pricing-api --format='{{.RestartCount}}'
```

### Execute Commands in Running Container

```bash
# Open interactive shell in container
docker exec -it pricing-api /bin/bash

# Run specific command
docker exec pricing-api python -c "print('Hello')"

# Check Python version
docker exec pricing-api python --version

# List installed packages
docker exec pricing-api pip list
```

### View Docker Network

```bash
# List all networks
docker network ls

# Inspect spe-network
docker network inspect spe-network

# Test connectivity between containers
docker exec pricing-api ping admin-dashboard
docker exec admin-dashboard curl http://pricing-api:5001/health
```

### Common Docker Compose Commands

```bash
# View compose file
docker-compose config

# Validate compose file
docker-compose config --quiet

# Build specific service
docker-compose build pricing-api

# Start specific service
docker-compose up -d pricing-api

# Restart specific service
docker-compose restart pricing-api

# Stop all services (don't delete data)
docker-compose stop

# Stop specific service
docker-compose stop pricing-api

# Stop and remove containers
docker-compose down

# Stop and remove everything (volumes, networks)
docker-compose down -v

# View running containers
docker-compose ps

# View all containers
docker-compose ps -a
```

---

## 🔧 Part 3: Checking Jenkins Pipeline

### Access Jenkins UI

```bash
# Jenkins runs at
http://localhost:8080

# Get initial admin password
docker logs jenkins 2>/dev/null | grep -A 5 "Jenkins initial setup is required"

# Or if running via Ansible
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Jenkins CLI Commands

```bash
# Get Jenkins version
docker exec jenkins java -jar /usr/share/jenkins/jenkins.war --version

# Or if installed via Ansible
java -jar /usr/share/jenkins/jenkins.war --version
```

### View Pipeline Status (via Jenkins UI)

1. **Open Jenkins UI:** http://localhost:8080
2. **Login** with admin credentials
3. **Click on Pipeline Job** (if configured)
4. **View Stages:**
   - ✅ Checkout - Git repository cloned
   - ✅ Build - Docker images built
   - ✅ Unit Tests - Tests passed
   - ✅ Code Quality - Linting passed
   - ✅ Push - Images pushed to registry
   - ✅ Deploy - Deployed to Kubernetes
   - ✅ Post-Deploy Tests - Health checks passed

### Monitor Jenkins Jobs via CLI

```bash
# If Jenkins CLI installed, check job status
curl http://localhost:8080/api/json

# Get all jobs
curl http://localhost:8080/api/json | jq '.jobs'

# Get specific job details
curl http://localhost:8080/job/spe-pipeline/api/json

# Get last build status
curl http://localhost:8080/job/spe-pipeline/lastBuild/api/json
```

### View Jenkins Logs

```bash
# Docker container logs
docker logs -f jenkins

# Via Jenkins UI: Manage Jenkins → System Log → All Logs

# Jenkins log files (if running on host)
tail -f /var/log/jenkins/jenkins.log
```

### Configure Jenkins Pipeline (First Time)

```
1. Go to http://localhost:8080
2. Click "New Item"
3. Enter pipeline name: "spe-platform"
4. Select "Pipeline"
5. Click OK
6. Under "Pipeline" section:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: https://github.com/YOUR_REPO/spe-platform
   - Branch: */main
   - Script Path: Jenkinsfile
7. Click "Save"
8. Click "Build Now" to trigger first build
```

### Monitor Jenkins Build Logs

```bash
# View build console output via CLI
curl http://localhost:8080/job/spe-platform/lastBuild/consoleText

# Real-time monitoring (requires Jenkins CLI)
java -jar jenkins-cli.jar -s http://localhost:8080 \
  build -s -v spe-platform

# Check build status
curl -s http://localhost:8080/job/spe-platform/lastBuild/api/json \
  | jq '{status: .result, duration: .duration}'
```

### Jenkins Webhook Setup (GitHub Integration)

```
1. In GitHub Repository Settings:
   - Go to Settings → Webhooks
   - Click "Add webhook"
   - Payload URL: http://YOUR_SERVER:8080/github-webhook/
   - Content type: application/json
   - Events: Push events
   - Active: Yes
   - Click "Add webhook"

2. Verify by pushing to repository:
   - Go to Jenkins and check if build triggered automatically
   - Monitor build progress at http://localhost:8080/job/spe-platform/
```

### Troubleshoot Jenkins

```bash
# Check Jenkins is running
curl -I http://localhost:8080

# Get Jenkins system info
curl http://localhost:8080/systemInfo

# Check plugin updates
curl http://localhost:8080/manage/checkUpdates

# View all installed plugins
curl http://localhost:8080/api/json?tree=plugins[*] | jq
```

---

## ☸️ Part 4: Checking Kubernetes Pod Health

### Prerequisites

```bash
# Ensure kubectl is installed
kubectl version --client

# Ensure Kubernetes cluster is running
kubectl cluster-info

# If using minikube, start it
minikube start --cpus=4 --memory=8192
```

### View Pod Status

```bash
# List all pods in spe-platform namespace
kubectl get pods -n spe-platform

# Expected output:
# NAME                            READY   STATUS    RESTARTS   AGE
# pricing-api-xyz1234            2/2     Running   0          5m
# admin-dashboard-abc5678        1/1     Running   0          5m
# customer-portal-def9012        1/1     Running   0          5m

# Watch pods in real-time
kubectl get pods -n spe-platform -w

# Get more details
kubectl get pods -n spe-platform -o wide

# Output with node names and IPs
# NAME                      READY  STATUS   NODE           INTERNAL-IP
# pricing-api-xyz1234       1/1    Running  minikube       192.168.1.100
# admin-dashboard-abc5678   1/1    Running  minikube       192.168.1.100
```

### Get Detailed Pod Information

```bash
# Describe specific pod
kubectl describe pod pricing-api-xyz1234 -n spe-platform

# Shows:
# - Name, namespace, labels
# - Status, ready status
# - Container info
# - Recent events
# - Resource requests/limits
# - Volumes mounted

# Get all pod details in YAML
kubectl get pod pricing-api-xyz1234 -n spe-platform -o yaml

# Get pod details in JSON
kubectl get pod pricing-api-xyz1234 -n spe-platform -o json
```

### Check Pod Logs

```bash
# View pod logs
kubectl logs pricing-api-xyz1234 -n spe-platform

# Follow logs in real-time
kubectl logs -f pricing-api-xyz1234 -n spe-platform

# Get last 100 lines
kubectl logs --tail=100 pricing-api-xyz1234 -n spe-platform

# Get logs from specific time
kubectl logs --since=10m pricing-api-xyz1234 -n spe-platform

# Get logs from multiple pods (all pricing-api pods)
kubectl logs -l app=pricing-api -n spe-platform -f

# Get logs from all containers if pod has multiple
kubectl logs pricing-api-xyz1234 -n spe-platform --all-containers=true

# Get logs from previous container if crashed
kubectl logs pricing-api-xyz1234 -n spe-platform --previous
```

### Check Pod Health & Probes

```bash
# Check liveness and readiness probe status
kubectl describe pod pricing-api-xyz1234 -n spe-platform | grep -A 10 "Liveness"
kubectl describe pod pricing-api-xyz1234 -n spe-platform | grep -A 10 "Readiness"

# Manual health check (port-forward then curl)
kubectl port-forward pod/pricing-api-xyz1234 5001:5001 -n spe-platform &
curl http://localhost:5001/health

# Check events for probe failures
kubectl get events -n spe-platform --sort-by='.lastTimestamp'
```

### Check Pod Resource Usage

```bash
# View pod resource metrics (requires metrics-server)
kubectl top pod -n spe-platform

# Output:
# NAME                      CPU(cores)   MEMORY(bytes)
# pricing-api-xyz1234       150m         256Mi
# admin-dashboard-abc5678   100m         512Mi

# View pod resource usage over time
kubectl top pod -n spe-platform --containers

# View node resource usage
kubectl top node
```

### Execute Commands in Pod

```bash
# Open interactive shell in pod
kubectl exec -it pricing-api-xyz1234 -n spe-platform -- /bin/bash

# Run specific command
kubectl exec pricing-api-xyz1234 -n spe-platform -- curl http://localhost:5001/health

# Check environment variables
kubectl exec pricing-api-xyz1234 -n spe-platform -- env

# Install tools if needed
kubectl exec pricing-api-xyz1234 -n spe-platform -- apt-get update
kubectl exec pricing-api-xyz1234 -n spe-platform -- apt-get install -y curl
```

### Check Deployment Status

```bash
# List all deployments
kubectl get deployments -n spe-platform

# Expected output:
# NAME                READY   UP-TO-DATE   AVAILABLE   AGE
# pricing-api         2/2     2            2           5m
# admin-dashboard     1/1     1            1           5m
# customer-portal     2/2     2            2           5m

# Watch deployment rollout
kubectl rollout status deployment/pricing-api -n spe-platform

# Get deployment details
kubectl describe deployment pricing-api -n spe-platform

# View deployment history
kubectl rollout history deployment/pricing-api -n spe-platform

# View specific revision details
kubectl rollout history deployment/pricing-api -n spe-platform --revision=2
```

### Check Services

```bash
# List all services
kubectl get services -n spe-platform

# Get service details
kubectl describe svc pricing-api -n spe-platform

# Get service endpoints
kubectl get endpoints -n spe-platform

# Port-forward to service
kubectl port-forward svc/pricing-api 5001:5001 -n spe-platform

# Test service connectivity from another pod
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n spe-platform \
  -- curl http://pricing-api:5001/health
```

### Check CronJob (ML Trainer)

```bash
# List CronJobs
kubectl get cronjobs -n spe-platform

# Get CronJob details
kubectl describe cronjob ml-trainer -n spe-platform

# List jobs created by CronJob
kubectl get jobs -n spe-platform

# Get job details
kubectl describe job ml-trainer-manual-1 -n spe-platform

# View job pod logs
kubectl logs -n spe-platform job/ml-trainer-manual-1

# Trigger manual job from CronJob
kubectl create job --from=cronjob/ml-trainer ml-trainer-manual-1 -n spe-platform
```

### Check Horizontal Pod Autoscaler (HPA)

```bash
# List all HPAs
kubectl get hpa -n spe-platform

# Expected output:
# NAME                   REFERENCE              TARGETS          MINPODS  MAXPODS  REPLICAS
# pricing-api-hpa        Deployment/pricing-api  45%/70%, 256Mi/512Mi  2    5        2
# customer-portal-hpa    Deployment/customer-portal 30%/75%, 128Mi/512Mi 2  4        2

# Get HPA details
kubectl describe hpa pricing-api-hpa -n spe-platform

# Watch HPA scaling in action
kubectl get hpa -n spe-platform -w

# Get metrics for HPA
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes
```

### Check Pod Events

```bash
# Get events in namespace
kubectl get events -n spe-platform

# Get events sorted by time
kubectl get events -n spe-platform --sort-by='.lastTimestamp'

# Watch for new events
kubectl get events -n spe-platform -w

# Get events for specific pod
kubectl describe pod pricing-api-xyz1234 -n spe-platform | grep -A 20 "Events:"
```

### Check Network Policies

```bash
# List network policies
kubectl get networkpolicies -n spe-platform

# Get network policy details
kubectl describe networkpolicy spe-network-policy -n spe-platform

# Test network connectivity
kubectl exec -it pricing-api-xyz1234 -n spe-platform -- \
  curl -v admin-dashboard:8503
```

### Check RBAC

```bash
# List service accounts
kubectl get serviceaccounts -n spe-platform

# Get role bindings
kubectl get rolebindings -n spe-platform

# Describe role binding
kubectl describe rolebinding pricing-api-role-binding -n spe-platform

# Check permissions
kubectl auth can-i get configmaps \
  --as=system:serviceaccount:spe-platform:pricing-api-sa -n spe-platform
```

### Troubleshoot Pod Issues

```bash
# Pod stuck in Pending
kubectl describe pod pricing-api-xyz1234 -n spe-platform
# Check "Events" section for reason (usually: insufficient resources)

# Pod in CrashLoopBackOff
kubectl logs pricing-api-xyz1234 -n spe-platform --previous
# Check previous logs to see error

# Pod in ImagePullBackOff
kubectl describe pod pricing-api-xyz1234 -n spe-platform
# Check if image exists in registry

# Pod not ready (readiness probe failing)
kubectl exec pricing-api-xyz1234 -n spe-platform -- curl localhost:5001/health
# Check if health endpoint is responding

# Check pod events
kubectl describe pod pricing-api-xyz1234 -n spe-platform | tail -20
```

---

## 📊 Part 5: All Monitoring Commands Quick Reference

### Health Checks

```bash
# ===== API HEALTH =====
curl http://localhost:5001/health
curl http://localhost:5001/health | jq

# ===== STREAMLIT HEALTH =====
curl http://localhost:8503/_stcore/health
curl http://localhost:8504/_stcore/health

# ===== DATABASE HEALTH =====
docker exec postgres-db pg_isready -U spe_user

# ===== REDIS HEALTH =====
docker exec redis-cache redis-cli ping
# Expected: PONG
```

### Docker Monitoring

```bash
# ===== CONTAINERS =====
docker ps                                    # List running
docker ps -a                                 # List all
docker stats                                 # Resource usage
docker logs -f <container_name>             # Follow logs
docker inspect <container_name>             # Detailed info

# ===== NETWORKS =====
docker network ls
docker network inspect spe-network

# ===== VOLUMES =====
docker volume ls
docker volume inspect spe-platform_postgres_data

# ===== IMAGES =====
docker images | grep spe-platform
docker image inspect spe-platform:pricing-api
```

### Kubernetes Monitoring

```bash
# ===== PODS =====
kubectl get pods -n spe-platform              # List pods
kubectl get pods -n spe-platform -w           # Watch pods
kubectl get pods -n spe-platform -o wide      # More details
kubectl describe pod <pod_name> -n spe-platform  # Detailed info
kubectl logs -f pod/<pod_name> -n spe-platform  # Follow logs

# ===== DEPLOYMENTS =====
kubectl get deployments -n spe-platform       # List deployments
kubectl describe deployment <name> -n spe-platform  # Details
kubectl rollout status deployment/<name> -n spe-platform  # Rollout status
kubectl rollout history deployment/<name> -n spe-platform # History

# ===== SERVICES =====
kubectl get services -n spe-platform          # List services
kubectl describe svc <name> -n spe-platform   # Service details
kubectl get endpoints -n spe-platform         # Service endpoints

# ===== RESOURCE USAGE =====
kubectl top nodes                             # Node metrics
kubectl top pods -n spe-platform              # Pod metrics
kubectl top pods -n spe-platform --containers # Per-container metrics

# ===== EVENTS =====
kubectl get events -n spe-platform --sort-by='.lastTimestamp'
kubectl get events -n spe-platform -w         # Watch events

# ===== LOGS =====
kubectl logs -f deployment/pricing-api -n spe-platform     # Follow deployment logs
kubectl logs -f deployment/pricing-api -n spe-platform --all-containers  # All containers
kubectl logs -f -l app=pricing-api -n spe-platform         # All pods with label
```

### Jenkins Monitoring

```bash
# ===== STATUS =====
curl http://localhost:8080/api/json | jq '.version'  # Jenkins version
curl http://localhost:8080/api/json | jq '.jobs'      # All jobs
curl http://localhost:8080/job/spe-platform/lastBuild/api/json | jq '.result'  # Last build status

# ===== LOGS =====
docker logs -f jenkins                              # Jenkins logs
curl http://localhost:8080/job/spe-platform/lastBuild/consoleText  # Build console
```

---

## 📋 Part 6: Daily Operations Checklist

### Start of Day

```bash
# 1. Start all services
docker-compose up -d

# 2. Verify all services are running
docker-compose ps

# 3. Check health endpoints
curl http://localhost:5001/health
curl http://localhost:8503/_stcore/health
curl http://localhost:8504/_stcore/health

# 4. Check logs for errors
docker-compose logs --tail=50

# 5. Verify database connectivity
docker exec postgres-db pg_isready -U spe_user
```

### During the Day

```bash
# Monitor resource usage
watch -n 5 'docker stats --no-stream'

# Monitor logs
docker-compose logs -f

# Check specific service
docker logs -f pricing-api

# Monitor pod status (if K8s)
kubectl get pods -n spe-platform -w
```

### End of Day

```bash
# Review logs for errors
docker-compose logs | grep -i error

# Check resource usage peak
docker stats --no-stream

# Verify backups (if applicable)
ls -la data/backups/

# Review Jenkins build logs (if applicable)
curl http://localhost:8080/job/spe-platform/lastBuild/consoleText
```

---

## 🚨 Common Issues & Solutions

### Services Not Starting

```bash
# Check if ports are already in use
lsof -i :5001
lsof -i :8503
lsof -i :8504

# Kill process using port
kill -9 <PID>

# Check docker daemon
sudo systemctl start docker
sudo systemctl status docker
```

### Pod Health Checks Failing

```bash
# Check logs
kubectl logs -f pod/<pod_name> -n spe-platform

# Check if endpoint is responding
kubectl port-forward pod/<pod_name> 5001:5001 -n spe-platform &
curl http://localhost:5001/health

# Check resource limits
kubectl describe pod <pod_name> -n spe-platform | grep -A 5 "Limits"
```

### Database Connection Issues

```bash
# Test connection
docker exec postgres-db psql -U spe_user -d spe_platform -c "SELECT 1"

# Check database status
docker exec postgres-db pg_isready -v

# View database logs
docker logs postgres-db
```

### Jenkins Build Failures

```bash
# View build logs
curl http://localhost:8080/job/spe-platform/lastBuild/consoleText

# Check Jenkins logs
docker logs jenkins

# Restart Jenkins
docker restart jenkins
```

---

## 📞 Quick Command Reference Card

```bash
# ========== DOCKER COMPOSE ==========
docker-compose up -d              # Start all
docker-compose down               # Stop all
docker-compose restart            # Restart all
docker-compose ps                 # Status
docker-compose logs -f            # View logs
docker-compose build              # Build images

# ========== DOCKER CONTAINERS ==========
docker ps                         # List running
docker inspect <container>        # Details
docker logs -f <container>        # Follow logs
docker exec -it <container> bash  # Shell access
docker stats                      # Resource usage

# ========== KUBERNETES PODS ==========
kubectl get pods -n spe-platform  # List pods
kubectl describe pod <pod> -n spe-platform  # Details
kubectl logs -f pod/<pod> -n spe-platform   # Follow logs
kubectl exec -it pod/<pod> -n spe-platform -- bash  # Shell

# ========== HEALTH CHECKS ==========
curl http://localhost:5001/health        # API health
curl http://localhost:8503/_stcore/health # Admin health
curl http://localhost:8504/_stcore/health # Customer health

# ========== JENKINS ==========
docker logs -f jenkins                    # Jenkins logs
curl http://localhost:8080/api/json       # Jenkins info
http://localhost:8080                     # Jenkins UI
```

---

## 🎯 Summary: How to Monitor Everything

1. **Docker Containers:** `docker ps` + `docker logs -f`
2. **Kubernetes Pods:** `kubectl get pods -n spe-platform` + `kubectl logs -f`
3. **Jenkins Pipeline:** http://localhost:8080 + `curl` for API checks
4. **Service Health:** `curl http://localhost:PORT/health`
5. **Resource Usage:** `docker stats` or `kubectl top pods`
6. **Events & Issues:** `docker logs` or `kubectl get events`

Start with: `docker-compose up -d` then monitor with `docker ps` and `docker logs -f`

