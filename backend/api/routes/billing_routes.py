"""
Rotas da API para funcionalidades de cobrança
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import logging

from modules.billing_dispatcher import BillingDispatcher
from modules.validation_engine import ValidationEngine
from modules.logger_system import LoggerSystem

logger = logging.getLogger(__name__)
router = APIRouter()

# Referências globais (serão definidas no app.py)
billing_dispatcher: Optional[BillingDispatcher] = None
validation_engine: Optional[ValidationEngine] = None
logger_system: Optional[LoggerSystem] = None

def set_dependencies(bd: BillingDispatcher, ve: ValidationEngine, ls: LoggerSystem):
    """Definir dependências dos módulos"""
    global billing_dispatcher, validation_engine, logger_system
    billing_dispatcher = bd
    validation_engine = ve
    logger_system = ls

@router.post("/process-json")
async def process_billing_json(
    background_tasks: BackgroundTasks,
    json_data: str = Form(...),
    template: Optional[str] = Form(None)
):
    """
    Processar JSON com dados de cobrança
    
    Args:
        json_data: String JSON com dados dos clientes
        template: Template customizado de mensagem (opcional)
    """
    try:
        if not billing_dispatcher:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        # Validar estrutura do JSON
        json_validation = await validation_engine.validate_json_structure(json_data)
        if not json_validation["is_valid"]:
            raise HTTPException(status_code=400, detail=json_validation["error"])
        
        # Validar template se fornecido
        if template:
            template_validation = await validation_engine.validate_template(template)
            if not template_validation["is_valid"]:
                raise HTTPException(status_code=400, detail=template_validation["error"])
        
        # Processar em background
        background_tasks.add_task(
            _process_billing_background,
            json_data,
            template
        )
        
        return {
            "success": True,
            "message": "Processamento iniciado",
            "records_count": json_validation["records_count"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar JSON de cobrança: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _process_billing_background(json_data: str, template: Optional[str]):
    """Processar cobrança em background"""
    try:
        result = await billing_dispatcher.process_billing_json(json_data, template)
        logger.info(f"Processamento concluído: {result}")
    except Exception as e:
        logger.error(f"Erro no processamento em background: {str(e)}")

@router.post("/upload-file")
async def upload_billing_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    template: Optional[str] = Form(None)
):
    """
    Upload de arquivo JSON com dados de cobrança
    """
    try:
        if not billing_dispatcher:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        # Verificar tipo de arquivo
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Apenas arquivos JSON são aceitos")
        
        # Ler conteúdo do arquivo
        content = await file.read()
        json_data = content.decode('utf-8')
        
        # Validar estrutura do JSON
        json_validation = await validation_engine.validate_json_structure(json_data)
        if not json_validation["is_valid"]:
            raise HTTPException(status_code=400, detail=json_validation["error"])
        
        # Validar template se fornecido
        if template:
            template_validation = await validation_engine.validate_template(template)
            if not template_validation["is_valid"]:
                raise HTTPException(status_code=400, detail=template_validation["error"])
        
        # Processar em background
        background_tasks.add_task(
            _process_billing_background,
            json_data,
            template
        )
        
        return {
            "success": True,
            "message": "Arquivo processado com sucesso",
            "filename": file.filename,
            "records_count": json_validation["records_count"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate-json")
async def validate_json_data(json_data: str):
    """Validar estrutura de dados JSON"""
    try:
        if not validation_engine:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        result = await validation_engine.validate_json_structure(json_data)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao validar JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate-template")
async def validate_template_data(template: str):
    """Validar template de mensagem"""
    try:
        if not validation_engine:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        result = await validation_engine.validate_template(template)
        return result
        
    except Exception as e:
        logger.error(f"Erro ao validar template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_billing_stats():
    """Obter estatísticas de processamento"""
    try:
        if not billing_dispatcher:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        stats = await billing_dispatcher.get_processing_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def get_billing_logs(limit: int = 100):
    """Obter logs de operações de cobrança"""
    try:
        if not logger_system:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        operation_logs = await logger_system.get_operation_logs(limit=limit)
        message_logs = await logger_system.get_message_logs(limit=limit)
        
        return {
            "operation_logs": operation_logs,
            "message_logs": message_logs
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report")
async def generate_billing_report(start_date: Optional[str] = None):
    """Gerar relatório de atividades"""
    try:
        if not logger_system:
            raise HTTPException(status_code=500, detail="Sistema não inicializado")
        
        report = await logger_system.generate_report(start_date)
        return report
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
