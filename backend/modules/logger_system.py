#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Avançado de Logs
Monitoramento e registro detalhado de operações
"""

import os
import json
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    """Níveis de log personalizados"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    TRACE = 5

class LogCategory(Enum):
    """Categorias de logs para melhor organização"""
    SYSTEM = "system"
    BILLING = "billing"
    CONVERSATION = "conversation"
    WHATSAPP = "whatsapp"
    VALIDATION = "validation"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class LogEntry:
    """Estrutura de entrada de log"""
    timestamp: str
    level: str
    category: str
    message: str
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    execution_time: Optional[float] = None
    stack_trace: Optional[str] = None

class JSONFormatter(logging.Formatter):
    """Formatador JSON para logs estruturados"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adicionar informações extras se disponíveis
        if hasattr(record, 'category'):
            log_entry['category'] = record.category
        if hasattr(record, 'details'):
            log_entry['details'] = record.details
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        
        # Adicionar stack trace se for erro
        if record.exc_info:
            log_entry['stack_trace'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)

class ColoredFormatter(logging.Formatter):
    """Formatador colorido para console"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formatar timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Formatar categoria se disponível
        category = f"[{getattr(record, 'category', 'GENERAL')}]"
        
        # Montar mensagem colorida
        formatted = f"{color}{timestamp} {record.levelname:8} {category:12} {record.getMessage()}{reset}"
        
        # Adicionar detalhes se disponíveis
        if hasattr(record, 'details') and record.details:
            formatted += f"\n{color}Details: {json.dumps(record.details, indent=2, ensure_ascii=False)}{reset}"
        
        return formatted

class SmartLogger:
    """Logger inteligente com funcionalidades avançadas"""
    
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        self._setup_logger()
        
        # Contadores de performance
        self.stats = {
            'total_logs': 0,
            'errors': 0,
            'warnings': 0,
            'start_time': datetime.now()
        }
    
    def _setup_logger(self):
        """Configurar logger com handlers múltiplos"""
        self.logger.setLevel(logging.DEBUG)
        
        # Remover handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Criar diretório de logs
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Handler para arquivo JSON (logs estruturados)
        json_handler = RotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}.json"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        json_handler.setFormatter(JSONFormatter())
        json_handler.setLevel(logging.INFO)
        
        # Handler para arquivo de texto (logs legíveis)
        text_handler = TimedRotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}.log"),
            when='midnight',
            interval=1,
            backupCount=30
        )
        text_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        text_handler.setLevel(logging.DEBUG)
        
        # Handler para console (desenvolvimento)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter())
        console_handler.setLevel(logging.INFO)
        
        # Handler para erros críticos
        error_handler = RotatingFileHandler(
            os.path.join(self.log_dir, "errors.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10
        )
        error_handler.setFormatter(JSONFormatter())
        error_handler.setLevel(logging.ERROR)
        
        # Adicionar handlers
        self.logger.addHandler(json_handler)
        self.logger.addHandler(text_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
    
    def log(self, level: LogLevel, category: LogCategory, message: str, 
            details: Optional[Dict[str, Any]] = None, **kwargs):
        """Log personalizado com categorias e detalhes"""
        
        # Atualizar estatísticas
        self.stats['total_logs'] += 1
        if level == LogLevel.ERROR:
            self.stats['errors'] += 1
        elif level == LogLevel.WARNING:
            self.stats['warnings'] += 1
        
        # Criar record personalizado
        record = self.logger.makeRecord(
            self.logger.name, level.value, __file__, 0, message, (), None
        )
        
        # Adicionar atributos extras
        record.category = category.value
        if details:
            record.details = details
        
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        # Enviar para handlers
        self.logger.handle(record)
    
    def debug(self, category: LogCategory, message: str, **kwargs):
        """Log de debug"""
        self.log(LogLevel.DEBUG, category, message, **kwargs)
    
    def info(self, category: LogCategory, message: str, **kwargs):
        """Log de informação"""
        self.log(LogLevel.INFO, category, message, **kwargs)
    
    def warning(self, category: LogCategory, message: str, **kwargs):
        """Log de aviso"""
        self.log(LogLevel.WARNING, category, message, **kwargs)
    
    def error(self, category: LogCategory, message: str, **kwargs):
        """Log de erro"""
        self.log(LogLevel.ERROR, category, message, **kwargs)
    
    def critical(self, category: LogCategory, message: str, **kwargs):
        """Log crítico"""
        self.log(LogLevel.CRITICAL, category, message, **kwargs)
    
    def billing_event(self, event_type: str, client_id: str, details: Dict[str, Any]):
        """Log específico para eventos de cobrança"""
        self.info(
            LogCategory.BILLING,
            f"Evento de cobrança: {event_type}",
            details={
                'event_type': event_type,
                'client_id': client_id,
                **details
            }
        )
    
    def conversation_event(self, phone: str, direction: str, message: str, ai_response: bool = False):
        """Log específico para conversas"""
        self.info(
            LogCategory.CONVERSATION,
            f"Mensagem {direction}",
            details={
                'phone': phone,
                'direction': direction,
                'message_preview': message[:100] + '...' if len(message) > 100 else message,
                'ai_response': ai_response,
                'message_length': len(message)
            }
        )
    
    def security_event(self, event_type: str, severity: str, details: Dict[str, Any]):
        """Log específico para eventos de segurança"""
        level = LogLevel.CRITICAL if severity == 'high' else LogLevel.WARNING
        self.log(
            level,
            LogCategory.SECURITY,
            f"Evento de segurança: {event_type}",
            details={
                'event_type': event_type,
                'severity': severity,
                **details
            }
        )
    
    def performance_metric(self, operation: str, execution_time: float, details: Dict[str, Any] = None):
        """Log específico para métricas de performance"""
        self.info(
            LogCategory.PERFORMANCE,
            f"Métrica de performance: {operation}",
            details={
                'operation': operation,
                'execution_time': execution_time,
                'performance_category': 'slow' if execution_time > 1.0 else 'normal',
                **(details or {})
            },
            execution_time=execution_time
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do logger"""
        uptime = (datetime.now() - self.stats['start_time']).total_seconds()
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'logs_per_minute': (self.stats['total_logs'] / uptime) * 60 if uptime > 0 else 0,
            'error_rate': (self.stats['errors'] / self.stats['total_logs']) * 100 if self.stats['total_logs'] > 0 else 0
        }

class LogManager:
    """Gerenciador central de logs"""
    
    _loggers: Dict[str, SmartLogger] = {}
    
    @classmethod
    def get_logger(cls, name: str) -> SmartLogger:
        """Obter ou criar logger"""
        if name not in cls._loggers:
            cls._loggers[name] = SmartLogger(name)
        return cls._loggers[name]
    
    @classmethod
    def get_all_stats(cls) -> Dict[str, Any]:
        """Obter estatísticas de todos os loggers"""
        return {
            name: logger.get_stats() 
            for name, logger in cls._loggers.items()
        }
    
    @classmethod
    def shutdown(cls):
        """Fechar todos os loggers"""
        for logger in cls._loggers.values():
            for handler in logger.logger.handlers:
                handler.close()

# Instâncias globais para uso comum
app_logger = LogManager.get_logger('app')
billing_logger = LogManager.get_logger('billing')
conversation_logger = LogManager.get_logger('conversation')
security_logger = LogManager.get_logger('security')
