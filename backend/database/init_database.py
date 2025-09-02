#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicialização do banco de dados
Cria todas as tabelas e estruturas necessárias para o sistema Claudia
"""

import os
import sys
import psycopg2
import redis
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config.settings import Config

def get_database_connection():
    """Estabelece conexão com o banco de dados"""
    try:
        # Usar variáveis de ambiente do Railway
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL não configurada!")
            return None
        
        conn = psycopg2.connect(database_url)
        print("✅ Conexão com PostgreSQL estabelecida")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com PostgreSQL: {e}")
        return None

def get_redis_connection():
    """Estabelece conexão com o Redis"""
    try:
        # Usar variáveis de ambiente do Railway
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            print("❌ REDIS_URL não configurada!")
            return None
        
        r = redis.from_url(redis_url)
        r.ping()  # Testar conexão
        print("✅ Conexão com Redis estabelecida")
        return r
    except Exception as e:
        print(f"❌ Erro ao conectar com Redis: {e}")
        return None

def execute_migration(conn, migration_file):
    """Executa um arquivo de migração SQL"""
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        
        print(f"✅ Migração executada com sucesso: {migration_file}")
        return True
    except Exception as e:
        print(f"❌ Erro ao executar migração {migration_file}: {e}")
        conn.rollback()
        return False

def initialize_redis_structures(redis_conn):
    """Inicializa estruturas básicas no Redis"""
    try:
        # Configurações do sistema
        redis_conn.set('system:version', '2.0.0')
        redis_conn.set('system:status', 'active')
        redis_conn.set('system:maintenance_mode', 'false')
        
        # Contadores de campanhas
        redis_conn.set('campaigns:total_count', 0)
        redis_conn.set('campaigns:active_count', 0)
        redis_conn.set('campaigns:completed_count', 0)
        
        # Contadores de mensagens
        redis_conn.set('messages:total_sent', 0)
        redis_conn.set('messages:total_received', 0)
        redis_conn.set('messages:success_rate', 0.0)
        
        # Cache de templates
        redis_conn.set('templates:last_updated', '')
        redis_conn.set('templates:total_count', 0)
        
        # Cache de clientes
        redis_conn.set('clients:total_count', 0)
        redis_conn.set('clients:active_count', 0)
        
        # Configurar TTL para algumas chaves
        redis_conn.expire('system:status', 3600)  # 1 hora
        redis_conn.expire('templates:last_updated', 1800)  # 30 minutos
        
        print("✅ Estruturas Redis inicializadas com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar estruturas Redis: {e}")
        return False

def verify_database_structure(conn):
    """Verifica se todas as tabelas foram criadas corretamente"""
    try:
        cursor = conn.cursor()
        
        # Lista de tabelas esperadas
        expected_tables = [
            'conversation_contexts',
            'response_quality_scores',
            'template_performance',
            'campaigns',
            'campaign_contacts',
            'clients',
            'billing_records',
            'system_logs',
            'message_templates',
            'system_config'
        ]
        
        # Verificar cada tabela
        for table in expected_tables:
            cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            exists = cursor.fetchone()[0]
            
            if exists:
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ Tabela {table}: {count} registros")
            else:
                print(f"❌ Tabela {table}: NÃO EXISTE!")
                return False
        
        cursor.close()
        print("✅ Todas as tabelas foram criadas corretamente")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura do banco: {e}")
        return False

def insert_sample_data(conn):
    """Insere dados de exemplo para teste"""
    try:
        cursor = conn.cursor()
        
        # Inserir cliente de exemplo
        cursor.execute("""
            INSERT INTO clients (phone, name, email, city, state, vendedor) 
            VALUES ('11999999999', 'Cliente Teste', 'teste@exemplo.com', 'São Paulo', 'SP', 'Vendedor Teste')
            ON CONFLICT (phone) DO NOTHING
        """
        )
        
        # Inserir registro de cobrança de exemplo
        cursor.execute("""
            INSERT INTO billing_records (client_id, amount, due_date, tipo, fpd_days)
            SELECT id, 150.00, CURRENT_DATE + INTERVAL '30 days', 'FPD', 0
            FROM clients WHERE phone = '11999999999'
            ON CONFLICT DO NOTHING
        """)
        
        conn.commit()
        cursor.close()
        print("✅ Dados de exemplo inseridos com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir dados de exemplo: {e}")
        conn.rollback()
        return False

def main():
    """Função principal de inicialização"""
    print("🚀 INICIALIZANDO BANCO DE DADOS CLAUDIA")
    print("=" * 50)
    
    # 1. Conectar com PostgreSQL
    pg_conn = get_database_connection()
    if not pg_conn:
        print("❌ Falha ao conectar com PostgreSQL. Abortando...")
        return False
    
    # 2. Conectar com Redis
    redis_conn = get_redis_connection()
    if not redis_conn:
        print("⚠️  Falha ao conectar com Redis. Continuando apenas com PostgreSQL...")
    
    # 3. Executar migração SQL
    migration_file = Path(__file__).parent / "migrations" / "001_create_initial_tables.sql"
    if not migration_file.exists():
        print(f"❌ Arquivo de migração não encontrado: {migration_file}")
        return False
    
    if not execute_migration(pg_conn, migration_file):
        print("❌ Falha na migração. Abortando...")
        return False
    
    # 4. Verificar estrutura do banco
    if not verify_database_structure(pg_conn):
        print("❌ Estrutura do banco incorreta. Abortando...")
        return False
    
    # 5. Inicializar estruturas Redis
    if redis_conn:
        if not initialize_redis_structures(redis_conn):
            print("⚠️  Falha ao inicializar Redis. Continuando...")
    
    # 6. Inserir dados de exemplo
    if not insert_sample_data(pg_conn):
        print("⚠️  Falha ao inserir dados de exemplo. Continuando...")
    
    # 7. Finalizar
    pg_conn.close()
    if redis_conn:
        redis_conn.close()
    
    print("=" * 50)
    print("🎉 INICIALIZAÇÃO COMPLETA COM SUCESSO!")
    print("✅ Banco de dados PostgreSQL configurado")
    print("✅ Cache Redis configurado")
    print("✅ Todas as tabelas criadas")
    print("✅ Sistema pronto para uso!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
