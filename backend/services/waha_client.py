"""
Cliente para integração com Waha (WhatsApp HTTP API)
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from backend.config.settings import active_config
from backend.utils.logger import waha_logger, app_logger
from backend.utils.validators import MessageValidator

class WahaClient:
    """Cliente para comunicação com API Waha"""
    
    def __init__(self):
        self.config = active_config
        self.base_url = self.config.WAHA_BASE_URL.rstrip('/')
        self.api_key = self.config.WAHA_API_KEY
        self.session_name = self.config.WAHA_SESSION_NAME
        self.timeout = aiohttp.ClientTimeout(total=30)
        
    async def send_text_message(self, phone: str, message: str) -> Dict[str, Any]:
        """Envia mensagem de texto via Waha"""
        result = {"success": False, "message_id": None, "error": None}
        
        try:
            # Valida mensagem
            validation = MessageValidator.validate_message_content(message)
            if not validation["valid"]:
                result["error"] = f"Mensagem inválida: {'; '.join(validation['errors'])}"
                return result
            
            # Prepara payload
            payload = {
                "chatId": phone,
                "text": message,
                "session": self.session_name
            }
            
            # Envia mensagem
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/api/sendText"
                headers = self._get_headers()
                
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        result["success"] = True
                        result["message_id"] = response_data.get("id")
                        
                        waha_logger.api_call(
                            endpoint="/api/sendText",
                            method="POST",
                            success=True,
                            status_code=response.status
                        )
                    else:
                        result["error"] = response_data.get("error", f"HTTP {response.status}")
                        
                        waha_logger.api_call(
                            endpoint="/api/sendText",
                            method="POST",
                            success=False,
                            status_code=response.status,
                            error=result["error"]
                        )
        
        except asyncio.TimeoutError:
            result["error"] = "Timeout ao enviar mensagem"
            waha_logger.error("MESSAGE_SEND_TIMEOUT", data={"phone": phone})
            
        except Exception as e:
            result["error"] = f"Erro interno: {str(e)}"
            waha_logger.error("MESSAGE_SEND_ERROR", e, {"phone": phone})
        
        return result
    
    async def send_template_message(self, phone: str, template_name: str, variables: Dict[str, str]) -> Dict[str, Any]:
        """Envia mensagem usando template"""
        result = {"success": False, "message_id": None, "error": None}
        
        try:
            payload = {
                "chatId": phone,
                "template": {
                    "name": template_name,
                    "language": {"code": "pt_BR"},
                    "components": self._build_template_components(variables)
                },
                "session": self.session_name
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/api/sendTemplate"
                headers = self._get_headers()
                
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        result["success"] = True
                        result["message_id"] = response_data.get("id")
                    else:
                        result["error"] = response_data.get("error", f"HTTP {response.status}")
        
        except Exception as e:
            result["error"] = f"Erro ao enviar template: {str(e)}"
            waha_logger.error("TEMPLATE_SEND_ERROR", e, {
                "phone": phone,
                "template": template_name
            })
        
        return result
    
    async def get_session_status(self) -> Dict[str, Any]:
        """Verifica status da sessão Waha"""
        result = {"success": False, "status": None, "error": None}
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/api/sessions/{self.session_name}"
                headers = self._get_headers()
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        result["success"] = True
                        result["status"] = data.get("status")
                        result["data"] = data
                    else:
                        result["error"] = f"HTTP {response.status}"
        
        except Exception as e:
            result["error"] = f"Erro ao verificar sessão: {str(e)}"
            waha_logger.error("SESSION_STATUS_ERROR", e)
        
        return result
    
    async def start_session(self) -> Dict[str, Any]:
        """Inicia sessão Waha"""
        result = {"success": False, "error": None}
        
        try:
            payload = {
                "name": self.session_name,
                "config": {
                    "webhooks": [
                        {
                            "url": self.config.WAHA_WEBHOOK_URL,
                            "events": ["message", "message.any", "state.change"]
                        }
                    ]
                }
            }
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/api/sessions"
                headers = self._get_headers()
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status in [200, 201]:
                        result["success"] = True
                        waha_logger.info("SESSION_STARTED", {"session": self.session_name})
                    else:
                        data = await response.json()
                        result["error"] = data.get("error", f"HTTP {response.status}")
        
        except Exception as e:
            result["error"] = f"Erro ao iniciar sessão: {str(e)}"
            waha_logger.error("SESSION_START_ERROR", e)
        
        return result
    
    async def stop_session(self) -> Dict[str, Any]:
        """Para sessão Waha"""
        result = {"success": False, "error": None}
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/api/sessions/{self.session_name}/stop"
                headers = self._get_headers()
                
                async with session.post(url, headers=headers) as response:
                    if response.status == 200:
                        result["success"] = True
                        waha_logger.info("SESSION_STOPPED", {"session": self.session_name})
                    else:
                        result["error"] = f"HTTP {response.status}"
        
        except Exception as e:
            result["error"] = f"Erro ao parar sessão: {str(e)}"
            waha_logger.error("SESSION_STOP_ERROR", e)
        
        return result
    
    async def get_qr_code(self) -> Dict[str, Any]:
        """Obtém QR code para autenticação"""
        result = {"success": False, "qr_code": None, "error": None}
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{self.base_url}/api/sessions/{self.session_name}/auth/qr"
                headers = self._get_headers()
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        result["success"] = True
                        result["qr_code"] = data.get("qr")
                    else:
                        result["error"] = f"HTTP {response.status}"
        
        except Exception as e:
            result["error"] = f"Erro ao obter QR code: {str(e)}"
            waha_logger.error("QR_CODE_ERROR", e)
        
        return result
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers
    
    def _build_template_components(self, variables: Dict[str, str]) -> List[Dict]:
        """Constrói componentes para template do WhatsApp"""
        components = []
        
        if variables:
            parameters = []
            for key, value in variables.items():
                parameters.append({
                    "type": "text",
                    "text": str(value)
                })
            
            components.append({
                "type": "body",
                "parameters": parameters
            })
        
        return components

class WahaWebhookHandler:
    """Handler para webhooks recebidos da Waha"""
    
    def __init__(self):
        self.message_handlers = []
        self.status_handlers = []
    
    def add_message_handler(self, handler):
        """Adiciona handler para mensagens"""
        self.message_handlers.append(handler)
    
    def add_status_handler(self, handler):
        """Adiciona handler para mudanças de status"""
        self.status_handlers.append(handler)
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa webhook recebido"""
        result = {"success": False, "processed": False, "error": None}
        
        try:
            event_type = webhook_data.get("event")
            
            waha_logger.webhook_received(event_type, webhook_data)
            
            if event_type in ["message", "message.any"]:
                await self._handle_message_event(webhook_data)
                result["processed"] = True
            
            elif event_type == "state.change":
                await self._handle_status_event(webhook_data)
                result["processed"] = True
            
            else:
                waha_logger.warning("UNKNOWN_WEBHOOK_EVENT", {
                    "event_type": event_type,
                    "available_keys": list(webhook_data.keys())
                })
            
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            waha_logger.error("WEBHOOK_PROCESSING_ERROR", e, webhook_data)
        
        return result
    
    async def _handle_message_event(self, webhook_data: Dict[str, Any]):
        """Processa evento de mensagem"""
        message_data = self._extract_message_data(webhook_data)
        
        # Executa todos os handlers de mensagem
        for handler in self.message_handlers:
            try:
                await handler(message_data)
            except Exception as e:
                app_logger.error("MESSAGE_HANDLER_ERROR", e, {"handler": str(handler)})
    
    async def _handle_status_event(self, webhook_data: Dict[str, Any]):
        """Processa evento de mudança de status"""
        status_data = {
            "session": webhook_data.get("session"),
            "status": webhook_data.get("payload", {}).get("state"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Executa todos os handlers de status
        for handler in self.status_handlers:
            try:
                await handler(status_data)
            except Exception as e:
                app_logger.error("STATUS_HANDLER_ERROR", e, {"handler": str(handler)})
    
    def _extract_message_data(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai dados da mensagem do webhook"""
        payload = webhook_data.get("payload", {})
        
        return {
            "message_id": payload.get("id"),
            "from": payload.get("from"),
            "to": payload.get("to"),
            "body": payload.get("body"),
            "type": payload.get("type", "text"),
            "timestamp": payload.get("timestamp"),
            "session": webhook_data.get("session"),
            "raw_payload": payload
        }

