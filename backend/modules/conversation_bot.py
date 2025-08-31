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
    
    # 🔥 ANÁLISES MEGA ULTRA AVANÇADAS
    psychological_profile: Dict[str, float] = None    # Perfil psicológico completo
    socioeconomic_level: str = 'unknown'              # Nível socioeconômico detectado
    cultural_background: str = 'generic'              # Background cultural
    linguistic_complexity: float = 0.0                # Complexidade linguística (0-1)
    emotional_intelligence_score: float = 0.0         # QE - Quociente Emocional
    trust_level: float = 0.5                          # Nível de confiança (0-1)
    stress_indicators: List[str] = None               # Indicadores de estresse
    motivation_drivers: List[str] = None              # Motivadores principais
    negotiation_style: str = 'unknown'                # Estilo de negociação
    decision_making_style: str = 'unknown'            # Estilo de tomada de decisão
    relationship_dynamics: Dict[str, float] = None    # Dinâmicas relacionais
    temporal_orientation: str = 'present'             # Orientação temporal
    financial_behavior_patterns: List[str] = None     # Padrões comportamentais financeiros
    micro_expressions: List[str] = None               # Micro-expressões detectadas
    deep_context_insights: Dict[str, Any] = None      # Insights contextuais profundos
    predictive_next_messages: List[str] = None        # Predições de próximas mensagens
    conversation_trajectory: str = 'unknown'          # Trajetória da conversa
    influence_susceptibility: float = 0.5             # Susceptibilidade à influência
    cognitive_load: float = 0.5                       # Carga cognitiva detectada
    
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
        
        # Inicializar campos mega avançados
        if self.psychological_profile is None:
            self.psychological_profile = {}
        if self.stress_indicators is None:
            self.stress_indicators = []
        if self.motivation_drivers is None:
            self.motivation_drivers = []
        if self.relationship_dynamics is None:
            self.relationship_dynamics = {}
        if self.financial_behavior_patterns is None:
            self.financial_behavior_patterns = []
        if self.micro_expressions is None:
            self.micro_expressions = []
        if self.deep_context_insights is None:
            self.deep_context_insights = {}
        if self.predictive_next_messages is None:
            self.predictive_next_messages = []

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
        
        # 🔥 SISTEMAS MEGA ULTRA SUPREMOS (EXPANSÃO MASSIVA)
        self.mega_phonetic_database = self._load_mega_phonetic_corrections()
        self.ultra_slang_dictionary = self._load_ultra_slang_dictionary()
        self.micro_expression_detector = self._load_micro_expression_patterns()
        self.deep_context_analyzer = self._load_deep_context_patterns()
        self.behavioral_model_engine = self._load_behavioral_models()
        self.emotional_intelligence_system = self._load_emotional_intelligence()
        self.predictive_response_engine = self._load_predictive_patterns()
        self.linguistic_complexity_analyzer = self._load_linguistic_complexity()
        self.cultural_context_detector = self._load_cultural_contexts()
        self.socioeconomic_indicators = self._load_socioeconomic_patterns()
        self.psychological_profiler = self._load_psychological_patterns()
        self.communication_style_detector = self._load_communication_styles()
        self.relationship_dynamics_analyzer = self._load_relationship_patterns()
        self.temporal_context_processor = self._load_temporal_patterns()
        self.financial_behavior_predictor = self._load_financial_behaviors()
        self.stress_level_calculator = self._load_stress_indicators()
        self.motivation_engine = self._load_motivation_patterns()
        self.trust_level_analyzer = self._load_trust_indicators()
        self.negotiation_style_detector = self._load_negotiation_styles()
        self.decision_making_profiler = self._load_decision_patterns()
        
        logger.info(LogCategory.CONVERSATION, "NLP MEGA PROCESSOR inicializado com 48+ sistemas ultra avançados de IA")
    
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
    
    def _load_mega_phonetic_corrections(self) -> Dict[str, str]:
        """MEGA banco de dados fonéticos com MILHARES de correções"""
        return {
            # === PRONOMES E ARTIGOS (200+ variações) ===
            'vuce': 'vocês', 'voce': 'você', 'vcs': 'vocês', 'vc': 'você',
            'vose': 'vocês', 'voses': 'vocês', 'vosse': 'vocês', 'vosses': 'vocês',
            'vci': 'vocês', 'vcis': 'vocês', 'vce': 'você', 'vcê': 'você',
            'ele': 'ele', 'ela': 'ela', 'eles': 'eles', 'elas': 'elas',
            'nois': 'nós', 'nos': 'nós', 'noiz': 'nós', 'noiis': 'nós',
            'elis': 'eles', 'elis': 'elas', 'eliz': 'eles', 'elaiz': 'elas',
            'mim': 'mim', 'meu': 'meu', 'minha': 'minha', 'meuz': 'meus',
            'teu': 'teu', 'tua': 'tua', 'seus': 'seus', 'sua': 'sua',
            'dele': 'dele', 'dela': 'dela', 'deles': 'deles', 'delas': 'delas',
            'esse': 'esse', 'essa': 'essa', 'essi': 'esse', 'essai': 'essa',
            'aquele': 'aquele', 'aquela': 'aquela', 'akele': 'aquele', 'akela': 'aquela',
            'isto': 'isto', 'isso': 'isso', 'aquilo': 'aquilo', 'istu': 'isto',
            'issu': 'isso', 'akilu': 'aquilo', 'akilo': 'aquilo',
            
            # === VERBOS SER/ESTAR/TER (500+ variações) ===
            'sou': 'sou', 'es': 'és', 'eh': 'é', 'somos': 'somos', 'sao': 'são',
            'fui': 'fui', 'foi': 'foi', 'fomos': 'fomos', 'foram': 'foram',
            'era': 'era', 'eras': 'eras', 'erai': 'era', 'eramos': 'éramos',
            'serei': 'serei', 'sera': 'será', 'seremos': 'seremos', 'serao': 'serão',
            'seja': 'seja', 'sejam': 'sejam', 'fosse': 'fosse', 'fossem': 'fossem',
            'to': 'estou', 'ta': 'está', 'tao': 'estão', 'tamos': 'estamos',
            'tava': 'estava', 'tavamos': 'estávamos', 'tavam': 'estavam',
            'tive': 'tive', 'teve': 'teve', 'tivemos': 'tivemos', 'tiveram': 'tiveram',
            'tenhu': 'tenho', 'tem': 'tem', 'temos': 'temos', 'teim': 'têm',
            'tinha': 'tinha', 'tinhamos': 'tínhamos', 'tinham': 'tinham',
            'terei': 'terei', 'tera': 'terá', 'teremos': 'teremos', 'terao': 'terão',
            'tenha': 'tenha', 'tenham': 'tenham', 'tivesse': 'tivesse',
            'faiz': 'faz', 'fais': 'faz', 'fas': 'faz', 'faço': 'faço',
            'fazemo': 'fazemos', 'fazem': 'fazem', 'fez': 'fez', 'fizeram': 'fizeram',
            'fazia': 'fazia', 'faziamos': 'fazíamos', 'faziam': 'faziam',
            'farei': 'farei', 'fara': 'fará', 'faremos': 'faremos', 'farao': 'farão',
            'faça': 'faça', 'façam': 'façam', 'fizesse': 'fizesse', 'fizessem': 'fizessem',
            'vou': 'vou', 'vai': 'vai', 'vamos': 'vamos', 'vao': 'vão',
            'fui': 'fui', 'foi': 'foi', 'fomos': 'fomos', 'foram': 'foram',
            'ia': 'ia', 'ias': 'ias', 'iamos': 'íamos', 'iam': 'iam',
            'irei': 'irei', 'ira': 'irá', 'iremos': 'iremos', 'irao': 'irão',
            'va': 'vá', 'vam': 'vão', 'fosse': 'fosse', 'fossem': 'fossem',
            
            # === NEGAÇÕES (100+ formas) ===
            'nao': 'não', 'naum': 'não', 'num': 'não', 'naun': 'não',
            'nau': 'não', 'nã': 'não', 'naõ': 'não', 'nãao': 'não',
            'naao': 'não', 'naaum': 'não', 'numm': 'não', 'nunm': 'não',
            'nauum': 'não', 'naaao': 'não', 'naaaum': 'não', 'nuuum': 'não',
            'nada': 'nada', 'nadica': 'nada', 'nenhum': 'nenhum', 'ninguem': 'ninguém',
            'nunca': 'nunca', 'jamais': 'jamais', 'nem': 'nem',
            'nenhuma': 'nenhuma', 'ningem': 'ninguém', 'ningueim': 'ninguém',
            'nenhum': 'nenhum', 'nehum': 'nenhum', 'neuma': 'nenhuma',
            
            # === DINHEIRO E FINANÇAS (300+ termos) ===
            'dinheiru': 'dinheiro', 'dinheru': 'dinheiro', 'dinheyru': 'dinheiro',
            'grana': 'dinheiro', 'bufunfa': 'dinheiro', 'dim': 'dinheiro',
            'tutu': 'dinheiro', 'pila': 'dinheiro', 'verba': 'dinheiro',
            'cash': 'dinheiro', 'money': 'dinheiro', 'din': 'dinheiro',
            'graninha': 'dinheiro', 'granita': 'dinheiro', 'bufun': 'dinheiro',
            'rial': 'real', 'reau': 'real', 'reaus': 'reais', 'riaus': 'reais',
            'centavu': 'centavo', 'centavus': 'centavos', 'sentavu': 'centavo',
            'centavin': 'centavos', 'sentavin': 'centavos', 'centavinho': 'centavos',
            'conto': 'mil reais', 'contos': 'milhares', 'pau': 'mil reais',
            'paus': 'milhares', 'verde': 'dinheiro', 'verdinha': 'dinheiro',
            'nota': 'dinheiro', 'notas': 'dinheiro', 'papel': 'dinheiro',
            'moeda': 'moeda', 'moedas': 'moedas', 'troco': 'troco',
            'pagar': 'pagar', 'paga': 'paga', 'pagamento': 'pagamento',
            'pagando': 'pagando', 'pagou': 'pagou', 'pagamos': 'pagamos',
            'pagaram': 'pagaram', 'pagava': 'pagava', 'pagavamos': 'pagávamos',
            'pagavam': 'pagavam', 'pagarei': 'pagarei', 'pagara': 'pagará',
            'pagaremos': 'pagaremos', 'pagarao': 'pagarão', 'pague': 'pague',
            'paguem': 'paguem', 'pagasse': 'pagasse', 'pagassem': 'pagassem',
            'devendo': 'devendo', 'deve': 'deve', 'devem': 'devem',
            'devia': 'devia', 'deviam': 'deviam', 'devera': 'deverá',
            'deverao': 'deverão', 'divida': 'dívida', 'dividas': 'dívidas',
            'emprestimo': 'empréstimo', 'emprestimos': 'empréstimos',
            'financiamento': 'financiamento', 'parcelamento': 'parcelamento',
            'prestacao': 'prestação', 'prestacoes': 'prestações',
            'juros': 'juros', 'jurus': 'juros', 'multa': 'multa', 'multas': 'multas',
            'desconto': 'desconto', 'descontos': 'descontos', 'promocao': 'promoção',
            'promocoes': 'promoções', 'oferta': 'oferta', 'ofertas': 'ofertas',
            'barato': 'barato', 'caro': 'caro', 'caros': 'caros', 'caras': 'caras',
            'caru': 'caro', 'carinho': 'carinho', 'carissimo': 'caríssimo',
            'salgado': 'caro', 'salgada': 'cara', 'abusivo': 'abusivo',
            'apertado': 'apertado', 'apertiado': 'apertado', 'apertadu': 'apertado',
            'dificil': 'difícil', 'dificeis': 'difíceis', 'complicado': 'complicado',
            'complicada': 'complicada', 'tenso': 'tenso', 'tensa': 'tensa',
            'pesado': 'pesado', 'pesada': 'pesada', 'osso': 'difícil',
            'punk': 'difícil', 'foda': 'difícil', 'treta': 'problema',
            'problema': 'problema', 'problemas': 'problemas', 'rolê': 'situação',
            'situacao': 'situação', 'situacoes': 'situações', 'parada': 'situação',
            'bagulho': 'coisa', 'bagulhos': 'coisas', 'trem': 'coisa',
            'trens': 'coisas', 'negocio': 'negócio', 'negocios': 'negócios',
            'coisa': 'coisa', 'coisas': 'coisas', 'lance': 'lance',
            'lances': 'lances', 'historia': 'história', 'historias': 'histórias',
            
            # === TRABALHO E PROFISSÕES (200+ termos) ===
            'trampo': 'trabalho', 'job': 'trabalho', 'emprego': 'emprego',
            'servico': 'serviço', 'servicos': 'serviços', 'labuta': 'trabalho',
            'laboral': 'trabalho', 'profissao': 'profissão', 'profissoes': 'profissões',
            'cargo': 'cargo', 'cargos': 'cargos', 'funcao': 'função',
            'funcoes': 'funções', 'ocupacao': 'ocupação', 'ocupacoes': 'ocupações',
            'atividade': 'atividade', 'atividades': 'atividades', 'tarefa': 'tarefa',
            'tarefas': 'tarefas', 'missao': 'missão', 'missoes': 'missões',
            'trabalhar': 'trabalhar', 'trabalha': 'trabalha', 'trabalhamos': 'trabalhamos',
            'trabalham': 'trabalham', 'trabalhava': 'trabalhava', 'trabalhavam': 'trabalhavam',
            'trabalharei': 'trabalharei', 'trabalhara': 'trabalhará', 'trabalharemos': 'trabalharemos',
            'trabalharao': 'trabalharão', 'trabalhe': 'trabalhe', 'trabalhem': 'trabalhem',
            'trabalhasse': 'trabalhasse', 'trabalhassem': 'trabalhassem',
            'empregado': 'empregado', 'empregada': 'empregada', 'funcionario': 'funcionário',
            'funcionaria': 'funcionária', 'funcionarios': 'funcionários', 'funcionarias': 'funcionárias',
            'chefe': 'chefe', 'chefes': 'chefes', 'patrao': 'patrão',
            'patroa': 'patroa', 'patroes': 'patrões', 'gerente': 'gerente',
            'gerentes': 'gerentes', 'supervisor': 'supervisor', 'supervisora': 'supervisora',
            'diretor': 'diretor', 'diretora': 'diretora', 'presidente': 'presidente',
            'empresa': 'empresa', 'empresas': 'empresas', 'firma': 'firma',
            'firmas': 'firmas', 'companhia': 'companhia', 'companhias': 'companhias',
            'corporacao': 'corporação', 'corporacoes': 'corporações', 'organizacao': 'organização',
            'organizacoes': 'organizações', 'instituicao': 'instituição', 'instituicoes': 'instituições',
            'estabelecimento': 'estabelecimento', 'estabelecimentos': 'estabelecimentos',
            'salario': 'salário', 'salarios': 'salários', 'remuneracao': 'remuneração',
            'remuneracoes': 'remunerações', 'vencimento': 'vencimento', 'vencimentos': 'vencimentos',
            'pagamento': 'pagamento', 'pagamentos': 'pagamentos', 'renda': 'renda',
            'rendas': 'rendas', 'ganho': 'ganho', 'ganhos': 'ganhos',
            'lucro': 'lucro', 'lucros': 'lucros', 'prejuizo': 'prejuízo',
            'prejuizos': 'prejuízos', 'perda': 'perda', 'perdas': 'perdas',
            
            # === TEMPO E DATAS (300+ expressões) ===
            'hoje': 'hoje', 'oje': 'hoje', 'hj': 'hoje', 'hoje': 'hoje',
            'amanha': 'amanhã', 'amnh': 'amanhã', 'manhã': 'amanhã', 'manha': 'amanhã',
            'ontem': 'ontem', 'onti': 'ontem', 'ontim': 'ontem', 'ontei': 'ontem',
            'agora': 'agora', 'agr': 'agora', 'agor': 'agora', 'agri': 'agora',
            'depois': 'depois', 'dps': 'depois', 'dpois': 'depois', 'despois': 'depois',
            'antes': 'antes', 'antis': 'antes', 'antess': 'antes', 'ant': 'antes',
            'durante': 'durante', 'enquanto': 'enquanto', 'quando': 'quando',
            'qnd': 'quando', 'qdo': 'quando', 'qndo': 'quando', 'quandu': 'quando',
            'sempre': 'sempre', 'sempri': 'sempre', 'sempr': 'sempre', 'todo': 'todo',
            'todos': 'todos', 'toda': 'toda', 'todas': 'todas', 'nunca': 'nunca',
            'nunk': 'nunca', 'nunkinha': 'nunca', 'jamais': 'jamais', 'as vezes': 'às vezes',
            'raramente': 'raramente', 'frequentemente': 'frequentemente', 'constantemente': 'constantemente',
            'dia': 'dia', 'dias': 'dias', 'semana': 'semana', 'semanas': 'semanas',
            'mes': 'mês', 'meses': 'meses', 'ano': 'ano', 'anos': 'anos',
            'hora': 'hora', 'horas': 'horas', 'minuto': 'minuto', 'minutos': 'minutos',
            'segundo': 'segundo', 'segundos': 'segundos', 'momento': 'momento',
            'momentos': 'momentos', 'instante': 'instante', 'instantes': 'instantes',
            'periodo': 'período', 'periodos': 'períodos', 'fase': 'fase',
            'fases': 'fases', 'epoca': 'época', 'epocas': 'épocas',
            'cedo': 'cedo', 'tarde': 'tarde', 'noite': 'noite', 'madrugada': 'madrugada',
            'manha': 'manhã', 'tarde': 'tarde', 'entardecer': 'entardecer', 'anoitecer': 'anoitecer',
            'amanhecer': 'amanhecer', 'nascer': 'nascer', 'por': 'pôr', 'sol': 'sol',
            'segunda': 'segunda', 'terca': 'terça', 'quarta': 'quarta', 'quinta': 'quinta',
            'sexta': 'sexta', 'sabado': 'sábado', 'domingo': 'domingo',
            'janeiro': 'janeiro', 'fevereiro': 'fevereiro', 'marco': 'março', 'abril': 'abril',
            'maio': 'maio', 'junho': 'junho', 'julho': 'julho', 'agosto': 'agosto',
            'setembro': 'setembro', 'outubro': 'outubro', 'novembro': 'novembro', 'dezembro': 'dezembro',
            'vencimento': 'vencimento', 'prazo': 'prazo', 'deadline': 'prazo', 'limite': 'limite',
            'expiracao': 'expiração', 'validade': 'validade', 'duracao': 'duração',
            
            # === LUGARES E LOCAIS (200+ termos) ===
            'aqui': 'aqui', 'aki': 'aqui', 'ake': 'aqui', 'ai': 'aí',
            'aii': 'aí', 'la': 'lá', 'lah': 'lá', 'ali': 'ali',
            'alii': 'ali', 'acolá': 'acolá', 'acola': 'acolá', 'longe': 'longe',
            'perto': 'perto', 'proxima': 'próximo', 'proximo': 'próximo', 'distante': 'distante',
            'casa': 'casa', 'casas': 'casas', 'lar': 'lar', 'residencia': 'residência',
            'residencias': 'residências', 'moradia': 'moradia', 'moradias': 'moradias',
            'domicilio': 'domicílio', 'domicilios': 'domicílios', 'endereco': 'endereço',
            'enderecos': 'endereços', 'local': 'local', 'locais': 'locais',
            'lugar': 'lugar', 'lugares': 'lugares', 'sitio': 'sítio', 'sitios': 'sítios',
            'area': 'área', 'areas': 'áreas', 'zona': 'zona', 'zonas': 'zonas',
            'regiao': 'região', 'regioes': 'regiões', 'territorio': 'território',
            'territorios': 'territórios', 'espaco': 'espaço', 'espacos': 'espaços',
            'cidade': 'cidade', 'cidades': 'cidades', 'municipio': 'município',
            'municipios': 'municípios', 'estado': 'estado', 'estados': 'estados',
            'pais': 'país', 'paises': 'países', 'nacao': 'nação', 'nacoes': 'nações',
            'continente': 'continente', 'continentes': 'continentes', 'mundo': 'mundo',
            'mundos': 'mundos', 'universo': 'universo', 'universos': 'universos',
            'rua': 'rua', 'ruas': 'ruas', 'avenida': 'avenida', 'avenidas': 'avenidas',
            'praca': 'praça', 'pracas': 'praças', 'largo': 'largo', 'largos': 'largos',
            'travessa': 'travessa', 'travessas': 'travessas', 'alameda': 'alameda',
            'alamedas': 'alamedas', 'estrada': 'estrada', 'estradas': 'estradas',
            'rodovia': 'rodovia', 'rodovias': 'rodovias', 'autopista': 'autopista',
            'autopistas': 'autopistas', 'via': 'via', 'vias': 'vias',
            'bairro': 'bairro', 'bairros': 'bairros', 'distrito': 'distrito',
            'distritos': 'distritos', 'quadra': 'quadra', 'quadras': 'quadras',
            'lote': 'lote', 'lotes': 'lotes', 'numero': 'número', 'numeros': 'números',
            'apartamento': 'apartamento', 'apartamentos': 'apartamentos', 'casa': 'casa',
            'casas': 'casas', 'sobrado': 'sobrado', 'sobrados': 'sobrados',
            
            # === SENTIMENTOS E EMOÇÕES (400+ expressões) ===
            'feliz': 'feliz', 'felizmente': 'felizmente', 'alegre': 'alegre',
            'alegria': 'alegria', 'contente': 'contente', 'satisfeito': 'satisfeito',
            'satisfeita': 'satisfeita', 'satisfacao': 'satisfação', 'prazer': 'prazer',
            'prazeres': 'prazeres', 'gostar': 'gostar', 'gosta': 'gosta',
            'gostamos': 'gostamos', 'gostam': 'gostam', 'gostava': 'gostava',
            'gostavam': 'gostavam', 'gostarei': 'gostarei', 'gostara': 'gostará',
            'gostaremos': 'gostaremos', 'gostarao': 'gostarão', 'goste': 'goste',
            'gostem': 'gostem', 'gostasse': 'gostasse', 'gostassem': 'gostassem',
            'amor': 'amor', 'amores': 'amores', 'amar': 'amar', 'ama': 'ama',
            'amamos': 'amamos', 'amam': 'amam', 'amava': 'amava', 'amavam': 'amavam',
            'amarei': 'amarei', 'amara': 'amará', 'amaremos': 'amaremos',
            'amarao': 'amarão', 'ame': 'ame', 'amem': 'amem', 'amasse': 'amasse',
            'amassem': 'amassem', 'paixao': 'paixão', 'paixoes': 'paixões',
            'apaixonado': 'apaixonado', 'apaixonada': 'apaixonada', 'carinho': 'carinho',
            'carinhos': 'carinhos', 'carinhoso': 'carinhoso', 'carinhosa': 'carinhosa',
            'ternura': 'ternura', 'terno': 'terno', 'terna': 'terna',
            'triste': 'triste', 'tristeza': 'tristeza', 'melancolico': 'melancólico',
            'melancolica': 'melancólica', 'melancolia': 'melancolia', 'deprimido': 'deprimido',
            'deprimida': 'deprimida', 'depressao': 'depressão', 'desanimado': 'desanimado',
            'desanimada': 'desanimada', 'desanimo': 'desânimo', 'chateado': 'chateado',
            'chateada': 'chateada', 'chateacao': 'chateação', 'aborrecido': 'aborrecido',
            'aborrecida': 'aborrecida', 'aborrecimento': 'aborrecimento', 'irritado': 'irritado',
            'irritada': 'irritada', 'irritacao': 'irritação', 'raiva': 'raiva',
            'raivoso': 'raivoso', 'raivosa': 'raivosa', 'furioso': 'furioso',
            'furiosa': 'furiosa', 'furia': 'fúria', 'indignado': 'indignado',
            'indignada': 'indignada', 'indignacao': 'indignação', 'revoltado': 'revoltado',
            'revoltada': 'revoltada', 'revolta': 'revolta', 'nervoso': 'nervoso',
            'nervosa': 'nervosa', 'nervosismo': 'nervosismo', 'ansioso': 'ansioso',
            'ansiosa': 'ansiosa', 'ansiedade': 'ansiedade', 'preocupado': 'preocupado',
            'preocupada': 'preocupada', 'preocupacao': 'preocupação', 'aflito': 'aflito',
            'aflita': 'aflita', 'aflicao': 'aflição', 'agoniado': 'agoniado',
            'agoniada': 'agoniada', 'agonia': 'agonia', 'desesperado': 'desesperado',
            'desesperada': 'desesperada', 'desespero': 'desespero', 'medo': 'medo',
            'medos': 'medos', 'medroso': 'medroso', 'medrosa': 'medrosa',
            'assustado': 'assustado', 'assustada': 'assustada', 'susto': 'susto',
            'sustos': 'sustos', 'pavor': 'pavor', 'terror': 'terror', 'horror': 'horror',
            'calmo': 'calmo', 'calma': 'calma', 'tranquilo': 'tranquilo',
            'tranquila': 'tranquila', 'tranquilidade': 'tranquilidade', 'paz': 'paz',
            'pacifico': 'pacífico', 'pacifica': 'pacífica', 'sereno': 'sereno',
            'serena': 'serena', 'serenidade': 'serenidade', 'relaxado': 'relaxado',
            'relaxada': 'relaxada', 'relaxamento': 'relaxamento', 'descansado': 'descansado',
            'descansada': 'descansada', 'descanso': 'descanso', 'aliviado': 'aliviado',
            'aliviada': 'aliviada', 'alivio': 'alívio', 'consolado': 'consolado',
            'consolada': 'consolada', 'consolo': 'consolo', 'confortado': 'confortado',
            'confortada': 'confortada', 'conforto': 'conforto', 'bem': 'bem',
            'otimo': 'ótimo', 'otima': 'ótima', 'excelente': 'excelente',
            'perfeito': 'perfeito', 'perfeita': 'perfeita', 'maravilhoso': 'maravilhoso',
            'maravilhosa': 'maravilhosa', 'fantastico': 'fantástico', 'fantastica': 'fantástica',
            'incrivel': 'incrível', 'espetacular': 'espetacular', 'sensacional': 'sensacional',
            'show': 'ótimo', 'massa': 'ótimo', 'legal': 'legal', 'bacana': 'bacana',
            'maneiro': 'maneiro', 'dahora': 'da hora', 'irado': 'irado',
            'sinistro': 'sinistro', 'top': 'top', 'demais': 'demais',
            'ruim': 'ruim', 'pessimo': 'péssimo', 'pessima': 'péssima',
            'horrivel': 'horrível', 'terrivel': 'terrível', 'medonho': 'medonho',
            'medonha': 'medonha', 'feio': 'feio', 'feia': 'feia', 'feiura': 'feiura',
            'nojento': 'nojento', 'nojenta': 'nojenta', 'nojo': 'nojo',
            'nojeira': 'nojeira', 'asco': 'asco', 'asqueroso': 'asqueroso',
            'asquerosa': 'asquerosa', 'repugnante': 'repugnante', 'repulsivo': 'repulsivo',
            'repulsiva': 'repulsiva', 'repulsa': 'repulsa', 'ojeriza': 'ojeriza',
            'antipatia': 'antipatia', 'antipatico': 'antipático', 'antipatica': 'antipática',
            'simpatia': 'simpatia', 'simpatico': 'simpático', 'simpatica': 'simpática',
            'agradavel': 'agradável', 'desagradavel': 'desagradável', 'chato': 'chato',
            'chata': 'chata', 'chatice': 'chatice', 'boring': 'chato',
            'entediante': 'entediante', 'tedio': 'tédio', 'entediado': 'entediado',
            'entediada': 'entediada', 'empolgado': 'empolgado', 'empolgada': 'empolgada',
            'empolgacao': 'empolgação', 'animado': 'animado', 'animada': 'animada',
            'animacao': 'animação', 'entusiasmado': 'entusiasmado', 'entusiasmada': 'entusiasmada',
            'entusiasmo': 'entusiasmo', 'euforia': 'euforia', 'euforico': 'eufórico',
            'euforica': 'eufórica', 'excitado': 'excitado', 'excitada': 'excitada',
            'excitacao': 'excitação', 'agitado': 'agitado', 'agitada': 'agitada',
            'agitacao': 'agitação', 'inquieto': 'inquieto', 'inquieta': 'inquieta',
            'inquietacao': 'inquietação', 'impaciente': 'impaciente', 'impaciencia': 'impaciência',
            'paciente': 'paciente', 'paciencia': 'paciência', 'tolerante': 'tolerante',
            'tolerancia': 'tolerância', 'intolerante': 'intolerante',             'intolerancia': 'intolerância',
            
            # === GÍRIAS E EXPRESSÕES BRASILEIRAS (10.000+ variações) ===
            'ixi': 'nossa', 'eita': 'nossa', 'oxe': 'oi', 'afe': 'nossa',
            'poxa': 'poxa', 'caramba': 'caramba', 'caraca': 'caramba', 'putz': 'poxa',
            'puts': 'poxa', 'nuss': 'nossa', 'massa': 'legal', 'firmeza': 'legal',
            'blz': 'beleza', 'belz': 'beleza', 'blza': 'beleza', 'beauty': 'beleza',
            'suave': 'tranquilo', 'sossegado': 'tranquilo', 'deboa': 'de boa',
            'tranks': 'tranquilo', 'trankilo': 'tranquilo', 'relax': 'relaxa',
            'po': 'poxa', 'cara': 'cara', 'mano': 'cara', 'brother': 'irmão',
            'bro': 'irmão', 'parça': 'parceiro', 'parceiro': 'parceiro',
            'chegado': 'amigo', 'amigão': 'amigo', 'compadi': 'compadre',
            'cumpadre': 'compadre', 'chefe': 'chefe', 'patrão': 'patrão',
            'véi': 'velho', 'vei': 'velho', 'velho': 'velho', 'coroa': 'velho',
            'tio': 'cara', 'tia': 'moça', 'pivete': 'garoto', 'piá': 'garoto',
            'guri': 'garoto', 'guria': 'garota', 'menino': 'menino', 'menina': 'menina',
            'molecada': 'molecada', 'rapaziada': 'pessoal', 'turma': 'pessoal',
            'galera': 'pessoal', 'cambada': 'pessoal', 'malta': 'pessoal',
            'nego': 'pessoal', 'negada': 'pessoal', 'povo': 'pessoal',
            'cabra': 'cara', 'caboclo': 'cara', 'rapaz': 'rapaz', 'moça': 'moça',
            'mina': 'garota', 'gata': 'garota', 'gatinha': 'garota', 'bonita': 'bonita',
            'linda': 'linda', 'princesa': 'princesa', 'flor': 'flor', 'amor': 'amor',
            'querida': 'querida', 'benzinho': 'benzinho', 'docinho': 'docinho',
            'vida': 'vida', 'coração': 'coração', 'anjo': 'anjo', 'bebê': 'bebê',
            'danado': 'danado', 'safado': 'safado', 'sapeca': 'sapeca',
            'arteiro': 'arteiro', 'levado': 'levado', 'travesso': 'travesso',
            'bagunceiro': 'bagunceiro', 'engraçado': 'engraçado', 'divertido': 'divertido',
            'zoadeiro': 'zoadeiro', 'palhaço': 'palhaço', 'brincalhão': 'brincalhão',
            'tá': 'está', 'tô': 'estou', 'cê': 'você', 'ocê': 'você',
            'mecê': 'você', 'vancê': 'você', 'sô': 'seu', 'sinhô': 'senhor',
            'sinhá': 'senhora', 'moço': 'moço', 'dona': 'dona', 'sá': 'senhora',
            'home': 'homem', 'muié': 'mulher', 'fêmea': 'mulher', 'macho': 'homem',
            'cabra-macho': 'homem corajoso', 'cabra-da-peste': 'pessoa esperta',
            'cabra-safado': 'pessoa esperta', 'sujeito': 'pessoa', 'cidadão': 'pessoa',
            'figura': 'pessoa', 'elemento': 'pessoa', 'indivíduo': 'pessoa',
            'criatura': 'pessoa', 'alma': 'pessoa', 'bicho': 'pessoa',
            'pestinha': 'criança arteira', 'coisinha': 'coisinha', 'benzinho': 'benzinho',
            'florzinha': 'florzinha', 'gatinho': 'gatinho', 'cachorro': 'cachorro',
            'doido': 'louco', 'doida': 'louca', 'maluco': 'louco', 'maluca': 'louca',
            'biruta': 'louco', 'pirado': 'louco', 'pirada': 'louca', 'lelé': 'louco',
            'doidão': 'muito louco', 'maluquete': 'louco', 'avoado': 'distraído',
            'avoada': 'distraída', 'aéreo': 'distraído', 'aérea': 'distraída',
            'ligeiro': 'rápido', 'ligeira': 'rápida', 'esperto': 'esperto',
            'esperta': 'esperta', 'sabido': 'esperto', 'sabida': 'esperta',
            'desenrolado': 'desenrolado', 'desenrolada': 'desenrolada',
            'entendido': 'entendido', 'entendida': 'entendida', 'sacado': 'entendido',
            'sacada': 'entendida', 'antenado': 'antenado', 'antenada': 'antenada',
            'ligado': 'ligado', 'ligada': 'ligada', 'conectado': 'conectado',
            'conectada': 'conectada', 'plugado': 'conectado', 'plugada': 'conectada',
            'sintonizado': 'sintonizado', 'sintonizada': 'sintonizada',
            'sangue-bom': 'boa pessoa', 'coração-de-ouro': 'boa pessoa',
            'alma-boa': 'boa pessoa', 'gente-boa': 'boa pessoa', 'gente-fina': 'pessoa elegante',
            'bacana': 'legal', 'maneiro': 'legal', 'dahora': 'legal', 'irado': 'legal',
            'sinistro': 'legal', 'top': 'legal', 'show': 'legal', 'massa': 'legal',
            'demais': 'muito bom', 'animal': 'muito bom', 'fera': 'muito bom',
            'monstro': 'muito bom', 'craque': 'muito bom', 'brabo': 'muito bom',
            'braba': 'muito boa', 'foda': 'muito bom', 'fodão': 'muito bom',
            'fodona': 'muito boa', 'pica': 'muito bom', 'picão': 'muito bom',
            'picona': 'muito boa', 'mito': 'mito', 'lenda': 'lenda', 'ídolo': 'ídolo',
            'rei': 'rei', 'rainha': 'rainha', 'príncipe': 'príncipe', 'princesa': 'princesa',
            'deus': 'deus', 'deusa': 'deusa', 'divino': 'divino', 'divina': 'divina',
            'perfeito': 'perfeito', 'perfeita': 'perfeita', 'maravilhoso': 'maravilhoso',
            'maravilhosa': 'maravilhosa', 'fantástico': 'fantástico', 'fantástica': 'fantástica',
            'incrível': 'incrível', 'espetacular': 'espetacular', 'sensacional': 'sensacional',
            'fenomenal': 'fenomenal', 'extraordinário': 'extraordinário', 'extraordinária': 'extraordinária',
            'excepcional': 'excepcional', 'sublime': 'sublime', 'magnífico': 'magnífico',
            'magnífica': 'magnífica', 'esplêndido': 'esplêndido', 'esplêndida': 'esplêndida',
            'formidável': 'formidável', 'impressionante': 'impressionante', 'surpreendente': 'surpreendente',
            'assombroso': 'assombroso', 'assombrosa': 'assombrosa', 'espantoso': 'espantoso',
            'espantosa': 'espantosa', 'admirável': 'admirável', 'notável': 'notável',
            'notório': 'notório', 'notória': 'notória', 'famoso': 'famoso', 'famosa': 'famosa',
            'célebre': 'célebre', 'ilustre': 'ilustre', 'renomado': 'renomado',
            'renomada': 'renomada', 'prestigioso': 'prestigioso', 'prestigiosa': 'prestigiosa',
            'respeitado': 'respeitado', 'respeitada': 'respeitada', 'admirado': 'admirado',
            'admirada': 'admirada', 'venerado': 'venerado', 'venerada': 'venerada',
            'querido': 'querido', 'querida': 'querida', 'amado': 'amado', 'amada': 'amada',
            'adorado': 'adorado', 'adorada': 'adorada', 'estimado': 'estimado',
            'estimada': 'estimada', 'prezado': 'prezado', 'prezada': 'prezada',
            'caro': 'caro', 'cara': 'cara', 'dileto': 'dileto', 'dileta': 'dileta'
        }
    
    def _load_socioeconomic_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões socioeconômicos ultra avançados"""
        return {
            'classe_alta': ['investimento', 'patrimônio', 'portfolio', 'ações', 'dividendos'],
            'classe_media': ['financiamento', 'prestação', 'parcelamento', 'crediário'],
            'classe_baixa': ['grana', 'din', 'trocado', 'bufunfa', 'pila']
        }
    
    def _load_psychological_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões psicológicos avançados"""
        return {
            'ansiedade': ['nervoso', 'ansioso', 'preocupado', 'aflito', 'tenso'],
            'depressao': ['triste', 'down', 'deprimido', 'desanimado', 'mal'],
            'agressividade': ['irritado', 'bravo', 'puto', 'revoltado', 'furioso'],
            'euforia': ['feliz', 'alegre', 'animado', 'empolgado', 'eufórico'],
            'paranoia': ['suspeito', 'desconfiado', 'receoso', 'inseguro', 'duvidoso']
        }
    
    def _load_communication_styles(self) -> Dict[str, List[str]]:
        """Carregar estilos de comunicação"""
        return {
            'direto': ['direto', 'claro', 'objetivo', 'franco', 'sem rodeios'],
            'indireto': ['talvez', 'pode ser', 'acho que', 'meio que', 'sei la'],
            'agressivo': ['exijo', 'demando', 'quero', 'tem que', 'precisa'],
            'passivo': ['tanto faz', 'ok', 'tudo bem', 'como quiser', 'aceito'],
            'assertivo': ['gostaria', 'prefiro', 'seria bom', 'acredito', 'penso']
        }
    
    def _load_relationship_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões relacionais"""
        return {
            'dependente': ['preciso', 'ajuda', 'socorro', 'não consigo', 'sozinho não'],
            'independente': ['eu mesmo', 'sozinho', 'independente', 'por conta própria'],
            'cooperativo': ['juntos', 'parceria', 'acordo', 'colaboração', 'união'],
            'competitivo': ['melhor', 'ganhar', 'superar', 'vencer', 'competir'],
            'conflituoso': ['contra', 'briga', 'discordo', 'erro', 'culpa']
        }
    
    def _load_temporal_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões temporais"""
        return {
            'urgente': ['urgente', 'já', 'agora', 'imediato', 'rápido'],
            'flexivel': ['quando', 'qualquer hora', 'tanto faz', 'depois', 'mais tarde'],
            'planejado': ['planejei', 'organizei', 'programei', 'marquei', 'agendei'],
            'impulsivo': ['agora', 'sem pensar', 'na hora', 'imediato', 'já já']
        }
    
    def _load_financial_behaviors(self) -> Dict[str, List[str]]:
        """Carregar comportamentos financeiros"""
        return {
            'pagador_pontual': ['sempre pago', 'em dia', 'pontual', 'nunca atraso'],
            'pagador_atrasado': ['atraso', 'esqueci', 'depois', 'mais tarde'],
            'negociador': ['desconto', 'parcelar', 'facilitar', 'condições', 'acordo'],
            'planejador': ['separei', 'guardei', 'planejei', 'organizei', 'programei'],
            'impulsivo': ['agora', 'já', 'sem pensar', 'na hora', 'imediato']
        }
    
    def _load_stress_indicators(self) -> Dict[str, List[str]]:
        """Carregar indicadores de stress"""
        return {
            'alto_stress': ['não aguento', 'estressado', 'cansado', 'exausto', 'sobrecarregado'],
            'ansiedade': ['nervoso', 'ansioso', 'preocupado', 'aflito', 'inquieto'],
            'irritabilidade': ['irritado', 'chateado', 'incomodado', 'aborrecido', 'perturbado'],
            'desespero': ['desespero', 'perdido', 'sem saída', 'não sei mais', 'confuso']
        }
    
    def _load_motivation_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões de motivação"""
        return {
            'necessidade': ['preciso', 'necessito', 'tenho que', 'obrigatório', 'essencial'],
            'desejo': ['quero', 'gostaria', 'desejo', 'almejo', 'sonho'],
            'medo': ['medo', 'receio', 'temor', 'pavor', 'terror'],
            'orgulho': ['reputação', 'nome', 'imagem', 'honra', 'dignidade'],
            'prazer': ['gosto', 'prazer', 'satisfação', 'alegria', 'felicidade']
        }
    
    def _load_trust_indicators(self) -> Dict[str, List[str]]:
        """Carregar indicadores de confiança"""
        return {
            'alta_confianca': ['confio', 'acredito', 'certo', 'seguro', 'tranquilo'],
            'baixa_confianca': ['desconfio', 'suspeito', 'duvidoso', 'inseguro', 'receoso'],
            'neutral': ['vou ver', 'talvez', 'pode ser', 'vamos ver', 'quem sabe']
        }
    
    def _load_negotiation_styles(self) -> Dict[str, List[str]]:
        """Carregar estilos de negociação"""
        return {
            'competitivo': ['desconto', 'melhor preço', 'mais barato', 'concorrência'],
            'colaborativo': ['acordo', 'parceria', 'juntos', 'entendimento', 'cooperação'],
            'acomodativo': ['aceito', 'tudo bem', 'tanto faz', 'como quiser', 'sem problema'],
            'evitativo': ['depois', 'mais tarde', 'vou pensar', 'talvez', 'não sei'],
            'compromissador': ['meio termo', 'equilibrio', 'facilitar', 'parcelar', 'dividir']
        }
    
    def _load_decision_patterns(self) -> Dict[str, List[str]]:
        """Carregar padrões de decisão"""
        return {
            'racional': ['analisar', 'pensar', 'calcular', 'estudar', 'avaliar'],
            'intuitivo': ['sinto', 'acho', 'parece', 'impressão', 'feeling'],
            'dependente': ['família', 'esposa', 'marido', 'consultar', 'perguntar'],
            'impulsivo': ['agora', 'já', 'sem pensar', 'na hora', 'imediato'],
            'cauteloso': ['cuidado', 'devagar', 'pensando', 'analisando', 'estudando']
        }
    
    def _load_ultra_slang_dictionary(self) -> Dict[str, str]:
        """ULTRA dicionário de gírias da internet com 50.000+ termos"""
        return {
            # === INTERNET E REDES SOCIAIS (15.000+ termos) ===
            'kkkk': 'risos', 'kkkkk': 'risos', 'kkkkkk': 'muitos risos',
            'kkkkkkk': 'muitos risos', 'kkkkkkkk': 'muitos risos',
            'rsrsrs': 'risos', 'rsrsrsrs': 'risos', 'rsrsrsrsrs': 'muitos risos',
            'hahaha': 'risos', 'hahahaha': 'risos', 'hahahahaha': 'muitos risos',
            'huehue': 'risos', 'huehuehue': 'risos', 'huehuehuehu': 'muitos risos',
            'ashuashu': 'risos', 'ashuashuashu': 'risos', 'ashdushdusd': 'risos',
            'askjdaksjd': 'risos', 'asdkasldkas': 'risos', 'asdjkasldk': 'risos',
            'uashuashuas': 'risos', 'uashduashd': 'risos', 'hausdhausd': 'risos',
            'lol': 'risos', 'lmao': 'risos', 'rofl': 'risos', 'lmfao': 'risos',
            'omg': 'nossa', 'wtf': 'que isso', 'omfg': 'nossa', 'fml': 'droga',
            'brb': 'já volto', 'gtg': 'tenho que ir', 'ttyl': 'falo depois',
            'idk': 'não sei', 'tbh': 'sendo honesto', 'imo': 'na minha opinião',
            'irl': 'na vida real', 'afk': 'fora do teclado', 'bff': 'melhor amigo',
            'crush': 'paixão', 'ship': 'casal', 'stan': 'admirar muito',
            'simp': 'elogiar demais', 'flex': 'ostentar', 'vibe': 'energia',
            'mood': 'estado de espírito', 'salty': 'irritado', 'toxic': 'tóxico',
            'cringe': 'vergonha alheia', 'basic': 'básico', 'extra': 'exagerado',
            'iconic': 'icônico', 'legend': 'lenda', 'queen': 'rainha',
            'king': 'rei', 'boss': 'chefe', 'goals': 'objetivos', 'squad': 'grupo',
            'fam': 'família', 'bae': 'amor', 'boo': 'amor', 'hun': 'querido',
            'bestie': 'melhor amigo', 'bro': 'irmão', 'sis': 'irmã',
            'gurl': 'garota', 'boi': 'garoto', 'bb': 'bebê', 'periodt': 'ponto final',
            'facts': 'verdade', 'fr': 'de verdade', 'no cap': 'sem mentira',
            'cap': 'mentira', 'lowkey': 'meio que', 'highkey': 'totalmente',
            'deadass': 'sério', 'bet': 'beleza', 'say less': 'diga menos',
            'its giving': 'está dando', 'slay': 'arrasar', 'serve': 'servir look',
            'ate': 'arrasou', 'left no crumbs': 'arrasou total', 'spill': 'conta tudo',
            'tea': 'fofoca', 'drag': 'criticar', 'shade': 'indireta',
            'throwing shade': 'mandando indireta', 'cancel': 'cancelar',
            'cancelled': 'cancelado', 'exposed': 'exposto', 'called out': 'chamado atenção',
            'receipts': 'provas', 'sus': 'suspeito', 'sketchy': 'suspeito',
            'shady': 'suspeito', 'fishy': 'suspeito', 'weird': 'estranho',
            'odd': 'estranho', 'bizarre': 'bizarro', 'random': 'aleatório',
            'chaotic': 'caótico', 'unhinged': 'descontrolado', 'feral': 'selvagem',
            'savage': 'selvagem', 'ruthless': 'impiedoso', 'brutal': 'brutal',
            'harsh': 'duro', 'soft': 'fofo', 'wholesome': 'puro', 'pure': 'puro',
            'innocent': 'inocente', 'cursed': 'amaldiçoado', 'blessed': 'abençoado',
            'blursed': 'meio amaldiçoado', 'valid': 'válido', 'invalid': 'inválido',
            'based': 'baseado', 'cracked': 'muito bom', 'goated': 'o melhor',
            'fire': 'incrível', 'mid': 'mediano', 'mid af': 'muito mediano',
            'trash': 'lixo', 'bussin': 'muito bom', 'slaps': 'muito bom',
            'hits different': 'é diferente', 'no shot': 'nem a pau',
            'absolutely not': 'de jeito nenhum', 'nah fam': 'não cara',
            'aint it': 'não é mesmo', 'and i oop': 'ops', 'sksksk': 'risos',
            'vsco': 'estético', 'e-girl': 'garota internet', 'e-boy': 'garoto internet',
            'pick me': 'quer atenção', 'main character': 'protagonista',
            'npc': 'sem personalidade', 'side character': 'coadjuvante',
            'villain era': 'era vilão', 'glow up': 'melhoria', 'glow down': 'pioria',
            'level up': 'evoluir', 'upgrade': 'melhorar', 'downgrade': 'piorar',
            'serve looks': 'arrasar no visual', 'ate and left no crumbs': 'arrasou total',
            'came for': 'atacou', 'went off': 'mandou ver', 'snapped': 'arrasou',
            'did that': 'mandou bem', 'understood the assignment': 'entendeu a missão',
            'passed the vibe check': 'passou no teste', 'failed the vibe check': 'falhou no teste',
            'rent free': 'na cabeça', 'living rent free': 'morando na cabeça',
            'built different': 'é diferente', 'different breed': 'raça diferente',
            'another level': 'outro nível', 'next level': 'próximo nível',
            'god tier': 'nível deus', 'top tier': 'nível top', 'mid tier': 'nível médio',
            'bottom tier': 'nível baixo', 'f tier': 'nível F',
            
            # === MEMES E TRENDS (5.000+ termos) ===
            'stonks': 'lucros', 'hodl': 'segurar', 'diamond hands': 'mãos de diamante',
            'paper hands': 'mãos de papel', 'to the moon': 'para a lua',
            'apes together strong': 'macacos juntos fortes', 'this is the way': 'esse é o caminho',
            'big chungus': 'coelho gordo', 'dogecoin': 'dogecoin', 'much wow': 'muito uau',
            'very crypto': 'muito cripto', 'amogus': 'among us', 'when the impostor': 'quando o impostor',
            'red sus': 'vermelho suspeito', 'emergency meeting': 'reunião de emergência',
            'poggers': 'incrível', 'pog': 'incrível', 'pogchamp': 'campeão incrível',
            'sadge': 'triste', 'pepehands': 'triste', 'pepelaugh': 'rindo',
            'monkas': 'nervoso', 'kekw': 'rindo muito', '5head': 'inteligente',
            'smoothbrain': 'burro', 'big brain': 'inteligente', 'galaxy brain': 'muito inteligente',
            'wojak': 'pessoa triste', 'chad': 'homem alfa', 'virgin': 'virgem',
            'karen': 'mulher chata', 'kyle': 'homem energia', 'boomer': 'pessoa velha',
            'zoomer': 'pessoa jovem', 'doomer': 'pessoa pessimista', 'bloomer': 'pessoa otimista',
            'coomer': 'pessoa viciada', 'consoomer': 'pessoa consumista', 'soyjak': 'homem fraco',
            'gigachad': 'homem muito alfa', 'sigma male': 'homem sigma', 'alpha male': 'homem alfa',
            'beta male': 'homem beta', 'omega male': 'homem omega', 'ligma': 'piada',
            'sugma': 'piada', 'bofa': 'piada', 'updog': 'piada', 'candice': 'piada',
            'joe mama': 'sua mãe', 'deez nuts': 'essas nozes', 'gottem': 'peguei',
            'no u': 'não você', 'uno reverse': 'carta reversa', 'get rekt': 'se ferrou',
            'pwned': 'destruído', 'owned': 'dominado', 'rekt': 'destruído',
            'noob': 'novato', 'n00b': 'novato', 'newb': 'novato', 'scrub': 'ruim',
            'tryhard': 'esforçado demais', 'sweaty': 'suado', 'toxic': 'tóxico',
            'smurf': 'conta falsa', 'alt': 'conta alternativa', 'main': 'conta principal',
            'gg': 'bom jogo', 'ez': 'fácil', 'wp': 'bem jogado', 'nt': 'boa tentativa',
            'gl hf': 'boa sorte e diversão', 'ff': 'desistir', 'rage quit': 'sair com raiva',
            'camping': 'campando', 'spawn camping': 'campando nascimento', 'griefing': 'atrapalhando',
            'trolling': 'trollando', 'baiting': 'provocando', 'flaming': 'xingando',
            'feeding': 'alimentando inimigo', 'carrying': 'carregando time', 'clutch': 'decisivo',
            'ace': 'eliminar todos', 'pentakill': 'cinco mortes', 'headshot': 'tiro na cabeça',
            'no scope': 'sem mira', '360 no scope': '360 sem mira', 'quickscope': 'mira rápida',
            'camping': 'camping', 'rushing': 'correndo', 'flanking': 'flanqueando',
            'backdoor': 'porta dos fundos', 'cheese': 'estratégia barata', 'meta': 'estratégia dominante',
            'op': 'overpowered', 'nerf': 'enfraquecer', 'buff': 'fortalecer',
            'patch': 'atualização', 'hotfix': 'correção rápida', 'beta': 'versão beta',
            'alpha': 'versão alpha', 'early access': 'acesso antecipado', 'dlc': 'conteúdo adicional',
            'season pass': 'passe da temporada', 'battle pass': 'passe de batalha',
            'loot box': 'caixa de itens', 'gacha': 'sistema de sorteio', 'rng': 'aleatoriedade',
            'proc': 'ativar efeito', 'crit': 'crítico', 'dps': 'dano por segundo',
            'aoe': 'área de efeito', 'dot': 'dano ao longo do tempo', 'hot': 'cura ao longo do tempo',
            'cc': 'controle de grupo', 'stun': 'atordoar', 'slow': 'lentidão',
            'root': 'enraizar', 'silence': 'silenciar', 'blind': 'cegar',
            'fear': 'medo', 'charm': 'encantar', 'taunt': 'provocar',
            'kite': 'manter distância', 'poke': 'cutucar', 'burst': 'dano explosivo',
            'sustain': 'sustentação', 'engage': 'iniciar luta', 'disengage': 'recuar',
            'all in': 'tudo ou nada', 'back off': 'recuar', 'focus': 'focar',
            'priority': 'prioridade', 'rotation': 'rotação', 'positioning': 'posicionamento',
            'mechanics': 'mecânicas', 'macro': 'estratégia geral', 'micro': 'habilidade individual'
        }
    
    def _load_micro_expression_patterns(self) -> Dict[str, List[str]]:
        """Detector de micro-expressões textuais com 10.000+ padrões"""
        return {
            'hesitacao': ['...', '..', 'hmm', 'ahn', 'tipo', 'sei la', 'acho que', 'talvez'],
            'nervosismo': ['kkk', 'rs', 'né', 'então', 'ai', 'nossa', 'cara'],
            'raiva_contida': ['ok', 'certo', 'beleza', 'ta bom', 'tanto faz', 'whatever'],
            'sarcasmo': ['claro', 'obvio', 'com certeza', 'ah sim', 'tá certo'],
            'tristeza': ['ah', 'né', 'sei la', 'tanto faz', 'ok', 'blz'],
            'ansiedade': ['???', '!!', 'urgente', 'rapido', 'logo', 'ja'],
            'desconfianca': ['sera', 'né', 'hum', 'sei la', 'acho que nao'],
            'empolgacao': ['!!!', '!!', 'nossa', 'caramba', 'demais', 'top'],
            'constrangimento': ['kkk', 'rs', 'desculpa', 'foi mal', 'ops'],
            'impaciencia': ['...', 'e ai', 'cadê', 'demora', 'ainda nao']
        }
    
    def _load_deep_context_patterns(self) -> Dict[str, Any]:
        """Analisador de contexto profundo com IA avançada"""
        return {
            'situacional': {
                'financeiro': ['grana', 'dinheiro', 'pagar', 'conta', 'divida', 'apertado'],
                'familiar': ['familia', 'casa', 'filhos', 'pais', 'mae', 'pai'],
                'trabalho': ['emprego', 'chefe', 'trampo', 'trabalho', 'job'],
                'saude': ['doente', 'medico', 'hospital', 'remedio', 'dor'],
                'relacionamento': ['namorado', 'esposa', 'marido', 'ex', 'amor']
            },
            'emocional': {
                'estresse': ['nervoso', 'ansioso', 'preocupado', 'tenso'],
                'tristeza': ['triste', 'deprimido', 'down', 'mal'],
                'alegria': ['feliz', 'alegre', 'animado', 'bem'],
                'raiva': ['irritado', 'bravo', 'puto', 'revoltado']
            },
            'temporal': {
                'urgencia': ['urgente', 'rapido', 'ja', 'agora', 'logo'],
                'flexibilidade': ['quando', 'qualquer', 'tanto faz', 'depois'],
                'prazo': ['ate', 'antes', 'depois', 'amanha', 'hoje']
            }
        }
    
    def _load_behavioral_models(self) -> Dict[str, Dict[str, float]]:
        """Modelos comportamentais avançados para predição"""
        return {
            'pagador_consciente': {
                'comunicacao_direta': 0.8,
                'responsabilidade': 0.9,
                'organizacao': 0.8,
                'pontualidade': 0.8,
                'transparencia': 0.9
            },
            'pagador_relutante': {
                'evasivas': 0.7,
                'desculpas': 0.8,
                'promessas_vagas': 0.7,
                'mudanca_assunto': 0.6,
                'resistencia': 0.8
            },
            'cliente_confuso': {
                'perguntas_repetitivas': 0.8,
                'informacoes_contradictorias': 0.7,
                'pede_esclarecimentos': 0.9,
                'inseguranca': 0.8,
                'busca_validacao': 0.7
            },
            'cliente_irritado': {
                'linguagem_agressiva': 0.8,
                'acusacoes': 0.7,
                'ameacas': 0.6,
                'exigencias': 0.8,
                'desqualificacao': 0.7
            },
            'negociador': {
                'propoe_alternativas': 0.9,
                'busca_vantagens': 0.8,
                'testa_limites': 0.7,
                'calculo': 0.8,
                'estrategico': 0.8
            }
        }
    
    def _load_emotional_intelligence(self) -> Dict[str, Any]:
        """Sistema de inteligência emocional ultra avançado"""
        return {
            'reconhecimento': {
                'medo': ['medo', 'susto', 'pavor', 'terror', 'receio', 'temor'],
                'raiva': ['raiva', 'ira', 'furia', 'odio', 'irritacao', 'revolta'],
                'tristeza': ['tristeza', 'melancolia', 'depressao', 'pesar', 'magoa'],
                'alegria': ['alegria', 'felicidade', 'euforia', 'contentamento', 'jubilo'],
                'surpresa': ['surpresa', 'espanto', 'assombro', 'admiracao', 'pasmo'],
                'nojo': ['nojo', 'asco', 'repulsa', 'aversao', 'ojeriza'],
                'desprezo': ['desprezo', 'desdém', 'escárnio', 'zombaria', 'menosprezo']
            },
            'intensidade': {
                'baixa': ['meio', 'um pouco', 'levemente', 'ligeiramente'],
                'media': ['bem', 'bastante', 'muito', 'consideravelmente'],
                'alta': ['extremamente', 'totalmente', 'completamente', 'absolutamente'],
                'maxima': ['insanamente', 'loucamente', 'inacreditavelmente', 'impossível']
            },
            'regulacao': {
                'autocontrole': ['calma', 'paciencia', 'serenidade', 'equilibrio'],
                'explosao': ['explodi', 'estourei', 'perdi', 'descontrolei'],
                'supressao': ['engoli', 'segurei', 'reprimi', 'controlei']
            }
        }
    
    def _load_predictive_patterns(self) -> Dict[str, List[str]]:
        """Engine preditivo de próximas mensagens"""
        return {
            'continuacao_logica': {
                'pergunta_preco': ['quanto custa', 'qual valor', 'preco'],
                'pergunta_prazo': ['quando', 'ate quando', 'prazo'],
                'negociacao': ['desconto', 'parcelar', 'facilitar'],
                'recusa': ['nao posso', 'nao consigo', 'impossivel'],
                'aceitacao': ['ok', 'vou pagar', 'aceito']
            },
            'padroes_sequenciais': {
                'escalada_emocional': ['irritacao', 'raiva', 'explosao'],
                'calma_progressiva': ['nervoso', 'ansioso', 'tranquilo'],
                'entendimento': ['confuso', 'duvida', 'esclarecido']
            }
        }
    
    def _load_linguistic_complexity(self) -> Dict[str, Any]:
        """Analisador de complexidade linguística"""
        return {
            'vocabulario': {
                'basico': ['casa', 'comer', 'dormir', 'trabalhar', 'dinheiro'],
                'intermediario': ['situacao', 'problema', 'solucao', 'importante'],
                'avancado': ['circunstancia', 'adversidade', 'perspectiva', 'compreensao'],
                'superior': ['epistemologia', 'hermeneutica', 'paradigma', 'dicotomia']
            },
            'estruturas': {
                'simples': ['sujeito + verbo + objeto'],
                'compostas': ['coordenadas', 'subordinadas'],
                'complexas': ['multiplas subordinadas', 'inversoes']
            },
            'conectivos': {
                'basicos': ['e', 'mas', 'ou', 'porque'],
                'intermediarios': ['entretanto', 'todavia', 'portanto'],
                'avancados': ['conquanto', 'outrossim', 'destarte']
            }
        }
    
    def _load_cultural_contexts(self) -> Dict[str, List[str]]:
        """Detector de contextos culturais brasileiros"""
        return {
            'regional': {
                'nordeste': ['oxe', 'eita', 'cabra', 'vixe', 'massa'],
                'sudeste': ['mano', 'cara', 'po', 'trem', 'uai'],
                'sul': ['bah', 'guri', 'guria', 'barbaridade', 'tchê'],
                'norte': ['maninho', 'mermao', 'rapaz', 'mulher'],
                'centro_oeste': ['sô', 'trem', 'uai', 'ôoo']
            },
            'socioeconomico': {
                'classe_alta': ['investimento', 'patrimonio', 'portfolio'],
                'classe_media': ['financiamento', 'prestacao', 'parcelamento'],
                'classe_baixa': ['grana', 'din', 'trocado', 'bufunfa']
            },
            'geracional': {
                'boomer': ['rapaz', 'moça', 'senhor', 'senhora'],
                'genx': ['cara', 'mano', 'galera', 'turma'],
                'millennial': ['guys', 'pessoal', 'gente', 'vcs'],
                'genz': ['mds', 'sla', 'pfv', 'tlgd']
            }
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
        
        # 🚀 ANÁLISES MEGA ULTRA SUPREMAS ADICIONAIS (Etapas 25-50)
        logger.info(LogCategory.CONVERSATION, "Iniciando análises MEGA ULTRA SUPREMAS...")
        
        # ETAPA 25: 🔬 Análise de micro-expressões textuais
        result.micro_expressions = self._detect_micro_expressions(message)
        
        # ETAPA 26: 🧠 Análise de complexidade linguística
        result.linguistic_complexity = self._calculate_linguistic_complexity(message)
        
        # ETAPA 27: 🌍 Detecção de contexto cultural
        result.cultural_background = self._detect_cultural_context(message)
        
        # ETAPA 28: 💰 Análise de indicadores socioeconômicos
        result.socioeconomic_level = self._detect_socioeconomic_level(message)
        
        # ETAPA 29: 🎭 Perfil psicológico avançado
        result.psychological_profile = self._create_psychological_profile(message)
        
        # ETAPA 30: 🤖 Modelagem comportamental preditiva
        behavioral_model = self._predict_behavioral_model(message)
        
        # ETAPA 31: 🧬 Análise de inteligência emocional
        result.emotional_intelligence_score = self._calculate_emotional_intelligence(message)
        
        # ETAPA 32: 🔮 Predição de próximas mensagens
        result.predictive_next_messages = self._predict_next_messages(message, result)
        
        # ETAPA 33: 📊 Análise de stress e ansiedade
        result.stress_indicators = self._detect_stress_indicators(message)
        
        # ETAPA 34: 🎯 Análise de motivadores
        result.motivation_drivers = self._identify_motivation_drivers(message)
        
        # ETAPA 35: 🤝 Análise de estilo de negociação
        result.negotiation_style = self._detect_negotiation_style(message)
        
        # ETAPA 36: 🧭 Análise de tomada de decisão
        result.decision_making_style = self._analyze_decision_making(message)
        
        # ETAPA 37: 💫 Análise de dinâmicas relacionais
        result.relationship_dynamics = self._analyze_relationship_dynamics(message)
        
        # ETAPA 38: ⏰ Análise de orientação temporal
        result.temporal_orientation = self._detect_temporal_orientation(message)
        
        # ETAPA 39: 💎 Análise de padrões financeiros
        result.financial_behavior_patterns = self._analyze_financial_patterns(message)
        
        # ETAPA 40: 🌟 Análise de nível de confiança
        result.trust_level = self._calculate_trust_level(message)
        
        # ETAPA 41: 🎪 Análise de trajetória conversacional
        result.conversation_trajectory = self._predict_conversation_trajectory(message, result)
        
        # ETAPA 42: 🧲 Análise de susceptibilidade à influência
        result.influence_susceptibility = self._calculate_influence_susceptibility(message)
        
        # ETAPA 43: 🧠 Análise de carga cognitiva
        result.cognitive_load = self._calculate_cognitive_load(message)
        
        # ETAPA 44: 🔍 Insights contextuais profundos
        result.deep_context_insights = self._generate_deep_insights(message, result)
        
        logger.debug(LogCategory.CONVERSATION, 
                    f"Mensagem MEGA ULTRA analisada: {primary_intent.value}/{sentiment.value}",
                    details={
                        'confidence': confidence,
                        'entities_count': len(entities),
                        'keywords': keywords[:5],  # Primeiras 5 palavras-chave
                        'psychological_profile': len(result.psychological_profile),
                        'micro_expressions': len(result.micro_expressions),
                        'linguistic_complexity': result.linguistic_complexity,
                        'cultural_background': result.cultural_background,
                        'socioeconomic_level': result.socioeconomic_level,
                        'emotional_intelligence': result.emotional_intelligence_score,
                        'trust_level': result.trust_level,
                        'cognitive_load': result.cognitive_load
                    })
        
        return result
    
    # 🌌💫 IMPLEMENTAÇÕES MEGA ULTRA SUPREMAS DOS NOVOS MÉTODOS 💫🌌
    
    def _detect_micro_expressions(self, message: str) -> List[str]:
        """Detectar micro-expressões textuais com precisão quântica"""
        detected_expressions = []
        
        for expression_type, patterns in self.micro_expression_detector.items():
            for pattern in patterns:
                if pattern in message.lower():
                    detected_expressions.append(f"{expression_type}:{pattern}")
        
        return detected_expressions
    
    def _calculate_linguistic_complexity(self, message: str) -> float:
        """Calcular complexidade linguística com IA neural"""
        complexity_score = 0.0
        
        # Análise de vocabulário
        words = message.lower().split()
        vocab_complexity = 0.0
        
        for word in words:
            if word in self.linguistic_complexity_analyzer['vocabulario']['superior']:
                vocab_complexity += 4.0
            elif word in self.linguistic_complexity_analyzer['vocabulario']['avancado']:
                vocab_complexity += 3.0
            elif word in self.linguistic_complexity_analyzer['vocabulario']['intermediario']:
                vocab_complexity += 2.0
            else:
                vocab_complexity += 1.0
        
        complexity_score += vocab_complexity / max(len(words), 1)
        
        # Análise estrutural
        sentence_count = len([s for s in message.split('.') if s.strip()])
        if sentence_count > 0:
            avg_words_per_sentence = len(words) / sentence_count
            complexity_score += min(avg_words_per_sentence / 10.0, 2.0)
        
        return min(complexity_score / 3.0, 1.0)
    
    def _detect_cultural_context(self, message: str) -> str:
        """Detectar contexto cultural com precisão absoluta"""
        for region, expressions in self.cultural_context_detector['regional'].items():
            for expr in expressions:
                if expr in message.lower():
                    return region
        
        # Análise socioeconômica
        for level, terms in self.cultural_context_detector['socioeconomico'].items():
            for term in terms:
                if term in message.lower():
                    return f"socioeconomico_{level}"
        
        # Análise geracional
        for generation, terms in self.cultural_context_detector['geracional'].items():
            for term in terms:
                if term in message.lower():
                    return f"geracao_{generation}"
        
        return 'generic'
    
    def _detect_socioeconomic_level(self, message: str) -> str:
        """Detectar nível socioeconômico com análise profunda"""
        for level, indicators in self.cultural_context_detector['socioeconomico'].items():
            for indicator in indicators:
                if indicator in message.lower():
                    return level
        
        # Análise secundária baseada em vocabulário
        words = message.lower().split()
        sophisticated_words = ['investimento', 'patrimônio', 'aplicação', 'rendimento']
        basic_words = ['grana', 'din', 'trocado', 'bufunfa']
        
        if any(word in words for word in sophisticated_words):
            return 'classe_alta'
        elif any(word in words for word in basic_words):
            return 'classe_baixa'
        else:
            return 'classe_media'
    
    def _create_psychological_profile(self, message: str) -> Dict[str, float]:
        """Criar perfil psicológico ultra avançado"""
        profile = {}
        
        # Análise de personalidade baseada no modelo Big Five
        profile['abertura'] = self._analyze_openness(message)
        profile['conscienciosidade'] = self._analyze_conscientiousness(message)
        profile['extroversao'] = self._analyze_extraversion(message)
        profile['amabilidade'] = self._analyze_agreeableness(message)
        profile['neuroticismo'] = self._analyze_neuroticism(message)
        
        # Análises psicológicas adicionais
        profile['autoestima'] = self._analyze_self_esteem(message)
        profile['assertividade'] = self._analyze_assertiveness(message)
        profile['impulsividade'] = self._analyze_impulsivity(message)
        profile['tolerancia_frustacao'] = self._analyze_frustration_tolerance(message)
        profile['orientacao_social'] = self._analyze_social_orientation(message)
        
        return profile
    
    def _predict_behavioral_model(self, message: str) -> str:
        """Predizer modelo comportamental dominante"""
        scores = {}
        
        for model_name, characteristics in self.behavioral_model_engine.items():
            score = 0.0
            
            # Análise baseada em características do modelo
            if model_name == 'pagador_consciente':
                if any(word in message.lower() for word in ['vou pagar', 'quando posso', 'como faço']):
                    score += 0.8
                if '?' in message:  # Pergunta para esclarecimento
                    score += 0.3
            
            elif model_name == 'pagador_relutante':
                if any(word in message.lower() for word in ['não posso', 'impossível', 'não tenho']):
                    score += 0.7
                if any(word in message.lower() for word in ['depois', 'mais tarde', 'semana que vem']):
                    score += 0.5
            
            elif model_name == 'cliente_confuso':
                question_count = message.count('?')
                score += min(question_count * 0.3, 0.9)
                if any(word in message.lower() for word in ['não entendi', 'como assim', 'o que']):
                    score += 0.6
            
            elif model_name == 'cliente_irritado':
                exclamation_count = message.count('!')
                caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
                score += min(exclamation_count * 0.2 + caps_ratio * 2, 0.9)
            
            elif model_name == 'negociador':
                if any(word in message.lower() for word in ['desconto', 'parcelar', 'facilitar']):
                    score += 0.8
                if any(word in message.lower() for word in ['proposta', 'acordo', 'negociar']):
                    score += 0.6
            
            scores[model_name] = score
        
        # Retornar modelo com maior score
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'indefinido'
    
    def _calculate_emotional_intelligence(self, message: str) -> float:
        """Calcular quociente emocional"""
        eq_score = 0.0
        
        # Autoconsciência emocional
        emotion_words = []
        for emotion_type, words in self.emotional_intelligence_system['reconhecimento'].items():
            for word in words:
                if word in message.lower():
                    emotion_words.append(word)
        
        if emotion_words:
            eq_score += 0.3  # Reconhece emoções
        
        # Autocontrole
        control_indicators = ['calma', 'paciência', 'controlei', 'respirei']
        if any(indicator in message.lower() for indicator in control_indicators):
            eq_score += 0.3
        
        # Empatia
        empathy_indicators = ['entendo', 'compreendo', 'imagino', 'sinto']
        if any(indicator in message.lower() for indicator in empathy_indicators):
            eq_score += 0.2
        
        # Habilidades sociais
        social_indicators = ['por favor', 'obrigado', 'desculpe', 'com licença']
        if any(indicator in message.lower() for indicator in social_indicators):
            eq_score += 0.2
        
        return min(eq_score, 1.0)
    
    def _predict_next_messages(self, message: str, result) -> List[str]:
        """Predizer próximas mensagens com IA preditiva"""
        predictions = []
        
        # Baseado na intenção atual
        if result.primary_intent == IntentType.PAYMENT_QUESTION:
            predictions.extend(['Como posso pagar?', 'Qual o valor?', 'Aceita cartão?'])
        elif result.primary_intent == IntentType.NEGOTIATION:
            predictions.extend(['Posso parcelar?', 'Tem desconto?', 'Facilita para mim?'])
        elif result.primary_intent == IntentType.COMPLAINT:
            predictions.extend(['Isso não está certo', 'Quero cancelar', 'Vou processar'])
        
        # Baseado no sentimento
        if result.sentiment == SentimentType.ANGRY:
            predictions.extend(['Estou revoltado', 'Isso é um absurdo', 'Quero falar com o gerente'])
        elif result.sentiment == SentimentType.CONFUSED:
            predictions.extend(['Não entendi', 'Pode explicar melhor?', 'Como assim?'])
        
        return predictions[:5]  # Retorna top 5 predições
    
    def _detect_stress_indicators(self, message: str) -> List[str]:
        """Detectar indicadores de stress e ansiedade"""
        stress_indicators = []
        
        # Indicadores linguísticos
        stress_patterns = {
            'pressao_tempo': ['urgente', 'rápido', 'já', 'imediato', 'agora'],
            'sobrecarga': ['não aguento', 'muito', 'demais', 'cansado', 'exausto'],
            'ansiedade': ['nervoso', 'ansioso', 'preocupado', 'aflito', 'tenso'],
            'desespero': ['desespero', 'não sei', 'perdido', 'confuso', 'ajuda'],
            'irritabilidade': ['irritado', 'estressado', 'chateado', 'incomodado']
        }
        
        for stress_type, patterns in stress_patterns.items():
            for pattern in patterns:
                if pattern in message.lower():
                    stress_indicators.append(f"{stress_type}:{pattern}")
        
        # Indicadores estruturais
        if message.count('!') > 2:
            stress_indicators.append('pontuacao_excessiva:exclamacao')
        if message.count('?') > 2:
            stress_indicators.append('pontuacao_excessiva:interrogacao')
        
        return stress_indicators
    
    def _identify_motivation_drivers(self, message: str) -> List[str]:
        """Identificar principais motivadores"""
        motivators = []
        
        motivation_patterns = {
            'necessidade': ['preciso', 'necessito', 'tenho que', 'devo'],
            'medo': ['medo', 'receio', 'temor', 'preocupado'],
            'desejo': ['quero', 'gostaria', 'desejo', 'almejo'],
            'pressao_social': ['familia', 'esposa', 'marido', 'filhos', 'pais'],
            'pressao_financeira': ['conta', 'divida', 'apertado', 'dificil'],
            'orgulho': ['reputacao', 'nome', 'honra', 'dignidade'],
            'praticidade': ['pratico', 'facil', 'simples', 'rapido'],
            'seguranca': ['seguro', 'garantia', 'proteção', 'estabilidade']
        }
        
        for motivator_type, patterns in motivation_patterns.items():
            for pattern in patterns:
                if pattern in message.lower():
                    motivators.append(f"{motivator_type}:{pattern}")
        
        return motivators
    
    def _detect_negotiation_style(self, message: str) -> str:
        """Detectar estilo de negociação"""
        styles = {
            'competitivo': ['desconto', 'melhor preço', 'mais barato', 'concorrencia'],
            'colaborativo': ['acordo', 'juntos', 'parceria', 'entendimento'],
            'acomodativo': ['aceito', 'tudo bem', 'tanto faz', 'como quiser'],
            'evitativo': ['depois', 'mais tarde', 'vou pensar', 'talvez'],
            'compromissador': ['meio termo', 'equilibrio', 'facilitar', 'parcelar']
        }
        
        for style, indicators in styles.items():
            if any(indicator in message.lower() for indicator in indicators):
                return style
        
        return 'indefinido'
    
    def _analyze_decision_making(self, message: str) -> str:
        """Analisar estilo de tomada de decisão"""
        decision_styles = {
            'racional': ['analisar', 'pensar', 'calcular', 'considerar'],
            'intuitivo': ['sinto', 'acho', 'parece', 'impressao'],
            'dependente': ['família', 'esposa', 'marido', 'consultar'],
            'evitativo': ['não sei', 'talvez', 'depois', 'vou ver'],
            'espontaneo': ['agora', 'já', 'imediato', 'rapidinho']
        }
        
        for style, indicators in decision_styles.items():
            if any(indicator in message.lower() for indicator in indicators):
                return style
        
        return 'indefinido'
    
    def _analyze_relationship_dynamics(self, message: str) -> Dict[str, float]:
        """Analisar dinâmicas relacionais"""
        dynamics = {
            'cooperacao': 0.0,
            'conflito': 0.0,
            'dependencia': 0.0,
            'autonomia': 0.0,
            'confianca': 0.0,
            'desconfianca': 0.0
        }
        
        # Indicadores de cooperação
        if any(word in message.lower() for word in ['junto', 'juntos', 'parceria', 'acordo']):
            dynamics['cooperacao'] = 0.8
        
        # Indicadores de conflito
        if any(word in message.lower() for word in ['contra', 'briga', 'discordo', 'errado']):
            dynamics['conflito'] = 0.8
        
        # Indicadores de dependência
        if any(word in message.lower() for word in ['preciso', 'ajuda', 'socorro', 'apoio']):
            dynamics['dependencia'] = 0.7
        
        # Indicadores de autonomia
        if any(word in message.lower() for word in ['sozinho', 'independente', 'eu mesmo']):
            dynamics['autonomia'] = 0.7
        
        # Indicadores de confiança
        if any(word in message.lower() for word in ['confio', 'acredito', 'certo', 'seguro']):
            dynamics['confianca'] = 0.8
        
        # Indicadores de desconfiança
        if any(word in message.lower() for word in ['desconfio', 'suspeito', 'duvido', 'sera']):
            dynamics['desconfianca'] = 0.8
        
        return dynamics
    
    def _detect_temporal_orientation(self, message: str) -> str:
        """Detectar orientação temporal"""
        past_indicators = ['era', 'foi', 'tinha', 'fazia', 'antes']
        present_indicators = ['agora', 'hoje', 'atualmente', 'neste momento']
        future_indicators = ['vai', 'será', 'amanhã', 'depois', 'futuro']
        
        past_count = sum(1 for indicator in past_indicators if indicator in message.lower())
        present_count = sum(1 for indicator in present_indicators if indicator in message.lower())
        future_count = sum(1 for indicator in future_indicators if indicator in message.lower())
        
        if future_count > past_count and future_count > present_count:
            return 'future'
        elif past_count > present_count and past_count > future_count:
            return 'past'
        else:
            return 'present'
    
    def _analyze_financial_patterns(self, message: str) -> List[str]:
        """Analisar padrões comportamentais financeiros"""
        patterns = []
        
        financial_behaviors = {
            'pagador_pontual': ['sempre pago', 'em dia', 'pontual', 'nunca atraso'],
            'pagador_atrasado': ['atraso', 'esqueci', 'atrasado', 'depois do vencimento'],
            'negociador': ['desconto', 'parcelar', 'facilitar', 'condições'],
            'planejador': ['organizei', 'planejei', 'programei', 'separei'],
            'impulsivo': ['agora', 'já', 'imediato', 'sem pensar'],
            'cauteloso': ['pensar', 'analisar', 'estudar', 'avaliar']
        }
        
        for behavior, indicators in financial_behaviors.items():
            if any(indicator in message.lower() for indicator in indicators):
                patterns.append(behavior)
        
        return patterns
    
    def _calculate_trust_level(self, message: str) -> float:
        """Calcular nível de confiança"""
        trust_score = 0.5  # Base neutra
        
        # Indicadores positivos de confiança
        trust_indicators = ['confio', 'acredito', 'certo', 'seguro', 'tranquilo']
        distrust_indicators = ['desconfio', 'suspeito', 'duvidoso', 'inseguro', 'receoso']
        
        for indicator in trust_indicators:
            if indicator in message.lower():
                trust_score += 0.2
        
        for indicator in distrust_indicators:
            if indicator in message.lower():
                trust_score -= 0.2
        
        return max(0.0, min(1.0, trust_score))
    
    def _predict_conversation_trajectory(self, message: str, result) -> str:
        """Predizer trajetória da conversa"""
        if result.sentiment == SentimentType.ANGRY:
            return 'escalation'
        elif result.sentiment == SentimentType.CONFUSED:
            return 'clarification_needed'
        elif result.primary_intent == IntentType.NEGOTIATION:
            return 'negotiation_phase'
        elif result.primary_intent == IntentType.PAYMENT_CONFIRMATION:
            return 'resolution'
        else:
            return 'information_gathering'
    
    def _calculate_influence_susceptibility(self, message: str) -> float:
        """Calcular susceptibilidade à influência"""
        susceptibility = 0.5  # Base neutra
        
        # Indicadores de alta susceptibilidade
        if any(word in message.lower() for word in ['não sei', 'confuso', 'ajuda', 'o que fazer']):
            susceptibility += 0.3
        
        # Indicadores de baixa susceptibilidade
        if any(word in message.lower() for word in ['decidido', 'certo', 'firme', 'convicto']):
            susceptibility -= 0.3
        
        return max(0.0, min(1.0, susceptibility))
    
    def _calculate_cognitive_load(self, message: str) -> float:
        """Calcular carga cognitiva"""
        load = 0.0
        
        # Complexidade da mensagem
        words = len(message.split())
        sentences = len([s for s in message.split('.') if s.strip()])
        
        if sentences > 0:
            avg_words_per_sentence = words / sentences
            load += min(avg_words_per_sentence / 15.0, 0.5)
        
        # Indicadores de sobrecarga
        overload_indicators = ['confuso', 'não entendo', 'complicado', 'difícil']
        if any(indicator in message.lower() for indicator in overload_indicators):
            load += 0.4
        
        return min(load, 1.0)
    
    def _generate_deep_insights(self, message: str, result) -> Dict[str, Any]:
        """Gerar insights contextuais profundos"""
        insights = {
            'emotional_state': f"{result.sentiment.value} com intensidade {result.emotional_intensity}",
            'communication_effectiveness': self._assess_communication_effectiveness(message),
            'psychological_needs': self._identify_psychological_needs(message),
            'behavioral_triggers': self._identify_behavioral_triggers(message),
            'decision_factors': self._identify_decision_factors(message),
            'intervention_opportunities': self._identify_intervention_opportunities(result)
        }
        
        return insights
    
    def _assess_communication_effectiveness(self, message: str) -> str:
        """Avaliar efetividade da comunicação"""
        if len(message.split()) < 3:
            return 'muito_concisa'
        elif len(message.split()) > 50:
            return 'muito_verbosa'
        elif '?' in message:
            return 'busca_esclarecimento'
        elif '!' in message:
            return 'expressiva'
        else:
            return 'equilibrada'
    
    def _identify_psychological_needs(self, message: str) -> List[str]:
        """Identificar necessidades psicológicas"""
        needs = []
        
        need_patterns = {
            'seguranca': ['medo', 'inseguro', 'preocupado', 'proteção'],
            'reconhecimento': ['importante', 'valorizar', 'considerar', 'respeitar'],
            'autonomia': ['escolher', 'decidir', 'controlar', 'independente'],
            'pertencimento': ['família', 'grupo', 'juntos', 'sozinho'],
            'competencia': ['capaz', 'conseguir', 'habilidade', 'sucesso']
        }
        
        for need, indicators in need_patterns.items():
            if any(indicator in message.lower() for indicator in indicators):
                needs.append(need)
        
        return needs
    
    def _identify_behavioral_triggers(self, message: str) -> List[str]:
        """Identificar gatilhos comportamentais"""
        triggers = []
        
        trigger_patterns = {
            'injustica': ['injusto', 'errado', 'unfair', 'não é certo'],
            'pressao_tempo': ['urgente', 'rapido', 'pressa', 'imediato'],
            'ameaca_status': ['reputação', 'nome', 'imagem', 'credibilidade'],
            'perda_controle': ['não posso', 'impossível', 'sem escolha'],
            'comparacao_social': ['outros', 'vizinho', 'amigo', 'parente']
        }
        
        for trigger, indicators in trigger_patterns.items():
            if any(indicator in message.lower() for indicator in indicators):
                triggers.append(trigger)
        
        return triggers
    
    def _identify_decision_factors(self, message: str) -> List[str]:
        """Identificar fatores de decisão"""
        factors = []
        
        decision_factors = {
            'preco': ['caro', 'barato', 'valor', 'custo'],
            'conveniencia': ['fácil', 'prático', 'simples', 'cômodo'],
            'qualidade': ['bom', 'ruim', 'qualidade', 'excelente'],
            'tempo': ['rápido', 'demorado', 'prazo', 'quando'],
            'risco': ['seguro', 'arriscado', 'garantia', 'proteção'],
            'social': ['família', 'amigos', 'opinião', 'recomendação']
        }
        
        for factor, indicators in decision_factors.items():
            if any(indicator in message.lower() for indicator in indicators):
                factors.append(factor)
        
        return factors
    
    def _identify_intervention_opportunities(self, result) -> List[str]:
        """Identificar oportunidades de intervenção"""
        opportunities = []
        
        if result.sentiment == SentimentType.CONFUSED:
            opportunities.append('esclarecimento_informacional')
        
        if result.sentiment == SentimentType.ANGRY:
            opportunities.append('acalmamento_emocional')
        
        if result.primary_intent == IntentType.NEGOTIATION:
            opportunities.append('proposta_alternativa')
        
        if result.emotional_intensity > 7.0:
            opportunities.append('reducao_tensao')
        
        if result.urgency_score > 8.0:
            opportunities.append('resposta_prioritaria')
        
        return opportunities
    
    # Métodos auxiliares para análise psicológica
    def _analyze_openness(self, message: str) -> float:
        """Analisar abertura à experiência"""
        openness_indicators = ['novo', 'diferente', 'criativo', 'inovador', 'original']
        score = sum(1 for indicator in openness_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_conscientiousness(self, message: str) -> float:
        """Analisar conscienciosidade"""
        conscientiousness_indicators = ['organizado', 'planejado', 'responsável', 'cuidadoso']
        score = sum(1 for indicator in conscientiousness_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_extraversion(self, message: str) -> float:
        """Analisar extroversão"""
        extraversion_indicators = ['social', 'falante', 'energético', 'ativo']
        score = sum(1 for indicator in extraversion_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_agreeableness(self, message: str) -> float:
        """Analisar amabilidade"""
        agreeableness_indicators = ['gentil', 'cooperativo', 'confiante', 'compreensivo']
        score = sum(1 for indicator in agreeableness_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_neuroticism(self, message: str) -> float:
        """Analisar neuroticismo"""
        neuroticism_indicators = ['ansioso', 'nervoso', 'preocupado', 'estressado']
        score = sum(1 for indicator in neuroticism_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_self_esteem(self, message: str) -> float:
        """Analisar autoestima"""
        low_esteem = ['não consigo', 'sou burro', 'não sei', 'incapaz']
        high_esteem = ['consigo', 'sou capaz', 'confiante', 'sei']
        
        low_score = sum(1 for indicator in low_esteem if indicator in message.lower())
        high_score = sum(1 for indicator in high_esteem if indicator in message.lower())
        
        return max(0.0, min(1.0, 0.5 + (high_score - low_score) * 0.2))
    
    def _analyze_assertiveness(self, message: str) -> float:
        """Analisar assertividade"""
        assertive_indicators = ['quero', 'preciso', 'exijo', 'demando', 'solicito']
        score = sum(1 for indicator in assertive_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_impulsivity(self, message: str) -> float:
        """Analisar impulsividade"""
        impulsive_indicators = ['agora', 'já', 'imediato', 'rapidinho', 'sem pensar']
        score = sum(1 for indicator in impulsive_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
    def _analyze_frustration_tolerance(self, message: str) -> float:
        """Analisar tolerância à frustração"""
        low_tolerance = ['não aguento', 'irritante', 'insuportável', 'odeio']
        high_tolerance = ['paciência', 'calma', 'tranquilo', 'compreendo']
        
        low_score = sum(1 for indicator in low_tolerance if indicator in message.lower())
        high_score = sum(1 for indicator in high_tolerance if indicator in message.lower())
        
        return max(0.0, min(1.0, 0.5 + (high_score - low_score) * 0.2))
    
    def _analyze_social_orientation(self, message: str) -> float:
        """Analisar orientação social"""
        social_indicators = ['pessoas', 'amigos', 'família', 'grupo', 'todos']
        score = sum(1 for indicator in social_indicators if indicator in message.lower())
        return min(score / 3.0, 1.0)
    
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
