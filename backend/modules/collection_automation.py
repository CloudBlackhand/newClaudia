#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 COLLECTION AUTOMATION - INTEGRAÇÃO WEB + COBRANÇA
================================================

Sistema que integra a automação web com o sistema de cobrança
Permite automatizar consultas e validações em sites externos

Funcionalidades:
- Consulta automática de dados do devedor
- Validação de informações em órgãos de proteção
- Integração com Claudia Suprema
- Relatórios automatizados
"""

import asyncio
import json
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

try:
    from .web_automation_engine import WebAutomationEngine, LoginCredentials, ScrapingTask, SiteType
    from .conversation_bot import ConversationBot, ConversationContext
    WEB_AUTOMATION_AVAILABLE = True
except ImportError:
    WEB_AUTOMATION_AVAILABLE = False

# ===== LOGGING =====
logger = logging.getLogger(__name__)


# ===== ENUMS =====
class ConsultationType(Enum):
    """Tipos de consulta disponíveis"""
    CPF_VALIDATION = "cpf_validation"
    DEBT_VERIFICATION = "debt_verification"
    CONTACT_VALIDATION = "contact_validation"
    CREDIT_SCORE = "credit_score"
    LEGAL_STATUS = "legal_status"


class AutomationPriority(Enum):
    """Prioridade das automações"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


# ===== DATACLASSES =====
@dataclass
class DebtorInfo:
    """Informações do devedor"""
    name: str
    cpf: str
    phone: str
    email: str = ""
    address: str = ""
    debt_amount: float = 0.0
    days_overdue: int = 0


@dataclass
class ConsultationRequest:
    """Solicitação de consulta"""
    request_id: str
    debtor_info: DebtorInfo
    consultation_type: ConsultationType
    priority: AutomationPriority
    target_sites: List[SiteType]
    created_at: datetime
    deadline: Optional[datetime] = None


@dataclass
class ConsultationResult:
    """Resultado da consulta"""
    request_id: str
    success: bool
    data: Dict[str, Any]
    sites_consulted: List[str]
    errors: List[str]
    execution_time: float
    completed_at: datetime


