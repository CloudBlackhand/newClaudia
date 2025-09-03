#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para fazer upload dos dados limpos para o banco PostgreSQL
"""

import json
import psycopg2
from datetime import datetime

def connect_to_database():
    """Conecta ao banco PostgreSQL"""
    database_url = "postgresql://postgres:KQBgHeNvKIVDPRzmrXVgzXtPFLbCeMeX@hopper.proxy.rlwy.net:34660/railway"
    
    try:
        conn = psycopg2.connect(database_url)
        print("✅ Conectado ao banco PostgreSQL!")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def upload_customers_to_database(conn, customers_data):
    """Faz upload dos clientes para o banco"""
    cursor = conn.cursor()
    
    print(f"🚀 INICIANDO UPLOAD DE {len(customers_data)} CLIENTES...")
    
    success_count = 0
    error_count = 0
    
    for i, customer in enumerate(customers_data, 1):
        try:
            dados_fpd = customer.get('dados_fpd', {})
            
            # Extrair dados do cliente (usando apenas colunas que existem)
            customer_info = {
                'tipo': customer.get('tipo', ''),
                'protocolo': str(customer.get('protocolo', '')),
                'first_name': dados_fpd.get('first_name', ''),
                'documento': dados_fpd.get('documento', ''),
                'num_cliente': dados_fpd.get('num_cliente', ''),
                'contrato': dados_fpd.get('contrato', ''),
                'num_adm': dados_fpd.get('num_adm', ''),
                'num_migrado': dados_fpd.get('num_migrado', ''),
                'segmento': dados_fpd.get('segmento', ''),
                'data_contrato': dados_fpd.get('data_contrato'),
                'data_ativacao': dados_fpd.get('data_ativacao'),
                'dsc_plano': dados_fpd.get('dsc_plano', ''),
                'valor_plano': dados_fpd.get('valor_plano', ''),
                'valor_promocao': dados_fpd.get('valor_promocao', ''),
                'valor_mensalidade': dados_fpd.get('valor_mensalidade', ''),
                'dsc_tipo_contrato': dados_fpd.get('dsc_tipo_contrato', ''),
                'regional': dados_fpd.get('regional', ''),
                'territorio': dados_fpd.get('territorio', ''),
                'dsc_cidade_inst': dados_fpd.get('dsc_cidade_inst', ''),
                'estado_inst': dados_fpd.get('estado_inst', ''),
                'regional_inst': dados_fpd.get('regional_inst', ''),
                'cobrado_fpd': dados_fpd.get('cobrado_fpd', ''),
                'pago_fpd': dados_fpd.get('pago_fpd', ''),
                'data_vencimento_fpd': dados_fpd.get('data_vencimento_fpd'),
                'data_pagamento_fpd': dados_fpd.get('data_pagamento_fpd'),
                'dias_fpd': dados_fpd.get('dias_fpd', ''),
                'faixa_pgto_fpd': dados_fpd.get('faixa_pgto_fpd', ''),
                'fpd': dados_fpd.get('fpd', ''),
                'fpd_20': dados_fpd.get('fpd_20', ''),
                'fpd_10': dados_fpd.get('fpd_10', ''),
                'fpd_5': dados_fpd.get('fpd_5', ''),
                'fpd_spd': dados_fpd.get('fpd_spd', ''),
                'cobrado_spd': dados_fpd.get('cobrado_spd', ''),
                'pago_spd': dados_fpd.get('pago_spd', ''),
                'data_vencimento_spd': dados_fpd.get('data_vencimento_spd'),
                'data_pagamento_spd': dados_fpd.get('data_pagamento_spd'),
                'dias_spd': dados_fpd.get('dias_spd', ''),
                'faixa_pgto_spd': dados_fpd.get('faixa_pgto_spd', ''),
                'spd': dados_fpd.get('spd', ''),
                'cliente_cancelado': dados_fpd.get('cliente_cancelado', ''),
                'cliente_bloqueado': dados_fpd.get('cliente_bloqueado', ''),
                'cliente_possui_app': dados_fpd.get('cliente_possui_app', ''),
                'cliente_preventivo': dados_fpd.get('cliente_preventivo', ''),
                'cliente_preventivo_spd': dados_fpd.get('cliente_preventivo_spd', ''),
                'data_bloqueio': dados_fpd.get('data_bloqueio'),
                'flag_app': dados_fpd.get('flag_app', ''),
                'data_app': dados_fpd.get('data_app'),
                'grupo_acao_preventivo': dados_fpd.get('grupo_acao_preventivo', ''),
                'preventivo': dados_fpd.get('preventivo', ''),
                'preventivo_agrupado': dados_fpd.get('preventivo_agrupado', ''),
                'grupo_acao_preventivo_spd': dados_fpd.get('grupo_acao_preventivo_spd', ''),
                'preventivo_spd': dados_fpd.get('preventivo_spd', ''),
                'preventivo_agrupado_spd': dados_fpd.get('preventivo_agrupado_spd', ''),
                'cod_login_vendedor': dados_fpd.get('cod_login_vendedor', ''),
                'dsc_vendedor_ger': dados_fpd.get('dsc_vendedor_ger', ''),
                'canal_de_venda_ger': dados_fpd.get('canal_de_venda_ger', ''),
                'canal': dados_fpd.get('canal', ''),
                'dsc_nome_supervisor': dados_fpd.get('dsc_nome_supervisor', ''),
                'dsc_nome_gerente': dados_fpd.get('dsc_nome_gerente', ''),
                'canal_vendedor': dados_fpd.get('canal_vendedor', ''),
                'canal_hierarquia': dados_fpd.get('canal_hierarquia', ''),
                'canal_sistemico': dados_fpd.get('canal_sistemico', ''),
                'id_vendedor_hierarquia': dados_fpd.get('id_vendedor_hierarquia', ''),
                'nome_vendedor_hierarquia': dados_fpd.get('nome_vendedor_hierarquia', ''),
                'coordenador_hierarquia': dados_fpd.get('coordenador_hierarquia', ''),
                'gerente_hierarquia': dados_fpd.get('gerente_hierarquia', ''),
                'regional_hierarquia': dados_fpd.get('regional_hierarquia', ''),
                'territorio_hierarquia': dados_fpd.get('territorio_hierarquia', ''),
                'linha_boleto': dados_fpd.get('linha_boleto', ''),
                'pix': dados_fpd.get('pix', ''),
                'mes_ativacao': dados_fpd.get('mes_ativacao'),
                'empresa': dados_fpd.get('empresa', ''),
                'dsc_origem_venda': dados_fpd.get('dsc_origem_venda', ''),
                'atualizacao_tabela': dados_fpd.get('atualizacao_tabela'),
                'qtd': dados_fpd.get('qtd', ''),
                'dados_vendas': json.dumps(customer.get('dados_vendas', [])),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Verificar se cliente já existe
            cursor.execute("SELECT protocolo FROM customers WHERE protocolo = %s", (customer_info['protocolo'],))
            existing = cursor.fetchone()
            
            if existing:
                # Atualizar cliente existente
                cursor.execute("""
                    UPDATE customers SET
                        first_name = %s, documento = %s, cobrado_fpd = %s, dias_fpd = %s,
                        data_vencimento_fpd = %s, contrato = %s, regional = %s,
                        territorio = %s, dsc_plano = %s, valor_mensalidade = %s, empresa = %s,
                        updated_at = %s
                    WHERE protocolo = %s
                """, (
                    customer_info['first_name'], customer_info['documento'], customer_info['cobrado_fpd'],
                    customer_info['dias_fpd'], customer_info['data_vencimento_fpd'], customer_info['contrato'],
                    customer_info['regional'], customer_info['territorio'], customer_info['dsc_plano'],
                    customer_info['valor_mensalidade'], customer_info['empresa'], 
                    customer_info['updated_at'], customer_info['protocolo']
                ))
                print(f"🔄 Cliente {i}/{len(customers_data)} atualizado: {customer_info['first_name']}")
            else:
                # Inserir novo cliente (apenas campos essenciais)
                cursor.execute("""
                    INSERT INTO customers (
                        protocolo, first_name, documento, cobrado_fpd, dias_fpd,
                        data_vencimento_fpd, contrato, regional, territorio, 
                        dsc_plano, valor_mensalidade, empresa, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    customer_info['protocolo'], customer_info['first_name'], customer_info['documento'],
                    customer_info['cobrado_fpd'], customer_info['dias_fpd'], customer_info['data_vencimento_fpd'],
                    customer_info['contrato'], customer_info['regional'], customer_info['territorio'],
                    customer_info['dsc_plano'], customer_info['valor_mensalidade'], customer_info['empresa'],
                    customer_info['created_at'], customer_info['updated_at']
                ))
                print(f"✅ Cliente {i}/{len(customers_data)} inserido: {customer_info['first_name']}")
            
            success_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"❌ Erro no cliente {i}: {e}")
            continue
    
    # Commit das alterações
    conn.commit()
    cursor.close()
    
    return success_count, error_count

