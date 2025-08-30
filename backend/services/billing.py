"""
Módulo principal de cobrança - disparo automatizado de mensagens
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from backend.services.json_processor import JSONProcessor, ClientsBatchProcessor
from backend.services.waha_client import WahaClient
from backend.utils.validators import ClientData, MessageValidator
from backend.utils.logger import billing_logger, app_logger
from backend.config.settings import active_config

class MessageTemplate:
    """Gerenciador de templates de mensagem"""
    
    def __init__(self):
        self.templates = {}
        self.load_templates()
    
    def load_templates(self):
        """Carrega templates do arquivo JSON"""
        try:
            templates_path = Path(active_config.TEMPLATES_PATH)
            if templates_path.exists():
                with open(templates_path, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            else:
                # Templates padrão se arquivo não existir
                self.templates = self._get_default_templates()
                self.save_templates()
                
            billing_logger.info("TEMPLATES_LOADED", {
                "count": len(self.templates),
                "templates": list(self.templates.keys())
            })
            
        except Exception as e:
            billing_logger.error("TEMPLATES_LOAD_ERROR", e)
            self.templates = self._get_default_templates()
    
    def save_templates(self):
        """Salva templates no arquivo"""
        try:
            templates_path = Path(active_config.TEMPLATES_PATH)
            templates_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(templates_path, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            billing_logger.error("TEMPLATES_SAVE_ERROR", e)
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Obtém template por nome"""
        return self.templates.get(template_name)
    
    def add_template(self, name: str, content: str) -> bool:
        """Adiciona novo template"""
        validation = MessageValidator.validate_template(
            content, 
            required_vars=["name", "amount"]
        )
        
        if validation["valid"]:
            self.templates[name] = content
            self.save_templates()
            billing_logger.info("TEMPLATE_ADDED", {"name": name})
            return True
        else:
            billing_logger.warning("TEMPLATE_INVALID", {
                "name": name,
                "errors": validation["errors"]
            })
            return False
    
    def format_message(self, template_name: str, client: ClientData) -> Dict[str, Any]:
        """Formata mensagem usando template e dados do cliente"""
        result = {"success": False, "message": None, "error": None}
        
        template = self.get_template(template_name)
        if not template:
            result["error"] = f"Template '{template_name}' não encontrado"
            return result
        
        try:
            # Variáveis disponíveis para o template
            variables = {
                "name": client.name,
                "amount": f"R$ {client.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "phone": client.phone,
                "due_date": client.due_date or "não informado",
                "description": client.description or "",
                "current_date": datetime.now().strftime("%d/%m/%Y"),
                "current_time": datetime.now().strftime("%H:%M")
            }
            
            # Substitui variáveis no template
            message = template.format(**variables)
            
            # Valida mensagem final
            validation = MessageValidator.validate_message_content(message)
            if validation["valid"]:
                result["success"] = True
                result["message"] = message
            else:
                result["error"] = f"Mensagem inválida: {'; '.join(validation['errors'])}"
                
        except KeyError as e:
            result["error"] = f"Variável não encontrada no template: {e}"
        except Exception as e:
            result["error"] = f"Erro ao formatar mensagem: {str(e)}"
        
        return result
    
    def _get_default_templates(self) -> Dict[str, str]:
        """Templates padrão do sistema"""
        return {
            "cobranca_simples": """Olá {name}! 👋

Esperamos que esteja tudo bem com você.

Este é um lembrete amigável sobre o pagamento pendente:
💰 Valor: {amount}
📅 Vencimento: {due_date}

Para facilitar o pagamento, entre em contato conosco respondendo esta mensagem.

Obrigado pela preferência! 🙏""",
            
            "cobranca_urgente": """⚠️ {name}, PAGAMENTO EM ATRASO ⚠️

Identificamos que o pagamento abaixo está em atraso:
💰 Valor: {amount}
📅 Venceu em: {due_date}

🔔 Para evitar juros e multas, regularize hoje mesmo!

Responda esta mensagem para negociar ou esclarecer dúvidas.

Contamos com sua compreensão! 📞""",
            
            "cobranca_cortesia": """Olá {name}! 😊

Tudo bem? Este é apenas um lembrete cortês sobre:

💼 Serviço: {description}
💰 Valor: {amount}
📅 Vencimento: {due_date}

Se já efetuou o pagamento, pode desconsiderar esta mensagem.

Qualquer dúvida, estamos à disposição! 💬""",
            
            "negociacao": """Olá {name}! 

Entendemos que podem existir dificuldades para quitar o valor de {amount}.

💡 Temos opções de parcelamento e desconto à vista!

Vamos conversar sobre a melhor solução para você?
Responda esta mensagem ou ligue para nós.

Estamos aqui para ajudar! 🤝"""
        }

