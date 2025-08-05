#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start Script - Claudia Cobranças
Script simples e robusto para Railway
"""

import os
import sys
import subprocess

def main():
    """Inicialização simples"""
    print("🚀 Iniciando Claudia Cobranças...")
    
    # Instalar Playwright se necessário
    try:
        print("📦 Instalando Playwright...")
        subprocess.run(["python", "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True)
        print("✅ Playwright instalado")
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
    
    # Iniciar servidor
    port = os.getenv("PORT", "8000")
    cmd = [
        "python", "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", port
    ]
    
    print(f"🎯 Iniciando servidor na porta {port}...")
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 