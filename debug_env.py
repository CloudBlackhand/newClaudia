#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug das variáveis de ambiente do Railway
"""

import os

def debug_environment():
    """Debug das variáveis de ambiente"""
    print("🔍 DEBUG DAS VARIÁVEIS DE AMBIENTE")
    print("=" * 50)
    
    # Variáveis do Railway
    railway_vars = [
        'DATABASE_URL',
        'PGHOST', 
        'PGPORT',
        'PGDATABASE',
        'PGUSER',
        'PGPASSWORD'
    ]
    
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            # Mascarar senha
            if 'PASSWORD' in var:
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NÃO DEFINIDA")
    
    print("\n🔍 VERIFICANDO CONEXÃO:")
    
    # Tentar conectar diretamente
    try:
        import psycopg2
        
        # Usar DATABASE_URL do Railway
        database_url = os.getenv('DATABASE_URL')
        if database_url and 'localhost' not in database_url:
            print(f"🔗 Tentando conectar via DATABASE_URL...")
            print(f"URL: {database_url[:50]}...")
            
            conn = psycopg2.connect(database_url)
            print("🎉 CONEXÃO BEM-SUCEDIDA!")
            
            # Testar query simples
            cursor = conn.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print(f"📊 Versão PostgreSQL: {version[0]}")
            
            cursor.close()
            conn.close()
            
        else:
            print("❌ DATABASE_URL não encontrada ou é localhost")
            
    except ImportError:
        print("❌ psycopg2 não instalado")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")

if __name__ == "__main__":
    debug_environment()