class BillingService:
    """Serviço principal de cobrança"""
    
    def __init__(self):
        self.config = active_config
        self.waha_client = WahaClient()
        self.json_processor = JSONProcessor()
        self.batch_processor = ClientsBatchProcessor()
        self.message_template = MessageTemplate()
        self.current_batch = None
        
    async def send_billing_batch(
        self, 
        clients_file: str, 
        template_name: str,
        filters: Optional[Dict[str, Any]] = None,
        delay_seconds: int = 2,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """Envia lote de cobrança para clientes"""
        
        result = {
            "success": False,
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_clients": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "start_time": datetime.utcnow(),
            "end_time": None,
            "duration": 0
        }
        
        self.current_batch = result
        
        try:
            billing_logger.info("BILLING_BATCH_STARTED", {
                "batch_id": result["batch_id"],
                "template": template_name,
                "filters": filters
            })
            
            # Carrega e processa clientes
            clients_result = self.json_processor.load_clients_from_file(clients_file)
            if not clients_result["success"]:
                result["errors"].extend(clients_result["errors"])
                return result
            
            clients = clients_result["clients"]
            
            # Aplica filtros se especificados
            if filters:
                clients = self.json_processor.filter_clients(clients, filters)
            
            result["total_clients"] = len(clients)
            
            if result["total_clients"] == 0:
                result["errors"].append("Nenhum cliente válido encontrado")
                return result
            
            billing_logger.batch_started(result["total_clients"], template_name)
            
            # Processa cada cliente
            for idx, client in enumerate(clients):
                try:
                    # Callback de progresso
                    if progress_callback:
                        progress_callback(idx + 1, result["total_clients"])
                    
                    # Envia mensagem
                    send_result = await self._send_client_message(client, template_name)
                    
                    result["processed"] += 1
                    
                    if send_result["success"]:
                        result["successful"] += 1
                        billing_logger.message_sent(
                            client.phone,
                            template_name,
                            True,
                            send_result["message_id"]
                        )
                    else:
                        result["failed"] += 1
                        billing_logger.message_sent(
                            client.phone,
                            template_name,
                            False,
                            error=send_result["error"]
                        )
                    
                    # Delay entre mensagens para evitar spam
                    if delay_seconds > 0 and idx < len(clients) - 1:
                        await asyncio.sleep(delay_seconds)
                
                except Exception as e:
                    result["failed"] += 1
                    billing_logger.error("CLIENT_PROCESSING_ERROR", e, {
                        "client_id": client.id,
                        "client_phone": client.phone
                    })
            
            # Finaliza lote
            result["end_time"] = datetime.utcnow()
            result["duration"] = (result["end_time"] - result["start_time"]).total_seconds()
            result["success"] = True
            
            billing_logger.batch_completed(
                result["total_clients"],
                result["successful"],
                result["failed"],
                result["duration"]
            )
            
        except Exception as e:
            result["errors"].append(str(e))
            billing_logger.error("BILLING_BATCH_ERROR", e, {"batch_id": result["batch_id"]})
        
        finally:
            self.current_batch = None
        
        return result
    
    async def _send_client_message(self, client: ClientData, template_name: str) -> Dict[str, Any]:
        """Envia mensagem para um cliente específico"""
        # Formata mensagem usando template
        format_result = self.message_template.format_message(template_name, client)
        if not format_result["success"]:
            return format_result
        
        # Envia mensagem via Waha
        send_result = await self.waha_client.send_text_message(
            client.phone,
            format_result["message"]
        )
        
        return send_result
    
    async def send_single_message(self, client_data: Dict[str, Any], template_name: str) -> Dict[str, Any]:
        """Envia mensagem para cliente único"""
        try:
            # Valida dados do cliente
            client = ClientData(**client_data)
            
            # Envia mensagem
            result = await self._send_client_message(client, template_name)
            
            billing_logger.client_processed(
                client_data,
                result["success"],
                result.get("error")
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Erro ao processar cliente: {str(e)}"
            billing_logger.error("SINGLE_MESSAGE_ERROR", e, client_data)
            return {"success": False, "error": error_msg}
    
    def get_batch_status(self) -> Optional[Dict[str, Any]]:
        """Retorna status do lote atual"""
        if self.current_batch:
            current_time = datetime.utcnow()
            duration = (current_time - self.current_batch["start_time"]).total_seconds()
            
            return {
                **self.current_batch,
                "current_duration": duration,
                "is_running": True,
                "progress_percentage": (
                    self.current_batch["processed"] / self.current_batch["total_clients"] * 100
                    if self.current_batch["total_clients"] > 0 else 0
                )
            }
        
        return None
    
    async def validate_before_sending(self, clients_file: str, template_name: str) -> Dict[str, Any]:
        """Valida configuração antes de enviar lote"""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "client_stats": {},
            "waha_status": {},
            "template_info": {}
        }
        
        try:
            # Verifica template
            template = self.message_template.get_template(template_name)
            if not template:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Template '{template_name}' não encontrado")
            else:
                validation_result["template_info"] = {
                    "name": template_name,
                    "length": len(template),
                    "variables": MessageValidator.validate_template(template)["variables"]
                }
            
            # Verifica arquivo de clientes
            stats = self.json_processor.get_processing_stats(clients_file)
            validation_result["client_stats"] = stats
            
            if not stats["file_exists"]:
                validation_result["valid"] = False
                validation_result["issues"].append("Arquivo de clientes não encontrado")
            
            # Verifica status da Waha
            waha_status = await self.waha_client.get_session_status()
            validation_result["waha_status"] = waha_status
            
            if not waha_status["success"]:
                validation_result["valid"] = False
                validation_result["issues"].append(f"Waha não disponível: {waha_status['error']}")
            elif waha_status["status"] != "WORKING":
                validation_result["warnings"].append(f"Waha status: {waha_status['status']}")
            
        except Exception as e:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Erro na validação: {str(e)}")
            app_logger.error("VALIDATION_ERROR", e)
        
        return validation_result
    
    def get_available_templates(self) -> Dict[str, Any]:
        """Retorna templates disponíveis"""
        templates_info = {}
        
        for name, content in self.message_template.templates.items():
            validation = MessageValidator.validate_template(content)
            templates_info[name] = {
                "content": content,
                "length": len(content),
                "variables": validation["variables"],
                "valid": validation["valid"],
                "preview": content[:100] + "..." if len(content) > 100 else content
            }
        
        return templates_info
    
    async def test_message_sending(self, test_phone: str, template_name: str) -> Dict[str, Any]:
        """Testa envio de mensagem para número específico"""
        try:
            # Cria cliente de teste
            test_client = ClientData(
                id="test_001",
                name="Cliente Teste",
                phone=test_phone,
                amount=100.00,
                due_date=datetime.now().strftime('%Y-%m-%d'),
                description="Teste de mensagem"
            )
            
            # Envia mensagem de teste
            result = await self._send_client_message(test_client, template_name)
            
            billing_logger.info("TEST_MESSAGE_SENT", {
                "phone": test_phone,
                "template": template_name,
                "success": result["success"]
            })
            
            return result
            
        except Exception as e:
            billing_logger.error("TEST_MESSAGE_ERROR", e, {
                "phone": test_phone,
                "template": template_name
            })
            return {"success": False, "error": str(e)}

