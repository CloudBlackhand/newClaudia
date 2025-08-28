#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente WAHA (WhatsApp HTTP API) Integrado
Sistema WhatsApp via API HTTP - Compatível com Railway
"""

import asyncio
import logging
import time
import json
import os
from typing import Optional, Dict, Any, List
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class WAHAWhatsAppClient:
    """Cliente WhatsApp via WAHA (WhatsApp HTTP API)"""
    
    def __init__(self, waha_url: str = None):
        # URL padrão para Railway - deve ser configurada via variável de ambiente
        default_url = os.getenv('WAHA_URL', 'https://waha-claudia.up.railway.app')
        self.waha_url = waha_url or default_url
        self.session = requests.Session()
        self.is_connected = False
        self.instance_id = None
        self.qr_code_data = None
        self.message_queue = []
        self.last_message_time = 0
        self.message_count = 0
        
    async def initialize(self, phone_number: str = None, code: str = None) -> Optional[str]:
        """Inicializar instância WAHA com código e número"""
        try:
            logger.info("🚀 Inicializando WAHA WhatsApp...")
            
            # Criar instância WAHA
            instance_data = {
                "instanceName": "claudia-cobrancas",
                "webhook": f"{self.waha_url}/webhook",
                "webhookByEvents": False,
                "webhookBase64": False
            }
            
            response = self.session.post(
                f"{self.waha_url}/api/instances/create",
                json=instance_data
            )
            
            if response.status_code == 200:
                self.instance_id = "claudia-cobrancas"
                logger.info(f"✅ Instância WAHA criada: {self.instance_id}")
            else:
                logger.error(f"❌ Erro ao criar instância: {response.text}")
            return None
            
            # Iniciar instância
            start_response = self.session.post(
                f"{self.waha_url}/api/instances/{self.instance_id}/start"
            )
            
            if start_response.status_code == 200:
                logger.info("✅ Instância WAHA iniciada")
            else:
                logger.error(f"❌ Erro ao iniciar instância: {start_response.text}")
                return None
            
            # Se fornecido código e número, conectar diretamente
            if phone_number and code:
                logger.info(f"📱 Conectando com número: {phone_number}")
                
                # Enviar código de verificação
                code_data = {
                    "code": code,
                    "phoneNumber": phone_number
                }
                
                code_response = self.session.post(
                    f"{self.waha_url}/api/instances/{self.instance_id}/auth/verify",
                    json=code_data
                )
                
                if code_response.status_code == 200:
                    logger.info("✅ Código verificado, WhatsApp conectado")
                    self.is_connected = True
                    return "CONNECTED"
                else:
                    logger.error(f"❌ Erro ao verificar código: {code_response.text}")
            return None
            
            # Verificar se já está conectado
            info_response = self.session.get(
                f"{self.waha_url}/api/instances/{self.instance_id}/info"
            )
            
            if info_response.status_code == 200:
                info = info_response.json()
                if info.get('status') == 'qr':
                    logger.info("✅ WhatsApp já conectado")
                    self.is_connected = True
                    return "CONNECTED"
                else:
                    logger.info("📱 Aguardando conexão...")
                    return "WAITING_CONNECTION"
            else:
                logger.error(f"❌ Erro ao verificar status: {info_response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar WAHA: {e}")
            return None
    
    async def check_connection(self) -> bool:
        """Verificar se está conectado"""
        try:
            if not self.instance_id:
                return False
                
            response = self.session.get(
                f"{self.waha_url}/api/instances/{self.instance_id}/info"
            )
            
            if response.status_code == 200:
                info = response.json()
                self.is_connected = info.get('status') == 'qr'
                return self.is_connected
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar conexão: {e}")
            return False
    
    async def send_message(self, phone: str, message: str) -> bool:
        """Enviar mensagem via WAHA"""
        try:
            if not self.is_connected:
                logger.error("❌ WhatsApp não conectado")
                return False
            
            # Formatar número de telefone
            phone = self._format_phone(phone)
            
            message_data = {
                "chatId": f"{phone}@c.us",
                "text": message
            }
            
            response = self.session.post(
                f"{self.waha_url}/api/instances/{self.instance_id}/messages/sendText",
                json=message_data
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Mensagem enviada para {phone}")
                self.message_count += 1
                self.last_message_time = time.time()
                return True
            else:
                logger.error(f"❌ Erro ao enviar mensagem: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    async def send_media(self, phone: str, file_path: str, caption: str = "") -> bool:
        """Enviar mídia via WAHA"""
        try:
            if not self.is_connected:
                logger.error("❌ WhatsApp não conectado")
                return False
            
            phone = self._format_phone(phone)
            
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'chatId': f"{phone}@c.us",
                    'caption': caption
                }
                
                response = self.session.post(
                    f"{self.waha_url}/api/instances/{self.instance_id}/messages/sendFile",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                logger.info(f"✅ Mídia enviada para {phone}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar mídia: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mídia: {e}")
            return False
    
    async def get_messages(self) -> List[Dict]:
        """Obter mensagens recebidas"""
        try:
            if not self.instance_id:
                return []
            
            response = self.session.get(
                f"{self.waha_url}/api/instances/{self.instance_id}/messages"
            )
            
            if response.status_code == 200:
                messages = response.json()
                return messages.get('messages', [])
            else:
                logger.error(f"❌ Erro ao obter mensagens: {response.text}")
                return []
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter mensagens: {e}")
            return []
    
    def _format_phone(self, phone: str) -> str:
        """Formatar número de telefone"""
        # Remover caracteres especiais
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se necessário
        if phone.startswith('0'):
            phone = phone[1:]
        if not phone.startswith('55'):
            phone = '55' + phone
            
        return phone
    
    async def disconnect(self):
        """Desconectar instância WAHA"""
        try:
            if self.instance_id:
                response = self.session.delete(
                    f"{self.waha_url}/api/instances/{self.instance_id}"
                )
                if response.status_code == 200:
                    logger.info("✅ Instância WAHA desconectada")
                else:
                    logger.error(f"❌ Erro ao desconectar: {response.text}")
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status do cliente"""
        return {
            "connected": self.is_connected,
            "instance_id": self.instance_id,
            "message_count": self.message_count,
            "last_message_time": self.last_message_time,
            "waha_url": self.waha_url
        }

# Alias para compatibilidade
WhatsAppClient = WAHAWhatsAppClient