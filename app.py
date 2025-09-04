#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cobrança Inteligente
Launcher para Railway - Versão Simplificada
"""

import os
import sys
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Adicionar diretório atual ao path ANTES de qualquer importação
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app():
    """Factory function para criar a aplicação Flask"""
    
    app = Flask(__name__, 
                static_folder='frontend',
                static_url_path='')
    
    # Configurações da aplicação
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-me')
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Configurar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key"]
        }
    })
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar handlers de erro
    register_error_handlers(app)
    
    logger.info("✅ Aplicação Flask criada com sucesso")
    return app

def register_blueprints(app):
    """Registrar blueprints da aplicação"""
    logger.info("🔄 Tentando importar blueprints...")
    
    # Lista de blueprints para tentar importar
    blueprints_config = [
        ('backend.api.routes.billing_routes', 'billing_bp', '/api/billing'),
        ('backend.api.routes.conversation_routes', 'conversation_bp', '/api/conversation'),
        ('backend.api.routes.webhook_routes', 'webhook_bp', ''),
        ('backend.api.routes.campaign_routes', 'campaign_blueprint', '/api'),
        ('backend.api.routes.admin_routes', 'admin_blueprint', '/api'),
        ('backend.api.routes.vendas_routes', 'vendas_blueprint', '/api')
    ]
    
    registered_count = 0
    
    for module_path, blueprint_name, url_prefix in blueprints_config:
        try:
            # Importar o módulo
            module = __import__(module_path, fromlist=[blueprint_name])
            blueprint = getattr(module, blueprint_name)
            
            # Registrar blueprint
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            logger.info(f"✅ {blueprint_name} registrado com sucesso - url_prefix='{url_prefix}'")
            registered_count += 1
            
        except Exception as e:
            logger.error(f"❌ Erro ao importar {module_path}.{blueprint_name}: {e}")
            continue
    
    logger.info(f"✅ {registered_count} blueprints registrados com sucesso")
    
    # Rota principal
    @app.route('/')
    def index():
        try:
            return send_from_directory('frontend', 'index.html')
        except:
            return jsonify({
                'message': 'Sistema de Cobrança Inteligente',
                'status': 'running',
                'frontend': 'not_found'
            })
    
    # Servir arquivos estáticos
    @app.route('/<path:filename>')
    def static_files(filename):
        try:
            return send_from_directory('frontend', filename)
        except:
            return jsonify({'error': 'File not found'}), 404
    
    # Rota de health check
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Sistema de Cobrança Inteligente',
            'version': '1.0.0',
            'blueprints_registered': registered_count
        }), 200

def register_error_handlers(app):
    """Registrar handlers de erro personalizados"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint não encontrado',
            'message': 'O recurso solicitado não existe',
            'status': 404
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Requisição inválida',
            'message': 'Os dados fornecidos são inválidos',
            'status': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Não autorizado',
            'message': 'Credenciais inválidas ou ausentes',
            'status': 401
        }), 401
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Erro interno do servidor: {error}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': 'Ocorreu um erro inesperado',
            'status': 500
        }), 500
    
    logger.info("✅ Handlers de erro registrados com sucesso")

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
