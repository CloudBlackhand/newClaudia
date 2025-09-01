from flask import Blueprint, request, jsonify
from backend.modules.campaign_processor import CampaignProcessor
from backend.utils.logger import Logger, LogCategory
import os
import json

logger = Logger()
campaign_blueprint = Blueprint('campaign', __name__)
campaign_processor = CampaignProcessor()

@campaign_blueprint.route('/campaigns/process', methods=['POST'])
def process_campaign():
    """Processa uma campanha em massa"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados da campanha não fornecidos'}), 400
        
        # Valida campos obrigatórios
        required_fields = ['file_path', 'campaign_config']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório: {field}'}), 400
        
        file_path = data['file_path']
        campaign_config = data['campaign_config']
        
        # Valida se arquivo existe
        if not os.path.exists(file_path):
            return jsonify({'error': f'Arquivo não encontrado: {file_path}'}), 404
        
        # Valida configuração da campanha
        if not isinstance(campaign_config, dict):
            return jsonify({'error': 'Configuração da campanha deve ser um objeto'}), 400
        
        # Processa campanha
        logger.info(LogCategory.BILLING, f"🚀 Iniciando processamento de campanha: {file_path}")
        result = campaign_processor.process_campaign_file(file_path, campaign_config)
        
        if result['success']:
            return jsonify({
                'success': True,
                'campaign_id': result['campaign_id'],
                'stats': result['stats'],
                'message': 'Campanha processada com sucesso'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao processar campanha: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaign_blueprint.route('/campaigns/status/<campaign_id>', methods=['GET'])
def get_campaign_status(campaign_id):
    """Retorna status de uma campanha específica"""
    try:
        campaign_status = campaign_processor.get_campaign_status(campaign_id)
        
        if not campaign_status:
            return jsonify({'error': 'Campanha não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'status': campaign_status
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao obter status da campanha: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaign_blueprint.route('/campaigns/list', methods=['GET'])
def list_campaigns():
    """Lista todas as campanhas processadas"""
    try:
        campaigns = campaign_processor.get_all_campaigns()
        
        return jsonify({
            'success': True,
            'campaigns': campaigns
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao listar campanhas: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaign_blueprint.route('/campaigns/stats', methods=['GET'])
def get_campaign_stats():
    """Retorna estatísticas gerais das campanhas"""
    try:
        stats = campaign_processor.get_campaign_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaign_blueprint.route('/campaigns/templates', methods=['GET'])
def get_message_templates():
    """Retorna templates de mensagem disponíveis"""
    try:
        templates = {
            'fpd_reminder': {
                'name': 'Lembrete FPD',
                'template': 'Olá {NOME}! 👋\n\nSua fatura de {VALOR} reais venceu há {DIAS_FPD} dias.\n\nPara evitar bloqueios, regularize seu pagamento o quanto antes.\n\nAgradecemos sua preferência! 🙏',
                'variables': ['NOME', 'VALOR', 'DIAS_FPD']
            },
            'spd_reminder': {
                'name': 'Lembrete SPD',
                'template': 'Oi {NOME}! 😊\n\nSua segunda fatura de {VALOR} reais venceu há {DIAS_FPD} dias.\n\nMantenha seu serviço ativo regularizando o pagamento.\n\nQualquer dúvida, estamos aqui! 📞',
                'variables': ['NOME', 'VALOR', 'DIAS_FPD']
            },
            'welcome_message': {
                'name': 'Boas-vindas',
                'template': 'Bem-vindo(a) {NOME}! 🎉\n\nSeu plano {PLANO} foi ativado com sucesso em {CIDADE}.\n\nValor mensal: R$ {VALOR}\nVendedor: {VENDEDOR}\n\nAproveite sua internet! 🚀',
                'variables': ['NOME', 'PLANO', 'CIDADE', 'VALOR', 'VENDEDOR']
            },
            'custom': {
                'name': 'Personalizado',
                'template': 'Olá {NOME}! 👋\n\n{SUA_MENSAGEM_AQUI}\n\nAtenciosamente,\nEquipe Stochos Telecom',
                'variables': ['NOME', 'SUA_MENSAGEM_AQUI']
            }
        }
        
        return jsonify({
            'success': True,
            'templates': templates
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao obter templates: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaign_blueprint.route('/campaigns/validate', methods=['POST'])
def validate_campaign_config():
    """Valida configuração de uma campanha antes do processamento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Configuração não fornecida'}), 400
        
        config = data.get('campaign_config', {})
        file_path = data.get('file_path', '')
        
        errors = []
        warnings = []
        
        # Validações obrigatórias
        if not config.get('message_template'):
            errors.append('Template de mensagem é obrigatório')
        
        if not file_path:
            errors.append('Caminho do arquivo é obrigatório')
        elif not os.path.exists(file_path):
            errors.append(f'Arquivo não encontrado: {file_path}')
        
        # Validações de filtros
        if 'status_filter' in config and not isinstance(config['status_filter'], list):
            errors.append('Filtro de status deve ser uma lista')
        
        if 'tipo_filter' in config and not isinstance(config['tipo_filter'], list):
            errors.append('Filtro de tipo deve ser uma lista')
        
        if 'valor_minimo' in config and not isinstance(config['valor_minimo'], (int, float)):
            errors.append('Valor mínimo deve ser um número')
        
        if 'cidades' in config and not isinstance(config['cidades'], list):
            errors.append('Filtro de cidades deve ser uma lista')
        
        if 'vendedores' in config and not isinstance(config['vendedores'], list):
            errors.append('Filtro de vendedores deve ser uma lista')
        
        # Avisos
        if not config.get('fallback_message'):
            warnings.append('Mensagem de fallback não definida')
        
        if not config.get('rate_limit'):
            warnings.append('Limite de taxa não definido (pode causar bloqueios)')
        
        # Retorna resultado da validação
        is_valid = len(errors) == 0
        
        return jsonify({
            'success': True,
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'config_summary': {
                'has_template': bool(config.get('message_template')),
                'has_filters': any(key in config for key in ['status_filter', 'tipo_filter', 'valor_minimo', 'cidades', 'vendedores']),
                'has_fallback': bool(config.get('fallback_message')),
                'has_rate_limit': bool(config.get('rate_limit'))
            }
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao validar configuração: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@campaign_blueprint.route('/campaigns/preview', methods=['POST'])
def preview_campaign():
    """Gera preview de uma campanha sem enviar mensagens"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados da campanha não fornecidos'}), 400
        
        file_path = data.get('file_path', '')
        campaign_config = data.get('campaign_config', {})
        max_preview = data.get('max_preview', 5)  # Máximo de contatos para preview
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'Arquivo não encontrado: {file_path}'}), 404
        
        # Carrega dados
        with open(file_path, 'r', encoding='utf-8') as file:
            campaign_data = json.load(file)
        
        # Filtra contatos válidos
        valid_contacts = []
        for contact in campaign_data[:max_preview]:
            try:
                if 'dados_vendas' in contact and contact['dados_vendas']:
                    venda = contact['dados_vendas'][0]
                    
                    # Extrai dados básicos
                    nome = venda.get('NOME', '').strip()
                    telefone = venda.get('TELEFONE1', '')
                    
                    if nome and telefone:
                        # Gera mensagem de preview
                        message = campaign_config.get('message_template', '')
                        if message:
                            message = message.replace('{NOME}', nome)
                            message = message.replace('{CIDADE}', venda.get('CIDADE', 'N/A'))
                            message = message.replace('{PLANO}', venda.get('INTERNET', 'N/A'))
                            message = message.replace('{VALOR}', str(venda.get('PREÇO', 'N/A')))
                            message = message.replace('{VENDEDOR}', venda.get('VENDEDOR', 'N/A'))
                        
                        valid_contacts.append({
                            'protocolo': contact.get('protocolo', 'N/A'),
                            'nome': nome,
                            'telefone': telefone,
                            'cidade': venda.get('CIDADE', 'N/A'),
                            'plano': venda.get('INTERNET', 'N/A'),
                            'valor': venda.get('PREÇO', 'N/A'),
                            'vendedor': venda.get('VENDEDOR', 'N/A'),
                            'preview_message': message
                        })
            except Exception as e:
                continue
        
        return jsonify({
            'success': True,
            'preview_contacts': valid_contacts,
            'total_contacts': len(campaign_data),
            'preview_count': len(valid_contacts),
            'message': f'Preview gerado com {len(valid_contacts)} contatos válidos'
        }), 200
        
    except Exception as e:
        logger.error(LogCategory.BILLING, f"❌ Erro ao gerar preview: {str(e)}")
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
