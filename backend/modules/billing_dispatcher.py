"""
Módulo de Disparo de Mensagens de Cobrança
Sistema otimizado para processamento de JSON e envio de mensagens
"""
import json
import asyncio
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from pathlib import Path

from .logger_system import LoggerSystem
from .validation_engine import ValidationEngine
from .waha_integration import WahaIntegration

logger = logging.getLogger(__name__)

class BillingDispatcher:
    """Sistema de disparo de mensagens de cobrança"""
    
    def __init__(self, logger_system: LoggerSystem, validation_engine: ValidationEngine):
        self.logger_system = logger_system
        self.validation_engine = validation_engine
        self.waha_integration: Optional[WahaIntegration] = None
        self.is_initialized = False
        self.processing_queue = asyncio.Queue()
        self.workers_running = False
        
    async def initialize(self):
        """Inicialização do módulo"""
        try:
            logger.info("Inicializando BillingDispatcher...")
            
            # Iniciar workers de processamento
            await self._start_workers()
            
            self.is_initialized = True
            logger.info("BillingDispatcher inicializado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar BillingDispatcher: {str(e)}")
            raise
    
    async def cleanup(self):
        """Limpeza do módulo"""
        self.workers_running = False
        self.is_initialized = False
        logger.info("BillingDispatcher finalizado")
    
    def is_healthy(self) -> bool:
        """Verificação de saúde do módulo"""
        return self.is_initialized and self.workers_running
    
    def set_waha_integration(self, waha_integration: WahaIntegration):
        """Definir integração com Waha"""
        self.waha_integration = waha_integration
    
    async def process_billing_json(self, json_data: str, template: Optional[str] = None) -> Dict[str, Any]:
        """
        Processar arquivo JSON com dados de cobrança
        
        Args:
            json_data: String contendo dados JSON
            template: Template personalizado de mensagem (opcional)
            
        Returns:
            Relatório de processamento
        """
        try:
            # Log da operação
            operation_id = await self.logger_system.log_operation(
                "billing_dispatch",
                {"data_size": len(json_data)}
            )
            
            # Parse otimizado do JSON
            clients_data = await self._parse_json_optimized(json_data)
            
            # Validação rigorosa dos dados
            validation_result = await self.validation_engine.validate_billing_data(clients_data)
            
            if not validation_result.is_valid:
                await self.logger_system.log_error(
                    operation_id,
                    "validation_failed",
                    {"errors": validation_result.errors}
                )
                return {
                    "success": False,
                    "error": "Dados inválidos",
                    "details": validation_result.errors
                }
            
            # Processar mensagens em lote
            processing_result = await self._process_billing_batch(
                validation_result.valid_data,
                template,
                operation_id
            )
            
            await self.logger_system.log_success(
                operation_id,
                {"processed": len(validation_result.valid_data)}
            )
            
            return processing_result
            
        except Exception as e:
            logger.error(f"Erro ao processar JSON de cobrança: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _parse_json_optimized(self, json_data: str) -> List[Dict[str, Any]]:
        """Parser otimizado de JSON"""
        try:
            # Parse usando orjson se disponível, senão json padrão
            try:
                import orjson
                data = orjson.loads(json_data)
            except ImportError:
                data = json.loads(json_data)
            
            # Garantir que é uma lista
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                raise ValueError("JSON deve conter uma lista ou objeto de clientes")
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {str(e)}")
    
    async def _process_billing_batch(
        self, 
        clients_data: List[Dict[str, Any]], 
        template: Optional[str],
        operation_id: str
    ) -> Dict[str, Any]:
        """Processar lote de mensagens de cobrança"""
        
        total_clients = len(clients_data)
        successful_sends = 0
        failed_sends = 0
        errors = []
        
        # Configurar template
        message_template = template or self._get_default_template()
        
        # Processar em lotes para otimizar performance
        batch_size = 10  # Ajustável conforme necessário
        
        for i in range(0, total_clients, batch_size):
            batch = clients_data[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self._send_billing_message(client, message_template, operation_id) 
                  for client in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    failed_sends += 1
                    errors.append(str(result))
                elif result.get("success"):
                    successful_sends += 1
                else:
                    failed_sends += 1
                    errors.append(result.get("error", "Erro desconhecido"))
        
        return {
            "success": True,
            "total_processed": total_clients,
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "errors": errors,
            "operation_id": operation_id
        }
    
    async def _send_billing_message(
        self, 
        client_data: Dict[str, Any], 
        template: str,
        operation_id: str
    ) -> Dict[str, Any]:
        """Enviar mensagem de cobrança para um cliente"""
        try:
            # Formatar mensagem com dados do cliente
            message = self._format_message(template, client_data)
            
            # Validar número de telefone
            phone = client_data.get("telefone") or client_data.get("phone")
            if not phone:
                raise ValueError("Número de telefone não encontrado")
            
            # Enviar via Waha se disponível
            if self.waha_integration:
                send_result = await self.waha_integration.send_message(phone, message)
                
                # Log do envio
                await self.logger_system.log_message_sent(
                    operation_id,
                    phone,
                    message,
                    send_result.get("success", False)
                )
                
                return send_result
            else:
                # Simular envio para desenvolvimento
                await asyncio.sleep(0.1)  # Simular latência
                return {"success": True, "message_id": f"sim_{datetime.now().timestamp()}"}
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _format_message(self, template: str, client_data: Dict[str, Any]) -> str:
        """Formatar mensagem com dados do cliente"""
        try:
            # Substituir placeholders no template
            message = template
            
            # Mapeamento de campos comuns
            field_mapping = {
                "nome": client_data.get("nome") or client_data.get("name", "Cliente"),
                "valor": client_data.get("valor") or client_data.get("amount", "0,00"),
                "vencimento": client_data.get("vencimento") or client_data.get("due_date", ""),
                "descricao": client_data.get("descricao") or client_data.get("description", "Pendência financeira")
            }
            
            # Aplicar formatações
            for field, value in field_mapping.items():
                message = message.replace(f"{{{field}}}", str(value))
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao formatar mensagem: {str(e)}")
            return template  # Retornar template original em caso de erro
    
    def _get_default_template(self) -> str:
        """Obter template padrão de mensagem"""
        return """
🔔 *Lembrete de Pagamento*

Olá {nome}!

Identificamos que há uma pendência em sua conta:
💰 Valor: R$ {valor}
📅 Vencimento: {vencimento}
📋 Descrição: {descricao}

Para regularizar sua situação, por favor realize o pagamento o quanto antes.

Se já efetuou o pagamento, desconsidere esta mensagem.

Qualquer dúvida, estou aqui para ajudar! 😊
        """.strip()
    
    async def _start_workers(self):
        """Iniciar workers de processamento"""
        self.workers_running = True
        # Implementar workers se necessário para processamento assíncrono
        logger.info("Workers de processamento iniciados")

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Obter estatísticas de processamento"""
        return {
            "is_healthy": self.is_healthy(),
            "queue_size": self.processing_queue.qsize() if hasattr(self.processing_queue, 'qsize') else 0,
            "workers_running": self.workers_running
        }
