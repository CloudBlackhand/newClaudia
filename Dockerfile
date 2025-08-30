# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-railway.txt requirements.txt ./

# Install Python dependencies optimized for Railway
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-warn-script-location -r requirements-railway.txt

# Copy application code
COPY . .

# Create directories for logs and data
RUN mkdir -p logs data/uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=backend.app:app
ENV FLASK_ENV=production
ENV PORT=8000

# Create non-root user for security
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "300", "backend.app:app"]

