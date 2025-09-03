#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir tabela APENAS para dados_vendas - FODA-SE O RESTO!
"""

import psycopg2

def main():
    print("🎯 TABELA APENAS PARA DADOS_VENDAS")
    print("=" * 50)
    
    # URL de conexão Railway
    database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@hopper.proxy.rlwy.net:34660/railway"
    
    try:
        print("🔗 Conectando...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("🗑️ DELETANDO tabela antiga...")
        cursor.execute("DROP TABLE IF EXISTS customers CASCADE;")
        
        print("🏗️ Criando tabela APENAS para dados_vendas...")
        cursor.execute("""
            CREATE TABLE customers (
                id SERIAL PRIMARY KEY,
                
                -- APENAS CAMPOS DOS dados_vendas - FODA-SE O RESTO!
                nome VARCHAR(255) NOT NULL,                    -- NOME
                documento VARCHAR(20),                         -- DOCUMENTO  
                telefone1 VARCHAR(50),                        -- TELEFONE1
                telefone2 VARCHAR(50),                        -- TELEFONE2
                email VARCHAR(255),                           -- EMAIL
                rua_endereco TEXT,                            -- RUA / ENDEREÇO
                cidade VARCHAR(255),                          -- CIDADE
                cep VARCHAR(20),                              -- CEP
                data_nascimento VARCHAR(20),                  -- DATA NASCIMENTO
                status VARCHAR(50),                           -- STATUS
                origem_venda VARCHAR(100),                    -- ORIGEM DA VENDA
                contrato VARCHAR(50),                         -- CONTRATO
                data_agenda VARCHAR(50),                      -- DATA AGENDA
                obs TEXT,                                     -- OBS
                aba_origem VARCHAR(100),                      -- aba_origem
                spd VARCHAR(10),                              -- spd
                
                -- Só metadados básicos
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        print("📊 Criando índices essenciais...")
        indices = [
            "CREATE INDEX idx_customers_documento ON customers(documento);",
            "CREATE INDEX idx_customers_telefone1 ON customers(telefone1);", 
            "CREATE INDEX idx_customers_email ON customers(email);",
            "CREATE INDEX idx_customers_status ON customers(status);",
            "CREATE INDEX idx_customers_nome ON customers(nome);",
            "CREATE INDEX idx_customers_contrato ON customers(contrato);"
        ]
        
        for idx_sql in indices:
            cursor.execute(idx_sql)
        
        conn.commit()
        
        # Verificar estrutura
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'customers'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n✅ NOVA ESTRUTURA - SÓ DADOS_VENDAS:")
        print("-" * 50)
        for col in columns:
            print(f"  {col[0]:<20} | {col[1]}")
        
        print(f"\n🎯 PRONTO! Tabela focada APENAS em dados_vendas!")
        print("📄 Campos exatos do JSON resultado_cruzamento_20250903_114254.json")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
