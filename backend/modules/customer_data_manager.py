#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Dados dos Clientes com Persistência SQL
Sistema para armazenar e recuperar dados dos clientes de forma persistente
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configuração de logging
logger = logging.getLogger(__name__)

@dataclass
class CustomerData:
    """Dados completos do cliente para cobrança"""
    phone: str
    name: str
    documento: str
    debt_amount: float
    days_overdue: int
    due_date: str
    protocolo: str
    contrato: str
    regional: str
    territorio: str
    plano: str
    valor_mensalidade: float
    company: str
    status: str
    priority: str
    is_customer: bool
    last_contact: Optional[str] = None
    conversation_count: int = 0
    payment_promises: int = 0
    last_payment_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@dataclass
class ConversationContext:
    """Contexto persistente da conversa"""
    phone: str
    customer_name: str
    debt_amount: float
    days_overdue: int
    conversation_history: List[Dict]
    cooperation_level: float = 0.5
    lie_probability: float = 0.0
    urgency_level: float = 0.5
    last_intent: Optional[str] = None
    last_sentiment: Optional[str] = None
    payment_promises: int = 0
    last_contact: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CustomerDataManager:
    """Gerenciador inteligente de dados dos clientes com cache + persistência"""
    
    def __init__(self):
        self.memory_cache: Dict[str, CustomerData] = {}
        self.conversation_cache: Dict[str, ConversationContext] = {}
        self.cache_ttl = timedelta(hours=24)  # Cache válido por 24h
        self.last_cache_cleanup = datetime.now()
        
        # Importar gerenciador de banco se disponível
        try:
            from backend.database.database_manager import db_manager
            self.db_manager = db_manager
            self.database_available = True
            logger.info("🗄️ Banco de dados integrado ao CustomerDataManager")
        except ImportError:
            self.db_manager = None
            self.database_available = False
            logger.warning("⚠️ Banco de dados não disponível - usando apenas cache")
    
    def save_customer_data(self, customer_data: Dict[str, Any]) -> bool:
        """
        💾 SALVAR DADOS DO CLIENTE NO BANCO + CACHE
        
        Salva dados do cliente de forma persistente para uso futuro
        """
        try:
            # Converter para objeto CustomerData
            customer = CustomerData(
                phone=customer_data.get('phone', ''),
                name=customer_data.get('name', 'Cliente'),
                documento=customer_data.get('documento', ''),
                debt_amount=float(customer_data.get('debt_amount', 0)),
                days_overdue=int(customer_data.get('days_overdue', 0)),
                due_date=customer_data.get('due_date', ''),
                protocolo=customer_data.get('protocolo', ''),
                contrato=customer_data.get('contrato', ''),
                regional=customer_data.get('regional', ''),
                territorio=customer_data.get('territorio', ''),
                plano=customer_data.get('plano', ''),
                valor_mensalidade=float(customer_data.get('valor_mensalidade', 0)),
                company=customer_data.get('company', ''),
                status=customer_data.get('status', 'active'),
                priority=customer_data.get('priority', 'medium'),
                is_customer=customer_data.get('is_customer', True),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # ✅ SALVAR NO BANCO SQL (PERSISTENTE)
            if self.database_available and self.db_manager:
                try:
                    # Salvar na tabela de clientes
                    success = self.db_manager.save_customer_data(customer)
                    if success:
                        logger.info(f"💾 Cliente {customer.name} salvo no banco SQL")
                    else:
                        logger.warning(f"⚠️ Falha ao salvar cliente {customer.name} no banco")
                except Exception as e:
                    logger.error(f"❌ Erro ao salvar no banco: {str(e)}")
            
            # ✅ SALVAR NO CACHE (RÁPIDO)
            self.memory_cache[customer.phone] = customer
            logger.info(f"📱 Cliente {customer.name} salvo no cache: {customer.phone}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados do cliente: {str(e)}")
            return False
    
    def get_customer_data(self, phone: str) -> Optional[CustomerData]:
        """
        🔍 BUSCAR DADOS DO CLIENTE (CACHE + BANCO)
        
        Busca dados do cliente primeiro no cache, depois no banco
        """
        try:
            # 1. 🚀 TENTAR CACHE (RÁPIDO)
            if phone in self.memory_cache:
                customer = self.memory_cache[phone]
                logger.info(f"⚡ Cliente {customer.name} encontrado no cache: {phone}")
                return customer
            
            # 2. 🗄️ BUSCAR NO BANCO (PERSISTENTE)
            if self.database_available and self.db_manager:
                try:
                    # Buscar por telefone
                    customer = self.db_manager.get_customer_by_phone(phone)
                    if customer:
                        # Converter para CustomerData
                        customer_data = CustomerData(
                            phone=customer.phone,
                            name=customer.name,
                            documento=customer.documento,
                            debt_amount=customer.debt_amount,
                            days_overdue=customer.days_overdue,
                            due_date=customer.due_date,
                            protocolo=customer.protocolo,
                            contrato=customer.contrato,
                            regional=customer.regional,
                            territorio=customer.territorio,
                            plano=customer.plano,
                            valor_mensalidade=customer.valor_mensalidade,
                            company=customer.company,
                            status=customer.status,
                            priority=customer.priority,
                            is_customer=customer.is_customer,
                            created_at=customer.created_at,
                            updated_at=customer.updated_at
                        )
                        
                        # Salvar no cache para próximas consultas
                        self.memory_cache[phone] = customer_data
                        logger.info(f"🗄️ Cliente {customer_data.name} carregado do banco: {phone}")
                        return customer_data
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao buscar no banco: {str(e)}")
            
            # 3. ❌ CLIENTE NÃO ENCONTRADO
            logger.warning(f"⚠️ Cliente não encontrado: {phone}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar dados do cliente: {str(e)}")
            return None
    
    def save_conversation_context(self, phone: str, context: ConversationContext) -> bool:
        """
        💾 SALVAR CONTEXTO DA CONVERSA (PERSISTENTE)
        
        Salva contexto da conversa para continuidade entre sessões
        """
        try:
            # Atualizar timestamps
            context.updated_at = datetime.now().isoformat()
            if not context.created_at:
                context.created_at = context.updated_at
            
            # ✅ SALVAR NO BANCO SQL
            if self.database_available and self.db_manager:
                try:
                    success = self.db_manager.save_conversation_context(context)
                    if success:
                        logger.info(f"💾 Contexto da conversa salvo no banco: {phone}")
                    else:
                        logger.warning(f"⚠️ Falha ao salvar contexto no banco: {phone}")
                except Exception as e:
                    logger.error(f"❌ Erro ao salvar contexto no banco: {str(e)}")
            
            # ✅ SALVAR NO CACHE
            self.conversation_cache[phone] = context
            logger.info(f"📱 Contexto da conversa salvo no cache: {phone}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar contexto da conversa: {str(e)}")
            return False
    
    def get_conversation_context(self, phone: str) -> Optional[ConversationContext]:
        """
        🔍 BUSCAR CONTEXTO DA CONVERSA (CACHE + BANCO)
        
        Busca contexto da conversa para continuidade
        """
        try:
            # 1. 🚀 TENTAR CACHE
            if phone in self.conversation_cache:
                context = self.conversation_cache[phone]
                logger.info(f"⚡ Contexto da conversa encontrado no cache: {phone}")
                return context
            
            # 2. 🗄️ BUSCAR NO BANCO
            if self.database_available and self.db_manager:
                try:
                    context = self.db_manager.get_conversation_context(phone)
                    if context:
                        # Converter para ConversationContext
                        conversation_context = ConversationContext(
                            phone=context.phone,
                            customer_name=context.customer_name,
                            debt_amount=context.debt_amount,
                            days_overdue=context.days_overdue,
                            conversation_history=context.conversation_history,
                            cooperation_level=context.cooperation_level,
                            lie_probability=context.lie_probability,
                            urgency_level=context.urgency_level,
                            last_intent=context.last_intent,
                            last_sentiment=context.last_sentiment,
                            payment_promises=context.payment_promises,
                            last_contact=context.last_contact,
                            created_at=context.created_at,
                            updated_at=context.updated_at
                        )
                        
                        # Salvar no cache
                        self.conversation_cache[phone] = conversation_context
                        logger.info(f"🗄️ Contexto da conversa carregado do banco: {phone}")
                        return conversation_context
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao buscar contexto no banco: {str(e)}")
            
            # 3. ❌ CONTEXTO NÃO ENCONTRADO
            logger.warning(f"⚠️ Contexto da conversa não encontrado: {phone}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar contexto da conversa: {str(e)}")
            return None
    
    def update_customer_interaction(self, phone: str, interaction_data: Dict[str, Any]) -> bool:
        """
        📝 ATUALIZAR INTERAÇÃO DO CLIENTE
        
        Atualiza dados do cliente com nova interação
        """
        try:
            # Buscar cliente atual
            customer = self.get_customer_data(phone)
            if not customer:
                logger.warning(f"⚠️ Cliente não encontrado para atualização: {phone}")
                return False
            
            # Atualizar dados
            customer.conversation_count += 1
            customer.last_contact = datetime.now().isoformat()
            customer.updated_at = datetime.now().isoformat()
            
            # Atualizar promessas de pagamento se aplicável
            if interaction_data.get('intent') == 'pagamento_confirmado':
                customer.payment_promises += 1
            
            # Salvar atualizações
            success = self.save_customer_data(asdict(customer))
            if success:
                logger.info(f"📝 Interação do cliente {customer.name} atualizada: {phone}")
                return True
            else:
                logger.error(f"❌ Falha ao atualizar interação do cliente: {phone}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar interação do cliente: {str(e)}")
            return False
    
    def cleanup_expired_cache(self) -> int:
        """
        🧹 LIMPAR CACHE EXPIRADO
        
        Remove itens do cache que expiraram
        """
        try:
            now = datetime.now()
            expired_count = 0
            
            # Limpar cache de clientes
            expired_phones = []
            for phone, customer in self.memory_cache.items():
                if customer.updated_at:
                    updated = datetime.fromisoformat(customer.updated_at)
                    if now - updated > self.cache_ttl:
                        expired_phones.append(phone)
            
            for phone in expired_phones:
                del self.memory_cache[phone]
                expired_count += 1
            
            # Limpar cache de conversas
            expired_conversations = []
            for phone, context in self.conversation_cache.items():
                if context.updated_at:
                    updated = datetime.fromisoformat(context.updated_at)
                    if now - updated > self.cache_ttl:
                        expired_conversations.append(phone)
            
            for phone in expired_conversations:
                del self.conversation_cache[phone]
                expired_count += 1
            
            if expired_count > 0:
                logger.info(f"🧹 Cache limpo: {expired_count} itens expirados removidos")
            
            self.last_cache_cleanup = now
            return expired_count
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {str(e)}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        📊 ESTATÍSTICAS DO CACHE
        
        Retorna estatísticas do sistema de cache
        """
        try:
            # Limpar cache expirado automaticamente
            if datetime.now() - self.last_cache_cleanup > timedelta(hours=1):
                self.cleanup_expired_cache()
            
            return {
                'customers_in_cache': len(self.memory_cache),
                'conversations_in_cache': len(self.conversation_cache),
                'cache_ttl_hours': self.cache_ttl.total_seconds() / 3600,
                'last_cleanup': self.last_cache_cleanup.isoformat(),
                'database_available': self.database_available
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas do cache: {str(e)}")
            return {}
    
    def clear_all_cache(self) -> bool:
        """
        🗑️ LIMPAR TODO O CACHE
        
        Remove todos os itens do cache (útil para testes)
        """
        try:
            customer_count = len(self.memory_cache)
            conversation_count = len(self.conversation_cache)
            
            self.memory_cache.clear()
            self.conversation_cache.clear()
            
            logger.info(f"🗑️ Cache limpo: {customer_count} clientes e {conversation_count} conversas removidos")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {str(e)}")
            return False

# Instância global do gerenciador
customer_data_manager = CustomerDataManager()

# Funções de conveniência para uso externo
def save_customer_data(customer_data: Dict[str, Any]) -> bool:
    """Salvar dados do cliente"""
    return customer_data_manager.save_customer_data(customer_data)

def get_customer_data(phone: str) -> Optional[CustomerData]:
    """Buscar dados do cliente"""
    return customer_data_manager.get_customer_data(phone)

def save_conversation_context(phone: str, context: ConversationContext) -> bool:
    """Salvar contexto da conversa"""
    return customer_data_manager.save_conversation_context(phone, context)

def get_conversation_context(phone: str) -> Optional[ConversationContext]:
    """Buscar contexto da conversa"""
    return customer_data_manager.get_conversation_context(phone)

def update_customer_interaction(phone: str, interaction_data: Dict[str, Any]) -> bool:
    """Atualizar interação do cliente"""
    return customer_data_manager.update_customer_interaction(phone, interaction_data)

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 TESTANDO CUSTOMER DATA MANAGER")
    
    # Teste de dados de cliente
    test_customer = {
        'phone': '11999999999',
        'name': 'João Silva',
        'documento': '123.456.789-00',
        'debt_amount': 1500.00,
        'days_overdue': 45,
        'due_date': '2024-08-15',
        'protocolo': '12345',
        'contrato': '67890',
        'regional': 'Central',
        'territorio': 'São Paulo',
        'plano': 'Fibra 600M',
        'valor_mensalidade': 99.99,
        'company': 'DESKTOP_SF',
        'status': 'active',
        'priority': 'high',
        'is_customer': True
    }
    
    # Salvar cliente
    success = save_customer_data(test_customer)
    print(f"✅ Cliente salvo: {success}")
    
    # Buscar cliente
    customer = get_customer_data('11999999999')
    if customer:
        print(f"✅ Cliente encontrado: {customer.name} - R$ {customer.debt_amount}")
    else:
        print("❌ Cliente não encontrado")
    
    # Estatísticas do cache
    stats = customer_data_manager.get_cache_stats()
    print(f"📊 Estatísticas do cache: {stats}")
    
    print("✅ TESTE COMPLETO!")
