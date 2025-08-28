#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Instalação Otimizado para Railway
Instala apenas as dependências essenciais para o bot de conversação
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
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "python-dotenv==1.0.0"
    ]
    
    # Instalar dependências essenciais
    for package in essential_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✅ {package} instalado")
        except Exception as e:
            logger.error(f"❌ Erro ao instalar {package}: {e}")
            return False
    
    return True

def create_directories():
    """Criar diretórios necessários"""
    logger.info("📁 Criando diretórios...")
    
    directories = [
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
    
    logger.info("✅ Instalação concluída com sucesso!")
    logger.info("🚀 Bot de conversação pronto para execução")

if __name__ == "__main__":
    main()
