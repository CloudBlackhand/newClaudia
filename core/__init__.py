#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulos Core do Claudia Cobranças
Sistema oficial de cobrança da Desktop
ULTRA STEALTH - Sistema Ultra-Robusto Anti-Detecção
"""

# Importar módulos principais (apenas os essenciais)
from .excel_processor import ExcelProcessor
from .whatsapp_client import WAHAWhatsAppClient, WhatsAppClient
from .conversation import SuperConversationEngine
from .logger import logger, ClaudiaLogger
from .storage_manager import StorageManager, storage_manager

# Lista de módulos disponíveis
__all__ = [
    # Processadores
    'ExcelProcessor',
    
    # Clientes
    'WAHAWhatsAppClient',
    'WhatsAppClient',
    
    # Engines
    'SuperConversationEngine',
    
    # Logging
    'logger',
    'ClaudiaLogger',
    
    # Storage
    'StorageManager',
    'storage_manager',
]

# Informações do módulo
__version__ = "2.2"
__author__ = "Desktop"
__description__ = "Claudia Cobranças - Sistema oficial de cobrança da Desktop"

# Lista de funcionalidades
__features__ = [
    "Sistema de Cobrança Inteligente",
    "Conversação Nível ChatGPT",
    "Sistema de Login Seguro",
    "Smart Storage Management",
    "Railway Optimized",
    "Integração WAHA",
    "100% Funcional"
]

# Status das funcionalidades
STORAGE_MANAGER_AVAILABLE = True
PRODUCTION_READY = True

# Log de inicialização
logger.info("🚀 Claudia Cobranças - Módulos Core carregados com sucesso!")
logger.info(f"📦 Versão: {__version__}")
logger.info(f"🏢 Empresa: {__author__}")
logger.info(f"✨ Funcionalidades: {len(__features__)} disponíveis")
logger.info("📱 Integração WAHA ativa - Sistema otimizado para Railway!")