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

# Removido bloco de inicialização direta do servidor para evitar conflito com Dockerfile
