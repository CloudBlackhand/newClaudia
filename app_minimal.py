#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Minimalista para Railway - Apenas FastAPI
"""

import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Criar app FastAPI
app = FastAPI(title="Claudia Cobranças", version="2.2")

# Adicionar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Endpoint raiz"""
    logger.info("🔍 Root endpoint chamado")
    return {"message": "Claudia Cobranças Online", "status": "ok"}

@app.get("/health")
async def health():
    """Healthcheck simples"""
    logger.info("✅ Healthcheck chamado")
    return {"status": "healthy"}

@app.get("/test")
async def test():
    """Endpoint de teste"""
    logger.info("🧪 Test endpoint chamado")
    return {"test": "ok"}

# Log de inicialização
logger.info("🚀 App minimalista iniciando...")
logger.info(f"📊 PORT: {os.getenv('PORT', '8000')}")
logger.info(f"🌐 HOST: {os.getenv('HOST', '0.0.0.0')}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🎯 Iniciando uvicorn na porta {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 