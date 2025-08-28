#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Instalação Otimizado para Railway
Instala apenas as dependências essenciais para o sistema básico
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_requirements():
    """Instalar dependências essenciais"""
    logger.info("🚀 Instalando dependências essenciais...")
    
    # Lista de dependências essenciais
    essential_packages = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "python-multipart==0.0.6",
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "python-dotenv==1.0.0"
    ]
    
    # Instalar psutil se possível (para monitoramento)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil==5.9.6"])
        logger.info("✅ psutil instalado")
    except:
        logger.warning("⚠️ psutil não instalado - monitoramento limitado")
    
    # Instalar dependências essenciais
    for package in essential_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✅ {package} instalado")
        except Exception as e:
            logger.error(f"❌ Erro ao instalar {package}: {e}")
            return False
    
    return True

def install_optional_packages():
    """Instalar pacotes opcionais se necessário"""
    logger.info("📦 Instalando pacotes opcionais...")
    
    # Verificar se é necessário instalar pandas/openpyxl
    railway_mode = os.getenv('RAILWAY_DEPLOY', 'False') == 'True'
    
    if not railway_mode:
        # Modo desenvolvimento - instalar tudo
        optional_packages = [
            "pandas==2.1.3",
            "openpyxl==3.1.2",
            "playwright==1.40.0",
            "SpeechRecognition==3.10.0"
        ]
        
        for package in optional_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                logger.info(f"✅ {package} instalado")
            except Exception as e:
                logger.warning(f"⚠️ {package} não instalado: {e}")
    else:
        # Modo Railway - instalar apenas se necessário
        logger.info("🚂 Modo Railway - pacotes opcionais não instalados")

def create_directories():
    """Criar diretórios necessários"""
    logger.info("📁 Criando diretórios...")
    
    directories = [
        "uploads",
        "faturas", 
        "logs",
        "temp",
        "web/static"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"✅ Diretório criado: {directory}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar {directory}: {e}")

def main():
    """Função principal"""
    logger.info("🔧 Iniciando instalação otimizada para Railway...")
    
    # Criar diretórios
    create_directories()
    
    # Instalar dependências essenciais
    if not install_requirements():
        logger.error("❌ Falha na instalação de dependências essenciais")
        sys.exit(1)
    
    # Instalar pacotes opcionais
    install_optional_packages()
    
    logger.info("✅ Instalação concluída com sucesso!")
    logger.info("🚀 Sistema pronto para execução")

if __name__ == "__main__":
    main()
