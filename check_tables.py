#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar estrutura das tabelas existentes no banco
"""

import psycopg2

def check_table_structure():
    """Verifica estrutura das tabelas existentes"""
    print("🔍 VERIFICANDO ESTRUTURA DAS TABELAS")
    print("=" * 50)
    
    # Conectar ao banco
    database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@hopper.proxy.rlwy.net:34660/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Verificar tabela customers
        print("\n📋 TABELA 'customers':")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'customers' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # Verificar tabela conversations
        print("\n📋 TABELA 'conversations':")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'conversations' 
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2] == 'YES' else 'NOT NULL'})")
        
        # Verificar dados existentes
        print("\n📊 DADOS EXISTENTES:")
        cursor.execute("SELECT COUNT(*) FROM customers")
        customers_count = cursor.fetchone()[0]
        print(f"  - Clientes: {customers_count}")
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversations_count = cursor.fetchone()[0]
        print(f"  - Conversas: {conversations_count}")
        
        if customers_count > 0:
            print("\n👥 EXEMPLO DE CLIENTE:")
            cursor.execute("SELECT * FROM customers LIMIT 1")
            customer = cursor.fetchone()
            print(f"  {customer}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    check_table_structure()

