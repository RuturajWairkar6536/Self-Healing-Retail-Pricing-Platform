# SPE Platform - Visual Monitoring & Operations Guide

## 📊 System Architecture (For Monitoring)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SPE PLATFORM (Localhost)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DOCKER LAYER (Or Kubernetes Layer)                         │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                             │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                │ │
│  │  │ Pricing API      │  │ Admin Dashboard  │ (Streamlit)    │ │
│  │  │ (Flask)          │  │ Port 8503        │                │ │
│  │  │ Port 5001        │  └──────────────────┘                │ │
│  │  ├──────────────────┤                                       │ │
│  │  │ health: ✓        │  ┌──────────────────┐                │ │
│  │  │ status: Running  │  │ Customer Portal  │ (Streamlit)    │ │
│  │  │ uptime: 2 min    │  │ Port 8504        │                │ │
│  │  └──────────────────┘  └──────────────────┘                │ │
│  │                                                             │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                │ │
│  │  │ PostgreSQL DB    │  │ Redis Cache      │                │ │
│  │  │ Port 5432        │  │ Port 6379        │                │ │
│  │  └──────────────────┘  └──────────────────┘                │ │
│  │                                                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ CI/CD LAYER                                                 │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │ Jenkins (Port 8080)                                        │ │
│  │ Pipelines: Build → Test → Deploy                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

EXTERNAL ACCESS (localhost):
- API:      http://localhost:5001
- Admin:    http://localhost:8503
- Customer: http://localhost:8504
- Jenkins:  http://localhost:8080
```

---

## 🔄 Monitoring Flow

```
┌─────────────────────────────────────────────────────────────┐
│              MONITORING & HEALTH CHECK FLOW                  │
└─────────────────────────────────────────────────────────────┘

START HERE:
     ↓
1. RUN SETUP
   ./scripts/devops-setup.sh
     ↓
2. VERIFY RUNNING
   docker-compose ps
   kubectl get pods -n spe-platform
     ↓
3. CHECK HEALTH
   ./scripts/health-check.sh
     ├─ API: curl /health
     ├─ Admin: curl /_stcore/health
     ├─ Customer: curl /_stcore/health
     └─ DB: pg_isready
     ↓
4. MONITOR IN REAL-TIME
   ├─ Option A: docker-compose logs -f
   ├─ Option B: kubectl logs -f deployment/pricing-api
   └─ Option C: ./scripts/monitor-docker.sh
     ↓
5. TROUBLESHOOT IF NEEDED
   ├─ Check logs: docker logs <container>
   ├─ Check status: docker ps
   ├─ Check resources: docker stats
   └─ Restart: docker restart <container>
     ↓
6. ACCESS DASHBOARDS
   ├─ Admin: http://localhost:8503
   ├─ Customer: http://localhost:8504
   └─ API: http://localhost:5001
```

---

## 📊 Monitoring Checkpoints & What to Look For

### Checkpoint 1: Container Status
```
COMMAND: docker ps

EXPECTED OUTPUT:
✓ All containers show "Up X minutes"
✓ All containers show "healthy" status
✓ Port mappings are correct

ISSUES TO WATCH:
✗ Container shows "Exited" or "Exit Code"
✗ Container in "Created" state
✗ Port conflicts (Address already in use)
```

### Checkpoint 2: Service Health
```
COMMAND: curl http://localhost:5001/health

EXPECTED OUTPUT:
{
  "status": "healthy",
  "model_loaded": true,
  "api_version": "1.0.0"
}

ISSUES TO WATCH:
✗ Connection refused → API not running
✗ 500 Internal Server Error → Model failed to load
✗ Timeout → API is hanging
```

### Checkpoint 3: Resource Usage
```
COMMAND: docker stats --no-stream

EXPECTED OUTPUT:
CONTAINER          CPU %    MEM USAGE / LIMIT
pricing-api        2%       256Mi / 512Mi
admin-dashboard    1%       380Mi / 1Gi
customer-portal    1.5%     350Mi / 1Gi

