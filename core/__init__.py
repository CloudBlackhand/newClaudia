#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - Core Modules
Módulos essenciais do bot de conversação
"""

import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulo essencial
from .conversation import SuperConversationEngine

# Exportar classe principal
__all__ = [
    'SuperConversationEngine'
]

# Versão do sistema
__version__ = "2.2"

def initialize_core():
    """Inicializar módulos core"""
    logger.info("🚀 Inicializando bot de conversação Claudia Cobranças...")
    
    try:
        # Inicializar engine de conversação
        logger.info("✅ Conversation Engine inicializado")
        
        logger.info("🎯 Bot de conversação inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar core: {e}")
        return False

# Inicializar automaticamente
if __name__ == "__main__":
    initialize_core()