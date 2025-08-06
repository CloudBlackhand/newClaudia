#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Teste Ultra-Básico para Railway
"""

from fastapi import FastAPI
import logging
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Criar app
app = FastAPI()

@app.get("/")
async def root():
    logger.info("🔍 Root endpoint chamado")
    return {"message": "Claudia Cobranças Online", "status": "ok"}

@app.get("/health")
async def health():
    logger.info("✅ Healthcheck chamado")
    return {"status": "healthy"}

@app.get("/test")
async def test():
    logger.info("🧪 Test endpoint chamado")
    return {"test": "ok"}

# Log de inicialização
logger.info("🚀 App iniciando...")
logger.info(f"📊 PORT: {os.getenv('PORT', '8000')}")
logger.info(f"🌐 HOST: {os.getenv('HOST', '0.0.0.0')}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"🎯 Iniciando uvicorn na porta {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 