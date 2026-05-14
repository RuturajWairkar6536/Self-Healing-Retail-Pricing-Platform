#!/bin/bash
# SPE Platform - Kubernetes Monitoring Script
# Usage: chmod +x scripts/monitor-k8s.sh && ./scripts/monitor-k8s.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

NAMESPACE="spe-platform"

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    SPE Platform - Kubernetes Monitoring        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl is not installed${NC}"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo -e "${RED}✗ Kubernetes cluster is not accessible${NC}"
    echo "Start cluster with: minikube start"
    exit 1
fi

echo -e "${GREEN}✓ Kubernetes cluster is accessible${NC}"
echo

# ===== CLUSTER INFO =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}CLUSTER INFORMATION${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl version --short
echo

# ===== NAMESPACE =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}NAMESPACE: $NAMESPACE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if kubectl get namespace $NAMESPACE >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Namespace exists${NC}"
else
    echo -e "${RED}✗ Namespace does not exist${NC}"
    exit 1
fi
echo

# ===== PODS STATUS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}POD STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get pods -n $NAMESPACE --no-headers || echo "No pods found"

# Check pod count
total_pods=$(kubectl get pods -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
running_pods=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase=Running --no-headers 2>/dev/null | wc -l)

echo
echo -e "Total Pods: ${YELLOW}$total_pods${NC}"
echo -e "Running: ${GREEN}$running_pods${NC}"
echo

# ===== POD DETAILS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}POD DETAILS (Health & Ready Status)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get pods -n $NAMESPACE -o custom-columns=NAME:.metadata.name,READY:.status.conditions[?(@.type=="Ready")].status,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount || echo "No pods found"
echo

# ===== DEPLOYMENTS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}DEPLOYMENTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get deployments -n $NAMESPACE || echo "No deployments found"
echo

# ===== SERVICES =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SERVICES & ENDPOINTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get services -n $NAMESPACE || echo "No services found"
echo

echo -e "${YELLOW}Service Endpoints:${NC}"
kubectl get endpoints -n $NAMESPACE || echo "No endpoints found"
echo

# ===== CRONJOBS & JOBS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}CRONJOBS & JOBS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}CronJobs:${NC}"
kubectl get cronjobs -n $NAMESPACE || echo "No cronjobs found"

echo
echo -e "${YELLOW}Recent Jobs:${NC}"
kubectl get jobs -n $NAMESPACE || echo "No jobs found"
echo

# ===== HPA (HORIZONTAL POD AUTOSCALER) =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}HORIZONTAL POD AUTOSCALER (HPA)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get hpa -n $NAMESPACE || echo "No HPAs found"
echo

# ===== RESOURCE USAGE =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}RESOURCE USAGE (Pods)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if kubectl top pod -n $NAMESPACE >/dev/null 2>&1; then
    kubectl top pods -n $NAMESPACE
else
    echo -e "${YELLOW}⊘ Metrics server not installed (install with: kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml)${NC}"
fi
echo

# ===== EVENTS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}RECENT EVENTS (Last 10)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | tail -10 || echo "No events found"
echo

# ===== POD HEALTH CHECK =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}POD HEALTH CHECK (Probe Status)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

for pod in $(kubectl get pods -n $NAMESPACE -o name --field-selector=status.phase=Running); do
    pod_name=$(basename $pod)
    ready=$(kubectl get $pod -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}')
    if [ "$ready" = "True" ]; then
        echo -e "${GREEN}✓ $pod_name${NC}: Ready"
    else
        echo -e "${RED}✗ $pod_name${NC}: Not Ready"
    fi
done
echo

# ===== PERSISTENT VOLUMES =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}PERSISTENT VOLUMES & CLAIMS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

kubectl get pvc -n $NAMESPACE || echo "No persistent volume claims found"
echo

# ===== CONFIG MAPS & SECRETS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}CONFIGMAPS & SECRETS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}ConfigMaps:${NC}"
kubectl get configmaps -n $NAMESPACE || echo "No configmaps found"

echo
echo -e "${YELLOW}Secrets:${NC}"
kubectl get secrets -n $NAMESPACE || echo "No secrets found"
echo

# ===== SERVICE ENDPOINTS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SERVICE ACCESS (Port Forwarding)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "To access services locally, use:"
echo -e "  ${GREEN}kubectl port-forward svc/pricing-api 5001:5001 -n $NAMESPACE${NC}"
echo -e "  ${GREEN}kubectl port-forward svc/admin-dashboard 8503:8503 -n $NAMESPACE${NC}"
echo -e "  ${GREEN}kubectl port-forward svc/customer-portal 8504:8504 -n $NAMESPACE${NC}"
echo

# ===== SUMMARY =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "Namespace:            ${YELLOW}$NAMESPACE${NC}"
echo -e "Total Pods:           ${YELLOW}$total_pods${NC}"
echo -e "Running:              ${GREEN}$running_pods${NC}"
echo -e "Deployments:          ${YELLOW}$(kubectl get deployments -n $NAMESPACE --no-headers 2>/dev/null | wc -l)${NC}"
echo -e "Services:             ${YELLOW}$(kubectl get services -n $NAMESPACE --no-headers 2>/dev/null | wc -l)${NC}"
echo -e "ConfigMaps:           ${YELLOW}$(kubectl get configmaps -n $NAMESPACE --no-headers 2>/dev/null | wc -l)${NC}"

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Monitoring complete!${NC}"
echo -e "${GREEN}Watch pods with: kubectl get pods -n $NAMESPACE -w${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
