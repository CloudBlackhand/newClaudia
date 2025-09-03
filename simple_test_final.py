#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste final do sistema de banco de dados
"""

import psycopg2
from datetime import datetime

def test_system():
    """Testa o sistema completo"""
    print("🧪 TESTE FINAL DO SISTEMA")
    print("=" * 50)
    
    # Conectar ao banco
    database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@hopper.proxy.rlwy.net:34660/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        print("✅ Conectado ao banco!")
        
        # Testar inserção de cliente
        print("\n📝 TESTANDO INSERÇÃO DE CLIENTE:")
        
        # Dados do cliente (estrutura do banco existente)
        customer_data = {
            'protocolo': '12345',
            'first_name': 'João Silva Teste',
            'documento': '123.456.789-00',
            'cobrado_fpd': 1500.00,
            'dias_fpd': 45,
            'data_vencimento_fpd': '2024-08-15',
            'contrato': '67890',
            'regional': 'Central',
            'territorio': 'São Paulo',
            'dsc_plano': 'Fibra 600M',
            'valor_mensalidade': 99.99,
            'empresa': 'DESKTOP_SF',
            'status': 'active',
            'priority': 'high',
            'is_customer': True,
            'last_contact': datetime.now(),
            'conversation_count': 0,
            'payment_promises': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Inserir cliente
        cursor.execute("""
            INSERT INTO customers (
                protocolo, first_name, documento, cobrado_fpd, dias_fpd,
                data_vencimento_fpd, contrato, regional, territorio, dsc_plano, 
                valor_mensalidade, empresa, status, priority, is_customer, last_contact,
                conversation_count, payment_promises, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_data['protocolo'], customer_data['first_name'], customer_data['documento'],
            customer_data['cobrado_fpd'], customer_data['dias_fpd'], customer_data['data_vencimento_fpd'],
            customer_data['contrato'], customer_data['regional'], customer_data['territorio'],
            customer_data['dsc_plano'], customer_data['valor_mensalidade'], customer_data['empresa'],
            customer_data['status'], customer_data['priority'], customer_data['is_customer'],
            customer_data['last_contact'], customer_data['conversation_count'], customer_data['payment_promises'],
            customer_data['created_at'], customer_data['updated_at']
        ))
        
        conn.commit()
        print("✅ Cliente inserido com sucesso!")
        
        # Buscar cliente
        print("\n🔍 TESTANDO BUSCA DE CLIENTE:")
        cursor.execute("SELECT * FROM customers WHERE protocolo = %s", ('12345',))
        customer = cursor.fetchone()
        
        if customer:
            print(f"✅ Cliente encontrado: {customer[3]} - R$ {customer[22]}")
        else:
            print("❌ Cliente não encontrado")
        
        # Testar conversa
        print("\n💬 TESTANDO INSERÇÃO DE CONVERSA:")
        cursor.execute("""
            INSERT INTO conversations (
                customer_protocolo, customer_name, message, response, 
                intent, sentiment, cooperation_level, success, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            '12345', 'João Silva Teste', 'Olá, preciso de ajuda',
            'Olá! Como posso ajudá-lo?', 'SAUDACAO', 'POSITIVO', 0.8, True, datetime.now()
        ))
        
        conn.commit()
        print("✅ Conversa inserida com sucesso!")
        
        # Limpar teste
        print("\n🗑️ LIMPANDO DADOS DE TESTE:")
        cursor.execute("DELETE FROM conversations WHERE customer_protocolo = %s", ('12345',))
        cursor.execute("DELETE FROM customers WHERE protocolo = %s", ('12345',))
        conn.commit()
        print("✅ Dados de teste removidos!")
        
        cursor.close()
        conn.close()
        print("\n🎉 TESTE COMPLETO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system()

