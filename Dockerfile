# Railway Optimized Dockerfile - Claudia Cobranças
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements_minimal.txt requirements.txt ./

# Install Python dependencies with fallback
RUN pip install --no-cache-dir -r requirements_minimal.txt && \
    pip install --no-cache-dir -r requirements.txt || echo "Some optional dependencies failed"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads faturas web/static logs temp

# Set environment variables
ENV RAILWAY_DEPLOY=True \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Expose port
EXPOSE 8000

# Health check with longer timeout for Railway
HEALTHCHECK --interval=60s --timeout=90s --start-period=180s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
