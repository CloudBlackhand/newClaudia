#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Start Script - Claudia Cobranças
Script otimizado para inicialização na Railway
"""

import os
import sys
import subprocess
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Função principal de inicialização"""
    print("🚂 Iniciando Claudia Cobranças na Railway...")
    print("🏢 Sistema oficial de cobrança da Desktop")
    print("🧠 Inteligência nível ChatGPT")
    print("🔐 Sistema de login com aprovação manual")
    print("💾 StorageManager com limite de 50MB")
    print("🚀 Otimizado para Railway")
    print()
    
    # Verificar dependências
    print("📦 Verificando dependências...")
    try:
        import fastapi
        import uvicorn
        import playwright
        print("✅ Dependências principais OK")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        sys.exit(1)
    
    # Verificar arquivos essenciais
    essential_files = [
        "app.py",
        "config.py", 
        "requirements.txt",
        "Procfile",
        "railway.toml"
    ]
    
    print("📁 Verificando arquivos essenciais...")
    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - FALTANDO!")
            sys.exit(1)
    
    print("✅ Todos os arquivos essenciais encontrados")
    print()
    
    # Iniciar aplicação
    print("🚀 Iniciando Claudia Cobranças...")
    
    # Mostrar URL real do Railway
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    railway_url = os.getenv('RAILWAY_URL')
    
    if railway_domain:
        base_url = f"https://{railway_domain}"
        print(f"🌐 URL REAL: {base_url}")
        print(f"🔐 Login: {base_url}/login")
        print(f"📊 Dashboard: {base_url}/dashboard")
    elif railway_url:
        print(f"🌐 URL REAL: {railway_url}")
        print(f"🔐 Login: {railway_url}/login")
        print(f"📊 Dashboard: {railway_url}/dashboard")
    else:
        print("🌐 Acesse: https://seu-app.railway.app")
        print("🔐 Login: /login")
        print("📊 Dashboard: /dashboard")
        print("💡 Verifique o painel do Railway para a URL real")
    
    print()
    
    # Comando de inicialização CORRIGIDO
    port = os.getenv("PORT", 8000)
    cmd = [
        "python", "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ]
    
    print(f"🎯 Comando: {' '.join(cmd)}")
    print("🚀 Iniciando servidor...")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Parando Claudia Cobranças...")
    except Exception as e:
        print(f"❌ Erro ao iniciar: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()