#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - Bot de Conversação
Configurações específicas para Railway
Otimizado para bot de conversação inteligente
"""

import os

# Configurações da Claudia Cobranças
CLAUDIA_CONFIG = {
    'name': 'Claudia Cobranças',
    'company': 'Desktop',
    'version': '2.2',
    'description': 'Bot inteligente de conversação da Desktop',
    'website': 'https://sac.desktop.com.br/Cliente_Documento.jsp',
    'support_email': 'cobranca@desktop.com.br'
}

class RailwayConfig:
    """Configurações otimizadas para Railway"""
    
    def __init__(self):
        # Detecção de ambiente
        self.RAILWAY_DEPLOY = os.getenv('RAILWAY_DEPLOY', 'False') == 'True'
        self.PORT = int(os.getenv('PORT', 8000))
        
        # Configurações de recursos (conservadoras)
        self.MAX_WORKERS = 1 if self.RAILWAY_DEPLOY else 4
        self.CONCURRENT_REQUESTS = 1 if self.RAILWAY_DEPLOY else 3
        self.CACHE_TTL = 3600 if self.RAILWAY_DEPLOY else 1800
        
        # Logging (minimal para Railway)
        self.LOG_LEVEL = 'WARNING' if self.RAILWAY_DEPLOY else 'INFO'
        self.ENABLE_DETAILED_LOGS = not self.RAILWAY_DEPLOY
        
        # Performance (railway-specific)
        if self.RAILWAY_DEPLOY:
            self.ENABLE_CACHING = True
            self.ENABLE_COMPRESSION = True
            self.MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
        else:
            self.ENABLE_CACHING = False
            self.ENABLE_COMPRESSION = False
            self.MAX_REQUEST_SIZE = 50 * 1024 * 1024  # 50MB
            
    def get_railway_optimizations(self):
        """Retorna otimizações específicas para Railway"""
        if not self.RAILWAY_DEPLOY:
            return {}
            
        return {
            'gc_threshold': (700, 10, 10),  # Garbage collection agressivo
            'max_memory_usage': 0.8,  # 80% max RAM usage
            'cpu_throttle': True,
            'minimal_logging': True,
            'compress_responses': True
        }
    
    def get_cost_control_settings(self):
        """Configurações para controle de custos"""
        return {
            'max_concurrent_requests': 5 if self.RAILWAY_DEPLOY else 20,
            'request_timeout': 30 if self.RAILWAY_DEPLOY else 60,
            'max_file_size': 5 * 1024 * 1024 if self.RAILWAY_DEPLOY else 20 * 1024 * 1024,
            'enable_request_limiting': self.RAILWAY_DEPLOY,
            'sleep_inactive_time': 300 if self.RAILWAY_DEPLOY else 0  # 5min sleep
        }

# Instância global
railway_config = RailwayConfig()

class Config:
    """Configuração principal do sistema"""
    
    def __init__(self):
        self.railway_config = railway_config
        self.claudia_config = CLAUDIA_CONFIG
        
        # Configurações básicas
        self.DEBUG = os.getenv('DEBUG', 'False') == 'True'
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'claudia-cobrancas-secret-key')
        
        # Configurações de sessão
        self.SESSION_TIMEOUT = 3600  # 1 hora
        self.REQUEST_TIMEOUT = 300   # 5 minutos