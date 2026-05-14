# ELK Stack Integration Guide

## 📊 **What is ELK Stack?**

- **Elasticsearch**: Stores and indexes logs
- **Logstash**: Collects, processes, and forwards logs
- **Kibana**: Visualizes logs and creates dashboards

---

## 🚀 **Quick Start: Run ELK Stack**

```bash
cd /home/ruturajwairkar/Desktop/SPE_MP

# Start ELK services
docker-compose -f docker-compose.elk.yml up -d

# Verify services started
docker-compose -f docker-compose.elk.yml ps

# Check logs
docker-compose -f docker-compose.elk.yml logs -f logstash
```

---

## 📝 **Services & Ports**

| Service | Port | URL |
|---------|------|-----|
| **Elasticsearch** | 9200 | http://localhost:9200 |
| **Kibana** | 5601 | http://localhost:5601 |
| **Logstash** | 5000 | localhost:5000 (TCP/UDP) |

---

## 🔗 **Integration with Your App**

### **Current Setup:**
1. ✅ Flask API logs to `logs/api.log` in JSON format
2. ✅ Logstash reads `logs/` directory
3. ✅ Logs sent to Elasticsearch
4. ✅ Kibana visualizes them

### **Log Flow:**
```
Flask App → logs/api.log (JSON) → Logstash → Elasticsearch → Kibana Dashboard
```

---

## 📊 **Access Kibana Dashboard**

1. Open: **http://localhost:5601**
2. Go to **Analytics** → **Discover**
3. Create index pattern:
   - Name: `spe-platform-*`
   - Time field: `@timestamp`
4. View logs in real-time!

---

## 📌 **Useful Kibana Commands**

### Create Index Pattern (CLI)
```bash
curl -X POST "http://localhost:5601/api/saved_objects/index-pattern" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "spe-platform-*",
      "timeFieldName": "@timestamp"
    }
  }'
```

### Query Logs
```bash
# Get all logs
curl "http://localhost:9200/spe-platform-*/_search"

# Get error logs only
curl "http://localhost:9200/spe-platform-*/_search?q=level:ERROR"

# Get logs from last 1 hour
curl "http://localhost:9200/spe-platform-*/_search" -d '{
  "query": {
    "range": {
      "@timestamp": {"gte": "now-1h"}
    }
  }
}'
```

---

## ✅ **Verify ELK is Working**

```bash
# Check Elasticsearch is running
curl http://localhost:9200/_cluster/health

# Expected output:
# {
#   "cluster_name" : "docker-cluster",
#   "status" : "green",
#   "timed_out" : false
# }

# Check if logs are indexed
curl "http://localhost:9200/_cat/indices"

# Expected: spe-platform-2026.05.14 (or today's date)
```

---

## 🎯 **Dashboard Examples**

Create these visualizations in Kibana:

### 1. **Log Levels Pie Chart**
```
Visualization → Pie Chart
Data: Count of logs grouped by level (INFO, ERROR, WARNING)
```

### 2. **Errors Timeline**
```
Visualization → Line Chart
Data: Count of ERROR level logs over time
```

### 3. **Service Health**
```
Visualization → Gauge
Data: Percentage of successful logs (not ERROR)
```

### 4. **Top Endpoints**
```
Visualization → Table
Data: Function names with error count
```

---

## 🔍 **Troubleshooting**

### "No data in Kibana"
```bash
# Check Logstash is reading logs
docker-compose -f docker-compose.elk.yml logs logstash

# Manually check indices
curl "http://localhost:9200/_cat/indices?v"

# If empty, trigger some API requests
curl http://localhost:5001/health
curl http://localhost:5001/products
```

### "Elasticsearch won't start"
```bash
# Check memory
docker-compose -f docker-compose.elk.yml logs elasticsearch

# Increase memory (edit docker-compose.elk.yml)
# Change: "ES_JAVA_OPTS=-Xms512m -Xmx512m" to "-Xms1g -Xmx1g"

docker-compose -f docker-compose.elk.yml restart elasticsearch
```

---

## 📦 **Stop ELK Stack**

```bash
docker-compose -f docker-compose.elk.yml down

# Remove all data
docker-compose -f docker-compose.elk.yml down -v
```

---

## 🎓 **How to Use for Your Project**

1. **Start your main services:**
   ```bash
   docker-compose up -d
   ```

2. **Start ELK Stack:**
   ```bash
   docker-compose -f docker-compose.elk.yml up -d
   ```

3. **Generate logs by using your app:**
   ```bash
   curl http://localhost:5001/products
   curl http://localhost:8503  # Admin dashboard
   curl http://localhost:8504  # Customer portal
   ```

4. **View in Kibana:**
   - Open http://localhost:5601
   - Go to Discover
   - Search and filter logs in real-time!

---

## ✨ **Advanced Features**

### Log Alert Example
In Kibana → Alerting → Create alert when ERROR count > 10 in 5 minutes

### Log Export
In Kibana Discover → Export → CSV/JSON

### Custom Dashboards
Create multi-panel dashboards combining multiple visualizations

---

That's it! ELK Stack integration is complete! 🎉

Next: **GitHub Webhook Setup** for automatic Jenkins triggers
