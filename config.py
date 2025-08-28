#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - Sistema de Cobrança da Desktop
Configurações Específicas para Railway
Otimizado para custos baixos e performance adequada
"""

import os

# Configurações da Claudia Cobranças
CLAUDIA_CONFIG = {
    'name': 'Claudia Cobranças',
    'company': 'Desktop',
    'version': '2.2',
    'description': 'Sistema oficial de cobrança da Desktop',
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
        self.CONCURRENT_DOWNLOADS = 1 if self.RAILWAY_DEPLOY else 3
        self.CACHE_TTL = 3600 if self.RAILWAY_DEPLOY else 1800
        
        # Playwright config (otimizado)
        self.PLAYWRIGHT_CONFIG = {
            'headless': True,
            'timeout': 90000 if self.RAILWAY_DEPLOY else 60000,
            'max_retries': 2 if self.RAILWAY_DEPLOY else 3,
            'wait_for_download': 5 if self.RAILWAY_DEPLOY else 10
        }
        
        # Downloader config
        self.DOWNLOADER_CONFIG = {
            'headless': True,
            'timeout': 30000,
            'max_retries': 2,  # Reduzido para Railway
            'wait_for_download': 5,  # Reduzido para Railway
            'sac_url': 'https://sac.desktop.com.br/Cliente_Documento.jsp'
        }
        
        # WAHA config (WhatsApp HTTP API)
        self.WAHA_CONFIG = {
            'url': os.getenv('WAHA_URL', 'http://localhost:3000'),
            'instance_name': 'claudia-cobrancas',
            'webhook_url': os.getenv('WEBHOOK_URL', ''),
            'timeout': 30000 if self.RAILWAY_DEPLOY else 60000,
            'max_retries': 3,
            'auto_reconnect': True
        }
        
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

# Classe Config para compatibilidade
class Config:
    """Classe de configuração para compatibilidade"""
    def __init__(self):
        self.PORT = railway_config.PORT
        self.RAILWAY_MODE = railway_config.RAILWAY_DEPLOY
        self.PLAYWRIGHT_CONFIG = railway_config.PLAYWRIGHT_CONFIG
        self.DOWNLOADER_CONFIG = railway_config.DOWNLOADER_CONFIG
        self.WHATSAPP_CONFIG = railway_config.WHATSAPP_CONFIG
        self.LOG_LEVEL = railway_config.LOG_LEVEL
        self.ENABLE_DETAILED_LOGS = railway_config.ENABLE_DETAILED_LOGS

# Exportar configurações principais
PORT = railway_config.PORT
RAILWAY_MODE = railway_config.RAILWAY_DEPLOY
PLAYWRIGHT_CONFIG = railway_config.PLAYWRIGHT_CONFIG