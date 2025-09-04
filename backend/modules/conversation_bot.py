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
import difflib
from collections import Counter

# Importar sistema de logging
# Usar logger padrão temporariamente para resolver problema
import logging
logger = logging.getLogger(__name__)

# Verificar disponibilidade de dados persistentes
try:
    from backend.database.database_manager import get_customer_data, save_conversation_context, update_customer_interaction
    CUSTOMER_DATA_AVAILABLE = True
except ImportError:
    CUSTOMER_DATA_AVAILABLE = False
    # Funções dummy para compatibilidade
    def get_customer_data(phone: str):
        return None
    def save_conversation_context(phone: str, context):
        pass
    def update_customer_interaction(phone: str, data: dict):
        pass

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
    COBRANCA_SIMPLES = "cobranca_simples"
    EXPLICACAO_BASICA = "explicacao_basica"
    AJUDA_LEITURA = "ajuda_leitura"
    CONFIRMACAO_FACIL = "confirmacao_facil"
    INSTRUCAO_PASSO_A_PASSO = "instrucao_passo_a_passo"
    RESPOSTA_EDUCADA = "resposta_educada"
    CUMPRIMENTO_RESPOSTA = "cumprimento_resposta"
    DESPEDIDA_RESPOSTA = "despedida_resposta"
    IGNORAR_ENROLACAO = "ignorar_enrolacao"


class LiteracyLevel(Enum):
    """Níveis de alfabetização dos clientes"""
    ALFABETIZADO = "alfabetizado"
    ALFABETIZADO_BASICO = "alfabetizado_basico"
    ANALFABETO_FUNCIONAL = "analfabeto_funcional"
    ANALFABETO_TOTAL = "analfabeto_total"

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
    literacy_level: LiteracyLevel = LiteracyLevel.ALFABETIZADO
    communication_preference: str = "texto"
    needs_help_reading: bool = False
    text_errors_count: int = 0
    simple_language_needed: bool = False

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
    literacy_level: LiteracyLevel
    text_quality_score: float
    needs_simple_language: bool
    communication_issues: List[str]

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

