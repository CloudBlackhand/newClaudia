"""
Integração com Waha - WhatsApp API
Sistema para receber webhooks e enviar mensagens via Waha
"""
import aiohttp
import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging
from urllib.parse import urljoin

from .logger_system import LoggerSystem
from .conversation_bot import ConversationBot
from config.settings import settings

logger = logging.getLogger(__name__)

class WahaIntegration:
    """Integração completa com Waha para WhatsApp"""
    
    def __init__(self, logger_system: LoggerSystem, conversation_bot: ConversationBot):
        self.logger_system = logger_system
        self.conversation_bot = conversation_bot
        self.base_url = settings.waha_base_url
        self.session_name = settings.waha_session
        self.api_key = settings.waha_api_key
        self.is_initialized = False
        
        # Session HTTP reutilizável
        self.http_session: Optional[aiohttp.ClientSession] = None
        
        # Callbacks para diferentes tipos de webhook
        self.webhook_handlers: Dict[str, Callable] = {}
        
        # Status da conexão
        self.connection_status = "disconnected"
        self.last_health_check = None
        
    async def initialize(self):
        """Inicializar integração com Waha"""
        try:
            logger.info("Inicializando WahaIntegration...")
            
            # Criar sessão HTTP
            timeout = aiohttp.ClientTimeout(total=30)
            self.http_session = aiohttp.ClientSession(timeout=timeout)
            
            # Configurar headers padrão
            self.default_headers = {
                "Content-Type": "application/json"
            }
            
            if self.api_key:
                self.default_headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Registrar handlers de webhook
            self._register_webhook_handlers()
            
            # Verificar conexão com Waha (se configurado)
            if self.base_url:
                await self._check_waha_connection()
            
            self.is_initialized = True
            logger.info("WahaIntegration inicializada com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar WahaIntegration: {str(e)}")
            raise
    
    async def cleanup(self):
        """Limpeza da integração"""
        if self.http_session:
            await self.http_session.close()
        
        self.is_initialized = False
        logger.info("WahaIntegration finalizada")
    
    def is_healthy(self) -> bool:
        """Verificação de saúde"""
        return self.is_initialized and self.connection_status == "connected"
    
    def _register_webhook_handlers(self):
        """Registrar handlers para diferentes tipos de webhook"""
        self.webhook_handlers = {
            "message": self._handle_message_webhook,
            "message.any": self._handle_message_webhook,
            "message.text": self._handle_text_message,
            "session.status": self._handle_session_status,
            "state.change": self._handle_state_change,
            "qr": self._handle_qr_code,
            "ready": self._handle_ready,
            "auth_failure": self._handle_auth_failure
        }
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processar webhook recebido do Waha
        
        Args:
            webhook_data: Dados do webhook
            
        Returns:
            Resultado do processamento
        """
        try:
            # Log do webhook recebido
            await self.logger_system.log_webhook_received(
                webhook_data.get("event", "unknown"), 
                webhook_data
            )
            
            event_type = webhook_data.get("event", "")
            
            # Encontrar handler apropriado
            handler = self.webhook_handlers.get(event_type)
            if not handler:
                # Tentar handler genérico para mensagens
                if "message" in event_type:
                    handler = self.webhook_handlers.get("message")
            
            if handler:
                result = await handler(webhook_data)
                return {"success": True, "result": result}
            else:
                logger.warning(f"Handler não encontrado para evento: {event_type}")
                return {"success": False, "error": f"Handler não encontrado: {event_type}"}
            
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _handle_message_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler genérico para mensagens"""
        try:
            payload = webhook_data.get("payload", {})
            
            # Extrair informações da mensagem
            from_number = payload.get("from", "")
            message_body = payload.get("body", "")
            message_type = payload.get("type", "text")
            
            # Ignorar mensagens próprias
            if payload.get("fromMe", False):
                return {"ignored": True, "reason": "own_message"}
            
            # Processar apenas mensagens de texto por agora
            if message_type == "text" and message_body:
                return await self._handle_text_message(webhook_data)
            
            return {"processed": False, "reason": f"unsupported_message_type: {message_type}"}
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_text_message(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler específico para mensagens de texto"""
        try:
            payload = webhook_data.get("payload", {})
            
            from_number = payload.get("from", "")
            message_body = payload.get("body", "")
            
            if not from_number or not message_body:
                return {"error": "Dados insuficientes na mensagem"}
            
            # Limpar número de telefone
            clean_number = self._clean_phone_number(from_number)
            
            # Processar mensagem com o bot
            bot_response = await self.conversation_bot.process_message(
                user_phone=clean_number,
                message=message_body,
                context={}
            )
            
            # Enviar resposta
            if bot_response.message:
                send_result = await self.send_message(clean_number, bot_response.message)
                
                return {
                    "processed": True,
                    "user_phone": clean_number,
                    "user_message": message_body,
                    "bot_response": bot_response.message,
                    "send_result": send_result,
                    "requires_human": bot_response.requires_human
                }
            
            return {"processed": False, "reason": "no_bot_response"}
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem de texto: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_session_status(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para status da sessão"""
        try:
            payload = webhook_data.get("payload", {})
            status = payload.get("status", "")
            
            self.connection_status = status
            
            logger.info(f"Status da sessão Waha: {status}")
            
            return {"status_updated": True, "new_status": status}
            
        except Exception as e:
            logger.error(f"Erro ao processar status da sessão: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_state_change(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para mudança de estado"""
        try:
            payload = webhook_data.get("payload", {})
            state = payload.get("state", "")
            
            logger.info(f"Mudança de estado Waha: {state}")
            
            if state == "CONNECTED":
                self.connection_status = "connected"
            elif state == "DISCONNECTED":
                self.connection_status = "disconnected"
            
            return {"state_changed": True, "new_state": state}
            
        except Exception as e:
            logger.error(f"Erro ao processar mudança de estado: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_qr_code(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para QR Code"""
        try:
            payload = webhook_data.get("payload", {})
            qr_code = payload.get("qr", "")
            
            logger.info("QR Code recebido para autenticação WhatsApp")
            
            # Aqui você pode implementar lógica para exibir o QR code
            # Por exemplo, salvar em arquivo ou enviar para frontend
            
            return {"qr_received": True, "qr_length": len(qr_code)}
            
        except Exception as e:
            logger.error(f"Erro ao processar QR code: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_ready(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para quando WhatsApp está pronto"""
        try:
            self.connection_status = "connected"
            logger.info("WhatsApp está pronto e conectado!")
            
            return {"ready": True}
            
        except Exception as e:
            logger.error(f"Erro ao processar evento ready: {str(e)}")
            return {"error": str(e)}
    
    async def _handle_auth_failure(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para falha de autenticação"""
        try:
            self.connection_status = "auth_failed"
            logger.error("Falha na autenticação do WhatsApp")
            
            return {"auth_failed": True}
            
        except Exception as e:
            logger.error(f"Erro ao processar falha de auth: {str(e)}")
            return {"error": str(e)}
    
    async def send_message(self, to_number: str, message: str) -> Dict[str, Any]:
        """
        Enviar mensagem via Waha
        
        Args:
            to_number: Número de destino
            message: Mensagem a ser enviada
            
        Returns:
            Resultado do envio
        """
        try:
            if not self.base_url:
                # Simular envio para desenvolvimento
                logger.info(f"Simulando envio para {to_number}: {message[:50]}...")
                return {
                    "success": True,
                    "message_id": f"sim_{datetime.now().timestamp()}",
                    "simulated": True
                }
            
            # Preparar dados da mensagem
            clean_number = self._clean_phone_number(to_number)
            
            message_data = {
                "chatId": f"{clean_number}@c.us",
                "text": message
            }
            
            # URL para envio de mensagem
            url = urljoin(self.base_url, f"/api/{self.session_name}/sendText")
            
            # Enviar mensagem
            async with self.http_session.post(
                url,
                json=message_data,
                headers=self.default_headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    logger.info(f"Mensagem enviada com sucesso para {clean_number}")
                    
                    return {
                        "success": True,
                        "message_id": result.get("id"),
                        "response": result
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Erro ao enviar mensagem: {response.status} - {error_text}")
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
            
        except aiohttp.ClientError as e:
            logger.error(f"Erro de conexão ao enviar mensagem: {str(e)}")
            return {
                "success": False,
                "error": f"Erro de conexão: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar mensagem: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_session_status(self) -> Dict[str, Any]:
        """Obter status da sessão Waha"""
        try:
            if not self.base_url:
                return {
                    "status": "simulated",
                    "connected": True,
                    "session": self.session_name
                }
            
            url = urljoin(self.base_url, f"/api/{self.session_name}/status")
            
            async with self.http_session.get(url, headers=self.default_headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "status": "error",
                        "error": f"HTTP {response.status}"
                    }
            
        except Exception as e:
            logger.error(f"Erro ao obter status da sessão: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_waha_connection(self):
        """Verificar conexão com Waha"""
        try:
            status = await self.get_session_status()
            
            if status.get("status") == "WORKING":
                self.connection_status = "connected"
                logger.info("Conexão com Waha verificada com sucesso")
            else:
                self.connection_status = "disconnected"
                logger.warning(f"Waha não está conectado: {status}")
            
            self.last_health_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com Waha: {str(e)}")
            self.connection_status = "error"
    
    def _clean_phone_number(self, phone: str) -> str:
        """Limpar e normalizar número de telefone"""
        # Remover caracteres especiais
        clean = "".join(char for char in phone if char.isdigit() or char == "+")
        
        # Garantir formato brasileiro
        if clean.startswith("55") and len(clean) == 13:
            clean = "+" + clean
        elif clean.startswith("55") and len(clean) == 12:
            clean = "+" + clean
        elif len(clean) == 11 and not clean.startswith("+"):
            clean = "+55" + clean
        elif len(clean) == 10 and not clean.startswith("+"):
            clean = "+55" + clean
        
        return clean
    
    async def send_bulk_messages(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Enviar múltiplas mensagens em lote
        
        Args:
            messages: Lista de {"to": "number", "message": "text"}
            
        Returns:
            Resultado do envio em lote
        """
        try:
            total_messages = len(messages)
            successful_sends = 0
            failed_sends = 0
            results = []
            
            # Enviar em lotes para não sobrecarregar
            batch_size = 5
            
            for i in range(0, total_messages, batch_size):
                batch = messages[i:i + batch_size]
                
                # Enviar lote com delay
                batch_results = await asyncio.gather(
                    *[self.send_message(msg["to"], msg["message"]) for msg in batch],
                    return_exceptions=True
                )
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        failed_sends += 1
                        results.append({"success": False, "error": str(result)})
                    elif result.get("success"):
                        successful_sends += 1
                        results.append(result)
                    else:
                        failed_sends += 1
                        results.append(result)
                
                # Delay entre lotes para evitar rate limiting
                if i + batch_size < total_messages:
                    await asyncio.sleep(1)
            
            return {
                "total_messages": total_messages,
                "successful_sends": successful_sends,
                "failed_sends": failed_sends,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Erro no envio em lote: {str(e)}")
            return {
                "total_messages": len(messages),
                "successful_sends": 0,
                "failed_sends": len(messages),
                "error": str(e)
            }
    
    async def get_integration_stats(self) -> Dict[str, Any]:
        """Obter estatísticas da integração"""
        return {
            "is_initialized": self.is_initialized,
            "connection_status": self.connection_status,
            "base_url": self.base_url,
            "session_name": self.session_name,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "has_api_key": bool(self.api_key)
        }
