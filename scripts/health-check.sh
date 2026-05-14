#!/bin/bash
# SPE Platform - Health Check Script
# Usage: chmod +x scripts/health-check.sh && ./scripts/health-check.sh

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      SPE Platform - Health Check               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo

# ===== API HEALTH =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}PRICING API (http://localhost:5001)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if curl -s http://localhost:5001/health | jq . >/dev/null 2>&1; then
    health=$(curl -s http://localhost:5001/health | jq '.')
    echo -e "${GREEN}✓ API is responding${NC}"
    echo "$health" | jq '.' | sed 's/^/  /'
else
    echo -e "${RED}✗ API is not responding${NC}"
fi
echo

# ===== ADMIN DASHBOARD HEALTH =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}ADMIN DASHBOARD (http://localhost:8503)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if curl -s http://localhost:8503/_stcore/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Admin Dashboard is responding${NC}"
else
    echo -e "${RED}✗ Admin Dashboard is not responding${NC}"
fi
echo

# ===== CUSTOMER PORTAL HEALTH =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}CUSTOMER PORTAL (http://localhost:8504)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if curl -s http://localhost:8504/_stcore/health >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Customer Portal is responding${NC}"
else
    echo -e "${RED}✗ Customer Portal is not responding${NC}"
fi
echo

# ===== DATABASE HEALTH =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}PostgreSQL Database (localhost:5432)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if docker exec postgres-db pg_isready -U spe_user >/dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is responding${NC}"
else
    echo -e "${RED}✗ PostgreSQL is not responding${NC}"
fi
echo

# ===== REDIS HEALTH =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Redis Cache (localhost:6379)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if docker exec redis-cache redis-cli ping >/dev/null 2>&1; then
    response=$(docker exec redis-cache redis-cli ping)
    echo -e "${GREEN}✓ Redis is responding: $response${NC}"
else
    echo -e "${RED}✗ Redis is not responding${NC}"
fi
echo

# ===== API ENDPOINTS TEST =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}API ENDPOINTS TEST${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test /products endpoint
if curl -s http://localhost:5001/products >/dev/null 2>&1; then
    product_count=$(curl -s http://localhost:5001/products | jq '.products | length' 2>/dev/null || echo "?")
    echo -e "${GREEN}✓ GET /products${NC} - Found $product_count products"
else
    echo -e "${RED}✗ GET /products${NC} - Failed"
fi

# Test /analytics endpoint
if curl -s http://localhost:5001/analytics >/dev/null 2>&1; then
    echo -e "${GREEN}✓ GET /analytics${NC} - OK"
else
    echo -e "${RED}✗ GET /analytics${NC} - Failed"
fi

# Test /cart endpoint
if curl -s http://localhost:5001/cart >/dev/null 2>&1; then
    echo -e "${GREEN}✓ GET /cart${NC} - OK"
else
    echo -e "${RED}✗ GET /cart${NC} - Failed"
fi
echo

# ===== DOCKER CONTAINERS =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}DOCKER CONTAINERS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

containers=("pricing-api" "admin-dashboard" "customer-portal" "postgres-db" "redis-cache")

for container in "${containers[@]}"; do
    if docker ps | grep -q "$container"; then
        echo -e "${GREEN}✓ $container${NC} - Running"
    else
        if docker ps -a | grep -q "$container"; then
            echo -e "${YELLOW}⊘ $container${NC} - Stopped"
        else
            echo -e "${RED}✗ $container${NC} - Not found"
        fi
    fi
done
echo

# ===== SUMMARY =====
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

total_checks=0
passed_checks=0

# Count results (simplified for this example)
running=$(docker ps | grep -c "spe-platform\|postgres\|redis" || echo 0)

if [ $running -ge 3 ]; then
    echo -e "${GREEN}✓ All services appear to be running${NC}"
else
    echo -e "${RED}✗ Some services are not running${NC}"
fi

echo
echo -e "${BLUE}Quick Access:${NC}"
echo -e "  Admin:      ${GREEN}http://localhost:8503${NC}"
echo -e "  Customer:   ${GREEN}http://localhost:8504${NC}"
echo -e "  API:        ${GREEN}http://localhost:5001${NC}"
echo

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Health check complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
