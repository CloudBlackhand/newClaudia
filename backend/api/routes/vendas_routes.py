from flask import Blueprint, request, jsonify
from backend.modules.logger_system import SmartLogger, LogCategory
from backend.modules.vendas_data_processor import VendasDataProcessor
import os
import json
import psycopg2
from datetime import datetime

vendas_blueprint = Blueprint('vendas', __name__)
logger = SmartLogger("vendas_routes")

@vendas_blueprint.route('/vendas/validate', methods=['POST'])
def validate_vendas_data():
    """Validar dados de vendas sem inserir no banco"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Dados devem ser enviados como JSON'
            }), 400
        
        vendas_data = request.get_json()
        
        # Importar processador
        processor = VendasDataProcessor()
        
        # Processar dados
        processed_vendas, errors = processor.process_vendas_json(json.dumps(vendas_data))
        
        # Obter resumo do processamento
        summary = processor.get_processing_summary(processed_vendas)
        
        return jsonify({
            'success': True,
            'validation_summary': summary,
            'errors': errors,
            'message': f'Validação concluída: {summary["valid_records"]} registros válidos'
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao validar dados de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vendas_blueprint.route('/vendas/process', methods=['POST'])
def process_vendas_data():
    """Processa e insere dados de vendas no banco de dados"""
    try:
        logger.info(LogCategory.SYSTEM, "Iniciando processamento de dados de vendas")
        
        # Verificar se há dados no request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Dados devem ser enviados como JSON'
            }), 400
        
        vendas_data = request.get_json()
        
        # Importar processador
        processor = VendasDataProcessor()
        
        # Processar dados
        processed_vendas, errors = processor.process_vendas_json(json.dumps(vendas_data))
        
        # Obter resumo do processamento
        summary = processor.get_processing_summary(processed_vendas)
        
        # Inserir vendas válidas no banco
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        inserted_count = 0
        insertion_errors = []
        
        for venda in processed_vendas:
            if venda.is_valid:
                try:
                    # Inserir na tabela customers - NOVA ESTRUTURA APENAS dados_vendas
                    cursor.execute("""
                        INSERT INTO customers (
                            nome, documento, telefone1, telefone2, email, rua_endereco,
                            cidade, cep, data_nascimento, status, origem_venda,
                            contrato, data_agenda, obs, aba_origem, fpd, spd
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        venda.nome,
                        venda.documento,
                        venda.telefone1,
                        venda.telefone2,
                        venda.email,
                        venda.endereco,
                        venda.cidade,
                        venda.cep,
                        venda.data_nascimento,
                        venda.status,
                        venda.aba_origem,  # origem_venda
                        venda.aba_origem,  # contrato (usando aba_origem como contrato)
                        venda.fpd,  # data_agenda (usando fpd como data_agenda)
                        f"FPD: {venda.fpd}",  # obs
                        venda.aba_origem,
                        venda.fpd,  # fpd (campo correto)
                        venda.fpd  # spd (mantendo compatibilidade)
                    ))
                    
                    inserted_count += 1
                    
                except Exception as e:
                    insertion_errors.append(f"Erro ao inserir {venda.nome}: {str(e)}")
                    logger.error(LogCategory.SYSTEM, f"Erro ao inserir venda {venda.nome}: {e}")
                    # Rollback da transação atual e continuar
                    conn.rollback()
                    # Reconectar para continuar
                    conn = psycopg2.connect(database_url)
                    cursor = conn.cursor()
        
        # Commit das alterações
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(LogCategory.SYSTEM, f"Processamento concluído: {inserted_count} vendas inseridas")
        
        return jsonify({
            'success': True,
            'message': 'Dados de vendas processados com sucesso',
            'processing_summary': summary,
            'inserted_count': inserted_count,
            'insertion_errors': insertion_errors
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao processar dados de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vendas_blueprint.route('/vendas/list', methods=['GET'])
def list_customers():
    """Listar todas as pessoas cadastradas para cobrança"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Buscar todos os clientes
        cursor.execute("""
            SELECT 
                id, nome, documento, telefone1, telefone2, email, 
                rua_endereco, cidade, cep, data_nascimento, status, 
                origem_venda, contrato, data_agenda, obs, aba_origem, fpd, spd,
                created_at, updated_at
            FROM customers 
            ORDER BY created_at DESC
        """)
        
        customers = cursor.fetchall()
        
        # Converter para lista de dicionários
        customers_list = []
        for customer in customers:
            customers_list.append({
                'id': customer[0],
                'nome': customer[1],
                'documento': customer[2],
                'telefone1': customer[3],
                'telefone2': customer[4],
                'email': customer[5],
                'endereco': customer[6],
                'cidade': customer[7],
                'cep': customer[8],
                'data_nascimento': customer[9],
                'status': customer[10],
                'origem_venda': customer[11],
                'contrato': customer[12],
                'data_agenda': customer[13],
                'obs': customer[14],
                'aba_origem': customer[15],
                'fpd': customer[16],  # Campo FPD
                'spd': customer[17],  # Campo SPD
                'created_at': customer[18].isoformat() if customer[18] else None,
                'updated_at': customer[19].isoformat() if customer[19] else None
            })
        
        cursor.close()
        conn.close()
        
        logger.info(LogCategory.SYSTEM, f"Listagem de clientes: {len(customers_list)} registros encontrados")
        
        return jsonify({
            'success': True,
            'total_customers': len(customers_list),
            'customers': customers_list,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao listar clientes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vendas_blueprint.route('/vendas/stats', methods=['GET'])
def get_vendas_stats():
    """Obter estatísticas dos dados de vendas processados"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Contar total de vendas
        cursor.execute("""
            SELECT COUNT(*) FROM customers
        """)
        vendas_count = cursor.fetchone()[0]
        
        # Contar por cidade
        cursor.execute("""
            SELECT cidade, COUNT(*) FROM customers 
            GROUP BY cidade 
            ORDER BY COUNT(*) DESC
        """)
        regional_stats = dict(cursor.fetchall())
        
        # Contar por FPD
        cursor.execute("""
            SELECT fpd, COUNT(*) FROM customers 
            WHERE fpd IS NOT NULL AND fpd != ''
            GROUP BY fpd 
            ORDER BY fpd
        """)
        fpd_stats = dict(cursor.fetchall())
        
        # Contar por SPD também
        cursor.execute("""
            SELECT spd, COUNT(*) FROM customers 
            WHERE spd IS NOT NULL AND spd != ''
            GROUP BY spd 
            ORDER BY spd
        """)
        spd_stats = dict(cursor.fetchall())
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_vendas': vendas_count,
                'por_cidade': regional_stats,
                'por_fpd': fpd_stats,
                'por_spd': spd_stats,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao obter estatísticas de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
