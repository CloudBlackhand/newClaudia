#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logs Estruturados para Oracle Cloud
Logging avançado com JSON, rotação automática e métricas
"""

import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import sys

class StructuredFormatter(logging.Formatter):
    """Formatter que gera logs em JSON estruturado"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Dados base do log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": os.getpid(),
            "thread_id": record.thread
        }
        
        # Adicionar campos extras se existirem
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
            
        # Adicionar stack trace se for erro
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data, ensure_ascii=False)

class BlacktemplarLogger:
    """Sistema de logging avançado para Blacktemplar Bolter"""
    
    def __init__(self, name: str = "blacktemplar"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.metrics = {
            "messages_sent": 0,
            "errors_count": 0,
            "warnings_count": 0,
            "startup_time": time.time()
        }
        self._setup_logger()
    
    def _setup_logger(self):
        """Configurar sistema de logging"""
        # Configurações do ambiente
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        log_format = os.getenv('LOG_FORMAT', 'json').lower()
        
        # Nível de log
        self.logger.setLevel(getattr(logging, log_level))
        
        # Limpar handlers existentes
        self.logger.handlers.clear()
        
        # Criar diretório de logs
        logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Handler para arquivo (JSON estruturado)
        if log_format == 'json':
            formatter = StructuredFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Handler rotativo por tempo (diário)
        file_handler = TimedRotatingFileHandler(
            filename=os.path.join(logs_dir, 'blacktemplar.log'),
            when='midnight',
            interval=1,
            backupCount=int(os.getenv('LOG_RETENTION_DAYS', '30')),
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        if log_format == 'json':
            console_handler.setFormatter(formatter)
        else:
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
        console_handler.setLevel(logging.INFO)
        
        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Não propagar para root logger
        self.logger.propagate = False
    
    def log_with_metrics(self, level: str, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log com métricas automáticas"""
        # Atualizar métricas
        if level.upper() == 'ERROR':
            self.metrics["errors_count"] += 1
        elif level.upper() == 'WARNING':
            self.metrics["warnings_count"] += 1
            
        # Preparar dados extras
        if extra_data is None:
            extra_data = {}
            
        extra_data.update({
            "metrics": self.metrics.copy(),
            "system_uptime": time.time() - self.metrics["startup_time"]
        })
        
        # Fazer log
        record = self.logger.makeRecord(
            name=self.name,
            level=getattr(logging, level.upper()),
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )
        record.extra_data = extra_data
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs):
        """Log info com dados estruturados"""
        self.log_with_metrics('INFO', message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning com dados estruturados"""
        self.log_with_metrics('WARNING', message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error com dados estruturados"""
        self.log_with_metrics('ERROR', message, kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug com dados estruturados"""
        self.log_with_metrics('DEBUG', message, kwargs)
        
    def whatsapp_event(self, event_type: str, phone: str = "", status: str = "", **kwargs):
        """Log específico para eventos WhatsApp"""
        self.info(f"WhatsApp: {event_type}", 
                 event_type=event_type, 
                 phone=phone, 
                 status=status, 
                 category="whatsapp",
                 **kwargs)
        
    def excel_event(self, event_type: str, filename: str = "", rows_processed: int = 0, **kwargs):
        """Log específico para processamento Excel"""
        self.info(f"Excel: {event_type}",
                 event_type=event_type,
                 filename=filename,
                 rows_processed=rows_processed,
                 category="excel",
                 **kwargs)
                 
    def conversation_event(self, intent: str, phone: str = "", confidence: float = 0.0, **kwargs):
        """Log específico para conversações"""
        self.info(f"Conversação: {intent}",
                 intent=intent,
                 phone=phone,
                 confidence=confidence,
                 category="conversation",
                 **kwargs)
                 
    def performance_metric(self, operation: str, duration: float, **kwargs):
        """Log de métricas de performance"""
        self.info(f"Performance: {operation}",
                 operation=operation,
                 duration_seconds=duration,
                 category="performance",
                 **kwargs)
                 
    def security_event(self, event_type: str, risk_level: str = "low", **kwargs):
        """Log de eventos de segurança"""
        level = "WARNING" if risk_level in ["medium", "high"] else "INFO"
        self.log_with_metrics(level, f"Security: {event_type}",
                             event_type=event_type,
                             risk_level=risk_level,
                             category="security",
                             **kwargs)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obter métricas atuais"""
        self.metrics["current_time"] = time.time()
        self.metrics["uptime_seconds"] = time.time() - self.metrics["startup_time"]
        return self.metrics.copy()

# Instância global do logger
logger = BlacktemplarLogger("blacktemplar")

# Funções de conveniência
def info(message: str, **kwargs):
    logger.info(message, **kwargs)

def warning(message: str, **kwargs):
    logger.warning(message, **kwargs)

def error(message: str, **kwargs):
    logger.error(message, **kwargs)

def debug(message: str, **kwargs):
    logger.debug(message, **kwargs)

def whatsapp_event(event_type: str, **kwargs):
    logger.whatsapp_event(event_type, **kwargs)

def excel_event(event_type: str, **kwargs):
    logger.excel_event(event_type, **kwargs)

def conversation_event(intent: str, **kwargs):
    logger.conversation_event(intent, **kwargs)

def performance_metric(operation: str, duration: float, **kwargs):
    logger.performance_metric(operation, duration, **kwargs)

def security_event(event_type: str, risk_level: str = "low", **kwargs):
    logger.security_event(event_type, risk_level, **kwargs)

# Decorator para medir performance
def measure_performance(operation_name: str):
    """Decorator para medir performance de funções"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_metric(f"{operation_name}_{func.__name__}", duration, status="success")
                return result
            except Exception as e:
                duration = time.time() - start_time
                performance_metric(f"{operation_name}_{func.__name__}", duration, status="error", error=str(e))
                raise
        return wrapper
    return decorator