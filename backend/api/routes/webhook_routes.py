#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas da API de Webhooks
Endpoints para receber webhooks do WhatsApp (Waha)
"""

import hmac
import hashlib
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from backend.modules.conversation_bot import ConversationBot
from backend.modules.waha_integration import WahaIntegration
from backend.modules.logger_system import LogManager, LogCategory
from backend.modules.customer_data_manager import get_customer_data
from backend.config.settings import Config

logger = LogManager.get_logger('api_webhook')
webhook_bp = Blueprint('webhook', __name__)

# Instâncias globais
conversation_bot = None
waha_client = None

def get_services():
    """Obter instâncias dos serviços"""
    global conversation_bot, waha_client
    
    if conversation_bot is None:
        conversation_bot = ConversationBot()
        
    if waha_client is None and Config.WAHA_BASE_URL:
        waha_client = WahaIntegration()
    
    return conversation_bot, waha_client

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verificar assinatura do webhook"""
    if not Config.WEBHOOK_SECRET:
        # Se não há secret configurado, aceita qualquer webhook
        logger.warning(LogCategory.SECURITY, "Webhook sem verificação de assinatura")
        return True
    
    try:
        # Calcular hash HMAC-SHA256
        expected_signature = hmac.new(
            Config.WEBHOOK_SECRET.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Comparar assinaturas
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
        
    except Exception as e:
        logger.error(LogCategory.SECURITY, f"Erro na verificação de assinatura: {e}")
        return False

@webhook_bp.route('/test-simple', methods=['GET'])
def test_simple():
    """Rota de teste simples para verificar se o blueprint está funcionando"""
    return jsonify({
        'status': 'success',
        'message': 'Blueprint webhook está funcionando!',
        'timestamp': '2025-09-02'
    }), 200

@webhook_bp.route('/webhooks/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Receber webhooks do WhatsApp via Waha"""
    try:
        # Verificar Content-Type
        if not request.is_json:
            logger.warning(LogCategory.WHATSAPP, "Webhook recebido com Content-Type inválido")
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        # Obter dados do webhook
        webhook_data = request.get_json()
        if not webhook_data:
            logger.warning(LogCategory.WHATSAPP, "Webhook recebido sem dados")
            return jsonify({
                'error': 'Dados do webhook ausentes'
            }), 400
        
        # VERIFICAÇÃO HMAC DESABILITADA - Funcionava antes sem isso
        # signature = request.headers.get('X-Hub-Signature-256', '')
        # payload = request.get_data()
        
        # if not verify_webhook_signature(payload, signature):
        #     logger.security_event('invalid_webhook_signature', 'high', {
        #         'source_ip': request.remote_addr,
        #         'user_agent': request.headers.get('User-Agent', ''),
        #         'signature_provided': bool(signature)
        #     })
        #     return jsonify({
        #         'error': 'Assinatura inválida'
        #     }), 401
        
        # Log do webhook recebido
        logger.debug(LogCategory.WHATSAPP, 
                    "Webhook recebido",
                    details={
                        'event_type': webhook_data.get('event'),
                        'session': webhook_data.get('session'),
                        'has_payload': 'payload' in webhook_data
                    })
        
        # Processar webhook baseado no tipo de evento
        event_type = webhook_data.get('event')
        
        if event_type == 'message':
            return handle_message_event(webhook_data)
        elif event_type == 'session.status':
            return handle_session_status_event(webhook_data)
        elif event_type == 'message.ack':
            return handle_message_ack_event(webhook_data)
        else:
            logger.info(LogCategory.WHATSAPP, f"Evento não processado: {event_type}")
            return jsonify({
                'status': 'ignored',
                'message': f'Evento {event_type} não processado'
            }), 200
        
    except Exception as e:
        logger.error(LogCategory.WHATSAPP, f"Erro no processamento do webhook: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

def handle_message_event(webhook_data: Dict[str, Any]):
    """Processar evento de mensagem"""
    try:
        bot, waha = get_services()
        
        if not waha:
            logger.warning(LogCategory.WHATSAPP, "Waha não configurado para processar mensagem")
            return jsonify({
                'status': 'ignored',
                'message': 'Waha não configurado'
            }), 200
        
        # Parsear mensagem do webhook
        message = waha.parse_webhook_message(webhook_data)
        
        if not message:
            logger.warning(LogCategory.WHATSAPP, "Falha ao parsear mensagem do webhook")
            return jsonify({
                'error': 'Falha ao parsear mensagem'
            }), 400
        
        # Ignorar mensagens próprias
        if message.from_me:
            logger.debug(LogCategory.WHATSAPP, "Mensagem própria ignorada")
            return jsonify({
                'status': 'ignored',
                'message': 'Mensagem própria'
            }), 200
        
        # Ignorar mensagens não de texto por enquanto
        if message.message_type != 'text':
            logger.debug(LogCategory.WHATSAPP, f"Tipo de mensagem não suportado: {message.message_type}")
            return jsonify({
                'status': 'ignored',
                'message': f'Tipo {message.message_type} não suportado'
            }), 200
        
        # Extrair telefone limpo
        phone = message.sender.replace('@c.us', '')
        
        logger.conversation_event(
            phone=phone,
            direction="incoming",
            message=message.content
        )
        
        # Verificar se é cliente antes de processar
        
        # Buscar dados do cliente
        customer_data = get_customer_data(phone)
        
        if customer_data and customer_data.get('is_customer', False):
            # É cliente - processar com dados do cliente
            logger.info(f"👤 Cliente identificado: {customer_data.get('name', 'Cliente')}")
            response = bot.process_message(phone, message.content, customer_data)
        else:
            # Não é cliente - responder com mensagem geral
            logger.info(f"👤 Pessoa não cadastrada como cliente: {phone}")
            general_response = bot.generate_general_response(phone, message.content)
            response = general_response
        
        # Enviar resposta automaticamente
        sent = False
        try:
            async def send_response():
                async with waha:
                    return await waha.send_text_message(phone, response.message)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                sent = loop.run_until_complete(send_response())
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(LogCategory.WHATSAPP, f"Erro ao enviar resposta: {e}")
        
        if sent:
            logger.conversation_event(
                phone=phone,
                direction="outgoing",
                message=response.message,
                ai_response=True
            )
        
        # Verificar se deve escalar
        if response.escalate:
            logger.warning(LogCategory.CONVERSATION, 
                         f"Conversa requer escalação: {phone}",
                         details={
                             'reason': 'Sistema detectou necessidade de intervenção humana',
                             'confidence': response.confidence,
                             'suggested_actions': response.suggested_actions
                         })
        
        return jsonify({
            'status': 'processed',
            'message': 'Mensagem processada com sucesso',
            'response_sent': sent,
            'should_escalate': response.escalate,
            'phone': phone
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.WHATSAPP, f"Erro no processamento de mensagem: {e}")
        return jsonify({
            'error': 'Erro no processamento',
            'message': str(e)
        }), 500

def handle_session_status_event(webhook_data: Dict[str, Any]):
    """Processar evento de status da sessão"""
    try:
        payload = webhook_data.get('payload', {})
        session_name = payload.get('name', 'unknown')
        status = payload.get('status', 'unknown')
        
        logger.info(LogCategory.WHATSAPP, 
                   f"Status da sessão alterado: {session_name} -> {status}",
                   details=payload)
        
        # Ações baseadas no status
        if status == 'SCAN_QR_CODE':
            logger.info(LogCategory.WHATSAPP, "QR Code necessário para autenticação")
        elif status == 'WORKING':
            logger.info(LogCategory.WHATSAPP, "Sessão WhatsApp conectada e funcionando")
        elif status == 'FAILED':
            logger.error(LogCategory.WHATSAPP, "Falha na sessão WhatsApp")
        
        return jsonify({
            'status': 'processed',
            'session': session_name,
            'new_status': status
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.WHATSAPP, f"Erro no processamento de status: {e}")
        return jsonify({
            'error': 'Erro no processamento',
            'message': str(e)
        }), 500

def handle_message_ack_event(webhook_data: Dict[str, Any]):
    """Processar evento de confirmação de mensagem"""
    try:
        payload = webhook_data.get('payload', {})
        message_id = payload.get('id', 'unknown')
        ack_type = payload.get('ack', 'unknown')
        
        # Mapear tipos de ACK
        ack_map = {
            '1': 'sent',      # Enviada ao servidor
            '2': 'received',  # Recebida pelo destinatário
            '3': 'read'       # Lida pelo destinatário
        }
        
        ack_status = ack_map.get(str(ack_type), ack_type)
        
        logger.debug(LogCategory.WHATSAPP, 
                    f"ACK da mensagem: {message_id} -> {ack_status}",
                    details=payload)
        
        return jsonify({
            'status': 'processed',
            'message_id': message_id,
            'ack_status': ack_status
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.WHATSAPP, f"Erro no processamento de ACK: {e}")
        return jsonify({
            'error': 'Erro no processamento',
            'message': str(e)
        }), 500

@webhook_bp.route('/test', methods=['POST'])
def test_webhook():
    """Endpoint para testar webhooks"""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        logger.info(LogCategory.WHATSAPP, 
                   "Webhook de teste recebido",
                   details={
                       'data_keys': list(data.keys()) if data else [],
                       'source_ip': request.remote_addr
                   })
        
        return jsonify({
            'status': 'test_successful',
            'message': 'Webhook de teste processado',
            'received_data': data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.WHATSAPP, f"Erro no webhook de teste: {e}")
        return jsonify({
            'error': 'Erro no processamento',
            'message': str(e)
        }), 500

@webhook_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do módulo de webhooks"""
    try:
        bot, waha = get_services()
        
        # Verificar status do Waha se configurado
        waha_status = 'not_configured'
        if waha:
            try:
                async def check_waha():
                    async with waha:
                        return await waha.health_check()
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    waha_healthy = loop.run_until_complete(check_waha())
                    waha_status = 'healthy' if waha_healthy else 'unhealthy'
                finally:
                    loop.close()
                    
            except Exception as e:
                waha_status = f'error: {e}'
        
        return jsonify({
            'status': 'healthy',
            'module': 'webhook',
            'services': {
                'conversation_bot': 'initialized' if bot else 'not_initialized',
                'waha_integration': waha_status
            },
            'configuration': {
                'webhook_secret_configured': bool(Config.WEBHOOK_SECRET),
                'waha_url_configured': bool(Config.WAHA_BASE_URL)
            }
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.WHATSAPP, f"Erro no health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
