#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulos Core do Claudia Cobranças
Sistema oficial de cobrança da Desktop
ULTRA STEALTH - Sistema Ultra-Robusto Anti-Detecção
"""

# Importar módulos principais
from .excel_processor import ExcelProcessor
from .whatsapp_client import WhatsAppClient
from .conversation import SuperConversationEngine
from .fatura_downloader import FaturaDownloader
from .captcha_solver import CaptchaSolver, get_captcha_solver_info
from .logger import logger, ClaudiaLogger
from .storage_manager import StorageManager, storage_manager
from .ultra_stealth_sender import UltraStealthSender

# Lista de módulos disponíveis
__all__ = [
    # Processadores
    'ExcelProcessor',
    
    # Clientes
    'WhatsAppClient',
    
    # Engines
    'SuperConversationEngine',
    
    # Downloaders
    'FaturaDownloader',
    
    # Solvers
    'CaptchaSolver',
    'get_captcha_solver_info',
    
    # Logging
    'logger',
    'ClaudiaLogger',
    
    # Storage
    'StorageManager',
    'storage_manager',
    
    # 🚀 ULTRA STEALTH
    'UltraStealthSender'
]

# Informações do módulo
__version__ = "2.2"
__author__ = "Desktop"
__description__ = "Claudia Cobranças - Sistema oficial de cobrança da Desktop"

# Lista de funcionalidades
__features__ = [
    "Sistema de Cobrança Inteligente",
    "Download Automático de Faturas",
    "Anti-Captcha Avançado",
    "Conversação Nível ChatGPT",
    "Sistema de Login Seguro",
    "Smart Storage Management",
    "🚀 ULTRA STEALTH SENDER",
    "🤖 Simulação Humana Avançada",
    "🛡️ Proteção Anti-Bloqueio",
    "🛑 Controle de Fim de Lista",
    "🎲 Comportamento Aleatório",
    "Railway Optimized",
    "100% Funcional"
]

# Status das funcionalidades
CAPTCHA_SOLVER_AVAILABLE = True
FATURA_DOWNLOADER_AVAILABLE = True
STORAGE_MANAGER_AVAILABLE = True
ULTRA_STEALTH_AVAILABLE = True
PRODUCTION_READY = True

# Log de inicialização
logger.info("🚀 Claudia Cobranças - Módulos Core carregados com sucesso!")
logger.info(f"📦 Versão: {__version__}")
logger.info(f"🏢 Empresa: {__author__}")
logger.info(f"✨ Funcionalidades: {len(__features__)} disponíveis")
logger.info("🛡️ ULTRA STEALTH SENDER ativo - Proteção máxima!")