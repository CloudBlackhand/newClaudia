#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas administrativas para configuração do sistema
"""

from flask import Blueprint, request, jsonify
import psycopg2
import redis
import os
from backend.modules.logger_system import SmartLogger, LogCategory

logger = SmartLogger("admin_routes")
admin_blueprint = Blueprint('admin', __name__)

@admin_blueprint.route('/admin/init-database', methods=['POST'])
def init_database():
    """Inicializar banco de dados e Redis"""
    try:
        logger.info(LogCategory.SYSTEM, "Iniciando configuração do banco de dados")
        
        # Verificar variáveis de ambiente
        database_url = os.getenv('DATABASE_URL')
        redis_url = os.getenv('REDIS_URL')
        
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        if not redis_url:
            return jsonify({
                'success': False,
                'error': 'REDIS_URL não encontrada'
            }), 500
        
        # 1. Conectar ao PostgreSQL
        logger.info(LogCategory.SYSTEM, "Conectando ao PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 2. Criar tabelas básicas
        logger.info(LogCategory.SYSTEM, "Criando tabelas...")
        
        # Tabela de contextos de conversa
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation_contexts (
                id SERIAL PRIMARY KEY,
                phone VARCHAR(20) NOT NULL UNIQUE,
                session_id VARCHAR(100) NOT NULL,
                user_name VARCHAR(100),
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                payment_amount DECIMAL(10,2),
                due_date DATE,
                topics_discussed TEXT[],
                intent_history TEXT[],
                sentiment_history TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabela de campanhas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                status VARCHAR(50) DEFAULT 'pending',
                total_contacts INTEGER DEFAULT 0,
                processed_contacts INTEGER DEFAULT 0,
                successful_messages INTEGER DEFAULT 0,
                failed_messages INTEGER DEFAULT 0,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                config JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabela de mensagens
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                campaign_id VARCHAR(100),
                phone VARCHAR(20) NOT NULL,
                message_type VARCHAR(50) DEFAULT 'text',
                content TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                sent_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabela de aprendizado
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_data (
                id SERIAL PRIMARY KEY,
                phone VARCHAR(20),
                intent VARCHAR(100),
                response_quality DECIMAL(3,2),
                template_effectiveness DECIMAL(3,2),
                client_feedback VARCHAR(50),
                campaign_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Criar índices
        logger.info(LogCategory.SYSTEM, "Criando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_phone ON conversation_contexts(phone);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_id ON campaigns(campaign_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_campaign ON messages(campaign_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_phone ON learning_data(phone);")
        
        # Commit das mudanças
        conn.commit()
        logger.info(LogCategory.SYSTEM, "Tabelas criadas com sucesso!")
        
        # 3. Conectar ao Redis
        logger.info(LogCategory.SYSTEM, "Conectando ao Redis...")
        redis_client = redis.from_url(redis_url)
        
        # Testar conexão Redis
        redis_client.ping()
        
        # 4. Configurar estruturas iniciais do Redis
        logger.info(LogCategory.SYSTEM, "Configurando Redis...")
        redis_client.set("system:initialized", "true")
        redis_client.set("system:version", "2.0")
        redis_client.set("campaigns:active_count", "0")
        redis_client.set("messages:sent_today", "0")
        redis_client.set("messages:failed_today", "0")
        
        # 5. Inserir dados de exemplo
        logger.info(LogCategory.SYSTEM, "Inserindo dados de exemplo...")
        
        # Exemplo de contexto de conversa
        cursor.execute("""
            INSERT INTO conversation_contexts (phone, session_id, user_name, message_count)
            VALUES ('5511999999999', 'example_session', 'Cliente Exemplo', 0)
            ON CONFLICT (phone) DO NOTHING;
        """)
        
        # Exemplo de campanha
        cursor.execute("""
            INSERT INTO campaigns (campaign_id, name, description, status, total_contacts)
            VALUES ('example_campaign', 'Campanha Exemplo', 'Campanha de teste', 'completed', 1)
            ON CONFLICT (campaign_id) DO NOTHING;
        """)
        
        conn.commit()
        
        # 6. Verificar estrutura
        cursor.execute("SELECT COUNT(*) FROM conversation_contexts;")
        contexts_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM campaigns;")
        campaigns_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages;")
        messages_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM learning_data;")
        learning_count = cursor.fetchone()[0]
        
        # Fechar conexões
        cursor.close()
        conn.close()
        
        logger.info(LogCategory.SYSTEM, "Inicialização do banco de dados concluída com sucesso!")
        
        return jsonify({
            'success': True,
            'message': 'Banco de dados inicializado com sucesso!',
            'data': {
                'contexts_count': contexts_count,
                'campaigns_count': campaigns_count,
                'messages_count': messages_count,
                'learning_count': learning_count,
                'redis_configured': True
            }
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao inicializar banco de dados: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_blueprint.route('/admin/health', methods=['GET'])
def health_check():
    """Verificar saúde do sistema"""
    try:
        # Verificar PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT 1;")
            cursor.close()
            conn.close()
            postgres_status = "OK"
        else:
            postgres_status = "NOT_CONFIGURED"
        
        # Verificar Redis
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            redis_status = "OK"
        else:
            redis_status = "NOT_CONFIGURED"
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'services': {
                'postgres': postgres_status,
                'redis': redis_status,
                'flask': 'OK'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
