#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER - Claudia Cobranças
Sistema de logging simplificado para Railway
"""

import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Criar logger principal
logger = logging.getLogger('claudia_cobrancas')

class ClaudiaLogger:
    """Logger personalizado para Claudia Cobranças"""
    
    def __init__(self, name: str = "claudia"):
        self.logger = logging.getLogger(name)
        self.start_time = time.time()
    
    def info(self, message: str, **kwargs):
        """Log de informação"""
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso"""
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log de erro"""
        self.logger.error(message)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self.logger.debug(message)
    
    def performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log de métrica de performance"""
        self.logger.info(f"PERFORMANCE: {metric_name} = {value}{unit}")
    
    def security_event(self, event_type: str, details: Dict[str, Any]):
        """Log de evento de segurança"""
        self.logger.warning(f"SECURITY: {event_type} - {details}")
    
    def user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log de ação do usuário"""
        self.logger.info(f"USER: {user_id} - {action}")
    
    def system_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log de evento do sistema"""
        self.logger.info(f"SYSTEM: {event_type}")

# Instância global do logger
claudia_logger = ClaudiaLogger()

# Funções de conveniência
def performance_metric(metric_name: str, value: float, unit: str = "ms"):
    """Log de métrica de performance"""
    claudia_logger.performance_metric(metric_name, value, unit)

def security_event(event_type: str, details: Dict[str, Any]):
    """Log de evento de segurança"""
    claudia_logger.security_event(event_type, details)

def user_action(user_id: str, action: str, details: Dict[str, Any] = None):
    """Log de ação do usuário"""
    claudia_logger.user_action(user_id, action, details)

def system_event(event_type: str, details: Dict[str, Any] = None):
    """Log de evento do sistema"""
    claudia_logger.system_event(event_type, details)

# Configurar logger para diferentes módulos
def get_logger(name: str) -> ClaudiaLogger:
    """Obter logger para um módulo específico"""
    return ClaudiaLogger(name)

# Log de inicialização
logger.info("🚀 Sistema de logging Claudia Cobranças inicializado!") 