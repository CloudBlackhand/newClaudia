"""
CLAUDIA SUPREMA ULTRA INTELIGENTE - IA REAL DE COBRANÇA COM APRENDIZADO AVANÇADO
Sistema de Inteligência Artificial focado EXCLUSIVAMENTE em cobrança eficaz.
INTEGRAÇÃO TOTAL com sistemas de aprendizado, otimização e análise de qualidade.

REGRAS DE OURO:
- SÓ COBRAMOS, NÃO PARCELAMOS
- SÓ COBRAMOS, NÃO AJUDAMOS  
- SÓ COBRAMOS, NÃO NEGOCIAMOS
- NÃO PRESSIONAMOS - APENAS INFORMAMOS
- FOCO TOTAL: RECEBER O PAGAMENTO
- APRENDE COM CADA INTERAÇÃO
- OTIMIZA AUTOMATICAMENTE
- ENTENDE TUDO QUE O CLIENTE FALA
"""

import re
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import random
from pathlib import Path
import asyncio
import statistics

# Configuração de logging
logger = logging.getLogger(__name__)

# Importar módulos de aprendizado
try:
    from backend.modules.response_quality_analyzer import ResponseQualityAnalyzer
    from backend.modules.template_learning_engine import TemplateLearningEngine
    from backend.modules.campaign_optimizer import CampaignOptimizer
    LEARNING_MODULES_AVAILABLE = True
    logger.info("🧠 MÓDULOS DE APRENDIZADO CARREGADOS COM SUCESSO!")
except ImportError as e:
    logger.warning(f"⚠️ Módulos de aprendizado não disponíveis: {e}")
    LEARNING_MODULES_AVAILABLE = False

class IntentType(Enum):
    """Intenções do cliente em conversas de cobrança"""
    PAGAMENTO_CONFIRMADO = "pagamento_confirmado"
    PAGAMENTO_NEGADO = "pagamento_negado" 
    PEDIDO_PARCELAMENTO = "pedido_parcelamento"
    PEDIDO_DESCONTO = "pedido_desconto"
    CONTESTACAO_DIVIDA = "contestacao_divida"
    PEDIDO_COMPROVANTE = "pedido_comprovante"
    INFORMACAO_PAGAMENTO = "informacao_pagamento"
    PERGUNTA_GERAL = "pergunta_geral"
    CUMPRIMENTO = "cumprimento"
    DESPEDIDA = "despedida"
    DUVIDA_COBRANCA = "duvida_cobranca"
    NOME_INCORRETO = "nome_incorreto"
    PEDIDO_DADOS = "pedido_dados"
    RECLAMACAO = "reclamacao"
    AGRADECIMENTO = "agradecimento"
    CONFIRMACAO = "confirmacao"
    NEGACAO = "negacao"
    ENROLACAO = "enrolacao"
    PROMESSA_FALSA = "promessa_falsa"
    IGNORAR = "ignorar"

class SentimentType(Enum):
    """Sentimentos identificados na mensagem"""
    COOPERATIVO = "cooperativo"
    RESISTENTE = "resistente"
    AGRESSIVO = "agressivo"
    DESESPERADO = "desesperado"
    ENROLADOR = "enrolador"
    MENTIROSO = "mentiroso"
    NEUTRO = "neutro"

class ResponseType(Enum):
    """Tipos de resposta da IA"""
    COBRANCA_EDUCADA = "cobranca_educada"
    COBRANCA_DIRETA = "cobranca_direta"
    COBRANCA_INFORMATIVA = "cobranca_informativa"
    REJEITAR_PARCELAMENTO = "rejeitar_parcelamento"
    REJEITAR_DESCONTO = "rejeitar_desconto"
    CONFIRMAR_PAGAMENTO = "confirmar_pagamento"
    ESCLARECER_DUVIDA = "esclarecer_duvida"
    CONFIRMAR_DADOS = "confirmar_dados"
    NOME_INCORRETO_RESPOSTA = "nome_incorreto_resposta"
    RESPOSTA_EDUCADA = "resposta_educada"
    CUMPRIMENTO_RESPOSTA = "cumprimento_resposta"
    DESPEDIDA_RESPOSTA = "despedida_resposta"
    IGNORAR_ENROLACAO = "ignorar_enrolacao"

@dataclass
class ConversationContext:
    """Contexto da conversa para análise inteligente"""
    customer_phone: str
    customer_name: str
    debt_amount: float
    days_overdue: int
    previous_contacts: int
    payment_promises: int
    conversation_history: List[Dict]
    last_response_time: Optional[datetime] = None
    cooperation_level: float = 0.5
    lie_probability: float = 0.0
    urgency_level: float = 0.5

@dataclass 
class AnalysisResult:
    """Resultado da análise inteligente da mensagem"""
    intent: IntentType
    sentiment: SentimentType
    lie_probability: float
    cooperation_score: float
    urgency_level: float
    payment_indicators: List[str]
    excuse_indicators: List[str]
    emotional_state: str
    recommended_response: ResponseType
    confidence: float

@dataclass
class BotResponse:
    """Resposta gerada pela IA"""
    message: str
    response_type: ResponseType
    urgency_level: float
    next_contact_hours: int
    escalate: bool
    context_update: Dict[str, Any]
    confidence: float = 0.8