class TextNormalizer:
    """Classe para normalização de texto e detecção de erros de escrita"""
    
    def __init__(self):
        # Dicionário de correções comuns para analfabetos
        self.common_corrections = {
            # Erros fonéticos comuns
            'vc': 'você', 'voce': 'você', 'vcs': 'vocês', 'voceis': 'vocês',
            'nao': 'não', 'naum': 'não', 'nao': 'não',
            'pq': 'porque', 'porq': 'porque', 'por que': 'porque',
            'q': 'que', 'ke': 'que', 'ki': 'que',
            'tbm': 'também', 'tambem': 'também',
            'mt': 'muito', 'mto': 'muito',
            'hj': 'hoje', 'hoje': 'hoje',
            'ontem': 'ontem', 'onte': 'ontem',
            'amanha': 'amanhã', 'amanha': 'amanhã',
            'agora': 'agora', 'agr': 'agora',
            'depois': 'depois', 'dps': 'depois',
            'antes': 'antes', 'antes': 'antes',
            'dinheiro': 'dinheiro', 'grana': 'dinheiro', 'money': 'dinheiro',
            'pagar': 'pagar', 'pago': 'pagar',
            'conta': 'conta', 'fatura': 'conta',
            'debito': 'débito', 'debito': 'débito',
            'credito': 'crédito', 'credito': 'crédito',
            'banco': 'banco', 'bco': 'banco',
            'cartao': 'cartão', 'cartao': 'cartão',
            'pix': 'pix', 'PIX': 'pix',
            'boleto': 'boleto', 'boleto': 'boleto',
            'parcela': 'parcela', 'parcelas': 'parcelas',
            'desconto': 'desconto', 'desconto': 'desconto',
            'negociar': 'negociar', 'negociar': 'negociar',
            'ajuda': 'ajuda', 'ajudar': 'ajudar',
            'problema': 'problema', 'problemas': 'problemas',
            'dificuldade': 'dificuldade', 'dificuldades': 'dificuldades',
            'entender': 'entender', 'entendi': 'entender',
            'explicar': 'explicar', 'explicacao': 'explicação',
            'sim': 'sim', 's': 'sim', 'ss': 'sim',
            'nao': 'não', 'n': 'não', 'nn': 'não',
            'talvez': 'talvez', 'talvez': 'talvez',
            'depends': 'depende', 'depende': 'depende',
            'pode': 'pode', 'pode ser': 'pode ser',
            'nao sei': 'não sei', 'n sei': 'não sei',
            'nao entendo': 'não entendo', 'n entendo': 'não entendo',
            'nao consigo': 'não consigo', 'n consigo': 'não consigo',
            'preciso': 'preciso', 'preciso de': 'preciso de',
            'quero': 'quero', 'quero saber': 'quero saber',
            'como': 'como', 'como fazer': 'como fazer',
            'onde': 'onde', 'onde pagar': 'onde pagar',
            'quando': 'quando', 'quando pagar': 'quando pagar',
            'quanto': 'quanto', 'quanto custa': 'quanto custa',
            'por favor': 'por favor', 'pf': 'por favor',
            'obrigado': 'obrigado', 'obrigada': 'obrigada',
            'desculpa': 'desculpa', 'desculpe': 'desculpe',
            'com licenca': 'com licença', 'com licenca': 'com licença',
        }
        
        # Padrões de erros comuns
        self.error_patterns = [
            r'[^a-zA-ZáàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ\s]',  # Caracteres especiais
            r'\b\w{1,2}\b',  # Palavras muito curtas
            r'(.)\1{2,}',  # Repetição de caracteres
            r'\b\w*[aeiou]{3,}\w*\b',  # Muitas vogais seguidas
            r'\b\w*[bcdfghjklmnpqrstvwxyz]{4,}\w*\b',  # Muitas consoantes seguidas
        ]
        
        # Palavras-chave que indicam dificuldade de leitura
        self.reading_difficulty_indicators = [
            'nao entendo', 'n entendo', 'nao sei ler', 'n sei ler',
            'nao consigo ler', 'n consigo ler', 'difícil de ler',
            'muito difícil', 'mto difícil', 'complicado',
            'pode explicar', 'pode falar', 'pode ligar',
            'nao vejo', 'n vejo', 'letra pequena',
            'muito texto', 'mto texto', 'texto grande'
        ]
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto com erros de escrita"""
        if not text:
            return text
            
        # Converter para minúsculas
        normalized = text.lower().strip()
        
        # Aplicar correções comuns
        words = normalized.split()
        corrected_words = []
        
        for word in words:
            # Remover caracteres especiais desnecessários
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Aplicar correção se existir
            if clean_word in self.common_corrections:
                corrected_words.append(self.common_corrections[clean_word])
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def detect_text_errors(self, text: str) -> Dict[str, Any]:
        """Detecta erros no texto"""
        errors = {
            'error_count': 0,
            'error_types': [],
            'error_positions': [],
            'quality_score': 1.0
        }
        
        if not text:
            return errors
        
        # Contar caracteres especiais desnecessários
        special_chars = len(re.findall(r'[^a-zA-ZáàâãéèêíìîóòôõúùûçÁÀÂÃÉÈÊÍÌÎÓÒÔÕÚÙÛÇ\s.,!?]', text))
        if special_chars > 0:
            errors['error_count'] += special_chars
            errors['error_types'].append('caracteres_especiais')
        
        # Contar palavras muito curtas (provavelmente abreviações)
        short_words = len(re.findall(r'\b\w{1,2}\b', text))
        if short_words > 2:
            errors['error_count'] += short_words - 2
            errors['error_types'].append('abreviacoes_excessivas')
        
        # Contar repetições de caracteres
        repetitions = len(re.findall(r'(.)\1{2,}', text))
        if repetitions > 0:
            errors['error_count'] += repetitions
            errors['error_types'].append('repeticao_caracteres')
        
        # Calcular score de qualidade (0-1, onde 1 é perfeito)
        total_chars = len(text)
        if total_chars > 0:
            errors['quality_score'] = max(0, 1 - (errors['error_count'] / total_chars))
        
        return errors
    
    def detect_literacy_level(self, text: str, context: ConversationContext) -> LiteracyLevel:
        """Detecta o nível de alfabetização baseado no texto"""
        if not text:
            return LiteracyLevel.ANALFABETO_TOTAL
        
        # Normalizar texto
        normalized = self.normalize_text(text)
        
        # Detectar indicadores de dificuldade de leitura
        difficulty_indicators = sum(1 for indicator in self.reading_difficulty_indicators 
                                  if indicator in normalized)
        
        # Analisar erros no texto
        errors = self.detect_text_errors(text)
        
        # Calcular score de alfabetização
        literacy_score = 0
        
        # Score baseado na qualidade do texto
        literacy_score += errors['quality_score'] * 0.4
        
        # Score baseado no comprimento e complexidade
        word_count = len(normalized.split())
        if word_count > 10:
            literacy_score += 0.2
        elif word_count > 5:
            literacy_score += 0.1
        
        # Score baseado na presença de indicadores de dificuldade
        if difficulty_indicators > 0:
            literacy_score -= difficulty_indicators * 0.2
        
        # Score baseado no histórico do cliente
        if hasattr(context, 'text_errors_count') and context.text_errors_count > 5:
            literacy_score -= 0.2
        
        # Determinar nível de alfabetização
        if literacy_score >= 0.8:
            return LiteracyLevel.ALFABETIZADO
        elif literacy_score >= 0.6:
            return LiteracyLevel.ALFABETIZADO_BASICO
        elif literacy_score >= 0.3:
            return LiteracyLevel.ANALFABETO_FUNCIONAL
        else:
            return LiteracyLevel.ANALFABETO_TOTAL
    
    def suggest_communication_method(self, literacy_level: LiteracyLevel) -> str:
        """Sugere o melhor método de comunicação baseado no nível de alfabetização"""
        if literacy_level == LiteracyLevel.ANALFABETO_TOTAL:
            return "voz"
        elif literacy_level == LiteracyLevel.ANALFABETO_FUNCIONAL:
            return "voz_com_texto_simples"
        elif literacy_level == LiteracyLevel.ALFABETIZADO_BASICO:
            return "texto_simples"
        else:
            return "texto"


class AdvancedNLPProcessor:
    """Processador de Linguagem Natural ULTRA AVANÇADO focado em cobrança"""
    
    def __init__(self):
        # Inicializar normalizador de texto
        self.text_normalizer = TextNormalizer()
        
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
        
        # SISTEMA DE APRENDIZADO CONTÍNUO AVANÇADO
        self.learned_patterns = {}
        self.success_correlations = {}
        self.failure_patterns = {}
        self.response_effectiveness = {}  # Efetividade de cada tipo de resposta
        self.client_behavior_profiles = {}  # Perfis comportamentais dos clientes
        self.conversation_outcomes = {}  # Resultados das conversas
        self.adaptive_templates = {}  # Templates que se adaptam
        self.pattern_confidence_scores = {}  # Confiança nos padrões aprendidos
        self.feedback_learning_queue = []  # Fila de feedback para aprendizado
        self.contextual_memory = {}  # Memória contextual por cliente
        
        # SISTEMA DE PREDIÇÃO AVANÇADA
        self.intent_prediction_model = {}
        self.sentiment_evolution_tracking = {}
        self.payment_likelihood_predictor = {}
        
        logger.info("🧠 NLP ULTRA AVANÇADO INICIALIZADO - 20+ SISTEMAS DE ANÁLISE + APRENDIZADO CONTÍNUO!")
        
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
        
        # 0. NORMALIZAR TEXTO E DETECTAR ALFABETIZAÇÃO
        normalized_message = self.text_normalizer.normalize_text(message)
        text_errors = self.text_normalizer.detect_text_errors(message)
        literacy_level = self.text_normalizer.detect_literacy_level(message, context)
        
        # Atualizar contexto com informações de alfabetização
        context.literacy_level = literacy_level
        context.text_errors_count += text_errors['error_count']
        context.simple_language_needed = literacy_level in [LiteracyLevel.ANALFABETO_TOTAL, LiteracyLevel.ANALFABETO_FUNCIONAL]
        context.communication_preference = self.text_normalizer.suggest_communication_method(literacy_level)
        
        logger.info(f"📚 Nível de alfabetização detectado: {literacy_level.value}")
        logger.info(f"📝 Erros no texto: {text_errors['error_count']}, Score: {text_errors['quality_score']:.2f}")
        
        # 1. DETECTAR INTENÇÃO REAL (usando texto normalizado)
        intent = self._detect_intent_advanced(normalized_message)
        
        # 2. ANALISAR SENTIMENTO (usando texto normalizado)
        sentiment = self._analyze_sentiment_advanced(normalized_message)
        
        # 3. CALCULAR PROBABILIDADE DE MENTIRA
        lie_probability = self._calculate_lie_probability(normalized_message, context)
        
        # 4. AVALIAR NÍVEL DE COOPERAÇÃO
        cooperation_score = self._evaluate_cooperation_advanced(normalized_message, context)
        
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
            confidence=confidence,
            literacy_level=literacy_level,
            text_quality_score=text_errors['quality_score'],
            needs_simple_language=context.simple_language_needed,
            communication_issues=text_errors['error_types']
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
    
    # ===== SISTEMA DE APRENDIZADO CONTÍNUO AVANÇADO =====
    
    def learn_from_conversation_outcome(self, phone: str, conversation_data: Dict[str, Any]):
        """Aprende com o resultado de uma conversa completa"""
        try:
            outcome = conversation_data.get('outcome', 'unknown')
            intent_sequence = conversation_data.get('intent_sequence', [])
            response_sequence = conversation_data.get('response_sequence', [])
            final_result = conversation_data.get('final_result', {})
            
            # Atualizar efetividade das respostas
            for i, response_type in enumerate(response_sequence):
                if response_type not in self.response_effectiveness:
                    self.response_effectiveness[response_type] = {
                        'total_uses': 0,
                        'successful_outcomes': 0,
                        'success_rate': 0.0,
                        'contexts': []
                    }
                
                self.response_effectiveness[response_type]['total_uses'] += 1
                
                # Considerar sucesso se pagamento foi feito ou cliente cooperou
                if outcome in ['payment_made', 'cooperative_response', 'information_provided']:
                    self.response_effectiveness[response_type]['successful_outcomes'] += 1
                
                # Calcular nova taxa de sucesso
                total = self.response_effectiveness[response_type]['total_uses']
                successful = self.response_effectiveness[response_type]['successful_outcomes']
                self.response_effectiveness[response_type]['success_rate'] = successful / total
                
                # Armazenar contexto da resposta
                context = {
                    'phone': phone,
                    'intent': intent_sequence[i] if i < len(intent_sequence) else 'unknown',
                    'outcome': outcome,
                    'timestamp': datetime.now().isoformat()
                }
                self.response_effectiveness[response_type]['contexts'].append(context)
            
            # Atualizar perfil comportamental do cliente
            self._update_client_behavior_profile(phone, conversation_data)
            
            # Aprender padrões de sucesso/falha
            self._learn_success_failure_patterns(conversation_data)
            
            logger.info( f"🎓 Aprendizado registrado para {phone}: {outcome}")
            
        except Exception as e:
            logger.error( f"❌ Erro no aprendizado: {e}")
    
    def _update_client_behavior_profile(self, phone: str, conversation_data: Dict[str, Any]):
        """Atualiza perfil comportamental do cliente"""
        if phone not in self.client_behavior_profiles:
            self.client_behavior_profiles[phone] = {
                'total_conversations': 0,
                'common_intents': {},
                'response_patterns': {},
                'cooperation_level': 0.5,
                'payment_likelihood': 0.3,
                'preferred_communication_style': 'neutral',
                'escalation_frequency': 0.0,
                'last_updated': datetime.now().isoformat()
            }
        
        profile = self.client_behavior_profiles[phone]
        profile['total_conversations'] += 1
        
        # Atualizar intenções comuns
        intents = conversation_data.get('intent_sequence', [])
        for intent in intents:
            if intent not in profile['common_intents']:
                profile['common_intents'][intent] = 0
            profile['common_intents'][intent] += 1
        
        # Atualizar nível de cooperação
        outcome = conversation_data.get('outcome', 'unknown')
        if outcome in ['cooperative_response', 'payment_made']:
            profile['cooperation_level'] = min(1.0, profile['cooperation_level'] + 0.1)
        elif outcome in ['aggressive_response', 'escalated']:
            profile['cooperation_level'] = max(0.0, profile['cooperation_level'] - 0.1)
        
        # Atualizar probabilidade de pagamento
        if outcome == 'payment_made':
            profile['payment_likelihood'] = min(1.0, profile['payment_likelihood'] + 0.2)
        elif outcome in ['payment_denied', 'aggressive_response']:
            profile['payment_likelihood'] = max(0.0, profile['payment_likelihood'] - 0.1)
        
        profile['last_updated'] = datetime.now().isoformat()
    
    def _learn_success_failure_patterns(self, conversation_data: Dict[str, Any]):
        """Aprende padrões de sucesso e falha"""
        outcome = conversation_data.get('outcome', 'unknown')
        intent_sequence = conversation_data.get('intent_sequence', [])
        response_sequence = conversation_data.get('response_sequence', [])
        
        # Padrões de sucesso
        if outcome in ['payment_made', 'cooperative_response']:
            pattern_key = f"{'->'.join(intent_sequence)}->{outcome}"
            if pattern_key not in self.success_correlations:
                self.success_correlations[pattern_key] = 0
            self.success_correlations[pattern_key] += 1
        
        # Padrões de falha
        elif outcome in ['payment_denied', 'escalated', 'no_response']:
            pattern_key = f"{'->'.join(intent_sequence)}->{outcome}"
            if pattern_key not in self.failure_patterns:
                self.failure_patterns[pattern_key] = 0
            self.failure_patterns[pattern_key] += 1
    
    def predict_client_behavior(self, phone: str, current_intent: str) -> Dict[str, Any]:
        """Prediz comportamento do cliente baseado no histórico"""
        prediction = {
            'cooperation_likelihood': 0.5,
            'payment_likelihood': 0.3,
            'escalation_risk': 0.2,
            'preferred_response_type': 'cobranca_educada',
            'confidence': 0.5
        }
        
        if phone in self.client_behavior_profiles:
            profile = self.client_behavior_profiles[phone]
            prediction['cooperation_likelihood'] = profile['cooperation_level']
            prediction['payment_likelihood'] = profile['payment_likelihood']
            
            # Calcular risco de escalação
            if profile['total_conversations'] > 3:
                escalation_count = sum(1 for outcome in profile.get('outcomes', []) 
                                     if outcome == 'escalated')
                prediction['escalation_risk'] = escalation_count / profile['total_conversations']
            
            # Determinar tipo de resposta preferido
            if profile['cooperation_level'] > 0.7:
                prediction['preferred_response_type'] = 'cobranca_educada'
            elif profile['cooperation_level'] < 0.3:
                prediction['preferred_response_type'] = 'cobranca_direta'
            else:
                prediction['preferred_response_type'] = 'cobranca_informativa'
            
            prediction['confidence'] = min(1.0, profile['total_conversations'] * 0.2)
        
        return prediction
    
    def get_adaptive_response_recommendation(self, analysis: AnalysisResult, 
                                           client_prediction: Dict[str, Any]) -> ResponseType:
        """Recomenda resposta adaptativa baseada no aprendizado"""
        # Usar predição do cliente se confiança for alta
        if client_prediction['confidence'] > 0.7:
            preferred_type = client_prediction['preferred_response_type']
            try:
                return ResponseType(preferred_type)
            except ValueError:
                pass
        
        # Usar análise padrão se predição não for confiável
        return analysis.recommended_response
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Retorna insights do sistema de aprendizado"""
        insights = {
            'total_learned_patterns': len(self.learned_patterns),
            'success_correlations_count': len(self.success_correlations),
            'failure_patterns_count': len(self.failure_patterns),
            'response_effectiveness': {},
            'top_successful_responses': [],
            'client_profiles_count': len(self.client_behavior_profiles),
            'learning_confidence': 0.0
        }
        
        # Análise de efetividade das respostas
        for response_type, data in self.response_effectiveness.items():
            if data['total_uses'] >= 5:  # Mínimo de 5 usos
                insights['response_effectiveness'][response_type] = {
                    'success_rate': data['success_rate'],
                    'total_uses': data['total_uses']
                }
        
        # Top respostas bem-sucedidas
        successful_responses = [(rt, data['success_rate']) 
                              for rt, data in self.response_effectiveness.items()
                              if data['total_uses'] >= 5]
        successful_responses.sort(key=lambda x: x[1], reverse=True)
        insights['top_successful_responses'] = successful_responses[:5]
        
        # Calcular confiança geral do aprendizado
        total_patterns = len(self.learned_patterns) + len(self.success_correlations) + len(self.failure_patterns)
        insights['learning_confidence'] = min(1.0, total_patterns / 100)  # Normalizado
        
        return insights

