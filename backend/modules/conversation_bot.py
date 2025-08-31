#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Conversação Inteligente
Sistema próprio de IA para interação com clientes
"""

import re
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import unicodedata
import math

from backend.modules.logger_system import LogManager, LogCategory

logger = LogManager.get_logger('conversation_bot')

class IntentType(Enum):
    """Tipos de intenção do usuário"""
    GREETING = "greeting"
    PAYMENT_CONFIRMATION = "payment_confirmation"
    PAYMENT_QUESTION = "payment_question"
    NEGOTIATION = "negotiation"
    COMPLAINT = "complaint"
    INFORMATION_REQUEST = "information_request"
    GOODBYE = "goodbye"
    URGENCY = "urgency"
    DISCOUNT_REQUEST = "discount_request"
    INTEREST_QUESTION = "interest_question"
    FINANCIAL_DIFFICULTY = "financial_difficulty"
    PAYMENT_PROOF = "payment_proof"
    INSTALLMENT_REQUEST = "installment_request"
    DEADLINE_EXTENSION = "deadline_extension"
    CONTACT_REQUEST = "contact_request"
    
    # Queixas específicas de serviço
    NETWORK_COMPLAINT = "network_complaint"
    SERVICE_CANCELLATION = "service_cancellation"
    INVALID_CHARGE = "invalid_charge"
    TECHNICAL_PROBLEM = "technical_problem"
    BILLING_ERROR = "billing_error"
    DATA_CHANGE_REQUEST = "data_change_request"
    SERVICE_NOT_USED = "service_not_used"
    DUPLICATE_CHARGE = "duplicate_charge"
    WRONG_PLAN = "wrong_plan"
    POOR_SIGNAL = "poor_signal"
    EQUIPMENT_PROBLEM = "equipment_problem"
    CUSTOMER_NOT_REGISTERED = "customer_not_registered"
    MOVED_ADDRESS = "moved_address"
    WRONG_PERSON = "wrong_person"
    FRAUD_CLAIM = "fraud_claim"
    
    UNKNOWN = "unknown"

class SentimentType(Enum):
    """Tipos de sentimento da mensagem"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    RELIEVED = "relieved"
    CONFUSED = "confused"
    URGENT = "urgent"

class ResponseType(Enum):
    """Tipos de resposta do bot"""
    INFORMATIVE = "informative"
    EMPATHETIC = "empathetic"
    DIRECTIVE = "directive"
    CONFIRMATION = "confirmation"
    ESCALATION = "escalation"

@dataclass
class ConversationContext:
    """Contexto da conversa"""
    user_phone: str
    session_id: str
    started_at: str
    last_activity: str
    message_count: int
    user_name: Optional[str] = None
    payment_amount: Optional[float] = None
    due_date: Optional[str] = None
    topics_discussed: Set[str] = None
    sentiment_history: List[SentimentType] = None
    intent_history: List[IntentType] = None
    
    # Novos campos para análise avançada
    frustration_level: int = 0  # 0-10 escala de frustração
    urgency_level: int = 0      # 0-10 escala de urgência
    payment_capacity: Optional[str] = None  # 'high', 'medium', 'low', 'none'
    preferred_solution: Optional[str] = None  # Solução preferida do cliente
    escalation_reasons: List[str] = None     # Motivos para escalação
    conversation_tone: str = 'neutral'       # Tom geral da conversa
    last_sentiment_change: Optional[str] = None  # Última mudança de sentimento
    
    def __post_init__(self):
        if self.topics_discussed is None:
            self.topics_discussed = set()
        if self.sentiment_history is None:
            self.sentiment_history = []
        if self.intent_history is None:
            self.intent_history = []
        if self.escalation_reasons is None:
            self.escalation_reasons = []

@dataclass
class AnalysisResult:
    """Resultado da análise de mensagem SUPREMA"""
    intent: IntentType
    sentiment: SentimentType
    confidence: float
    entities: Dict[str, Any]
    keywords: List[str]
    
    # Campos avançados de compreensão
    multiple_intents: List[Dict[str, Any]] = None
    contradictions: List[Dict[str, str]] = None
    ambiguities: List[str] = None
    subtext: Dict[str, List[str]] = None
    personality: Dict[str, float] = None
    urgency_score: float = 0.0
    regional_context: str = 'generic'
    semantic_expansion: Dict[str, List[str]] = None
    emotional_intensity: float = 0.0
    communication_style: str = 'neutral'
    
    # 🔥 ANÁLISES ULTRA AVANÇADAS
    implicit_meanings: Dict[str, List[str]] = None      # O que não foi dito mas está implícito
    emotional_progression: List[str] = None             # Evolução emocional na conversa
    behavioral_predictions: Dict[str, float] = None     # Predições de comportamento
    deception_indicators: List[str] = None              # Indicadores de mentira/omissão
    commitment_level: float = 0.0                       # Nível de comprometimento com pagamento
    financial_stress_score: float = 0.0                # Score de estresse financeiro
    empathy_triggers: List[str] = None                  # Gatilhos de empatia detectados
    conversation_momentum: str = 'neutral'              # Momentum da conversa
    hidden_objections: List[str] = None                 # Objeções não verbalizadas
    social_proof_needs: List[str] = None               # Necessidades de prova social
    decision_readiness: float = 0.0                    # Prontidão para tomar decisão
    relationship_quality: str = 'neutral'              # Qualidade do relacionamento
    
    # 🌟 ANÁLISES INCLUSIVAS
    education_level: str = 'unknown'                   # Nível educacional detectado
    original_message: str = ''                         # Mensagem original antes das correções
    corrected_message: str = ''                        # Mensagem após correções
    spelling_errors: List[Dict[str, str]] = None       # Erros de grafia detectados
    phonetic_corrections: List[Dict[str, str]] = None  # Correções fonéticas aplicadas
    colloquial_translations: List[Dict[str, str]] = None # Traduções de gírias
    informal_grammar_score: float = 0.0               # Score de informalidade (0-1)
    communication_barriers: List[str] = None          # Barreiras de comunicação detectadas
    
    def __post_init__(self):
        if self.multiple_intents is None:
            self.multiple_intents = []
        if self.contradictions is None:
            self.contradictions = []
        if self.ambiguities is None:
            self.ambiguities = []
        if self.subtext is None:
            self.subtext = {}
        if self.personality is None:
            self.personality = {}
        if self.semantic_expansion is None:
            self.semantic_expansion = {}
        
        # Inicializar novos campos ultra avançados
        if self.implicit_meanings is None:
            self.implicit_meanings = {}
        if self.emotional_progression is None:
            self.emotional_progression = []
        if self.behavioral_predictions is None:
            self.behavioral_predictions = {}
        if self.deception_indicators is None:
            self.deception_indicators = []
        if self.empathy_triggers is None:
            self.empathy_triggers = []
        if self.hidden_objections is None:
            self.hidden_objections = []
        if self.social_proof_needs is None:
            self.social_proof_needs = []
        
        # Inicializar campos inclusivos
        if self.spelling_errors is None:
            self.spelling_errors = []
        if self.phonetic_corrections is None:
            self.phonetic_corrections = []
        if self.colloquial_translations is None:
            self.colloquial_translations = []
        if self.communication_barriers is None:
            self.communication_barriers = []

@dataclass
class BotResponse:
    """Resposta do bot"""
    text: str
    response_type: ResponseType
    confidence: float
    should_escalate: bool = False
    suggested_actions: List[str] = None
    
    def __post_init__(self):
        if self.suggested_actions is None:
            self.suggested_actions = []