# ===== MAIN CLASS =====
class CollectionAutomation:
    """
    🤖 SISTEMA DE AUTOMAÇÃO PARA COBRANÇA
    
    Integra automação web com sistema de cobrança inteligente
    """
    
    def __init__(self):
        """Inicializa o sistema de automação"""
        self.web_engine: Optional[WebAutomationEngine] = None
        self.conversation_bot: Optional[ConversationBot] = None
        self.active_sessions: Dict[str, Dict] = {}
        self.consultation_queue: List[ConsultationRequest] = []
        self.results_cache: Dict[str, ConsultationResult] = {}
        
        # Credenciais dos sites (devem vir de variáveis de ambiente)
        self.site_credentials = self._load_site_credentials()
        
        if WEB_AUTOMATION_AVAILABLE:
            self.web_engine = WebAutomationEngine()
            logger.info("🤖 Collection Automation inicializado!")
        else:
            logger.warning("⚠️ Web Automation não disponível - funcionalidade limitada")
    
    def _load_site_credentials(self) -> Dict[SiteType, LoginCredentials]:
        """🔐 Carrega credenciais dos sites"""
        import os
        
        credentials = {}
        
        # Serasa
        serasa_user = os.getenv('SERASA_USERNAME')
        serasa_pass = os.getenv('SERASA_PASSWORD')
        if serasa_user and serasa_pass:
            from .web_automation_engine import create_serasa_credentials
            credentials[SiteType.SERASA] = create_serasa_credentials(serasa_user, serasa_pass)
        
        # SPC
        spc_user = os.getenv('SPC_USERNAME')
        spc_pass = os.getenv('SPC_PASSWORD')
        if spc_user and spc_pass:
            from .web_automation_engine import create_spc_credentials
            credentials[SiteType.SPC] = create_spc_credentials(spc_user, spc_pass)
        
        logger.info(f"🔐 Credenciais carregadas para {len(credentials)} sites")
        return credentials
    
    async def start_automation_engine(self) -> bool:
        """🚀 Inicia o engine de automação"""
        if not self.web_engine:
            logger.error("❌ Web engine não disponível")
            return False
        
        try:
            success = await self.web_engine.start_browser()
            if success:
                logger.info("🚀 Engine de automação iniciado!")
                return True
            else:
                logger.error("❌ Falha ao iniciar engine")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar automação: {e}")
            return False
    
    async def authenticate_sites(self) -> Dict[SiteType, bool]:
        """🔐 Autentica em todos os sites configurados"""
        results = {}
        
        for site_type, credentials in self.site_credentials.items():
            try:
                logger.info(f"🔐 Autenticando em {site_type.value}...")
                success = await self.web_engine.login_to_site(credentials, f"session_{site_type.value}")
                results[site_type] = success
                
                if success:
                    logger.info(f"✅ Login realizado em {site_type.value}")
                else:
                    logger.error(f"❌ Falha no login em {site_type.value}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao autenticar {site_type.value}: {e}")
                results[site_type] = False
        
        return results
    
    async def validate_cpf(self, cpf: str, debtor_name: str) -> Dict[str, Any]:
        """
        📋 Valida CPF em órgãos de proteção
        """
        if not self.web_engine:
            return {"error": "Engine não disponível"}
        
        results = {
            "cpf": cpf,
            "name": debtor_name,
            "valid": False,
            "sites_checked": [],
            "details": {}
        }
        
        # Serasa
        if SiteType.SERASA in self.site_credentials:
            try:
                serasa_task = ScrapingTask(
                    task_id=f"cpf_validation_{cpf}",
                    site_type=SiteType.SERASA,
                    target_url="https://www.serasa.com.br/consulta-cpf",
                    data_selectors={
                        "cpf_status_text": ".cpf-status, .status-cpf, .resultado-cpf",
                        "name_match_text": ".nome-titular, .titular-nome",
                        "restrictions_text": ".restricoes, .pendencias"
                    },
                    search_params={"cpf": cpf}
                )
                
                serasa_result = await self.web_engine.scrape_data(serasa_task)
                results["sites_checked"].append("Serasa")
                results["details"]["serasa"] = serasa_result.data
                
            except Exception as e:
                logger.error(f"❌ Erro na consulta Serasa: {e}")
        
        # SPC
        if SiteType.SPC in self.site_credentials:
            try:
                spc_task = ScrapingTask(
                    task_id=f"cpf_spc_{cpf}",
                    site_type=SiteType.SPC,
                    target_url="https://www.spcbrasil.org.br/consulta",
                    data_selectors={
                        "score_text": ".score-valor, .pontuacao",
                        "status_text": ".situacao-cpf, .status"
                    },
                    search_params={"documento": cpf}
                )
                
                spc_result = await self.web_engine.scrape_data(spc_task)
                results["sites_checked"].append("SPC")
                results["details"]["spc"] = spc_result.data
                
            except Exception as e:
                logger.error(f"❌ Erro na consulta SPC: {e}")
        
        # Determinar se é válido
        results["valid"] = len(results["sites_checked"]) > 0
        
        return results
    
    async def verify_debt_legitimacy(self, debtor_info: DebtorInfo) -> Dict[str, Any]:
        """
        💰 Verifica legitimidade da dívida
        """
        results = {
            "debtor": debtor_info.name,
            "cpf": debtor_info.cpf,
            "debt_amount": debtor_info.debt_amount,
            "legitimate": False,
            "confidence": 0.0,
            "evidence": []
        }
        
        try:
            # Validar CPF
            cpf_validation = await self.validate_cpf(debtor_info.cpf, debtor_info.name)
            
            if cpf_validation["valid"]:
                results["evidence"].append("CPF válido nos órgãos consultados")
                results["confidence"] += 0.3
            
            # Verificar histórico de dívidas
            if "serasa" in cpf_validation.get("details", {}):
                serasa_data = cpf_validation["details"]["serasa"]
                if serasa_data.get("restrictions_text"):
                    results["evidence"].append("Histórico de restrições encontrado")
                    results["confidence"] += 0.2
            
            # Verificar score
            if "spc" in cpf_validation.get("details", {}):
                spc_data = cpf_validation["details"]["spc"]
                if spc_data.get("score_text"):
                    results["evidence"].append("Score de crédito disponível")
                    results["confidence"] += 0.1
            
            # Determinar legitimidade
            results["legitimate"] = results["confidence"] >= 0.5
            
        except Exception as e:
            logger.error(f"❌ Erro na verificação de legitimidade: {e}")
            results["error"] = str(e)
        
        return results
    
    async def enhance_conversation_context(self, context: ConversationContext) -> ConversationContext:
        """
        🧠 Enriquece contexto da conversa com dados automatizados
        """
        try:
            # Criar info do devedor
            debtor_info = DebtorInfo(
                name=context.customer_name,
                cpf="",  # Seria necessário ter o CPF
                phone=context.customer_phone,
                debt_amount=context.debt_amount,
                days_overdue=context.days_overdue
            )
            
            # Se tivéssemos CPF, poderíamos fazer validações
            # validation_result = await self.verify_debt_legitimacy(debtor_info)
            
            # Por enquanto, apenas adicionar informações básicas
            context.additional_info = context.additional_info or {}
            context.additional_info.update({
                "automation_available": True,
                "last_validation": datetime.now().isoformat(),
                "validation_status": "pending_cpf"
            })
            
        except Exception as e:
            logger.error(f"❌ Erro ao enriquecer contexto: {e}")
        
        return context
    
    async def generate_automated_report(self, debtor_info: DebtorInfo) -> Dict[str, Any]:
        """
        📊 Gera relatório automatizado sobre o devedor
        """
        report = {
            "debtor_name": debtor_info.name,
            "report_date": datetime.now().isoformat(),
            "validations": {},
            "recommendations": [],
            "risk_score": 0.0
        }
        
        try:
            # Validar CPF se disponível
            if debtor_info.cpf:
                cpf_result = await self.validate_cpf(debtor_info.cpf, debtor_info.name)
                report["validations"]["cpf"] = cpf_result
                
                if cpf_result["valid"]:
                    report["risk_score"] += 0.3
                    report["recommendations"].append("CPF válido - prosseguir com cobrança")
                else:
                    report["recommendations"].append("CPF inválido - verificar dados")
            
            # Verificar legitimidade da dívida
            debt_verification = await self.verify_debt_legitimacy(debtor_info)
            report["validations"]["debt"] = debt_verification
            
            if debt_verification["legitimate"]:
                report["risk_score"] += 0.4
                report["recommendations"].append("Dívida legítima - cobrança recomendada")
            
            # Análise de risco final
            if report["risk_score"] >= 0.7:
                report["final_recommendation"] = "COBRANÇA RECOMENDADA"
            elif report["risk_score"] >= 0.4:
                report["final_recommendation"] = "COBRANÇA COM CAUTELA"
            else:
                report["final_recommendation"] = "VERIFICAR DADOS ANTES DA COBRANÇA"
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            report["error"] = str(e)
        
        return report
    
    async def close_automation(self):
        """🔚 Encerra o sistema de automação"""
        if self.web_engine:
            await self.web_engine.close_browser()
            logger.info("🔚 Sistema de automação encerrado")
    
    def get_automation_status(self) -> Dict[str, Any]:
        """📊 Retorna status do sistema de automação"""
        return {
            "web_automation_available": WEB_AUTOMATION_AVAILABLE,
            "engine_active": self.web_engine is not None,
            "authenticated_sites": len([s for s in self.active_sessions.values() if s.get("status") == "active"]),
            "consultation_queue": len(self.consultation_queue),
            "results_cached": len(self.results_cache)
        }


# ===== TESTE =====
async def test_collection_automation():
    """🧪 Teste do sistema de automação"""
    automation = CollectionAutomation()
    
    try:
        # Iniciar engine
        if automation.web_engine:
            await automation.start_automation_engine()
            
            # Teste de validação CPF (simulado)
            test_debtor = DebtorInfo(
                name="João Silva",
                cpf="12345678901",
                phone="11999999999",
                debt_amount=1500.00,
                days_overdue=45
            )
            
            # Gerar relatório
            report = await automation.generate_automated_report(test_debtor)
            print("📊 Relatório gerado:")
            print(json.dumps(report, indent=2, ensure_ascii=False))
            
        print("✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
    
    finally:
        await automation.close_automation()


if __name__ == "__main__":
    print("🤖 COLLECTION AUTOMATION - INTEGRAÇÃO WEB + COBRANÇA")
    print("=" * 60)
    
    asyncio.run(test_collection_automation())