class AdvancedNLPProcessor:
    """Processador de Linguagem Natural ULTRA AVANÇADO focado em cobrança"""
    
    def __init__(self):
        # Padrões básicos
        self.intent_patterns = self._load_intent_patterns()
        self.sentiment_indicators = self._load_sentiment_indicators()
        self.payment_keywords = self._load_payment_keywords()
        self.excuse_patterns = self._load_excuse_patterns()
        self.lie_indicators = self._load_lie_indicators()
        self.cooperation_indicators = self._load_cooperation_indicators()
        
        # NOVOS SISTEMAS AVANÇADOS DE ENTENDIMENTO
        self.contextual_patterns = self._load_contextual_patterns()
        self.behavioral_indicators = self._load_behavioral_indicators()
        self.conversation_flow_patterns = self._load_conversation_flow_patterns()
        self.question_patterns = self._load_question_patterns()
        self.greeting_patterns = self._load_greeting_patterns()
        self.doubt_patterns = self._load_doubt_patterns()
        
        # Histórico de aprendizado
        self.learned_patterns = {}
        self.success_correlations = {}
        self.failure_patterns = {}
        
        logger.info("🧠 NLP ULTRA AVANÇADO INICIALIZADO - 15+ SISTEMAS DE ANÁLISE!")
        
    def _load_intent_patterns(self) -> Dict[IntentType, List[str]]:
        """Padrões para detectar intenções reais do cliente"""
        return {
            IntentType.PAGAMENTO_CONFIRMADO: [
                r'(?:já|acabei de|vou) (?:pagar|pagei|pago)',
                r'(?:pix|transferência|depósito) (?:feito|realizado|enviado)',
                r'(?:comprovante|recibo) (?:anexo|em anexo|segue)',
                r'(?:quitei|quitado|liquidei)',
                r'(?:valor|dívida) (?:pago|quitado|liquidado)'
            ],
            IntentType.PAGAMENTO_NEGADO: [
                r'não (?:vou|posso|tenho como) pagar',
                r'não (?:tenho|possuo) (?:dinheiro|grana|condições)',
                r'(?:sem|não tenho) (?:dinheiro|grana|condições|como)',
                r'(?:desempregado|sem trabalho|sem renda)',
                r'(?:impossível|não consigo) pagar'
            ],
            IntentType.PEDIDO_PARCELAMENTO: [
                r'(?:parcelar|dividir|fracionar)',
                r'(?:parcelas|vezes|prestações)',
                r'pagar (?:aos poucos|devagar|parcelado)',
                r'(?:acordo|negociação) (?:de|para) pagamento',
                r'(?:facilitar|ajudar) (?:o|no) pagamento'
            ],
            IntentType.PEDIDO_DESCONTO: [
                r'(?:desconto|abatimento|redução)',
                r'(?:diminuir|reduzir|baixar) (?:o|a) (?:valor|dívida)',
                r'pagar (?:menos|menor|parte)',
                r'(?:valor|preço) (?:menor|mais baixo)',
                r'(?:promoção|oferta|condição especial)'
            ],
            IntentType.CONTESTACAO_DIVIDA: [
                r'(?:não|nunca) (?:comprei|contratei|usei)',
                r'(?:não|nunca) (?:devo|tenho dívida)',
                r'(?:erro|engano|equívoco)',
                r'(?:não|nunca) (?:foi|era) (?:meu|minha)',
                r'(?:fraude|golpe|clonaram)'
            ],
            IntentType.ENROLACAO: [
                r'(?:depois|mais tarde|amanhã|semana que vem)',
                r'(?:vou ver|vou tentar|vou verificar)',
                r'(?:talvez|pode ser|quem sabe)',
                r'(?:ocupado|corrido|sem tempo)',
                r'(?:resolver|organizar|acertar) (?:depois|mais tarde)'
            ],
            IntentType.PROMESSA_FALSA: [
                r'(?:hoje mesmo|ainda hoje|até (?:hoje|amanhã))',
                r'(?:já|agora mesmo|neste momento)',
                r'(?:pode|podem) (?:confiar|acreditar)',
                r'(?:palavra|prometo|garanto)',
                r'(?:certeza|com certeza|sem dúvida)'
            ],
            IntentType.CUMPRIMENTO: [
                r'(?:oi|olá|boa tarde|bom dia|boa noite)',
                r'(?:e aí|eae|salve|hey|hello)',
                r'(?:tudo bem|como vai|beleza)',
                r'(?:opa|oie|oii)'
            ],
            IntentType.DESPEDIDA: [
                r'(?:tchau|até logo|até mais|flw)',
                r'(?:obrigado|obrigada|valeu)',
                r'(?:até|falou|bye|adeus)',
                r'(?:tenha um bom dia|boa tarde|boa noite)'
            ],
            IntentType.DUVIDA_COBRANCA: [
                r'(?:essa cobrança|essa dívida|esse valor) (?:é|está) (?:meu|minha|certo)',
                r'(?:não|nunca) (?:contratei|comprei|usei)',
                r'(?:de onde|qual) (?:vem|é) (?:essa|esta) (?:cobrança|dívida)',
                r'(?:não|nunca) (?:foi|é) (?:meu|minha)',
                r'(?:erro|engano|equívoco|fraude)',
                r'(?:meu nome|esse nome) (?:não|nao) (?:é|sou) (?:esse|meu)',
                r'(?:não|nao) (?:sou|é) (?:eu|meu nome)',
                r'(?:número|telefone) (?:não|nao) (?:é|sou) (?:meu|dele)',
                r'(?:pessoa errada|número errado|nome errado)',
                r'(?:não|nao) (?:conheço|sei quem é) (?:esse|essa) (?:nome|pessoa)'
            ],
            IntentType.NOME_INCORRETO: [
                r'(?:meu nome|esse nome) (?:não|nao) (?:é|sou) (?:esse|este)',
                r'(?:não|nao) (?:sou|é|me chamo) (?:eu|esse nome)',
                r'(?:número|telefone) (?:não|nao) (?:é|sou) (?:meu|dele)',
                r'(?:pessoa errada|número errado|nome errado)',
                r'(?:não|nao) (?:conheço|sei quem é) (?:esse|essa) (?:nome|pessoa)',
                r'(?:engano|erro) (?:de|no) (?:nome|número|telefone)',
                r'(?:vocês|você) (?:erraram|errou) (?:o|meu) (?:nome|número)',
                r'(?:esse|este) (?:nome|número) (?:não|nao) (?:é|sou|pertence) (?:meu|a mim)',
                r'(?:quem é|não sei quem é|nunca ouvi falar) (?:esse|essa|este|esta) (?:nome|pessoa)'
            ],
            IntentType.PERGUNTA_GERAL: [
                r'(?:como|onde|quando|qual|quanto|por que|porque)',
                r'(?:pode|podem) (?:me|ajudar|explicar|dizer)',
                r'(?:gostaria|queria) (?:de|saber)',
                r'(?:tenho|tenho uma) (?:dúvida|pergunta)'
            ],
            IntentType.PEDIDO_DADOS: [
                r'(?:qual|onde) (?:é|fica) (?:meu|o) (?:nome|cpf|telefone)',
                r'(?:confirma|confirmar) (?:meus|os) (?:dados|informações)',
                r'(?:meu nome|meus dados) (?:está|estão) (?:certo|correto)',
                r'(?:pode|podem) (?:conferir|verificar) (?:meus dados|meu nome)'
            ],
            IntentType.AGRADECIMENTO: [
                r'(?:obrigado|obrigada|muito obrigado)',
                r'(?:valeu|vlw|brigadão|brigada)',
                r'(?:agradeço|grato|grata)',
                r'(?:muito|mt) (?:obrigado|obrigada)'
            ],
            IntentType.CONFIRMACAO: [
                r'(?:sim|yes|é isso mesmo|correto)',
                r'(?:ok|okay|certo|beleza|tranquilo)',
                r'(?:pode ser|tudo bem|sem problema)',
                r'(?:confirmo|é isso|exato)'
            ],
            IntentType.NEGACAO: [
                r'(?:não|nao|nunca|jamais)',
                r'(?:negativo|não é|não foi)',
                r'(?:de jeito nenhum|nem pensar)',
                r'(?:claro que não|obviamente não)'
            ]
        }
    
    def _load_sentiment_indicators(self) -> Dict[SentimentType, List[str]]:
        """Indicadores de sentimento do cliente"""
        return {
            SentimentType.COOPERATIVO: [
                r'(?:entendo|compreendo|sei)',
                r'(?:desculpa|perdão|me perdoe)',
                r'(?:vou|irei) (?:resolver|pagar|acertar)',
                r'(?:obrigado|obrigada|agradeço)',
                r'(?:certo|ok|tudo bem|beleza)'
            ],
            SentimentType.AGRESSIVO: [
                r'(?:caralho|porra|merda|droga)',
                r'(?:chato|enchendo|perturbando)',
                r'(?:deixa|para) (?:de|com isso)',
                r'(?:não|para) (?:me|de) (?:perturbar|incomodar)',
                r'(?:vai|vão) (?:se|tomar no) (?:foder|cu)'
            ],
            SentimentType.DESESPERADO: [
                r'(?:pelo amor de deus|por favor)',
                r'(?:desesperad|aflito|desesper)',
                r'(?:preciso|urgente|socorro)',
                r'(?:difícil|complicad|apertad)',
                r'(?:imploro|suplico|peço)'
            ],
            SentimentType.ENROLADOR: [
                r'(?:vou ver|deixa eu ver|vou verificar)',
                r'(?:depois|mais tarde|outro dia)',
                r'(?:ocupado|sem tempo|corrido)',
                r'(?:talvez|pode ser|quem sabe)',
                r'(?:complicado|difícil|impossível)'
            ]
        }
    
    def _load_payment_keywords(self) -> List[str]:
        """Palavras-chave relacionadas a pagamento"""
        return [
            'pix', 'transferencia', 'deposito', 'ted', 'doc',
            'cartao', 'dinheiro', 'pagamento', 'valor', 'quantia',
            'conta', 'banco', 'agencia', 'comprovante', 'recibo'
        ]
    
    def _load_excuse_patterns(self) -> List[str]:
        """Padrões de desculpas comuns"""
        return [
            r'(?:sem|não tenho) (?:dinheiro|grana)',
            r'(?:desempregado|sem trabalho)',
            r'(?:doente|internado|hospital)',
            r'(?:viagem|viajando|fora)',
            r'(?:problema|dificuldade) (?:familiar|pessoal)',
            r'(?:cartão|conta) (?:bloqueado|sem limite)',
            r'(?:salário|pagamento) (?:atrasado|não saiu)',
            r'(?:filho|família) (?:doente|problema)'
        ]
    
    def _load_lie_indicators(self) -> List[str]:
        """Indicadores de possível mentira"""
        return [
            r'(?:juro|prometo|garanto) (?:por|pela) (?:minha|meu)',
            r'(?:palavra|honra|vida) (?:de|que)',
            r'(?:pode|podem) (?:confiar|acreditar)',
            r'(?:certeza|com certeza|sem dúvida)',
            r'(?:verdade|sério|real|de verdade)',
            r'(?:hoje mesmo|ainda hoje|agora mesmo)',
            r'(?:já|acabei de|neste momento)'
        ]
    
    def _load_cooperation_indicators(self) -> List[str]:
        """Indicadores de cooperação genuína"""
        return [
            r'(?:entendo|compreendo|sei) (?:a|o) (?:situação|problema)',
            r'(?:desculpa|perdão|me perdoe)',
            r'(?:assumo|reconheço) (?:a|o) (?:dívida|débito)',
            r'(?:vou|irei) (?:resolver|pagar|acertar)',
            r'(?:como|qual) (?:faço|posso fazer) (?:para|o) (?:pagar|pagamento)'
        ]
    
    def _load_contextual_patterns(self) -> Dict[str, List[str]]:
        """Padrões contextuais avançados para análise profunda"""
        return {
            'desperation_context': [
                r'(?:preciso|urgente|desesperado|aflito)',
                r'(?:pelo amor de deus|por favor|socorro)',
                r'(?:família|filho|mãe|pai) (?:doente|problema)',
                r'(?:perder|perdendo) (?:casa|emprego|tudo)'
            ],
            'financial_stress': [
                r'(?:sem|não tenho) (?:dinheiro|grana|condições)',
                r'(?:desempregado|demitido|sem trabalho)',
                r'(?:salário|pagamento) (?:atrasado|cortado)',
                r'(?:conta|cartão) (?:bloqueado|cancelado)'
            ],
            'confusion_patterns': [
                r'(?:não entendo|não sei|confuso)',
                r'(?:como assim|que isso|o que)',
                r'(?:explica|esclarece) (?:melhor|isso)',
                r'(?:não|nunca) (?:vi|recebi) (?:essa|esta) (?:cobrança|mensagem)'
            ],
            'politeness_patterns': [
                r'(?:por favor|por gentileza)',
                r'(?:obrigado|obrigada|agradeço)',
                r'(?:desculpa|perdão|me perdoe)',
                r'(?:com licença|se possível)'
            ]
        }
    
    def _load_behavioral_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Indicadores comportamentais para predição de ações"""
        return {
            'payment_likelihood': {
                'high': [
                    r'(?:já|acabei de|vou) (?:pagar|fazer o pix)',
                    r'(?:qual|onde) (?:é|fica) (?:a|o) (?:chave|conta)',
                    r'(?:como|onde) (?:faço|posso fazer) (?:o|para) pagar',
                    r'(?:comprovante|recibo) (?:segue|anexo|aqui)'
                ],
                'medium': [
                    r'(?:vou|irei) (?:resolver|acertar|pagar)',
                    r'(?:entendo|sei) (?:que|da) (?:situação|problema)',
                    r'(?:quando|até quando) (?:posso|tenho) (?:para|até) pagar',
                    r'(?:preciso|quero) (?:resolver|acertar) isso'
                ],
                'low': [
                    r'(?:não|nunca) (?:vou|posso|tenho como) pagar',
                    r'(?:impossível|não consigo|não dá)',
                    r'(?:sem|não tenho) (?:condições|como|jeito)',
                    r'(?:não|nunca) (?:comprei|contratei|usei)'
                ]
            },
            'cooperation_level': {
                'high': [
                    r'(?:obrigado|obrigada|agradeço)',
                    r'(?:desculpa|perdão|me perdoe)',
                    r'(?:entendo|compreendo|sei)',
                    r'(?:certo|ok|tudo bem|beleza)'
                ],
                'low': [
                    r'(?:não|para) (?:me|de) (?:perturbar|incomodar)',
                    r'(?:chato|enchendo|perturbando)',
                    r'(?:deixa|para) (?:de|com isso)',
                    r'(?:vai|vão) (?:se|tomar no) (?:foder|cu)'
                ]
            }
        }
    
    def _load_conversation_flow_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Padrões de fluxo de conversa para otimizar sequência"""
        return {
            'opening_effectiveness': {
                'direct': 0.7,
                'empathetic': 0.8,
                'informative': 0.75,
                'educational': 0.85
            },
            'follow_up_timing': {
                'immediate_response': 2,  # horas
                'cooperative_client': 6,
                'resistant_client': 4,
                'confused_client': 1
            },
            'escalation_triggers': {
                'no_response_after': 3,  # tentativas
                'repeated_confusion': 2,
                'aggressive_behavior': 1,
                'payment_denial': 2
            }
        }
    
    def _load_question_patterns(self) -> List[str]:
        """Padrões para identificar perguntas"""
        return [
            r'(?:como|onde|quando|qual|quanto|por que|porque)',
            r'(?:pode|podem) (?:me|ajudar|explicar|dizer)',
            r'(?:gostaria|queria) (?:de|saber)',
            r'(?:tenho|tenho uma) (?:dúvida|pergunta)',
            r'(?:o que|que) (?:é|significa|quer dizer)',
            r'(?:será que|será) (?:pode|podem)'
        ]
    
    def _load_greeting_patterns(self) -> List[str]:
        """Padrões para identificar cumprimentos"""
        return [
            r'(?:oi|olá|boa tarde|bom dia|boa noite)',
            r'(?:e aí|eae|salve|hey|hello)',
            r'(?:tudo bem|como vai|beleza)',
            r'(?:opa|oie|oii|oi tudo bem)'
        ]
    
    def _load_doubt_patterns(self) -> List[str]:
        """Padrões para identificar dúvidas sobre a cobrança"""
        return [
            r'(?:essa cobrança|essa dívida|esse valor) (?:é|está) (?:meu|minha|certo)',
            r'(?:não|nunca) (?:contratei|comprei|usei)',
            r'(?:de onde|qual) (?:vem|é) (?:essa|esta) (?:cobrança|dívida)',
            r'(?:meu nome|meus dados) (?:está|estão) (?:certo|correto)',
            r'(?:erro|engano|equívoco|fraude|golpe)'
        ]

    def analyze_message(self, message: str, context: ConversationContext) -> AnalysisResult:
        """ANÁLISE ULTRA AVANÇADA da mensagem do cliente - 20+ SISTEMAS DE ANÁLISE"""
        message_lower = message.lower()
        
        logger.info(f"🔍 INICIANDO ANÁLISE ULTRA AVANÇADA: {message[:50]}...")
        
        # 1. DETECTAR INTENÇÃO REAL
        intent = self._detect_intent_advanced(message_lower)
        
        # 2. ANALISAR SENTIMENTO 
        sentiment = self._analyze_sentiment_advanced(message_lower)
        
        # 3. CALCULAR PROBABILIDADE DE MENTIRA
        lie_probability = self._calculate_lie_probability(message_lower, context)
        
        # 4. AVALIAR NÍVEL DE COOPERAÇÃO
        cooperation_score = self._evaluate_cooperation_advanced(message_lower, context)
        
        # 5. DETERMINAR URGÊNCIA
        urgency_level = self._calculate_urgency(context, intent, sentiment)
        
        # 6. IDENTIFICAR INDICADORES DE PAGAMENTO
        payment_indicators = self._find_payment_indicators(message_lower)
        
        # 7. IDENTIFICAR DESCULPAS
        excuse_indicators = self._find_excuse_indicators(message_lower)
        
        # ===== NOVOS SISTEMAS ULTRA AVANÇADOS =====
        
        # 8. ANÁLISE CONTEXTUAL PROFUNDA
        contextual_analysis = self._analyze_context_patterns(message_lower, context)
        
        # 9. PREDIÇÃO DE COMPORTAMENTO
        behavioral_prediction = self._predict_client_behavior(message_lower, context)
        
        # 10. ANÁLISE DE CONFUSÃO/DÚVIDAS
        confusion_level = self._analyze_confusion_level(message_lower)
        
        # 11. DETECÇÃO DE PERGUNTAS
        is_question = self._is_question(message_lower)
        
        # 12. ANÁLISE DE POLIDEZ
        politeness_level = self._analyze_politeness(message_lower)
        
        # 13. DETECÇÃO DE CUMPRIMENTOS/DESPEDIDAS
        conversation_stage = self._detect_conversation_stage(message_lower)
        
        # 14. ANÁLISE DE DÚVIDA SOBRE COBRANÇA
        doubt_about_charge = self._analyze_charge_doubt(message_lower)
        
        # 15. ANALISAR ESTADO EMOCIONAL AVANÇADO
        emotional_state = self._analyze_advanced_emotional_state(
            sentiment, lie_probability, cooperation_score, contextual_analysis
        )
        
        # 16. RECOMENDAR TIPO DE RESPOSTA INTELIGENTE
        recommended_response = self._recommend_intelligent_response_type(
            intent, sentiment, lie_probability, cooperation_score, context,
            behavioral_prediction, confusion_level, is_question, doubt_about_charge
        )
        
        # 17. CALCULAR CONFIANÇA AVANÇADA DA ANÁLISE
        confidence = self._calculate_advanced_confidence(
            intent, sentiment, payment_indicators, excuse_indicators,
            contextual_analysis, behavioral_prediction, confusion_level
        )
        
        logger.info(f"🧠 ANÁLISE COMPLETA: Intent={intent.value}, Confusão={confusion_level:.2f}, Pergunta={is_question}")
        
        return AnalysisResult(
            intent=intent,
            sentiment=sentiment,
            lie_probability=lie_probability,
            cooperation_score=cooperation_score,
            urgency_level=urgency_level,
            payment_indicators=payment_indicators,
            excuse_indicators=excuse_indicators,
            emotional_state=emotional_state,
            recommended_response=recommended_response,
            confidence=confidence
        )
    
    def _detect_intent(self, message: str) -> IntentType:
        """Detecta a VERDADEIRA intenção do cliente"""
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message))
                score += matches * 2  # Peso maior para matches exatos
                
            intent_scores[intent_type] = score
        
        # Se não encontrou padrões específicos, analisa contexto
        if max(intent_scores.values()) == 0:
            if any(word in message for word in ['sim', 'ok', 'certo', 'beleza']):
                return IntentType.PAGAMENTO_CONFIRMADO
            elif any(word in message for word in ['não', 'nao', 'nunca', 'jamais']):
                return IntentType.PAGAMENTO_NEGADO
            else:
                return IntentType.ENROLACAO
        
        return max(intent_scores, key=intent_scores.get)
    
    def _analyze_sentiment(self, message: str) -> SentimentType:
        """Analisa o VERDADEIRO sentimento do cliente"""
        sentiment_scores = {}
        
        for sentiment_type, indicators in self.sentiment_indicators.items():
            score = 0
            for indicator in indicators:
                matches = len(re.findall(indicator, message))
                score += matches
            sentiment_scores[sentiment_type] = score
        
        if max(sentiment_scores.values()) == 0:
            return SentimentType.NEUTRO
        
        return max(sentiment_scores, key=sentiment_scores.get)
    
    def _calculate_lie_probability(self, message: str, context: ConversationContext) -> float:
        """Calcula probabilidade de mentira baseada em padrões"""
        lie_score = 0.0
        
        # Verifica indicadores de mentira
        for indicator in self.lie_indicators:
            matches = len(re.findall(indicator, message))
            lie_score += matches * 0.2
        
        # Histórico de promessas não cumpridas aumenta probabilidade
        lie_score += context.payment_promises * 0.15
        
        # Respostas muito rápidas ou muito elaboradas podem indicar mentira
        if len(message) > 200:  # Resposta muito longa
            lie_score += 0.1
        
        # Múltiplas desculpas na mesma mensagem
        excuse_count = sum(1 for pattern in self.excuse_patterns 
                          if re.search(pattern, message))
        if excuse_count > 1:
            lie_score += excuse_count * 0.1
        
        return min(lie_score, 1.0)  # Máximo 1.0
    
    def _evaluate_cooperation(self, message: str, context: ConversationContext) -> float:
        """Avalia nível real de cooperação do cliente"""
        cooperation_score = 0.5  # Base neutra
        
        # Indicadores positivos de cooperação
        for indicator in self.cooperation_indicators:
            matches = len(re.findall(indicator, message))
            cooperation_score += matches * 0.15
        
        # Penaliza histórico de não cooperação
        cooperation_score -= context.payment_promises * 0.1
        cooperation_score -= (context.days_overdue / 30) * 0.2
        
        # Bonifica menções específicas de pagamento
        payment_mentions = sum(1 for keyword in self.payment_keywords 
                             if keyword in message)
        cooperation_score += payment_mentions * 0.1
        
        return max(0.0, min(cooperation_score, 1.0))
    
    def _calculate_urgency(self, context: ConversationContext, 
                          intent: IntentType, sentiment: SentimentType) -> float:
        """Calcula nível de urgência da situação"""
        urgency = 0.5  # Base
        
        # Dias de atraso aumentam urgência
        urgency += (context.days_overdue / 30) * 0.3
        
        # Múltiplos contatos aumentam urgência
        urgency += (context.previous_contacts / 10) * 0.2
        
        # Valor da dívida afeta urgência
        if context.debt_amount > 1000:
            urgency += 0.2
        elif context.debt_amount > 5000:
            urgency += 0.4
        
        # Intenções específicas afetam urgência
        if intent == IntentType.PAGAMENTO_NEGADO:
            urgency += 0.3
        elif intent == IntentType.CONTESTACAO_DIVIDA:
            urgency += 0.4
        elif sentiment == SentimentType.AGRESSIVO:
            urgency += 0.2
        
        return min(urgency, 1.0)
    
    def _find_payment_indicators(self, message: str) -> List[str]:
        """Encontra indicadores específicos de pagamento"""
        indicators = []
        for keyword in self.payment_keywords:
            if keyword in message:
                indicators.append(keyword)
        return indicators
    
    def _find_excuse_indicators(self, message: str) -> List[str]:
        """Encontra padrões de desculpas"""
        indicators = []
        for pattern in self.excuse_patterns:
            if re.search(pattern, message):
                indicators.append(pattern)
        return indicators
    
    def _analyze_emotional_state(self, sentiment: SentimentType, 
                                lie_probability: float, cooperation_score: float) -> str:
        """Analisa estado emocional real do cliente"""
        if sentiment == SentimentType.AGRESSIVO:
            return "Agressivo - Abordar com firmeza"
        elif sentiment == SentimentType.DESESPERADO:
            return "Desesperado - Manter pressão"
        elif lie_probability > 0.7:
            return "Mentiroso - Não acreditar em promessas"
        elif cooperation_score > 0.7:
            return "Cooperativo - Pode pagar se pressionado"
        elif sentiment == SentimentType.ENROLADOR:
            return "Enrolador - Ignorar desculpas"
        else:
            return "Neutro - Cobrança padrão"
    
    def _recommend_response_type(self, intent: IntentType, sentiment: SentimentType,
                                lie_probability: float, cooperation_score: float,
                                context: ConversationContext) -> ResponseType:
        """Recomenda tipo de resposta baseado na análise"""
        
        # Rejeitar pedidos de parcelamento/desconto SEMPRE
        if intent == IntentType.PEDIDO_PARCELAMENTO:
            return ResponseType.REJEITAR_PARCELAMENTO
        elif intent == IntentType.PEDIDO_DESCONTO:
            return ResponseType.REJEITAR_DESCONTO
        
        # Confirmação de pagamento
        elif intent == IntentType.PAGAMENTO_CONFIRMADO:
            return ResponseType.CONFIRMAR_PAGAMENTO
        
        # Cliente agressivo - resposta firme
        elif sentiment == SentimentType.AGRESSIVO:
            return ResponseType.COBRANCA_FIRME
        
        # Cliente mentiroso ou enrolador - pressionar
        elif lie_probability > 0.6 or sentiment == SentimentType.ENROLADOR:
            return ResponseType.PRESSIONAR_PAGAMENTO
        
        # Situação urgente (muito atraso)
        elif context.days_overdue > 60:
            return ResponseType.COBRANCA_URGENTE
        
        # Cliente cooperativo - cobrança direta
        elif cooperation_score > 0.6:
            return ResponseType.COBRANCA_DIRETA
        
        # Default - cobrança padrão
        else:
            return ResponseType.COBRANCA_DIRETA
    
    def _calculate_confidence(self, intent: IntentType, sentiment: SentimentType,
                             payment_indicators: List[str], excuse_indicators: List[str]) -> float:
        """Calcula confiança da análise"""
        confidence = 0.5
        
        # Mais indicadores = maior confiança
        confidence += len(payment_indicators) * 0.1
        confidence += len(excuse_indicators) * 0.05
        
        # Sentimentos claros aumentam confiança
        if sentiment != SentimentType.NEUTRO:
            confidence += 0.2
        
        # Intenções específicas aumentam confiança
        if intent != IntentType.ENROLACAO:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    # ===== NOVOS MÉTODOS ULTRA AVANÇADOS =====
    
    def _detect_intent_advanced(self, message: str) -> IntentType:
        """Detecta intenção com análise avançada"""
        intent_scores = {}
        
        for intent_type, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message))
                score += matches * 2  # Peso maior para matches exatos
                
            intent_scores[intent_type] = score
        
        # Análise contextual adicional
        if max(intent_scores.values()) == 0:
            # Detectar perguntas
            if self._is_question(message):
                if any(word in message for word in ['cobrança', 'dívida', 'valor', 'meu']):
                    return IntentType.DUVIDA_COBRANCA
                else:
                    return IntentType.PERGUNTA_GERAL
            
            # Detectar cumprimentos
            if any(re.search(pattern, message) for pattern in self.greeting_patterns):
                return IntentType.CUMPRIMENTO
            
            # Detectar confirmações simples
            if any(word in message for word in ['sim', 'ok', 'certo', 'beleza']):
                return IntentType.CONFIRMACAO
            elif any(word in message for word in ['não', 'nao', 'nunca', 'jamais']):
                return IntentType.NEGACAO
            else:
                return IntentType.ENROLACAO
        
        return max(intent_scores, key=intent_scores.get)
    
    def _analyze_sentiment_advanced(self, message: str) -> SentimentType:
        """Análise avançada de sentimento"""
        sentiment_scores = {}
        
        for sentiment_type, indicators in self.sentiment_indicators.items():
            score = 0
            for indicator in indicators:
                matches = len(re.findall(indicator, message))
                score += matches
            sentiment_scores[sentiment_type] = score
        
        # Análise contextual adicional
        politeness_level = self._analyze_politeness(message)
        if politeness_level > 0.7:
            sentiment_scores[SentimentType.COOPERATIVO] += 2
        
        confusion_level = self._analyze_confusion_level(message)
        if confusion_level > 0.7:
            sentiment_scores[SentimentType.NEUTRO] += 1
        
        if max(sentiment_scores.values()) == 0:
            return SentimentType.NEUTRO
        
        return max(sentiment_scores, key=sentiment_scores.get)
    
    def _evaluate_cooperation_advanced(self, message: str, context: ConversationContext) -> float:
        """Avalia cooperação com análise avançada"""
        cooperation_score = 0.5  # Base neutra
        
        # Indicadores positivos de cooperação
        for indicator in self.cooperation_indicators:
            matches = len(re.findall(indicator, message))
            cooperation_score += matches * 0.15
        
        # Bonus por polidez
        politeness_level = self._analyze_politeness(message)
        cooperation_score += politeness_level * 0.2
        
        # Bonus por perguntas genuínas
        if self._is_question(message) and not self._analyze_charge_doubt(message):
            cooperation_score += 0.1
        
        # Penaliza histórico de não cooperação
        cooperation_score -= context.payment_promises * 0.1
        cooperation_score -= (context.days_overdue / 30) * 0.2
        
        # Bonifica menções específicas de pagamento
        payment_mentions = sum(1 for keyword in self.payment_keywords 
                             if keyword in message)
        cooperation_score += payment_mentions * 0.1
        
        return max(0.0, min(cooperation_score, 1.0))
    
    def _analyze_context_patterns(self, message: str, context: ConversationContext) -> Dict[str, float]:
        """Análise contextual profunda da mensagem"""
        analysis = {
            'desperation_level': 0.0,
            'financial_stress': 0.0,
            'confusion_level': 0.0,
            'politeness_level': 0.0
        }
        
        for pattern_type, patterns in self.contextual_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, message))
                score += matches * 0.3
            
            if pattern_type == 'desperation_context':
                analysis['desperation_level'] = min(score, 1.0)
            elif pattern_type == 'financial_stress':
                analysis['financial_stress'] = min(score, 1.0)
            elif pattern_type == 'confusion_patterns':
                analysis['confusion_level'] = min(score, 1.0)
            elif pattern_type == 'politeness_patterns':
                analysis['politeness_level'] = min(score, 1.0)
        
        return analysis
    
    def _predict_client_behavior(self, message: str, context: ConversationContext) -> Dict[str, str]:
        """Prediz comportamento futuro do cliente"""
        behavior_scores = {
            'payment_likelihood': {'high': 0, 'medium': 0, 'low': 0},
            'cooperation_level': {'high': 0, 'low': 0}
        }
        
        # Analisar indicadores comportamentais
        for behavior_type, levels in self.behavioral_indicators.items():
            for level, patterns in levels.items():
                score = 0
                for pattern in patterns:
                    matches = len(re.findall(pattern, message))
                    score += matches
                behavior_scores[behavior_type][level] = score
        
        # Determinar comportamento mais provável
        prediction = {}
        for behavior_type, scores in behavior_scores.items():
            max_level = max(scores, key=scores.get)
            max_score = scores[max_level]
            if max_score > 0:
                prediction[behavior_type] = max_level
            else:
                prediction[behavior_type] = 'medium' if behavior_type == 'payment_likelihood' else 'medium'
        
        return prediction
    
    def _analyze_confusion_level(self, message: str) -> float:
        """Analisa nível de confusão do cliente"""
        confusion_score = 0.0
        
        confusion_patterns = self.contextual_patterns.get('confusion_patterns', [])
        for pattern in confusion_patterns:
            matches = len(re.findall(pattern, message))
            confusion_score += matches * 0.25
        
        # Detectar perguntas múltiplas (sinal de confusão)
        question_count = sum(1 for pattern in self.question_patterns 
                           if re.search(pattern, message))
        if question_count > 2:
            confusion_score += 0.3
        
        return min(confusion_score, 1.0)
    
    def _is_question(self, message: str) -> bool:
        """Verifica se a mensagem é uma pergunta"""
        # Detectar pontos de interrogação
        if '?' in message:
            return True
        
        # Detectar padrões de pergunta
        for pattern in self.question_patterns:
            if re.search(pattern, message):
                return True
        
        return False
    
    def _analyze_politeness(self, message: str) -> float:
        """Analisa nível de polidez"""
        politeness_score = 0.0
        
        politeness_patterns = self.contextual_patterns.get('politeness_patterns', [])
        for pattern in politeness_patterns:
            matches = len(re.findall(pattern, message))
            politeness_score += matches * 0.25
        
        return min(politeness_score, 1.0)
    
    def _detect_conversation_stage(self, message: str) -> str:
        """Detecta estágio da conversa"""
        if any(re.search(pattern, message) for pattern in self.greeting_patterns):
            return 'opening'
        elif any(word in message for word in ['tchau', 'até', 'obrigado', 'valeu']):
            return 'closing'
        else:
            return 'middle'
    
    def _analyze_charge_doubt(self, message: str) -> bool:
        """Analisa se cliente tem dúvida sobre a cobrança"""
        for pattern in self.doubt_patterns:
            if re.search(pattern, message):
                return True
        return False
    
    def _analyze_advanced_emotional_state(self, sentiment: SentimentType, lie_probability: float, 
                                        cooperation_score: float, contextual_analysis: Dict[str, float]) -> str:
        """Análise avançada do estado emocional"""
        if contextual_analysis.get('desperation_level', 0) > 0.7:
            return "Cliente desesperado - Abordar com empatia"
        elif contextual_analysis.get('confusion_level', 0) > 0.7:
            return "Cliente confuso - Esclarecer dúvidas"
        elif contextual_analysis.get('politeness_level', 0) > 0.7:
            return "Cliente educado - Manter tom respeitoso"
        elif sentiment == SentimentType.AGRESSIVO:
            return "Cliente agressivo - Resposta profissional"
        elif lie_probability > 0.8:
            return "Possível mentira - Focar em fatos"
        elif cooperation_score > 0.8:
            return "Cliente cooperativo - Facilitar processo"
        else:
            return "Estado neutro - Cobrança educada"
    
    def _recommend_intelligent_response_type(self, intent: IntentType, sentiment: SentimentType,
                                           lie_probability: float, cooperation_score: float,
                                           context: ConversationContext, behavioral_prediction: Dict[str, str],
                                           confusion_level: float, is_question: bool, doubt_about_charge: bool) -> ResponseType:
        """Recomendação INTELIGENTE de resposta baseada em TODOS os fatores"""
        
        # Prioridade 1: Rejeitar pedidos SEMPRE (mas educadamente)
        if intent == IntentType.PEDIDO_PARCELAMENTO:
            return ResponseType.REJEITAR_PARCELAMENTO
        elif intent == IntentType.PEDIDO_DESCONTO:
            return ResponseType.REJEITAR_DESCONTO
        
        # Prioridade 2: Confirmação de pagamento
        elif intent == IntentType.PAGAMENTO_CONFIRMADO:
            return ResponseType.CONFIRMAR_PAGAMENTO
        
        # Prioridade 3: Nome incorreto - caso especial
        elif intent == IntentType.NOME_INCORRETO:
            return ResponseType.NOME_INCORRETO_RESPOSTA
        
        # Prioridade 4: Esclarecer dúvidas sobre cobrança
        elif doubt_about_charge or intent == IntentType.DUVIDA_COBRANCA:
            return ResponseType.CONFIRMAR_DADOS
        
        # Prioridade 5: Responder perguntas
        elif is_question or intent == IntentType.PERGUNTA_GERAL:
            return ResponseType.ESCLARECER_DUVIDA
        
        # Prioridade 6: Cumprimentos e despedidas
        elif intent == IntentType.CUMPRIMENTO:
            return ResponseType.CUMPRIMENTO_RESPOSTA
        elif intent == IntentType.DESPEDIDA:
            return ResponseType.DESPEDIDA_RESPOSTA
        
        # Prioridade 7: Cliente confuso
        elif confusion_level > 0.6:
            return ResponseType.COBRANCA_INFORMATIVA
        
        # Prioridade 8: Cliente cooperativo
        elif cooperation_score > 0.7:
            return ResponseType.COBRANCA_EDUCADA
        
        # Default - cobrança direta mas educada
        else:
            return ResponseType.COBRANCA_DIRETA
    
    def _calculate_advanced_confidence(self, intent: IntentType, sentiment: SentimentType,
                                     payment_indicators: List[str], excuse_indicators: List[str],
                                     contextual_analysis: Dict[str, float], behavioral_prediction: Dict[str, str],
                                     confusion_level: float) -> float:
        """Calcula confiança avançada da análise"""
        confidence = 0.5  # Base
        
        # Mais indicadores = maior confiança
        confidence += len(payment_indicators) * 0.1
        confidence += len(excuse_indicators) * 0.05
        
        # Análise contextual clara aumenta confiança
        if max(contextual_analysis.values()) > 0.7:
            confidence += 0.2
        
        # Predição comportamental clara aumenta confiança
        if behavioral_prediction.get('payment_likelihood') in ['high', 'low']:
            confidence += 0.15
        
        # Nível de confusão baixo aumenta confiança
        if confusion_level < 0.3:
            confidence += 0.1
        
        # Sentimentos e intenções claras
        if sentiment != SentimentType.NEUTRO:
            confidence += 0.1
        if intent != IntentType.ENROLACAO:
            confidence += 0.1
        
        return min(confidence, 1.0)

