# DevOps Files Created for SPE Platform

This document provides a summary of all DevOps files created for the SPE Platform DevOps setup.

## 📁 Directory Structure

```
spe-platform/
├── 🐳 Docker Files
│   ├── Dockerfile                    # Pricing API container
│   ├── Dockerfile.admin             # Admin Dashboard container
│   ├── Dockerfile.customer          # Customer Portal container
│   ├── Dockerfile.trainer           # ML Trainer container
│   ├── docker-compose.yml           # Local development orchestration
│   └── .dockerignore                # Docker build exclusions
│
├── 🚀 CI/CD Pipeline
│   └── Jenkinsfile                  # Jenkins pipeline (build, test, deploy)
│
├── ☸️ Kubernetes Manifests (k8s/)
│   ├── namespace.yaml               # spe-platform namespace
│   ├── configmaps/
│   │   └── app-config.yaml         # ConfigMaps for all services
│   ├── secrets/
│   │   └── app-secrets.yaml        # Secrets (DB, API keys)
│   ├── deployments/
│   │   ├── app-deployments.yaml    # Pricing API, Admin, Customer deployments
│   │   └── ml-trainer-cronjob.yaml # ML retraining CronJob
│   ├── services/
│   │   └── app-services.yaml       # ClusterIP & LoadBalancer services
│   ├── policies/
│   │   └── network-policy.yaml     # Network policies & HPA & PDB
│   ├── ingress/
│   │   └── ingress.yaml            # Ingress with TLS
│   └── rbac/
│       └── rbac.yaml               # Service accounts & roles
│
├── 🔧 Infrastructure as Code (ansible/)
│   ├── site.yml                    # Main playbook (Docker, K8s, Jenkins)
│   ├── deploy-k8s.yml              # Kubernetes deployment playbook
│   ├── hosts.ini                   # Ansible inventory
│   └── ansible.cfg                 # Ansible configuration
│
├── 📜 Automation Scripts (scripts/)
│   └── devops-setup.sh             # One-click DevOps setup script
│
├── 📊 Streamlit Configuration (streamlit/)
│   └── config.toml                 # Streamlit UI settings
│
└── 📚 Documentation
    ├── DEVOPS_GUIDE.md             # Complete DevOps documentation
    ├── QUICKSTART.md               # 5-minute quick start guide
    ├── MICROSERVICES.md            # Microservices architecture document
    └── DEVOPS_FILES_SUMMARY.md     # This file
```

## 🐳 Docker Files Explained

### `Dockerfile` (Pricing API Service)
**Purpose:** Container image for Flask-based pricing API  
**Base Image:** python:3.11-slim  
**Multi-stage Build:** Yes (reduced final image size)  
**Ports:** 5001  
**Features:**
- Health check endpoint
- Non-root user execution
- Minimal attack surface
- Model and data volume mounts

**Build Command:**
```bash
docker build -t spe-platform:pricing-api .
```

### `Dockerfile.admin` (Admin Dashboard)
**Purpose:** Container image for Streamlit admin interface  
**Base Image:** python:3.11-slim  
**Ports:** 8503  
**Features:**
- Streamlit-specific health checks
- ConfigMap-based configuration
- Volume mounts for data persistence

**Build Command:**
```bash
docker build -f Dockerfile.admin -t spe-platform:admin .
```

### `Dockerfile.customer` (Customer Portal)
**Purpose:** Container image for Streamlit customer interface  
**Base Image:** python:3.11-slim  
**Ports:** 8504  
**Features:**
- Identical to admin container (reusable pattern)
- Separate configuration
- Independent scaling

**Build Command:**
```bash
docker build -f Dockerfile.customer -t spe-platform:customer .
```

### `Dockerfile.trainer` (ML Trainer)
**Purpose:** Container image for model retraining pipeline  
**Base Image:** python:3.11-slim  
**Features:**
- No exposed ports (background job)
- All ML dependencies included
- Volume mounts for model storage

**Build Command:**
```bash
docker build -f Dockerfile.trainer -t spe-platform:trainer .
```

