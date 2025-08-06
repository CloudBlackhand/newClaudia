#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Simples para Teste Railway
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import logging
from datetime import datetime

# Configuração básica
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar app
app = FastAPI(title="Claudia Cobranças", version="2.2")

# Estado básico
system_state = {
    "whatsapp_connected": False,
    "bot_active": False,
    "fpd_loaded": False,
    "vendas_loaded": False,
    "stats": {}
}

@app.get("/")
async def root():
    """Página inicial"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Claudia Cobranças</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>🚀 Claudia Cobranças - Sistema Online</h3>
                        </div>
                        <div class="card-body">
                            <p>✅ Sistema funcionando corretamente!</p>
                            <p>📊 Status: Online</p>
                            <p>🕐 Timestamp: """ + str(datetime.now()) + """</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    """Healthcheck ultra-simples"""
    logger.info("✅ Healthcheck chamado")
    return {"status": "healthy", "timestamp": str(datetime.now())}

@app.get("/api/status")
async def status():
    """Status do sistema"""
    return {
        "status": "online",
        "version": "2.2",
        "whatsapp_connected": system_state["whatsapp_connected"],
        "bot_active": system_state["bot_active"],
        "fpd_loaded": system_state["fpd_loaded"],
        "vendas_loaded": system_state["vendas_loaded"],
        "timestamp": str(datetime.now())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 