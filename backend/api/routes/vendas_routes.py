from flask import Blueprint, request, jsonify
from modules.logger_system import SmartLogger, LogCategory
from modules.vendas_data_processor import VendasDataProcessor
import os
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
        processed_vendas, errors = processor.process_vendas_json(str(vendas_data))
        
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
        processed_vendas, errors = processor.process_vendas_json(str(vendas_data))
        
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
                            contrato, data_agenda, obs, aba_origem, spd
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                        venda.fpd  # spd
                    ))
                    
                    inserted_count += 1
                    
                except Exception as e:
                    insertion_errors.append(f"Erro ao inserir {venda.nome}: {str(e)}")
                    logger.error(LogCategory.SYSTEM, f"Erro ao inserir venda {venda.nome}: {e}")
        
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
        
        # Contar por priority (FPD)
        cursor.execute("""
            SELECT priority, COUNT(*) FROM customers 
            WHERE empresa = 'VENDAS' 
            GROUP BY priority 
            ORDER BY priority
        """)
        priority_stats = dict(cursor.fetchall())
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_vendas': vendas_count,
                'por_regional': regional_stats,
                'por_priority': priority_stats,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao obter estatísticas de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
