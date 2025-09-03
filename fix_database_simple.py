#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para corrigir tabela customers
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.database_manager import DatabaseManager

def main():
    print("🔧 CORREÇÃO DA TABELA CUSTOMERS")
    print("=" * 50)
    
    try:
        # Usar o DatabaseManager existente
        db = DatabaseManager()
        
        print("🔗 Conectando ao banco...")
        
        # Verificar tabela atual
        query_check = """
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'customers'
            ORDER BY ordinal_position;
        """
        
        result = db.execute_query(query_check)
        
        if result:
            print("📋 Estrutura atual da tabela 'customers':")
            print("=" * 40)
            for row in result:
                print(f"  {row[0]} | {row[1]}")
        
        # Contar registros
        count_query = "SELECT COUNT(*) FROM customers;"
        count_result = db.execute_query(count_query)
        if count_result:
            print(f"\n📈 Total de registros: {count_result[0][0]}")
        
        print(f"\n⚠️ ATENÇÃO: Vou DELETAR todos os dados e recriar a tabela!")
        print("🎯 Nova estrutura será adequada ao formato do arquivo JSON")
        
        # Dropar e recriar tabela
        print("\n🗑️ Removendo tabela antiga...")
        db.execute_query("DROP TABLE IF EXISTS customers CASCADE;")
        
        # Criar nova tabela
        print("🏗️ Criando nova tabela 'customers'...")
        create_table_sql = """
            CREATE TABLE customers (
                id SERIAL PRIMARY KEY,
                
                -- Dados do protocolo/tipo
                tipo VARCHAR(50),
                protocolo VARCHAR(100) UNIQUE,
                
                -- Dados essenciais
                first_name VARCHAR(255),
                documento_essencial VARCHAR(20),
                dsc_cidade_inst VARCHAR(255),
                dsc_plano VARCHAR(255),
                valor_mensalidade DECIMAL(10,2),
                
                -- Dados de vendas
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
                
                -- Campos específicos
                fpd VARCHAR(50),
                aba_origem VARCHAR(100),
                status VARCHAR(50),
                observacoes TEXT,
                
                -- Metadados
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP
            );
        """
        
        db.execute_query(create_table_sql)
        
        # Criar índices
        print("📊 Criando índices...")
        indices = [
            "CREATE INDEX idx_customers_protocolo ON customers(protocolo);",
            "CREATE INDEX idx_customers_documento ON customers(documento);",
            "CREATE INDEX idx_customers_telefone1 ON customers(telefone1);",
            "CREATE INDEX idx_customers_email ON customers(email);",
            "CREATE INDEX idx_customers_status ON customers(status);",
            "CREATE INDEX idx_customers_fpd ON customers(fpd);"
        ]
        
        for idx_sql in indices:
            db.execute_query(idx_sql)
        
        # Verificar nova estrutura
        new_result = db.execute_query(query_check)
        
        print("\n✅ Nova tabela 'customers' criada!")
        print("📋 Nova estrutura:")
        print("=" * 40)
        for row in new_result:
            print(f"  {row[0]} | {row[1]}")
        
        print(f"\n🎉 CONCLUÍDO! Tabela adequada ao formato JSON!")
        print("📄 Agora você pode fazer upload do arquivo resultado_cruzamento_20250903_114254.json")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
