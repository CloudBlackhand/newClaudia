#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir estrutura da tabela customers
Adequar ao formato do resultado_cruzamento_20250903_114254.json
"""

import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def connect_to_database():
    """Conectar ao banco PostgreSQL"""
    # Usar DATABASE_URL do Railway via variável de ambiente
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        # Fallback para URL direta se não tiver variável
        database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@postgres.railway.internal:5432/railway"
    
    try:
        print(f"🔗 Conectando ao banco...")
        conn = psycopg2.connect(database_url)
        print("✅ Conectado com sucesso!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return None

def check_current_structure(conn):
    """Verificar estrutura atual da tabela customers"""
    cursor = conn.cursor()
    
    try:
        # Verificar se tabela existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'customers'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        print(f"📋 Tabela 'customers' existe: {table_exists}")
        
        if table_exists:
            # Verificar estrutura atual
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'customers'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📊 Estrutura atual da tabela 'customers':")
            print("=" * 60)
            for col in columns:
                print(f"  {col[0]} | {col[1]} | Nullable: {col[2]} | Default: {col[3]}")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM customers;")
            count = cursor.fetchone()[0]
            print(f"\n📈 Total de registros: {count}")
            
            return columns
        else:
            print("⚠️ Tabela 'customers' não existe")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return None
    finally:
        cursor.close()

def create_new_customers_table(conn):
    """Criar nova tabela customers adequada ao formato JSON"""
    cursor = conn.cursor()
    
    try:
        # Dropar tabela existente se necessário
        print("\n🗑️ Removendo tabela antiga...")
        cursor.execute("DROP TABLE IF EXISTS customers CASCADE;")
        
        # Criar nova tabela baseada no formato do JSON
        print("🏗️ Criando nova tabela 'customers'...")
        cursor.execute("""
            CREATE TABLE customers (
                id SERIAL PRIMARY KEY,
                
                -- Dados do protocolo/tipo
                tipo VARCHAR(50),
                protocolo VARCHAR(100) UNIQUE,
                
                -- Dados essenciais (do campo dados_essenciais)
                first_name VARCHAR(255),
                documento_essencial VARCHAR(20), -- documento mascarado
                dsc_cidade_inst VARCHAR(255),
                dsc_plano VARCHAR(255),
                valor_mensalidade DECIMAL(10,2),
                
                -- Dados de vendas (do campo dados_vendas)
                nome VARCHAR(255) NOT NULL,
                documento VARCHAR(20),
                telefone1 VARCHAR(50),
                telefone2 VARCHAR(50),
                email VARCHAR(255),
                rua_endereco TEXT,
                cidade VARCHAR(255),
                cep VARCHAR(20),
                bairro VARCHAR(255),
                uf VARCHAR(5),
                
                -- Campos específicos de vendas
                fpd VARCHAR(50),
                aba_origem VARCHAR(100),
                status VARCHAR(50),
                observacoes TEXT,
                
                -- Metadados
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                
                -- Índices para performance
                CONSTRAINT unique_documento UNIQUE(documento),
                CONSTRAINT unique_protocolo_documento UNIQUE(protocolo, documento)
            );
        """)
        
        # Criar índices
        print("📊 Criando índices...")
        cursor.execute("""
            CREATE INDEX idx_customers_protocolo ON customers(protocolo);
            CREATE INDEX idx_customers_documento ON customers(documento);
            CREATE INDEX idx_customers_telefone1 ON customers(telefone1);
            CREATE INDEX idx_customers_email ON customers(email);
            CREATE INDEX idx_customers_status ON customers(status);
            CREATE INDEX idx_customers_fpd ON customers(fpd);
            CREATE INDEX idx_customers_created_at ON customers(created_at);
        """)
        
        # Commit das mudanças
        conn.commit()
        print("✅ Nova tabela 'customers' criada com sucesso!")
        
        # Mostrar estrutura final
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'customers'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 Nova estrutura da tabela 'customers':")
        print("=" * 60)
        for col in columns:
            print(f"  {col[0]} | {col[1]} | Nullable: {col[2]} | Default: {col[3]}")
            
    except Exception as e:
        print(f"❌ Erro ao criar nova tabela: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    print("🔧 CORREÇÃO DA TABELA CUSTOMERS")
    print("=" * 50)
    
    # Conectar ao banco
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Verificar estrutura atual
        current_structure = check_current_structure(conn)
        
        # Confirmar se deve recriar a tabela
        print(f"\n⚠️ ATENÇÃO: Isso vai DELETAR todos os dados da tabela 'customers'!")
        print("🎯 Nova estrutura será adequada ao formato do arquivo JSON")
        
        # Recriar tabela
        create_new_customers_table(conn)
        
        print("\n🎉 CONCLUÍDO! Tabela 'customers' adequada ao formato JSON!")
        print("📄 Agora você pode fazer upload do arquivo resultado_cruzamento_20250903_114254.json")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()
