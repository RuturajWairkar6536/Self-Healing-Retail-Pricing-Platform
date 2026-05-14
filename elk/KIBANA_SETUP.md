# Kibana Dashboard Setup for SPE Platform

## Pre-configured Dashboards

This file contains the API calls to setup Kibana dashboards for the SPE Platform.

### 1. Create Index Pattern
```bash
curl -X POST "http://localhost:5601/api/saved_objects/index-pattern/spe-platform" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "spe-platform-*",
      "timeFieldName": "@timestamp"
    }
  }'
```

### 2. Create Log Dashboard
```bash
curl -X POST "http://localhost:5601/api/saved_objects/dashboard/spe-logs" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "SPE Platform Logs",
      "panels": [
        {
          "visualization": "spe-log-levels",
          "x": 0,
          "y": 0,
          "w": 12,
          "h": 4
        },
        {
          "visualization": "spe-errors",
          "x": 0,
          "y": 4,
          "w": 12,
          "h": 4
        }
      ]
    }
  }'
```

### 3. Create Visualizations

#### Log Levels Pie Chart
```bash
curl -X POST "http://localhost:5601/api/saved_objects/visualization/spe-log-levels" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "title": "Log Levels Distribution",
      "visState": "{\"title\": \"Log Levels Distribution\", \"type\": \"pie\"}",
      "kibanaSavedObjectMeta": {"searchSourceJSON": "{\"index\": \"spe-platform-*\"}"}
    }
  }'
```

### Manual Setup (Easier)

1. Open Kibana: http://localhost:5601
2. Go to **Stack Management** → **Index Patterns**
3. Create pattern: `spe-platform-*`
4. Set **@timestamp** as time field
5. Go to **Dashboards** → **Create Dashboard**
6. Add visualizations:
   - Log counts by level
   - Error distribution
   - API response times
   - Service uptime
