#!/bin/bash
# SPE Platform - Docker Monitoring Script
# Usage: chmod +x scripts/monitor-docker.sh && ./scripts/monitor-docker.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SPE Platform - Docker Monitoring           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo

# Check if docker is running
if ! docker ps >/dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running or not installed${NC}"
    echo "Start Docker with: sudo systemctl start docker"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"
echo

# ===== RUNNING CONTAINERS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}RUNNING CONTAINERS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No containers running"
echo

# ===== CONTAINER STATUS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SERVICE STATUS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check pricing-api
if docker inspect pricing-api >/dev/null 2>&1; then
    if docker ps | grep -q pricing-api; then
        echo -e "${GREEN}✓ Pricing API${NC}: Running"
        # Check health
        if curl -s http://localhost:5001/health >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Health Check${NC}: PASSING"
        else
            echo -e "  ${RED}✗ Health Check${NC}: FAILING"
        fi
    else
        echo -e "${RED}✗ Pricing API${NC}: Stopped"
    fi
else
    echo -e "${YELLOW}⊘ Pricing API${NC}: Not created"
fi

# Check admin-dashboard
if docker inspect admin-dashboard >/dev/null 2>&1; then
    if docker ps | grep -q admin-dashboard; then
        echo -e "${GREEN}✓ Admin Dashboard${NC}: Running"
        if curl -s http://localhost:8503/_stcore/health >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Health Check${NC}: PASSING"
        else
            echo -e "  ${RED}✗ Health Check${NC}: FAILING"
        fi
    else
        echo -e "${RED}✗ Admin Dashboard${NC}: Stopped"
    fi
else
    echo -e "${YELLOW}⊘ Admin Dashboard${NC}: Not created"
fi

# Check customer-portal
if docker inspect customer-portal >/dev/null 2>&1; then
    if docker ps | grep -q customer-portal; then
        echo -e "${GREEN}✓ Customer Portal${NC}: Running"
        if curl -s http://localhost:8504/_stcore/health >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Health Check${NC}: PASSING"
        else
            echo -e "  ${RED}✗ Health Check${NC}: FAILING"
        fi
    else
        echo -e "${RED}✗ Customer Portal${NC}: Stopped"
    fi
else
    echo -e "${YELLOW}⊘ Customer Portal${NC}: Not created"
fi

# Check PostgreSQL
if docker inspect postgres-db >/dev/null 2>&1; then
    if docker ps | grep -q postgres-db; then
        echo -e "${GREEN}✓ PostgreSQL${NC}: Running (Port 5432)"
    else
        echo -e "${RED}✗ PostgreSQL${NC}: Stopped"
    fi
else
    echo -e "${YELLOW}⊘ PostgreSQL${NC}: Not created"
fi

# Check Redis
if docker inspect redis-cache >/dev/null 2>&1; then
    if docker ps | grep -q redis-cache; then
        echo -e "${GREEN}✓ Redis${NC}: Running (Port 6379)"
    else
        echo -e "${RED}✗ Redis${NC}: Stopped"
    fi
else
    echo -e "${YELLOW}⊘ Redis${NC}: Not created"
fi

echo

# ===== RESOURCE USAGE =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}RESOURCE USAGE (Top 5)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -6 || echo "No containers running"
echo

# ===== DOCKER IMAGES =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SPE PLATFORM IMAGES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker images | grep -i "spe-platform\|python:3.11" || echo "No SPE images found"
echo

# ===== DOCKER VOLUMES =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}DOCKER VOLUMES${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker volume ls | grep -i spe || echo "No SPE volumes found"
echo

# ===== DOCKER NETWORKS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}DOCKER NETWORKS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker network ls | grep -i spe || echo "No SPE networks found"
echo

# ===== SERVICE ENDPOINTS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SERVICE ENDPOINTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "API Server:        ${GREEN}http://localhost:5001${NC}"
echo -e "Admin Dashboard:   ${GREEN}http://localhost:8503${NC}"
echo -e "Customer Portal:   ${GREEN}http://localhost:8504${NC}"
echo -e "PostgreSQL:        ${GREEN}localhost:5432${NC}"
echo -e "Redis:             ${GREEN}localhost:6379${NC}"
echo -e "Jenkins:           ${GREEN}http://localhost:8080${NC}"
echo

# ===== RECENT LOGS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}RECENT LOG ERRORS (Last 10 lines)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check for errors in pricing-api logs
if docker ps | grep -q pricing-api; then
    error_count=$(docker logs pricing-api 2>&1 | grep -i "error\|exception" | wc -l)
    if [ $error_count -gt 0 ]; then
        echo -e "${RED}Found $error_count errors in Pricing API logs:${NC}"
        docker logs pricing-api 2>&1 | grep -i "error\|exception" | tail -5
    else
        echo -e "${GREEN}✓ No errors in Pricing API logs${NC}"
    fi
fi
echo

# ===== SUMMARY =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

total=$(docker ps --all --quiet | wc -l)
running=$(docker ps --quiet | wc -l)
stopped=$((total - running))

echo -e "Total Containers:     ${YELLOW}$total${NC}"
echo -e "Running:              ${GREEN}$running${NC}"
echo -e "Stopped:              ${YELLOW}$stopped${NC}"
echo -e "Docker Images:        ${YELLOW}$(docker images --quiet | wc -l)${NC}"
echo -e "Docker Volumes:       ${YELLOW}$(docker volume ls --quiet | wc -l)${NC}"

echo
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Monitoring complete! Refresh with: docker-compose logs -f${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
