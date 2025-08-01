#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações do Blacktemplar Bolter
Centralizador de todas as configurações do sistema
"""

import os
from typing import Dict, Any

class Config:
    """Classe de configuração centralizada"""
    
    def __init__(self):
        # Configurações da aplicação
        self.APP_NAME = "Blacktemplar Bolter"
        self.APP_VERSION = "1.0.0"
        self.APP_DESCRIPTION = "SuperBot de Cobrança 100% Gratuito"
        
        # Configurações do servidor
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', 8000))
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Configurações de paths
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.UPLOADS_DIR = os.path.join(self.BASE_DIR, 'uploads')
        self.FATURAS_DIR = os.path.join(self.BASE_DIR, 'faturas')
        self.SESSIONS_DIR = os.path.join(self.BASE_DIR, 'sessions')
        self.LOGS_DIR = os.path.join(self.BASE_DIR, 'logs')
        
        # Configurações WhatsApp
        self.WHATSAPP_CONFIG = {
            'session_name': 'blacktemplar_session',
            'qr_timeout': 120,  # 2 minutos
            'headless': True,  # Sempre headless para evitar abrir Safari/browsers
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Configurações do sistema stealth
        self.STEALTH_CONFIG = {
            'base_interval': 15,  # segundos entre mensagens
            'interval_variation': 0.3,  # variação de ±30%
            'batch_size': 5,
            'batch_pause': 120,  # 2 minutos entre lotes
            'daily_limit': 200,
            'hourly_limit': 30,
            'typing_simulation': True,
            'human_pauses': True
        }
        
        # Configurações do downloader
        self.DOWNLOADER_CONFIG = {
            'headless': True,
            'timeout': 30000,
            'max_retries': 3,
            'wait_for_download': 10,
            'sac_url': 'https://sac.desktop.com.br/Cliente_Documento.jsp'
        }
        
        # Configurações do anti-captcha
        self.CAPTCHA_CONFIG = {
            'max_attempts': 3,
            'audio_recognition': True,
            'manual_fallback': True,
            'manual_timeout': 60
        }
        
        # Configurações de logging
        self.LOGGING_CONFIG = {
            'level': 'INFO' if not self.DEBUG else 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_enabled': True,
            'console_enabled': True
        }
        
        # Configurações da empresa (personalizáveis)
        self.COMPANY_CONFIG = {
            'name': 'Desktop Tecnologia',
            'phone': '(19) 3511-5800',
            'whatsapp': '(19) 99999-9999',
            'website': 'https://desktop.com.br',
            'sac_website': 'https://sac.desktop.com.br',
            'email': 'atendimento@desktop.com.br',
            'assistant_name': 'Claudia'
        }
        
        # Configurações de deploy
        self.DEPLOY_CONFIG = {
            'oracle_cloud_ready': True,
            'railway_compatible': True,
            'render_compatible': True,
            'heroku_compatible': True,
            'dockerfile_included': True
        }
        
        # Criar diretórios necessários
        self._create_directories()
    
    def _create_directories(self):
        """Criar diretórios necessários"""
        directories = [
            self.UPLOADS_DIR,
            self.FATURAS_DIR,
            self.SESSIONS_DIR,
            self.LOGS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_public_config(self) -> Dict[str, Any]:
        """Obter configurações públicas (sem informações sensíveis)"""
        return {
            'app': {
                'name': self.APP_NAME,
                'version': self.APP_VERSION,
                'description': self.APP_DESCRIPTION
            },
            'company': self.COMPANY_CONFIG,
            'features': {
                'whatsapp_web': True,
                'anti_captcha': True,
                'stealth_mode': True,
                'excel_processing': True,
                'auto_fatura_download': True,
                'conversation_engine': True,
                'burst_message_detection': True
            },
            'limits': {
                'daily_messages': self.STEALTH_CONFIG['daily_limit'],
                'hourly_messages': self.STEALTH_CONFIG['hourly_limit'],
                'batch_size': self.STEALTH_CONFIG['batch_size']
            }
        }
    
    def update_stealth_config(self, new_config: Dict[str, Any]):
        """Atualizar configurações stealth"""
        for key, value in new_config.items():
            if key in self.STEALTH_CONFIG:
                self.STEALTH_CONFIG[key] = value
    
    def update_company_config(self, new_config: Dict[str, Any]):
        """Atualizar configurações da empresa"""
        for key, value in new_config.items():
            if key in self.COMPANY_CONFIG:
                self.COMPANY_CONFIG[key] = value
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Obter informações do ambiente"""
        return {
            'platform': os.name,
            'debug_mode': self.DEBUG,
            'host': self.HOST,
            'port': self.PORT,
            'base_dir': self.BASE_DIR,
            'python_version': os.sys.version,
            'environment_variables': {
                'PORT': os.getenv('PORT'),
                'DEBUG': os.getenv('DEBUG'),
                'HOST': os.getenv('HOST')
            }
        } 