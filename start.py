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
    
    # Verificar se estamos no Railway
    railway_mode = os.getenv("RAILWAY_DEPLOY", "False") == "True"
    port = os.getenv("PORT", "8000")
    
    print(f"🔧 Modo Railway: {railway_mode}")
    print(f"🌐 Porta: {port}")
    
    # Criar diretórios necessários
    print("📁 Criando diretórios necessários...")
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("faturas", exist_ok=True)
    os.makedirs("web/static", exist_ok=True)
    print("✅ Diretórios criados")
    
    # Instalar Playwright se necessário (com tratamento de erro)
    try:
        print("📦 Instalando Playwright...")
        subprocess.run(["python", "-m", "playwright", "install", "chromium"], 
                      check=True, capture_output=True, timeout=300)
        print("✅ Playwright instalado")
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
        print("🔄 Continuando sem Playwright...")
    
    # Iniciar servidor
    cmd = [
        "python", "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", port,
        "--timeout-keep-alive", "300",
        "--log-level", "info"
    ]
    
    print(f"🎯 Iniciando servidor na porta {port}...")
    print(f"🌐 Healthcheck: http://0.0.0.0:{port}/health")
    print(f"📊 Dashboard: http://0.0.0.0:{port}/")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 Servidor interrompido pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    main() 