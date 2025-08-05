#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOGGER - Claudia Cobranças
Sistema de logging avançado para o sistema de cobrança
"""

import logging
import structlog
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

# Configurar structlog para logs estruturados
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

class ClaudiaLogger:
    """Logger personalizado para Claudia Cobranças"""
    
    def __init__(self, name: str = "claudia"):
        self.logger = structlog.get_logger(name)
        self.start_time = time.time()
    
    def info(self, message: str, **kwargs):
        """Log de informação"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro"""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log de debug"""
        self.logger.debug(message, **kwargs)
    
    def performance_metric(self, metric_name: str, value: float, unit: str = "ms"):
        """Log de métrica de performance"""
        self.logger.info(
            "performance_metric",
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now().isoformat()
        )
    
    def security_event(self, event_type: str, details: Dict[str, Any]):
        """Log de evento de segurança"""
        self.logger.warning(
            "security_event",
            event_type=event_type,
            details=details,
            timestamp=datetime.now().isoformat()
        )
    
    def user_action(self, user_id: str, action: str, details: Dict[str, Any] = None):
        """Log de ação do usuário"""
        self.logger.info(
            "user_action",
            user_id=user_id,
            action=action,
            details=details or {},
            timestamp=datetime.now().isoformat()
        )
    
    def system_event(self, event_type: str, details: Dict[str, Any] = None):
        """Log de evento do sistema"""
        self.logger.info(
            "system_event",
            event_type=event_type,
            details=details or {},
            timestamp=datetime.now().isoformat()
        )

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