def main():
    """Função principal"""
    print("🚀 UPLOAD DE DADOS PARA O BANCO DE DADOS")
    print("=" * 50)
    
    # Conectar ao banco
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Ler arquivo JSON limpo
        print("📁 Lendo arquivo JSON limpo...")
        with open('resultado_cruzamento_limpo.json', 'r', encoding='utf-8') as f:
            customers_data = json.load(f)
        
        print(f"✅ Arquivo lido: {len(customers_data)} clientes")
        
        # Filtrar apenas clientes com dívida
        customers_with_debt = [
            customer for customer in customers_data
            if customer.get('dados_fpd', {}).get('cobrado_fpd', 0) > 0
        ]
        
        print(f"💰 Clientes com dívida: {len(customers_with_debt)}")
        
        if not customers_with_debt:
            print("❌ Nenhum cliente com dívida encontrado!")
            return
        
        # Fazer upload para o banco
        success_count, error_count = upload_customers_to_database(conn, customers_with_debt)
        
        # Resultados
        print("\n🎉 UPLOAD CONCLUÍDO!")
        print(f"✅ Sucessos: {success_count}")
        print(f"❌ Erros: {error_count}")
        print(f"📊 Total processado: {len(customers_with_debt)}")
        
        # Verificar dados no banco
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_in_db = cursor.fetchone()[0]
        cursor.close()
        
        print(f"🗄️ Total no banco: {total_in_db}")
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    
    finally:
        conn.close()
        print("🔌 Conexão fechada")

if __name__ == "__main__":
    main()
