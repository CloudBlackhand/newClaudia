#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas da API de Cobrança
Endpoints para gerenciamento de cobranças
"""

import asyncio
import json
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any

from backend.modules.billing_dispatcher import BillingDispatcher
from backend.modules.waha_integration import WahaIntegration
from backend.modules.logger_system import LogManager, LogCategory
from backend.config.settings import Config

logger = LogManager.get_logger('api_billing')
billing_bp = Blueprint('billing', __name__)

# Instância global do dispatcher
billing_dispatcher = None
waha_client = None

def get_billing_dispatcher():
    """Obter instância do billing dispatcher"""
    global billing_dispatcher, waha_client
    
    if billing_dispatcher is None:
        # Inicializar integração com Waha se configurada
        if Config.WAHA_BASE_URL:
            waha_client = WahaIntegration()
        
        billing_dispatcher = BillingDispatcher(waha_client)
        logger.info(LogCategory.BILLING, "Billing Dispatcher inicializado")
    
    return billing_dispatcher

@billing_bp.route('/health', methods=['GET'])
def health_check():
    """Health check do módulo de cobrança"""
    try:
        dispatcher = get_billing_dispatcher()
        stats = dispatcher.get_statistics()
        
        return jsonify({
            'status': 'healthy',
            'module': 'billing',
            'statistics': stats,
            'timestamp': logger.get_stats()['start_time']
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro no health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@billing_bp.route('/send-batch', methods=['POST'])
def send_billing_batch():
    """Enviar lote de cobranças"""
    try:
        # Validar dados de entrada
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        if 'clients' not in data:
            return jsonify({
                'error': 'Campo "clients" é obrigatório'
            }), 400
        
        template_id = data.get('template_id', 'initial_br')
        schedule_time = data.get('schedule_time')  # ISO format
        
        logger.info(LogCategory.BILLING, 
                   f"Iniciando envio de lote de cobrança",
                   details={
                       'client_count': len(data['clients']),
                       'template_id': template_id,
                       'scheduled': schedule_time is not None
                   })
        
        # Obter dispatcher
        dispatcher = get_billing_dispatcher()
        
        # Processar JSON de clientes
        json_data = json.dumps(data)
        clients, errors = dispatcher.load_clients_from_json(json_data)
        
        if errors:
            logger.error(LogCategory.BILLING, "Erro na validação dos clientes", details={'errors': errors})
            return jsonify({
                'error': 'Dados inválidos',
                'validation_errors': errors
            }), 400
        
        # Criar mensagens
        from datetime import datetime
        schedule_datetime = None
        if schedule_time:
            try:
                schedule_datetime = datetime.fromisoformat(schedule_time)
            except ValueError:
                return jsonify({
                    'error': 'Formato de data/hora inválido para schedule_time'
                }), 400
        
        messages = dispatcher.create_billing_messages(
            clients=clients,
            template_id=template_id,
            schedule_time=schedule_datetime
        )
        
        # Enviar mensagens de forma assíncrona
        async def send_messages():
            return await dispatcher.dispatch_batch(messages)
        
        # Executar envio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(send_messages())
        finally:
            loop.close()
        
        logger.billing_event('batch_sent', 'system', {
            'total_messages': result.total_messages,
            'successful': result.successful,
            'failed': result.failed,
            'execution_time': result.execution_time
        })
        
        return jsonify({
            'success': True,
            'message': 'Lote de cobrança processado',
            'result': {
                'total_messages': result.total_messages,
                'successful': result.successful,
                'failed': result.failed,
                'skipped': result.skipped,
                'execution_time': result.execution_time,
                'errors': result.errors
            }
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro no envio de lote: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@billing_bp.route('/validate-clients', methods=['POST'])
def validate_clients():
    """Validar dados de clientes sem enviar"""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        json_data = json.dumps(data)
        
        # Obter dispatcher
        dispatcher = get_billing_dispatcher()
        
        # Validar dados
        clients, errors = dispatcher.load_clients_from_json(json_data)
        
        if errors:
            return jsonify({
                'valid': False,
                'errors': errors,
                'client_count': 0
            }), 400
        
        logger.info(LogCategory.BILLING, f"Validação de clientes concluída: {len(clients)} válidos")
        
        return jsonify({
            'valid': True,
            'client_count': len(clients),
            'clients_preview': clients[:5],  # Prévia dos primeiros 5
            'message': f'{len(clients)} clientes validados com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro na validação: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@billing_bp.route('/templates', methods=['GET'])
def get_templates():
    """Obter templates de mensagem disponíveis"""
    try:
        dispatcher = get_billing_dispatcher()
        templates = {}
        
        for template_id, template in dispatcher.template_manager.templates.items():
            templates[template_id] = {
                'id': template_id,
                'type': template.type.value,
                'subject': template.subject,
                'content': template.content,
                'variables': template.variables,
                'priority': template.priority
            }
        
        return jsonify({
            'templates': templates,
            'count': len(templates)
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro ao obter templates: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@billing_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Obter estatísticas do sistema de cobrança"""
    try:
        dispatcher = get_billing_dispatcher()
        stats = dispatcher.get_statistics()
        
        # Adicionar estatísticas do logger
        logger_stats = logger.get_stats()
        
        return jsonify({
            'billing_stats': stats,
            'logger_stats': logger_stats,
            'timestamp': logger_stats['start_time']
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro ao obter estatísticas: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@billing_bp.route('/retry-failed', methods=['POST'])
def retry_failed_messages():
    """Reenviar mensagens falhadas"""
    try:
        dispatcher = get_billing_dispatcher()
        
        # Executar retry de forma assíncrona
        async def retry_messages():
            return await dispatcher.retry_failed_messages()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(retry_messages())
        finally:
            loop.close()
        
        logger.billing_event('retry_completed', 'system', {
            'successful': result.successful,
            'failed': result.failed,
            'execution_time': result.execution_time
        })
        
        return jsonify({
            'success': True,
            'message': 'Retry de mensagens concluído',
            'result': {
                'total_messages': result.total_messages,
                'successful': result.successful,
                'failed': result.failed,
                'execution_time': result.execution_time,
                'errors': result.errors
            }
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro no retry: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@billing_bp.route('/test-template', methods=['POST'])
def test_template():
    """Testar renderização de template"""
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Content-Type deve ser application/json'
            }), 400
        
        data = request.get_json()
        template_id = data.get('template_id')
        variables = data.get('variables', {})
        
        if not template_id:
            return jsonify({
                'error': 'Campo "template_id" é obrigatório'
            }), 400
        
        dispatcher = get_billing_dispatcher()
        rendered = dispatcher.template_manager.render_template(template_id, variables)
        
        if rendered is None:
            return jsonify({
                'error': f'Template "{template_id}" não encontrado'
            }), 404
        
        return jsonify({
            'template_id': template_id,
            'variables': variables,
            'rendered': rendered
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"Erro no teste de template: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500
