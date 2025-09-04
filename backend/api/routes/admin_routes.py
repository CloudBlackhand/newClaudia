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

@admin_blueprint.route('/admin/test-waha', methods=['POST'])
def test_waha():
    """Testar conexão com Waha"""
    try:
        import asyncio
        from backend.modules.waha_integration import WahaIntegration, SessionStatus
        
        async def test_connection():
            waha_url = os.getenv('WAHA_BASE_URL', 'https://wahawa-production.up.railway.app')
            session_name = os.getenv('WAHA_SESSION_NAME', 'claudia-cobrancas')
            
            waha = WahaIntegration(waha_url, session_name)
            
            try:
                # Testar health check
                health_ok = await waha.health_check()
                if not health_ok:
                    return {'success': False, 'error': 'Waha não está respondendo'}
                
                # Verificar status da sessão
                status = await waha.get_session_status(force_refresh=True)
                
                if status:
                    if status == SessionStatus.WORKING:
                        return {
                            'success': True,
                            'status': 'working',
                            'message': 'WhatsApp está funcionando e pronto!'
                        }
                    elif status == SessionStatus.SCAN_QR_CODE:
                        qr_code = await waha.get_qr_code()
                        return {
                            'success': True,
                            'status': 'qr_required',
                            'message': 'QR Code necessário para autenticação',
                            'qr_code': qr_code
                        }
                    elif status == SessionStatus.STOPPED:
                        started = await waha.start_whatsapp_session()
                        if started:
                            return {
                                'success': True,
                                'status': 'started',
                                'message': 'Sessão iniciada com sucesso!'
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'Falha ao iniciar sessão'
                            }
                    else:
                        return {
                            'success': True,
                            'status': status.value,
                            'message': f'Status atual: {status.value}'
                        }
                else:
                    return {
                        'success': False,
                        'error': 'Não foi possível obter status da sessão'
                    }
                    
            except Exception as e:
                return {'success': False, 'error': str(e)}
            finally:
                await waha.close_session()
        
        # Executar teste assíncrono
        result = asyncio.run(test_connection())
        
        if result['success']:
            logger.info(LogCategory.SYSTEM, f"Teste Waha bem-sucedido: {result.get('status', 'unknown')}")
        else:
            logger.error(LogCategory.SYSTEM, f"Teste Waha falhou: {result.get('error', 'unknown')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro no teste Waha: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_blueprint.route('/admin/database/stats', methods=['GET'])
def get_database_stats():
    """Obter estatísticas do banco de dados"""
    try:
        logger.info(LogCategory.SYSTEM, "Buscando estatísticas do banco de dados")
        
        # Conectar ao banco
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Contar clientes
        cursor.execute("SELECT COUNT(*) FROM customers")
        clients_count = cursor.fetchone()[0]
        
        # Contar conversas
        cursor.execute("SELECT COUNT(*) FROM conversation_contexts")
        conversations_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(LogCategory.SYSTEM, f"Estatísticas: {clients_count} clientes, {conversations_count} conversas")
        
        return jsonify({
            'success': True,
            'clients_count': clients_count,
            'conversations_count': conversations_count,
            'total_records': clients_count + conversations_count
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao buscar estatísticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_blueprint.route('/admin/database/clear', methods=['POST'])
def clear_database():
    """Limpar todos os dados do banco de dados"""
    try:
        logger.warning(LogCategory.SYSTEM, "INICIANDO LIMPEZA COMPLETA DO BANCO DE DADOS")
        
        # Conectar ao banco
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Contar registros antes da limpeza
        cursor.execute("SELECT COUNT(*) FROM customers")
        clients_before = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversation_contexts")
        conversations_before = cursor.fetchone()[0]
        
        # Limpar todas as tabelas
        logger.warning(LogCategory.SYSTEM, "Limpando tabela customers...")
        cursor.execute("DELETE FROM customers")
        
        logger.warning(LogCategory.SYSTEM, "Limpando tabela conversation_contexts...")
        cursor.execute("DELETE FROM conversation_contexts")
        
        # Resetar sequências
        cursor.execute("ALTER SEQUENCE customers_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE conversation_contexts_id_seq RESTART WITH 1")
        
        # Commit das alterações
        conn.commit()
        
        cursor.close()
        conn.close()
        
        total_removed = clients_before + conversations_before
        
        logger.warning(LogCategory.SYSTEM, f"BANCO LIMPO! {total_removed} registros removidos")
        
        return jsonify({
            'success': True,
            'message': 'Banco de dados limpo com sucesso',
            'removed_count': total_removed,
            'details': {
                'clients_removed': clients_before,
                'conversations_removed': conversations_before
            }
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao limpar banco: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@admin_blueprint.route('/admin/database/export', methods=['GET'])
def export_database():
    """Exportar todos os dados do banco como JSON"""
    try:
        logger.info(LogCategory.SYSTEM, "Iniciando exportação do banco de dados")
        
        # Conectar ao banco
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Exportar clientes
        cursor.execute("SELECT * FROM customers")
        clients = []
        for row in cursor.fetchall():
            clients.append({
                'id': row[0],
                'protocolo': row[1],
                'first_name': row[2],
                'documento': row[3],
                'cobrado_fpd': float(row[4]) if row[4] else 0,
                'dias_fpd': int(row[5]) if row[5] else 0,
                'data_vencimento_fpd': row[6].isoformat() if row[6] else None,
                'contrato': row[7],
                'regional': row[8],
                'territorio': row[9],
                'dsc_plano': row[10],
                'valor_mensalidade': float(row[11]) if row[11] else 0,
                'empresa': row[12],
                'status': row[13],
                'priority': int(row[14]) if row[14] else 0,
                'is_customer': bool(row[15]) if row[15] else False,
                'last_contact': row[16].isoformat() if row[16] else None,
                'conversation_count': int(row[17]) if row[17] else 0,
                'payment_promises': int(row[18]) if row[18] else 0,
                'last_payment_date': row[19].isoformat() if row[19] else None,
                'created_at': row[20].isoformat() if row[20] else None,
                'updated_at': row[21].isoformat() if row[21] else None
            })
        
        # Exportar conversas
        cursor.execute("SELECT * FROM conversation_contexts")
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row[0],
                'phone': row[1],
                'session_id': row[2],
                'user_name': row[3],
                'started_at': row[4].isoformat() if row[4] else None,
                'last_activity': row[5].isoformat() if row[5] else None,
                'message_count': int(row[6]) if row[6] else 0,
                'payment_amount': float(row[7]) if row[7] else 0,
                'due_date': row[8].isoformat() if row[8] else None,
                'topics_discussed': row[9] if row[9] else [],
                'intent_history': row[10] if row[10] else [],
                'sentiment_history': row[11] if row[11] else [],
                'created_at': row[12].isoformat() if row[12] else None,
                'updated_at': row[13].isoformat() if row[13] else None
            })
        
        cursor.close()
        conn.close()
        
        # Preparar dados para exportação
        from datetime import datetime
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_records': len(clients) + len(conversations),
            'clients': clients,
            'conversations': conversations
        }
        
        logger.info(LogCategory.SYSTEM, f"Exportação concluída: {len(clients)} clientes, {len(conversations)} conversas")
        
        # Retornar como arquivo JSON para download
        from flask import Response
        import json
        
        response = Response(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename=database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'}
        )
        
        return response
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao exportar banco: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
