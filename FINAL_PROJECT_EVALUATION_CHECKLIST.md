# SPE Final Project Evaluation Checklist

This file maps the CSE 816 final project rubric to the implemented project artifacts.

## Mandatory Requirements

| Requirement | Project Evidence |
| --- | --- |
| Git and GitHub version control | Git repository in `SPE_MP`; push to GitHub and configure webhook to Jenkins. |
| GitHub hook trigger for Jenkins | `Jenkinsfile` has `githubPush()` and `pollSCM('H/5 * * * *')`. |
| Jenkins pipeline | `Jenkinsfile` checks out code, builds images, runs automated syntax tests, pushes Docker images, deploys to Kubernetes, and runs post-deployment health check. |
| Docker containerization | `Dockerfile`, `Dockerfile.admin`, `Dockerfile.customer`, `Dockerfile.trainer`. |
| Docker Compose | `docker-compose.yml` runs pricing API, admin portal, customer portal, PostgreSQL, and Redis. |
| Ansible configuration management | `ansible/site.yml` uses modular roles from `ansible/roles/*`. |
| Kubernetes orchestration | `k8s/namespace.yaml`, deployments, services, ingress, configmaps, secrets, and RBAC. |
| Scaling | `k8s/policies/network-policy.yaml` includes HPA for `pricing-api` and `customer-portal`. |
| Monitoring and logging with ELK | `docker-compose.elk.yml`, `elk/logstash.conf`, `elk/README.md`, `elk/KIBANA_SETUP.md`; API writes JSON logs to `logs/api.log`. |
| New changes visible after refresh | CI/CD rebuilds images, deploys to K8s, and rollout status waits for updated pods. |

## Advanced Features

| Feature | Project Evidence |
| --- | --- |
| Vault or secure storage | `docker-compose.vault.yml`, `vault/README.md`; intended for Docker Hub credentials, kubeconfig, and app secrets. |
| Modular Ansible | Roles under `ansible/roles/common`, `docker`, `jenkins`, `kubernetes`, and `monitoring`. |
| Kubernetes HPA | `pricing-api-hpa` and `customer-portal-hpa` in `k8s/policies/network-policy.yaml`. |
| Domain-specific innovation | MLOps-oriented AI pricing platform with retraining workflow, model reload endpoint, admin optimizer, customer portal, and price history. |

## Demo Flow

1. Push code to GitHub.
2. GitHub webhook triggers Jenkins.
3. Jenkins checks out code, builds Docker images, and runs automated syntax checks.
4. On `main`, Jenkins pushes images to Docker Hub.
5. Jenkins deploys Kubernetes manifests and waits for rollout.
6. Open the admin/customer portal and refresh to see the latest change.
7. Generate app traffic and open Kibana at `http://localhost:5601`.
8. Show `spe-platform-*` logs in Kibana Discover/dashboard.

## Commands

```bash
docker compose up -d --build
docker compose -f docker-compose.elk.yml up -d
docker compose -f docker-compose.vault.yml up -d
ansible-playbook -i ansible/hosts.ini ansible/site.yml --check
kubectl apply -f k8s/
```
