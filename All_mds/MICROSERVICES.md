# Microservices Architecture Document

## Executive Summary

The SPE Platform can be decomposed into **4-5 microservices**, each with distinct responsibilities, scalability requirements, and deployment patterns.

---

## Microservices Inventory

### 1️⃣ **Pricing API Service**
**Type:** Backend API (Critical)  
**Technology:** Flask + Python  
**Port:** 5001  
**Responsibilities:**
- Product CRUD operations
- Price optimization (ML inference)
- Order processing
- Cart management
- Analytics aggregation
- Health checks

**Endpoints:**
```
GET    /health                  # Health check
GET    /products                # List all products
POST   /products                # Create product
GET    /product/<product_id>    # Get product details
POST   /optimize                # Run price optimizer
POST   /apply_price             # Apply optimized price
GET    /analytics               # Analytics dashboard
GET    /cart                    # Get user cart
POST   /cart/add                # Add to cart
POST   /checkout                # Process order
```

**Resource Requirements:**
- CPU: 250m (requests) → 500m (limits)
- Memory: 256Mi (requests) → 512Mi (limits)
- Replicas: 2-5 (scales with HPA)

**Dependencies:**
- Scikit-learn ML model
- CSV data files (products, inventory, orders)
- PostgreSQL (future enhancement)
- Redis (caching, future)

**Deployment:** Kubernetes Deployment with rolling updates

---

### 2️⃣ **Admin Dashboard Service**
**Type:** Frontend UI (Non-critical)  
**Technology:** Streamlit (Python)  
**Port:** 8503  
**Responsibilities:**
- Admin interface for price optimization
- Product management UI
- Analytics visualization
- Model retraining trigger
- Revenue metrics display
- Sales data viewing

**Features:**
- Price optimizer tab (run optimizer, apply prices)
- Products tab (add, edit, delete products)
- Analytics tab (revenue, bestsellers, trends)
- Retraining tab (upload data, retrain model)

**Resource Requirements:**
- CPU: 250m (requests) → 500m (limits)
- Memory: 512Mi (requests) → 1Gi (limits)
- Replicas: 1 (single user, non-scalable UI)

**Dependencies:**
- Pricing API Service

**Deployment:** Kubernetes Deployment (1 replica)

---

### 3️⃣ **Customer Portal Service**
**Type:** Frontend UI (High Priority)  
**Technology:** Streamlit (Python)  
**Port:** 8504  
**Responsibilities:**
- Product browsing and search
- Shopping cart management
- Checkout process
- Price display (AI-optimized)
- Customer experience

**Features:**
- Product catalog with search
- Filter by category
- Product details with images
- Stock indicators
- AI discount badges
- Add to cart
- Checkout process
- Order confirmation

**Resource Requirements:**
- CPU: 250m (requests) → 500m (limits)
- Memory: 512Mi (requests) → 1Gi (limits)
- Replicas: 2-4 (scales with HPA)

**Dependencies:**
- Pricing API Service

**Deployment:** Kubernetes Deployment with pod anti-affinity

---

### 4️⃣ **ML Trainer Service**
**Type:** Background Job (Scheduled)  
**Technology:** Python + Scikit-learn  
**Trigger:** Kubernetes CronJob (daily 2 AM)  
**Responsibilities:**
- Model retraining
- Performance metrics calculation
- Model evaluation (MAE, R²)
- Model versioning
- Log generation

**Features:**
- Automatic data loading
- Feature engineering
- Model training
- Cross-validation
- Metrics reporting
- Model backup

**Resource Requirements:**
- CPU: 1000m (requests) → 2000m (limits)
- Memory: 1Gi (requests) → 2Gi (limits)
- Schedule: Daily at 2 AM (configurable)

**Input/Output:**
- Input: sales_history.csv
- Output: pricing_model.pkl (new version)
- Logs: logs/retrain_*.log

**Deployment:** Kubernetes CronJob

---

### 5️⃣ **PostgreSQL Database Service**
**Type:** Data Storage (Optional, Future)  
**Technology:** PostgreSQL 15  
**Port:** 5432  
**Current Status:** Not used (using CSV files)  
**Responsibilities:**
- Persistent data storage
- Transaction management
- Backup and recovery
- ACID compliance

**Future Tables:**
```sql
-- Products
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(50),
  product_name VARCHAR(255),
  stock_code VARCHAR(50),
  current_price DECIMAL(10,2),
  optimized_price DECIMAL(10,2),
  stock INT
);

-- Orders
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  order_id VARCHAR(50),
  order_date TIMESTAMP,
  customer_email VARCHAR(255),
  total_amount DECIMAL(10,2)
);

-- Price History
CREATE TABLE price_history (
  id SERIAL PRIMARY KEY,
  product_id VARCHAR(50),
  old_price DECIMAL(10,2),
  new_price DECIMAL(10,2),
  changed_at TIMESTAMP,
  revenue_gain_pct DECIMAL(5,2)
);
```

**Resource Requirements:**
- CPU: 500m
- Memory: 1Gi
- Storage: 10-50Gi (grows with data)

**Deployment:** Kubernetes StatefulSet (with PersistentVolume)

---

## Communication Patterns

```
┌──────────────────┐
│  Admin Dashboard │────────┐
└──────────────────┘        │
                            │ HTTP REST
                            │ (requests lib)
                            ▼
                    ┌─────────────────┐
                    │ Pricing API     │◄────────────┐
                    │ (Flask)         │             │
                    └─────────────────┘             │
                            ▲                       │
                            │                       │
                    ┌───────┴──────┐                │
                    │              │                │
        ┌───────────┘              └──────┐         │
        │                                 │         │
        ▼                                 ▼         │
   CSV Files                      PostgreSQL/Redis │
   (products.csv,                 (future)         │
    inventory.csv,                                  │
    orders.csv)          ┌──────────────────┐      │
                         │ Customer Portal  │──────┘
                         │ (Streamlit)      │
                         └──────────────────┘

        ML Trainer (CronJob)
        ↓
        └─→ Reads: sales_history.csv
        └─→ Writes: pricing_model.pkl
```

