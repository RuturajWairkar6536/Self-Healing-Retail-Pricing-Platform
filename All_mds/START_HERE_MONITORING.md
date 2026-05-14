# SPE Platform - Running & Monitoring Complete Setup ✅

## 📋 What's Been Created

I've created a **comprehensive guide system** for running and monitoring your DevOpsified project locally. Here's everything:

### 📚 Documentation Files (5 New)

| File | Purpose | Read Time |
|------|---------|-----------|
| **RUNNING_AND_MONITORING.md** ⭐ | Complete 800-line guide for all operations | 20 min |
| **QUICK_COMMANDS.md** | Quick reference cheat sheet | 5 min |
| **MONITORING_VISUAL_GUIDE.md** | Visual diagrams and monitoring flows | 10 min |
| **scripts/health-check.sh** | Automated health check script | - |
| **scripts/monitor-docker.sh** | Docker monitoring dashboard | - |
| **scripts/monitor-k8s.sh** | Kubernetes monitoring dashboard | - |

---

## 🚀 QUICKEST START (30 Seconds)

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Option 1: One-command setup (automatic everything)
chmod +x scripts/devops-setup.sh
./scripts/devops-setup.sh

# Option 2: Manual Docker Compose
docker-compose up -d

# Then monitor
./scripts/health-check.sh
```

**Result:** All services running in 2-3 minutes at:
- API: http://localhost:5001
- Admin: http://localhost:8503
- Customer: http://localhost:8504

---

## 🎯 How to Run on Localhost

### Method 1: Automated Setup ⭐⭐⭐ (Recommended)

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP
chmod +x scripts/devops-setup.sh
./scripts/devops-setup.sh
```

**What happens:**
1. ✅ Installs Docker, Docker Compose, kubectl, Ansible, Jenkins
2. ✅ Builds all 4 Docker images
3. ✅ Starts all 6 services (API, Admin, Customer, PostgreSQL, Redis, Jenkins)
4. ✅ Runs health checks
5. ✅ Displays all endpoints

**Time:** 3-5 minutes

### Method 2: Manual Docker Compose

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Build
docker-compose build

# Start
docker-compose up -d

# Verify
docker-compose ps

# Check health
curl http://localhost:5001/health
```

**Time:** 2-3 minutes

### Method 3: Manual Kubernetes

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Start cluster
minikube start --cpus=4 --memory=8192

# Deploy
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml

# Verify
kubectl get pods -n spe-platform

# Access (port-forward)
kubectl port-forward svc/pricing-api 5001:5001 -n spe-platform &
```

**Time:** 5-10 minutes (cluster startup slower)

---

## ✅ How to Check Everything

### Quick Health Check (30 seconds)
```bash
chmod +x scripts/health-check.sh
./scripts/health-check.sh
```

**Output shows:**
- ✓ All services running (green checkmarks)
- ✓ Health endpoints responding
- ✓ Database connected
- ✓ Quick links to dashboards

### Docker Container Status

```bash
# All containers
docker ps

# Status with details
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Resource usage
docker stats

# Logs
docker logs -f pricing-api
docker-compose logs -f

# Full monitoring dashboard
./scripts/monitor-docker.sh
```

### Kubernetes Pod Health

```bash
# All pods
kubectl get pods -n spe-platform

# Pod details
kubectl describe pod pricing-api-xyz -n spe-platform

# Real-time logs
kubectl logs -f deployment/pricing-api -n spe-platform

# Full monitoring dashboard
./scripts/monitor-k8s.sh
```

### Jenkins Pipeline Status

```
1. Open: http://localhost:8080
2. Click on pipeline job: "spe-platform"
3. View stages: Checkout → Build → Test → Deploy
4. Check console output for any errors

# Via CLI
docker logs -f jenkins
curl http://localhost:8080/api/json | jq '.version'
```

---

## 📊 Monitoring Commands Quick Reference

### Docker (Most Common for Localhost)

