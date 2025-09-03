from flask import Blueprint, request, jsonify
import json
import os
import psycopg2
from datetime import datetime
from backend.modules.logger_system import LogCategory
from backend.modules.vendas_data_processor import VendasDataProcessor

# Criar blueprint para rotas de vendas
vendas_bp = Blueprint('vendas', __name__)

@vendas_bp.route('/api/vendas/process', methods=['POST'])
def process_vendas_data():
    """Processa e insere dados de vendas no banco de dados"""
    try:
        # Configurar logger
        from backend.modules.logger_system import SmartLogger
        logger = SmartLogger()
        
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
        processor.set_logger(logger)
        
        # Processar dados
        json_string = json.dumps(vendas_data)
        processed_vendas = processor.process_vendas_json(json_string)
        
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
        errors = []
        
        for vendas in processed_vendas:
            if vendas.is_valid:
                try:
                    # Converter para formato de cliente
                    customer_data = processor.convert_to_customer_format(vendas)
                    
                    # Inserir na tabela customers
                    cursor.execute("""
                        INSERT INTO customers (
                            protocolo, first_name, documento, cobrado_fpd, dias_fpd,
                            data_vencimento_fpd, contrato, regional, territorio, dsc_plano,
                            valor_mensalidade, empresa, status, priority, is_customer,
                            last_contact, conversation_count, payment_promises, last_payment_date,
                            email, endereco, cidade, cep, data_nascimento, aba_origem
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        f"VDA_{customer_data['documento'][:8]}_{datetime.now().strftime('%Y%m%d')}",  # Protocolo único
                        customer_data['name'],
                        customer_data['documento'],
                        float(customer_data['fpd']) if customer_data['fpd'].isdigit() else 0.0,
                        0,  # dias_fpd - será calculado depois
                        None,  # data_vencimento_fpd - será calculado depois
                        customer_data['aba_origem'],  # contrato
                        customer_data['cidade'],  # regional
                        customer_data['endereco'],  # territorio
                        f"Plano FPD {customer_data['fpd']}",  # dsc_plano
                        0.0,  # valor_mensalidade
                        "VENDAS",  # empresa
                        customer_data['status'],
                        customer_data['priority'],
                        True,  # is_customer
                        None,  # last_contact
                        0,  # conversation_count
                        0,  # payment_promises
                        None,  # last_payment_date
                        customer_data['email'],
                        customer_data['endereco'],
                        customer_data['cidade'],
                        customer_data['cep'],
                        customer_data['data_nascimento'],
                        customer_data['aba_origem']
                    ))
                    
                    inserted_count += 1
                    
                except Exception as e:
                    errors.append(f"Erro ao inserir {vendas.nome}: {str(e)}")
                    logger.error(LogCategory.SYSTEM, f"Erro ao inserir venda {vendas.nome}: {e}")
        
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
            'insertion_errors': errors
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao processar dados de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vendas_bp.route('/api/vendas/validate', methods=['POST'])
def validate_vendas_data():
    """Validar dados de vendas sem inserir no banco"""
    try:
        # Configurar logger
        from backend.modules.logger_system import SmartLogger
        logger = SmartLogger()
        
        logger.info(LogCategory.SYSTEM, "Iniciando validação de dados de vendas")
        
        # Verificar se há dados no request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Dados devem ser enviados como JSON'
            }), 400
        
        vendas_data = request.get_json()
        
        # Importar processador
        processor = VendasDataProcessor()
        processor.set_logger(logger)
        
        # Processar dados
        json_string = json.dumps(vendas_data)
        processed_vendas = processor.process_vendas_json(json_string)
        
        # Obter resumo do processamento
        summary = processor.get_processing_summary(processed_vendas)
        
        # Preparar preview dos dados
        preview_data = []
        for vendas in processed_vendas[:10]:  # Primeiros 10 para preview
            if vendas.is_valid:
                preview_data.append({
                    'nome': vendas.nome,
                    'documento': vendas.documento,
                    'telefone': vendas.telefone1,
                    'cidade': vendas.cidade,
                    'fpd': vendas.fpd,
                    'status': vendas.status
                })
        
        logger.info(LogCategory.SYSTEM, f"Validação concluída: {len(processed_vendas)} registros processados")
        
        return jsonify({
            'success': True,
            'message': 'Dados de vendas validados com sucesso',
            'processing_summary': summary,
            'preview_data': preview_data,
            'total_valid': len([v for v in processed_vendas if v.is_valid]),
            'total_invalid': len([v for v in processed_vendas if not v.is_valid])
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao validar dados de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@vendas_bp.route('/api/vendas/stats', methods=['GET'])
def get_vendas_stats():
    """Obter estatísticas dos dados de vendas no banco"""
    try:
        # Configurar logger
        from backend.modules.logger_system import SmartLogger
        logger = SmartLogger()
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'DATABASE_URL não encontrada'
            }), 500
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Contar total de vendas
        cursor.execute("SELECT COUNT(*) FROM customers WHERE empresa = 'VENDAS'")
        total_vendas = cursor.fetchone()[0]
        
        # Contar por FPD
        cursor.execute("SELECT cobrado_fpd, COUNT(*) FROM customers WHERE empresa = 'VENDAS' GROUP BY cobrado_fpd")
        fpd_stats = dict(cursor.fetchall())
        
        # Contar por cidade
        cursor.execute("SELECT cidade, COUNT(*) FROM customers WHERE empresa = 'VENDAS' GROUP BY cidade ORDER BY COUNT(*) DESC LIMIT 10")
        city_stats = dict(cursor.fetchall())
        
        # Contar por status
        cursor.execute("SELECT status, COUNT(*) FROM customers WHERE empresa = 'VENDAS' GROUP BY status")
        status_stats = dict(cursor.fetchall())
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_vendas': total_vendas,
                'fpd_distribution': fpd_stats,
                'top_cities': city_stats,
                'status_distribution': status_stats,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(LogCategory.SYSTEM, f"Erro ao obter estatísticas de vendas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
