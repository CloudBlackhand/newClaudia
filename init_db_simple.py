#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para inicializar banco de dados no Railway
"""

import os
import sys
import psycopg2
import redis
from pathlib import Path

def main():
    print("🚀 INICIALIZANDO BANCO DE DADOS NO RAILWAY")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    database_url = os.getenv('DATABASE_URL')
    redis_url = os.getenv('REDIS_URL')
    
    if not database_url:
        print("❌ DATABASE_URL não encontrada")
        return False
    
    if not redis_url:
        print("❌ REDIS_URL não encontrada")
        return False
    
    print(f"✅ DATABASE_URL: {database_url[:20]}...")
    print(f"✅ REDIS_URL: {redis_url[:20]}...")
    
    try:
        # 1. Conectar ao PostgreSQL
        print("\n🔍 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Conectado ao PostgreSQL!")
        
        # 2. Criar tabelas básicas
        print("\n🔧 Criando tabelas...")
        
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
        print("🔧 Criando índices...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversation_phone ON conversation_contexts(phone);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_id ON campaigns(campaign_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_campaign ON messages(campaign_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_learning_phone ON learning_data(phone);")
        
        # Commit das mudanças
        conn.commit()
        print("✅ Tabelas criadas com sucesso!")
        
        # 3. Conectar ao Redis
        print("\n🔍 Conectando ao Redis...")
        redis_client = redis.from_url(redis_url)
        
        # Testar conexão Redis
        redis_client.ping()
        print("✅ Conectado ao Redis!")
        
        # 4. Configurar estruturas iniciais do Redis
        print("\n🔧 Configurando Redis...")
        redis_client.set("system:initialized", "true")
        redis_client.set("system:version", "2.0")
        redis_client.set("campaigns:active_count", "0")
        redis_client.set("messages:sent_today", "0")
        redis_client.set("messages:failed_today", "0")
        
        print("✅ Redis configurado!")
        
        # 5. Inserir dados de exemplo
        print("\n🔧 Inserindo dados de exemplo...")
        
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
        print("✅ Dados de exemplo inseridos!")
        
        # 6. Verificar estrutura
        print("\n🔍 Verificando estrutura criada...")
        
        cursor.execute("SELECT COUNT(*) FROM conversation_contexts;")
        contexts_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM campaigns;")
        campaigns_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages;")
        messages_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM learning_data;")
        learning_count = cursor.fetchone()[0]
        
        print(f"✅ Contextos de conversa: {contexts_count}")
        print(f"✅ Campanhas: {campaigns_count}")
        print(f"✅ Mensagens: {messages_count}")
        print(f"✅ Dados de aprendizado: {learning_count}")
        
        # Fechar conexões
        cursor.close()
        conn.close()
        
        print("\n🎉 INICIALIZAÇÃO COMPLETA!")
        print("✅ PostgreSQL configurado com todas as tabelas")
        print("✅ Redis configurado com estruturas iniciais")
        print("✅ Sistema pronto para funcionar!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante inicialização: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
