# Multi-stage build for Pricing API Service
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install globally to avoid /root/.local permission issues
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Create a non-root user for security
RUN groupadd -g 1000 spegroup && \
    useradd -u 1000 -g spegroup -m speuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app.py .
COPY requirements.txt .
COPY pricing_model.pkl .
COPY data/ ./data/
RUN mkdir -p ./logs && chown -R speuser:spegroup /app

# Switch to non-root user
USER speuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

EXPOSE 5001
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
