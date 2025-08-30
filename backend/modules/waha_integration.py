#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração com Waha (WhatsApp HTTP API)
Módulo para comunicação com WhatsApp via Waha
"""

import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import time

from backend.modules.logger_system import LogManager, LogCategory
from backend.config.settings import Config

logger = LogManager.get_logger('waha_integration')

class MessageType(Enum):
    """Tipos de mensagem suportados pelo Waha"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    CONTACT = "contact"

class SessionStatus(Enum):
    """Status da sessão do WhatsApp"""
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    SCAN_QR_CODE = "SCAN_QR_CODE"
    WORKING = "WORKING"
    FAILED = "FAILED"

@dataclass
class WahaMessage:
    """Estrutura de mensagem do Waha"""
    id: str
    timestamp: int
    from_me: bool
    sender: str
    chat_id: str
    message_type: str
    content: str
    reply_to: Optional[str] = None

@dataclass
class WahaSession:
    """Informações da sessão Waha"""
    name: str
    status: SessionStatus
    config: Dict[str, Any]
    me: Optional[Dict[str, str]] = None

class WahaIntegration:
    """Cliente para integração com Waha"""
    
    def __init__(self, base_url: str = None, session_name: str = None):
        self.base_url = base_url or Config.WAHA_BASE_URL
        self.session_name = session_name or Config.WAHA_SESSION_NAME
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Cache de status
        self._session_status = None
        self._last_status_check = 0
        self._status_cache_duration = 30  # segundos
        
        logger.info(LogCategory.WHATSAPP, f"Waha Integration inicializada - URL: {self.base_url}")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self.start_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_session()
    
    async def start_session(self):
        """Inicializar sessão HTTP"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            logger.debug(LogCategory.WHATSAPP, "Sessão HTTP iniciada")
    
    async def close_session(self):
        """Fechar sessão HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.debug(LogCategory.WHATSAPP, "Sessão HTTP fechada")
    
    async def _make_request(self, method: str, endpoint: str, 
                          data: Optional[Dict[str, Any]] = None,
                          params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Fazer requisição para a API do Waha"""
        if not self.session:
            await self.start_session()
        
        url = f"{self.base_url.rstrip('/')}/api/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                
                # Log da requisição
                logger.debug(LogCategory.WHATSAPP, 
                           f"Waha Request: {method} {url}",
                           details={
                               'status': response.status,
                               'data': data,
                               'params': params
                           })
                
                if response.status == 200:
                    result = await response.json()
                    return True, result
                else:
                    error_text = await response.text()
                    logger.error(LogCategory.WHATSAPP, 
                               f"Waha API Error: {response.status}",
                               details={'error': error_text, 'url': url})
                    return False, None
                    
        except aiohttp.ClientError as e:
            logger.error(LogCategory.WHATSAPP, f"Erro de conexão com Waha: {e}")
            return False, None
        except Exception as e:
            logger.error(LogCategory.WHATSAPP, f"Erro inesperado na requisição Waha: {e}")
            return False, None
    
    async def get_session_status(self, force_refresh: bool = False) -> Optional[SessionStatus]:
        """Obter status da sessão do WhatsApp"""
        now = time.time()
        
        # Usar cache se não forçar refresh e cache válido
        if not force_refresh and self._session_status and (now - self._last_status_check) < self._status_cache_duration:
            return self._session_status
        
        success, data = await self._make_request('GET', f'/sessions/{self.session_name}')
        
        if success and data:
            status_str = data.get('status', 'FAILED')
            try:
                self._session_status = SessionStatus(status_str)
                self._last_status_check = now
                
                logger.debug(LogCategory.WHATSAPP, f"Status da sessão: {status_str}")
                return self._session_status
            except ValueError:
                logger.warning(LogCategory.WHATSAPP, f"Status desconhecido: {status_str}")
                return SessionStatus.FAILED
        
        return None
    
    async def start_whatsapp_session(self) -> bool:
        """Iniciar sessão do WhatsApp"""
        session_config = {
            'name': self.session_name,
            'config': {
                'webhooks': [
                    {
                        'url': Config.WAHA_WEBHOOK_URL,
                        'events': ['message']
                    }
                ] if Config.WAHA_WEBHOOK_URL else []
            }
        }
        
        success, data = await self._make_request('POST', '/sessions/start', session_config)
        
        if success:
            logger.info(LogCategory.WHATSAPP, f"Sessão WhatsApp iniciada: {self.session_name}")
            return True
        else:
            logger.error(LogCategory.WHATSAPP, f"Falha ao iniciar sessão WhatsApp: {self.session_name}")
            return False
    
    async def stop_whatsapp_session(self) -> bool:
        """Parar sessão do WhatsApp"""
        success, data = await self._make_request('POST', f'/sessions/{self.session_name}/stop')
        
        if success:
            logger.info(LogCategory.WHATSAPP, f"Sessão WhatsApp parada: {self.session_name}")
            return True
        else:
            logger.error(LogCategory.WHATSAPP, f"Falha ao parar sessão WhatsApp: {self.session_name}")
            return False
    
    async def get_qr_code(self) -> Optional[str]:
        """Obter QR code para autenticação"""
        success, data = await self._make_request('GET', f'/sessions/{self.session_name}/auth/qr')
        
        if success and data:
            qr_code = data.get('qr')
            if qr_code:
                logger.info(LogCategory.WHATSAPP, "QR Code obtido com sucesso")
                return qr_code
        
        logger.warning(LogCategory.WHATSAPP, "QR Code não disponível")
        return None
    
    async def send_text_message(self, phone: str, text: str, 
                               reply_to: Optional[str] = None) -> bool:
        """Enviar mensagem de texto"""
        # Normalizar número de telefone
        clean_phone = self._normalize_phone(phone)
        
        message_data = {
            'session': self.session_name,
            'chatId': clean_phone,
            'text': text
        }
        
        if reply_to:
            message_data['reply_to'] = reply_to
        
        success, data = await self._make_request('POST', '/sendText', message_data)
        
        if success:
            logger.info(LogCategory.WHATSAPP, 
                       f"Mensagem enviada para {clean_phone}",
                       details={
                           'message_length': len(text),
                           'reply_to': reply_to
                       })
            return True
        else:
            logger.error(LogCategory.WHATSAPP, f"Falha ao enviar mensagem para {clean_phone}")
            return False
    
    async def send_image_message(self, phone: str, image_url: str, 
                                caption: Optional[str] = None) -> bool:
        """Enviar mensagem com imagem"""
        clean_phone = self._normalize_phone(phone)
        
        message_data = {
            'session': self.session_name,
            'chatId': clean_phone,
            'file': {
                'url': image_url
            }
        }
        
        if caption:
            message_data['file']['caption'] = caption
        
        success, data = await self._make_request('POST', '/sendImage', message_data)
        
        if success:
            logger.info(LogCategory.WHATSAPP, f"Imagem enviada para {clean_phone}")
            return True
        else:
            logger.error(LogCategory.WHATSAPP, f"Falha ao enviar imagem para {clean_phone}")
            return False
    
    async def send_document_message(self, phone: str, document_url: str, 
                                   filename: Optional[str] = None) -> bool:
        """Enviar documento"""
        clean_phone = self._normalize_phone(phone)
        
        message_data = {
            'session': self.session_name,
            'chatId': clean_phone,
            'file': {
                'url': document_url
            }
        }
        
        if filename:
            message_data['file']['filename'] = filename
        
        success, data = await self._make_request('POST', '/sendFile', message_data)
        
        if success:
            logger.info(LogCategory.WHATSAPP, f"Documento enviado para {clean_phone}")
            return True
        else:
            logger.error(LogCategory.WHATSAPP, f"Falha ao enviar documento para {clean_phone}")
            return False
    
    async def get_chats(self) -> List[Dict[str, Any]]:
        """Obter lista de chats"""
        success, data = await self._make_request('GET', f'/sessions/{self.session_name}/chats')
        
        if success and data:
            chats = data.get('chats', [])
            logger.debug(LogCategory.WHATSAPP, f"Chats obtidos: {len(chats)}")
            return chats
        
        logger.warning(LogCategory.WHATSAPP, "Falha ao obter chats")
        return []
    
    async def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[WahaMessage]:
        """Obter mensagens de um chat"""
        params = {
            'chatId': chat_id,
            'limit': limit
        }
        
        success, data = await self._make_request('GET', f'/sessions/{self.session_name}/chats/{chat_id}/messages', params=params)
        
        if success and data:
            messages = []
            for msg_data in data.get('messages', []):
                try:
                    message = WahaMessage(
                        id=msg_data.get('id', ''),
                        timestamp=msg_data.get('timestamp', 0),
                        from_me=msg_data.get('fromMe', False),
                        sender=msg_data.get('from', ''),
                        chat_id=msg_data.get('chatId', ''),
                        message_type=msg_data.get('type', 'text'),
                        content=msg_data.get('body', ''),
                        reply_to=msg_data.get('quotedMsgId')
                    )
                    messages.append(message)
                except Exception as e:
                    logger.warning(LogCategory.WHATSAPP, f"Erro ao processar mensagem: {e}")
            
            logger.debug(LogCategory.WHATSAPP, f"Mensagens obtidas do chat {chat_id}: {len(messages)}")
            return messages
        
        logger.warning(LogCategory.WHATSAPP, f"Falha ao obter mensagens do chat {chat_id}")
        return []
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalizar número de telefone para formato do WhatsApp"""
        # Remover caracteres especiais
        clean = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se necessário
        if len(clean) == 11 and clean.startswith('11'):
            clean = '55' + clean
        elif len(clean) == 10:
            clean = '5511' + clean
        elif not clean.startswith('55'):
            clean = '55' + clean
        
        # Formato final para WhatsApp
        return clean + '@c.us'
    
    def parse_webhook_message(self, webhook_data: Dict[str, Any]) -> Optional[WahaMessage]:
        """Parsear mensagem recebida via webhook"""
        try:
            payload = webhook_data.get('payload', {})
            
            message = WahaMessage(
                id=payload.get('id', ''),
                timestamp=payload.get('timestamp', 0),
                from_me=payload.get('fromMe', False),
                sender=payload.get('from', ''),
                chat_id=payload.get('chatId', ''),
                message_type=payload.get('type', 'text'),
                content=payload.get('body', ''),
                reply_to=payload.get('quotedMsgId')
            )
            
            logger.debug(LogCategory.WHATSAPP, 
                       f"Mensagem webhook parseada: {message.sender}",
                       details={
                           'type': message.message_type,
                           'from_me': message.from_me,
                           'content_preview': message.content[:50] + '...' if len(message.content) > 50 else message.content
                       })
            
            return message
            
        except Exception as e:
            logger.error(LogCategory.WHATSAPP, f"Erro ao parsear webhook: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Verificar saúde da conexão com Waha"""
        success, data = await self._make_request('GET', '/health')
        
        if success:
            logger.debug(LogCategory.WHATSAPP, "Waha health check: OK")
            return True
        else:
            logger.warning(LogCategory.WHATSAPP, "Waha health check: FAILED")
            return False
