#!/bin/bash
set -e

# SPE Platform DevOps Setup Script
# This script sets up Docker, Kubernetes, Jenkins, and Ansible

echo "======================================"
echo "SPE Platform DevOps Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed${NC}"
    exit 1
fi
if ! command -v ansible &> /dev/null; then
    echo -e "${RED}Ansible is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Prerequisites OK${NC}"

# Setup Docker
echo -e "${YELLOW}[2/6] Running Ansible infrastructure setup...${NC}"
cd ansible
ansible-playbook -i hosts.ini site.yml -b -K
echo -e "${GREEN}✓ Infrastructure setup complete${NC}"

# Build Docker images
echo -e "${YELLOW}[3/6] Building Docker images...${NC}"
cd ..
docker build -t spe-platform:pricing-api .
docker build -f Dockerfile.admin -t spe-platform:admin .
docker build -f Dockerfile.customer -t spe-platform:customer .
docker build -f Dockerfile.trainer -t spe-platform:trainer .
echo -e "${GREEN}✓ Docker images built${NC}"

# Start Docker containers
echo -e "${YELLOW}[4/6] Starting Docker containers...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Docker containers started${NC}"

# Wait for services to be ready
echo -e "${YELLOW}[5/6] Waiting for services to be ready...${NC}"
sleep 15
for i in {1..30}; do
    if curl -f http://localhost:5001/health &> /dev/null; then
        echo -e "${GREEN}✓ Pricing API is healthy${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Timeout waiting for Pricing API${NC}"
        exit 1
    fi
    echo "Waiting for Pricing API ($i/30)..."
    sleep 2
done

# Display access information
echo -e "${YELLOW}[6/6] Setup complete!${NC}"
echo ""
echo -e "${GREEN}===== SERVICE ENDPOINTS =====${NC}"
echo -e "Pricing API:      ${GREEN}http://localhost:5001${NC}"
echo -e "Admin Dashboard:  ${GREEN}http://localhost:8503${NC}"
echo -e "Customer Portal:  ${GREEN}http://localhost:8504${NC}"
echo -e "PostgreSQL:       ${GREEN}localhost:5432${NC}"
echo -e "Redis:            ${GREEN}localhost:6379${NC}"
echo -e "Jenkins:          ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "${GREEN}===== NEXT STEPS =====${NC}"
echo "1. Access the admin dashboard at http://localhost:8503"
echo "2. Access the customer portal at http://localhost:8504"
echo "3. Check API health: curl http://localhost:5001/health"
echo "4. For Kubernetes deployment: ansible-playbook ansible/deploy-k8s.yml"
echo "5. View logs: docker-compose logs -f"
echo ""