### `docker-compose.yml`
**Purpose:** Local development environment orchestration  
**Services Defined:** 6 (pricing-api, admin, customer, postgres, redis, optional)  
**Features:**
- Service dependencies (depends_on)
- Health checks for all services
- Named volumes for data persistence
- Internal network (spe-network)
- Environment variable management
- Auto-restart policies

**Usage:**
```bash
docker-compose build       # Build all images
docker-compose up -d       # Start in background
docker-compose logs -f     # View logs
docker-compose down        # Stop and remove
```

---

## 🚀 Jenkins CI/CD Pipeline

### `Jenkinsfile`
**Purpose:** Automated build, test, and deployment pipeline  
**Pipeline Type:** Declarative  
**Trigger:** GitHub webhook (on push)  
**Stages:** 7

**Stages Breakdown:**

| Stage | Purpose | Actions |
|-------|---------|---------|
| **Checkout** | Clone repository | Git clone + commit info |
| **Build** | Create container images | 4 parallel Docker builds |
| **Unit Tests** | Run tests | pytest suite |
| **Code Quality** | Lint & analyze | flake8, pylint |
| **Push** | Upload to registry | Docker Hub push |
| **Deploy** | K8s deployment | kubectl apply (main branch) |
| **Post-Deploy Tests** | Verify deployment | Health checks |

**Features:**
- Parallel builds for faster pipeline
- Conditional deployments (main branch only)
- Build history preservation
- Docker registry integration
- Kubernetes rollout status checking

**Sample Config:**
```groovy
pipeline {
    agent any
    stages {
        stage('Build Docker Images') {
            parallel { ... }
        }
    }
}
```

---

## ☸️ Kubernetes Manifests

### Namespace
**File:** `k8s/namespace.yaml`  
**Purpose:** Isolate SPE Platform resources  
**Name:** spe-platform  
**Labels:** For monitoring and selection

### ConfigMaps (Configuration)
**File:** `k8s/configmaps/app-config.yaml`  
**ConfigMaps Created:**
1. **pricing-api-config** - Flask environment variables
2. **streamlit-config** - Streamlit UI settings
3. **ml-trainer-config** - Trainer environment variables

**Usage:** Referenced in pod env vars

### Secrets (Credentials)
**File:** `k8s/secrets/app-secrets.yaml`  
**Secrets Created:**
1. **pricing-api-secrets** - Database URL, Redis URL, Secret key
2. **docker-registry-secret** - Docker Hub credentials

**⚠️ Important:** Update before deploying to production

### Deployments
**File:** `k8s/deployments/app-deployments.yaml`  
**Deployments:**

1. **pricing-api**
   - Replicas: 2 (scales to 5 with HPA)
   - Strategy: Rolling update
   - Resources: 256Mi → 512Mi RAM, 250m → 500m CPU
   - Probe: Liveness & Readiness
   - Anti-affinity: Spread across nodes

2. **admin-dashboard**
   - Replicas: 1 (not scalable)
   - Resources: 512Mi → 1Gi RAM
   - Probe: Streamlit-specific

3. **customer-portal**
   - Replicas: 2 (scales to 4 with HPA)
   - Resources: 512Mi → 1Gi RAM
   - Anti-affinity: Spread across nodes

### CronJob (ML Trainer)
**File:** `k8s/deployments/ml-trainer-cronjob.yaml`  
**Schedule:** 0 2 * * * (Daily at 2 AM)  
**Resources:** 1 CPU, 1-2Gi RAM  
**Restart:** OnFailure  
**History:** Keep last 3 successes, 1 failure

### Services
**File:** `k8s/services/app-services.yaml`  
**Services Created:**

1. **ClusterIP Services** (Internal)
   - pricing-api:5001
   - admin-dashboard:8503
   - customer-portal:8504

2. **LoadBalancer Services** (External)
   - pricing-api-external
   - admin-dashboard-external
   - customer-portal-external

### Network Policies
**File:** `k8s/policies/network-policy.yaml`  
**Policies:**
- Namespace isolation (only spe-platform pods can communicate)
- Ingress/Egress rules
- Allow DNS (port 53)