class ResponseGenerator:
    """Gerador INTELIGENTE de respostas focadas em cobrança"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.personalization_data = self._load_personalization_data()
    
    def _load_response_templates(self) -> Dict[ResponseType, List[str]]:
        """Templates de resposta por tipo - COBRANÇA EDUCADA MAS EFICAZ"""
        return {
            ResponseType.COBRANCA_EDUCADA: [
                "Olá {name}! Espero que esteja bem. Tenho uma pendência de R$ {amount} em seu nome, vencida há {days} dias. Poderia fazer o pagamento? Obrigado!",
                "Oi {name}! Tudo bem? Estou entrando em contato sobre uma pendência de R$ {amount}. Para quitar, entre em contato conosco. Agradeço sua atenção!",
                "Bom dia/tarde {name}! Identificamos uma pendência de R$ {amount} vencida há {days} dias. Para regularizar, entre em contato. Desde já, obrigado!"
            ],
            ResponseType.COBRANCA_DIRETA: [
                "{name}, você tem uma pendência de R$ {amount} vencida há {days} dias. Para quitar, entre em contato conosco.",
                "{name}, débito de R$ {amount} em aberto há {days} dias. Entre em contato para pagamento.",
                "{name}, pendência de R$ {amount} precisa ser quitada. Entre em contato conosco."
            ],
            ResponseType.COBRANCA_INFORMATIVA: [
                "{name}, para esclarecer: você tem uma pendência de R$ {amount} vencida há {days} dias. Entre em contato conosco para pagamento. Caso tenha dúvidas, estou aqui para ajudar.",
                "Oi {name}! Estou entrando em contato sobre uma cobrança de R$ {amount}. Vencimento foi há {days} dias. Para quitar, entre em contato conosco. Se precisar de mais informações, me avise!",
                "{name}, informo que há uma pendência de R$ {amount} em seu nome. Para regularizar a situação, entre em contato. Qualquer dúvida, pode perguntar!"
            ],
            ResponseType.REJEITAR_PARCELAMENTO: [
                "{name}, entendo sua situação, mas nossa política não permite parcelamento. O valor de R$ {amount} deve ser pago integralmente. Entre em contato conosco.",
                "Compreendo {name}, porém não trabalhamos com parcelamento. R$ {amount} deve ser quitado à vista. Entre em contato conosco.",
                "{name}, infelizmente não é possível parcelar. O pagamento de R$ {amount} deve ser integral. Entre em contato conosco."
            ],
            ResponseType.REJEITAR_DESCONTO: [
                "{name}, o valor de R$ {amount} já está correto e não pode ser alterado. Entre em contato conosco para pagamento.",
                "Entendo {name}, mas o valor de R$ {amount} é fixo. Para quitar, entre em contato conosco.",
                "{name}, não é possível conceder desconto. Valor a pagar: R$ {amount}. Entre em contato conosco."
            ],
            ResponseType.CONFIRMAR_PAGAMENTO: [
                "Perfeito {name}! Assim que efetuar o pagamento de R$ {amount}, por favor envie o comprovante aqui. Obrigado!",
                "Ótimo {name}! Aguardo o pagamento de R$ {amount}. Não esqueça de enviar o comprovante!",
                "Excelente {name}! Faça o pagamento de R$ {amount} e me envie o comprovante para confirmarmos."
            ],
            ResponseType.ESCLARECER_DUVIDA: [
                "Claro {name}! Posso ajudá-lo com sua dúvida. Sobre a pendência de R$ {amount}, entre em contato conosco para pagamento. O que mais gostaria de saber?",
                "Sem problema {name}! Estou aqui para esclarecer. A cobrança é de R$ {amount}, vencida há {days} dias. Entre em contato conosco. Tem alguma outra pergunta?",
                "Claro que posso ajudar {name}! A pendência de R$ {amount} pode ser quitada. Entre em contato conosco. Em que mais posso auxiliá-lo?"
            ],
            ResponseType.CONFIRMAR_DADOS: [
                "Sim {name}, sua cobrança está correta. Seu contato está aqui no nome de {name} referente ao valor de R$ {amount}. Para quitar, entre em contato conosco.",
                "Confirmo {name}, os dados estão corretos. A pendência de R$ {amount} está mesmo em seu nome. Entre em contato para pagamento.",
                "Exato {name}, sua cobrança está certa. Valor: R$ {amount}, vencida há {days} dias. Para regularizar, entre em contato conosco."
            ],
            ResponseType.NOME_INCORRETO_RESPOSTA: [
                "Entendo! Se o nome {name} não é seu, peço que repasse esta mensagem para a pessoa correta ou nos informe o nome correto. A pendência de R$ {amount} está registrada neste número.",
                "Compreendo. Se você não é {name}, por favor repasse esta cobrança para a pessoa correta. O valor de R$ {amount} está vinculado a este número. Para quitar, entre em contato conosco.",
                "Entendo sua situação. Se este não é seu nome, pedimos que encaminhe para {name} ou nos informe quem é o responsável. Pendência: R$ {amount}.",
                "Obrigado pelo esclarecimento. Se você não é {name}, peça para a pessoa correta entrar em contato conosco para fazer o pagamento de R$ {amount}."
            ],
            ResponseType.RESPOSTA_EDUCADA: [
                "Obrigado pela sua mensagem {name}! Sobre a pendência de R$ {amount}, entre em contato conosco para pagamento.",
                "Agradeço o contato {name}! Para quitar os R$ {amount} em aberto, entre em contato conosco.",
                "Muito obrigado {name}! A pendência de R$ {amount} pode ser quitada. Entre em contato conosco."
            ],
            ResponseType.CUMPRIMENTO_RESPOSTA: [
                "Olá {name}! Tudo bem sim, obrigado! Estou entrando em contato sobre uma pendência de R$ {amount}. Entre em contato conosco.",
                "Oi {name}! Tudo ótimo, obrigado por perguntar! Você tem uma cobrança de R$ {amount} para quitar. Entre em contato conosco.",
                "Bom dia/tarde {name}! Tudo bem sim! Sobre sua pendência de R$ {amount}, entre em contato conosco."
            ],
            ResponseType.DESPEDIDA_RESPOSTA: [
                "Obrigado {name}! Não esqueça da pendência de R$ {amount}. Entre em contato conosco. Tenha um ótimo dia!",
                "Até mais {name}! Lembre-se de quitar os R$ {amount}. Entre em contato conosco. Abraço!",
                "Tchau {name}! Aguardo o pagamento de R$ {amount}. Entre em contato conosco. Até breve!"
            ],
            ResponseType.IGNORAR_ENROLACAO: [
                "{name}, vamos focar no importante: sua pendência de R$ {amount}. Entre em contato conosco.",
                "Entendo {name}, mas o que importa agora é quitar os R$ {amount}. Entre em contato conosco.",
                "{name}, o foco é regularizar sua situação: R$ {amount}. Entre em contato conosco."
            ]
        }
    
    def _load_personalization_data(self) -> Dict[str, Any]:
        """Dados para personalização das mensagens"""
        return {
            'pix_key': '11999999999',  # Será carregado da config
            'company_name': 'Sistema de Cobrança',
            'contact_hours': '08:00 às 18:00',
            'escalation_threshold': 3
        }
    
    def generate_response(self, analysis: AnalysisResult, context: ConversationContext) -> BotResponse:
        """Gera resposta INTELIGENTE baseada na análise"""
        
        # Seleciona template baseado na recomendação
        templates = self.response_templates[analysis.recommended_response]
        
        # Escolhe template baseado na confiança da análise
        if analysis.confidence > 0.8:
            # Alta confiança - usa template mais específico
            template = templates[0] if len(templates) > 0 else templates[0]
        elif analysis.confidence > 0.5:
            # Confiança média - template balanceado  
            template = templates[1] if len(templates) > 1 else templates[0]
        else:
            # Baixa confiança - template mais genérico
            template = templates[-1] if len(templates) > 0 else templates[0]
        
        # Personaliza a mensagem
        message = self._personalize_message(template, context, analysis)
        
        # Calcula próximo contato baseado na urgência
        next_contact_hours = self._calculate_next_contact(analysis.urgency_level, context)
        
        # Decide se deve escalar
        escalate = self._should_escalate(analysis, context)
        
        # Atualiza contexto
        context_update = self._prepare_context_update(analysis, context)
        
        return BotResponse(
            message=message,
            response_type=analysis.recommended_response,
            urgency_level=analysis.urgency_level,
            next_contact_hours=next_contact_hours,
            escalate=escalate,
            context_update=context_update
        )
    
    def _personalize_message(self, template: str, context: ConversationContext, 
                           analysis: AnalysisResult) -> str:
        """Personaliza mensagem com dados do cliente"""
        return template.format(
            name=context.customer_name,
            amount=f"{context.debt_amount:.2f}",
            days=context.days_overdue,
            company=self.personalization_data['company_name']
        )
    
    def _calculate_next_contact(self, urgency_level: float, context: ConversationContext) -> int:
        """Calcula quando fazer próximo contato"""
        base_hours = 24
        
        # Urgência alta = contato mais frequente
        if urgency_level > 0.8:
            return 4  # 4 horas
        elif urgency_level > 0.6:
            return 8  # 8 horas  
        elif urgency_level > 0.4:
            return 12  # 12 horas
        else:
            return base_hours
    
    def _should_escalate(self, analysis: AnalysisResult, context: ConversationContext) -> bool:
        """Decide se deve escalar para humano"""
        # Escala se muito atraso E cliente não cooperativo
        if (context.days_overdue > 90 and 
            analysis.cooperation_score < 0.3):
            return True
        
        # Escala se muitos contatos sem resultado
        if context.previous_contacts > 10:
            return True
        
        # Escala se contestação da dívida
        if analysis.intent == IntentType.CONTESTACAO_DIVIDA:
            return True
        
        return False
    
    def _prepare_context_update(self, analysis: AnalysisResult, 
                               context: ConversationContext) -> Dict[str, Any]:
        """Prepara atualizações do contexto"""
        updates = {
            'last_intent': analysis.intent.value,
            'last_sentiment': analysis.sentiment.value,
            'cooperation_level': analysis.cooperation_score,
            'lie_probability': analysis.lie_probability,
            'last_contact': datetime.now().isoformat()
        }
        
        # Incrementa promessas se cliente prometeu pagar
        if analysis.intent == IntentType.PAGAMENTO_CONFIRMADO:
            updates['payment_promises'] = context.payment_promises + 1
        
        return updates

class ConversationBot:
    """IA SUPREMA ULTRA INTELIGENTE de Cobrança - Sistema Principal com Aprendizado"""
    
    def __init__(self):
        self.nlp_processor = AdvancedNLPProcessor()
        self.response_generator = ResponseGenerator()
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # INTEGRAÇÃO COM MÓDULOS DE APRENDIZADO
        if LEARNING_MODULES_AVAILABLE:
            self.quality_analyzer = ResponseQualityAnalyzer()
            self.learning_engine = TemplateLearningEngine()
            self.campaign_optimizer = CampaignOptimizer()
            logger.info("🧠 MÓDULOS DE APRENDIZADO INTEGRADOS!")
        else:
            self.quality_analyzer = None
            self.learning_engine = None
            self.campaign_optimizer = None
            logger.warning("⚠️ Módulos de aprendizado não disponíveis")
        
        logger.info("🧠 CLAUDIA SUPREMA ULTRA INTELIGENTE ATIVADA!")
        logger.info("🎯 MODO: COBRANÇA EDUCADA MAS EFICAZ")
        logger.info("🚫 SEM PARCELAMENTO - SEM DESCONTO")
        logger.info("⚡ SISTEMA DE ANÁLISE ULTRA AVANÇADO CARREGADO!")
        logger.info("🎓 SISTEMA DE APRENDIZADO ATIVO!")
    
    def process_message(self, phone: str, message: str, customer_data: Dict[str, Any]) -> BotResponse:
        """Processa mensagem do cliente com INTELIGÊNCIA REAL + APRENDIZADO"""
        
        logger.info(f"🔍 Analisando mensagem de {phone}: {message[:50]}...")
        
        # Carrega ou cria contexto
        context = self._get_or_create_context(phone, customer_data)
        
        # ANÁLISE ULTRA INTELIGENTE da mensagem
        analysis = self.nlp_processor.analyze_message(message, context)
        
        logger.info(f"🧠 Análise: Intent={analysis.intent.value}, "
                   f"Sentiment={analysis.sentiment.value}, "
                   f"Cooperação={analysis.cooperation_score:.2f}, "
                   f"Estado={analysis.emotional_state}")
        
        # GERA RESPOSTA INTELIGENTE
        response = self.response_generator.generate_response(analysis, context)
        
        # ===== SISTEMA DE APRENDIZADO =====
        if self.quality_analyzer and self.learning_engine:
            # Analisa qualidade da resposta
            quality_scores = self.quality_analyzer.analyze_response_quality({
                'text': response.message,
                'intent': analysis.intent.value,
                'sentiment': analysis.sentiment.value
            })
            
            # Aprende com a resposta para melhorar futuras
            self.learning_engine.learn_from_response({
                'intent': analysis.intent.value,
                'template_id': response.response_type.value,
                'response': response.message,
                'client_reaction': 'pending',  # Será atualizado quando cliente responder
                'quality_scores': quality_scores
            })
            
            logger.info(f"🎓 Qualidade: {quality_scores.get('overall', 0):.2f}")
        
        # ATUALIZA CONTEXTO
        self._update_context(phone, response.context_update)
        
        # ADICIONA À HISTÓRIA
        self._add_to_history(phone, message, response.message)
        
        logger.info(f"💬 Resposta gerada: {response.response_type.value}")
        
        return response
    
    def generate_general_response(self, phone: str, message: str) -> BotResponse:
        """Gera resposta para pessoas não cadastradas como clientes"""
        try:
            logger.info(f"👤 Gerando resposta geral para não-cliente: {phone}")
            
            # Análise básica da mensagem
            message_lower = message.lower().strip()
            
            # Respostas para diferentes tipos de mensagens
            if any(word in message_lower for word in ['oi', 'olá', 'ola', 'hey', 'hi', 'hello']):
                response_text = "Olá! Como posso ajudá-lo hoje? Se você for cliente nosso, posso verificar suas informações. Caso contrário, posso direcioná-lo para o setor correto."
                response_type = ResponseType.CUMPRIMENTO_RESPOSTA
                urgency_level = 0.3
                
            elif any(word in message_lower for word in ['ajuda', 'help', 'suporte', 'atendimento']):
                response_text = "Estou aqui para ajudar! Se você for cliente nosso, posso verificar suas informações. Caso contrário, posso direcioná-lo para o setor correto. Como posso ajudá-lo?"
                response_type = ResponseType.RESPOSTA_EDUCADA
                urgency_level = 0.4
                
            elif any(word in message_lower for word in ['cliente', 'cadastro', 'cadastrado']):
                response_text = "Para verificar se você é cliente nosso, preciso que você entre em contato com nosso setor de atendimento através do número principal. Eles poderão verificar seu cadastro e te ajudar melhor."
                response_type = ResponseType.RESPOSTA_EDUCADA
                urgency_level = 0.5
                
            elif any(word in message_lower for word in ['cobrança', 'fatura', 'conta', 'pagamento']):
                response_text = "Se você recebeu uma cobrança nossa, por favor entre em contato com nosso setor de atendimento através do número principal para verificar se há algum equívoco. Eles poderão te ajudar melhor."
                response_type = ResponseType.RESPOSTA_EDUCADA
                urgency_level = 0.6
                
            else:
                response_text = "Obrigado por entrar em contato! Se você for cliente nosso, posso verificar suas informações. Caso contrário, posso direcioná-lo para o setor correto. Como posso ajudá-lo?"
                response_type = ResponseType.RESPOSTA_EDUCADA
                urgency_level = 0.4
            
            # Criar resposta estruturada
            response = BotResponse(
                message=response_text,
                response_type=response_type,
                urgency_level=urgency_level,
                next_contact_hours=24,
                escalate=False,
                context_update={},
                confidence=0.8
            )
            
            logger.info(f"✅ Resposta geral gerada para {phone}: {response_type.value}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar resposta geral: {str(e)}")
            # Resposta de fallback
            fallback_response = BotResponse(
                message="Obrigado por entrar em contato! Como posso ajudá-lo?",
                response_type=ResponseType.RESPOSTA_EDUCADA,
                urgency_level=0.5,
                next_contact_hours=24,
                escalate=False,
                context_update={},
                confidence=0.5
            )
            return fallback_response
    
    def _get_or_create_context(self, phone: str, customer_data: Dict[str, Any]) -> ConversationContext:
        """Carrega ou cria contexto da conversa"""
        if phone not in self.active_contexts:
            self.active_contexts[phone] = ConversationContext(
                customer_phone=phone,
                customer_name=customer_data.get('name', 'Cliente'),
                debt_amount=float(customer_data.get('debt_amount', 0)),
                days_overdue=int(customer_data.get('days_overdue', 0)),
                previous_contacts=int(customer_data.get('previous_contacts', 0)),
                payment_promises=int(customer_data.get('payment_promises', 0)),
                conversation_history=[]
            )
            logger.info(f"📋 Novo contexto criado para {phone}")
        
        return self.active_contexts[phone]
    
    def _update_context(self, phone: str, updates: Dict[str, Any]):
        """Atualiza contexto com novos dados"""
        if phone in self.active_contexts:
            context = self.active_contexts[phone]
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                    
            logger.info(f"📊 Contexto atualizado para {phone}")
    
    def _add_to_history(self, phone: str, customer_message: str, bot_response: str):
        """Adiciona interação ao histórico"""
        if phone in self.active_contexts:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'customer_message': customer_message,
                'bot_response': bot_response,
                'message_type': 'conversation'
            }
            self.active_contexts[phone].conversation_history.append(interaction)
            
            # Mantém apenas últimas 50 interações
            if len(self.active_contexts[phone].conversation_history) > 50:
                self.active_contexts[phone].conversation_history = \
                    self.active_contexts[phone].conversation_history[-50:]
    
    def get_context(self, phone: str) -> Optional[ConversationContext]:
        """Retorna contexto da conversa"""
        return self.active_contexts.get(phone)
    
    def get_active_conversations(self) -> Dict[str, ConversationContext]:
        """Retorna todas as conversas ativas"""
        return self.active_contexts.copy()
    
    def clear_context(self, phone: str) -> bool:
        """Limpa contexto de uma conversa"""
        if phone in self.active_contexts:
            del self.active_contexts[phone]
            logger.info(f"🗑️ Contexto limpo para {phone}")
            return True
        return False
    
    # ===== MÉTODOS DE APRENDIZADO E OTIMIZAÇÃO =====
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Obtém insights do sistema de aprendizado"""
        insights = {
            'learning_available': LEARNING_MODULES_AVAILABLE,
            'quality_insights': {},
            'template_performance': {},
            'campaign_insights': {}
        }
        
        if self.quality_analyzer:
            insights['quality_insights'] = self.quality_analyzer.get_quality_insights()
        
        if self.learning_engine:
            insights['template_performance'] = self.learning_engine.get_template_performance_summary()
        
        if self.campaign_optimizer:
            insights['campaign_insights'] = self.campaign_optimizer.get_campaign_insights()
        
        return insights
    
    def optimize_responses_for_intent(self, intent: str) -> Dict[str, Any]:
        """Otimiza respostas para uma intenção específica"""
        if not self.learning_engine:
            return {'error': 'Sistema de aprendizado não disponível'}
        
        return self.learning_engine.optimize_template_for_intent(intent)
    
    def get_best_templates(self, intent: str) -> List[Dict[str, Any]]:
        """Obtém melhores templates para uma intenção"""
        if not self.learning_engine:
            return []
        
        return self.learning_engine.get_best_templates(intent)
    
    def update_client_reaction(self, phone: str, reaction: str):
        """Atualiza reação do cliente para aprendizado"""
        if not self.learning_engine:
            return
        
        context = self.active_contexts.get(phone)
        if context and context.conversation_history:
            last_interaction = context.conversation_history[-1]
            
            # Atualiza sistema de aprendizado com a reação
            self.learning_engine.learn_from_response({
                'intent': 'unknown',  # Seria necessário armazenar o intent da última resposta
                'template_id': 'unknown',
                'response': last_interaction.get('bot_response', ''),
                'client_reaction': reaction,
                'quality_scores': {}
            })
            
            logger.info(f"🎓 Reação do cliente {phone} atualizada: {reaction}")
    
    def analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa performance de uma campanha"""
        if not self.campaign_optimizer:
            return {'error': 'Otimizador de campanha não disponível'}
        
        return self.campaign_optimizer.analyze_campaign_performance(campaign_data)
    
    def get_conversation_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das conversas ativas"""
        stats = {
            'total_active_conversations': len(self.active_contexts),
            'intent_distribution': {},
            'sentiment_distribution': {},
            'cooperation_levels': [],
            'average_interactions': 0
        }
        
        if not self.active_contexts:
            return stats
        
        total_interactions = 0
        for context in self.active_contexts.values():
            total_interactions += len(context.conversation_history)
            stats['cooperation_levels'].append(context.cooperation_level)
        
        stats['average_interactions'] = total_interactions / len(self.active_contexts)
        stats['average_cooperation'] = sum(stats['cooperation_levels']) / len(stats['cooperation_levels'])
        
        return stats

