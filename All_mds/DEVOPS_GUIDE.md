# SPE Platform DevOps Guide

## 🏗️ Architecture Overview

### Microservices (4-5 Services)

```
┌─────────────────────────────────────────────────────────┐
│         SPE Platform - Microservices Architecture       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐│
│  │ Pricing API  │  │ Admin        │  │ Customer       ││
│  │ (Flask)      │  │ Dashboard    │  │ Portal         ││
│  │ Port: 5001   │  │ (Streamlit)  │  │ (Streamlit)    ││
│  │ Service #1   │  │ Port: 8503   │  │ Port: 8504     ││
│  │              │  │ Service #2   │  │ Service #3     ││
│  └──────────────┘  └──────────────┘  └────────────────┘│
│         │                  │                   │        │
│         └──────────────────┼───────────────────┘        │
│                            │                            │
│                    ┌───────▼────────┐                   │
│                    │ ML Trainer     │                   │
│                    │ (CronJob)      │                   │
│                    │ Service #4     │                   │
│                    └────────────────┘                   │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐│
│  │ PostgreSQL   │  │ Redis        │  │ Shared Storage ││
│  │ Port: 5432   │  │ Port: 6379   │  │ (Volumes)      ││
│  │ Service #5   │  │ (Optional)   │  │                ││
│  └──────────────┘  └──────────────┘  └────────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Services Breakdown

| Service | Purpose | Technology | Port | Replicas | 
|---------|---------|-----------|------|----------|
| **Pricing API** | ML inference, product CRUD, orders | Flask + Python | 5001 | 2+ |
| **Admin Dashboard** | Analytics, price optimization, config | Streamlit | 8503 | 1 |
| **Customer Portal** | Shopping, checkout, product browsing | Streamlit | 8504 | 2+ |
| **ML Trainer** | Model retraining (scheduled) | Python/Scikit-learn | - | Cron |
| **PostgreSQL** | Persistent data (future) | PostgreSQL | 5432 | 1 |

---

## 🐳 Docker Setup

### Quick Start

```bash
# Build all images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f pricing-api

# Stop all services
docker-compose down
```

### Individual Docker Builds

```bash
# Pricing API
docker build -t spe-platform:pricing-api .

# Admin Dashboard
docker build -f Dockerfile.admin -t spe-platform:admin .

# Customer Portal
docker build -f Dockerfile.customer -t spe-platform:customer .

# ML Trainer
docker build -f Dockerfile.trainer -t spe-platform:trainer .
```

### Docker Images

```bash
# View images
docker images | grep spe-platform

# Run a specific service
docker run -d -p 5001:5001 spe-platform:pricing-api

# Interactive shell
docker run -it spe-platform:pricing-api /bin/bash
```

---

## 🚀 Jenkins CI/CD Pipeline

### Pipeline Stages

1. **Checkout** - Clone repository
2. **Build** - Build Docker images for all services (parallel)
3. **Unit Tests** - Run test suite
4. **Code Quality** - Lint and static analysis
5. **Push** - Push images to Docker registry
6. **Deploy** - Deploy to Kubernetes (main branch only)
7. **Post-Deploy Tests** - Health checks

### Setup Jenkins

```bash
# Access Jenkins
http://localhost:8080

# Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Create pipeline job:
1. New Item → Pipeline
2. Pipeline script from SCM → Git
3. Repository URL: https://github.com/YOUR_REPO/spe-platform
4. Script path: Jenkinsfile
```

### Required Jenkins Credentials

```groovy
// Add these credentials in Jenkins:
1. docker-hub-credentials (username/password)
2. kubeconfig (file)
3. github-ssh-key (SSH private key)
```

---

## ☸️ Kubernetes Deployment

### Prerequisites

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install minikube (for local testing)
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube
sudo mv minikube /usr/local/bin/

# Start Kubernetes
minikube start --cpus=4 --memory=8192
```

### Deploy to Kubernetes

