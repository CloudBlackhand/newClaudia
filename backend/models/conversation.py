"""
Gerenciamento de conversas e contexto para o bot
"""
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from backend.utils.logger import conversation_logger
from backend.config.settings import active_config

@dataclass
class ConversationMessage:
    """Representa uma mensagem na conversa"""
    role: str  # 'user' ou 'assistant'
    content: str
    timestamp: datetime
    message_id: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'message_id': self.message_id,
            'intent': self.intent,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationMessage':
        """Cria instância a partir de dicionário"""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            message_id=data.get('message_id'),
            intent=data.get('intent'),
            confidence=data.get('confidence')
        )

@dataclass
class ConversationContext:
    """Contexto da conversa"""
    phone: str
    client_name: Optional[str] = None
    client_amount: Optional[float] = None
    payment_status: str = "pending"  # pending, negotiating, paid, disputed
    last_template_sent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Campos avançados para cobranças
    financial_entities: Dict[str, List[str]] = None
    billing_intent_history: List[str] = None
    payment_method: Optional[str] = None
    due_date: Optional[datetime] = None
    negotiation_attempts: int = 0
    dispute_reason: Optional[str] = None
    confirmed_amount: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        if self.financial_entities is None:
            self.financial_entities = {}
        if self.billing_intent_history is None:
            self.billing_intent_history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário serializável"""
        return {
            'phone': self.phone,
            'client_name': self.client_name,
            'client_amount': self.client_amount,
            'payment_status': self.payment_status,
            'last_template_sent': self.last_template_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'financial_entities': self.financial_entities,
            'billing_intent_history': self.billing_intent_history,
            'payment_method': self.payment_method,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'negotiation_attempts': self.negotiation_attempts,
            'dispute_reason': self.dispute_reason,
            'confirmed_amount': self.confirmed_amount
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Cria instância a partir de dicionário"""
        context = cls(
            phone=data['phone'],
            client_name=data.get('client_name'),
            client_amount=data.get('client_amount'),
            payment_status=data.get('payment_status', 'pending'),
            last_template_sent=data.get('last_template_sent'),
            payment_method=data.get('payment_method'),
            negotiation_attempts=data.get('negotiation_attempts', 0),
            dispute_reason=data.get('dispute_reason'),
            confirmed_amount=data.get('confirmed_amount'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
        
        # Carrega campos complexos
        context.financial_entities = data.get('financial_entities', {})
        context.billing_intent_history = data.get('billing_intent_history', [])
        
        if data.get('due_date'):
            context.due_date = datetime.fromisoformat(data['due_date'])
            
        return context

class ConversationManager:
    """Gerenciador de conversas ativas"""
    
    def __init__(self, max_conversations: int = 1000):
        self.conversations: Dict[str, List[ConversationMessage]] = {}
        self.contexts: Dict[str, ConversationContext] = {}
        self.max_conversations = max_conversations
        self.cleanup_interval = timedelta(hours=24)  # Remove conversas antigas
        
    def start_conversation(self, phone: str, context: Optional[ConversationContext] = None) -> ConversationContext:
        """Inicia nova conversa ou retorna existente"""
        
        # Limpa conversas antigas se necessário
        self._cleanup_old_conversations()
        
        if phone not in self.conversations:
            self.conversations[phone] = []
            
            # Cria contexto se não fornecido
            if context is None:
                context = ConversationContext(phone=phone)
            
            self.contexts[phone] = context
            
            conversation_logger.conversation_started(phone, "new_conversation")
        else:
            # Atualiza timestamp da conversa existente
            if phone in self.contexts:
                self.contexts[phone].updated_at = datetime.utcnow()
        
        return self.contexts[phone]
    
    def add_message(self, phone: str, role: str, content: str, **kwargs) -> ConversationMessage:
        """Adiciona mensagem à conversa"""
        
        # Garante que conversa existe
        if phone not in self.conversations:
            self.start_conversation(phone)
        
        # Cria mensagem
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            **kwargs
        )
        
        # Adiciona à conversa
        self.conversations[phone].append(message)
        
        # Atualiza contexto
        if phone in self.contexts:
            self.contexts[phone].updated_at = datetime.utcnow()
        
        # Limita tamanho da conversa (mantém apenas últimas N mensagens)
        max_messages = 50
        if len(self.conversations[phone]) > max_messages:
            self.conversations[phone] = self.conversations[phone][-max_messages:]
        
        # Log da mensagem
        if role == "user":
            conversation_logger.message_received(phone, content)
        else:
            conversation_logger.bot_response(
                phone, 
                content,
                kwargs.get('intent'),
                kwargs.get('confidence')
            )
        
        return message
    
    def get_conversation_history(self, phone: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """Retorna histórico da conversa"""
        if phone not in self.conversations:
            return []
        
        history = self.conversations[phone]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_context(self, phone: str) -> Optional[ConversationContext]:
        """Retorna contexto da conversa"""
        return self.contexts.get(phone)
    
    def update_context(self, phone: str, **updates):
        """Atualiza contexto da conversa"""
        if phone in self.contexts:
            for key, value in updates.items():
                if hasattr(self.contexts[phone], key):
                    setattr(self.contexts[phone], key, value)
            
            self.contexts[phone].updated_at = datetime.utcnow()
    
    def end_conversation(self, phone: str):
        """Finaliza conversa"""
        if phone in self.conversations:
            # Calcula estatísticas
            messages_count = len(self.conversations[phone])
            duration = 0
            
            if phone in self.contexts and self.contexts[phone].created_at:
                duration = (datetime.utcnow() - self.contexts[phone].created_at).total_seconds()
            
            conversation_logger.conversation_ended(phone, duration, messages_count)
            
            # Remove da memória
            del self.conversations[phone]
            if phone in self.contexts:
                del self.contexts[phone]
    
    def get_conversation_summary(self, phone: str) -> Dict[str, Any]:
        """Retorna resumo da conversa"""
        if phone not in self.conversations:
            return {"exists": False}
        
        messages = self.conversations[phone]
        context = self.contexts.get(phone)
        
        # Estatísticas básicas
        user_messages = [msg for msg in messages if msg.role == "user"]
        bot_messages = [msg for msg in messages if msg.role == "assistant"]
        
        # Último intent detectado
        last_intent = None
        last_confidence = None
        
        for msg in reversed(bot_messages):
            if msg.intent:
                last_intent = msg.intent
                last_confidence = msg.confidence
                break
        
        summary = {
            "exists": True,
            "total_messages": len(messages),
            "user_messages": len(user_messages),
            "bot_messages": len(bot_messages),
            "last_message_time": messages[-1].timestamp.isoformat() if messages else None,
            "last_intent": last_intent,
            "last_confidence": last_confidence,
            "context": context.to_dict() if context else None
        }
        
        return summary
    
    def _cleanup_old_conversations(self):
        """Remove conversas antigas para liberar memória"""
        cutoff_time = datetime.utcnow() - self.cleanup_interval
        phones_to_remove = []
        
        for phone, context in self.contexts.items():
            if context.updated_at < cutoff_time:
                phones_to_remove.append(phone)
        
        for phone in phones_to_remove:
            if phone in self.conversations:
                del self.conversations[phone]
            if phone in self.contexts:
                del self.contexts[phone]
        
        if phones_to_remove:
            conversation_logger.info("CONVERSATIONS_CLEANED", {
                "removed_count": len(phones_to_remove),
                "active_conversations": len(self.conversations)
            })
    
    def save_conversations_backup(self, backup_path: str) -> bool:
        """Salva backup das conversas em arquivo"""
        try:
            backup_data = {
                "conversations": {
                    phone: [msg.to_dict() for msg in messages]
                    for phone, messages in self.conversations.items()
                },
                "contexts": {
                    phone: context.to_dict()
                    for phone, context in self.contexts.items()
                },
                "backup_timestamp": datetime.utcnow().isoformat()
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            conversation_logger.info("CONVERSATIONS_BACKUP_SAVED", {
                "path": backup_path,
                "conversations_count": len(self.conversations)
            })
            
            return True
            
        except Exception as e:
            conversation_logger.error("CONVERSATIONS_BACKUP_FAILED", e, {"path": backup_path})
            return False
    
    def load_conversations_backup(self, backup_path: str) -> bool:
        """Carrega backup das conversas"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restaura conversas
            for phone, messages_data in backup_data.get("conversations", {}).items():
                self.conversations[phone] = [
                    ConversationMessage.from_dict(msg_data)
                    for msg_data in messages_data
                ]
            
            # Restaura contextos
            for phone, context_data in backup_data.get("contexts", {}).items():
                self.contexts[phone] = ConversationContext.from_dict(context_data)
            
            conversation_logger.info("CONVERSATIONS_BACKUP_LOADED", {
                "path": backup_path,
                "conversations_count": len(self.conversations)
            })
            
            return True
            
        except Exception as e:
            conversation_logger.error("CONVERSATIONS_BACKUP_LOAD_FAILED", e, {"path": backup_path})
            return False
    
    def get_active_conversations_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das conversas ativas"""
        stats = {
            "total_conversations": len(self.conversations),
            "total_messages": sum(len(msgs) for msgs in self.conversations.values()),
            "conversations_by_status": {},
            "recent_activity": 0
        }
        
        # Conta por status
        for phone, context in self.contexts.items():
            status = context.payment_status
            stats["conversations_by_status"][status] = stats["conversations_by_status"].get(status, 0) + 1
        
        # Atividade recente (últimas 24h)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        for phone, context in self.contexts.items():
            if context.updated_at > recent_cutoff:
                stats["recent_activity"] += 1
        
        return stats
    
    def update_billing_context(self, phone: str, financial_entities: Dict[str, List[str]], 
                             billing_intent: str, payment_method: Optional[str] = None,
                             due_date: Optional[datetime] = None):
        """Atualiza contexto com informações de cobrança"""
        if phone in self.contexts:
            context = self.contexts[phone]
            
            # Atualiza entidades financeiras
            if financial_entities:
                for entity_type, values in financial_entities.items():
                    if entity_type not in context.financial_entities:
                        context.financial_entities[entity_type] = []
                    context.financial_entities[entity_type].extend(values)
                    # Remove duplicatas
                    context.financial_entities[entity_type] = list(set(context.financial_entities[entity_type]))
            
            # Atualiza histórico de intenções
            if billing_intent and billing_intent not in context.billing_intent_history:
                context.billing_intent_history.append(billing_intent)
            
            # Atualiza outros campos
            if payment_method:
                context.payment_method = payment_method
            if due_date:
                context.due_date = due_date
                
            context.updated_at = datetime.utcnow()
    
    def get_billing_insights(self, phone: str) -> Dict[str, Any]:
        """Retorna insights avançados sobre a conversa de cobrança"""
        if phone not in self.contexts:
            return {"exists": False}
        
        context = self.contexts[phone]
        messages = self.conversations.get(phone, [])
        
        insights = {
            "exists": True,
            "financial_entities": context.financial_entities,
            "intent_history": context.billing_intent_history,
            "payment_method": context.payment_method,
            "due_date": context.due_date.isoformat() if context.due_date else None,
            "negotiation_attempts": context.negotiation_attempts,
            "dispute_reason": context.dispute_reason,
            "confirmed_amount": context.confirmed_amount,
            "conversation_duration_minutes": 0,
            "user_message_count": 0,
            "emotional_indicators": []
        }
        
        if messages and context.created_at:
            duration = (messages[-1].timestamp - context.created_at).total_seconds() / 60
            insights["conversation_duration_minutes"] = round(duration, 2)
            
        user_messages = [msg for msg in messages if msg.role == "user"]
        insights["user_message_count"] = len(user_messages)
        
        # Análise de sentimento baseada em palavras-chave
        emotional_keywords = {
            "frustration": ["raiva", "bravo", "irritado", "odio"],
            "anxiety": ["preocupado", "medo", "ansioso", "desesperado"],
            "cooperation": ["entendo", "ajuda", "obrigado", "valeu"]
        }
        
        for category, keywords in emotional_keywords.items():
            for msg in user_messages:
                content_lower = msg.content.lower()
                if any(keyword in content_lower for keyword in keywords):
                    insights["emotional_indicators"].append(category)
                    break
        
        return insights
    
    def increment_negotiation_attempt(self, phone: str):
        """Incrementa contador de tentativas de negociação"""
        if phone in self.contexts:
            self.contexts[phone].negotiation_attempts += 1
            self.contexts[phone].updated_at = datetime.utcnow()

# Instância global do gerenciador
conversation_manager = ConversationManager()

