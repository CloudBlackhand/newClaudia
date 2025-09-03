#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples de conexão com PostgreSQL do Railway
"""

import psycopg2

def test_connection():
    """Testa conexão direta"""
    print("🧪 TESTE SIMPLES DE CONEXÃO")
    print("=" * 40)
    
    # String de conexão do Railway (URL pública)
    database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@hopper.proxy.rlwy.net:34660/railway"
    
    try:
        print("🔗 Conectando ao banco...")
        conn = psycopg2.connect(database_url)
        print("✅ CONEXÃO BEM-SUCEDIDA!")
        
        # Testar query
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL: {version[0]}")
        
        # Testar tabelas
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = cursor.fetchall()
        print(f"📋 Tabelas existentes: {[t[0] for t in tables]}")
        
        cursor.close()
        conn.close()
        print("🔌 Conexão fechada")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_connection()