**Autoscaling (HPA):**
- **pricing-api:** 2-5 replicas (CPU 70%, Memory 80%)
- **customer-portal:** 2-4 replicas (CPU 75%, Memory 85%)

**Pod Disruption Budget:**
- Minimum 1 pod available during disruptions
- Prevents total service outage

### Ingress
**File:** `k8s/ingress/ingress.yaml`  
**Controller:** NGINX  
**Hosts:**
- api.spe-platform.local → Pricing API
- admin.spe-platform.local → Admin Dashboard
- shop.spe-platform.local → Customer Portal

**TLS:** Enabled (requires certificate)  
**Rate Limiting:** 10 requests per IP

### RBAC (Role-Based Access Control)
**File:** `k8s/rbac/rbac.yaml`  
**Resources:**
- 4 ServiceAccounts (one per service)
- 1 Role (read-only for ConfigMaps, Secrets, Pods)
- 4 RoleBindings

**Principle:** Least privilege access

---

## 🔧 Ansible Configuration

### `site.yml` (Main Playbook)
**Purpose:** Set up infrastructure on target servers  
**What It Does:**
1. Updates system packages
2. Installs Docker & Docker Compose
3. Installs Kubernetes tools (kubectl)
4. Installs Jenkins
5. Configures firewall
6. Creates systemd services
7. Sets up monitoring (Prometheus)

**Run:**
```bash
ansible-playbook -i ansible/hosts.ini ansible/site.yml
```

**Key Tasks:**
- Docker GPG key setup
- Repository management
- Service enablement (systemd)
- User creation (spe-admin)
- Port configuration

### `deploy-k8s.yml` (K8s Deployment)
**Purpose:** Deploy SPE Platform to Kubernetes  
**Requires:** Ansible kubernetes.core module  
**What It Does:**
1. Creates namespace
2. Creates ConfigMaps & Secrets
3. Deploys applications
4. Creates services
5. Waits for rollout
6. Displays status

**Run:**
```bash
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml
```

### `hosts.ini` (Ansible Inventory)
**Format:** INI  
**Groups:** all, k8s_masters, docker_hosts, jenkins_masters  
**Default:** localhost with local connection

**Customization:**
```ini
[all]
prod-server1 ansible_host=10.0.1.10
prod-server2 ansible_host=10.0.1.11
```

### `ansible.cfg` (Ansible Configuration)
**Settings:**
- Inventory file location
- Host key checking (disabled for containers)
- Deprecation warnings
- Fork count (parallel execution)
- Timeout (30 seconds)

---

## 📜 Automation Scripts

### `scripts/devops-setup.sh`
**Purpose:** One-command setup for entire DevOps stack  
**Language:** Bash  
**What It Does:**
1. Checks prerequisites (Docker, Ansible)
2. Runs Ansible infrastructure playbook
3. Builds Docker images (parallel)
4. Starts services with docker-compose
5. Waits for health checks
6. Displays endpoints and next steps

**Usage:**
```bash
chmod +x scripts/devops-setup.sh
./scripts/devops-setup.sh
```

**Output:** Colored terminal output with endpoints

---

## 📊 Streamlit Configuration

### `streamlit/config.toml`
**Purpose:** Streamlit UI customization  
**Settings:**
- Client: Hide error details, minimal toolbar
- Logger: Info level
- Server: Headless, XSRF protection
- Theme: Custom colors and fonts

---

## 📚 Documentation Files

### `DEVOPS_GUIDE.md` (Complete Documentation)
**Length:** ~500 lines  
**Sections:**
- Architecture overview
- Docker setup
- Jenkins pipeline
- Kubernetes deployment
- Ansible configuration
- Monitoring
- Security
- Troubleshooting
- Deployment checklist

### `QUICKSTART.md` (5-Minute Start)
**Length:** ~100 lines  
**Sections:**
- Automated setup
- Manual setup
- Service verification
- Access URLs
- Quick troubleshooting

