#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - Lazy Imports
Carregamento lazy de módulos para otimização
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Verificar disponibilidade de módulos
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.warning("⚠️ Pandas não disponível")

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    logger.warning("⚠️ OpenPyXL não disponível")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("⚠️ Requests não disponível")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️ psutil não disponível")

try:
    import playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("⚠️ playwright não disponível")

try:
    import speech_recognition
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    logger.warning("⚠️ speech_recognition não disponível")

# Status de disponibilidade
MODULE_STATUS = {
    "pandas": PANDAS_AVAILABLE,
    "openpyxl": OPENPYXL_AVAILABLE,
    "requests": REQUESTS_AVAILABLE,
    "psutil": PSUTIL_AVAILABLE,
    "playwright": PLAYWRIGHT_AVAILABLE,
    "speech_recognition": SPEECH_AVAILABLE
}

class LazyExcelProcessor:
    """Processador Excel com carregamento lazy"""
    
    def __init__(self):
        self._processor = None
    
    def _load_processor(self):
        """Carregar processador se necessário"""
        if self._processor is None:
            try:
                from .excel_processor import ExcelProcessor
                self._processor = ExcelProcessor()
                logger.info("✅ Excel Processor carregado")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar Excel Processor: {e}")
                raise
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Processar arquivo Excel"""
        self._load_processor()
        return self._processor.process_file(file_path)
    
    def get_available_methods(self) -> Dict[str, Any]:
        """Obter métodos disponíveis"""
        if self._processor is None:
            return {"error": "Excel Processor não disponível"}
        return {"methods": ["process_file", "validate_file", "extract_data"]}

class LazyConversationEngine:
    """Engine de conversação com carregamento lazy"""
    
    def __init__(self):
        self._engine = None
    
    def _load_engine(self):
        """Carregar engine se necessário"""
        if self._engine is None:
            try:
                from .conversation import SuperConversationEngine
                self._engine = SuperConversationEngine()
                logger.info("✅ Conversation Engine carregado")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar Conversation Engine: {e}")
                raise
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Processar mensagem"""
        self._load_engine()
        return self._engine.process_message(message)
    
    def get_available_methods(self) -> Dict[str, Any]:
        """Obter métodos disponíveis"""
        if self._engine is None:
            return {"error": "Conversation Engine não disponível"}
        return {"methods": ["process_message", "analyze_intent", "generate_response"]}

class LazyFaturaDownloader:
    """Downloader de faturas com carregamento lazy"""
    
    def __init__(self):
        self._downloader = None
    
    def _load_downloader(self):
        """Carregar downloader se necessário"""
        if self._downloader is None:
            try:
                from .fatura_downloader import FaturaDownloader
                self._downloader = FaturaDownloader()
                logger.info("✅ Fatura Downloader carregado")
            except Exception as e:
                logger.error(f"❌ Erro ao carregar Fatura Downloader: {e}")
                raise
    
    def download_fatura(self, cpf: str, periodo: str) -> Dict[str, Any]:
        """Download de fatura"""
        self._load_downloader()
        return self._downloader.download_fatura(cpf, periodo)
    
    def get_available_methods(self) -> Dict[str, Any]:
        """Obter métodos disponíveis"""
        if self._downloader is None:
            return {"error": "Fatura Downloader não disponível"}
        return {"methods": ["download_fatura", "validate_cpf", "check_periodo"]}

# Instâncias lazy
lazy_excel_processor = LazyExcelProcessor()
lazy_conversation_engine = LazyConversationEngine()
lazy_fatura_downloader = LazyFaturaDownloader()

def get_module_status() -> Dict[str, bool]:
    """Obter status de todos os módulos"""
    return MODULE_STATUS.copy()

def check_dependencies() -> Dict[str, Any]:
    """Verificar dependências do sistema"""
    return {
        "core_modules": {
            "excel_processor": lazy_excel_processor.get_available_methods(),
            "conversation_engine": lazy_conversation_engine.get_available_methods(),
            "fatura_downloader": lazy_fatura_downloader.get_available_methods()
        },
        "dependencies": MODULE_STATUS,
        "status": "ready" if all(MODULE_STATUS.values()) else "missing_dependencies"
    }