```bash
# Using Ansible
cd ansible
ansible-playbook -i hosts.ini deploy-k8s.yml

# Or manually apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/rbac/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/policies/
kubectl apply -f k8s/ingress/
```

### K8s Operations

```bash
# View resources
kubectl get pods -n spe-platform
kubectl get deployments -n spe-platform
kubectl get services -n spe-platform

# Logs
kubectl logs -n spe-platform deployment/pricing-api -f
kubectl logs -n spe-platform pod/admin-dashboard-xyz

# Port forwarding
kubectl port-forward -n spe-platform svc/pricing-api 5001:5001

# Describe resource
kubectl describe deployment pricing-api -n spe-platform

# Scale deployment
kubectl scale deployment/pricing-api --replicas=3 -n spe-platform

# Update image
kubectl set image deployment/pricing-api pricing-api=spe-platform:pricing-api-v2 -n spe-platform

# Delete deployment
kubectl delete deployment pricing-api -n spe-platform
```

### Kubernetes Ingress

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml

# Update /etc/hosts
127.0.0.1 api.spe-platform.local
127.0.0.1 admin.spe-platform.local
127.0.0.1 shop.spe-platform.local

# Access services
curl http://api.spe-platform.local/health
curl http://admin.spe-platform.local
curl http://shop.spe-platform.local
```

### Kubernetes Autoscaling

```bash
# View HPA status
kubectl get hpa -n spe-platform

# Manual scaling
kubectl scale deployment pricing-api --replicas=5 -n spe-platform

# Check autoscale metrics
kubectl top pods -n spe-platform
kubectl top nodes
```

### CronJob for ML Training

```bash
# View CronJobs
kubectl get cronjobs -n spe-platform

# Trigger manual job
kubectl create job --from=cronjob/ml-trainer ml-trainer-manual-1 -n spe-platform

# View job history
kubectl get jobs -n spe-platform
kubectl logs -n spe-platform job/ml-trainer-manual-1
```

---

## 🔧 Ansible Configuration

### Playbooks

```bash
# 1. Setup infrastructure (Docker, Kubernetes, Jenkins)
ansible-playbook -i ansible/hosts.ini ansible/site.yml

# 2. Deploy to Kubernetes
ansible-playbook -i ansible/hosts.ini ansible/deploy-k8s.yml

# 3. Specific tags
ansible-playbook -i ansible/hosts.ini ansible/site.yml --tags docker

# 4. Dry run
ansible-playbook -i ansible/hosts.ini ansible/site.yml --check
```

### Hosts Configuration

```ini
[all]
localhost ansible_connection=local

[k8s_masters]
localhost

[docker_hosts]
localhost

[jenkins_masters]
localhost
```

### Ansible Modules Used

- `package` - Install packages
- `apt_key` - Add GPG keys
- `apt_repository` - Add repos
- `systemd` - Manage services
- `copy` - Copy files
- `kubernetes.core.k8s` - Kubernetes operations
- `get_url` - Download files

---

## 📊 Monitoring & Logging

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'pricing-api'
    static_configs:
      - targets: ['localhost:5001']
```

### Docker Logs

```bash
# View all logs
docker-compose logs

# Follow specific service
docker-compose logs -f pricing-api

# Last 50 lines
docker-compose logs --tail=50

# With timestamps
docker-compose logs -t
```

### Kubernetes Logs

```bash
# Pod logs
kubectl logs -n spe-platform pod/pricing-api-xyz

# Deployment logs (all pods)
kubectl logs -n spe-platform deployment/pricing-api -f

# Previous pod logs (if restarted)
kubectl logs -n spe-platform pod/pricing-api-xyz --previous
```

---

## 🔐 Security Best Practices

### Implemented Security Features

✅ **Pod Security**
- Non-root users (UID 1000)
- Read-only root filesystems
- Dropped Linux capabilities
- Resource limits

✅ **Network Security**
- Network policies (namespace isolation)
- Pod-to-pod communication rules
- Ingress TLS/SSL

