# Quick Start Guide - DevOps Setup

## 🚀 Five-Minute Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Make script executable
chmod +x scripts/devops-setup.sh

# Run setup
./scripts/devops-setup.sh
```

### Option 2: Manual Docker Setup

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Build images
docker-compose build

# Start services
docker-compose up -d

# Verify
docker-compose ps
```

### Option 3: Kubernetes Setup

```bash
# 1. Install kubectl and minikube (if needed)
sudo apt install -y docker.io

# 2. Start Kubernetes
minikube start --cpus=4 --memory=8192

# 3. Deploy with Ansible
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml
```

---

## ✅ Verify Services Are Running

```bash
# Docker
docker ps

# Kubernetes
kubectl get pods -n spe-platform

# Health checks
curl http://localhost:5001/health           # Pricing API
curl http://localhost:8503/_stcore/health   # Admin Dashboard
curl http://localhost:8504/_stcore/health   # Customer Portal
```

---

## 📍 Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Pricing API** | http://localhost:5001 | - |
| **Admin Dashboard** | http://localhost:8503 | None (open) |
| **Customer Portal** | http://localhost:8504 | None (open) |
| **PostgreSQL** | localhost:5432 | spe_user / spe_secure_password_change_me |
| **Redis** | localhost:6379 | - |
| **Jenkins** | http://localhost:8080 | See initial password |

---

## 🆘 Troubleshooting

### Docker not running?
```bash
sudo systemctl start docker
```

### Port already in use?
```bash
# Find and kill process using port
lsof -i :5001
kill -9 <PID>
```

### Kubernetes cluster issues?
```bash
# Check cluster status
kubectl cluster-info
minikube status

# Reset cluster
minikube delete
minikube start --cpus=4 --memory=8192
```

### Need to rebuild?
```bash
docker-compose down
docker-compose up -d --build
```

---

## 📊 Microservices Summary

✅ **Pricing API Service** - Flask backend (products, pricing, orders)  
✅ **Admin Dashboard** - Streamlit admin UI  
✅ **Customer Portal** - Streamlit customer UI  
✅ **ML Trainer** - Model retraining (scheduled CronJob)  
✅ **PostgreSQL** - Database (optional, currently using CSV)  

---

See [DEVOPS_GUIDE.md](DEVOPS_GUIDE.md) for detailed documentation.