class NLPProcessor:
    """Processador de linguagem natural avançado"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.sentiment_words = self._load_sentiment_words()
        self.entity_patterns = self._load_entity_patterns()
        
        # Sistemas avançados de compreensão
        self.synonym_map = self._load_synonym_map()
        self.regional_patterns = self._load_regional_patterns()
        self.contradiction_detectors = self._load_contradiction_patterns()
        self.ambiguity_resolvers = self._load_ambiguity_patterns()
        self.subtext_analyzers = self._load_subtext_patterns()
        self.personality_indicators = self._load_personality_patterns()
        self.urgency_multipliers = self._load_urgency_multipliers()
        self.multi_intent_separators = self._load_multi_intent_patterns()
        
        # 🔥 SISTEMAS ULTRA AVANÇADOS DE COMPREENSÃO
        self.context_builders = self._load_context_builders()
        self.implicit_meaning_detectors = self._load_implicit_meaning_patterns()
        self.emotional_state_analyzers = self._load_emotional_state_patterns()
        self.conversation_flow_predictors = self._load_conversation_flow_patterns()
        self.micro_expression_detectors = self._load_micro_expression_patterns()
        self.behavioral_predictors = self._load_behavioral_patterns()
        self.escalation_preventers = self._load_escalation_prevention_patterns()
        self.empathy_triggers = self._load_empathy_trigger_patterns()
        self.lie_detectors = self._load_deception_patterns()
        self.commitment_analyzers = self._load_commitment_patterns()
        self.financial_stress_indicators = self._load_financial_stress_patterns()
        self.time_sensitivity_calculators = self._load_time_sensitivity_patterns()
        
        # 🌟 SISTEMAS ULTRA INCLUSIVOS
        self.phonetic_corrections = self._load_phonetic_corrections()
        self.spelling_corrections = self._load_spelling_corrections()
        self.colloquial_translations = self._load_colloquial_translations()
        self.education_level_detectors = self._load_education_patterns()
        self.informal_grammar_patterns = self._load_informal_grammar()
        self.abbreviation_expanders = self._load_abbreviation_expanders()
        self.emotion_sounds = self._load_emotion_sounds()
        self.repetition_patterns = self._load_repetition_patterns()
        
        logger.info(LogCategory.CONVERSATION, "NLP Processor ULTRA SUPREMO++ inicializado com 28+ sistemas inclusivos")
    
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Carregar padrões de intenção"""
        return {
            IntentType.GREETING: [
                r'\b(oi|olá|bom dia|boa tarde|boa noite|e aí|salve)\b',
                r'\b(tudo bem|como vai|beleza)\b',
                r'^(oi|olá|bom\s+dia|boa\s+tarde|boa\s+noite)',
                r'\b(eae|opa|fala|hey|hello)\b',
            ],
            IntentType.PAYMENT_CONFIRMATION: [
                r'\b(já paguei|paguei|efetuei o pagamento|quitei|pix feito)\b',
                r'\b(comprovante|recibo|transferência realizada)\b',
                r'\b(pagamento efetuado|conta quitada|valor pago)\b',
                r'\b(enviei o pix|mandei o dinheiro|transferi)\b',
                r'\b(depositei|depositado|ted feito|doc feito)\b',
                r'\b(boleto pago|cartão processado|débito autorizado)\b',
            ],
            IntentType.PAYMENT_QUESTION: [
                r'\b(como pagar|onde pagar|forma de pagamento|chave pix)\b',
                r'\b(dados bancários|conta para depósito|qr code)\b',
                r'\b(valor|quanto|qual o valor|valor correto)\b',
                r'\b(vencimento|quando vence|prazo)\b',
                r'\b(aceita cartão|aceita pix|como depositar)\b',
                r'\b(banco|agência|conta corrente|dados da conta)\b',
            ],
            IntentType.NEGOTIATION: [
                r'\b(negociar|parcelar|dividir|desconto|abatimento)\b',
                r'\b(condições|facilitar|reduzir|diminuir)\b',
                r'\b(não consigo pagar|difícil situação|sem condições)\b',
                r'\b(proposta|acordo|acerto|combinar)\b',
                r'\b(renegociar|refinanciar|rever condições)\b',
            ],
            IntentType.COMPLAINT: [
                r'\b(reclamação|problema|erro|não concordo|injusto)\b',
                r'\b(absurdo|revoltante|inadmissível|inaceitável)\b',
                r'\b(não devo|não é meu|cobrança indevida)\b',
                r'\b(advogado|procon|justiça|processo)\b',
                r'\b(irregularidade|fraude|golpe|enganação)\b',
            ],
            IntentType.URGENCY: [
                r'\b(urgente|emergência|preciso urgente|é urgente)\b',
                r'\b(hoje mesmo|agora|imediatamente|já)\b',
                r'\b(problema sério|situação crítica|emergencial)\b',
                r'\b(prazo acabando|último dia|vence hoje)\b',
            ],
            IntentType.DISCOUNT_REQUEST: [
                r'\b(desconto|redução|abatimento|diminuir valor)\b',
                r'\b(preço menor|valor menor|pode baixar)\b',
                r'\b(promoção|oferta|condição especial)\b',
                r'\b(tem desconto|fazem desconto|dão desconto)\b',
            ],
            IntentType.INTEREST_QUESTION: [
                r'\b(juros|multa|correção|atualização monetária)\b',
                r'\b(taxa|porcentagem|percentual|acréscimo)\b',
                r'\b(valor original|valor inicial|sem juros)\b',
                r'\b(incidência|cobrança de juros|juros sobre)\b',
            ],
            IntentType.FINANCIAL_DIFFICULTY: [
                r'\b(desempregado|sem trabalho|sem renda|aposentado)\b',
                r'\b(dificuldade financeira|crise|sem dinheiro)\b',
                r'\b(não tenho como|impossível|fora das condições)\b',
                r'\b(situação difícil|momento difícil|período ruim)\b',
                r'\b(auxílio|benefício|pensão|bolsa família)\b',
            ],
            IntentType.PAYMENT_PROOF: [
                r'\b(comprovante|recibo|extrato|print)\b',
                r'\b(foto do pagamento|imagem|screenshot)\b',
                r'\b(documento|evidência|prova de pagamento)\b',
                r'\b(confirmação|validação|verificação)\b',
            ],
            IntentType.INSTALLMENT_REQUEST: [
                r'\b(parcelar|parcelas|dividir|fatiar)\b',
                r'\b(em vez|vezes|prestações|mensalidades)\b',
                r'\b(pagar em partes|pagar aos poucos)\b',
                r'\b(entrada|sinal|primeira parcela)\b',
            ],
            IntentType.DEADLINE_EXTENSION: [
                r'\b(prorrogar|estender|adiar|postergar)\b',
                r'\b(mais tempo|prazo maior|prazo adicional)\b',
                r'\b(próxima semana|mês que vem|depois)\b',
                r'\b(aguardar|esperar|dar um tempo)\b',
            ],
            IntentType.CONTACT_REQUEST: [
                r'\b(falar com|conversar com|contato com)\b',
                r'\b(supervisor|gerente|responsável|chefe)\b',
                r'\b(humano|pessoa|gente|atendente)\b',
                r'\b(telefone|whatsapp|email|endereço)\b',
            ],
            IntentType.INFORMATION_REQUEST: [
                r'\b(informação|detalhe|esclarecimento|dúvida)\b',
                r'\b(referente a|sobre|relativo|concernente)\b',
                r'\b(o que é|do que se trata|qual o motivo)\b',
                r'\b(histórico|extrato|demonstrativo)\b',
                r'\b(origem|procedência|de onde vem)\b',
            ],
            IntentType.GOODBYE: [
                r'\b(tchau|até|obrigad|valeu|flw|falou)\b',
                r'\b(até logo|até mais|nos falamos)\b',
                r'^(ok|certo|entendi|beleza)$',
                r'\b(xau|bye|adeus|fui)\b',
            ],
            
            # QUEIXAS ESPECÍFICAS DE SERVIÇO
            IntentType.NETWORK_COMPLAINT: [
                r'\b(não tenho rede|sem rede|rede caiu|internet não funciona)\b',
                r'\b(sem sinal|signal ruim|conexão ruim|não conecta)\b',
                r'\b(wi-fi não funciona|wifi ruim|internet lenta|net caiu)\b',
                r'\b(fibra não funciona|cabo cortado|modem com problema)\b',
                r'\b(não consigo navegar|não abre site|sem acesso)\b'
            ],
            IntentType.SERVICE_CANCELLATION: [
                r'\b(cancelei o serviço|cancelei a assinatura|não uso mais)\b',
                r'\b(pedi cancelamento|solicitei cancelamento|não quero mais)\b',
                r'\b(rescindi contrato|encerrei|dei baixa no serviço)\b',
                r'\b(não sou mais cliente|ex-cliente|já cancelei)\b',
                r'\b(não tenho mais o serviço|não uso há meses)\b'
            ],
            IntentType.INVALID_CHARGE: [
                r'\b(cobrança indevida|não devo|cobrança errada)\b',
                r'\b(nunca contratei|não assinei|não autorizei)\b',
                r'\b(cobrança irregular|não reconheço|não é meu)\b',
                r'\b(jamais contratei|nunca usei|não solicitei)\b',
                r'\b(golpe|fraude|me cobrando indevidamente)\b'
            ],
            IntentType.TECHNICAL_PROBLEM: [
                r'\b(problema técnico|defeito|não funciona direito)\b',
                r'\b(instabilidade|oscilação|cai direto|intermitente)\b',
                r'\b(lentidão|travando|congelando|com bug)\b',
                r'\b(erro no sistema|falha técnica|mal funcionamento)\b',
                r'\b(precisa de manutenção|reparo|conserto)\b'
            ],
            IntentType.BILLING_ERROR: [
                r'\b(erro na fatura|cobrança duplicada|valor errado)\b',
                r'\b(fatura incorreta|conta com erro|valor a mais)\b',
                r'\b(cobraram dobrado|valor diferente|preço errado)\b',
                r'\b(desconto não aplicado|promoção não aplicada)\b',
                r'\b(plano errado na fatura|valor não confere)\b'
            ],
            IntentType.DATA_CHANGE_REQUEST: [
                r'\b(mudei de endereço|novo endereço|endereço diferente)\b',
                r'\b(mudança de dados|atualizar dados|dados incorretos)\b',
                r'\b(telefone novo|celular novo|email novo)\b',
                r'\b(transferir titularidade|mudar titular|novo responsável)\b',
                r'\b(dados desatualizados|informações antigas)\b'
            ],
            IntentType.SERVICE_NOT_USED: [
                r'\b(nunca usei|não uso|não utilizo)\b',
                r'\b(não instalaram|não ativaram|não liberaram)\b',
                r'\b(está desligado|não ativo|inativo)\b',
                r'\b(não tem instalação|sem instalação|pendente)\b',
                r'\b(não chegou técnico|não visitaram|aguardando)\b'
            ],
            IntentType.DUPLICATE_CHARGE: [
                r'\b(cobrança duplicada|cobraram duas vezes|em dobro)\b',
                r'\b(fatura repetida|conta dupla|pagamento duplo)\b',
                r'\b(mesmo valor duas vezes|cobraram novamente)\b',
                r'\b(já paguei mas cobraram de novo|re-cobrança)\b',
                r'\b(apareceu duas vezes|duplicidade)\b'
            ],
            IntentType.WRONG_PLAN: [
                r'\b(plano errado|não é meu plano|plano diferente)\b',
                r'\b(não contratei esse plano|outro plano|mudaram meu plano)\b',
                r'\b(velocidade errada|megas errados|gb errado)\b',
                r'\b(não autorizei mudança|alteraram sem avisar)\b',
                r'\b(plano mais caro|upgrade não autorizado)\b'
            ],
            IntentType.POOR_SIGNAL: [
                r'\b(sinal fraco|signal ruim|baixo sinal)\b',
                r'\b(não pega bem|oscila muito|instável)\b',
                r'\b(área sem cobertura|local sem sinal)\b',
                r'\b(antena com problema|torre com defeito)\b',
                r'\b(qualidade ruim|conexão instável)\b'
            ],
            IntentType.EQUIPMENT_PROBLEM: [
                r'\b(modem com problema|roteador defeituoso|aparelho ruim)\b',
                r'\b(equipamento queimou|cabo com defeito|fonte queimada)\b',
                r'\b(wi-fi router com problema|antena quebrada)\b',
                r'\b(preciso trocar equipamento|aparelho velho)\b',
                r'\b(instalação mal feita|fiação com problema)\b'
            ],
            IntentType.CUSTOMER_NOT_REGISTERED: [
                r'\b(não sou cliente|nunca fui cliente|não tenho cadastro)\b',
                r'\b(não consta no sistema|não estou registrado)\b',
                r'\b(engano de pessoa|pessoa errada|não é comigo)\b',
                r'\b(nunca me cadastrei|não fiz inscrição)\b',
                r'\b(deve ser outro cliente|confundiram)\b'
            ],
            IntentType.MOVED_ADDRESS: [
                r'\b(me mudei|mudança|novo endereço|endereço diferente)\b',
                r'\b(não moro mais|mudei de casa|nova residência)\b',
                r'\b(outro local|local diferente|endereço antigo)\b',
                r'\b(transferir endereço|mudar localização)\b',
                r'\b(saí de lá|não fico mais lá)\b'
            ],
            IntentType.WRONG_PERSON: [
                r'\b(não é comigo|pessoa errada|nome errado)\b',
                r'\b(confundiram|engano|mix-up|trocaram)\b',
                r'\b(outro fulano|não sou eu|homônimo)\b',
                r'\b(mesmo nome diferente pessoa|xará)\b',
                r'\b(número errado|telefone de outra pessoa)\b'
            ],
            IntentType.FRAUD_CLAIM: [
                r'\b(fraude|golpe|clonaram|falsificação)\b',
                r'\b(usaram meus dados|identidade roubada)\b',
                r'\b(alguém se passou por mim|terceiros)\b',
                r'\b(não autorizei|sem meu conhecimento)\b',
                r'\b(crime|estelionato|falsidade ideológica)\b'
            ]
        }
    
    def _load_sentiment_words(self) -> Dict[SentimentType, List[str]]:
        """Carregar palavras de sentimento"""
        return {
            SentimentType.POSITIVE: [
                'obrigado', 'grato', 'excelente', 'ótimo', 'bom', 'legal', 'show',
                'perfeito', 'maravilhoso', 'agradável', 'satisfeito', 'feliz',
                'positivo', 'correto', 'certo', 'bem', 'melhor', 'sucesso',
                'adorei', 'amei', 'fantástico', 'incrível', 'top', 'massa',
                'bacana', 'sensacional', 'espetacular', 'aprovado', 'concordo'
            ],
            SentimentType.NEGATIVE: [
                'ruim', 'péssimo', 'horrível', 'terrível', 'difícil', 'complicado',
                'problema', 'erro', 'falha', 'insatisfeito', 'chateado', 'triste',
                'preocupado', 'nervoso', 'estressado', 'desempregado', 'apertado',
                'complicada', 'deteriorado', 'prejudicado', 'desfavorável'
            ],
            SentimentType.ANGRY: [
                'raiva', 'irritado', 'furioso', 'revoltado', 'indignado', 'bravo',
                'absurdo', 'inadmissível', 'inaceitável', 'ridículo', 'vergonha',
                'escândalo', 'safado', 'ladrão', 'roubo', 'enganação', 'palhaçada',
                'revoltante', 'injusto', 'injustiça', 'exploração', 'abuso'
            ],
            SentimentType.ANXIOUS: [
                'ansioso', 'ansiosa', 'preocupado', 'preocupada', 'aflito', 'aflita',
                'desesperado', 'desesperada', 'angustiado', 'tenso', 'nervoso',
                'apreensivo', 'inquieto', 'agitado', 'estressado', 'pressão'
            ],
            SentimentType.FRUSTRATED: [
                'frustrado', 'frustrada', 'irritado', 'chateado', 'aborrecido',
                'impaciente', 'cansado', 'farto', 'saturado', 'desgostoso',
                'contrariado', 'descontente', 'incomodado', 'perturbado'
            ],
            SentimentType.RELIEVED: [
                'aliviado', 'aliviada', 'tranquilo', 'tranquila', 'calmo', 'calma',
                'relaxado', 'despreocupado', 'sereno', 'sossegado', 'descansado',
                'reconfortado', 'consolado', 'satisfeito', 'contente'
            ],
            SentimentType.CONFUSED: [
                'confuso', 'confusa', 'perdido', 'perdida', 'sem entender',
                'não compreendo', 'não entendi', 'como assim', 'que isso',
                'não sei', 'dúvida', 'incerto', 'indefinido', 'indeciso'
            ],
            SentimentType.URGENT: [
                'urgente', 'emergência', 'emergencial', 'pressa', 'rápido',
                'imediato', 'já', 'agora', 'hoje', 'inadiável', 'crítico',
                'prioritário', 'importante', 'sério', 'grave'
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, str]:
        """Carregar padrões de entidades"""
        return {
            'money': r'(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)|(\d+(?:,\d+)?\s*(?:reais?|real))',
            'money_written': r'\b(um|dois|três|quatro|cinco|seis|sete|oito|nove|dez|vinte|trinta|quarenta|cinquenta|sessenta|setenta|oitenta|noventa|cem|mil)\s*(?:reais?|real)\b',
            'date': r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'date_relative': r'\b(hoje|amanhã|ontem|semana que vem|mês que vem|próximo mês|próxima semana|final do mês)\b',
            'phone': r'(\d{2}\s*\d{4,5}\-?\d{4})',
            'pix_key': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|\d{11}|\d{14})',
            'bank_details': r'\b(banco\s+\w+|agência\s+\d+|conta\s+\d+|op\s+\d+)\b',
            'time': r'(\d{1,2}:\d{2})',
            'percentage': r'(\d+(?:,\d+)?%)',
            'installments': r'\b(\d+)\s*(?:x|vezes|parcelas?)\b',
            'documents': r'\b(cpf|rg|cnpj)\s*:?\s*(\d{3}\.?\d{3}\.?\d{3}\-?\d{2}|\d{2}\.?\d{3}\.?\d{3}\/?\d{4}\-?\d{2})\b',
            'urgency_level': r'\b(muito urgente|super urgente|emergencial|crítico|importante)\b'
        }
    
    def _load_synonym_map(self) -> Dict[str, List[str]]:
        """Mapa de sinônimos para expandir entendimento"""
        return {
            # Dinheiro/Pagamento
            'dinheiro': ['grana', 'bufunfa', 'dim', 'tutu', 'pila', 'verba', 'cash', 'money'],
            'pagar': ['quitar', 'acertar', 'liquidar', 'saldar', 'regularizar', 'resolver'],
            'valor': ['quantia', 'montante', 'soma', 'total', 'preço'],
            
            # Dificuldade/Problemas
            'difícil': ['complicado', 'tenso', 'apertado', 'pesado', 'brabo', 'osso'],
            'problema': ['perrengue', 'treta', 'briga', 'confusão', 'encrenca', 'b.o.'],
            'ruim': ['péssimo', 'horrível', 'terrível', 'tosco', 'zuado', 'merda'],
            
            # Tempo/Urgência
            'rápido': ['ligeiro', 'veloz', 'correndo', 'voando', 'já', 'agora'],
            'urgente': ['correndo', 'emergência', 'pressa', 'fire', 'crítico'],
            'devagar': ['calma', 'tranquilo', 'sem pressa', 'no tempo'],
            
            # Negociação
            'desconto': ['abatimento', 'redução', 'diminuição', 'promoção'],
            'parcelar': ['dividir', 'fatiar', 'quebrar', 'picotear'],
            'negociar': ['conversar', 'acertar', 'combinar', 'bater papo'],
            
            # Sentimentos Positivos
            'bom': ['legal', 'bacana', 'massa', 'show', 'top', 'dahora'],
            'ótimo': ['perfeito', 'excelente', 'maravilhoso', 'sensacional'],
            'obrigado': ['valeu', 'thanks', 'grato', 'agradecido'],
            
            # Sentimentos Negativos
            'irritado': ['puto', 'nervoso', 'bravo', 'pistola', 'bolado'],
            'triste': ['chateado', 'down', 'mal', 'depre', 'cabisbaixo'],
            'preocupado': ['aflito', 'ansioso', 'tenso', 'agoniado'],
            
            # Gírias Regionais
            'cara': ['mano', 'brother', 'bro', 'véi', 'parceiro', 'amigo'],
            'muito': ['demais', 'pra caramba', 'bagarai', 'pra caralho', 'absurdo'],
            'entender': ['sacar', 'captar', 'pegar', 'manjar', 'entender'],
            
            # Afirmação/Negação
            'sim': ['é', 'claro', 'com certeza', 'óbvio', 'lógico', 'pode crer'],
            'não': ['nada', 'nope', 'negativo', 'nem', 'jamais', 'nunca'],
            
            # Trabalho/Emprego
            'trabalho': ['trampo', 'job', 'emprego', 'serviço', 'labuta'],
            'desempregado': ['sem trampo', 'parado', 'encostado', 'na seca'],
            
            # Relacionamento Cliente
            'empresa': ['firma', 'companhia', 'negócio', 'estabelecimento'],
            'atendimento': ['serviço', 'suporte', 'help', 'apoio'],
            'cliente': ['consumidor', 'usuário', 'comprador', 'pessoa']
        }
    
    def _load_regional_patterns(self) -> Dict[str, List[str]]:
        """Padrões linguísticos regionais e gírias"""
        return {
            'nordeste': [
                r'\b(oxe|eita|vixe|rapaz|cabra|arretado|massa|véi)\b',
                r'\b(pra chuchu|do caramba|da peste|dos inferno)\b'
            ],
            'sudeste': [
                r'\b(mano|cara|véio|truta|parça|firmeza|suave)\b',
                r'\b(da hora|dahora|maneiro|irado|sinistro)\b'
            ],
            'sul': [
                r'\b(bah|tchê|guri|piá|barbaridade|bom demais)\b',
                r'\b(tri|muito bom|legal demais)\b'
            ],
            'norte': [
                r'\b(rapaz|mermão|doido|caboclo|massa)\b',
                r'\b(da hora|top demais|muito bom)\b'
            ],
            'internet': [
                r'\b(kk|rs|lol|wtf|omg|plz|tbm|vc|pq|qnd)\b',
                r'\b(naum|eh|pra|aki|la|to|ta|tava)\b'
            ]
        }
    
    def _load_contradiction_patterns(self) -> List[Dict[str, str]]:
        """Detectores de contradições na fala"""
        return [
            {
                'pattern1': r'\b(não tenho dinheiro|sem grana|sem condições)\b',
                'pattern2': r'\b(posso pagar|vou pagar|tenho como)\b',
                'type': 'financial_contradiction'
            },
            {
                'pattern1': r'\b(não é meu|não devo|não reconheço)\b',
                'pattern2': r'\b(vou pagar|como pagar|quando pagar)\b',
                'type': 'debt_contradiction'
            },
            {
                'pattern1': r'\b(não tenho pressa|sem urgência|tranquilo)\b',
                'pattern2': r'\b(urgente|rápido|já|agora|hoje)\b',
                'type': 'urgency_contradiction'
            },
            {
                'pattern1': r'\b(não quero parcelar|à vista)\b',
                'pattern2': r'\b(posso dividir|em quantas vezes)\b',
                'type': 'payment_method_contradiction'
            }
        ]
    
    def _load_ambiguity_patterns(self) -> Dict[str, List[str]]:
        """Padrões que indicam ambiguidade ou incerteza"""
        return {
            'uncertainty': [
                r'\b(acho que|talvez|pode ser|não sei se|meio que)\b',
                r'\b(mais ou menos|tipo assim|sei lá|vai ver)\b'
            ],
            'confusion': [
                r'\b(não entendi|como assim|que isso|perdão)\b',
                r'\b(não sei|confuso|perdido|não compreendo)\b'
            ],
            'hesitation': [
                r'\b(bem|né|então|assim|ahn|hmm)\b',
                r'\b(é que|acontece que|a questão é)\b'
            ],
            'multiple_options': [
                r'\b(ou|talvez|quem sabe|pode ser)\b',
                r'\b(tanto faz|qualquer um|qualquer coisa)\b'
            ]
        }
    
    def _load_subtext_patterns(self) -> Dict[str, List[str]]:
        """Detectores de subtexto e comunicação indireta"""
        return {
            'passive_aggressive': [
                r'\b(imagino que|suponho que|creio que|deve ser)\b',
                r'\b(claro né|óbvio né|lógico né)\b'
            ],
            'hidden_anger': [
                r'\b(tudo bem|ok|certo)\b.*[.]{2,}',  # "Tudo bem..." com reticências
                r'\b(entendi|compreendi|vejo)\b.*!'   # "Entendi!" com exclamação
            ],
            'desperation': [
                r'\b(pelo amor de|por favor|imploro|preciso muito)\b',
                r'\b(não aguento mais|não sei mais|to perdido)\b'
            ],
            'testing_limits': [
                r'\b(se eu não pagar|e se eu|what if|e daí)\b',
                r'\b(o que acontece|qual a consequência)\b'
            ],
            'social_proof': [
                r'\b(todo mundo|todos|outras pessoas|outros clientes)\b',
                r'\b(meu amigo|conhecidos|vizinho|parente)\b'
            ],
            'emotional_manipulation': [
                r'\b(tenho filhos|família|doente|hospital)\b',
                r'\b(situação difícil|momento complicado|fase ruim)\b'
            ]
        }
    
    def _load_personality_patterns(self) -> Dict[str, List[str]]:
        """Indicadores de personalidade/estilo comunicativo"""
        return {
            'analytical': [
                r'\b(analisar|verificar|conferir|checar|dados)\b',
                r'\b(detalhes|especificamente|exatamente|precisamente)\b'
            ],
            'emotional': [
                r'\b(sinto|sente|emoção|coração|sentimento)\b',
                r'\b(♥|❤|💔|😢|😭|🥺)\b'
            ],
            'aggressive': [
                r'\b(exijo|demando|quero já|inaceitável)\b',
                r'[!]{2,}|[?]{2,}',  # Múltiplos ! ou ?
                r'[A-Z]{5,}'  # Texto em CAPS
            ],
            'formal': [
                r'\b(solicito|gostaria|cordialmente|atenciosamente)\b',
                r'\b(prezados|venho por meio|informo que)\b'
            ],
            'informal': [
                r'\b(oi|opa|eae|salve|fala|véi|mano)\b',
                r'\b(kk|rs|haha|kkk|rsrs)\b'
            ],
            'anxious': [
                r'\b(preocup|ansios|nervos|aflito|tenso)\b',
                r'[?]{1,}.*[!]{1,}',  # Mistura ? e !
                r'\b(será que|será|e se|como será)\b'
            ]
        }
    
    def _load_urgency_multipliers(self) -> Dict[str, float]:
        """Multiplicadores para cálculo de urgência"""
        return {
            'time_pressure': 3.0,    # "hoje", "agora", "já"
            'consequences': 2.5,     # "senão", "caso contrário"
            'external_pressure': 2.0, # "chefe mandou", "esposa cobrando"
            'repetition': 1.5,       # Repetir a mesma coisa
            'emotional_intensity': 2.2, # "desesperado", "aflito"
            'financial_impact': 1.8,  # "prejuízo", "perda"
            'health_related': 2.8,    # "hospital", "remédio"
            'legal_threats': 1.7      # "advogado", "processo"
        }
    
    def _load_multi_intent_patterns(self) -> List[str]:
        """Separadores para múltiplas intenções"""
        return [
            r'\b(mas|porém|contudo|entretanto|todavia)\b',
            r'\b(também|além disso|e mais|e também)\b',
            r'\b(ou então|ou|talvez|quem sabe)\b',
            r'\b(primeiro|segundo|terceiro|por último)\b',
            r'[.!?]\s+',  # Pontuação seguida de espaço
            r'\b(agora|depois|então|aí)\b'
        ]
    
    def _load_context_builders(self) -> Dict[str, List[str]]:
        """Construtores de contexto conversacional"""
        return {
            'financial_context': [
                r'\b(desemprego|demissão|fechou empresa|pandemia)\b',
                r'\b(aposentado|pensionista|auxílio|benefício)\b',
                r'\b(parcelou|financiou|empréstimo|cartão)\b'
            ],
            'family_context': [
                r'\b(filhos|família|esposa|marido|mãe|pai)\b',
                r'\b(casa|aluguel|condomínio|financiamento)\b',
                r'\b(escola|faculdade|hospital|remédio)\b'
            ],
            'emotional_context': [
                r'\b(estresse|pressão|ansiedade|depressão)\b',
                r'\b(desesperado|sem saída|encurralado)\b',
                r'\b(envergonhado|humilhado|constrangido)\b'
            ],
            'time_context': [
                r'\b(pressa|urgente|correndo|atrasado)\b',
                r'\b(fim do mês|salário|15|30)\b',
                r'\b(vencimento|prazo|deadline)\b'
            ]
        }
    
    def _load_implicit_meaning_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Detectores de significado implícito"""
        return {
            'financial_distress': {
                'euphemisms': [
                    r'\b(meio apertado|situação complicada|momento difícil)\b',
                    r'\b(fazendo economia|cortando gastos|sem luxo)\b',
                    r'\b(só o essencial|priorizando|reorganizando)\b'
                ],
                'hidden_meaning': ['Cliente em dificuldade financeira grave']
            },
            'relationship_deterioration': {
                'patterns': [
                    r'\b(vocês sempre|toda vez|de novo)\b',
                    r'\b(já falei|quantas vezes|repetindo)\b',
                    r'\b(não adianta|não resolve|mesma coisa)\b'
                ],
                'hidden_meaning': ['Frustração acumulada', 'Perda de confiança']
            },
            'desperation_signals': {
                'patterns': [
                    r'\b(pelo amor de|por favor|imploro)\b',
                    r'\b(qualquer coisa|aceito qualquer|seja o que for)\b',
                    r'\b(última chance|último recurso|não sei mais)\b'
                ],
                'hidden_meaning': ['Desespero extremo', 'Disposição total a negociar']
            },
            'resistance_patterns': {
                'patterns': [
                    r'\b(vou pensar|deixa eu ver|preciso consultar)\b',
                    r'\b(minha esposa|meu marido|família decide)\b',
                    r'\b(não sei se posso|vou verificar|depois vejo)\b'
                ],
                'hidden_meaning': ['Resistência educada', 'Falta de autonomia decisória']
            }
        }
    
    def _load_emotional_state_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Analisadores de estado emocional profundo"""
        return {
            'overwhelmed': {
                'patterns': [r'\b(não aguento|não suporto|sufocando)\b'],
                'intensity': 9,
                'empathy_required': True
            },
            'defensive': {
                'patterns': [r'\b(não é verdade|não foi assim|vocês que)\b'],
                'intensity': 7,
                'approach': 'gentle'
            },
            'resigned': {
                'patterns': [r'\b(tanto faz|que seja|fazer o que)\b'],
                'intensity': 6,
                'opportunity': 'motivation_boost'
            },
            'hopeful': {
                'patterns': [r'\b(quem sabe|talvez|se der certo)\b'],
                'intensity': 5,
                'approach': 'encourage'
            },
            'bargaining': {
                'patterns': [r'\b(e se|que tal|você aceita)\b'],
                'intensity': 6,
                'approach': 'negotiate'
            }
        }
    
    def _load_conversation_flow_patterns(self) -> Dict[str, List[str]]:
        """Preditores de fluxo conversacional"""
        return {
            'opening_to_close': [
                r'\b(então|resumindo|enfim)\b',
                r'\b(tá bom|ok então|beleza)\b'
            ],
            'escalation_building': [
                r'\b(cada vez mais|toda vez|sempre assim)\b',
                r'\b(cansado disso|farto|saturado)\b'
            ],
            'agreement_signals': [
                r'\b(faz sentido|concordo|entendo)\b',
                r'\b(é verdade|tem razão|é isso mesmo)\b'
            ],
            'objection_incoming': [
                r'\b(mas|porém|só que|acontece que)\b',
                r'\b(o problema é|a questão é|o negócio é)\b'
            ]
        }
    
    def _load_micro_expression_patterns(self) -> Dict[str, List[str]]:
        """Detectores de micro-expressões textuais"""
        return {
            'fake_agreement': [
                r'\b(tá bom)\.{3,}',  # "Tá bom..." com reticências
                r'\b(ok|certo)\s*\!+',  # "Ok!!!" com múltiplas exclamações
            ],
            'hidden_frustration': [
                r'\b(entendi)\.\s*$',  # "Entendi." seco
                r'\b(beleza)\s*$',     # "Beleza" sem entusiasmo
            ],
            'passive_aggression': [
                r'\b(claro né|óbvio né|lógico né)\b',
                r'\b(imagino|suponho|deve ser)\b'
            ],
            'genuine_interest': [
                r'\b(nossa|sério|interessante)\?',
                r'\b(como assim|me explica|conta mais)\b'
            ]
        }
    
    def _load_behavioral_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Preditores comportamentais"""
        return {
            'payment_likelihood': {
                'high_indicators': [
                    r'\b(quando|onde|como pagar)\b',
                    r'\b(dados bancários|pix|conta)\b'
                ],
                'low_indicators': [
                    r'\b(não posso|impossível|não dá)\b',
                    r'\b(outro dia|depois|mais tarde)\b'
                ]
            },
            'negotiation_openness': {
                'open_indicators': [
                    r'\b(conversar|negociar|acordo)\b',
                    r'\b(proposta|condições|jeito)\b'
                ],
                'closed_indicators': [
                    r'\b(não quero|não aceito|recuso)\b',
                    r'\b(final|definitivo|ponto final)\b'
                ]
            },
            'escalation_probability': {
                'high_risk': [
                    r'\b(advogado|justiça|processo)\b',
                    r'\b(procon|órgão|denunciar)\b'
                ],
                'medium_risk': [
                    r'\b(reclamação|problema sério)\b',
                    r'\b(não concordo|inadmissível)\b'
                ]
            }
        }
    
    def _load_escalation_prevention_patterns(self) -> Dict[str, List[str]]:
        """Padrões para prevenção de escalação"""
        return {
            'early_warning': [
                r'\b(começo a achar|parece que|impressão)\b',
                r'\b(toda vez|sempre|nunca)\b'
            ],
            'frustration_building': [
                r'\b(quantas vezes|de novo|outra vez)\b',
                r'\b(cansado|farto|chato)\b'
            ],
            'trust_erosion': [
                r'\b(não confio|duvidoso|suspeito)\b',
                r'\b(promessa|palavra|garantia)\b'
            ],
            'respect_issues': [
                r'\b(me tratam|vocês acham|consideram)\b',
                r'\b(desrespeito|descaso|ignoram)\b'
            ]
        }
    
    def _load_empathy_trigger_patterns(self) -> Dict[str, List[str]]:
        """Gatilhos que requerem resposta empática"""
        return {
            'health_issues': [
                r'\b(doente|hospital|cirurgia|tratamento)\b',
                r'\b(remédio|médico|saúde|dor)\b'
            ],
            'family_crisis': [
                r'\b(faleceu|morreu|funeral|velório)\b',
                r'\b(separação|divórcio|sozinho)\b'
            ],
            'job_loss': [
                r'\b(demitido|desempregado|perdeu emprego)\b',
                r'\b(empresa fechou|lay-off|corte)\b'
            ],
            'financial_ruin': [
                r'\b(falência|dívidas|despejo)\b',
                r'\b(perdeu tudo|sem nada|zerado)\b'
            ]
        }
    
    def _load_deception_patterns(self) -> Dict[str, List[str]]:
        """Detectores de possível decepção/omissão"""
        return {
            'evasion': [
                r'\b(meio que|tipo assim|sei lá)\b',
                r'\b(mais ou menos|por aí|algo assim)\b'
            ],
            'overcompensation': [
                r'\b(juro|prometo|palavra de honra)\b.*\!{2,}',
                r'\b(acredite|pode ter certeza|com toda certeza)\b'
            ],
            'deflection': [
                r'\b(mas e vocês|e a empresa|e o sistema)\b',
                r'\b(todo mundo|outros clientes|sempre assim)\b'
            ],
            'inconsistency': [
                r'\b(na verdade|aliás|quer dizer)\b',
                r'\b(esqueci de falar|não mencionei)\b'
            ]
        }
    
    def _load_commitment_patterns(self) -> Dict[str, float]:
        """Analisadores de nível de comprometimento"""
        return {
            # Frases que indicam alto comprometimento
            'vou pagar': 3.0,
            'pode contar': 3.0,
            'palavra': 2.5,
            'prometo': 2.5,
            'me comprometo': 3.0,
            'combinado': 2.0,
            
            # Frases que indicam baixo comprometimento
            'vou tentar': 0.5,
            'vou ver': 0.3,
            'talvez': 0.2,
            'quem sabe': 0.2,
            'se possível': 0.4,
            'se der': 0.3
        }
    
    def _load_financial_stress_patterns(self) -> Dict[str, float]:
        """Indicadores de estresse financeiro"""
        return {
            # Alto estresse
            'sem dinheiro': 4.0,
            'quebrado': 4.0,
            'desempregado': 3.5,
            'dívidas': 3.0,
            'apertado': 2.5,
            
            # Médio estresse
            'complicado': 2.0,
            'difícil': 2.0,
            'controlando gastos': 1.5,
            'economizando': 1.5,
            
            # Baixo estresse
            'organizando': 1.0,
            'planejando': 0.5
        }
    
    def _load_time_sensitivity_patterns(self) -> Dict[str, float]:
        """Calculadores de sensibilidade temporal"""
        return {
            # Altíssima urgência
            'hoje': 5.0,
            'agora': 5.0,
            'já': 4.5,
            'imediato': 4.5,
            
            # Alta urgência
            'amanhã': 3.5,
            'urgente': 3.0,
            'rápido': 2.5,
            
            # Média urgência
            'semana': 2.0,
            'breve': 1.5,
            
            # Baixa urgência
            'mês': 1.0,
            'futuro': 0.5
        }
    
    def _load_phonetic_corrections(self) -> Dict[str, str]:
        """Correções fonéticas para erros comuns de escrita"""
        return {
            # Pronomes e artigos
            'vuce': 'vocês',
            'vcs': 'vocês',
            'vc': 'você',
            'voce': 'você',
            'vose': 'vocês',
            'voses': 'vocês',
            
            # Verbos comuns
            'tao': 'estão',
            'ta': 'está',
            'to': 'estou',
            'faiz': 'faz',
            'fais': 'faz',
            'tem': 'têm',
            'vao': 'vão',
            'sao': 'são',
            'eh': 'é',
            'nao': 'não',
            'naum': 'não',
            'num': 'não',
            
            # Palavras comuns
            'pra': 'para',
            'pro': 'para o',
            'pq': 'porque',
            'pork': 'porque',
            'porq': 'porque',
            'tbm': 'também',
            'tbn': 'também',
            'qnd': 'quando',
            'qdo': 'quando',
            'aki': 'aqui',
            'ai': 'aí',
            'oi': 'oi',
            'oie': 'oi',
            
            # Dinheiro e números
            'dinheiru': 'dinheiro',
            'dinheru': 'dinheiro',
            'rial': 'real',
            'reau': 'real',
            'reais': 'reais',
            'centavu': 'centavo',
            
            # Expressões
            'naum sei': 'não sei',
            'naum tenhu': 'não tenho',
            'naum possu': 'não posso',
            'naum da': 'não dá',
            'naum tem': 'não tem',
            
            # Gírias regionais
            'oxe': 'nossa',
            'eita': 'nossa',
            'vixe': 'nossa',
            'rapaz': 'cara',
            'cabra': 'cara',
            'mermao': 'cara',
            'veio': 'cara',
            'vei': 'cara',
            'mano': 'cara',
            'brother': 'cara',
            'bro': 'cara',
            'parça': 'parceiro',
            'truta': 'cara',
            
            # Questões financeiras
            'quebrado': 'sem dinheiro',
            'liso': 'sem dinheiro',
            'duro': 'sem dinheiro',
            'apertiado': 'apertado',
            'apertadu': 'apertado',
            
            # Tempo
            'oje': 'hoje',
            'onti': 'ontem',
            'amanha': 'amanhã',
            'despois': 'depois',
            'antis': 'antes',
            
            # Números escritos errado
            'um': '1',
            'dois': '2',
            'tres': '3',
            'quatro': '4',
            'cinco': '5',
            'seis': '6',
            'sete': '7',
            'oito': '8',
            'nove': '9',
            'dez': '10'
        }
    
    def _load_spelling_corrections(self) -> Dict[str, str]:
        """Correções de erros de grafia comuns"""
        return {
            # Erros de acentuação
            'voce': 'você',
            'voces': 'vocês',
            'esta': 'está',
            'estao': 'estão',
            'tambem': 'também',
            'so': 'só',
            'la': 'lá',
            'ja': 'já',
            'nao': 'não',
            'ate': 'até',
            'apos': 'após',
            
            # Erros de ortografia
            'maz': 'mas',
            'mais': 'mas',  # quando usado como conjunção
            'derrepente': 'de repente',
            'denovo': 'de novo',
            'davez': 'da vez',
            'porfavor': 'por favor',
            'obrigadu': 'obrigado',
            'brigadu': 'obrigado',
            'valeu': 'valeu',
            'falou': 'falou',
            
            # Contrações informais
            'tava': 'estava',
            'tavo': 'estava',
            'tiver': 'tiver',
            'tivesse': 'tivesse',
            'fosse': 'fosse',
            'fizesse': 'fizesse',
            
            # Plurais errados
            'real': 'reais',  # quando no contexto de dinheiro
            'centavo': 'centavos',
            
            # Gênero errado
            'uma dinheiru': 'um dinheiro',
            'uma problema': 'um problema'
        }
    
    def _load_colloquial_translations(self) -> Dict[str, str]:
        """Traduções de linguagem coloquial para formal"""
        return {
            # Expressões de concordância
            'beleza': 'está bem',
            'blz': 'está bem',
            'sussa': 'está bem',
            'tranquilo': 'está bem',
            'firmeza': 'está bem',
            'de boa': 'está bem',
            'show': 'ótimo',
            'massa': 'ótimo',
            'dahora': 'ótimo',
            'legal': 'ótimo',
            'bacana': 'ótimo',
            
            # Expressões de negação
            'nada haver': 'não tem nada a ver',
            'nada ve': 'não tem nada a ver',
            'nem': 'não',
            'nem a pau': 'de jeito nenhum',
            'nem fodendo': 'de jeito nenhum',
            'nem pensar': 'de jeito nenhum',
            
            # Expressões de surpresa
            'caraca': 'nossa',
            'caralho': 'nossa',
            'porra': 'nossa',
            'nossa senhora': 'nossa',
            'meu deus': 'nossa',
            'jesus': 'nossa',
            
            # Expressões de dificuldade
            'osso': 'difícil',
            'tenso': 'difícil',
            'pesado': 'difícil',
            'punk': 'difícil',
            'foda': 'difícil',
            'complicado': 'difícil',
            'treta': 'problema',
            'rolê': 'situação',
            'parada': 'situação',
            'bagulho': 'coisa',
            'trem': 'coisa',
            'negócio': 'coisa',
            
            # Expressões sobre dinheiro
            'grana': 'dinheiro',
            'bufunfa': 'dinheiro',
            'dim': 'dinheiro',
            'tutu': 'dinheiro',
            'pila': 'dinheiro',
            'verba': 'dinheiro',
            'cash': 'dinheiro',
            'money': 'dinheiro',
            
            # Expressões de trabalho
            'trampo': 'trabalho',
            'job': 'trabalho',
            'serviço': 'trabalho',
            'labuta': 'trabalho',
            
            # Expressões temporais
            'rolando': 'acontecendo',
            'pintou': 'apareceu',
            'surgiu': 'apareceu',
            'deu ruim': 'deu problema',
            'deu merda': 'deu problema',
            'deu bosta': 'deu problema'
        }
    
    def _load_education_patterns(self) -> Dict[str, List[str]]:
        """Padrões para detectar nível educacional"""
        return {
            'baixa_escolaridade': [
                r'\b(naum|nau|num|naun)\b',  # Erros de 'não'
                r'\b(maz|mais)\b.*\b(porem|entao)\b',  # Confusão mas/mais
                r'\b(derrepenti|derrepente)\b',  # 'de repente'
                r'\b(concerteza|concertesa)\b',  # 'com certeza'
                r'\b(enves|em ves)\b',  # 'em vez'
                r'\b(aver|a ver)\b.*\b(com)\b',  # 'a ver com'
                r'\b(vuce|voces|vcs)\b',  # Erros de 'vocês'
                r'\b(faiz|fais|fas)\b',  # Erros de 'faz'
                r'\b(tem)\b.*\b(que)\b.*\b(tiver)\b'  # Confusão verbal
            ],
            'media_escolaridade': [
                r'\b(porque|pq|pork)\b',  # Abreviações
                r'\b(tambem|tbm)\b',  # Sem acentos
                r'\b(voce|vc)\b',  # Abreviações comuns
                r'\b(esta|estao)\b',  # Sem acentos
                r'\b(ja|la|so)\b'  # Monosílabos sem acento
            ],
            'alta_escolaridade': [
                r'\b(portanto|contudo|entretanto|todavia)\b',
                r'\b(solicito|gostaria|cordialmente)\b',
                r'\b(mediante|conforme|através)\b',
                r'\b(referente|concernente|pertinente)\b'
            ]
        }
    
    def _load_informal_grammar(self) -> Dict[str, List[str]]:
        """Padrões de gramática informal"""
        return {
            'double_negative': [
                r'\b(não|naum|num)\b.*\b(nada|ninguém|nunca|nem)\b'
            ],
            'verb_agreement_errors': [
                r'\b(nós vai|nós faz|nós tem)\b',
                r'\b(eles faz|eles tem|eles vai)\b'
            ],
            'pronoun_placement': [
                r'\b(me|te|se|nos|vos)\b.*\b(falou|disse|contou)\b'
            ],
            'colloquial_contractions': [
                r'\b(pro|pra|dum|duma|numa|numa)\b'
            ]
        }
    
    def _load_abbreviation_expanders(self) -> Dict[str, str]:
        """Expansões de abreviações e internetês"""
        return {
            # Internetês
            'kk': 'risos',
            'kkk': 'risos',
            'kkkk': 'muitos risos',
            'rs': 'risos',
            'rsrs': 'risos',
            'haha': 'risos',
            'hehe': 'risos',
            'lol': 'risos',
            'omg': 'meu deus',
            'wtf': 'que isso',
            'plz': 'por favor',
            'thx': 'obrigado',
            'ty': 'obrigado',
            
            # Abreviações comuns
            'bj': 'beijo',
            'bjs': 'beijos',
            'abs': 'abraços',
            'flw': 'falou',
            'vlw': 'valeu',
            'tmj': 'estamos juntos',
            'pdc': 'pode crer',
            'blz': 'beleza',
            'msg': 'mensagem',
            'tel': 'telefone',
            'cel': 'celular',
            
            # Números e tempo
            '1': 'um',
            '2': 'dois',
            '3': 'três',
            'hj': 'hoje',
            'amnh': 'amanhã',
            'ontem': 'ontem',
            'agr': 'agora',
            'dps': 'depois',
            'ant': 'antes'
        }
    
    def _load_emotion_sounds(self) -> Dict[str, str]:
        """Sons e expressões emocionais"""
        return {
            # Tristeza/Frustração
            'aff': 'expressão de frustração',
            'aff': 'descontentamento',
            'afe': 'expressão de desgosto',
            'puts': 'expressão de frustração',
            'putz': 'expressão de frustração',
            'nossa': 'expressão de surpresa',
            
            # Alegria/Aprovação
            'oba': 'expressão de alegria',
            'eba': 'expressão de alegria',
            'ihuuu': 'expressão de comemoração',
            'uhul': 'expressão de comemoração',
            
            # Dúvida/Pensamento
            'hmm': 'expressão de dúvida',
            'hum': 'expressão de reflexão',
            'ahn': 'expressão de dúvida',
            'né': 'confirmação',
            'ne': 'confirmação',
            
            # Interjeições regionais
            'oxe': 'expressão de surpresa nordestina',
            'oxente': 'expressão de surpresa nordestina',
            'eita': 'expressão de surpresa',
            'vixe': 'expressão de surpresa',
            'bah': 'expressão gaúcha',
            'tchê': 'expressão gaúcha'
        }
    
    def _load_repetition_patterns(self) -> Dict[str, str]:
        """Padrões de repetição para ênfase"""
        return {
            # Letras repetidas para ênfase
            r'(.)\1{2,}': r'\1',  # 'nãoooo' -> 'não'
            r'([aeiou])\1+': r'\1',  # 'siiiim' -> 'sim'
            r'([!?])\1+': r'\1',  # '!!!' -> '!'
            
            # Palavras repetidas
            r'\b(\w+)\s+\1\b': r'\1',  # 'não não' -> 'não'
            
            # Padrões específicos
            'kkkkkk+': 'risos',
            'hahaha+': 'risos',
            'rsrsrs+': 'risos'
        }
    
    def analyze_message(self, message: str) -> AnalysisResult:
        """Analisar mensagem do usuário com ULTRA SUPREMA++ compreensão INCLUSIVA"""
        # 🌟 ETAPA 0: Pré-processamento inclusivo
        original_message = message
        
        # Aplicar correções fonéticas e ortográficas
        corrected_message, corrections_applied = self._apply_inclusive_corrections(message)
        
        # Detectar nível educacional
        education_level = self._detect_education_level(original_message)
        
        # Analisar barreiras de comunicação
        communication_barriers = self._detect_communication_barriers(original_message)
        
        # Calcular score de informalidade
        informal_grammar_score = self._calculate_informal_grammar_score(original_message)
        
        message_clean = self._clean_text(corrected_message)
        
        # ETAPA 1: Expansão semântica (sinônimos e gírias)
        expanded_message, semantic_expansion = self._expand_semantics(message_clean)
        
        # ETAPA 2: Detecção de múltiplas intenções
        multiple_intents = self._detect_multiple_intents(expanded_message)
        primary_intent, intent_confidence = self._get_primary_intent(multiple_intents)
        
        # ETAPA 3: Análise de sentimento contextual
        sentiment = self._analyze_sentiment_advanced(expanded_message, multiple_intents)
        
        # ETAPA 4: Extração de entidades avançada
        entities = self._extract_entities_advanced(expanded_message)
        
        # ETAPA 5: Detecção de contradições
        contradictions = self._detect_contradictions(expanded_message)
        
        # ETAPA 6: Análise de ambiguidade
        ambiguities = self._detect_ambiguities(expanded_message)
        
        # ETAPA 7: Análise de subtexto
        subtext = self._analyze_subtext(expanded_message)
        
        # ETAPA 8: Análise de personalidade
        personality = self._analyze_personality(expanded_message)
        
        # ETAPA 9: Cálculo de urgência avançado
        urgency_score = self._calculate_urgency_score(expanded_message, sentiment, multiple_intents)
        
        # ETAPA 10: Detecção regional
        regional_context = self._detect_regional_context(expanded_message)
        
        # ETAPA 11: Intensidade emocional
        emotional_intensity = self._calculate_emotional_intensity(expanded_message, sentiment)
        
        # ETAPA 12: Estilo comunicativo
        communication_style = self._detect_communication_style(expanded_message)
        
        # 🔥 ETAPAS ULTRA AVANÇADAS (13-20):
        
        # ETAPA 13: Significados implícitos
        implicit_meanings = self._analyze_implicit_meanings(expanded_message)
        
        # ETAPA 14: Estado emocional profundo
        emotional_progression = self._analyze_emotional_progression(expanded_message, sentiment)
        
        # ETAPA 15: Predições comportamentais
        behavioral_predictions = self._predict_behavior(expanded_message, multiple_intents)
        
        # ETAPA 16: Detecção de decepção/omissão
        deception_indicators = self._detect_deception(expanded_message)
        
        # ETAPA 17: Nível de comprometimento
        commitment_level = self._calculate_commitment_level(expanded_message)
        
        # ETAPA 18: Score de estresse financeiro
        financial_stress_score = self._calculate_financial_stress(expanded_message)
        
        # ETAPA 19: Gatilhos de empatia
        empathy_triggers = self._identify_empathy_triggers(expanded_message)
        
        # ETAPA 20: Momentum conversacional
        conversation_momentum = self._analyze_conversation_momentum(expanded_message)
        
        # ETAPA 21: Objeções ocultas
        hidden_objections = self._detect_hidden_objections(expanded_message)
        
        # ETAPA 22: Necessidades de prova social
        social_proof_needs = self._analyze_social_proof_needs(expanded_message)
        
        # ETAPA 23: Prontidão para decisão
        decision_readiness = self._calculate_decision_readiness(expanded_message, sentiment)
        
        # ETAPA 24: Qualidade do relacionamento
        relationship_quality = self._assess_relationship_quality(expanded_message, sentiment)
        
        # Extrair palavras-chave básicas
        keywords = self._extract_keywords(message_clean)
        
        # Calcular confiança geral
        confidence = intent_confidence
        
        result = AnalysisResult(
            intent=primary_intent,
            sentiment=sentiment,
            confidence=confidence,
            entities=entities,
            keywords=keywords,
            multiple_intents=multiple_intents,
            contradictions=contradictions,
            ambiguities=ambiguities,
            subtext=subtext,
            personality=personality,
            urgency_score=urgency_score,
            regional_context=regional_context,
            semantic_expansion=semantic_expansion,
            emotional_intensity=emotional_intensity,
            communication_style=communication_style,
            
            # 🔥 Novos campos ultra avançados
            implicit_meanings=implicit_meanings,
            emotional_progression=emotional_progression,
            behavioral_predictions=behavioral_predictions,
            deception_indicators=deception_indicators,
            commitment_level=commitment_level,
            financial_stress_score=financial_stress_score,
            empathy_triggers=empathy_triggers,
            conversation_momentum=conversation_momentum,
            hidden_objections=hidden_objections,
            social_proof_needs=social_proof_needs,
            decision_readiness=decision_readiness,
            relationship_quality=relationship_quality,
            
            # 🌟 Campos inclusivos
            education_level=education_level,
            original_message=original_message,
            corrected_message=corrected_message,
            spelling_errors=corrections_applied.get('spelling', []),
            phonetic_corrections=corrections_applied.get('phonetic', []),
            colloquial_translations=corrections_applied.get('colloquial', []),
            informal_grammar_score=informal_grammar_score,
            communication_barriers=communication_barriers
        )
        
        logger.debug(LogCategory.CONVERSATION, 
                    f"Mensagem analisada: {primary_intent.value}/{sentiment.value}",
                    details={
                        'confidence': confidence,
                        'entities_count': len(entities),
                        'keywords': keywords[:5]  # Primeiras 5 palavras-chave
                    })
        
        return result
    
    def _expand_semantics(self, message: str) -> tuple[str, Dict[str, List[str]]]:
        """Expandir mensagem com sinônimos e variações"""
        expanded = message.lower()
        expansions = {}
        
        for word, synonyms in self.synonym_map.items():
            if word in expanded:
                expansions[word] = synonyms
                # Adicionar sinônimos como palavras "virtuais" para detecção
                for synonym in synonyms:
                    expanded += f" {synonym}"
        
        return expanded, expansions
    
    def _detect_multiple_intents(self, message: str) -> List[Dict[str, Any]]:
        """Detectar múltiplas intenções em uma mensagem"""
        intents = []
        
        # Dividir mensagem por separadores
        segments = []
        for separator in self.multi_intent_separators:
            if re.search(separator, message, re.IGNORECASE):
                segments = re.split(separator, message, flags=re.IGNORECASE)
                break
        
        if not segments:
            segments = [message]
        
        # Analisar cada segmento
        for i, segment in enumerate(segments):
            if segment.strip():
                intent, confidence = self._detect_intent(segment.strip())
                intents.append({
                    'intent': intent,
                    'confidence': confidence,
                    'segment': segment.strip(),
                    'order': i
                })
        
        return intents
    
    def _get_primary_intent(self, multiple_intents: List[Dict[str, Any]]) -> tuple[IntentType, float]:
        """Obter intenção primária das múltiplas detectadas"""
        if not multiple_intents:
            return IntentType.UNKNOWN, 0.0
        
        # Priorizar por confiança e tipo de intenção
        priority_weights = {
            # Queixas específicas têm prioridade MÁXIMA
            IntentType.FRAUD_CLAIM: 5.0,
            IntentType.INVALID_CHARGE: 4.5,
            IntentType.CUSTOMER_NOT_REGISTERED: 4.0,
            IntentType.SERVICE_CANCELLATION: 3.8,
            IntentType.WRONG_PERSON: 3.6,
            IntentType.BILLING_ERROR: 3.4,
            IntentType.DUPLICATE_CHARGE: 3.2,
            IntentType.MOVED_ADDRESS: 3.0,
            IntentType.DATA_CHANGE_REQUEST: 2.8,
            IntentType.NETWORK_COMPLAINT: 2.6,
            IntentType.TECHNICAL_PROBLEM: 2.4,
            IntentType.POOR_SIGNAL: 2.2,
            IntentType.EQUIPMENT_PROBLEM: 2.0,
            IntentType.SERVICE_NOT_USED: 1.9,
            IntentType.WRONG_PLAN: 1.8,
            
            # Intenções gerais
            IntentType.URGENCY: 3.0,
            IntentType.PAYMENT_CONFIRMATION: 2.5,
            IntentType.COMPLAINT: 2.0,
            IntentType.FINANCIAL_DIFFICULTY: 1.8,
            IntentType.NEGOTIATION: 1.5,
            IntentType.PAYMENT_QUESTION: 1.3,
            IntentType.GREETING: 0.5,
            IntentType.GOODBYE: 0.3
        }
        
        best_intent = None
        best_score = 0
        
        for intent_data in multiple_intents:
            intent = intent_data['intent']
            confidence = intent_data['confidence']
            weight = priority_weights.get(intent, 1.0)
            score = confidence * weight
            
            if score > best_score:
                best_score = score
                best_intent = intent_data
        
        return best_intent['intent'] if best_intent else IntentType.UNKNOWN, best_intent['confidence'] if best_intent else 0.0
    
    def _analyze_sentiment_advanced(self, message: str, multiple_intents: List[Dict[str, Any]]) -> SentimentType:
        """Análise de sentimento avançada considerando contexto"""
        # Primeiro análise básica
        basic_sentiment = self._analyze_sentiment(message)
        
        # Ajustes baseados nas intenções
        intent_sentiment_modifiers = {
            IntentType.URGENCY: SentimentType.URGENT,
            IntentType.COMPLAINT: SentimentType.ANGRY,
            IntentType.FINANCIAL_DIFFICULTY: SentimentType.ANXIOUS,
            IntentType.PAYMENT_CONFIRMATION: SentimentType.POSITIVE
        }
        
        for intent_data in multiple_intents:
            intent = intent_data['intent']
            if intent in intent_sentiment_modifiers:
                confidence = intent_data['confidence']
                if confidence > 0.7:
                    return intent_sentiment_modifiers[intent]
        
        return basic_sentiment
    
    def _extract_entities_advanced(self, message: str) -> Dict[str, Any]:
        """Extração de entidades avançada"""
        entities = self._extract_entities(message)
        
        # Adicionar entidades de contexto temporal
        time_entities = []
        for pattern in ['hoje', 'amanhã', 'semana que vem', 'mês que vem', 'ano que vem']:
            if pattern in message.lower():
                time_entities.append(pattern)
        
        if time_entities:
            entities['temporal_context'] = time_entities
        
        # Entidades de intensidade
        intensity_words = ['muito', 'super', 'extremamente', 'absurdamente', 'pra caramba']
        found_intensity = [word for word in intensity_words if word in message.lower()]
        if found_intensity:
            entities['intensity_modifiers'] = found_intensity
        
        # Entidades de negação
        negation_words = ['não', 'nunca', 'jamais', 'nem', 'nada']
        found_negations = [word for word in negation_words if word in message.lower()]
        if found_negations:
            entities['negations'] = found_negations
        
        return entities
    
    def _detect_contradictions(self, message: str) -> List[Dict[str, str]]:
        """Detectar contradições na mensagem"""
        contradictions = []
        
        for contradiction in self.contradiction_detectors:
            pattern1 = contradiction['pattern1']
            pattern2 = contradiction['pattern2']
            
            if re.search(pattern1, message, re.IGNORECASE) and re.search(pattern2, message, re.IGNORECASE):
                contradictions.append({
                    'type': contradiction['type'],
                    'pattern1': pattern1,
                    'pattern2': pattern2,
                    'description': f"Contradiction detected: {contradiction['type']}"
                })
        
        return contradictions
    
    def _detect_ambiguities(self, message: str) -> List[str]:
        """Detectar ambiguidades e incertezas"""
        ambiguities = []
        
        for ambiguity_type, patterns in self.ambiguity_resolvers.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    ambiguities.append(ambiguity_type)
                    break
        
        return list(set(ambiguities))  # Remove duplicatas
    
    def _analyze_subtext(self, message: str) -> Dict[str, List[str]]:
        """Analisar subtexto e comunicação indireta"""
        subtext = {}
        
        for subtext_type, patterns in self.subtext_analyzers.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                subtext[subtext_type] = matches
        
        return subtext
    
    def _analyze_personality(self, message: str) -> Dict[str, float]:
        """Analisar indicadores de personalidade"""
        personality_scores = {}
        
        for personality_type, patterns in self.personality_indicators.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message, re.IGNORECASE))
                score += matches
            
            # Normalizar score (0-1)
            personality_scores[personality_type] = min(score / 5.0, 1.0)
        
        return personality_scores
    
    def _calculate_urgency_score(self, message: str, sentiment: SentimentType, multiple_intents: List[Dict[str, Any]]) -> float:
        """Calcular score de urgência avançado"""
        base_score = 0.0
        
        # Score baseado no sentimento
        sentiment_urgency = {
            SentimentType.URGENT: 5.0,
            SentimentType.ANGRY: 3.0,
            SentimentType.FRUSTRATED: 2.5,
            SentimentType.ANXIOUS: 2.0,
            SentimentType.NEGATIVE: 1.0
        }
        
        base_score += sentiment_urgency.get(sentiment, 0.0)
        
        # Score baseado nas intenções
        for intent_data in multiple_intents:
            if intent_data['intent'] == IntentType.URGENCY:
                base_score += 4.0 * intent_data['confidence']
        
        # Multiplicadores baseados em padrões
        for multiplier_type, multiplier_value in self.urgency_multipliers.items():
            if multiplier_type == 'time_pressure' and any(word in message.lower() for word in ['hoje', 'agora', 'já', 'imediato']):
                base_score *= multiplier_value
            elif multiplier_type == 'consequences' and any(word in message.lower() for word in ['senão', 'caso contrário', 'vai dar']):
                base_score *= multiplier_value
            elif multiplier_type == 'emotional_intensity' and sentiment in [SentimentType.URGENT, SentimentType.ANGRY]:
                base_score *= multiplier_value
        
        # Normalizar (0-10)
        return min(base_score, 10.0)
    
    def _detect_regional_context(self, message: str) -> str:
        """Detectar contexto regional da linguagem"""
        for region, patterns in self.regional_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return region
        
        return 'generic'
    
    def _calculate_emotional_intensity(self, message: str, sentiment: SentimentType) -> float:
        """Calcular intensidade emocional"""
        intensity = 0.0
        
        # Pontuação como indicador
        exclamations = message.count('!')
        questions = message.count('?')
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
        
        intensity += exclamations * 0.5
        intensity += questions * 0.3
        intensity += caps_ratio * 2.0
        
        # Palavras intensificadoras
        intensifiers = ['muito', 'super', 'extremamente', 'absurdamente', 'demais', 'pra caramba']
        for intensifier in intensifiers:
            if intensifier in message.lower():
                intensity += 1.0
        
        # Multiplicador baseado no sentimento
        sentiment_multipliers = {
            SentimentType.ANGRY: 2.0,
            SentimentType.URGENT: 1.8,
            SentimentType.FRUSTRATED: 1.5,
            SentimentType.ANXIOUS: 1.3,
            SentimentType.POSITIVE: 0.8
        }
        
        intensity *= sentiment_multipliers.get(sentiment, 1.0)
        
        return min(intensity, 10.0)
    
    # 🔥 MÉTODOS ULTRA AVANÇADOS DE ANÁLISE
    
    def _analyze_implicit_meanings(self, message: str) -> Dict[str, List[str]]:
        """Analisar significados implícitos não verbalizados"""
        implicit_meanings = {}
        
        for category, patterns_data in self.implicit_meaning_detectors.items():
            # Verificar padrões ou eufemismos
            patterns = patterns_data.get('patterns', patterns_data.get('euphemisms', []))
            
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    if category not in implicit_meanings:
                        implicit_meanings[category] = []
                    implicit_meanings[category].extend(patterns_data['hidden_meaning'])
        
        return implicit_meanings
    
    def _analyze_emotional_progression(self, message: str, sentiment: SentimentType) -> List[str]:
        """Analisar progressão emocional na conversa"""
        progression = []
        
        # Detectar sinais de evolução emocional
        emotion_signals = {
            'getting_worse': [r'\b(cada vez pior|piorando|deteriorando)\b'],
            'improving': [r'\b(melhorando|mais calmo|tranquilizando)\b'],
            'escalating': [r'\b(mais irritado|perdendo paciência|explodindo)\b'],
            'stabilizing': [r'\b(controlando|respirando|pensando melhor)\b']
        }
        
        for emotion_state, patterns in emotion_signals.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    progression.append(emotion_state)
        
        return progression
    
    def _predict_behavior(self, message: str, multiple_intents: List[Dict[str, Any]]) -> Dict[str, float]:
        """Predizer comportamentos futuros do cliente"""
        predictions = {
            'payment_probability': 0.5,
            'negotiation_willingness': 0.5,
            'escalation_risk': 0.3,
            'ghosting_risk': 0.2
        }
        
        # Analisar indicadores comportamentais
        for behavior_type, indicators in self.behavioral_predictors.items():
            if behavior_type == 'payment_likelihood':
                high_indicators = indicators['high_indicators']
                low_indicators = indicators['low_indicators']
                
                score = 0.5
                for pattern in high_indicators:
                    if re.search(pattern, message, re.IGNORECASE):
                        score += 0.2
                        
                for pattern in low_indicators:
                    if re.search(pattern, message, re.IGNORECASE):
                        score -= 0.3
                        
                predictions['payment_probability'] = max(0.0, min(1.0, score))
        
        return predictions
    
    def _detect_deception(self, message: str) -> List[str]:
        """Detectar possíveis indicadores de decepção ou omissão"""
        deception_signs = []
        
        for deception_type, patterns in self.lie_detectors.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    deception_signs.append(deception_type)
        
        # Detectar super-detalhamento (possível compensação)
        if len(message.split()) > 50:
            deception_signs.append('over_explaining')
        
        # Detectar linguagem muito formal em contexto informal
        formal_words = ['solicito', 'cordialmente', 'atenciosamente']
        if any(word in message.lower() for word in formal_words):
            deception_signs.append('formality_mask')
        
        return list(set(deception_signs))
    
    def _calculate_commitment_level(self, message: str) -> float:
        """Calcular nível de comprometimento com pagamento"""
        commitment_score = 0.0
        word_count = 0
        
        for phrase, score in self.commitment_analyzers.items():
            if phrase in message.lower():
                commitment_score += score
                word_count += 1
        
        # Normalizar baseado no número de frases encontradas
        if word_count > 0:
            commitment_score = commitment_score / word_count
        
        # Ajustar por intensidade
        if '!' in message:
            commitment_score *= 1.2
        if '?' in message:
            commitment_score *= 0.8
        
        return max(0.0, min(3.0, commitment_score))
    
    def _calculate_financial_stress(self, message: str) -> float:
        """Calcular score de estresse financeiro"""
        stress_score = 0.0
        
        for indicator, score in self.financial_stress_indicators.items():
            if indicator in message.lower():
                stress_score += score
        
        # Multiplicadores baseados em contexto
        if any(word in message.lower() for word in ['família', 'filhos', 'casa']):
            stress_score *= 1.3
        
        if any(word in message.lower() for word in ['saúde', 'hospital', 'remédio']):
            stress_score *= 1.5
        
        return min(5.0, stress_score)
    
    def _identify_empathy_triggers(self, message: str) -> List[str]:
        """Identificar gatilhos que requerem resposta empática"""
        triggers = []
        
        for trigger_type, patterns in self.empathy_triggers.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    triggers.append(trigger_type)
        
        return list(set(triggers))
    
    def _analyze_conversation_momentum(self, message: str) -> str:
        """Analisar momentum da conversa"""
        # Detectar momentum positivo
        positive_signals = [r'\b(entendi|faz sentido|concordo|vamos)\b']
        
        # Detectar momentum negativo
        negative_signals = [r'\b(não adianta|sempre assim|cansei)\b']
        
        # Detectar momentum neutro/estagnado
        neutral_signals = [r'\b(não sei|talvez|vou pensar)\b']
        
        positive_count = sum(1 for pattern in positive_signals 
                           if re.search(pattern, message, re.IGNORECASE))
        negative_count = sum(1 for pattern in negative_signals 
                           if re.search(pattern, message, re.IGNORECASE))
        neutral_count = sum(1 for pattern in neutral_signals 
                          if re.search(pattern, message, re.IGNORECASE))
        
        if positive_count > negative_count and positive_count > neutral_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_hidden_objections(self, message: str) -> List[str]:
        """Detectar objeções não verbalizadas"""
        objections = []
        
        # Padrões que indicam objeções ocultas
        objection_patterns = {
            'price_concern': [r'\b(caro|alto|muito|absurdo)\b.*\b(valor|preço)\b'],
            'trust_issues': [r'\b(não confio|suspeito|duvidoso)\b'],
            'authority_issues': [r'\b(não posso decidir|esposa|marido|família)\b'],
            'timing_issues': [r'\b(não é o momento|agora não|mais tarde)\b'],
            'service_doubt': [r'\b(não funciona|não vale|não compensa)\b']
        }
        
        for objection_type, patterns in objection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    objections.append(objection_type)
        
        return objections
    
    def _analyze_social_proof_needs(self, message: str) -> List[str]:
        """Analisar necessidades de prova social"""
        social_needs = []
        
        # Padrões que indicam necessidade de validação social
        social_patterns = {
            'peer_validation': [r'\b(outros fazem|todo mundo|normal)\b'],
            'authority_validation': [r'\b(especialista|profissional|autoridade)\b'],
            'testimonial_need': [r'\b(experiência|depoimento|exemplo)\b'],
            'popularity_proof': [r'\b(muita gente|maioria|comum)\b']
        }
        
        for need_type, patterns in social_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    social_needs.append(need_type)
        
        return social_needs
    
    def _calculate_decision_readiness(self, message: str, sentiment: SentimentType) -> float:
        """Calcular prontidão para tomar decisão"""
        readiness = 0.5  # Base neutra
        
        # Sinais de alta prontidão
        ready_signals = [r'\b(vamos|aceito|combinado|fechado)\b']
        
        # Sinais de baixa prontidão
        hesitant_signals = [r'\b(pensar|ver|talvez|não sei)\b']
        
        # Contar sinais
        ready_count = sum(1 for pattern in ready_signals 
                         if re.search(pattern, message, re.IGNORECASE))
        hesitant_count = sum(1 for pattern in hesitant_signals 
                           if re.search(pattern, message, re.IGNORECASE))
        
        # Ajustar baseado nos sinais
        readiness += (ready_count * 0.2) - (hesitant_count * 0.2)
        
        # Ajustar baseado no sentimento
        if sentiment == SentimentType.POSITIVE:
            readiness += 0.2
        elif sentiment == SentimentType.URGENT:
            readiness += 0.3
        elif sentiment == SentimentType.ANXIOUS:
            readiness -= 0.1
        
        return max(0.0, min(1.0, readiness))
    
    def _assess_relationship_quality(self, message: str, sentiment: SentimentType) -> str:
        """Avaliar qualidade do relacionamento cliente-empresa"""
        # Indicadores de relacionamento positivo
        positive_indicators = [r'\b(obrigado|grato|educados|atenciosos)\b']
        
        # Indicadores de relacionamento deteriorado
        negative_indicators = [r'\b(sempre assim|toda vez|decepcionado|chateado)\b']
        
        # Indicadores de relacionamento neutro
        neutral_indicators = [r'\b(primeira vez|novo|não conheço)\b']
        
        positive_score = sum(1 for pattern in positive_indicators 
                           if re.search(pattern, message, re.IGNORECASE))
        negative_score = sum(1 for pattern in negative_indicators 
                           if re.search(pattern, message, re.IGNORECASE))
        neutral_score = sum(1 for pattern in neutral_indicators 
                          if re.search(pattern, message, re.IGNORECASE))
        
        # Considerar sentimento geral
        if sentiment == SentimentType.ANGRY:
            negative_score += 2
        elif sentiment == SentimentType.POSITIVE:
            positive_score += 1
        
        if positive_score > negative_score:
            return 'good'
        elif negative_score > positive_score:
            return 'deteriorated'
        else:
            return 'neutral'
    
    # 🌟 MÉTODOS ULTRA INCLUSIVOS
    
    def _apply_inclusive_corrections(self, message: str) -> tuple[str, Dict[str, List[Dict[str, str]]]]:
        """Aplicar correções fonéticas, ortográficas e coloquiais"""
        corrected = message.lower()
        corrections_applied = {
            'phonetic': [],
            'spelling': [],
            'colloquial': []
        }
        
        # 1. Correções fonéticas (vuce -> vocês)
        for wrong, correct in self.phonetic_corrections.items():
            if wrong in corrected:
                corrections_applied['phonetic'].append({
                    'original': wrong,
                    'corrected': correct,
                    'type': 'phonetic'
                })
                corrected = corrected.replace(wrong, correct)
        
        # 2. Correções ortográficas
        for wrong, correct in self.spelling_corrections.items():
            if wrong in corrected:
                corrections_applied['spelling'].append({
                    'original': wrong,
                    'corrected': correct,
                    'type': 'spelling'
                })
                corrected = corrected.replace(wrong, correct)
        
        # 3. Traduções coloquiais
        for colloquial, formal in self.colloquial_translations.items():
            if colloquial in corrected:
                corrections_applied['colloquial'].append({
                    'original': colloquial,
                    'corrected': formal,
                    'type': 'colloquial'
                })
                corrected = corrected.replace(colloquial, formal)
        
        # 4. Expandir abreviações
        for abbrev, expansion in self.abbreviation_expanders.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            if re.search(pattern, corrected, re.IGNORECASE):
                corrections_applied['spelling'].append({
                    'original': abbrev,
                    'corrected': expansion,
                    'type': 'abbreviation'
                })
                corrected = re.sub(pattern, expansion, corrected, flags=re.IGNORECASE)
        
        # 5. Limpar repetições excessivas
        for pattern, replacement in self.repetition_patterns.items():
            corrected = re.sub(pattern, replacement, corrected)
        
        return corrected, corrections_applied
    
    def _detect_education_level(self, message: str) -> str:
        """Detectar nível educacional baseado na linguagem"""
        scores = {
            'baixa_escolaridade': 0,
            'media_escolaridade': 0,
            'alta_escolaridade': 0
        }
        
        for level, patterns in self.education_level_detectors.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, message, re.IGNORECASE))
                scores[level] += matches
        
        # Fatores adicionais
        # Muitos erros de grafia = baixa escolaridade
        spelling_errors = sum(1 for word in self.spelling_corrections.keys() 
                            if word in message.lower())
        if spelling_errors > 3:
            scores['baixa_escolaridade'] += 2
        
        # Uso de gírias excessivas = escolaridade média/baixa
        slang_count = sum(1 for slang in self.colloquial_translations.keys() 
                         if slang in message.lower())
        if slang_count > 2:
            scores['media_escolaridade'] += 1
        
        # Palavras complexas = alta escolaridade
        complex_words = ['mediante', 'todavia', 'portanto', 'outrossim']
        complex_count = sum(1 for word in complex_words if word in message.lower())
        if complex_count > 0:
            scores['alta_escolaridade'] += complex_count * 2
        
        # Retornar nível com maior score
        max_level = max(scores, key=scores.get)
        max_score = scores[max_level]
        
        if max_score == 0:
            return 'unknown'
        
        return max_level
    
    def _detect_communication_barriers(self, message: str) -> List[str]:
        """Detectar barreiras de comunicação"""
        barriers = []
        
        # Analfabetismo funcional
        phonetic_errors = sum(1 for error in self.phonetic_corrections.keys() 
                            if error in message.lower())
        if phonetic_errors > 2:
            barriers.append('analfabetismo_funcional')
        
        # Dificuldade de expressão
        if len(message.split()) < 3:
            barriers.append('expressao_limitada')
        
        # Uso excessivo de gírias
        slang_count = sum(1 for slang in self.colloquial_translations.keys() 
                         if slang in message.lower())
        if slang_count > 3:
            barriers.append('linguagem_muito_informal')
        
        # Problemas de concordância
        for error_type, patterns in self.informal_grammar_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    barriers.append('problemas_gramaticais')
                    break
        
        # Comunicação emocional (só emoticons/sons)
        emotion_sounds = sum(1 for sound in self.emotion_sounds.keys() 
                           if sound in message.lower())
        total_words = len(message.split())
        if emotion_sounds > 0 and total_words <= emotion_sounds + 2:
            barriers.append('comunicacao_emocional')
        
        # Repetição excessiva (ênfase por repetição)
        if re.search(r'(.)\1{3,}', message):
            barriers.append('enfase_por_repeticao')
        
        return list(set(barriers))
    
    def _calculate_informal_grammar_score(self, message: str) -> float:
        """Calcular score de informalidade gramatical (0-1)"""
        informal_indicators = 0
        total_possible = 10  # Máximo de indicadores
        
        # Erros de concordância
        for error_type, patterns in self.informal_grammar_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    informal_indicators += 1
        
        # Uso de contrações informais
        contractions = ['pro', 'pra', 'dum', 'duma', 'numa']
        informal_indicators += sum(1 for contraction in contractions 
                                 if contraction in message.lower())
        
        # Falta de pontuação
        if not re.search(r'[.!?]', message):
            informal_indicators += 1
        
        # Uso de internetês
        internet_slang = ['kk', 'rs', 'kkk', 'haha', 'lol']
        informal_indicators += sum(1 for slang in internet_slang 
                                 if slang in message.lower())
        
        # Abreviações excessivas
        abbreviations = sum(1 for abbrev in self.abbreviation_expanders.keys() 
                          if abbrev in message.lower())
        informal_indicators += min(abbreviations, 3)
        
        return min(informal_indicators / total_possible, 1.0)
    
    def _detect_communication_style(self, message: str) -> str:
        """Detectar estilo comunicativo"""
        style_scores = {}
        
        for style_type, patterns in self.personality_indicators.items():
            score = 0
            for pattern in patterns:
                score += len(re.findall(pattern, message, re.IGNORECASE))
            style_scores[style_type] = score
        
        # Retornar estilo dominante
        if style_scores:
            return max(style_scores, key=style_scores.get)
        
        return 'neutral'
    
    def _clean_text(self, text: str) -> str:
        """Limpar e normalizar texto"""
        # Converter para minúsculas
        text = text.lower()
        
        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Remover caracteres especiais (manter apenas letras, números e espaços)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _detect_intent(self, message: str) -> Tuple[IntentType, float]:
        """Detectar intenção da mensagem"""
        best_intent = IntentType.UNKNOWN
        best_score = 0.0
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            matches = 0
            
            for pattern in patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    matches += 1
                    score += 1.0
            
            # Normalizar score
            if patterns:
                score = score / len(patterns)
            
            if score > best_score:
                best_score = score
                best_intent = intent
        
        # Ajustar confiança baseado na quantidade de matches
        confidence = min(best_score * 1.2, 1.0)
        
        return best_intent, confidence
    
    def _analyze_sentiment(self, message: str) -> SentimentType:
        """Analisar sentimento da mensagem com múltiplas emoções"""
        words = message.split()
        sentiment_scores = {sentiment: 0 for sentiment in SentimentType}
        
        # Contar palavras de cada sentimento
        for word in words:
            for sentiment, word_list in self.sentiment_words.items():
                if any(sentiment_word in word for sentiment_word in word_list):
                    sentiment_scores[sentiment] += 1
        
        # Aplicar pesos especiais
        sentiment_scores[SentimentType.ANGRY] *= 2.5      # Raiva tem prioridade
        sentiment_scores[SentimentType.URGENT] *= 2.0     # Urgência é importante
        sentiment_scores[SentimentType.FRUSTRATED] *= 1.5 # Frustração precisa atenção
        
        # Verificar padrões especiais
        message_lower = message.lower()
        
        # Detectar sarcasmo/ironia (sentimento negativo disfarçado)
        if any(word in message_lower for word in ['né', 'claro', 'obvio', 'lógico']) and '?' in message:
            sentiment_scores[SentimentType.FRUSTRATED] += 2
        
        # Detectar desespero
        if any(phrase in message_lower for phrase in ['não sei mais', 'não aguento', 'to desesperado']):
            sentiment_scores[SentimentType.ANXIOUS] += 3
        
        # Detectar múltiplas exclamações (emoção intensa)
        exclamation_count = message.count('!')
        if exclamation_count > 1:
            sentiment_scores[SentimentType.URGENT] += exclamation_count
        
        # Determinar sentimento dominante
        max_sentiment = max(sentiment_scores, key=sentiment_scores.get)
        max_score = sentiment_scores[max_sentiment]
        
        if max_score == 0:
            return SentimentType.NEUTRAL
        
        return max_sentiment
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extrair entidades da mensagem"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, message)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extrair palavras-chave relevantes"""
        # Palavras irrelevantes (stop words)
        stop_words = {
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
            'em', 'no', 'na', 'nos', 'nas', 'para', 'por', 'com', 'sem', 'sob', 'sobre',
            'e', 'ou', 'mas', 'que', 'se', 'ele', 'ela', 'eles', 'elas', 'eu', 'tu', 'nos',
            'é', 'são', 'foi', 'foram', 'ser', 'estar', 'ter', 'haver', 'isso', 'isto',
            'já', 'ainda', 'só', 'também', 'bem', 'muito', 'mais', 'menos', 'todo', 'toda'
        }
        
        words = message.split()
        keywords = []
        
        for word in words:
            if len(word) > 3 and word not in stop_words:
                keywords.append(word)
        
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords[:10]  # Máximo 10 palavras-chave

