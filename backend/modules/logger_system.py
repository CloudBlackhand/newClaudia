"""
Sistema de Logging Avançado
Registro detalhado de todas as operações do sistema
"""
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import aiofiles
from uuid import uuid4

logger = logging.getLogger(__name__)

class LoggerSystem:
    """Sistema centralizado de logging com funcionalidades avançadas"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurar diferentes tipos de logs
        self.operation_logs = []
        self.message_logs = []
        self.error_logs = []
        self.conversation_logs = []
        
        # Configurar formatadores
        self._setup_loggers()
        
    def _setup_loggers(self):
        """Configurar diferentes loggers especializados"""
        
        # Logger para operações
        self.operation_logger = logging.getLogger("operations")
        operation_handler = logging.FileHandler(self.log_dir / "operations.log")
        operation_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.operation_logger.addHandler(operation_handler)
        self.operation_logger.setLevel(logging.INFO)
        
        # Logger para mensagens
        self.message_logger = logging.getLogger("messages")
        message_handler = logging.FileHandler(self.log_dir / "messages.log")
        message_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.message_logger.addHandler(message_handler)
        self.message_logger.setLevel(logging.INFO)
        
        # Logger para erros
        self.error_logger = logging.getLogger("errors")
        error_handler = logging.FileHandler(self.log_dir / "errors.log")
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.error_logger.addHandler(error_handler)
        self.error_logger.setLevel(logging.ERROR)
        
        # Logger para conversas
        self.conversation_logger = logging.getLogger("conversations")
        conversation_handler = logging.FileHandler(self.log_dir / "conversations.log")
        conversation_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.conversation_logger.addHandler(conversation_handler)
        self.conversation_logger.setLevel(logging.INFO)
    
    async def log_operation(self, operation_type: str, metadata: Dict[str, Any]) -> str:
        """
        Registrar início de operação
        
        Args:
            operation_type: Tipo da operação
            metadata: Dados adicionais da operação
            
        Returns:
            ID único da operação
        """
        operation_id = str(uuid4())
        
        log_entry = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "metadata": metadata
        }
        
        self.operation_logs.append(log_entry)
        
        self.operation_logger.info(
            f"OPERATION_START - {operation_type} - ID: {operation_id} - "
            f"Metadata: {json.dumps(metadata)}"
        )
        
        return operation_id
    
    async def log_success(self, operation_id: str, result_data: Dict[str, Any]):
        """Registrar sucesso de operação"""
        
        log_entry = {
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "result": result_data
        }
        
        # Atualizar log existente
        for log in self.operation_logs:
            if log["operation_id"] == operation_id:
                log.update(log_entry)
                break
        
        self.operation_logger.info(
            f"OPERATION_SUCCESS - ID: {operation_id} - "
            f"Result: {json.dumps(result_data)}"
        )
    
    async def log_error(self, operation_id: str, error_type: str, error_data: Dict[str, Any]):
        """Registrar erro de operação"""
        
        log_entry = {
            "operation_id": operation_id,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error_type": error_type,
            "error_data": error_data
        }
        
        self.error_logs.append(log_entry)
        
        # Atualizar log existente
        for log in self.operation_logs:
            if log["operation_id"] == operation_id:
                log.update(log_entry)
                break
        
        self.error_logger.error(
            f"OPERATION_ERROR - ID: {operation_id} - Type: {error_type} - "
            f"Data: {json.dumps(error_data)}"
        )
    
    async def log_message_sent(
        self, 
        operation_id: str, 
        recipient: str, 
        message: str, 
        success: bool,
        message_id: Optional[str] = None
    ):
        """Registrar envio de mensagem"""
        
        log_entry = {
            "operation_id": operation_id,
            "message_id": message_id or str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "recipient": self._sanitize_phone(recipient),
            "message_preview": message[:100] + "..." if len(message) > 100 else message,
            "success": success,
            "message_length": len(message)
        }
        
        self.message_logs.append(log_entry)
        
        status = "SUCCESS" if success else "FAILED"
        self.message_logger.info(
            f"MESSAGE_{status} - Operation: {operation_id} - "
            f"Recipient: {self._sanitize_phone(recipient)} - "
            f"Length: {len(message)} chars"
        )
    
    async def log_conversation(
        self, 
        session_id: str, 
        user_message: str, 
        bot_response: str, 
        context: Dict[str, Any]
    ):
        """Registrar conversa com bot"""
        
        log_entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response,
            "context": context,
            "user_message_length": len(user_message),
            "bot_response_length": len(bot_response)
        }
        
        self.conversation_logs.append(log_entry)
        
        self.conversation_logger.info(
            f"CONVERSATION - Session: {session_id} - "
            f"User: {len(user_message)} chars - Bot: {len(bot_response)} chars"
        )
    
    async def log_webhook_received(self, webhook_type: str, data: Dict[str, Any]):
        """Registrar webhook recebido"""
        
        log_entry = {
            "webhook_type": webhook_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "data_size": len(str(data))
        }
        
        self.operation_logger.info(
            f"WEBHOOK_RECEIVED - Type: {webhook_type} - "
            f"Size: {len(str(data))} chars"
        )
    
    def _sanitize_phone(self, phone: str) -> str:
        """Sanitizar número de telefone para logs"""
        if len(phone) > 6:
            return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]
        return "*" * len(phone)
    
    async def get_operation_logs(
        self, 
        operation_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obter logs de operações"""
        
        if operation_id:
            return [log for log in self.operation_logs if log["operation_id"] == operation_id]
        
        return self.operation_logs[-limit:]
    
    async def get_message_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obter logs de mensagens"""
        return self.message_logs[-limit:]
    
    async def get_error_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obter logs de erros"""
        return self.error_logs[-limit:]
    
    async def get_conversation_logs(
        self, 
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obter logs de conversas"""
        
        if session_id:
            return [log for log in self.conversation_logs if log["session_id"] == session_id]
        
        return self.conversation_logs[-limit:]
    
    async def generate_report(self, start_date: Optional[str] = None) -> Dict[str, Any]:
        """Gerar relatório de atividades"""
        
        # Filtrar logs por data se especificado
        filtered_operations = self.operation_logs
        filtered_messages = self.message_logs
        filtered_errors = self.error_logs
        filtered_conversations = self.conversation_logs
        
        if start_date:
            # Implementar filtro por data
            pass
        
        # Calcular estatísticas
        total_operations = len(filtered_operations)
        successful_operations = len([log for log in filtered_operations if log.get("status") == "success"])
        failed_operations = len([log for log in filtered_operations if log.get("status") == "error"])
        
        total_messages = len(filtered_messages)
        successful_messages = len([log for log in filtered_messages if log.get("success")])
        failed_messages = total_messages - successful_messages
        
        total_conversations = len(filtered_conversations)
        total_errors = len(filtered_errors)
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "period": {
                "start_date": start_date or "início",
                "end_date": datetime.now().isoformat()
            },
            "operations": {
                "total": total_operations,
                "successful": successful_operations,
                "failed": failed_operations,
                "success_rate": (successful_operations / total_operations * 100) if total_operations > 0 else 0
            },
            "messages": {
                "total": total_messages,
                "successful": successful_messages,
                "failed": failed_messages,
                "success_rate": (successful_messages / total_messages * 100) if total_messages > 0 else 0
            },
            "conversations": {
                "total": total_conversations
            },
            "errors": {
                "total": total_errors
            }
        }
    
    async def cleanup_old_logs(self, days_to_keep: int = 30):
        """Limpar logs antigos"""
        # Implementar limpeza baseada em data
        pass
    
    async def export_logs(self, file_path: str, format: str = "json"):
        """Exportar logs para arquivo"""
        export_data = {
            "operations": self.operation_logs,
            "messages": self.message_logs,
            "errors": self.error_logs,
            "conversations": self.conversation_logs,
            "export_timestamp": datetime.now().isoformat()
        }
        
        if format == "json":
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(export_data, indent=2, ensure_ascii=False))
        
        return {"success": True, "file_path": file_path, "format": format}
