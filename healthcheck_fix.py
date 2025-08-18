#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick healthcheck fix for Railway deployment
"""

import os
import sys
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create a minimal healthcheck app
app = FastAPI()

@app.get("/health")
async def health_check():
    """Fast healthcheck for Railway"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "claudia-cobrancas",
        "environment": "railway"
    }

@app.get("/")
async def root():
    """Root endpoint for Railway"""
    return {
        "message": "Claudia Cobranças - Railway Deployment",
        "status": "running",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