---

## Scalability Analysis

### Horizontal Scaling (Pod Replicas)

| Service | Min | Max | Trigger |
|---------|-----|-----|---------|
| Pricing API | 2 | 5 | CPU >70%, Memory >80% |
| Customer Portal | 2 | 4 | CPU >75%, Memory >85% |
| Admin Dashboard | 1 | 1 | Not scalable (UI) |
| ML Trainer | 1 | 1 | Not scalable (CronJob) |

### Vertical Scaling (Resource Limits)

Can increase CPU/Memory limits if:
- High request latency (>500ms)
- High memory usage (>80% limit)
- CPU throttling detected

---

## Data Flow

### 1. Price Optimization Flow
```
Admin Dashboard
    ↓
Submits optimization request (product_id, price, stock, day, month, competitor_price)
    ↓
Pricing API /optimize endpoint
    ↓
Scikit-learn model.predict()
    ↓
Returns: optimized_price, predicted_demand, revenue_gain
    ↓
Admin applies price (POST /apply_price)
    ↓
Updates products.csv + price_history.csv
    ↓
Customer Portal reads updated price
```

### 2. Order Processing Flow
```
Customer Portal
    ↓
Customer adds items to cart
    ↓
Clicks checkout
    ↓
POST /checkout to Pricing API
    ↓
Creates order (orders.csv)
    ↓
Updates inventory.csv
    ↓
Updates sales_history.csv
    ↓
Order confirmation
```

### 3. Model Retraining Flow
```
Kubernetes CronJob triggers daily
    ↓
ML Trainer reads sales_history.csv
    ↓
Loads clean_demand_data.csv
    ↓
Feature engineering (day, month, demand, price)
    ↓
Train RandomForestRegressor
    ↓
Calculate metrics (MAE, R²)
    ↓
Save new pricing_model.pkl
    ↓
Pricing API reloads model (next restart/reload)
```

---

## Deployment Strategies

### Development
- Docker Compose (all services on local machine)
- CSV files for data
- Single replica per service

### Staging
- Kubernetes (minikube or small cluster)
- Multiple replicas for API services
- CronJob for model training
- PostgreSQL for data persistence

### Production
- Managed Kubernetes (EKS, AKS, GKE)
- Multi-node cluster
- Auto-scaling enabled
- Persistent volumes for data
- Load balancer for traffic distribution
- SSL/TLS for all endpoints

---

## Service Dependency Matrix

```
┌────────────────────┬─────────────┬─────────────┬──────────────┬──────────┐
│ Service            │ API Service │ Admin UI    │ Customer UI  │ Trainer  │
├────────────────────┼─────────────┼─────────────┼──────────────┼──────────┤
│ Pricing API        │ -           │ N/A         │ N/A          │ N/A      │
├────────────────────┼─────────────┼─────────────┼──────────────┼──────────┤
│ Admin Dashboard    │ Required    │ -           │ No           │ No       │
├────────────────────┼─────────────┼─────────────┼──────────────┼──────────┤
│ Customer Portal    │ Required    │ No          │ -            │ No       │
├────────────────────┼─────────────┼─────────────┼──────────────┼──────────┤
│ ML Trainer         │ No          │ No          │ No           │ -        │
├────────────────────┼─────────────┼─────────────┼──────────────┼──────────┤
│ PostgreSQL         │ Future      │ No          │ No           │ No       │
└────────────────────┴─────────────┴─────────────┴──────────────┴──────────┘
```

---

## Monitoring & Metrics

### Per-Service Metrics

**Pricing API:**
- Request latency (p50, p95, p99)
- Requests per second
- Error rate (4xx, 5xx)
- ML model inference time
- Data file access time

**Admin Dashboard:**
- Page load time
- API call success rate
- User session duration

**Customer Portal:**
- Page load time
- Checkout success rate
- Cart abandonment rate
- API call latency

**ML Trainer:**
- Training job duration
- Model accuracy (MAE, R²)
- Data loading time
- Model file size

---

## Future Enhancements

### Phase 2
- [ ] PostgreSQL integration
- [ ] Redis caching layer
- [ ] API authentication (JWT)
- [ ] Rate limiting
- [ ] Prometheus/Grafana monitoring

### Phase 3
- [ ] Microservices mesh (Istio)
- [ ] GraphQL API layer
- [ ] Event streaming (Kafka)
- [ ] Service discovery (Consul)
- [ ] Distributed tracing

### Phase 4
- [ ] Machine learning model serving (TensorFlow Serving, KServe)
- [ ] Real-time analytics (ELK Stack)
- [ ] Multi-region deployment
- [ ] Blue-green deployments
- [ ] Chaos engineering testing

---

## Summary

| Aspect | Details |
|--------|---------|
| **Total Microservices** | 4-5 services |
| **API-based communication** | REST HTTP |
| **Current data storage** | CSV files |
| **Scalability** | Horizontal (HPA enabled) |
| **Deployment target** | Kubernetes |
| **CI/CD tool** | Jenkins |
| **Infrastructure as Code** | Terraform/Ansible |
| **Monitoring** | Prometheus/Grafana (future) |

---

**Last Updated:** 2026-05-13  
**Version:** 1.0.0
