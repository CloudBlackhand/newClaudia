#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Disparo de Mensagens de Cobrança
Módulo avançado para envio automatizado de cobranças
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

from backend.modules.logger_system import LogManager, LogCategory
from backend.modules.validation_engine import JSONProcessor, ValidationResult

logger = LogManager.get_logger('billing_dispatcher')

class MessageStatus(Enum):
    """Status das mensagens de cobrança"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"

class MessageType(Enum):
    """Tipos de mensagem de cobrança"""
    INITIAL = "initial"
    REMINDER = "reminder"
    URGENT = "urgent"
    FINAL_NOTICE = "final_notice"

@dataclass
class MessageTemplate:
    """Template de mensagem"""
    type: MessageType
    subject: str
    content: str
    variables: List[str]
    priority: int = 1

@dataclass
class BillingMessage:
    """Estrutura de mensagem de cobrança"""
    id: str
    client_id: str
    phone: str
    client_name: str
    amount: float
    due_date: str
    message_type: MessageType
    template_id: str
    content: str
    status: MessageStatus
    created_at: str
    scheduled_at: Optional[str] = None
    sent_at: Optional[str] = None
    retry_count: int = 0
    error_message: Optional[str] = None

@dataclass
class BatchResult:
    """Resultado do processamento em lote"""
    total_messages: int
    successful: int
    failed: int
    skipped: int
    execution_time: float
    errors: List[str]

class MessageTemplateManager:
    """Gerenciador de templates de mensagens"""
    
    def __init__(self):
        self.templates: Dict[str, MessageTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Carregar templates padrão"""
        
        # Template inicial de cobrança
        self.templates['initial_br'] = MessageTemplate(
            type=MessageType.INITIAL,
            subject="Cobrança - Vencimento {due_date}",
            content="""Olá {client_name}! 👋

Esperamos que esteja bem! 

📋 Temos uma cobrança pendente em seu nome:
💰 Valor: R$ {amount}
📅 Vencimento: {due_date}

Para efetuar o pagamento ou esclarecer dúvidas, entre em contato conosco.

Agradecemos sua atenção! 🙏""",
            variables=['client_name', 'amount', 'due_date'],
            priority=1
        )
        
        # Template de lembrete
        self.templates['reminder_br'] = MessageTemplate(
            type=MessageType.REMINDER,
            subject="Lembrete - Vencimento {due_date}",
            content="""Oi {client_name}! 🔔

Este é um lembrete amigável sobre sua cobrança:

💰 Valor: R$ {amount}
📅 Vencimento: {due_date}

Se já efetuou o pagamento, pode desconsiderar esta mensagem.

Qualquer dúvida, estamos aqui para ajudar! 😊""",
            variables=['client_name', 'amount', 'due_date'],
            priority=2
        )
        
        # Template urgente
        self.templates['urgent_br'] = MessageTemplate(
            type=MessageType.URGENT,
            subject="URGENTE - Cobrança Vencida",
            content="""Atenção {client_name}! ⚠️

Sua cobrança está VENCIDA:

💰 Valor: R$ {amount}
📅 Venceu em: {due_date}

Para evitar maiores complicações, entre em contato URGENTEMENTE para regularizar a situação.

⚡ Ação necessária IMEDIATA""",
            variables=['client_name', 'amount', 'due_date'],
            priority=3
        )
        
        # Template de aviso final
        self.templates['final_notice_br'] = MessageTemplate(
            type=MessageType.FINAL_NOTICE,
            subject="AVISO FINAL - Última oportunidade",
            content="""🚨 AVISO FINAL - {client_name}

Esta é sua ÚLTIMA OPORTUNIDADE para regularizar:

💰 Valor: R$ {amount}
📅 Vencido desde: {due_date}

⚠️ Próximos passos caso não haja retorno:
• Inclusão em órgãos de proteção ao crédito
• Cobrança judicial

Entre em contato IMEDIATAMENTE! 📞""",
            variables=['client_name', 'amount', 'due_date'],
            priority=4
        )
        
        # Template urgent_reminder (compatibilidade com frontend)
        self.templates['urgent_reminder'] = MessageTemplate(
            type=MessageType.URGENT,
            subject="URGENTE - Cobrança Vencida",
            content="""Atenção {client_name}! ⚠️

Sua fatura está VENCIDA.

💰 Valor: R$ {amount}
📅 Venceu em: {due_date}

Para evitar maiores complicações, entre em contato URGENTEMENTE para regularizar a situação.

⚡ Ação necessária IMEDIATA""",
            variables=['client_name', 'amount', 'due_date'],
            priority=3
        )
        
        logger.info(LogCategory.BILLING, f"Templates carregados: {len(self.templates)}")
    
    def get_template(self, template_id: str) -> Optional[MessageTemplate]:
        """Obter template por ID"""
        return self.templates.get(template_id)
    
    def render_template(self, template_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """Renderizar template com variáveis"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        try:
            content = template.content
            for var, value in variables.items():
                placeholder = '{' + var + '}'
                content = content.replace(placeholder, str(value))
            
            return content
        except Exception as e:
            logger.error(LogCategory.BILLING, f"Erro ao renderizar template {template_id}: {e}")
            return None

class RateLimiter:
    """Controlador de taxa de envio com simulação humana"""
    
    def __init__(self, max_per_minute: int = 10):
        self.max_per_minute = max_per_minute
        self.sent_times: List[float] = []
        self.min_delay = 5  # Mínimo 5 segundos entre mensagens
        self.max_delay = 60  # Máximo 1 minuto entre mensagens
    
    def wait_if_needed(self):
        """Aguardar com tempo variado e simulação humana"""
        now = time.time()
        
        # Remover timestamps antigos (mais de 1 minuto)
        self.sent_times = [t for t in self.sent_times if now - t < 60]
        
        # Verificar se atingiu o limite
        if len(self.sent_times) >= self.max_per_minute:
            # Calcular tempo de espera
            oldest = min(self.sent_times)
            wait_time = 60 - (now - oldest)
            
            if wait_time > 0:
                logger.info(LogCategory.BILLING, f"Rate limit atingido, aguardando {wait_time:.2f}s")
                time.sleep(wait_time)
        
        # Tempo variado entre mensagens (5s a 1min)
        if self.sent_times:
            last_sent = max(self.sent_times)
            time_since_last = now - last_sent
            
            if time_since_last < self.min_delay:
                # Calcular delay aleatório
                import random
                delay = random.uniform(self.min_delay, self.max_delay)
                actual_delay = delay - time_since_last
                
                if actual_delay > 0:
                    logger.info(LogCategory.BILLING, f"Delay inteligente: {actual_delay:.2f}s")
                    time.sleep(actual_delay)
        
        # Registrar envio atual
        self.sent_times.append(time.time())
    
    def simulate_human_typing(self, message: str):
        """Simular digitação humana para evitar detecção"""
        try:
            # Calcular tempo de digitação baseado no tamanho da mensagem
            typing_time = len(message) * 0.05  # 50ms por caractere
            typing_time = max(1, min(typing_time, 10))  # Entre 1s e 10s
            
            logger.debug(LogCategory.BILLING, f"Simulando digitação: {typing_time:.2f}s")
            
            # Simular digitação em chunks
            chunk_size = max(1, len(message) // 10)
            for i in range(0, len(message), chunk_size):
                chunk = message[i:i + chunk_size]
                chunk_time = (len(chunk) / len(message)) * typing_time
                time.sleep(chunk_time)
                
        except Exception as e:
            logger.warning(LogCategory.BILLING, f"Erro na simulação de digitação: {e}")
            # Fallback: delay simples
            time.sleep(2)

class BillingDispatcher:
    """Dispatcher principal de mensagens de cobrança"""
    
    def __init__(self, waha_integration=None, max_per_minute: int = 10, 
                 min_delay: int = 5, max_delay: int = 60):
        self.waha = waha_integration
        self.template_manager = MessageTemplateManager()
        self.rate_limiter = RateLimiter(max_per_minute)
        self.rate_limiter.min_delay = min_delay
        self.rate_limiter.max_delay = max_delay
        self.json_processor = JSONProcessor()
        
        # Configurações
        self.max_retry_attempts = 3
        self.retry_delay = 5  # segundos
        
        # Storage temporário para mensagens
        self.pending_messages: List[BillingMessage] = []
        self.sent_messages: List[BillingMessage] = []
        
        logger.info(LogCategory.BILLING, f"Billing Dispatcher inicializado - Rate: {max_per_minute}/min, Delay: {min_delay}-{max_delay}s")
    
    def configure_smart_dispatch(self, max_per_minute: int = 10, min_delay: int = 5, max_delay: int = 60):
        """Configurar parâmetros de disparo inteligente"""
        self.rate_limiter.max_per_minute = max_per_minute
        self.rate_limiter.min_delay = min_delay
        self.rate_limiter.max_delay = max_delay
        
        logger.info(LogCategory.BILLING, f"🚀 Disparo inteligente configurado: {max_per_minute}/min, delay {min_delay}-{max_delay}s")
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalizar número de telefone para formato do WhatsApp"""
        # Remover caracteres especiais
        clean = ''.join(filter(str.isdigit, phone))
        
        # Adicionar código do país se necessário
        if len(clean) == 11 and clean.startswith('11'):
            clean = '55' + clean
        elif len(clean) == 10:
            clean = '5511' + clean
        elif not clean.startswith('55'):
            clean = '55' + clean
        
        # Formato final para WhatsApp (APENAS CONTATOS INDIVIDUAIS)
        return clean + '@c.us'
    
    def _is_group_chat(self, chat_id: str) -> bool:
        """Verificar se é um grupo do WhatsApp"""
        # Grupos terminam com @g.us
        return chat_id.endswith('@g.us')
    
    def _is_broadcast_list(self, chat_id: str) -> bool:
        """Verificar se é uma lista de transmissão"""
        # Listas de transmissão terminam com @broadcast
        return chat_id.endswith('@broadcast')
    
    def _validate_individual_contact(self, phone: str) -> bool:
        """Validar se é um contato individual válido"""
        try:
            # Normalizar o número
            normalized = self._normalize_phone(phone)
            
            # Verificar se é contato individual
            if self._is_group_chat(normalized):
                logger.warning(LogCategory.BILLING, f"🚫 GRUPO DETECTADO: {phone} - Ignorando")
                return False
            
            if self._is_broadcast_list(normalized):
                logger.warning(LogCategory.BILLING, f"🚫 LISTA DE TRANSMISSÃO DETECTADA: {phone} - Ignorando")
                return False
            
            # Verificar se termina com @c.us (contato individual)
            if not normalized.endswith('@c.us'):
                logger.warning(LogCategory.BILLING, f"🚫 FORMATO INVÁLIDO: {phone} - Ignorando")
                return False
            
            logger.debug(LogCategory.BILLING, f"✅ CONTATO INDIVIDUAL VÁLIDO: {phone}")
            return True
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"Erro ao validar contato {phone}: {e}")
            return False
    
    def load_clients_from_json(self, json_data: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Carregar clientes do JSON - MODO TOLERANTE"""
        try:
            import json
            data = json.loads(json_data)
            clients = data.get('clients', [])
            
            # Processar clientes de forma tolerante
            processed_clients = []
            for idx, client in enumerate(clients):
                try:
                    # Garantir campos obrigatórios com valores padrão
                    processed_client = {
                        'id': client.get('id', f"client_{idx}"),
                        'name': client.get('name', 'Cliente'),
                        'phone': client.get('phone', '11999999999'),
                        'amount': float(client.get('amount', 100.00)),
                        'due_date': client.get('due_date', '2025-12-31'),
                        'document': client.get('document', ''),
                        'city': client.get('city', ''),
                        'contract': client.get('contract', ''),
                        'status': client.get('status', 'active')
                    }
                    
                    # Normalizar telefone
                    phone = str(processed_client['phone']).strip()
                    if len(phone) < 8:
                        phone = '11999999999'
                    processed_client['phone'] = phone
                    
                    processed_clients.append(processed_client)
                    
                except Exception as e:
                    logger.warning(LogCategory.BILLING, f"Erro ao processar cliente {idx}: {e}")
                    continue
            
            logger.info(LogCategory.BILLING, f"✅ {len(processed_clients)} clientes processados com sucesso (modo tolerante)")
            return processed_clients, []
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"Erro ao processar JSON: {e}")
            return [], [f"Erro ao processar JSON: {e}"]
    
    def create_billing_messages(self, clients: List[Dict[str, Any]], 
                              template_id: str = 'initial_br',
                              schedule_time: Optional[datetime] = None) -> List[BillingMessage]:
        """Criar mensagens de cobrança a partir da lista de clientes"""
        messages = []
        skipped_groups = 0
        
        for client in clients:
            try:
                # 🚫 VALIDAÇÃO ANTI-GRUPOS - VERIFICAR SE É CONTATO INDIVIDUAL
                if not self._validate_individual_contact(client['phone']):
                    skipped_groups += 1
                    logger.warning(LogCategory.BILLING, f"🚫 PULANDO GRUPO/LISTA: {client['name']} - {client['phone']}")
                    continue
                
                # Preparar variáveis para o template
                variables = {
                    'client_name': client['name'],
                    'amount': f"{client['amount']:.2f}",
                    'due_date': self._format_date(client['due_date'])
                }
                
                # Renderizar mensagem
                content = self.template_manager.render_template(template_id, variables)
                if not content:
                    logger.error(LogCategory.BILLING, f"Falha ao renderizar template {template_id} para cliente {client['id']}")
                    continue
                
                # Criar mensagem
                message = BillingMessage(
                    id=f"msg_{client['id']}_{int(time.time())}",
                    client_id=client['id'],
                    phone=client['phone'],
                    client_name=client['name'],
                    amount=client['amount'],
                    due_date=client['due_date'],
                    message_type=self.template_manager.get_template(template_id).type,
                    template_id=template_id,
                    content=content,
                    status=MessageStatus.PENDING,
                    created_at=datetime.now().isoformat(),
                    scheduled_at=schedule_time.isoformat() if schedule_time else None
                )
                
                messages.append(message)
                
                logger.debug(LogCategory.BILLING, f"✅ Mensagem criada para {client['name']}", 
                           details={'message_id': message.id, 'phone': message.phone})
                
            except Exception as e:
                logger.error(LogCategory.BILLING, f"Erro ao criar mensagem para cliente {client.get('id', 'unknown')}: {e}")
        
        logger.info(LogCategory.BILLING, f"📊 Mensagens criadas: {len(messages)} | Grupos ignorados: {skipped_groups}")
        return messages
    
    def dispatch_batch(self, messages: List[BillingMessage]) -> BatchResult:
        """Disparar lote de mensagens"""
        start_time = time.time()
        
        successful = 0
        failed = 0
        skipped = 0
        errors = []
        
        logger.info(LogCategory.BILLING, f"Iniciando dispatch de {len(messages)} mensagens")
        
        for message in messages:
            try:
                # Verificar se deve pular mensagem
                if message.status in [MessageStatus.SENT, MessageStatus.CANCELLED]:
                    skipped += 1
                    continue
                
                # Verificar agendamento
                if message.scheduled_at:
                    scheduled_time = datetime.fromisoformat(message.scheduled_at)
                    if datetime.now() < scheduled_time:
                        skipped += 1
                        continue
                
                # Respeitar rate limit
                self.rate_limiter.wait_if_needed()
                
                # Enviar mensagem
                success = self._send_single_message(message)
                
                if success:
                    successful += 1
                    message.status = MessageStatus.SENT
                    message.sent_at = datetime.now().isoformat()
                    self.sent_messages.append(message)
                    
                    logger.billing_event('message_sent', message.client_id, {
                        'phone': message.phone,
                        'message_type': message.message_type.value,
                        'template_id': message.template_id
                    })
                else:
                    failed += 1
                    message.status = MessageStatus.FAILED
                    errors.append(f"Falha ao enviar para {message.phone}")
                
            except Exception as e:
                failed += 1
                message.status = MessageStatus.FAILED
                message.error_message = str(e)
                errors.append(f"Erro ao processar {message.phone}: {e}")
                
                logger.error(LogCategory.BILLING, f"Erro no dispatch da mensagem {message.id}: {e}")
        
        execution_time = time.time() - start_time
        
        result = BatchResult(
            total_messages=len(messages),
            successful=successful,
            failed=failed,
            skipped=skipped,
            execution_time=execution_time,
            errors=errors
        )
        
        logger.info(LogCategory.BILLING, "Batch dispatch concluído", details=asdict(result))
        return result
    
    def _send_single_message(self, message: BillingMessage) -> bool:
        """Enviar uma única mensagem com simulação humana"""
        try:
            # 🚫 VALIDAÇÃO FINAL ANTI-GRUPOS
            if not self._validate_individual_contact(message.phone):
                logger.warning(LogCategory.BILLING, f"🚫 BLOQUEANDO ENVIO PARA GRUPO: {message.phone}")
                message.status = MessageStatus.CANCELLED
                message.error_message = "Grupo detectado - envio bloqueado"
                return False
            
            message.status = MessageStatus.SENDING
            
            # 1. Simular digitação humana ANTES de enviar
            logger.info(LogCategory.BILLING, f"🤖 Simulando digitação para {message.phone}")
            self.rate_limiter.simulate_human_typing(message.content)
            
            # 2. Delay adicional para simular "escrevendo..."
            import random
            writing_delay = random.uniform(1, 3)  # 1-3 segundos
            logger.debug(LogCategory.BILLING, f"✍️ Simulando 'escrevendo...': {writing_delay:.2f}s")
            time.sleep(writing_delay)
            
            # Debug: verificar se Waha está configurado
            logger.info(LogCategory.BILLING, f"🔍 Waha configurado: {self.waha is not None}")
            if self.waha:
                logger.info(LogCategory.BILLING, f"🔍 Waha base URL: {self.waha.base_url}")
            
            if not self.waha:
                # Modo simulação/desenvolvimento
                logger.warning(LogCategory.BILLING, f"⚠️ [SIMULAÇÃO] Waha não configurado - Enviando para {message.phone}")
                logger.info(LogCategory.BILLING, f"📝 Conteúdo: {message.content[:100]}...")
                time.sleep(0.5)  # Simular delay de rede
                return True
            
            # 3. Integração real com Waha (agora síncrona)
            logger.info(LogCategory.BILLING, f"📤 [REAL] Enviando mensagem real para {message.phone}")
            
            # INICIALIZAR SESSÃO ANTES DO ENVIO (igual ao webhook que funciona!)
            self.waha.start_session()
            
            success = self.waha.send_text_message(
                phone=message.phone,
                text=message.content
            )
            
            if success:
                logger.info(LogCategory.BILLING, f"✅ Mensagem enviada com sucesso para {message.phone}")
                return True
            else:
                logger.warning(LogCategory.BILLING, f"❌ Falha no envio para {message.phone}")
                return False
                
        except Exception as e:
            logger.error(LogCategory.BILLING, f"💥 Erro ao enviar mensagem para {message.phone}: {e}")
            return False
    
    def retry_failed_messages(self) -> BatchResult:
        """Reenviar mensagens falhadas"""
        failed_messages = [msg for msg in self.pending_messages if msg.status == MessageStatus.FAILED]
        
        # Filtrar mensagens que ainda podem ser reenviadas
        retry_messages = []
        for msg in failed_messages:
            if msg.retry_count < self.max_retry_attempts:
                msg.retry_count += 1
                msg.status = MessageStatus.RETRY
                retry_messages.append(msg)
        
        if retry_messages:
            logger.info(LogCategory.BILLING, f"Reenviando {len(retry_messages)} mensagens falhadas")
            return self.dispatch_batch(retry_messages)
        
        return BatchResult(0, 0, 0, 0, 0, [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obter estatísticas do dispatcher"""
        total_messages = len(self.pending_messages) + len(self.sent_messages)
        
        status_count = {}
        for status in MessageStatus:
            status_count[status.value] = sum(
                1 for msg in (self.pending_messages + self.sent_messages)
                if msg.status == status
            )
        
        return {
            'total_messages': total_messages,
            'sent_messages': len(self.sent_messages),
            'pending_messages': len(self.pending_messages),
            'status_breakdown': status_count,
            'templates_available': len(self.template_manager.templates)
        }
    
    def _format_date(self, date_str: str) -> str:
        """Formatar data para exibição"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%d/%m/%Y')
        except:
            return date_str