class ResponseGenerator:
    """Gerador de respostas inteligentes"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        logger.info(LogCategory.CONVERSATION, "Response Generator inicializado")
    
    def _load_response_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Carregar templates de resposta"""
        return {
            'greeting': {
                'positive': [
                    "Olá! 😊 Obrigado por entrar em contato. Como posso ajudá-lo hoje?",
                    "Oi! Tudo bem? Estou aqui para esclarecer suas dúvidas sobre a cobrança.",
                    "Olá! 👋 Fico feliz em falar com você. Em que posso ser útil?"
                ],
                'neutral': [
                    "Olá! Sou o assistente virtual. Como posso ajudá-lo?",
                    "Oi! Estou aqui para tirar suas dúvidas. O que precisa?",
                    "Olá! Como posso auxiliá-lo hoje?"
                ]
            },
            'payment_confirmation': {
                'positive': [
                    "Que ótima notícia! 🎉 Obrigado por nos informar sobre o pagamento. Vou verificar em nosso sistema e retorno em breve.",
                    "Perfeito! Agradeço por avisar. Vou confirmar o recebimento e te dou um retorno.",
                    "Excelente! 👏 Obrigado pela informação. Vou checar e confirmo o pagamento."
                ],
                'neutral': [
                    "Entendi. Vou verificar o pagamento em nosso sistema e retorno com a confirmação.",
                    "Ok, recebida a informação. Vou validar o pagamento e te dou um feedback.",
                    "Anotado. Vou conferir e confirmo se está tudo certo."
                ]
            },
            'payment_question': {
                'neutral': [
                    "Claro! Posso te ajudar com as informações de pagamento. Qual sua dúvida específica?",
                    "Sem problemas! Estou aqui para esclarecer sobre o pagamento. O que gostaria de saber?",
                    "Perfeitamente! Vou te passar todas as informações necessárias para o pagamento."
                ]
            },
            'negotiation': {
                'empathetic': [
                    "Entendo sua situação e agradeço por ser transparente. 🤝 Vamos encontrar uma solução que funcione para ambos.",
                    "Compreendo que às vezes surgem dificuldades. Estou aqui para ajudar a encontrar uma alternativa viável.",
                    "Obrigado por compartilhar sua situação. Vamos trabalhar juntos para encontrar uma solução adequada."
                ],
                'neutral': [
                    "Entendi. Vamos avaliar as possibilidades de negociação disponíveis para seu caso.",
                    "Ok, posso verificar as opções de parcelamento ou desconto disponíveis.",
                    "Anotado. Vou consultar as alternativas de pagamento que temos."
                ]
            },
            'complaint': {
                'empathetic': [
                    "Lamento que esteja passando por essa situação. 😔 Vou fazer o possível para resolver sua questão.",
                    "Peço desculpas pelo transtorno. Sua reclamação é importante e vou encaminhá-la adequadamente.",
                    "Entendo sua frustração e vou trabalhar para solucionar essa questão o mais rápido possível."
                ],
                'directive': [
                    "Vou registrar sua reclamação e encaminhar para o setor responsável analisar.",
                    "Sua questão será tratada com prioridade. Vou direcioná-la para resolução.",
                    "Entendido. Vou escalar sua reclamação para que seja resolvida adequadamente."
                ]
            },
            'information_request': {
                'informative': [
                    "Claro! Ficarei feliz em esclarecer suas dúvidas. O que gostaria de saber?",
                    "Sem problemas! Estou aqui para fornecer todas as informações necessárias.",
                    "Perfeitamente! Vou te passar os detalhes que precisa. Qual sua dúvida?"
                ]
            },
            'goodbye': {
                'positive': [
                    "Foi um prazer ajudá-lo! 😊 Qualquer dúvida, estarei aqui. Tenha um ótimo dia!",
                    "Obrigado pelo contato! 👋 Fico à disposição sempre que precisar.",
                    "Até mais! Espero ter ajudado. Qualquer coisa, é só chamar! 🙂"
                ],
                'neutral': [
                    "Até logo! Qualquer dúvida, estarei disponível.",
                    "Tchau! Fico à disposição para futuras questões.",
                    "Até mais! Obrigado pelo contato."
                ]
            },
            'urgency': {
                'urgent': [
                    "Entendo a urgência da sua situação! 🚨 Vou priorizar seu atendimento.",
                    "Situação urgente identificada! Vou encaminhar para resolução imediata.",
                    "Compreendo que é urgente! Vamos resolver isso o mais rápido possível."
                ],
                'empathetic': [
                    "Percebo que é uma situação urgente para você. Como posso ajudar?",
                    "Entendo sua pressa. Vamos ver como resolver isso rapidamente.",
                    "Situação urgente compreendida. Qual a melhor forma de te ajudar?"
                ]
            },
            'discount_request': {
                'neutral': [
                    "Entendo seu interesse em desconto. Vou verificar as opções disponíveis para seu caso.",
                    "Sobre desconto, preciso consultar as políticas. Vou verificar o que é possível.",
                    "Vou analisar as possibilidades de desconto baseado na sua situação."
                ]
            },
            'financial_difficulty': {
                'empathetic': [
                    "Compreendo sua situação financeira difícil. 💙 Vamos encontrar uma solução juntos.",
                    "Entendo que está passando por dificuldades. Vou buscar a melhor alternativa para você.",
                    "Situação difícil compreendida. Vamos trabalhar uma solução que caiba no seu orçamento."
                ]
            },
            'installment_request': {
                'positive': [
                    "Claro! Vamos verificar as opções de parcelamento disponíveis para você. 💳",
                    "Parcelamento é uma ótima opção! Vou consultar as condições disponíveis.",
                    "Perfeito! Vou verificar quantas parcelas podemos oferecer para seu caso."
                ]
            },
            'deadline_extension': {
                'empathetic': [
                    "Entendo que precisa de mais tempo. Vou verificar a possibilidade de prorrogação.",
                    "Compreendo sua necessidade de mais prazo. Vamos ver o que é possível fazer.",
                    "Situação compreendida. Vou consultar sobre extensão de prazo para você."
                ]
            },
            'contact_request': {
                'informative': [
                    "Claro! Vou te passar os dados de contato adequados para sua situação.",
                    "Sem problemas! Aqui estão as informações de contato que precisa.",
                    "Perfeitamente! Vou te direcionar para o contato correto."
                ]
            },
            # RESPOSTAS PARA QUEIXAS ESPECÍFICAS
            'network_complaint': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Mesmo com problemas técnicos, a cobrança permanece ativa conforme contrato.",
                    "Entendo o problema de rede. Seu cadastro consta em nosso sistema para cobrança dos débitos a Desktop, independente de instabilidades técnicas.",
                    "Problemas de conexão não suspendem automaticamente a cobrança. Seu número está registrado em nossa base para cobrança dos débitos a Desktop."
                ]
            },
            'service_cancellation': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Para confirmar cancelamento, preciso verificar se o processo foi finalizado corretamente.",
                    "Consta em nosso sistema seu cadastro ativo para cobrança dos débitos a Desktop. Vou verificar o status do seu pedido de cancelamento.",
                    "Seu registro está em nossa base de cobrança dos débitos a Desktop. É necessário confirmar se o cancelamento foi processado adequadamente."
                ]
            },
            'invalid_charge': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Vou verificar a origem da cobrança em questão.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Preciso analisar os detalhes da contratação para esclarecer a situação.",
                    "Seu registro está em nossa base de dados para cobrança dos débitos a Desktop. Vou consultar o histórico da contratação do serviço."
                ]
            },
            'technical_problem': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Problemas técnicos não impedem a cobrança do serviço contratado.",
                    "Entendo o problema técnico. Seu cadastro permanece ativo em nosso sistema para cobrança dos débitos a Desktop conforme termos contratuais.",
                    "Seu registro consta em nossa base para cobrança dos débitos a Desktop. Questões técnicas são tratadas separadamente da cobrança do plano."
                ]
            },
            'billing_error': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Vou verificar se há inconsistências no valor cobrado.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Preciso analisar os detalhes da fatura para identificar possíveis erros.",
                    "Seu registro está em nossa base de dados para cobrança dos débitos a Desktop. Vou revisar os valores para confirmar se estão corretos conforme contrato."
                ]
            },
            'data_change_request': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Para atualizar dados, preciso confirmar sua identidade primeiro.",
                    "Consta seu registro em nosso sistema para cobrança dos débitos a Desktop. Mudanças de dados devem ser validadas para manter a cobrança atualizada.",
                    "Seu cadastro está em nossa base para cobrança dos débitos a Desktop. Vou verificar como proceder com a atualização dos seus dados."
                ]
            },
            'service_not_used': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop, independente do uso efetivo.",
                    "Consta em nosso sistema seu cadastro ativo para cobrança dos débitos a Desktop. A disponibilização do serviço gera cobrança conforme contrato.",
                    "Seu registro está em nossa base para cobrança dos débitos a Desktop. O não uso não suspende automaticamente a cobrança mensal."
                ]
            },
            'duplicate_charge': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Vou verificar se houve duplicidade na cobrança.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Preciso analisar se realmente ocorreu cobrança em duplicata.",
                    "Seu registro está em nossa base de dados para cobrança dos débitos a Desktop. Vou revisar o histórico para identificar possível duplicação."
                ]
            },
            'wrong_plan': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Vou verificar qual plano está ativo em seu nome.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Preciso confirmar os detalhes do plano contratado.",
                    "Seu registro está em nossa base para cobrança dos débitos a Desktop. Vou consultar qual modalidade de serviço foi ativada."
                ]
            },
            'poor_signal': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Problemas de sinal não afetam a cobrança do serviço contratado.",
                    "Entendo a questão do sinal. Seu cadastro permanece em nosso sistema para cobrança dos débitos a Desktop conforme contrato firmado.",
                    "Seu registro consta em nossa base para cobrança dos débitos a Desktop. Qualidade do sinal é tratada separadamente da cobrança mensal."
                ]
            },
            'equipment_problem': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Problemas de equipamento não suspendem a cobrança do plano.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Defeitos em equipamentos são resolvidos sem afetar a cobrança mensal.",
                    "Seu registro está em nossa base para cobrança dos débitos a Desktop. Questões de equipamento são tratadas pelo suporte técnico."
                ]
            },
            'customer_not_registered': {
                'informative': [
                    "Realizei a consulta e seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop.",
                    "Verifiquei em nosso sistema e consta seu cadastro ativo para cobrança dos débitos a Desktop. Os dados foram confirmados em nossa base.",
                    "Consultei nossa base de dados e seu número está devidamente registrado para cobrança dos débitos a Desktop."
                ]
            },
            'moved_address': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Mudança de endereço não cancela automaticamente o serviço.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. É necessário formalizar a transferência ou cancelamento por mudança.",
                    "Seu registro permanece em nossa base para cobrança dos débitos a Desktop. Mudanças de endereço devem ser comunicadas formalmente."
                ]
            },
            'wrong_person': {
                'informative': [
                    "Verifiquei e seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Os dados conferem com nossos registros.",
                    "Consultei o sistema e consta seu cadastro para cobrança dos débitos a Desktop. As informações estão corretas em nossa base.",
                    "Confirmei em nossa base de dados: seu número está devidamente registrado para cobrança dos débitos a Desktop conforme contratação."
                ]
            },
            'fraud_claim': {
                'informative': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Casos de fraude devem ser formalizados com documentação.",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Alegações de fraude requerem investigação e comprovação oficial.",
                    "Seu registro está em nossa base para cobrança dos débitos a Desktop. Para casos de fraude, é necessário apresentar boletim de ocorrência."
                ]
            },
            'unknown': {
                'neutral': [
                    "Seu número está cadastrado no nosso banco de dados para cobrança referente aos seus débitos a Desktop. Pode me explicar melhor sua situação?",
                    "Consta seu cadastro em nosso sistema para cobrança dos débitos a Desktop. Preciso entender melhor sua questão para ajudá-lo.",
                    "Seu registro está em nossa base de dados para cobrança dos débitos a Desktop. Pode detalhar qual é sua dúvida ou problema?"
                ]
            }
        }
    
    def generate_response(self, analysis: AnalysisResult, context: ConversationContext) -> BotResponse:
        """Gerar resposta baseada na análise"""
        intent_key = analysis.intent.value
        
        # Determinar tom da resposta baseado no sentimento
        tone = self._determine_tone(analysis.sentiment, context)
        
        # Obter templates disponíveis
        templates = self.response_templates.get(intent_key, {})
        tone_templates = templates.get(tone, templates.get('neutral', []))
        
        if not tone_templates:
            # Fallback para resposta padrão
            tone_templates = self.response_templates['unknown']['neutral']
        
        # Escolher template aleatório
        template = random.choice(tone_templates)
        
        # Personalizar resposta com informações do contexto
        response_text = self._personalize_response(template, context, analysis)
        
        # Determinar tipo de resposta
        response_type = self._determine_response_type(analysis.intent, analysis.sentiment)
        
        # Verificar se deve escalar
        should_escalate = self._should_escalate(analysis, context)
        
        # Sugerir ações
        suggested_actions = self._get_suggested_actions(analysis.intent, context)
        
        response = BotResponse(
            text=response_text,
            response_type=response_type,
            confidence=analysis.confidence,
            should_escalate=should_escalate,
            suggested_actions=suggested_actions
        )
        
        logger.debug(LogCategory.CONVERSATION, 
                    f"Resposta gerada: {response_type.value}",
                    details={
                        'intent': analysis.intent.value,
                        'sentiment': analysis.sentiment.value,
                        'should_escalate': should_escalate,
                        'confidence': analysis.confidence
                    })
        
        return response
    
    def _determine_tone(self, sentiment: SentimentType, context: ConversationContext) -> str:
        """Determinar tom da resposta"""
        if sentiment == SentimentType.ANGRY:
            return 'empathetic'
        elif sentiment == SentimentType.NEGATIVE:
            return 'empathetic'
        elif sentiment == SentimentType.POSITIVE:
            return 'positive'
        else:
            return 'neutral'
    
    def _personalize_response(self, template: str, context: ConversationContext, analysis: AnalysisResult) -> str:
        """Personalizar resposta com dados do contexto"""
        response = template
        
        # Substituir nome se disponível
        if context.user_name:
            response = response.replace("{name}", context.user_name)
        
        # Adicionar informações específicas baseadas na intenção
        if analysis.intent == IntentType.PAYMENT_QUESTION:
            if context.payment_amount:
                response += f"\n\n💰 Valor: R$ {context.payment_amount:.2f}"
            if context.due_date:
                response += f"\n📅 Vencimento: {context.due_date}"
        
        return response
    
    def _determine_response_type(self, intent: IntentType, sentiment: SentimentType) -> ResponseType:
        """Determinar tipo de resposta"""
        if sentiment == SentimentType.ANGRY:
            return ResponseType.EMPATHETIC
        elif intent == IntentType.PAYMENT_CONFIRMATION:
            return ResponseType.CONFIRMATION
        elif intent == IntentType.NEGOTIATION:
            return ResponseType.EMPATHETIC
        elif intent == IntentType.COMPLAINT:
            return ResponseType.ESCALATION
        elif intent == IntentType.PAYMENT_QUESTION:
            return ResponseType.INFORMATIVE
        else:
            return ResponseType.INFORMATIVE
    
    def _should_escalate(self, analysis: AnalysisResult, context: ConversationContext) -> bool:
        """Verificar se deve escalar para humano"""
        # Escalar se usuário está muito irritado
        if analysis.sentiment == SentimentType.ANGRY:
            return True
        
        # Escalar se é uma reclamação
        if analysis.intent == IntentType.COMPLAINT:
            return True
        
        # Escalar se a conversa está muito longa
        if context.message_count > 10:
            return True
        
        # Escalar se confiança é muito baixa
        if analysis.confidence < 0.5:
            return True
        
        return False
    
    def _get_suggested_actions(self, intent: IntentType, context: ConversationContext) -> List[str]:
        """Obter ações sugeridas"""
        actions = []
        
        if intent == IntentType.PAYMENT_CONFIRMATION:
            actions.extend([
                "Verificar pagamento no sistema",
                "Enviar confirmação ao cliente",
                "Atualizar status da cobrança"
            ])
        
        elif intent == IntentType.NEGOTIATION:
            actions.extend([
                "Verificar opções de parcelamento",
                "Consultar política de desconto",
                "Propor acordo amigável"
            ])
        
        elif intent == IntentType.COMPLAINT:
            actions.extend([
                "Registrar reclamação formal",
                "Encaminhar para supervisor",
                "Investigar causa da reclamação"
            ])
        
        return actions

