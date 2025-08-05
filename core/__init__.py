#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulos Core do Blacktemplar Bolter
Sistema independente com funcionalidades essenciais para produção
"""

# Importações principais
from .whatsapp_client import WhatsAppClient
from .excel_processor import ExcelProcessor
from .conversation import SuperConversationEngine
from .stealth_sender import StealthSender

# Novos módulos independentes - FUNCIONALIDADES REAIS
from .captcha_solver import CaptchaSolver, solve_recaptcha, get_captcha_solver_info
from .fatura_downloader import FaturaDownloader, baixar_fatura_rapido
from .storage_manager import StorageManager, storage_manager

# Sistema de logging essencial
from .logger import logger, BlacktemplarLogger

__all__ = [
    # Core original
    'WhatsAppClient',
    'ExcelProcessor', 
    'SuperConversationEngine',
    'StealthSender',
    
    # Novos módulos independentes - FUNCIONAIS
    'CaptchaSolver',
    'FaturaDownloader',
    'StorageManager',
    'storage_manager',
    'solve_recaptcha',
    'baixar_fatura_rapido',
    'get_captcha_solver_info',
    
    # Sistema essencial
    'logger',
    'BlacktemplarLogger'
]

# Informações do módulo
__version__ = "2.2.0"
__description__ = "Blacktemplar Bolter - SuperBot de Cobrança 100% Funcional"
__features__ = [
    "WhatsApp Web Integration",
    "Excel Processing",
    "Intelligent Conversation Engine", 
    "Stealth Sending",
    "Anti-Captcha System (REAL)",
    "Automatic Invoice Download (REAL)",
    "Smart Storage Management",
    "Railway Optimized",
    "100% Free"
]

# Status das funcionalidades
CAPTCHA_SOLVER_AVAILABLE = True
FATURA_DOWNLOADER_AVAILABLE = True
STORAGE_MANAGER_AVAILABLE = True
PRODUCTION_READY = True