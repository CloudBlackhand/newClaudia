#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações centralizadas do sistema
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Classe base de configuração"""
    
    # Configurações da aplicação
    APP_NAME = os.getenv('APP_NAME', 'Sistema de Cobrança Inteligente')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-me')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Configurações do servidor
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    
    # Configurações do WhatsApp (Waha)
    WAHA_BASE_URL = os.getenv('WAHA_BASE_URL', 'http://localhost:3000')
    WAHA_SESSION_NAME = os.getenv('WAHA_SESSION_NAME', 'default')
    WAHA_WEBHOOK_URL = os.getenv('WAHA_WEBHOOK_URL', '')
    WAHA_API_KEY = os.getenv('WAHA_API_KEY', '')
    
    # Configurações de segurança
    API_KEY = os.getenv('API_KEY', '')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
    
    # Configurações de logs
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # Configurações do sistema de cobrança
    MAX_RETRY_ATTEMPTS = int(os.getenv('MAX_RETRY_ATTEMPTS', 3))
    RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', 5))
    MESSAGE_RATE_LIMIT = int(os.getenv('MESSAGE_RATE_LIMIT', 10))
    
    # Configurações da IA
    AI_CONFIDENCE_THRESHOLD = float(os.getenv('AI_CONFIDENCE_THRESHOLD', 0.8))
    AI_MODEL_VERSION = os.getenv('AI_MODEL_VERSION', '1.0')
    AI_LEARNING_ENABLED = os.getenv('AI_LEARNING_ENABLED', 'True').lower() == 'true'
    
    # Diretórios
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validar configurações obrigatórias"""
        errors = []
        warnings = []
        
        # Verificar configurações obrigatórias
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-key-change-me':
            errors.append("SECRET_KEY deve ser definida com um valor seguro")
        
        if not cls.API_KEY:
            warnings.append("API_KEY não definida - autenticação desabilitada")
        
        if not cls.WEBHOOK_SECRET:
            warnings.append("WEBHOOK_SECRET não definido - webhooks sem validação")
        
        if not cls.WAHA_BASE_URL:
            errors.append("WAHA_BASE_URL deve ser definida")
        
        if not cls.WAHA_API_KEY:
            warnings.append("WAHA_API_KEY não definida - autenticação Waha desabilitada")
        
        return {
            'errors': errors,
            'warnings': warnings,
            'valid': len(errors) == 0
        }
    
    @classmethod
    def get_waha_config(cls) -> Dict[str, str]:
        """Obter configurações do Waha"""
        return {
            'base_url': cls.WAHA_BASE_URL,
            'session_name': cls.WAHA_SESSION_NAME,
            'webhook_url': cls.WAHA_WEBHOOK_URL,
            'api_key': cls.WAHA_API_KEY
        }
    
    @classmethod
    def get_ai_config(cls) -> Dict[str, Any]:
        """Obter configurações da IA"""
        return {
            'confidence_threshold': cls.AI_CONFIDENCE_THRESHOLD,
            'model_version': cls.AI_MODEL_VERSION,
            'learning_enabled': cls.AI_LEARNING_ENABLED
        }

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    LOG_LEVEL = 'INFO'

class TestingConfig(Config):
    """Configurações para testes"""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = 'DEBUG'

def get_config() -> Config:
    """Obter configuração baseada no ambiente"""
    env = os.getenv('FLASK_ENV', 'production').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return config_map.get(env, ProductionConfig)
