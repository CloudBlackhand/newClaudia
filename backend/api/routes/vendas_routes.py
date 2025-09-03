from flask import Blueprint, request, jsonify
from backend.modules.logger_system import SmartLogger, LogCategory
from backend.modules.vendas_data_processor import VendasDataProcessor
import os
import psycopg2
from datetime import datetime

vendas_blueprint = Blueprint('vendas', __name__)
logger = SmartLogger()

@vendas_blueprint.route('/api/vendas/validate', methods=['POST'])
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

@vendas_blueprint.route('/api/vendas/process', methods=['POST'])
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
                    # Inserir na tabela customers
                    cursor.execute("""
                        INSERT INTO customers (
                            protocolo, first_name, documento, cobrado_fpd, dias_fpd,
                            data_vencimento_fpd, contrato, regional, territorio, dsc_plano,
                            valor_mensalidade, empresa, status, priority, is_customer,
                            last_contact, conversation_count, payment_promises, last_payment_date
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        f"VDA_{venda.documento[:8]}",  # Protocolo baseado no documento
                        venda.nome,
                        venda.documento,
                        float(venda.fpd) if venda.fpd.isdigit() else 0.0,
                        0,  # dias_fpd - será calculado depois
                        None,  # data_vencimento_fpd - será calculado depois
                        venda.aba_origem,  # contrato
                        venda.cidade,  # regional
                        venda.endereco,  # territorio
                        f"Plano FPD {venda.fpd}",  # dsc_plano
                        0.0,  # valor_mensalidade
                        "VENDAS",  # empresa
                        venda.status,
                        1 if venda.fpd == "1" else 0,  # priority baseado no FPD
                        True,  # is_customer
                        None,  # last_contact
                        0,  # conversation_count
                        0,  # payment_promises
                        None  # last_payment_date
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

@vendas_blueprint.route('/api/vendas/stats', methods=['GET'])
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
        
        # Contar vendas por empresa
        cursor.execute("""
            SELECT COUNT(*) FROM customers WHERE empresa = 'VENDAS'
        """)
        vendas_count = cursor.fetchone()[0]
        
        # Contar por regional (cidade)
        cursor.execute("""
            SELECT regional, COUNT(*) FROM customers 
            WHERE empresa = 'VENDAS' 
            GROUP BY regional 
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
