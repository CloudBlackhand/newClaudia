"""
Sistema de logging avançado e centralizado
"""
import os
import sys
import json
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
from backend.config.settings import active_config

class LoggerSetup:
    """Configuração e gerenciamento centralizado de logs"""
    
    def __init__(self):
        self.config = active_config
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o sistema de logging"""
        # Remove handlers padrão
        logger.remove()
        
        # Cria diretório de logs se não existir
        log_dir = Path(self.config.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Formato personalizado para logs
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # Handler para console (desenvolvimento)
        if self.config.DEBUG:
            logger.add(
                sys.stdout,
                format=log_format,
                level=self.config.LOG_LEVEL,
                colorize=True
            )
        
        # Handler para arquivo
        logger.add(
            self.config.LOG_FILE,
            format=log_format,
            level=self.config.LOG_LEVEL,
            rotation="10 MB",
            retention="10 days",
            compression="zip",
            encoding="utf-8"
        )
        
        # Handler para erros críticos
        logger.add(
            f"{log_dir}/errors.log",
            format=log_format,
            level="ERROR",
            rotation="1 week",
            retention="1 month",
            compression="zip",
            encoding="utf-8"
        )
        
        # Handler para auditoria de segurança
        logger.add(
            f"{log_dir}/security.log",
            format=log_format,
            level="WARNING",
            rotation="1 day",
            retention="3 months",
            compression="zip",
            encoding="utf-8",
            filter=lambda record: "SECURITY" in record["message"]
        )

class StructuredLogger:
    """Logger estruturado para diferentes tipos de eventos"""
    
    def __init__(self, component: str):
        self.component = component
        self.logger = logger.bind(component=component)
    
    def _log_structured(self, level: str, event: str, data: Dict[str, Any], **kwargs):
        """Log estruturado com metadados"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": self.component,
            "event": event,
            "data": data,
            **kwargs
        }
        
        message = f"{event} | {json.dumps(log_entry, default=str, ensure_ascii=False)}"
        getattr(self.logger, level.lower())(message)
    
    def info(self, event: str, data: Dict[str, Any] = None, **kwargs):
        """Log de informação"""
        self._log_structured("INFO", event, data or {}, **kwargs)
    
    def warning(self, event: str, data: Dict[str, Any] = None, **kwargs):
        """Log de aviso"""
        self._log_structured("WARNING", event, data or {}, **kwargs)
    
    def error(self, event: str, error: Exception = None, data: Dict[str, Any] = None, **kwargs):
        """Log de erro com traceback"""
        error_data = data or {}
        if error:
            error_data.update({
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc()
            })
        self._log_structured("ERROR", event, error_data, **kwargs)
    
    def security(self, event: str, data: Dict[str, Any] = None, **kwargs):
        """Log de segurança"""
        security_data = data or {}
        security_data["security_event"] = True
        self._log_structured("WARNING", f"SECURITY: {event}", security_data, **kwargs)

class BillingLogger(StructuredLogger):
    """Logger específico para módulo de cobrança"""
    
    def __init__(self):
        super().__init__("BILLING")
    
    def message_sent(self, phone: str, template: str, success: bool, message_id: str = None, error: str = None):
        """Log de envio de mensagem"""
        data = {
            "phone": self._mask_phone(phone),
            "template": template,
            "success": success,
            "message_id": message_id,
            "error": error
        }
        
        if success:
            self.info("MESSAGE_SENT", data)
        else:
            self.error("MESSAGE_SEND_FAILED", data=data)
    
    def client_processed(self, client_data: Dict[str, Any], success: bool, reason: str = None):
        """Log de processamento de cliente"""
        data = {
            "client_id": client_data.get("id"),
            "client_name": client_data.get("name", "").split()[0] if client_data.get("name") else None,
            "phone": self._mask_phone(client_data.get("phone", "")),
            "amount": client_data.get("amount"),
            "success": success,
            "reason": reason
        }
        
        if success:
            self.info("CLIENT_PROCESSED", data)
        else:
            self.warning("CLIENT_PROCESSING_FAILED", data)
    
    def batch_started(self, total_clients: int, template: str):
        """Log de início de lote de cobrança"""
        self.info("BATCH_STARTED", {
            "total_clients": total_clients,
            "template": template,
            "started_at": datetime.utcnow().isoformat()
        })
    
    def batch_completed(self, total_clients: int, successful: int, failed: int, duration: float):
        """Log de finalização de lote"""
        self.info("BATCH_COMPLETED", {
            "total_clients": total_clients,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_clients * 100) if total_clients > 0 else 0,
            "duration_seconds": duration,
            "completed_at": datetime.utcnow().isoformat()
        })
    
    @staticmethod
    def _mask_phone(phone: str) -> str:
        """Mascara número de telefone para privacidade"""
        if not phone or len(phone) < 4:
            return "****"
        return f"{phone[:2]}****{phone[-2:]}"

class ConversationLogger(StructuredLogger):
    """Logger específico para conversas do bot"""
    
    def __init__(self):
        super().__init__("CONVERSATION")
    
    def message_received(self, phone: str, message: str, message_type: str = "text"):
        """Log de mensagem recebida"""
        self.info("MESSAGE_RECEIVED", {
            "phone": BillingLogger._mask_phone(phone),
            "message_length": len(message),
            "message_type": message_type,
            "preview": message[:50] + "..." if len(message) > 50 else message
        })
    
    def bot_response(self, phone: str, response: str, intent: str = None, confidence: float = None):
        """Log de resposta do bot"""
        self.info("BOT_RESPONSE", {
            "phone": BillingLogger._mask_phone(phone),
            "response_length": len(response),
            "intent": intent,
            "confidence": confidence,
            "preview": response[:50] + "..." if len(response) > 50 else response
        })
    
    def conversation_started(self, phone: str, context: str = None):
        """Log de início de conversa"""
        self.info("CONVERSATION_STARTED", {
            "phone": BillingLogger._mask_phone(phone),
            "context": context
        })
    
    def conversation_ended(self, phone: str, duration: float, messages_count: int):
        """Log de fim de conversa"""
        self.info("CONVERSATION_ENDED", {
            "phone": BillingLogger._mask_phone(phone),
            "duration_seconds": duration,
            "messages_count": messages_count
        })

class WahaLogger(StructuredLogger):
    """Logger específico para integração Waha"""
    
    def __init__(self):
        super().__init__("WAHA")
    
    def webhook_received(self, event_type: str, data: Dict[str, Any]):
        """Log de webhook recebido"""
        self.info("WEBHOOK_RECEIVED", {
            "event_type": event_type,
            "data_keys": list(data.keys()),
            "phone": BillingLogger._mask_phone(data.get("from", ""))
        })
    
    def api_call(self, endpoint: str, method: str, success: bool, status_code: int = None, error: str = None):
        """Log de chamada para API Waha"""
        data = {
            "endpoint": endpoint,
            "method": method,
            "success": success,
            "status_code": status_code,
            "error": error
        }
        
        if success:
            self.info("API_CALL_SUCCESS", data)
        else:
            self.error("API_CALL_FAILED", data=data)

# Inicializa o sistema de logging
_logger_setup = LoggerSetup()

# Instâncias dos loggers especializados
billing_logger = BillingLogger()
conversation_logger = ConversationLogger()
waha_logger = WahaLogger()

# Logger geral da aplicação
app_logger = StructuredLogger("APP")