class ConversationBot:
    """Bot principal de conversação"""
    
    def __init__(self):
        self.nlp = NLPProcessor()
        self.response_generator = ResponseGenerator()
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        logger.info(LogCategory.CONVERSATION, "Conversation Bot inicializado")
    
    def process_message(self, phone: str, message: str, user_name: str = None) -> BotResponse:
        """Processar mensagem do usuário"""
        # Obter ou criar contexto
        context = self._get_or_create_context(phone, user_name)
        
        # Analisar mensagem
        analysis = self.nlp.analyze_message(message)
        
        # Atualizar contexto
        self._update_context(context, analysis)
        
        # Gerar resposta
        response = self.response_generator.generate_response(analysis, context)
        
        # Log da interação
        logger.conversation_event(
            phone=phone,
            direction="incoming",
            message=message,
            ai_response=True
        )
        
        logger.conversation_event(
            phone=phone,
            direction="outgoing",
            message=response.text,
            ai_response=True
        )
        
        return response
    
    def _get_or_create_context(self, phone: str, user_name: str = None) -> ConversationContext:
        """Obter ou criar contexto da conversa"""
        if phone not in self.active_contexts:
            session_id = f"session_{phone}_{int(time.time())}"
            
            context = ConversationContext(
                user_phone=phone,
                session_id=session_id,
                started_at=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat(),
                message_count=0,
                user_name=user_name
            )
            
            self.active_contexts[phone] = context
            
            logger.info(LogCategory.CONVERSATION, f"Nova conversa iniciada: {phone}")
        
        return self.active_contexts[phone]
    
    def _update_context(self, context: ConversationContext, analysis: AnalysisResult):
        """Atualizar contexto da conversa com análise avançada"""
        context.last_activity = datetime.now().isoformat()
        context.message_count += 1
        
        # Adicionar ao histórico
        previous_sentiment = context.sentiment_history[-1] if context.sentiment_history else None
        context.intent_history.append(analysis.intent)
        context.sentiment_history.append(analysis.sentiment)
        
        # Detectar mudança de sentimento
        if previous_sentiment and previous_sentiment != analysis.sentiment:
            context.last_sentiment_change = f"{previous_sentiment.value} -> {analysis.sentiment.value}"
        
        # Atualizar níveis de frustração e urgência
        self._update_emotion_levels(context, analysis)
        
        # Analisar capacidade de pagamento baseada no histórico
        self._analyze_payment_capacity(context, analysis)
        
        # Identificar solução preferida
        self._identify_preferred_solution(context, analysis)
        
        # Verificar motivos de escalação
        self._check_escalation_reasons(context, analysis)
        
        # Limitar histórico
        if len(context.intent_history) > 20:
            context.intent_history = context.intent_history[-20:]
        if len(context.sentiment_history) > 20:
            context.sentiment_history = context.sentiment_history[-20:]
        
        # Extrair e armazenar informações relevantes
        self._extract_context_entities(context, analysis)
        
        # Adicionar tópicos discutidos
        context.topics_discussed.add(analysis.intent.value)
        
    def _update_emotion_levels(self, context: ConversationContext, analysis: AnalysisResult):
        """Atualizar níveis emocionais do contexto"""
        # Atualizar frustração
        if analysis.sentiment in [SentimentType.ANGRY, SentimentType.FRUSTRATED]:
            context.frustration_level = min(10, context.frustration_level + 2)
        elif analysis.sentiment == SentimentType.POSITIVE:
            context.frustration_level = max(0, context.frustration_level - 1)
        
        # Atualizar urgência
        if analysis.sentiment == SentimentType.URGENT or analysis.intent == IntentType.URGENCY:
            context.urgency_level = min(10, context.urgency_level + 3)
        elif analysis.sentiment == SentimentType.RELIEVED:
            context.urgency_level = max(0, context.urgency_level - 2)
    
    def _analyze_payment_capacity(self, context: ConversationContext, analysis: AnalysisResult):
        """Analisar capacidade de pagamento do cliente"""
        if analysis.intent == IntentType.FINANCIAL_DIFFICULTY:
            context.payment_capacity = 'low'
        elif analysis.intent == IntentType.PAYMENT_CONFIRMATION:
            context.payment_capacity = 'high'
        elif analysis.intent == IntentType.INSTALLMENT_REQUEST:
            if not context.payment_capacity:
                context.payment_capacity = 'medium'
        elif analysis.intent == IntentType.DISCOUNT_REQUEST:
            if not context.payment_capacity:
                context.payment_capacity = 'medium'
    
    def _identify_preferred_solution(self, context: ConversationContext, analysis: AnalysisResult):
        """Identificar solução preferida do cliente"""
        if analysis.intent == IntentType.INSTALLMENT_REQUEST:
            context.preferred_solution = 'installments'
        elif analysis.intent == IntentType.DISCOUNT_REQUEST:
            context.preferred_solution = 'discount'
        elif analysis.intent == IntentType.DEADLINE_EXTENSION:
            context.preferred_solution = 'extension'
        elif analysis.intent == IntentType.NEGOTIATION:
            if not context.preferred_solution:
                context.preferred_solution = 'negotiation'
    
    def _check_escalation_reasons(self, context: ConversationContext, analysis: AnalysisResult):
        """Verificar motivos para escalação"""
        if context.frustration_level >= 7:
            context.escalation_reasons.append('High frustration level')
        
        if context.message_count > 15:
            context.escalation_reasons.append('Long conversation')
        
        if analysis.sentiment == SentimentType.ANGRY and context.message_count > 3:
            context.escalation_reasons.append('Persistent anger')
        
        if analysis.intent == IntentType.COMPLAINT:
            context.escalation_reasons.append('Formal complaint')
        
        if analysis.intent == IntentType.CONTACT_REQUEST:
            context.escalation_reasons.append('Human contact requested')
    
    def _extract_context_entities(self, context: ConversationContext, analysis: AnalysisResult):
        """Extrair entidades e atualizar contexto"""
        # Valores monetários
        if 'money' in analysis.entities:
            amounts = analysis.entities['money']
            if amounts:
                try:
                    amount_str = amounts[0].replace('.', '').replace(',', '.')
                    context.payment_amount = float(amount_str)
                except ValueError:
                    pass
        
        # Datas
        if 'date' in analysis.entities:
            dates = analysis.entities['date']
            if dates:
                context.due_date = dates[0]
        
        # Datas relativas
        if 'date_relative' in analysis.entities:
            relative_dates = analysis.entities['date_relative']
            if relative_dates:
                context.due_date = relative_dates[0]  # Processamento adicional seria feito aqui
        
        # Parcelas
        if 'installments' in analysis.entities:
            installments = analysis.entities['installments']
            if installments and not context.preferred_solution:
                context.preferred_solution = f'installments_{installments[0]}'
    
    def get_context_stats(self) -> Dict[str, Any]:
        """Obter estatísticas dos contextos ativos"""
        total_contexts = len(self.active_contexts)
        total_messages = sum(ctx.message_count for ctx in self.active_contexts.values())
        
        # Limpeza de contextos antigos (mais de 24h sem atividade)
        cutoff_time = datetime.now() - timedelta(hours=24)
        active_contexts = 0
        
        for phone, context in list(self.active_contexts.items()):
            last_activity = datetime.fromisoformat(context.last_activity)
            if last_activity < cutoff_time:
                del self.active_contexts[phone]
            else:
                active_contexts += 1
        
        return {
            'total_contexts': total_contexts,
            'active_contexts': active_contexts,
            'total_messages': total_messages,
            'average_messages_per_context': total_messages / total_contexts if total_contexts > 0 else 0
        }
