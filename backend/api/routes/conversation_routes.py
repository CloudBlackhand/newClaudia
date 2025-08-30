#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas da API de Conversação
Endpoints para gerenciamento de conversas com IA
"""

import asyncio
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from backend.modules.conversation_bot import ConversationBot
from backend.modules.waha_integration import WahaIntegration
from backend.modules.logger_system import LogManager, LogCategory
from backend.config.settings import Config

logger = LogManager.get_logger('api_conversation')
conversation_bp = Blueprint('conversation', __name__)

# Instância global do bot
conversation_bot = None
waha_client = None

def get_conversation_bot():
    """Obter instância do bot de conversação"""
    global conversation_bot, waha_client
    
    if conversation_bot is None:
        # Inicializar integração com Waha se configurada
        if Config.WAHA_BASE_URL:
            waha_client = WahaIntegration()
        
        conversation_bot = ConversationBot()
        logger.info(LogCategory.CONVERSATION, "Conversation Bot inicializado")
    
    return conversation_bot

@conversation_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do módulo de conversação"""
    try:
        bot = get_conversation_bot()
        stats = bot.get_context_stats()
        
        return jsonify({
            'status': 'healthy',
            'module': 'conversation',
            'statistics': stats,
            'timestamp': logger.get_stats()['start_time']
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro no health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@conversation_bp.route('/process-message', methods=['POST'])
def process_message():
    """Processar mensagem do usuário e gerar resposta"""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['phone', 'message']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Campos obrigatórios ausentes: {", ".join(missing_fields)}'
            }), 400
        
        phone = data['phone']
        message = data['message']
        user_name = data.get('user_name')
        auto_reply = data.get('auto_reply', True)
        
        logger.info(LogCategory.CONVERSATION, 
                   f"Processando mensagem de {phone}",
                   details={
                       'message_length': len(message),
                       'user_name': user_name,
                       'auto_reply': auto_reply
                   })
        
        # Obter bot
        bot = get_conversation_bot()
        
        # Processar mensagem
        response = bot.process_message(phone, message, user_name)
        
        # Enviar resposta automaticamente se solicitado e Waha configurado
        sent = False
        if auto_reply and waha_client:
            try:
                async def send_response():
                    async with waha_client:
                        return await waha_client.send_text_message(phone, response.text)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    sent = loop.run_until_complete(send_response())
                finally:
                    loop.close()
                    
                if sent:
                    logger.info(LogCategory.CONVERSATION, f"Resposta automática enviada para {phone}")
                else:
                    logger.warning(LogCategory.CONVERSATION, f"Falha ao enviar resposta automática para {phone}")
                    
            except Exception as e:
                logger.error(LogCategory.CONVERSATION, f"Erro ao enviar resposta automática: {e}")
        
        return jsonify({
            'success': True,
            'response': {
                'text': response.text,
                'type': response.response_type.value,
                'confidence': response.confidence,
                'should_escalate': response.should_escalate,
                'suggested_actions': response.suggested_actions
            },
            'auto_reply_sent': sent,
            'phone': phone
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro no processamento de mensagem: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@conversation_bp.route('/analyze-message', methods=['POST'])
def analyze_message():
    """Analisar mensagem sem gerar resposta"""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        if 'message' not in data:
            return jsonify({
                'error': 'Campo "message" é obrigatório'
            }), 400
        
        message = data['message']
        
        # Obter bot
        bot = get_conversation_bot()
        
        # Analisar mensagem
        analysis = bot.nlp.analyze_message(message)
        
        logger.debug(LogCategory.CONVERSATION, 
                    f"Mensagem analisada: {analysis.intent.value}",
                    details={
                        'sentiment': analysis.sentiment.value,
                        'confidence': analysis.confidence,
                        'entities_count': len(analysis.entities)
                    })
        
        return jsonify({
            'analysis': {
                'intent': analysis.intent.value,
                'sentiment': analysis.sentiment.value,
                'confidence': analysis.confidence,
                'entities': analysis.entities,
                'keywords': analysis.keywords
            },
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro na análise: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@conversation_bp.route('/contexts', methods=['GET'])
def get_active_contexts():
    """Obter contextos de conversa ativos"""
    try:
        bot = get_conversation_bot()
        
        # Filtros opcionais
        phone_filter = request.args.get('phone')
        limit = int(request.args.get('limit', 50))
        
        contexts = []
        for phone, context in bot.active_contexts.items():
            if phone_filter and phone_filter not in phone:
                continue
                
            contexts.append({
                'phone': context.user_phone,
                'session_id': context.session_id,
                'user_name': context.user_name,
                'started_at': context.started_at,
                'last_activity': context.last_activity,
                'message_count': context.message_count,
                'topics_discussed': list(context.topics_discussed),
                'recent_intents': [intent.value for intent in context.intent_history[-5:]],
                'recent_sentiments': [sentiment.value for sentiment in context.sentiment_history[-5:]]
            })
        
        # Ordenar por última atividade
        contexts.sort(key=lambda x: x['last_activity'], reverse=True)
        
        # Aplicar limite
        contexts = contexts[:limit]
        
        return jsonify({
            'contexts': contexts,
            'total_count': len(bot.active_contexts),
            'filtered_count': len(contexts)
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro ao obter contextos: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@conversation_bp.route('/contexts/<phone>', methods=['GET'])
def get_context_details(phone):
    """Obter detalhes de um contexto específico"""
    try:
        bot = get_conversation_bot()
        
        if phone not in bot.active_contexts:
            return jsonify({
                'error': 'Contexto não encontrado'
            }), 404
        
        context = bot.active_contexts[phone]
        
        details = {
            'phone': context.user_phone,
            'session_id': context.session_id,
            'user_name': context.user_name,
            'started_at': context.started_at,
            'last_activity': context.last_activity,
            'message_count': context.message_count,
            'payment_amount': context.payment_amount,
            'due_date': context.due_date,
            'topics_discussed': list(context.topics_discussed),
            'intent_history': [intent.value for intent in context.intent_history],
            'sentiment_history': [sentiment.value for sentiment in context.sentiment_history]
        }
        
        return jsonify({
            'context': details
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro ao obter detalhes do contexto: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@conversation_bp.route('/contexts/<phone>', methods=['DELETE'])
def delete_context(phone):
    """Excluir contexto de conversa"""
    try:
        bot = get_conversation_bot()
        
        if phone not in bot.active_contexts:
            return jsonify({
                'error': 'Contexto não encontrado'
            }), 404
        
        del bot.active_contexts[phone]
        
        logger.info(LogCategory.CONVERSATION, f"Contexto excluído: {phone}")
        
        return jsonify({
            'success': True,
            'message': f'Contexto de {phone} excluído com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro ao excluir contexto: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@conversation_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Obter estatísticas do sistema de conversação"""
    try:
        bot = get_conversation_bot()
        stats = bot.get_context_stats()
        
        # Adicionar estatísticas do logger
        logger_stats = logger.get_stats()
        
        return jsonify({
            'conversation_stats': stats,
            'logger_stats': logger_stats,
            'timestamp': logger_stats['start_time']
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro ao obter estatísticas: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@conversation_bp.route('/test-nlp', methods=['POST'])
def test_nlp():
    """Testar funcionalidades de NLP"""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        if 'messages' not in data:
            return jsonify({
                'error': 'Campo "messages" é obrigatório'
            }), 400
        
        messages = data['messages']
        if not isinstance(messages, list):
            messages = [messages]
        
        bot = get_conversation_bot()
        results = []
        
        for msg in messages:
            analysis = bot.nlp.analyze_message(msg)
            results.append({
                'message': msg,
                'intent': analysis.intent.value,
                'sentiment': analysis.sentiment.value,
                'confidence': analysis.confidence,
                'entities': analysis.entities,
                'keywords': analysis.keywords
            })
        
        return jsonify({
            'results': results,
            'count': len(results)
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.CONVERSATION, f"Erro no teste de NLP: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500