```bash
# ===== STATUS =====
docker ps                                # All running containers
docker-compose ps                        # Compose services status
docker stats                             # Resource usage

# ===== LOGS =====
docker logs pricing-api                  # Container logs
docker logs -f pricing-api               # Follow logs
docker-compose logs -f                   # All services logs

# ===== HEALTH =====
curl http://localhost:5001/health        # Pricing API
curl http://localhost:8503/_stcore/health  # Admin
curl http://localhost:8504/_stcore/health  # Customer

# ===== DETAILS =====
docker inspect pricing-api               # Full container info
docker exec pricing-api curl localhost:5001/health  # Run command

# ===== RESTART =====
docker restart pricing-api               # Restart service
docker-compose restart                   # Restart all
docker-compose down && docker-compose up -d  # Fresh start
```

### Kubernetes

```bash
# ===== PODS =====
kubectl get pods -n spe-platform         # List pods
kubectl get pods -n spe-platform -w      # Watch pods
kubectl describe pod <name> -n spe-platform  # Pod details

# ===== LOGS =====
kubectl logs -f pod/<name> -n spe-platform   # Follow logs
kubectl logs -f deployment/pricing-api -n spe-platform  # All pod logs

# ===== RESOURCES =====
kubectl top pods -n spe-platform         # Resource usage
kubectl top nodes                        # Node usage

# ===== RESTART =====
kubectl rollout restart deployment/pricing-api -n spe-platform
```

---

## 🔍 What Each Monitoring Script Does

### 1. health-check.sh (Most Important ⭐)
```bash
./scripts/health-check.sh
```
**Checks:**
- ✅ All containers/pods running
- ✅ API responding to requests
- ✅ Health endpoints accessible
- ✅ Database connectivity
- ✅ Redis cache working

**Use when:** First thing in the morning, troubleshooting

### 2. monitor-docker.sh
```bash
./scripts/monitor-docker.sh
```
**Shows:**
- Container status (running/stopped)
- Resource usage (CPU, memory)
- Docker images
- Docker volumes & networks
- Recent errors in logs
- Service endpoints

**Use when:** Need overview of Docker environment

### 3. monitor-k8s.sh
```bash
./scripts/monitor-k8s.sh
```
**Shows:**
- Pod status & health
- Deployment status
- Services & endpoints
- CronJobs & scheduled jobs
- HPA autoscaling status
- Resource metrics
- Recent events

**Use when:** Running on Kubernetes

---

## 📍 Service Endpoints

```
API Server      http://localhost:5001/health
Admin Dashboard http://localhost:8503
Customer Portal http://localhost:8504
Jenkins CI/CD   http://localhost:8080

Database        localhost:5432 (spe_user / spe_secure_password_change_me)
Redis Cache     localhost:6379
```

---

## 🆘 Troubleshooting Quick Guide

### "Connection refused" on localhost:5001

```bash
# Step 1: Check if container is running
docker ps | grep pricing-api

# Step 2: If not shown, check logs
docker logs pricing-api | tail -30

# Step 3: Restart
docker restart pricing-api

# Step 4: Verify
curl http://localhost:5001/health
```

### "Port already in use"

```bash
# Find what's using port 5001
lsof -i :5001

# Kill it
kill -9 <PID>

# Restart service
docker restart pricing-api
```

### Service not responding / High CPU / High Memory

```bash
# Check logs for errors
docker logs pricing-api 2>&1 | tail -50

# Check resource usage
docker stats --no-stream

# Restart service
docker restart pricing-api

# Monitor for recovery
watch -n 5 'docker stats --no-stream | head -5'
```

### Database connection failed

```bash
# Test DB connectivity
docker exec postgres-db pg_isready -U spe_user

# If failed, restart DB
docker restart postgres-db
sleep 5
docker exec postgres-db pg_isready -U spe_user

# Then restart API
docker restart pricing-api
```

---

## 📋 Daily Operations Checklist

### Morning (5 minutes)

- [ ] Start services: `docker-compose up -d` or `./scripts/devops-setup.sh`
- [ ] Wait 10 seconds
- [ ] Run health check: `./scripts/health-check.sh`
- [ ] Verify all ✓ (green checkmarks)
- [ ] Access dashboards if needed

