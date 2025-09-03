#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recriar tabela customers adequada ao JSON
"""

import psycopg2
import os
import sys

def main():
    print("🔧 RECRIANDO TABELA CUSTOMERS")
    print("=" * 50)
    
    # URL de conexão direta (pública do Railway)
    database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@hopper.proxy.rlwy.net:34660/railway"
    
    try:
        print("🔗 Conectando ao banco PostgreSQL...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Conectado com sucesso!")
        
        # Verificar tabela atual
        print("\n📋 Verificando tabela atual...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'customers'
            ORDER BY ordinal_position;
        """)
        
        current_columns = cursor.fetchall()
        if current_columns:
            print("Colunas atuais:")
            for col in current_columns:
                print(f"  - {col[0]} ({col[1]})")
            
            # Contar registros
            cursor.execute("SELECT COUNT(*) FROM customers;")
            count = cursor.fetchone()[0]
            print(f"📊 Registros atuais: {count}")
        else:
            print("⚠️ Tabela 'customers' não existe")
        
        print(f"\n🚨 ATENÇÃO: Vou DELETAR a tabela atual e recriar!")
        print("🎯 Nova estrutura para o formato do arquivo JSON")
        
        # Dropar tabela
        print("\n🗑️ Removendo tabela antiga...")
        cursor.execute("DROP TABLE IF EXISTS customers CASCADE;")
        
        # Criar nova tabela
        print("🏗️ Criando nova tabela...")
        cursor.execute("""
            CREATE TABLE customers (
                id SERIAL PRIMARY KEY,
                
                -- Dados do protocolo/tipo
                tipo VARCHAR(50),
                protocolo VARCHAR(100) UNIQUE,
                
                -- Dados essenciais (do JSON dados_essenciais)
                first_name VARCHAR(255),
                documento_essencial VARCHAR(20), -- documento mascarado
                dsc_cidade_inst VARCHAR(255),
                dsc_plano VARCHAR(255),
                valor_mensalidade DECIMAL(10,2),
                
                -- Dados de vendas (do JSON dados_vendas)
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
                
                -- Constraints
                CONSTRAINT unique_protocolo_documento UNIQUE(protocolo, documento)
            );
        """)
        
        print("📊 Criando índices para performance...")
        indices = [
            "CREATE INDEX idx_customers_protocolo ON customers(protocolo);",
            "CREATE INDEX idx_customers_documento ON customers(documento);", 
            "CREATE INDEX idx_customers_telefone1 ON customers(telefone1);",
            "CREATE INDEX idx_customers_email ON customers(email);",
            "CREATE INDEX idx_customers_status ON customers(status);",
            "CREATE INDEX idx_customers_fpd ON customers(fpd);",
            "CREATE INDEX idx_customers_nome ON customers(nome);",
            "CREATE INDEX idx_customers_created_at ON customers(created_at);"
        ]
        
        for idx_sql in indices:
            cursor.execute(idx_sql)
        
        # Commit
        conn.commit()
        
        # Verificar nova estrutura
        print("\n📋 Verificando nova estrutura...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'customers'
            ORDER BY ordinal_position;
        """)
        
        new_columns = cursor.fetchall()
        print("✅ Nova estrutura da tabela 'customers':")
        print("-" * 60)
        for col in new_columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"  {col[0]:<25} | {col[1]:<15} | {nullable}")
        
        print(f"\n🎉 TABELA RECRIADA COM SUCESSO!")
        print("📄 Estrutura adequada ao arquivo resultado_cruzamento_20250903_114254.json")
        print("🚀 Pronto para receber os dados de vendas!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
