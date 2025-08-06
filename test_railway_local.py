#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Local do Ambiente Railway
"""

import os
import subprocess
import time
import requests

def test_railway_environment():
    """Testar ambiente Railway localmente"""
    print("🚀 Testando ambiente Railway localmente...")
    
    # Configurar variáveis de ambiente como Railway
    os.environ['PORT'] = '8000'
    os.environ['HOST'] = '0.0.0.0'
    
    print(f"📊 PORT: {os.getenv('PORT')}")
    print(f"🌐 HOST: {os.getenv('HOST')}")
    
    # Testar se app_test.py funciona
    print("\n🔍 Testando app_test.py...")
    try:
        # Iniciar app em background
        process = subprocess.Popen([
            "python", "-m", "uvicorn", "app_test:app", 
            "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguardar um pouco para inicializar
        time.sleep(3)
        
        # Testar endpoints
        base_url = "http://localhost:8000"
        
        print("\n🧪 Testando endpoints...")
        
        # Testar healthcheck
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            print(f"✅ /health: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ /health: {e}")
        
        # Testar root
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print(f"✅ /: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ /: {e}")
        
        # Testar test endpoint
        try:
            response = requests.get(f"{base_url}/test", timeout=5)
            print(f"✅ /test: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"❌ /test: {e}")
        
        # Parar processo
        process.terminate()
        process.wait()
        
        print("\n✅ Teste local concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def check_dockerfile():
    """Verificar Dockerfile"""
    print("\n🐳 Verificando Dockerfile...")
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
            print("✅ Dockerfile encontrado")
            print(f"📄 Tamanho: {len(content)} caracteres")
            
            if "app_test:app" in content:
                print("✅ Usando app_test:app")
            else:
                print("❌ Não está usando app_test:app")
                
    except Exception as e:
        print(f"❌ Erro ao ler Dockerfile: {e}")

def check_requirements():
    """Verificar requirements"""
    print("\n📦 Verificando requirements...")
    
    try:
        with open("requirements_minimal.txt", "r") as f:
            content = f.read()
            print("✅ requirements_minimal.txt encontrado")
            print(f"📄 Conteúdo:\n{content}")
            
    except Exception as e:
        print(f"❌ Erro ao ler requirements: {e}")

def check_railway_config():
    """Verificar configuração Railway"""
    print("\n🚂 Verificando railway.toml...")
    
    try:
        with open("railway.toml", "r") as f:
            content = f.read()
            print("✅ railway.toml encontrado")
            print(f"📄 Conteúdo:\n{content}")
            
    except Exception as e:
        print(f"❌ Erro ao ler railway.toml: {e}")

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO RAILWAY LOCAL")
    print("=" * 50)
    
    check_dockerfile()
    check_requirements()
    check_railway_config()
    test_railway_environment()
    
    print("\n" + "=" * 50)
    print("✅ Diagnóstico concluído!") 