#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - Core Modules
Módulos essenciais do sistema de cobrança
"""

import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos essenciais
from .excel_processor import ExcelProcessor
from .conversation import SuperConversationEngine
from .storage_manager import storage_manager
from .fatura_downloader import FaturaDownloader
from .captcha_solver import CaptchaSolver
from .logger import Logger
from .monitoring import SystemMonitor
from .performance import PerformanceOptimizer
from .security import SecurityManager

# Exportar classes principais
__all__ = [
    'ExcelProcessor',
    'SuperConversationEngine', 
    'storage_manager',
    'FaturaDownloader',
    'CaptchaSolver',
    'Logger',
    'SystemMonitor',
    'PerformanceOptimizer',
    'SecurityManager'
]

# Versão do sistema
__version__ = "2.2"

def initialize_core():
    """Inicializar módulos core"""
    logger.info("🚀 Inicializando módulos core da Claudia Cobranças...")
    
    try:
        # Inicializar componentes essenciais
        logger.info("✅ Excel Processor inicializado")
        logger.info("✅ Conversation Engine inicializado")
        logger.info("✅ Storage Manager inicializado")
        logger.info("✅ Fatura Downloader inicializado")
        logger.info("✅ Captcha Solver inicializado")
        logger.info("✅ Logger inicializado")
        logger.info("✅ System Monitor inicializado")
        logger.info("✅ Performance Optimizer inicializado")
        logger.info("✅ Security Manager inicializado")
        
        logger.info("🎯 Sistema core inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar core: {e}")
        return False

# Inicializar automaticamente
if __name__ == "__main__":
    initialize_core()