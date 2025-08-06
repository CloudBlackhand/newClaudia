#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start Script - Claudia Cobranças
Script simples e robusto para Railway
"""

import os
import sys
import subprocess
import time

def main():
    """Inicialização simples"""
    print("🚀 Iniciando Claudia Cobranças...")
    
    # Verificar se estamos no Railway
    railway_mode = os.getenv("RAILWAY_DEPLOY", "False") == "True"
    port = os.getenv("PORT", "8000")
    
    print(f"🔧 Modo Railway: {railway_mode}")
    print(f"🌐 Porta: {port}")
    
    # Verificar Node.js (opcional)
    try:
        print("🔍 Verificando Node.js...")
        node_result = subprocess.run(["node", "--version"], 
                                   capture_output=True, text=True, timeout=10)
        if node_result.returncode == 0:
            print(f"✅ Node.js disponível: {node_result.stdout.strip()}")
        else:
            print("⚠️ Node.js não encontrado (não crítico)")
    except Exception as e:
        print(f"⚠️ Erro ao verificar Node.js: {e}")
    
    # Instalar Playwright se necessário (com timeout e retry)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"📦 Instalando Playwright (tentativa {attempt + 1}/{max_retries})...")
            
            # Instalar Playwright com timeout
            subprocess.run(["python", "-m", "playwright", "install", "chromium"], 
                          check=True, capture_output=True, timeout=300)
            print("✅ Playwright instalado")
            
            # Instalar dependências do sistema para Railway
            print("🔧 Instalando dependências do sistema...")
            subprocess.run(["python", "-m", "playwright", "install-deps"], 
                          check=True, capture_output=True, timeout=120)
            print("✅ Dependências do sistema instaladas")
            break
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout na tentativa {attempt + 1}")
            if attempt < max_retries - 1:
                print("🔄 Tentando novamente...")
                time.sleep(5)
            else:
                print("⚠️ Falha na instalação do Playwright - continuando...")
        except Exception as e:
            print(f"⚠️ Aviso: {e}")
            if attempt < max_retries - 1:
                print("🔄 Tentando instalação alternativa...")
                try:
                    # Fallback para Railway
                    subprocess.run(["python", "-m", "playwright", "install", "chromium", "--with-deps"], 
                                  check=True, capture_output=True, timeout=300)
                    print("✅ Playwright instalado com dependências")
                    break
                except Exception as e2:
                    print(f"⚠️ Aviso: {e2}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                    else:
                        print("⚠️ Falha na instalação alternativa - continuando...")
    
    # Criar diretórios necessários
    print("📁 Criando diretórios necessários...")
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("faturas", exist_ok=True)
    os.makedirs("web/static", exist_ok=True)
    print("✅ Diretórios criados")
    
    # Iniciar servidor com configurações otimizadas para Railway
    cmd = [
        "python", "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", port,
        "--timeout-keep-alive", "300",
        "--log-level", "info",
        "--access-log",
        "--reload", "false"  # Desabilitar reload no Railway
    ]
    
    # Configurações específicas para Railway
    if railway_mode:
        cmd.extend([
            "--workers", "1",
            "--limit-concurrency", "10",
            "--limit-max-requests", "1000",
            "--backlog", "100"
        ])
    
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