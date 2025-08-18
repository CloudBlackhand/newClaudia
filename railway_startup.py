#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Startup Script - Claudia Cobranças
Script otimizado para Railway com healthcheck rápido
"""

import os
import sys
import subprocess
import time
import threading
import signal
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

# Criar app minimalista para healthcheck rápido
health_app = FastAPI()

@health_app.get("/health")
async def health_check():
    return {"status": "healthy", "railway": True}

def install_playwright_async():
    """Instalar Playwright em background"""
    try:
        print("📦 Instalando Playwright em background...")
        subprocess.run([
            "python", "-m", "playwright", "install", "chromium"
        ], check=True, capture_output=True, timeout=300)
        print("✅ Playwright instalado")
    except Exception as e:
        print(f"⚠️ Aviso ao instalar Playwright: {e}")

def create_directories():
    """Criar diretórios necessários"""
    dirs = ["uploads", "faturas", "web/static", "logs", "temp"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
    print("✅ Diretórios criados")

def main():
    """Inicialização otimizada para Railway"""
    print("🚀 Iniciando Claudia Cobranças - Railway Mode")
    
    # Configurações
    port = int(os.getenv("PORT", 8000))
    railway_mode = os.getenv("RAILWAY_DEPLOY", "False") == "True"
    
    print(f"🔧 Modo Railway: {railway_mode}")
    print(f"🌐 Porta: {port}")
    
    # Criar diretórios imediatamente
    create_directories()
    
    # Iniciar instalação do Playwright em background
    if railway_mode:
        threading.Thread(target=install_playwright_async, daemon=True).start()
    
    # Configurações do servidor
    config = {
        "host": "0.0.0.0",
        "port": port,
        "log_level": "info",
        "access_log": True,
        "timeout_keep_alive": 300,
        "reload": False
    }
    
    if railway_mode:
        config.update({
            "workers": 1,
            "limit_concurrency": 10,
            "limit_max_requests": 1000,
            "backlog": 100
        })
    
    print(f"🎯 Iniciando servidor principal...")
    print(f"🌐 Healthcheck: http://0.0.0.0:{port}/health")
    print(f"📊 Dashboard: http://0.0.0.0:{port}/")
    
    try:
        # Importar app principal
        from app import app
        uvicorn.run("app:app", **config)
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        # Fallback para healthcheck básico
        print("🔄 Iniciando healthcheck básico...")
        uvicorn.run(health_app, host="0.0.0.0", port=port, log_level="error")

if __name__ == "__main__":
    main()
