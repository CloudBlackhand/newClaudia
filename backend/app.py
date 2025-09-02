#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação principal Flask
Sistema de Cobrança Inteligente
"""

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

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
    
    logger.info("🚀 Iniciando criação da aplicação Flask...")
    
    try:
        app = Flask(__name__, 
                    static_folder='../frontend',
                    static_url_path='')
        logger.info("✅ Flask app criado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar Flask app: {e}")
        raise
    
    try:
        # Configurações da aplicação
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-me')
        app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
        app.config['JSON_AS_ASCII'] = False
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
        logger.info("✅ Configurações da aplicação definidas")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar aplicação: {e}")
        raise
    
    try:
        # Configurar CORS
        CORS(app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-API-Key"]
            }
        })
        logger.info("✅ CORS configurado com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao configurar CORS: {e}")
        raise
    
    try:
        # Registrar blueprints
        logger.info("🔄 Iniciando registro de blueprints...")
        register_blueprints(app)
        logger.info("✅ Blueprints registrados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar blueprints: {e}")
        raise
    
    try:
        # Registrar handlers de erro
        logger.info("🔄 Iniciando registro de error handlers...")
        register_error_handlers(app)
        logger.info("✅ Error handlers registrados com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao registrar error handlers: {e}")
        raise
    
    logger.info("✅ Aplicação Flask criada com sucesso")
    return app

def register_blueprints(app):
    """Registrar blueprints da aplicação"""
    try:
        # Importar blueprints
        try:
            from backend.api.routes.billing_routes import billing_bp
            logger.info("✅ Billing blueprint importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar billing blueprint: {e}")
            billing_bp = None
            
        try:
            from backend.api.routes.conversation_routes import conversation_bp
            logger.info("✅ Conversation blueprint importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar conversation blueprint: {e}")
            conversation_bp = None
            
        try:
            from backend.api.routes.webhook_routes import webhook_bp
            logger.info("✅ Webhook blueprint importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar webhook blueprint: {e}")
            webhook_bp = None
            
        try:
            from backend.api.routes.campaign_routes import campaign_blueprint
            logger.info("✅ Campaign blueprint importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar campaign blueprint: {e}")
            campaign_blueprint = None
            
        try:
            from backend.api.routes.admin_routes import admin_blueprint
            logger.info("✅ Admin blueprint importado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao importar admin blueprint: {e}")
            admin_blueprint = None
        
        # Registrar blueprints
        app.register_blueprint(billing_bp, url_prefix='/api/billing')
        # CORREÇÃO DEFINITIVA: Registrar webhook sem prefixo
        app.register_blueprint(webhook_bp, url_prefix='')
        app.register_blueprint(campaign_blueprint, url_prefix='/api')
        app.register_blueprint(admin_blueprint, url_prefix='/api')
        
        # Rota principal
        @app.route('/')
        def index():
            return app.send_static_file('index.html')
        
        # Rota de health check
        @app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'service': 'Sistema de Cobrança Inteligente',
                'version': '1.0.0'
            }), 200
        
        logger.info("✅ Blueprints registrados com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao registrar blueprints: {e}")
        raise

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

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