✅ **RBAC**
- Service accounts per service
- Role-based access control
- Minimal permissions (least privilege)

✅ **Secrets Management**
- Kubernetes Secrets (encrypted at rest)
- Environment variables for credentials
- Secret files with restricted permissions

### Additional Security

```bash
# Enable Pod Security Standards
kubectl label namespace spe-platform pod-security.kubernetes.io/enforce=baseline

# View security context
kubectl get pods -n spe-platform -o jsonpath='{.items[*].spec.containers[*].securityContext}'

# Network policy verification
kubectl describe networkpolicy spe-network-policy -n spe-platform
```

---

## 🚨 Troubleshooting

### Docker Issues

```bash
# Docker daemon not running
sudo systemctl start docker

# Container won't start
docker logs container_name

# Remove dangling images
docker image prune -a

# Network connectivity
docker network inspect spe-network
```

### Kubernetes Issues

```bash
# Node not ready
kubectl describe node node_name

# Pod stuck in pending
kubectl describe pod pod_name -n spe-platform

# Service not accessible
kubectl describe svc service_name -n spe-platform

# Check events
kubectl get events -n spe-platform --sort-by='.lastTimestamp'
```

### Application Issues

```bash
# Check API health
curl http://localhost:5001/health

# Verify database connection
kubectl exec -it pod_name -n spe-platform -- /bin/bash

# Test internal service communication
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n spe-platform -- /bin/sh
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] Code reviewed and tested locally
- [ ] Docker images built and tested
- [ ] Security scan passed
- [ ] Secrets configured in Jenkins/K8s
- [ ] Database migrations ready
- [ ] Backup created

### Deployment

- [ ] Run full test suite
- [ ] Build and push Docker images
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Monitor logs and metrics
- [ ] Deploy to production

### Post-Deployment

- [ ] Verify all services are healthy
- [ ] Check endpoints are responding
- [ ] Monitor application metrics
- [ ] Verify data integrity
- [ ] Document any changes
- [ ] Notify stakeholders

---

## 📝 File Structure

```
spe-platform/
├── Dockerfile                    # Pricing API image
├── Dockerfile.admin             # Admin dashboard image
├── Dockerfile.customer          # Customer portal image
├── Dockerfile.trainer           # ML trainer image
├── docker-compose.yml           # Local development
├── Jenkinsfile                  # CI/CD pipeline
├── streamlit/
│   └── config.toml             # Streamlit config
├── ansible/
│   ├── site.yml                # Infrastructure setup
│   ├── deploy-k8s.yml          # Kubernetes deployment
│   ├── hosts.ini               # Ansible inventory
│   └── ansible.cfg             # Ansible config
├── scripts/
│   └── devops-setup.sh         # Setup script
├── k8s/
│   ├── namespace.yaml          # Namespace
│   ├── configmaps/
│   │   └── app-config.yaml
│   ├── secrets/
│   │   └── app-secrets.yaml
│   ├── deployments/
│   │   ├── app-deployments.yaml
│   │   └── ml-trainer-cronjob.yaml
│   ├── services/
│   │   └── app-services.yaml
│   ├── policies/
│   │   └── network-policy.yaml
│   ├── ingress/
│   │   └── ingress.yaml
│   └── rbac/
│       └── rbac.yaml
└── ...
```

---

## 🎯 Next Steps

1. **Customize Configurations**
   - Update Docker registry credentials
   - Configure database connection strings
   - Set up monitoring dashboards

2. **CI/CD Integration**
   - Connect Jenkins to GitHub/GitLab
   - Configure automated tests
   - Set up deployment notifications

3. **Monitoring & Alerts**
   - Set up Prometheus monitoring
   - Configure Grafana dashboards
   - Create alert rules

4. **Production Deployment**
   - Use managed Kubernetes (EKS, AKS, GKE)
   - Configure persistent volumes
   - Set up backup strategy
   - Enable SSL/TLS

---

## 📚 Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Last Updated:** 2026-05-13  
**Version:** 1.0.0
