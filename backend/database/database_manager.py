#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Banco de Dados PostgreSQL
Sistema para persistir dados dos clientes e conversas
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Configuração de logging
logger = logging.getLogger(__name__)

# Configurações do banco (serão carregadas do Railway)
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/cobranca')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'cobranca')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

@dataclass
class Customer:
    """Modelo de dados do cliente para banco"""
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
class Conversation:
    """Modelo de dados da conversa para banco"""
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

class DatabaseManager:
    """Gerenciador do banco de dados PostgreSQL"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connected = False
        
        # Tentar conectar ao banco
        self._connect()
        
        # Criar tabelas se não existirem
        if self.connected:
            self._create_tables()
    
    def _connect(self):
        """Conecta ao banco PostgreSQL"""
        try:
            # Tentar usar psycopg2 (PostgreSQL)
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            # Construir string de conexão
            if DATABASE_URL and DATABASE_URL != 'postgresql://localhost:5432/cobranca':
                # Railway ou conexão externa
                self.connection = psycopg2.connect(DATABASE_URL)
            else:
                # Conexão local
                self.connection = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD
                )
            
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            self.connected = True
            
            logger.info("🗄️ Conectado ao PostgreSQL com sucesso!")
            
        except ImportError:
            logger.error("❌ psycopg2 não instalado - instale com: pip install psycopg2-binary")
            self.connected = False
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao PostgreSQL: {str(e)}")
            self.connected = False
    
    def _create_tables(self):
        """Cria tabelas necessárias se não existirem"""
        try:
            # Tabela de clientes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    phone VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    documento VARCHAR(20),
                    debt_amount DECIMAL(10,2) DEFAULT 0.0,
                    days_overdue INTEGER DEFAULT 0,
                    due_date VARCHAR(20),
                    protocolo VARCHAR(50),
                    contrato VARCHAR(50),
                    regional VARCHAR(100),
                    territorio VARCHAR(100),
                    plano VARCHAR(100),
                    valor_mensalidade DECIMAL(10,2) DEFAULT 0.0,
                    company VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'active',
                    priority VARCHAR(50) DEFAULT 'medium',
                    is_customer BOOLEAN DEFAULT TRUE,
                    last_contact TIMESTAMP,
                    conversation_count INTEGER DEFAULT 0,
                    payment_promises INTEGER DEFAULT 0,
                    last_payment_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabela de conversas
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    phone VARCHAR(20) UNIQUE NOT NULL,
                    customer_name VARCHAR(255) NOT NULL,
                    debt_amount DECIMAL(10,2) DEFAULT 0.0,
                    days_overdue INTEGER DEFAULT 0,
                    conversation_history JSONB DEFAULT '[]',
                    cooperation_level DECIMAL(3,2) DEFAULT 0.5,
                    lie_probability DECIMAL(3,2) DEFAULT 0.0,
                    urgency_level DECIMAL(3,2) DEFAULT 0.5,
                    last_intent VARCHAR(100),
                    last_sentiment VARCHAR(100),
                    payment_promises INTEGER DEFAULT 0,
                    last_contact TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Índices para performance
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_phone ON conversations(phone)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(status)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_company ON customers(company)")
            
            self.connection.commit()
            logger.info("✅ Tabelas criadas/verificadas com sucesso!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {str(e)}")
            self.connected = False
    
    def save_customer_data(self, customer: Customer) -> bool:
        """Salva dados do cliente no banco"""
        try:
            if not self.connected:
                logger.warning("⚠️ Banco não conectado - usando cache apenas")
                return False
            
            # Verificar se cliente já existe
            self.cursor.execute("SELECT id FROM customers WHERE phone = %s", (customer.phone,))
            existing = self.cursor.fetchone()
            
            if existing:
                # Atualizar cliente existente
                self.cursor.execute("""
                    UPDATE customers SET
                        name = %s, documento = %s, debt_amount = %s, days_overdue = %s,
                        due_date = %s, protocolo = %s, contrato = %s, regional = %s,
                        territorio = %s, plano = %s, valor_mensalidade = %s, company = %s,
                        status = %s, priority = %s, is_customer = %s, last_contact = %s,
                        conversation_count = %s, payment_promises = %s, last_payment_date = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE phone = %s
                """, (
                    customer.name, customer.documento, customer.debt_amount, customer.days_overdue,
                    customer.due_date, customer.protocolo, customer.contrato, customer.regional,
                    customer.territorio, customer.plano, customer.valor_mensalidade, customer.company,
                    customer.status, customer.priority, customer.is_customer, customer.last_contact,
                    customer.conversation_count, customer.payment_promises, customer.last_payment_date,
                    customer.phone
                ))
                logger.info(f"🔄 Cliente {customer.name} atualizado no banco")
            else:
                # Inserir novo cliente
                self.cursor.execute("""
                    INSERT INTO customers (
                        phone, name, documento, debt_amount, days_overdue, due_date,
                        protocolo, contrato, regional, territorio, plano, valor_mensalidade,
                        company, status, priority, is_customer, last_contact,
                        conversation_count, payment_promises, last_payment_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    customer.phone, customer.name, customer.documento, customer.debt_amount,
                    customer.days_overdue, customer.due_date, customer.protocolo, customer.contrato,
                    customer.regional, customer.territorio, customer.plano, customer.valor_mensalidade,
                    customer.company, customer.status, customer.priority, customer.is_customer,
                    customer.last_contact, customer.conversation_count, customer.payment_promises,
                    customer.last_payment_date
                ))
                logger.info(f"✅ Cliente {customer.name} inserido no banco")
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cliente no banco: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_customer_by_phone(self, phone: str) -> Optional[Customer]:
        """Busca cliente por telefone"""
        try:
            if not self.connected:
                return None
            
            self.cursor.execute("""
                SELECT * FROM customers WHERE phone = %s
            """, (phone,))
            
            result = self.cursor.fetchone()
            if result:
                # Converter resultado para Customer
                customer = Customer(
                    phone=result['phone'],
                    name=result['name'],
                    documento=result['documento'] or '',
                    debt_amount=float(result['debt_amount'] or 0),
                    days_overdue=int(result['days_overdue'] or 0),
                    due_date=result['due_date'] or '',
                    protocolo=result['protocolo'] or '',
                    contrato=result['contrato'] or '',
                    regional=result['regional'] or '',
                    territorio=result['territorio'] or '',
                    plano=result['plano'] or '',
                    valor_mensalidade=float(result['valor_mensalidade'] or 0),
                    company=result['company'] or '',
                    status=result['status'] or 'active',
                    priority=result['priority'] or 'medium',
                    is_customer=bool(result['is_customer']),
                    last_contact=result['last_contact'].isoformat() if result['last_contact'] else None,
                    conversation_count=int(result['conversation_count'] or 0),
                    payment_promises=int(result['payment_promises'] or 0),
                    last_payment_date=result['last_payment_date'].isoformat() if result['last_payment_date'] else None,
                    created_at=result['created_at'].isoformat() if result['created_at'] else None,
                    updated_at=result['updated_at'].isoformat() if result['updated_at'] else None
                )
                return customer
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar cliente no banco: {str(e)}")
            return None
    
    def save_conversation_context(self, context: Conversation) -> bool:
        """Salva contexto da conversa no banco"""
        try:
            if not self.connected:
                logger.warning("⚠️ Banco não conectado - usando cache apenas")
                return False
            
            # Verificar se conversa já existe
            self.cursor.execute("SELECT id FROM conversations WHERE phone = %s", (context.phone,))
            existing = self.cursor.fetchone()
            
            if existing:
                # Atualizar conversa existente
                self.cursor.execute("""
                    UPDATE conversations SET
                        customer_name = %s, debt_amount = %s, days_overdue = %s,
                        conversation_history = %s, cooperation_level = %s, lie_probability = %s,
                        urgency_level = %s, last_intent = %s, last_sentiment = %s,
                        payment_promises = %s, last_contact = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE phone = %s
                """, (
                    context.customer_name, context.debt_amount, context.days_overdue,
                    json.dumps(context.conversation_history), context.cooperation_level,
                    context.lie_probability, context.urgency_level, context.last_intent,
                    context.last_sentiment, context.payment_promises, context.last_contact,
                    context.phone
                ))
                logger.info(f"🔄 Contexto da conversa atualizado no banco: {context.phone}")
            else:
                # Inserir nova conversa
                self.cursor.execute("""
                    INSERT INTO conversations (
                        phone, customer_name, debt_amount, days_overdue, conversation_history,
                        cooperation_level, lie_probability, urgency_level, last_intent,
                        last_sentiment, payment_promises, last_contact
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    context.phone, context.customer_name, context.debt_amount,
                    context.days_overdue, json.dumps(context.conversation_history),
                    context.cooperation_level, context.lie_probability, context.urgency_level,
                    context.last_intent, context.last_sentiment, context.payment_promises,
                    context.last_contact
                ))
                logger.info(f"✅ Contexto da conversa inserido no banco: {context.phone}")
            
            self.connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar contexto no banco: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_conversation_context(self, phone: str) -> Optional[Conversation]:
        """Busca contexto da conversa por telefone"""
        try:
            if not self.connected:
                return None
            
            self.cursor.execute("""
                SELECT * FROM conversations WHERE phone = %s
            """, (phone,))
            
            result = self.cursor.fetchone()
            if result:
                # Converter resultado para Conversation
                conversation = Conversation(
                    phone=result['phone'],
                    customer_name=result['customer_name'],
                    debt_amount=float(result['debt_amount'] or 0),
                    days_overdue=int(result['days_overdue'] or 0),
                    conversation_history=json.loads(result['conversation_history'] or '[]'),
                    cooperation_level=float(result['cooperation_level'] or 0.5),
                    lie_probability=float(result['lie_probability'] or 0.0),
                    urgency_level=float(result['urgency_level'] or 0.5),
                    last_intent=result['last_intent'],
                    last_sentiment=result['last_sentiment'],
                    payment_promises=int(result['payment_promises'] or 0),
                    last_contact=result['last_contact'].isoformat() if result['last_contact'] else None,
                    created_at=result['created_at'].isoformat() if result['created_at'] else None,
                    updated_at=result['updated_at'].isoformat() if result['updated_at'] else None
                )
                return conversation
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar contexto no banco: {str(e)}")
            return None
    
    def get_all_customers(self, limit: int = 1000) -> List[Customer]:
        """Busca todos os clientes (limitado)"""
        try:
            if not self.connected:
                return []
            
            self.cursor.execute("""
                SELECT * FROM customers ORDER BY updated_at DESC LIMIT %s
            """, (limit,))
            
            results = self.cursor.fetchall()
            customers = []
            
            for result in results:
                customer = Customer(
                    phone=result['phone'],
                    name=result['name'],
                    documento=result['documento'] or '',
                    debt_amount=float(result['debt_amount'] or 0),
                    days_overdue=int(result['days_overdue'] or 0),
                    due_date=result['due_date'] or '',
                    protocolo=result['protocolo'] or '',
                    contrato=result['contrato'] or '',
                    regional=result['regional'] or '',
                    territorio=result['territorio'] or '',
                    plano=result['plano'] or '',
                    valor_mensalidade=float(result['valor_mensalidade'] or 0),
                    company=result['company'] or '',
                    status=result['status'] or 'active',
                    priority=result['priority'] or 'medium',
                    is_customer=bool(result['is_customer']),
                    last_contact=result['last_contact'].isoformat() if result['last_contact'] else None,
                    conversation_count=int(result['conversation_count'] or 0),
                    payment_promises=int(result['payment_promises'] or 0),
                    last_payment_date=result['last_payment_date'].isoformat() if result['last_payment_date'] else None,
                    created_at=result['created_at'].isoformat() if result['created_at'] else None,
                    updated_at=result['updated_at'].isoformat() if result['updated_at'] else None
                )
                customers.append(customer)
            
            return customers
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar clientes no banco: {str(e)}")
            return []
    
    def get_customers_by_company(self, company: str) -> List[Customer]:
        """Busca clientes por empresa"""
        try:
            if not self.connected:
                return []
            
            self.cursor.execute("""
                SELECT * FROM customers WHERE company = %s ORDER BY updated_at DESC
            """, (company,))
            
            results = self.cursor.fetchall()
            customers = []
            
            for result in results:
                customer = Customer(
                    phone=result['phone'],
                    name=result['name'],
                    documento=result['documento'] or '',
                    debt_amount=float(result['debt_amount'] or 0),
                    days_overdue=int(result['days_overdue'] or 0),
                    due_date=result['due_date'] or '',
                    protocolo=result['protocolo'] or '',
                    contrato=result['contrato'] or '',
                    regional=result['regional'] or '',
                    territorio=result['territorio'] or '',
                    plano=result['plano'] or '',
                    valor_mensalidade=float(result['valor_mensalidade'] or 0),
                    company=result['company'] or '',
                    status=result['status'] or 'active',
                    priority=result['priority'] or 'medium',
                    is_customer=bool(result['is_customer']),
                    last_contact=result['last_contact'].isoformat() if result['last_contact'] else None,
                    conversation_count=int(result['conversation_count'] or 0),
                    payment_promises=int(result['payment_promises'] or 0),
                    last_payment_date=result['last_payment_date'].isoformat() if result['last_payment_date'] else None,
                    created_at=result['created_at'].isoformat() if result['created_at'] else None,
                    updated_at=result['updated_at'].isoformat() if result['updated_at'] else None
                )
                customers.append(customer)
            
            return customers
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar clientes por empresa: {str(e)}")
            return []
    
    def delete_customer(self, phone: str) -> bool:
        """Remove cliente do banco"""
        try:
            if not self.connected:
                return False
            
            self.cursor.execute("DELETE FROM customers WHERE phone = %s", (phone,))
            self.cursor.execute("DELETE FROM conversations WHERE phone = %s", (phone,))
            
            self.connection.commit()
            logger.info(f"🗑️ Cliente {phone} removido do banco")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover cliente: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def clear_all_data(self) -> bool:
        """Remove todos os dados (CUIDADO!)"""
        try:
            if not self.connected:
                return False
            
            self.cursor.execute("DELETE FROM conversations")
            self.cursor.execute("DELETE FROM customers")
            
            self.connection.commit()
            logger.warning("🗑️ TODOS OS DADOS FORAM REMOVIDOS!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar dados: {str(e)}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco"""
        try:
            if not self.connected:
                return {'connected': False}
            
            # Contar clientes
            self.cursor.execute("SELECT COUNT(*) as total FROM customers")
            customers_count = self.cursor.fetchone()['total']
            
            # Contar conversas
            self.cursor.execute("SELECT COUNT(*) as total FROM conversations")
            conversations_count = self.cursor.fetchone()['total']
            
            # Total de dívidas
            self.cursor.execute("SELECT SUM(debt_amount) as total FROM customers WHERE debt_amount > 0")
            total_debt = self.cursor.fetchone()['total'] or 0
            
            # Clientes com dívida
            self.cursor.execute("SELECT COUNT(*) as total FROM customers WHERE debt_amount > 0")
            customers_with_debt = self.cursor.fetchone()['total']
            
            return {
                'connected': True,
                'customers_total': customers_count,
                'conversations_total': conversations_count,
                'total_debt': float(total_debt),
                'customers_with_debt': customers_with_debt,
                'database_url': DATABASE_URL if 'localhost' not in DATABASE_URL else 'Local',
                'connection_info': {
                    'host': DB_HOST,
                    'port': DB_PORT,
                    'database': DB_NAME,
                    'user': DB_USER
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            return {'connected': False, 'error': str(e)}
    
    def close(self):
        """Fecha conexão com o banco"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connected = False
            logger.info("🔌 Conexão com banco fechada")
        except Exception as e:
            logger.error(f"❌ Erro ao fechar conexão: {str(e)}")

# Instância global do gerenciador
db_manager = DatabaseManager()

# Funções de conveniência
def save_customer_data(customer: Customer) -> bool:
    """Salvar dados do cliente"""
    return db_manager.save_customer_data(customer)

def get_customer_by_phone(phone: str) -> Optional[Customer]:
    """Buscar cliente por telefone"""
    return db_manager.get_customer_by_phone(phone)

def save_conversation_context(context: Conversation) -> bool:
    """Salvar contexto da conversa"""
    return db_manager.save_conversation_context(context)

def get_conversation_context(phone: str) -> Optional[Conversation]:
    """Buscar contexto da conversa"""
    return db_manager.get_conversation_context(phone)

def get_all_customers(limit: int = 1000) -> List[Customer]:
    """Buscar todos os clientes"""
    return db_manager.get_all_customers(limit)

def get_customers_by_company(company: str) -> List[Customer]:
    """Buscar clientes por empresa"""
    return db_manager.get_customers_by_company(company)

def delete_customer(phone: str) -> bool:
    """Remover cliente"""
    return db_manager.delete_customer(phone)

def clear_all_data() -> bool:
    """Limpar todos os dados"""
    return db_manager.clear_all_data()

def get_database_stats() -> Dict[str, Any]:
    """Obter estatísticas do banco"""
    return db_manager.get_database_stats()

if __name__ == "__main__":
    # Teste do sistema
    print("🧪 TESTANDO DATABASE MANAGER")
    
    # Verificar conexão
    stats = get_database_stats()
    print(f"📊 Estatísticas: {stats}")
    
    if stats['connected']:
        print("✅ Banco conectado com sucesso!")
        
        # Teste de cliente
        test_customer = Customer(
            phone='11999999999',
            name='João Silva Teste',
            documento='123.456.789-00',
            debt_amount=1500.00,
            days_overdue=45,
            due_date='2024-08-15',
            protocolo='12345',
            contrato='67890',
            regional='Central',
            territorio='São Paulo',
            plano='Fibra 600M',
            valor_mensalidade=99.99,
            company='DESKTOP_SF',
            status='active',
            priority='high',
            is_customer=True
        )
        
        # Salvar cliente
        success = save_customer_data(test_customer)
        print(f"✅ Cliente salvo: {success}")
        
        # Buscar cliente
        customer = get_customer_by_phone('11999999999')
        if customer:
            print(f"✅ Cliente encontrado: {customer.name} - R$ {customer.debt_amount}")
        else:
            print("❌ Cliente não encontrado")
        
        # Limpar teste
        delete_customer('11999999999')
        print("🗑️ Cliente de teste removido")
        
    else:
        print("❌ Banco não conectado")
        print("💡 Configure as variáveis de ambiente do Railway")
    
    print("✅ TESTE COMPLETO!")