### `MICROSERVICES.md` (Architecture Document)
**Length:** ~400 lines  
**Sections:**
- Microservices inventory (4-5 services)
- Service responsibilities
- Resource requirements
- Communication patterns
- Scalability analysis
- Data flow diagrams
- Deployment strategies
- Future enhancements

### `DEVOPS_FILES_SUMMARY.md` (This File)
**Purpose:** Quick reference for all created files

---

## 🔒 Security Implemented

✅ **Pod Security**
- Non-root containers (UID 1000)
- Read-only root filesystems
- Dropped Linux capabilities
- Resource limits (prevent resource hogging)

✅ **Network Security**
- Network policies (namespace isolation)
- Service-to-service communication rules
- Ingress TLS/SSL

✅ **RBAC**
- Service accounts per service
- Role-based access control
- Minimal permissions (least privilege)

✅ **Secrets Management**
- Kubernetes Secrets (encrypted)
- Environment variables for credentials
- Secret file restrictions

---

## 🎯 Deployment Workflow

```
Developer                 CI/CD (Jenkins)              Kubernetes
   │                            │                           │
   ├─→ Push code to Git ─→     │                           │
   │                            │                           │
   │                      ├─ Checkout code                 │
   │                      │                                │
   │                      ├─ Build Docker images ──→      │
   │                      │                                │
   │                      ├─ Run tests                     │
   │                      │                                │
   │                      ├─ Push to registry ──→  Docker Hub
   │                      │                                │
   │                      ├─ Deploy to K8s ─────→   kubectl apply
   │                      │                                │
   │                      ├─ Run health checks ────→  ✓ Ready
   │                      │                                │
   │                      └─ Send notification ─→     Slack/Email
   │
   └─ Monitor services at http://dashboard.local
```

---

## 📋 Quick Reference

### Common Commands

**Docker:**
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

**Kubernetes:**
```bash
kubectl get pods -n spe-platform
kubectl logs -n spe-platform deployment/pricing-api -f
kubectl scale deployment/pricing-api --replicas=3 -n spe-platform
```

**Ansible:**
```bash
ansible-playbook -i ansible/hosts.ini ansible/site.yml
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml --check
```

**Jenkins:**
```bash
Open http://localhost:8080
Configure pipeline from GitHub
Trigger build manually or via webhook
```

---

## 🚀 Next Steps After Setup

1. **Configure Credentials**
   - Update Docker Hub credentials in Jenkinsfile
   - Configure Kubernetes kubeconfig
   - Set environment variables

2. **Connect to GitHub/GitLab**
   - Create Jenkins webhook
   - Enable auto-build on push
   - Configure branch protection

3. **Set Up Monitoring**
   - Install Prometheus
   - Configure Grafana dashboards
   - Create alert rules

4. **Production Deployment**
   - Use managed Kubernetes (EKS, AKS, GKE)
   - Configure persistent volumes
   - Enable SSL/TLS certificates
   - Set up backup strategy

---

## 📞 Support & Resources

**Documentation:**
- [Docker Docs](https://docs.docker.com/)
- [Kubernetes Docs](https://kubernetes.io/docs/)
- [Ansible Docs](https://docs.ansible.com/)
- [Jenkins Docs](https://www.jenkins.io/doc/)

**Local Help:**
```bash
# View all DevOps files
ls -la Dockerfile* docker-compose.yml Jenkinsfile
ls -la k8s/ ansible/ scripts/

# Read documentation
cat DEVOPS_GUIDE.md
cat QUICKSTART.md
cat MICROSERVICES.md
```

---

## 📊 Files Summary

| File Type | Count | Total Lines |
|-----------|-------|------------|
| Dockerfiles | 4 | ~180 |
| Kubernetes YAML | 10 | ~1200 |
| Ansible Playbooks | 2 | ~350 |
| Shell Scripts | 1 | ~150 |
| Configuration | 2 | ~50 |
| Documentation | 4 | ~1500 |
| **Total** | **23** | **~3430** |

---

**Created:** May 13, 2026  
**Version:** 1.0.0  
**Project:** SPE Platform DevOps Setup
