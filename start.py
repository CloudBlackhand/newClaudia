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
        
        # Instalar dependências do sistema para Railway
        print("🔧 Instalando dependências do sistema...")
        subprocess.run(["python", "-m", "playwright", "install-deps"], 
                      check=True, capture_output=True)
        print("✅ Dependências do sistema instaladas")
    except Exception as e:
        print(f"⚠️ Aviso: {e}")
        print("🔄 Tentando instalação alternativa...")
        try:
            # Fallback para Railway
            subprocess.run(["python", "-m", "playwright", "install", "chromium", "--with-deps"], 
                          check=True, capture_output=True)
            print("✅ Playwright instalado com dependências")
        except Exception as e2:
            print(f"⚠️ Aviso: {e2}")
    
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