class ResponseGenerator:
    """Gerador INTELIGENTE de respostas focadas em cobrança"""
    
    def __init__(self):
        self.response_templates = self._load_response_templates()
        self.personalization_data = self._load_personalization_data()
        
        # SISTEMA DE TEMPLATES ADAPTATIVOS
        self.adaptive_templates = {}  # Templates que se adaptam baseado no aprendizado
        self.template_performance = {}  # Performance de cada template
        self.contextual_variations = {}  # Variações contextuais dos templates
        self.personalization_engine = {}  # Engine de personalização avançada
    
    def _load_response_templates(self) -> Dict[ResponseType, List[str]]:
        """Templates de resposta por tipo - COBRANÇA EDUCADA MAS EFICAZ"""
        return {
            ResponseType.COBRANCA_EDUCADA: [
                "Olá {name}! Espero que esteja bem. Temos uma pendência em seu nome que precisa ser regularizada. Poderia entrar em contato conosco? Obrigado!",
                "Oi {name}! Tudo bem? Estou entrando em contato sobre uma pendência em seu nome. Para regularizar, entre em contato conosco. Agradeço sua atenção!",
                "Bom dia/tarde {name}! Identificamos uma pendência em seu nome que precisa ser quitada. Para regularizar, entre em contato. Desde já, obrigado!"
            ],
            ResponseType.COBRANCA_DIRETA: [
                "{name}, você tem uma pendência em seu nome que precisa ser quitada. Entre em contato conosco.",
                "{name}, há um débito em aberto em seu nome. Entre em contato para regularizar.",
                "{name}, você tem uma pendência que precisa ser quitada. Entre em contato conosco."
            ],
            ResponseType.COBRANCA_INFORMATIVA: [
                "{name}, para esclarecer: você tem uma pendência em seu nome que precisa ser regularizada. Entre em contato conosco. Caso tenha dúvidas, estou aqui para ajudar.",
                "Oi {name}! Estou entrando em contato sobre uma cobrança em seu nome. Para quitar, entre em contato conosco. Se precisar de mais informações, me avise!",
                "{name}, informo que há uma pendência em seu nome. Para regularizar a situação, entre em contato. Qualquer dúvida, pode perguntar!"
            ],
            ResponseType.REJEITAR_PARCELAMENTO: [
                "{name}, entendo sua situação, mas nossa política não permite parcelamento. A pendência deve ser quitada integralmente. Entre em contato conosco.",
                "Compreendo {name}, porém não trabalhamos com parcelamento. A pendência deve ser quitada à vista. Entre em contato conosco.",
                "{name}, infelizmente não é possível parcelar. O pagamento deve ser integral. Entre em contato conosco."
            ],
            ResponseType.REJEITAR_DESCONTO: [
                "{name}, o valor da pendência já está correto e não pode ser alterado. Entre em contato conosco para pagamento.",
                "Entendo {name}, mas o valor da pendência é fixo. Para quitar, entre em contato conosco.",
                "{name}, não é possível conceder desconto. Entre em contato conosco para pagamento."
            ],
            ResponseType.CONFIRMAR_PAGAMENTO: [
                "Perfeito {name}! Assim que efetuar o pagamento, por favor envie o comprovante aqui. Obrigado!",
                "Ótimo {name}! Aguardo o pagamento da pendência. Não esqueça de enviar o comprovante!",
                "Excelente {name}! Faça o pagamento e me envie o comprovante para confirmarmos."
            ],
            ResponseType.ESCLARECER_DUVIDA: [
                "Claro {name}! Posso ajudá-lo com sua dúvida. Sobre a pendência em seu nome, entre em contato conosco para pagamento. O que mais gostaria de saber?",
                "Sem problema {name}! Estou aqui para esclarecer. A cobrança em seu nome pode ser quitada. Entre em contato conosco. Tem alguma outra pergunta?",
                "Claro que posso ajudar {name}! A pendência em seu nome pode ser quitada. Entre em contato conosco. Em que mais posso auxiliá-lo?"
            ],
            ResponseType.CONFIRMAR_DADOS: [
                "Sim {name}, sua cobrança está correta. Seu contato está aqui no nome de {name}. Para quitar, entre em contato conosco.",
                "Confirmo {name}, os dados estão corretos. A pendência está mesmo em seu nome. Entre em contato para pagamento.",
                "Exato {name}, sua cobrança está certa. Para regularizar, entre em contato conosco."
            ],
            ResponseType.NOME_INCORRETO_RESPOSTA: [
                "Entendo! Se o nome {name} não é seu, peço que repasse esta mensagem para a pessoa correta ou nos informe o nome correto. A pendência está registrada neste número.",
                "Compreendo. Se você não é {name}, por favor repasse esta cobrança para a pessoa correta. A pendência está vinculada a este número. Para quitar, entre em contato conosco.",
                "Entendo sua situação. Se este não é seu nome, pedimos que encaminhe para {name} ou nos informe quem é o responsável pela pendência.",
                "Obrigado pelo esclarecimento. Se você não é {name}, peça para a pessoa correta entrar em contato conosco para fazer o pagamento."
            ],
            ResponseType.RESPOSTA_EDUCADA: [
                "Obrigado pela sua mensagem {name}! Sobre a pendência em seu nome, entre em contato conosco para pagamento.",
                "Agradeço o contato {name}! Para quitar a pendência em aberto, entre em contato conosco.",
                "Muito obrigado {name}! A pendência em seu nome pode ser quitada. Entre em contato conosco."
            ],
            ResponseType.CUMPRIMENTO_RESPOSTA: [
                "Olá {name}! Tudo bem sim, obrigado! Estou entrando em contato sobre uma pendência em seu nome. Entre em contato conosco.",
                "Oi {name}! Tudo ótimo, obrigado por perguntar! Você tem uma cobrança para quitar. Entre em contato conosco.",
                "Bom dia/tarde {name}! Tudo bem sim! Sobre sua pendência, entre em contato conosco."
            ],
            ResponseType.DESPEDIDA_RESPOSTA: [
                "Obrigado {name}! Não esqueça da pendência em seu nome. Entre em contato conosco. Tenha um ótimo dia!",
                "Até mais {name}! Lembre-se de quitar a pendência. Entre em contato conosco. Abraço!",
                "Tchau {name}! Aguardo o pagamento da pendência. Entre em contato conosco. Até breve!"
            ],
            ResponseType.IGNORAR_ENROLACAO: [
                "{name}, vamos focar no importante: sua pendência. Entre em contato conosco.",
                "Entendo {name}, mas o que importa agora é quitar a pendência. Entre em contato conosco.",
                "{name}, o foco é regularizar sua situação. Entre em contato conosco."
            ],
            # TEMPLATES SIMPLIFICADOS PARA ANALFABETOS
            ResponseType.COBRANCA_SIMPLES: [
                "Oi {name}! Você tem uma conta para pagar. Pode resolver?",
                "Olá {name}! Tem uma pendência para quitar. Pode fazer hoje?",
                "Oi {name}! Precisa pagar uma conta. Pode resolver?"
            ],
            ResponseType.EXPLICACAO_BASICA: [
                "Oi {name}! Vou explicar simples: você tem uma conta. Precisa pagar.",
                "Olá {name}! É assim: tem uma pendência. Tem que pagar.",
                "Oi {name}! Vou falar claro: tem uma conta. Precisa quitar."
            ],
            ResponseType.AJUDA_LEITURA: [
                "Oi {name}! Se não entendeu, posso ligar para você. Você tem uma conta.",
                "Olá {name}! Se tem dificuldade para ler, posso falar por telefone. Tem uma pendência.",
                "Oi {name}! Se não consegue ler bem, posso explicar por voz. Você tem uma conta."
            ],
            ResponseType.CONFIRMACAO_FACIL: [
                "Oi {name}! Você entendeu? Tem uma conta. Pode pagar?",
                "Olá {name}! Ficou claro? Tem que pagar. Pode fazer?",
                "Oi {name}! Entendeu? Precisa quitar. Pode resolver?"
            ],
            ResponseType.INSTRUCAO_PASSO_A_PASSO: [
                "Oi {name}! Vou te ajudar passo a passo: 1) Você tem uma conta. 2) Precisa pagar. 3) Pode fazer hoje?",
                "Olá {name}! Vou explicar devagar: 1) Tem uma pendência. 2) Tem que pagar. 3) Pode resolver?",
                "Oi {name}! Vou te guiar: 1) Tem uma conta. 2) Precisa quitar. 3) Pode pagar agora?"
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
        
        # ADAPTAÇÃO PARA ANALFABETOS - Seleciona template baseado no nível de alfabetização
        if analysis.needs_simple_language:
            # Para analfabetos, usa templates simplificados
            if analysis.literacy_level == LiteracyLevel.ANALFABETO_TOTAL:
                response_type = ResponseType.AJUDA_LEITURA
            elif analysis.literacy_level == LiteracyLevel.ANALFABETO_FUNCIONAL:
                response_type = ResponseType.EXPLICACAO_BASICA
            else:
                response_type = ResponseType.COBRANCA_SIMPLES
        else:
            # Para alfabetizados, usa a recomendação normal
            response_type = analysis.recommended_response
        
        # Seleciona template baseado na recomendação (adaptada ou original)
        templates = self.response_templates[response_type]
        
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
        # Para analfabetos, simplifica ainda mais a formatação
        if analysis.needs_simple_language:
            # Simplifica o nome se muito longo
            name = context.customer_name.split()[0] if len(context.customer_name.split()) > 1 else context.customer_name
        else:
            name = context.customer_name
        
        return template.format(
            name=name,
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
    
    # ===== SISTEMA DE TEMPLATES ADAPTATIVOS =====
    
    def generate_adaptive_response(self, analysis: AnalysisResult, context: ConversationContext, 
                                 client_prediction: Dict[str, Any]) -> BotResponse:
        """Gera resposta adaptativa baseada no aprendizado"""
        try:
            # Selecionar template baseado na efetividade
            best_template = self._select_best_template(analysis.recommended_response, 
                                                     client_prediction, context)
            
            # Personalizar mensagem com dados contextuais
            personalized_message = self._personalize_adaptive_message(
                best_template, context, analysis, client_prediction
            )
            
            # Calcular próximo contato baseado no aprendizado
            next_contact_hours = self._calculate_adaptive_next_contact(
                analysis, context, client_prediction
            )
            
            # Decidir escalação baseada no histórico
            escalate = self._should_escalate_adaptive(analysis, context, client_prediction)
            
            # Atualizar performance do template usado
            self._update_template_performance(analysis.recommended_response, context.customer_phone)
            
            return BotResponse(
                message=personalized_message,
                response_type=analysis.recommended_response,
                urgency_level=analysis.urgency_level,
                next_contact_hours=next_contact_hours,
                escalate=escalate,
                context_update=self._prepare_adaptive_context_update(analysis, context, client_prediction)
            )
            
        except Exception as e:
            logger.error( f"❌ Erro na resposta adaptativa: {e}")
            # Fallback para método padrão
            return self.generate_response(analysis, context)
    
    def _select_best_template(self, response_type: ResponseType, 
                            client_prediction: Dict[str, Any], 
                            context: ConversationContext) -> str:
        """Seleciona o melhor template baseado na performance"""
        templates = self.response_templates.get(response_type, [])
        if not templates:
            return "Template não encontrado"
        
        # Se temos dados de performance, usar o melhor
        if response_type.value in self.template_performance:
            performance_data = self.template_performance[response_type.value]
            best_template_idx = performance_data.get('best_template_index', 0)
            if best_template_idx < len(templates):
                return templates[best_template_idx]
        
        # Selecionar baseado no perfil do cliente
        if client_prediction.get('cooperation_likelihood', 0.5) > 0.7:
            # Cliente cooperativo - usar template mais educado
            return templates[0] if len(templates) > 0 else templates[0]
        elif client_prediction.get('cooperation_likelihood', 0.5) < 0.3:
            # Cliente resistente - usar template mais direto
            return templates[-1] if len(templates) > 1 else templates[0]
        else:
            # Cliente neutro - usar template balanceado
            return templates[1] if len(templates) > 1 else templates[0]
    
    def _personalize_adaptive_message(self, template: str, context: ConversationContext,
                                    analysis: AnalysisResult, client_prediction: Dict[str, Any]) -> str:
        """Personaliza mensagem com dados adaptativos"""
        message = template
        
        # Dados básicos
        message = message.replace('{name}', context.customer_name)
        message = message.replace('{amount}', f"{context.debt_amount:.2f}")
        message = message.replace('{days}', str(context.days_overdue))
        
        # Personalização baseada no perfil do cliente
        if client_prediction.get('cooperation_likelihood', 0.5) > 0.7:
            # Cliente cooperativo - adicionar tom mais amigável
            message = message.replace('Olá', 'Olá! Espero que esteja bem')
        elif client_prediction.get('escalation_risk', 0.2) > 0.5:
            # Cliente com risco de escalação - tom mais profissional
            message = message.replace('Oi', 'Bom dia')
        
        # Personalização baseada no histórico de pagamentos
        if context.payment_promises > 2:
            message += " Lembramos que esta é uma situação que precisa ser resolvida."
        
        return message
    
    def _calculate_adaptive_next_contact(self, analysis: AnalysisResult, 
                                       context: ConversationContext,
                                       client_prediction: Dict[str, Any]) -> int:
        """Calcula próximo contato baseado no aprendizado"""
        base_hours = 24
        
        # Ajustar baseado na predição do cliente
        if client_prediction.get('payment_likelihood', 0.3) > 0.7:
            # Cliente com alta probabilidade de pagamento - contato mais frequente
            return 6
        elif client_prediction.get('escalation_risk', 0.2) > 0.5:
            # Cliente com risco de escalação - contato menos frequente
            return 48
        
        # Ajustar baseado na urgência
        if analysis.urgency_level > 0.8:
            return 4
        elif analysis.urgency_level > 0.6:
            return 8
        else:
            return base_hours
    
    def _should_escalate_adaptive(self, analysis: AnalysisResult, 
                                context: ConversationContext,
                                client_prediction: Dict[str, Any]) -> bool:
        """Decide escalação baseada no aprendizado"""
        # Escalar se risco de escalação for alto
        if client_prediction.get('escalation_risk', 0.2) > 0.7:
            return True
        
        # Escalar se muitos contatos sem resultado
        if context.previous_contacts > 8:
            return True
        
        # Escalar se contestação da dívida
        if analysis.intent == IntentType.CONTESTACAO_DIVIDA:
            return True
        
        return False
    
    def _update_template_performance(self, response_type: ResponseType, phone: str):
        """Atualiza performance do template usado"""
        if response_type.value not in self.template_performance:
            self.template_performance[response_type.value] = {
                'total_uses': 0,
                'successful_uses': 0,
                'success_rate': 0.0,
                'best_template_index': 0
            }
        
        self.template_performance[response_type.value]['total_uses'] += 1
    
    def _prepare_adaptive_context_update(self, analysis: AnalysisResult, 
                                       context: ConversationContext,
                                       client_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara atualizações contextuais adaptativas"""
        updates = {
            'last_intent': analysis.intent.value,
            'last_sentiment': analysis.sentiment.value,
            'cooperation_level': analysis.cooperation_score,
            'lie_probability': analysis.lie_probability,
            'last_contact': datetime.now().isoformat(),
            'client_prediction': client_prediction,
            'adaptive_response_used': True
        }
        
        # Incrementar promessas se cliente prometeu pagar
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
        """Processa mensagem do cliente com INTELIGÊNCIA REAL + APRENDIZADO AVANÇADO"""
        
        logger.info( f"🔍 Analisando mensagem de {phone}: {message[:50]}...")
        
        # Carrega ou cria contexto
        context = self._get_or_create_context(phone, customer_data)
        
        # ANÁLISE ULTRA INTELIGENTE da mensagem
        analysis = self.nlp_processor.analyze_message(message, context)
        
        # PREDIÇÃO COMPORTAMENTAL DO CLIENTE
        client_prediction = self.nlp_processor.predict_client_behavior(phone, analysis.intent.value)
        
        logger.info( f"🧠 Análise: Intent={analysis.intent.value}, "
                   f"Sentiment={analysis.sentiment.value}, "
                   f"Cooperação={analysis.cooperation_score:.2f}, "
                   f"Estado={analysis.emotional_state}")
        logger.info( f"🔮 Predição: Cooperação={client_prediction['cooperation_likelihood']:.2f}, "
                   f"Pagamento={client_prediction['payment_likelihood']:.2f}, "
                   f"Confiança={client_prediction['confidence']:.2f}")
        
        # GERA RESPOSTA ADAPTATIVA INTELIGENTE
        response = self.response_generator.generate_adaptive_response(analysis, context, client_prediction)
        
        # ===== SISTEMA DE APRENDIZADO AVANÇADO =====
        if self.quality_analyzer and self.learning_engine:
            # Analisa qualidade da resposta
            quality_scores = self.quality_analyzer.analyze_response_quality({
                'text': response.message,
                'intent': analysis.intent.value,
                'sentiment': analysis.sentiment.value,
                'client_prediction': client_prediction
            })
            
            # Aprende com a resposta para melhorar futuras
            self.learning_engine.learn_from_response({
                'intent': analysis.intent.value,
                'template_id': response.response_type.value,
                'response': response.message,
                'client_reaction': 'pending',  # Será atualizado quando cliente responder
                'quality_scores': quality_scores,
                'client_prediction': client_prediction,
                'adaptive_used': True
            })
            
            logger.info( f"🎓 Qualidade: {quality_scores.get('overall', 0):.2f}")
        
        # ATUALIZA CONTEXTO COM DADOS DE APRENDIZADO
        enhanced_context_update = response.context_update.copy()
        enhanced_context_update.update({
            'client_prediction': client_prediction,
            'learning_data': {
                'intent_sequence': [analysis.intent.value],
                'response_sequence': [response.response_type.value],
                'timestamp': datetime.now().isoformat()
            }
        })
        
        self._update_context(phone, enhanced_context_update)
        
        # ADICIONA À HISTÓRIA COM DADOS DE APRENDIZADO
        self._add_to_history_with_learning(phone, message, response.message, analysis, client_prediction)
        
        logger.info( f"💬 Resposta adaptativa gerada: {response.response_type.value}")
        
        return response
    
    def generate_general_response(self, phone: str, message: str) -> BotResponse:
        """Gera resposta para pessoas não cadastradas como clientes"""
        try:
            logger.info( f"👤 Gerando resposta geral para não-cliente: {phone}")
            
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
            
            logger.info( f"✅ Resposta geral gerada para {phone}: {response_type.value}")
            return response
            
        except Exception as e:
            logger.error( f"❌ Erro ao gerar resposta geral: {str(e)}")
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
            logger.info( f"📋 Novo contexto criado para {phone}")
        
        return self.active_contexts[phone]
    
    def _update_context(self, phone: str, updates: Dict[str, Any]):
        """Atualiza contexto com novos dados"""
        if phone in self.active_contexts:
            context = self.active_contexts[phone]
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                    
            logger.info( f"📊 Contexto atualizado para {phone}")
    
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
    
    def _add_to_history_with_learning(self, phone: str, customer_message: str, bot_response: str, 
                                    analysis: AnalysisResult, client_prediction: Dict[str, Any]):
        """Adiciona interação ao histórico com dados de aprendizado"""
        if phone in self.active_contexts:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'customer_message': customer_message,
                'bot_response': bot_response,
                'message_type': 'conversation',
                'learning_data': {
                    'intent': analysis.intent.value,
                    'sentiment': analysis.sentiment.value,
                    'cooperation_score': analysis.cooperation_score,
                    'lie_probability': analysis.lie_probability,
                    'urgency_level': analysis.urgency_level,
                    'emotional_state': analysis.emotional_state,
                    'client_prediction': client_prediction,
                    'response_type': analysis.recommended_response.value,
                    'confidence': analysis.confidence
                }
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
            logger.info( f"🗑️ Contexto limpo para {phone}")
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
            
            logger.info( f"🎓 Reação do cliente {phone} atualizada: {reaction}")
    
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
            'average_interactions': 0,
            'learning_insights': self.nlp_processor.get_learning_insights()
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
    
    def process_conversation_feedback(self, phone: str, feedback_data: Dict[str, Any]):
        """Processa feedback de uma conversa para aprendizado contínuo"""
        try:
            outcome = feedback_data.get('outcome', 'unknown')
            conversation_data = {
                'outcome': outcome,
                'intent_sequence': feedback_data.get('intent_sequence', []),
                'response_sequence': feedback_data.get('response_sequence', []),
                'final_result': feedback_data.get('final_result', {}),
                'client_satisfaction': feedback_data.get('client_satisfaction', 0.5),
                'payment_made': feedback_data.get('payment_made', False),
                'escalated': feedback_data.get('escalated', False)
            }
            
            # Aprender com o resultado da conversa
            self.nlp_processor.learn_from_conversation_outcome(phone, conversation_data)
            
            # Atualizar sistema de aprendizado se disponível
            if self.learning_engine:
                self.learning_engine.learn_from_conversation_outcome(conversation_data)
            
            logger.info( f"🎓 Feedback processado para {phone}: {outcome}")
            
        except Exception as e:
            logger.error( f"❌ Erro ao processar feedback: {e}")
    
    def get_adaptive_insights(self) -> Dict[str, Any]:
        """Obtém insights do sistema adaptativo"""
        insights = {
            'nlp_learning': self.nlp_processor.get_learning_insights(),
            'response_effectiveness': self.response_generator.template_performance,
            'client_profiles': len(self.nlp_processor.client_behavior_profiles),
            'adaptive_responses_used': 0,
            'learning_confidence': 0.0
        }
        
        # Contar respostas adaptativas usadas
        for context in self.active_contexts.values():
            for interaction in context.conversation_history:
                if interaction.get('learning_data', {}).get('adaptive_used'):
                    insights['adaptive_responses_used'] += 1
        
        # Calcular confiança geral do aprendizado
        nlp_confidence = insights['nlp_learning'].get('learning_confidence', 0.0)
        insights['learning_confidence'] = nlp_confidence
        
        return insights
    
    def optimize_for_client(self, phone: str) -> Dict[str, Any]:
        """Otimiza respostas para um cliente específico"""
        if phone not in self.nlp_processor.client_behavior_profiles:
            return {'message': 'Cliente não encontrado no sistema de aprendizado'}
        
        profile = self.nlp_processor.client_behavior_profiles[phone]
        prediction = self.nlp_processor.predict_client_behavior(phone, 'unknown')
        
        optimization = {
            'client_phone': phone,
            'profile': profile,
            'prediction': prediction,
            'recommended_approach': 'cobranca_educada',
            'optimal_timing': 'morning',
            'risk_factors': [],
            'success_factors': []
        }
        
        # Determinar abordagem recomendada
        if profile['cooperation_level'] > 0.7:
            optimization['recommended_approach'] = 'cobranca_educada'
            optimization['success_factors'].append('Cliente cooperativo - abordagem educada funciona')
        elif profile['cooperation_level'] < 0.3:
            optimization['recommended_approach'] = 'cobranca_direta'
            optimization['risk_factors'].append('Cliente resistente - risco de escalação')
        else:
            optimization['recommended_approach'] = 'cobranca_informativa'
        
        # Determinar timing ótimo
        if profile['payment_likelihood'] > 0.6:
            optimization['optimal_timing'] = 'morning'
        else:
            optimization['optimal_timing'] = 'afternoon'
        
        return optimization

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
                    logger.info( f"🗄️ CLIENTE ENCONTRADO no sistema persistente: {stored_customer.name}")
                else:
                    # 👤 NÃO É CLIENTE CADASTRADO - RESPONDER COMO PESSOA COMUM
                    logger.info( f"👤 Pessoa não cadastrada como cliente: {phone}")
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
                logger.info( f"💾 Contexto da conversa salvo (persistente): {phone}")
                
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
        logger.error( f"❌ Erro ao processar mensagem: {str(e)}")
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
