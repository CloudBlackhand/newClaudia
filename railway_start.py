#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Start Script - Claudia Cobranças
Script otimizado especificamente para Railway
"""

import os
import sys
import subprocess
import time
import signal
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    """Handler para sinais de interrupção"""
    logger.info("🛑 Recebido sinal de interrupção, encerrando...")
    sys.exit(0)

def check_dependencies():
    """Verificar dependências críticas"""
    logger.info("🔍 Verificando dependências...")
    
    # Verificar Python
    try:
        import fastapi
        import uvicorn
        logger.info("✅ FastAPI e Uvicorn disponíveis")
    except ImportError as e:
        logger.error(f"❌ Erro: {e}")
        return False
    
    # Verificar Playwright (opcional)
    try:
        import playwright
        logger.info("✅ Playwright disponível")
    except ImportError:
        logger.warning("⚠️ Playwright não disponível (será instalado)")
    
    return True

def install_playwright():
    """Instalar Playwright com retry"""
    logger.info("📦 Instalando Playwright...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Instalar Playwright
            result = subprocess.run(
                ["python", "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✅ Playwright instalado com sucesso")
                
                # Instalar dependências do sistema
                deps_result = subprocess.run(
                    ["python", "-m", "playwright", "install-deps"],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if deps_result.returncode == 0:
                    logger.info("✅ Dependências do sistema instaladas")
                    return True
                else:
                    logger.warning("⚠️ Falha ao instalar dependências do sistema")
            else:
                logger.warning(f"⚠️ Falha na instalação do Playwright: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ Timeout na tentativa {attempt + 1}")
        except Exception as e:
            logger.warning(f"⚠️ Erro na tentativa {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            logger.info("🔄 Tentando novamente...")
            time.sleep(5)
    
    logger.warning("⚠️ Falha na instalação do Playwright - continuando...")
    return False

def create_directories():
    """Criar diretórios necessários"""
    logger.info("📁 Criando diretórios...")
    
    directories = [
        "uploads",
        "faturas", 
        "web/static",
        "logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Diretório {directory} criado/verificado")
        except Exception as e:
            logger.error(f"❌ Erro ao criar diretório {directory}: {e}")

def start_server():
    """Iniciar servidor FastAPI"""
    port = os.getenv("PORT", "8000")
    railway_mode = os.getenv("RAILWAY_DEPLOY", "False") == "True"
    
    logger.info(f"🚀 Iniciando servidor na porta {port}")
    logger.info(f"🔧 Modo Railway: {railway_mode}")
    
    # Configuração do servidor
    cmd = [
        "python", "-m", "uvicorn",
        "app:app",
        "--host", "0.0.0.0",
        "--port", port,
        "--timeout-keep-alive", "300",
        "--log-level", "info"
    ]
    
    # Configurações específicas para Railway
    if railway_mode:
        cmd.extend([
            "--workers", "1",
            "--limit-concurrency", "10",
            "--limit-max-requests", "1000"
        ])
    
    try:
        logger.info(f"🎯 Comando: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
        sys.exit(0)

def main():
    """Função principal"""
    logger.info("🚀 Iniciando Claudia Cobranças no Railway...")
    
    # Configurar handler de sinais
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verificar dependências
    if not check_dependencies():
        logger.error("❌ Dependências críticas não encontradas")
        sys.exit(1)
    
    # Criar diretórios
    create_directories()
    
    # Instalar Playwright (opcional)
    install_playwright()
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()