ISSUES TO WATCH:
✗ Memory > 90% of limit → Container may crash
✗ CPU at 100% consistently → Overloaded
✗ Abnormal jumps → Memory leak or infinite loop
```

### Checkpoint 4: Logs for Errors
```
COMMAND: docker logs pricing-api 2>&1 | grep -i "error\|exception"

EXPECTED OUTPUT:
(No errors or only INFO level logs)

ISSUES TO WATCH:
✗ NameError, TypeError, AttributeError → Code bugs
✗ ConnectionError → Database/network issues
✗ OSError: too many open files → Resource exhaustion
✗ ModuleNotFoundError → Missing dependency
```

### Checkpoint 5: Database Connectivity
```
COMMAND: docker exec postgres-db pg_isready -U spe_user

EXPECTED OUTPUT:
accepting connections

ISSUES TO WATCH:
✗ rejecting connections → DB crashed or misconfigured
✗ no attempt → DB container not running
```

### Checkpoint 6: API Endpoints
```
COMMAND: curl http://localhost:5001/products

EXPECTED OUTPUT:
{
  "products": [
    {"product_id": "1", "product_name": "Product 1", ...},
    ...
  ]
}

ISSUES TO WATCH:
✗ Empty array → No products in CSV
✗ 404 Not Found → API endpoint doesn't exist
✗ 500 Error → CSV file missing or corrupted
```

---

## 🎯 Daily Monitoring Routine

### Morning (Start of Day)

```bash
# Step 1: Start everything
docker-compose up -d

# Step 2: Wait 10 seconds for services to start
sleep 10

# Step 3: Comprehensive health check
./scripts/health-check.sh

# Expected: All checks pass with ✓
# Time: ~2 minutes
```

### During the Day (Check Every Hour)

```bash
# Quick status check
docker ps --format "table {{.Names}}\t{{.Status}}"

# If issues: Check logs
docker logs -f pricing-api

# Monitor resource usage
docker stats --no-stream

# Expected: No errors, normal resource usage
# Time: ~1 minute
```

### Evening (End of Day)

```bash
# Review any errors
docker-compose logs | grep -i error

# Check metrics
docker stats --no-stream

# Verify data files
ls -la data/

# Optional: Backup
cp -r data data.backup.$(date +%s)

# Shutdown gracefully
docker-compose down

# Expected: Clean shutdown, no unsaved data
# Time: ~1 minute
```

---

## 🚨 Emergency Response Guide

### Service is Down

```
Symptom: Connection refused on localhost:5001

Step 1: Check if container is running
$ docker ps | grep pricing-api
(If not shown → container crashed)

Step 2: Check why it crashed
$ docker logs pricing-api | tail -50
(Look for error messages)

Step 3: Restart
$ docker restart pricing-api

Step 4: Verify
$ curl http://localhost:5001/health
```

### High CPU Usage

```
Symptom: Docker stats shows CPU at 100%

Step 1: Identify which container
$ docker stats --no-stream

Step 2: Check logs for infinite loops
$ docker logs pricing-api | tail -30

Step 3: Restart or scale
$ docker restart pricing-api
OR (for K8s)
$ kubectl scale deployment/pricing-api --replicas=2

Step 4: Monitor
$ watch -n 2 'docker stats --no-stream'
```

### High Memory Usage

```
Symptom: Memory approaching limit (>90%)

Step 1: Identify container
$ docker stats --no-stream

Step 2: Check for memory leaks
$ docker logs pricing-api | grep -i memory

Step 3: Restart container
$ docker restart pricing-api

Step 4: Check if resolved
$ docker stats --no-stream

If persists: May need to increase memory limits in docker-compose.yml
```

### Database Connection Failed

```
Symptom: API returns: "could not connect to server"

Step 1: Check if DB container is running
$ docker ps | grep postgres
$ docker logs postgres-db | tail -20

Step 2: Check if port is accessible
$ docker exec postgres-db pg_isready -U spe_user

Step 3: Restart database
$ docker restart postgres-db
$ sleep 5
$ docker exec postgres-db pg_isready -U spe_user

Step 4: Restart API
$ docker restart pricing-api

Step 5: Test connection
$ curl http://localhost:5001/health
```

### Network Issue

```
Symptom: Services can't talk to each other

