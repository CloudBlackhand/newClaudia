"""
Rotas da API para funcionalidades do bot de conversação
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import logging

from modules.conversation_bot import ConversationBot
from modules.logger_system import LoggerSystem

logger = logging.getLogger(__name__)
router = APIRouter()

# Referências globais
conversation_bot: Optional[ConversationBot] = None
logger_system: Optional[LoggerSystem] = None

def set_dependencies(cb: ConversationBot, ls: LoggerSystem):
    """Definir dependências dos módulos"""
    global conversation_bot, logger_system
    conversation_bot = cb
    logger_system = ls

@router.post("/send-message")
async def send_message_to_bot(
    user_phone: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
):
    """
    Enviar mensagem para o bot e obter resposta
    
    Args:
        user_phone: Telefone do usuário
        message: Mensagem do usuário
        context: Contexto adicional
    """
    try:
        if not conversation_bot:
            raise HTTPException(status_code=500, detail="Bot não inicializado")
        
        # Processar mensagem
        response = await conversation_bot.process_message(
            user_phone=user_phone,
            message=message,
            context=context or {}
        )
        
        return {
            "success": True,
            "bot_response": response.message,
            "intent": response.intent,
            "confidence": response.confidence,
            "suggested_actions": response.suggested_actions,
            "requires_human": response.requires_human
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-history/{user_phone}")
async def get_conversation_history(user_phone: str):
    """Obter histórico de conversa de um usuário"""
    try:
        if not conversation_bot:
            raise HTTPException(status_code=500, detail="Bot não inicializado")
        
        history = await conversation_bot.get_conversation_history(user_phone)
        
        return {
            "success": True,
            "user_phone": user_phone,
            "conversation_history": history
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/active-sessions")
async def get_active_sessions():
    """Obter número de sessões ativas"""
    try:
        if not conversation_bot:
            raise HTTPException(status_code=500, detail="Bot não inicializado")
        
        count = await conversation_bot.get_active_sessions_count()
        
        return {
            "success": True,
            "active_sessions": count
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter sessões ativas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversation-logs")
async def get_conversation_logs(
    session_id: Optional[str] = None,
    limit: int = 100
):
    """Obter logs de conversas"""
    try:
        if not logger_system:
            raise HTTPException(status_code=500, detail="Sistema de logs não inicializado")
        
        logs = await logger_system.get_conversation_logs(
            session_id=session_id,
            limit=limit
        )
        
        return {
            "success": True,
            "conversation_logs": logs
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter logs de conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bot-stats")
async def get_bot_statistics():
    """Obter estatísticas do bot"""
    try:
        if not conversation_bot:
            raise HTTPException(status_code=500, detail="Bot não inicializado")
        
        active_sessions = await conversation_bot.get_active_sessions_count()
        
        return {
            "success": True,
            "is_healthy": conversation_bot.is_healthy(),
            "active_sessions": active_sessions,
            "is_initialized": conversation_bot.is_initialized
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do bot: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
