"""
Rotas da API para webhooks do Waha
"""
from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import logging
import hmac
import hashlib

from modules.waha_integration import WahaIntegration
from modules.logger_system import LoggerSystem
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Referências globais
waha_integration: Optional[WahaIntegration] = None
logger_system: Optional[LoggerSystem] = None

def set_dependencies(wi: WahaIntegration, ls: LoggerSystem):
    """Definir dependências dos módulos"""
    global waha_integration, logger_system
    waha_integration = wi
    logger_system = ls

@router.post("/waha")
async def receive_waha_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    """
    Receber webhooks do Waha
    
    Args:
        request: Request com dados do webhook
        x_signature: Assinatura do webhook (se configurada)
        authorization: Token de autorização
    """
    try:
        if not waha_integration:
            raise HTTPException(status_code=500, detail="Integração Waha não inicializada")
        
        # Obter dados do webhook
        body = await request.body()
        
        # Verificar assinatura se configurada
        if settings.webhook_secret:
            if not _verify_webhook_signature(body, x_signature, settings.webhook_secret):
                raise HTTPException(status_code=401, detail="Assinatura inválida")
        
        # Parse dos dados
        try:
            webhook_data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="JSON inválido")
        
        # Processar webhook
        result = await waha_integration.process_webhook(webhook_data)
        
        return {
            "success": True,
            "processed": result.get("success", False),
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/waha/status")
async def get_waha_status():
    """Obter status da integração Waha"""
    try:
        if not waha_integration:
            raise HTTPException(status_code=500, detail="Integração Waha não inicializada")
        
        status = await waha_integration.get_session_status()
        stats = await waha_integration.get_integration_stats()
        
        return {
            "success": True,
            "waha_status": status,
            "integration_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter status Waha: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-message")
async def send_whatsapp_message(
    to_number: str,
    message: str
):
    """
    Enviar mensagem via WhatsApp
    
    Args:
        to_number: Número de destino
        message: Mensagem a ser enviada
    """
    try:
        if not waha_integration:
            raise HTTPException(status_code=500, detail="Integração Waha não inicializada")
        
        result = await waha_integration.send_message(to_number, message)
        
        return {
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Erro ao enviar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-bulk")
async def send_bulk_messages(
    messages: list[Dict[str, str]]
):
    """
    Enviar múltiplas mensagens
    
    Args:
        messages: Lista de {"to": "number", "message": "text"}
    """
    try:
        if not waha_integration:
            raise HTTPException(status_code=500, detail="Integração Waha não inicializada")
        
        if len(messages) > 1000:
            raise HTTPException(status_code=400, detail="Máximo 1000 mensagens por lote")
        
        result = await waha_integration.send_bulk_messages(messages)
        
        return {
            "success": True,
            "bulk_result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no envio em lote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _verify_webhook_signature(body: bytes, signature: Optional[str], secret: str) -> bool:
    """
    Verificar assinatura do webhook
    
    Args:
        body: Corpo da requisição
        signature: Assinatura recebida
        secret: Segredo para verificação
        
    Returns:
        True se assinatura for válida
    """
    if not signature:
        return False
    
    try:
        # Calcular assinatura esperada
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Comparar assinaturas
        return hmac.compare_digest(signature, f"sha256={expected_signature}")
        
    except Exception:
        return False

@router.get("/webhook-logs")
async def get_webhook_logs(limit: int = 100):
    """Obter logs de webhooks recebidos"""
    try:
        if not logger_system:
            raise HTTPException(status_code=500, detail="Sistema de logs não inicializado")
        
        # Por agora, retornar logs gerais - pode ser refinado depois
        operation_logs = await logger_system.get_operation_logs(limit=limit)
        
        webhook_logs = [
            log for log in operation_logs 
            if "webhook" in log.get("operation_type", "").lower()
        ]
        
        return {
            "success": True,
            "webhook_logs": webhook_logs
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter logs de webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