### During Day (Every hour)

- [ ] Quick status: `docker ps`
- [ ] Check for errors: `docker-compose logs | grep -i error`
- [ ] Monitor resources: `docker stats --no-stream | head -5`
- [ ] No action needed if all looks good

### Evening (3 minutes)

- [ ] Review errors: `docker-compose logs 2>&1 | grep -i error`
- [ ] Backup data: `cp -r data data.backup.$(date +%s)`
- [ ] Shutdown: `docker-compose down`
- [ ] Verify clean shutdown: `docker ps` (should be empty)

---

## 🎯 Test API Endpoints

```bash
# Get all products
curl http://localhost:5001/products | jq '.'

# Get analytics
curl http://localhost:5001/analytics | jq '.'

# Health check
curl http://localhost:5001/health | jq '.'

# Test admin dashboard loads
curl http://localhost:8503 -s | grep "AI-Powered" > /dev/null && echo "Admin OK" || echo "Admin DOWN"

# Test customer portal loads
curl http://localhost:8504 -s | grep "Smart" > /dev/null && echo "Customer OK" || echo "Customer DOWN"
```

---

## 📊 Example Monitoring Session

```bash
# Start session
cd /home/ruturajwairkar/Desktop/SPE_MP

# Terminal 1: Start services
./scripts/devops-setup.sh
(Wait for "Setup complete!")

# Terminal 2: Monitor in real-time
docker-compose logs -f

# Terminal 3: Resource usage
watch -n 5 'docker stats --no-stream'

# Terminal 4: Health checks
./scripts/health-check.sh
(Should show all ✓)

# Terminal 5: Access dashboards
# Open in browser:
# http://localhost:8503 (Admin)
# http://localhost:8504 (Customer)

# Keep Terminal 2 & 3 running for real-time monitoring
```

---

## 🎓 Documentation Map

```
START HERE
    ↓
QUICKSTART.md (5 min)
    ↓
RUNNING_AND_MONITORING.md (20 min) ← YOU ARE HERE
    ↓
QUICK_COMMANDS.md (reference)
    ↓
MONITORING_VISUAL_GUIDE.md (visual flows)
    ↓
DEVOPS_GUIDE.md (deep dive 50 min)
    ↓
MICROSERVICES.md (architecture details)
```

---

## ✨ What You Can Do Now

After setup and following this guide:

1. ✅ **Start project**: One command startup
2. ✅ **Monitor everything**: Real-time logs, metrics, health
3. ✅ **Troubleshoot quickly**: Follow troubleshooting guides
4. ✅ **Check service health**: All endpoints working
5. ✅ **Access dashboards**: Admin and customer UIs
6. ✅ **Scale services**: Add more replicas if needed (K8s)
7. ✅ **View performance**: Docker stats or kubectl metrics
8. ✅ **Debug issues**: Logs, events, container inspection

---

## 🚀 Next Steps

1. **Try it now:**
   ```bash
   cd /home/ruturajwairkar/Desktop/SPE_MP
   ./scripts/devops-setup.sh
   ```

2. **Once running:**
   ```bash
   ./scripts/health-check.sh
   ```

3. **Access services:**
   - Admin: http://localhost:8503
   - Customer: http://localhost:8504
   - API: http://localhost:5001

4. **For detailed info:**
   - See: RUNNING_AND_MONITORING.md (Full guide)
   - See: QUICK_COMMANDS.md (Command reference)
   - See: MONITORING_VISUAL_GUIDE.md (Visual flows)

---

## 📞 Need Help?

All documentation is in the project root:
- **Quick answers:** QUICK_COMMANDS.md
- **Setup issues:** QUICKSTART.md
- **Monitoring details:** RUNNING_AND_MONITORING.md
- **Visual guide:** MONITORING_VISUAL_GUIDE.md
- **Everything:** DEVOPS_GUIDE.md

---

**You're all set! Start with:** `./scripts/devops-setup.sh` 🚀

Your DevOpsified project is ready to run and monitor on localhost! 🎉