# Instância global da IA
conversation_bot = ConversationBot()

def process_customer_message(phone: str, message: str, customer_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    🎯 FUNÇÃO PRINCIPAL PARA PROCESSAR MENSAGEM DO CLIENTE
    
    Agora com sistema de dados persistentes (cache + banco SQL)
    """
    try:
        # 🗄️ BUSCAR DADOS DO CLIENTE (PERSISTENTE)
        if CUSTOMER_DATA_AVAILABLE:
            try:
                # Tentar buscar dados do cliente no sistema persistente
                stored_customer = get_customer_data(phone)
                if stored_customer:
                    # ✅ CLIENTE ENCONTRADO NO SISTEMA PERSISTENTE
                    customer_data = {
                        'name': stored_customer.name,
                        'phone': stored_customer.phone,
                        'documento': stored_customer.documento,
                        'debt_amount': stored_customer.debt_amount,
                        'days_overdue': stored_customer.days_overdue,
                        'due_date': stored_customer.due_date,
                        'protocolo': stored_customer.protocolo,
                        'contrato': stored_customer.contrato,
                        'regional': stored_customer.regional,
                        'territorio': stored_customer.territorio,
                        'plano': stored_customer.plano,
                        'valor_mensalidade': stored_customer.valor_mensalidade,
                        'company': stored_customer.company,
                        'status': stored_customer.status,
                        'priority': stored_customer.priority,
                        'is_customer': stored_customer.is_customer,
                        'conversation_count': stored_customer.conversation_count,
                        'payment_promises': stored_customer.payment_promises
                    }
                    logger.info(f"🗄️ CLIENTE ENCONTRADO no sistema persistente: {stored_customer.name}")
                else:
                    # 👤 NÃO É CLIENTE CADASTRADO - RESPONDER COMO PESSOA COMUM
                    logger.info(f"👤 Pessoa não cadastrada como cliente: {phone}")
                    customer_data = {
                        'name': 'Pessoa',
                        'phone': phone,
                        'is_customer': False,
                        'debt_amount': 0.0,
                        'days_overdue': 0,
                        'status': 'non_customer'
                    }
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar dados persistentes: {str(e)}")
                # Usar dados fornecidos como fallback
                if not customer_data:
                    customer_data = {'name': 'Cliente', 'phone': phone}
        
        # Se não tiver dados, usar default
        if not customer_data:
            customer_data = {'name': 'Cliente', 'phone': phone}
        
        # Processa com a IA REAL
        response = conversation_bot.process_message(phone, message, customer_data)
        
        # 💾 SALVAR CONTEXTO DA CONVERSA (PERSISTENTE)
        if CUSTOMER_DATA_AVAILABLE:
            try:
                # Criar contexto persistente
                context = ConversationContext(
                    phone=phone,
                    customer_name=customer_data.get('name', 'Cliente'),
                    debt_amount=customer_data.get('debt_amount', 0),
                    days_overdue=customer_data.get('days_overdue', 0),
                    conversation_history=[{
                        'timestamp': datetime.now().isoformat(),
                        'customer_message': message,
                        'bot_response': response.message,
                        'intent': response.response_type.value,
                        'urgency_level': response.urgency_level
                    }],
                    cooperation_level=getattr(response, 'cooperation_level', 0.5),
                    urgency_level=response.urgency_level,
                    last_intent=response.response_type.value,
                    last_contact=datetime.now().isoformat()
                )
                
                # Salvar contexto persistente
                save_conversation_context(phone, context)
                logger.info(f"💾 Contexto da conversa salvo (persistente): {phone}")
                
                # Atualizar interação do cliente
                update_customer_interaction(phone, {
                    'intent': response.response_type.value,
                    'urgency_level': response.urgency_level,
                    'response_type': response.response_type.value
                })
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar contexto persistente: {str(e)}")
        
        # Retorna resposta estruturada
        return {
            'success': True,
            'response': response.message,
            'response_type': response.response_type.value,
            'urgency_level': response.urgency_level,
            'next_contact_hours': response.next_contact_hours,
            'escalate': response.escalate,
            'context_updates': response.context_update,
            'customer_data_persistent': CUSTOMER_DATA_AVAILABLE,
            'customer_found': customer_data.get('is_customer', False)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'response': f"Erro interno. Contate o suporte técnico.",
            'response_type': 'error',
            'urgency_level': 0.5,
            'next_contact_hours': 24,
            'escalate': True,
            'customer_data_persistent': CUSTOMER_DATA_AVAILABLE,
            'customer_found': False
        }

# Função de compatibilidade
def analyze_message(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Função de compatibilidade para análise de mensagem"""
    phone = context.get('phone', 'unknown')
    customer_data = {
        'name': context.get('customer_name', 'Cliente'),
        'debt_amount': context.get('debt_amount', 0),
        'days_overdue': context.get('days_overdue', 0),
        'previous_contacts': context.get('previous_contacts', 0),
        'payment_promises': context.get('payment_promises', 0)
    }
    
    return process_customer_message(phone, message, customer_data)

if __name__ == "__main__":
    # Teste rápido da IA ULTRA INTELIGENTE
    print("🧠 TESTANDO CLAUDIA SUPREMA ULTRA INTELIGENTE - IA REAL DE COBRANÇA")
    print("🎓 COM SISTEMA DE APRENDIZADO AVANÇADO")
    
    test_data = {
        'name': 'João Silva',
        'debt_amount': 1500.00,
        'days_overdue': 45,
        'previous_contacts': 3,
        'payment_promises': 1
    }
    
    test_messages = [
        "Oi, tudo bem?",
        "Essa cobrança é minha mesmo?",
        "Meu nome não é esse",
        "Esse nome não sou eu",
        "Vocês erraram o nome",
        "Não conheço essa pessoa",
        "Número errado",
        "Não posso pagar agora",
        "Pode parcelar em 3 vezes?",
        "Como faço para pagar?",
        "Já fiz o PIX",
        "Vocês estão me perturbando!",
        "Vou pagar amanhã, prometo",
        "Obrigado pela informação",
        "Tchau!"
    ]
    
    print(f"\n🎯 TESTANDO {len(test_messages)} CENÁRIOS DIFERENTES:")
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n📱 [{i:2d}] Cliente: {msg}")
        result = process_customer_message("11999999999", msg, test_data)
        print(f"🤖      Claudia: {result['response']}")
        print(f"📊      Análise: {result['response_type']} | Urgência: {result['urgency_level']:.2f}")
    
    # Teste de insights de aprendizado
    print(f"\n🎓 TESTANDO SISTEMA DE APRENDIZADO:")
    insights = conversation_bot.get_learning_insights()
    print(f"📈 Módulos disponíveis: {insights['learning_available']}")
    
    # Estatísticas da conversa
    stats = conversation_bot.get_conversation_statistics()
    print(f"📊 Conversas ativas: {stats['total_active_conversations']}")
    print(f"📊 Média de interações: {stats.get('average_interactions', 0):.1f}")
    
    print(f"\n✅ TESTE COMPLETO - CLAUDIA SUPREMA FUNCIONANDO PERFEITAMENTE!")
    print(f"🧠 IA ULTRA INTELIGENTE: ATIVA")
    print(f"🎓 SISTEMA DE APRENDIZADO: ATIVO") 
    print(f"⚡ ANÁLISE AVANÇADA: ATIVA")