Step 1: Check network
$ docker network ls | grep spe
$ docker network inspect spe-network

Step 2: Check container connectivity
$ docker exec admin-dashboard curl http://pricing-api:5001/health

Step 3: Restart all services
$ docker-compose restart

Step 4: Test again
$ docker exec admin-dashboard curl http://pricing-api:5001/health
```

---

## 📈 Performance Monitoring Template

Use this to track performance over time:

```
┌─────────────┬──────────────┬──────────────┬──────────────┐
│ Metric      │ Morning      │ Afternoon    │ Evening      │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Uptime      │ 100%         │ 100%         │ 100%         │
│ CPU Avg     │ 3%           │ 12%          │ 5%           │
│ Memory Avg  │ 256Mi        │ 380Mi        │ 290Mi        │
│ Requests/s  │ 10           │ 45           │ 8            │
│ Error Rate  │ 0%           │ 0%           │ 0%           │
└─────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 📱 Dashboard Shortcuts

### Quick Access Bookmarks
```
Pricing API:      http://localhost:5001/health
Admin Dashboard:  http://localhost:8503
Customer Portal:  http://localhost:8504
Jenkins CI/CD:    http://localhost:8080
```

### Monitoring URLs (API)
```
Health Check:     http://localhost:5001/health
Products List:    http://localhost:5001/products
Analytics:        http://localhost:5001/analytics
```

---

## 🔧 One-Liner Commands for Quick Checks

```bash
# Is everything running?
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -c "Up"

# Top resource consumer?
docker stats --no-stream | sort -k3 -h | tail -1

# Any errors in logs?
docker-compose logs 2>&1 | grep -i "error" | wc -l

# API responding?
curl -s http://localhost:5001/health | jq '.status'

# How many products?
curl -s http://localhost:5001/products | jq '.products | length'

# Database connected?
docker exec postgres-db pg_isready -U spe_user

# All ports accessible?
for port in 5001 8503 8504 5432 6379; do curl -s http://localhost:$port 2>&1 | head -1; done
```

---

## 📊 Multi-Service Monitoring Dashboard

Create this monitoring display in a terminal:

```bash
# Create a monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
while true; do
  clear
  echo "═══════════════════════════════════════════════════════"
  echo "        SPE PLATFORM - LIVE MONITORING"
  echo "═══════════════════════════════════════════════════════"
  echo ""
  
  echo "CONTAINER STATUS:"
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -6
  
  echo ""
  echo "RESOURCE USAGE:"
  docker stats --no-stream | head -5
  
  echo ""
  echo "RECENT ERRORS:"
  docker-compose logs 2>&1 | grep -i error | tail -2 || echo "None"
  
  echo ""
  echo "SERVICE HEALTH:"
  curl -s http://localhost:5001/health | jq '.status' 2>/dev/null || echo "API: Unknown"
  
  echo ""
  echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Press Ctrl+C to exit"
  echo "═══════════════════════════════════════════════════════"
  
  sleep 10
done
EOF

chmod +x monitor.sh
./monitor.sh
```

---

## 🎓 Learning Path

1. **Start here:** QUICKSTART.md
2. **Understand architecture:** MICROSERVICES.md
3. **Run services:** RUNNING_AND_MONITORING.md (this file)
4. **Quick commands:** QUICK_COMMANDS.md
5. **Deep dive:** DEVOPS_GUIDE.md

---

## ✅ Pre-Go-Live Checklist

- [ ] All services start without errors
- [ ] Health checks pass on all endpoints
- [ ] CPU usage < 30% under normal load
- [ ] Memory usage stable (no growth over time)
- [ ] Database connectivity confirmed
- [ ] API returns valid responses
- [ ] Admin dashboard loads
- [ ] Customer portal loads and can browse
- [ ] No critical errors in logs
- [ ] Backups configured
- [ ] Monitoring scripts tested
- [ ] Documentation reviewed
- [ ] Team trained on monitoring

---

**Remember:** Start simple with `docker ps` and `docker logs`, then graduate to more advanced monitoring as needed.

Good luck! 🚀
