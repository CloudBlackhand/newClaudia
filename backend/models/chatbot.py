"""
🤖 CLAUDIA DA DESK - BOT CONVERSACIONAL SUPREMO 🚀
Sistema de IA Conversacional de Última Geração - Nível ChatGPT++
Processamento de Linguagem Natural Supremo para Português Brasileiro
Inteligência Emocional, Memória Contextual e Compreensão Semântica Avançada
"""
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None
import json
import re
import pickle
import asyncio
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime, timedelta
import numpy as np
import math
from dataclasses import dataclass
from collections import defaultdict, deque
try:
    from transformers import (
        AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
        BertTokenizer, BertForSequenceClassification, pipeline,
        AutoModelForCausalLM, GPT2LMHeadModel
    )
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoTokenizer = None
    AutoModel = None
from backend.config.settings import active_config
from backend.utils.logger import conversation_logger, app_logger
from backend.models.conversation import ConversationContext

@dataclass
class EmotionalState:
    """Estado emocional detectado na conversa"""
    primary_emotion: str  # raiva, tristeza, alegria, medo, surpresa, nojo
    intensity: float  # 0.0 a 1.0
    confidence: float  # confiança na detecção
    indicators: List[str]  # palavras/frases que indicaram a emoção
    timestamp: datetime

@dataclass
class ConversationMemory:
    """Memória de conversação avançada"""
    user_profile: Dict[str, Any]  # perfil do usuário construído ao longo do tempo
    conversation_history: deque  # histórico limitado de mensagens
    emotional_timeline: List[EmotionalState]  # linha do tempo emocional
    key_facts: Dict[str, Any]  # fatos importantes sobre o usuário
    preferences: Dict[str, Any]  # preferências detectadas
    context_embeddings: np.ndarray  # embeddings para busca semântica
    last_update: datetime

@dataclass
class SemanticUnderstanding:
    """Compreensão semântica avançada"""
    intent_confidence: float
    semantic_similarity: float
    contextual_relevance: float
    emotional_alignment: float
    topic_coherence: float

class EmotionalIntelligence:
    """Sistema de Inteligência Emocional Avançado"""
    
    def __init__(self):
        # Mapeamento de palavras para emoções
        self.emotion_lexicon = {
            "raiva": {
                "words": [
                    "raiva", "ódio", "irritado", "puto", "pissed", "furioso", 
                    "revoltado", "indignado", "zangado", "bravo", "nervoso",
                    "estressado", "saco cheio", "enchendo saco", "paciência",
                    "maldito", "droga", "merda", "inferno", "diabos"
                ],
                "phrases": [
                    "que raiva", "to puto", "saco cheio", "encheu o saco",
                    "perdi a paciência", "que merda", "vai se foder",
                    "to irritado", "me irrita", "que ódio"
                ]
            },
            "tristeza": {
                "words": [
                    "triste", "deprimido", "chateado", "desanimado", "down",
                    "melancólico", "cabisbaixo", "abatido", "chorar", "lágrimas",
                    "perdido", "sozinho", "abandonado", "desesperado", "sem esperança"
                ],
                "phrases": [
                    "to triste", "me sinto mal", "que tristeza", "quero chorar",
                    "to down", "depre total", "sem ânimo", "vida difícil",
                    "que barra", "to mal"
                ]
            },
            "alegria": {
                "words": [
                    "feliz", "alegre", "contente", "satisfeito", "animado",
                    "eufórico", "empolgado", "radiante", "sorrindo", "rindo",
                    "festa", "celebrar", "comemorar", "vitória", "sucesso"
                ],
                "phrases": [
                    "to feliz", "que alegria", "to animado", "muito bom",
                    "excelente", "perfeito", "show de bola", "massa",
                    "incrível", "sensacional"
                ]
            },
            "medo": {
                "words": [
                    "medo", "assustado", "nervoso", "ansioso", "preocupado",
                    "temeroso", "amedrontado", "inseguro", "receoso", "apreensivo",
                    "pânico", "terror", "pavor", "susto", "angústia"
                ],
                "phrases": [
                    "to com medo", "preocupado", "ansioso", "nervoso",
                    "que vai acontecer", "e se", "tenho receio", "inseguro",
                    "com pânico", "angustiado"
                ]
            },
            "surpresa": {
                "words": [
                    "surpreso", "espantado", "chocado", "impressionado", "uau",
                    "nossa", "caramba", "eita", "putz", "wow", "inacreditável"
                ],
                "phrases": [
                    "que surpresa", "não acredito", "sério mesmo", "nossa senhora",
                    "caramba", "eita nossa", "que isso", "incrível"
                ]
            },
            "frustração": {
                "words": [
                    "frustrado", "cansado", "desistir", "largar", "chega",
                    "basta", "não aguento", "saturado", "farto", "de saco cheio"
                ],
                "phrases": [
                    "to frustrado", "cansei", "desisto", "chega disso",
                    "não aguento mais", "que saco", "já deu", "basta"
                ]
            }
        }
        
        # Intensificadores emocionais
        self.intensifiers = {
            "alto": ["muito", "super", "mega", "ultra", "extremamente", "totalmente"],
            "médio": ["bem", "bastante", "meio", "um pouco"],
            "baixo": ["levemente", "ligeiramente", "pouco"]
        }
    
    def analyze_emotion(self, text: str) -> EmotionalState:
        """Analisa emoção no texto com precisão avançada"""
        text_lower = text.lower()
        detected_emotions = {}
        indicators = []
        
        # Analisa cada emoção
        for emotion, patterns in self.emotion_lexicon.items():
            score = 0.0
            emotion_indicators = []
            
            # Verifica palavras-chave
            for word in patterns["words"]:
                if word in text_lower:
                    score += 1.0
                    emotion_indicators.append(word)
            
            # Verifica frases
            for phrase in patterns["phrases"]:
                if phrase in text_lower:
                    score += 2.0  # Frases têm peso maior
                    emotion_indicators.append(phrase)
            
            # Aplica intensificadores
            for intensity_level, words in self.intensifiers.items():
                for intensifier in words:
                    if intensifier in text_lower and emotion_indicators:
                        if intensity_level == "alto":
                            score *= 1.5
                        elif intensity_level == "médio":
                            score *= 1.2
                        elif intensity_level == "baixo":
                            score *= 0.8
            
            if score > 0:
                detected_emotions[emotion] = {
                    "score": score,
                    "indicators": emotion_indicators
                }
                indicators.extend(emotion_indicators)
        
        # Determina emoção principal
        if detected_emotions:
            primary_emotion = max(detected_emotions.keys(), 
                                key=lambda x: detected_emotions[x]["score"])
            max_score = detected_emotions[primary_emotion]["score"]
            
            # Normaliza intensidade (0.0 - 1.0)
            intensity = min(max_score / 5.0, 1.0)  # Max 5 pontos = intensidade 1.0
            confidence = min(intensity * 1.2, 1.0)  # Confiança baseada na intensidade
            
            return EmotionalState(
                primary_emotion=primary_emotion,
                intensity=intensity,
                confidence=confidence,
                indicators=detected_emotions[primary_emotion]["indicators"],
                timestamp=datetime.now()
            )
        else:
            # Estado neutro
            return EmotionalState(
                primary_emotion="neutro",
                intensity=0.0,
                confidence=0.8,
                indicators=[],
                timestamp=datetime.now()
            )

class AdvancedMemorySystem:
    """Sistema de Memória Conversacional Supremo"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.conversations: Dict[str, ConversationMemory] = {}
        
        # Modelo para embeddings semânticos
        if TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('neuralmind/bert-base-portuguese-cased')
            except:
                self.sentence_model = None
                app_logger.warning("SentenceTransformer não disponível, usando fallback")
        else:
            self.sentence_model = None
    
    def get_or_create_memory(self, user_id: str) -> ConversationMemory:
        """Obtém ou cria memória para usuário"""
        if user_id not in self.conversations:
            self.conversations[user_id] = ConversationMemory(
                user_profile={},
                conversation_history=deque(maxlen=self.max_history),
                emotional_timeline=[],
                key_facts={},
                preferences={},
                context_embeddings=np.array([]),
                last_update=datetime.now()
            )
        return self.conversations[user_id]
    
    def update_memory(
        self, 
        user_id: str, 
        message: str, 
        response: str, 
        emotional_state: EmotionalState,
        extracted_facts: Dict[str, Any]
    ):
        """Atualiza memória do usuário"""
        memory = self.get_or_create_memory(user_id)
        
        # Adiciona ao histórico
        memory.conversation_history.append({
            "timestamp": datetime.now(),
            "user_message": message,
            "bot_response": response,
            "emotion": emotional_state
        })
        
        # Atualiza linha do tempo emocional
        memory.emotional_timeline.append(emotional_state)
        
        # Mantém apenas últimas 20 emoções
        if len(memory.emotional_timeline) > 20:
            memory.emotional_timeline = memory.emotional_timeline[-20:]
        
        # Atualiza fatos importantes
        memory.key_facts.update(extracted_facts)
        
        # Gera embeddings se disponível
        if self.sentence_model:
            try:
                embedding = self.sentence_model.encode([message + " " + response])
                if memory.context_embeddings.size == 0:
                    memory.context_embeddings = embedding
                else:
                    # Média dos embeddings (simplificado)
                    memory.context_embeddings = (memory.context_embeddings + embedding) / 2
            except Exception as e:
                app_logger.warning("Erro ao gerar embeddings", {"error": str(e)})
        
        memory.last_update = datetime.now()
    
    def get_contextual_information(self, user_id: str, current_message: str) -> Dict[str, Any]:
        """Obtém informações contextuais relevantes"""
        memory = self.get_or_create_memory(user_id)
        
        # Análise de padrões emocionais
        recent_emotions = memory.emotional_timeline[-5:] if memory.emotional_timeline else []
        emotional_pattern = self._analyze_emotional_pattern(recent_emotions)
        
        # Fatos relevantes
        relevant_facts = memory.key_facts
        
        # Histórico recente
        recent_history = list(memory.conversation_history)[-3:] if memory.conversation_history else []
        
        return {
            "emotional_pattern": emotional_pattern,
            "relevant_facts": relevant_facts,
            "recent_history": recent_history,
            "user_profile": memory.user_profile,
            "conversation_count": len(memory.conversation_history)
        }
    
    def _analyze_emotional_pattern(self, emotions: List[EmotionalState]) -> Dict[str, Any]:
        """Analisa padrão emocional do usuário"""
        if not emotions:
            return {"trend": "neutral", "stability": "stable"}
        
        # Calcula tendência emocional
        emotion_values = {
            "alegria": 1.0, "surpresa": 0.5, "neutro": 0.0,
            "frustração": -0.3, "tristeza": -0.7, "raiva": -1.0, "medo": -0.5
        }
        
        values = [emotion_values.get(e.primary_emotion, 0.0) * e.intensity for e in emotions]
        
        if len(values) >= 2:
            trend = "improving" if values[-1] > values[0] else "declining" if values[-1] < values[0] else "stable"
        else:
            trend = "stable"
        
        # Calcula estabilidade
        variance = np.var(values) if len(values) > 1 else 0
        stability = "unstable" if variance > 0.3 else "moderate" if variance > 0.1 else "stable"
        
        return {
            "trend": trend,
            "stability": stability,
            "recent_emotion": emotions[-1].primary_emotion,
            "average_intensity": np.mean([e.intensity for e in emotions])
        }

class BillingContextEnforcer:
    """Garante 100% das respostas permaneçam no contexto de cobranças"""
    
    def __init__(self):
        self.billing_keywords = {
            'pagamento', 'boleto', 'fatura', 'conta', 'valor', 'dívida', 'pix',
            'transferência', 'cartão', 'crédito', 'débito', 'parcelamento',
            'desconto', 'negociação', 'vencimento', 'vencido', 'atraso',
            'juros', 'multa', 'acordo', 'quitação', 'liquidação', 'cobrança'
        }
        
        self.billing_phrases = [
            "paguei a fatura", "enviei o comprovante", "quero parcelar",
            "preciso de desconto", "conta vencida", "valor incorreto",
            "não reconheço esta cobrança", "como faço para pagar",
            "qual é o código de barras", "posso negociar", "situação financeira"
        ]
        
        self.out_of_scope_responses = [
            "Desculpe, posso apenas ajudar com questões relacionadas à cobrança e pagamento de faturas.",
            "Estou aqui exclusivamente para auxiliar com pagamentos, faturas e questões financeiras.",
            "Por favor, limite sua pergunta a assuntos relacionados à cobrança e pagamento."
        ]
    
    def is_billing_related(self, text: str) -> tuple[bool, float]:
        """Verifica se o texto está relacionado a cobranças"""
        text_lower = text.lower()
        
        # Conta palavras-chave de cobrança
        keyword_count = sum(1 for keyword in self.billing_keywords 
                          if keyword in text_lower)
        
        # Verifica frases específicas
        phrase_matches = sum(1 for phrase in self.billing_phrases 
                           if phrase in text_lower)
        
        # Calcula score de relevância
        total_score = keyword_count + (phrase_matches * 2)
        confidence = min(total_score / 3.0, 1.0)
        
        return total_score > 0, confidence
    
    def enforce_billing_context(self, text: str, response: str) -> str:
        """Garante que a resposta permaneça no contexto de cobranças"""
        is_related, _ = self.is_billing_related(text)
        
        if not is_related:
            return np.random.choice(self.out_of_scope_responses)
        
        return response

class AdvancedBillingNLP:
    """NLP avançado especializado em cobranças - nível ChatGPT++"""
    
    def __init__(self):
        # Intenções específicas de cobrança
        self.billing_intents = {
            'payment_confirmation': {
                'patterns': [
                    r'paguei\s+(?:a|o)\s+(?:fatura|conta|boleto)',
                    r'(?:já|acabei de)\s+pagar',
                    r'enviei\s+(?:o|meu)\s+comprovante',
                    r'(?:fiz|realizei)\s+(?:o|um)\s+pagamento',
                    r'(?:pago|quitado|liquidado)'
                ],
                'confidence_threshold': 0.85
            },
            'payment_request': {
                'patterns': [
                    r'(?:como|onde)\s+posso\s+pagar',
                    r'(?:qual é|me diga)\s+o\s+código\s+de\s+barras',
                    r'(?:preciso|quero)\s+pagar',
                    r'(?:informações|dados)\s+para\s+pagamento',
                    r'(?:link|site|app)\s+para\s+pagar'
                ],
                'confidence_threshold': 0.80
            },
            'negotiation_request': {
                'patterns': [
                    r'(?:posso|dá para)\s+negociar',
                    r'(?:preciso|quero)\s+de\s+desconto',
                    r'(?:parcelar|dividir)\s+(?:o|em)\s+vezes',
                    r'(?:situação|problema)\s+financeir[ao]',
                    r'(?:desempregado|sem renda|dificuldade)'
                ],
                'confidence_threshold': 0.75
            },
            'dispute_charge': {
                'patterns': [
                    r'(?:não reconheço|não lembro|não comprei)',
                    r'(?:conta|valor)\s+incorreto',
                    r'(?:erro|engano)\s+na\s+cobrança',
                    r'(?:golpe|fraude|indevido)',
                    r'(?:cancelar|reverter)\s+pagamento'
                ],
                'confidence_threshold': 0.80
            }
        }
        
        # Entidades financeiras
        self.financial_entities = {
            'amount': [
                r'(?:R\$|RS|R)\s*\d+(?:[,.]\d{2})?',
                r'\d+(?:[,.]\d{2})?\s*(?:reais|real|centavos)',
                r'(?:total|valor|preço)\s+(?:de\s+)?\d+(?:[,.]\d{2})?'
            ],
            'date': [
                r'\d{2}/\d{2}/\d{4}',
                r'\d{2}/\d{2}',
                r'(?:vencimento|vence)\s+(?:dia\s+)?\d{1,2}',
                r'(?:ontem|hoje|amanhã|próxima semana)'
            ],
            'payment_method': [
                r'(?:pix|boleto|cartão|transferência|débito|crédito)',
                r'(?:débito automático|débito em conta)',
                r'(?:TED|DOC|DOC/TED)'
            ],
            'account_number': [
                r'(?:número|codigo)\s+(?:da\s+)?(?:conta|fatura)',
                r'(?:ref|referência)\s*[.:]\s*\d+',
                r'(?:nosso\s+)?número\s*[.:]\s*\d+'
            ]
        }
    
    def extract_billing_intent(self, text: str) -> Dict[str, Any]:
        """Extrai intenção específica de cobrança com alta precisão"""
        text_lower = text.lower()
        results = {}
        
        for intent_name, intent_data in self.billing_intents.items():
            max_confidence = 0.0
            matched_pattern = None
            
            for pattern in intent_data['patterns']:
                match = re.search(pattern, text_lower)
                if match:
                    # Calcula confiança baseada no tamanho do match
                    confidence = len(match.group()) / len(text_lower)
                    if confidence > max_confidence:
                        max_confidence = confidence
                        matched_pattern = pattern
            
            if max_confidence >= intent_data['confidence_threshold']:
                results[intent_name] = {
                    'confidence': max_confidence,
                    'pattern': matched_pattern,
                    'text_match': re.search(matched_pattern, text_lower).group() if matched_pattern else None
                }
        
        return results
    
    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrai entidades financeiras do texto"""
        entities = {}
        text_lower = text.lower()
        
        for entity_type, patterns in self.financial_entities.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_lower)
                matches.extend(found)
            
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def analyze_financial_sentiment(self, text: str) -> Dict[str, float]:
        """Analisa sentimento específico para contexto financeiro"""
        text_lower = text.lower()
        
        positive_indicators = [
            'pago', 'quitado', 'liquidado', 'resolvido', 'tudo certo',
            'obrigado', 'agradeço', 'excelente', 'ótimo', 'perfeito'
        ]
        
        negative_indicators = [
            'problema', 'erro', 'golpe', 'fraude', 'incorreto', 'indevido',
            'difícil', 'impossível', 'desempregado', 'sem dinheiro', 'quebrado'
        ]
        
        urgency_indicators = [
            'urgente', 'rápido', 'imediatamente', 'preciso', 'necessário',
            'agora', 'hoje', 'amanhã', 'prazo', 'vencimento'
        ]
        
        positive_score = sum(1 for indicator in positive_indicators if indicator in text_lower)
        negative_score = sum(1 for indicator in negative_indicators if indicator in text_lower)
        urgency_score = sum(1 for indicator in urgency_indicators if indicator in text_lower)
        
        total_words = len(text_lower.split())
        
        return {
            'positive': positive_score / max(total_words, 1),
            'negative': negative_score / max(total_words, 1),
            'urgency': urgency_score / max(total_words, 1),
            'overall': (positive_score - negative_score) / max(total_words, 1)
        }

class BrazilianTextNormalizer:
    """Normalizador supremo de texto brasileiro coloquial - otimizado para cobranças"""
    
    def __init__(self):
        # Mapeamento de abreviações e gírias para português formal - focado em termos financeiros
        self.abbreviations = {
            # Internet slang
            "vc": "você", "vcs": "vocês", "q": "que", "qq": "qualquer",
            "tb": "também", "tbm": "também", "td": "tudo", "mto": "muito",
            "mt": "muito", "msm": "mesmo", "dps": "depois", "blz": "beleza",
            "vlw": "valeu", "obg": "obrigado", "pq": "porque", "pqê": "porque",
            
            # Abreviações de tempo
            "hj": "hoje", "onti": "ontem", "amanha": "amanhã", "sema": "semana",
            "mes": "mês", "ano": "ano", "hr": "hora", "min": "minuto",
            
            # Abreviações financeiras especializadas
            "dinherio": "dinheiro", "bufunfa": "dinheiro", "grana": "dinheiro",
            "pixe": "pix", "pixi": "pix", "conta": "conta", "fat": "fatura",
            "bol": "boleto", "transf": "transferência", "cart": "cartão",
            "parc": "parcelamento", "desc": "desconto", "neg": "negociação",
            "venc": "vencimento", "atras": "atraso", "jur": "juros",
            "mult": "multa", "quit": "quitado", "liq": "liquidado",
            
            # Erros comuns de digitação financeira
            "nao": "não", "tah": "está", "tao": "tão", "eh": "é",
            "pra": "para", "pro": "para", "pros": "para", "pras": "para",
            "ta": "está", "to": "estou", "tava": "estava",
            "paguei": "paguei", "paguie": "paguei", "pagiei": "paguei",
            "pagar": "pagar", "pague": "pague", "pagando": "pagando",
            
            # Gírias financeiras
            "trampo": "trabalho", "role": "situação", "parada": "situação",
            "bagulho": "coisa", "troço": "coisa", "negócio": "coisa",
            "liso": "sem dinheiro", "quebrado": "sem recursos financeiros",
            "quebrado": "em dificuldade financeira", "falido": "sem condições de pagar",
            
            # Cumprimentos abreviados
            "bd": "bom dia", "bt": "boa tarde", "bn": "boa noite",
            "eae": "e aí", "blz": "beleza", "tmj": "estamos juntos",
            "flw": "falou", "vlws": "valeu", "obrigado": "obrigado"
        }
        
        # Correções de erros comuns
        self.spelling_corrections = {
            "paguie": "paguei", "pagiei": "paguei", "baguei": "paguei",
            "fis": "fiz", "fes": "fez", "seii": "sei", "intendi": "entendi",
            "esplica": "explica", "difisil": "difícil", "facil": "fácil",
            "seman": "semana", "seista": "sexta", "sesta": "sexta",
            "qunto": "quanto", "qnto": "quanto", "ond": "onde",
            "brigadu": "obrigado", "falow": "falou", "ati": "até",
            "difficuldades": "dificuldades", "negosiar": "negociar"
        }
        
        # Remoção de caracteres repetidos
        self.repeated_chars = re.compile(r'(.)\1{2,}')
    
    def normalize(self, text: str) -> str:
        """Normaliza texto coloquial brasileiro"""
        if not text:
            return ""
        
        # Converte para minúsculo
        normalized = text.lower().strip()
        
        # Remove caracteres especiais desnecessários
        normalized = re.sub(r'[^\w\s\-.,!?áéíóúâêîôûãõç]', '', normalized)
        
        # Corrige caracteres repetidos (ex: "oiiiii" -> "oi")
        normalized = self.repeated_chars.sub(r'\1\1', normalized)
        
        # Aplica correções ortográficas
        words = normalized.split()
        corrected_words = []
        
        for word in words:
            # Remove pontuação para comparação
            clean_word = re.sub(r'[.,!?]', '', word)
            
            # Verifica correções específicas
            if clean_word in self.spelling_corrections:
                corrected_word = self.spelling_corrections[clean_word]
                # Preserva pontuação
                if word != clean_word:
                    corrected_word += word[len(clean_word):]
                corrected_words.append(corrected_word)
            # Verifica abreviações
            elif clean_word in self.abbreviations:
                corrected_word = self.abbreviations[clean_word]
                # Preserva pontuação
                if word != clean_word:
                    corrected_word += word[len(clean_word):]
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
    
    def extract_intent_signals(self, text: str) -> List[str]:
        """Extrai sinais de intenção do texto"""
        signals = []
        text_lower = text.lower()
        
        # Sinais de confirmação de pagamento
        payment_signals = [
            "paguei", "pix", "transferi", "boleto", "depositei",
            "já foi", "já era", "mandei", "enviei"
        ]
        
        # Sinais de negociação
        negotiation_signals = [
            "parcelar", "desconto", "acordo", "difícil", "sem dinheiro",
            "desempregado", "quebrado", "liso", "condições"
        ]
        
        # Sinais de contestação
        dispute_signals = [
            "erro", "engano", "não devo", "não reconheço", "golpe",
            "nunca", "não fui eu"
        ]
        
        for signal in payment_signals:
            if signal in text_lower:
                signals.append("payment_confirmed")
                break
        
        for signal in negotiation_signals:
            if signal in text_lower:
                signals.append("wants_negotiation")
                break
        
        for signal in dispute_signals:
            if signal in text_lower:
                signals.append("disputes_charge")
                break
        
        return signals

class SpellCorrector:
    """Corretor ortográfico especializado em português brasileiro coloquial"""
    
    def __init__(self):
        # Distância de Levenshtein para palavras similares
        self.common_words = {
            "pagamento", "dinheiro", "valor", "conta", "banco", "pix",
            "transferência", "boleto", "débito", "crédito", "cartão",
            "parcelar", "desconto", "acordo", "negociar", "prazo"
        }
        
        # Correções fonéticas (como as pessoas escrevem vs como deveria ser)
        self.phonetic_corrections = {
            "ki": "qui", "ke": "que", "ka": "ca", "ko": "co",
            "ks": "x", "s": "ç", "ss": "ç"
        }
    
    def correct_word(self, word: str) -> str:
        """Corrige uma palavra usando similaridade fonética"""
        if len(word) < 3:
            return word
        
        best_match = word
        min_distance = float('inf')
        
        for correct_word in self.common_words:
            distance = self._levenshtein_distance(word.lower(), correct_word.lower())
            if distance < min_distance and distance <= 2:  # Máximo 2 erros
                min_distance = distance
                best_match = correct_word
        
        return best_match if min_distance <= 2 else word
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calcula distância de Levenshtein entre duas strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

class ConversationLearning:
    """Sistema de Aprendizado Contínuo"""
    
    def __init__(self):
        self.interaction_patterns = defaultdict(list)
        self.success_metrics = defaultdict(float)
        self.failure_patterns = defaultdict(list)


class AdvancedBillingNLP:
    """NLP avançado nivel ChatGPT para cobranças e faturas"""
    
    def __init__(self):
        # Contexto e memória de conversação
        self.conversation_memory = {}
        self.context_stack = []
        
        # Intenções refinadas com contexto emocional
        self.intent_contexts = {
            'urgent_payment': {
                'patterns': [
                    r'\b(urgente|imediato|rápido|hoje|agora|já)\s+(pagar|resolver|quitar)\b',
                    r'\b(vence\s+(hoje|amanhã|em\s+breve))\b.*\b(preciso|quero)\b',
                    r'\b(evitar|não\s+quero)\s+(multa|juros|atraso)\b'
                ],
                'context': {'urgency': 1.0, 'anxiety': 0.8, 'cooperation': 0.6},
                'responses': ['entendo_urgencia', 'oferecer_solucao_rapida']
            },
            'empathetic_negotiation': {
                'patterns': [
                    r'\b(não\s+tenho|sem\s+condições|dificuldade|crise)\s+(dinheiro|condições)\b',
                    r'\b(perdi\s+emprego|salário\s+reduzido|problema\s+financeiro)\b',
                    r'\b(posso\s+pagar\s+entrada\s+baixa|parcelar\s+em\s+muitas)\b'
                ],
                'context': {'empathy': 1.0, 'flexibility': 0.9, 'support': 0.8},
                'responses': ['demonstrar_empatia', 'oferecer_flexibilidade']
            },
            'detailed_dispute': {
                'patterns': [
                    r'\b(não\s+reconheço|não\s+fez|não\s+comprei)\s+(essa|esta)\s+(compra|cobrança)\b',
                    r'\b(contesto|questiono)\s+(motivo|razão)\s+.*\b(erro|fraude|golpe)\b',
                    r'\b(preciso\s+de)\s+(prova|comprovante|evidência)\b'
                ],
                'context': {'investigation': 1.0, 'documentation': 0.9, 'patience': 0.7},
                'responses': ['investigar_detalhadamente', 'solicitar_documentacao']
            },
            'proactive_payment': {
                'patterns': [
                    r'\b(quero|vou|pretendo)\s+(pagar|quitar|resolver)\s+(hoje|agora|imediatamente)\b',
                    r'\b(como\s+posso)\s+(gerar|emitir)\s+(boleto|pix)\b',
                    r'\b(consigo\s+pagar|tenho\s+condições)\s+(à\s+vista|parcelado)\b'
                ],
                'context': {'proactivity': 1.0, 'efficiency': 0.9, 'appreciation': 0.8},
                'responses': ['facilitar_processo', 'agradecer_proatividade']
            }
        }
        
        # Entidades financeiras com validação inteligente
        self.smart_entities = {
            'dynamic_amount': {
                'patterns': [
                    r'\b(total|valor|dívida|saldo)\s+(?:de\s+)?R\$\s*(\d+(?:\.\d{3})*(?:,\d{2})?)\b',
                    r'\b(\d+(?:\.\d{3})*(?:,\d{2})?)\s*(?:reais|R\$)\s+(?:de|em)\s+(?:dívida|débito)\b',
                    r'\b(?:está|fica\s+em)\s+R\$\s*(\d+(?:\.\d{3})*(?:,\d{2})?)\b'
                ],
                'validators': ['is_valid_brazilian_currency'],
                'normalizers': ['format_brl_currency']
            },
            'contextual_date': {
                'patterns': [
                    r'\b(vence|vencimento|prazo)\s+(?:em|dia)\s+(\d{1,2}(?:\/\d{1,2}(?:\/\d{2,4})?)?)\b',
                    r'\b(\d{1,2}\s+de\s+\w+(?:\s+de\s+\d{2,4})?)\s+(?:vence|vencimento)\b',
                    r'\b(?:próxima?|próximo)\s+(?:data|dia)\s+(?:vencimento|pagamento)\b'
                ],
                'validators': ['is_valid_date', 'is_future_date'],
                'normalizers': ['format_iso_date', 'add_year_context']
            },
            'payment_preference': {
                'patterns': [
                    r'\b(prefiro|quero|gostaria)\s+(?:de\s+)?(pix|boleto|cartão|transferência)\b',
                    r'\b(?:via|por)\s+(pix|boleto|cartão\s+(?:de\s+)?(?:crédito|débito))\b',
                    r'\b(aceita|aceitam)\s+(pix|boleto|cartão)\b'
                ],
                'validators': ['is_valid_payment_method'],
                'normalizers': ['standardize_payment_method']
            }
        }
        
        # Análise emocional avançada
        self.emotional_intelligence = {
            'sentiment_layers': {
                'surface_emotion': {
                    'positive': ['obrigado', 'valeu', 'ótimo', 'excelente', 'resolvido', 'perfeito'],
                    'negative': ['ruim', 'péssimo', 'horrível', 'terrível', 'pior'],
                    'neutral': ['ok', 'entendo', 'certo', 'tudo bem', 'normal']
                },
                'deep_emotion': {
                    'anxiety': ['preocupado', 'ansioso', 'medo', 'desesperado', 'nervoso', 'stress'],
                    'frustration': ['frustrado', 'irritado', 'chateado', 'insatisfeito', 'decepcionado'],
                    'hope': ['esperança', 'confiante', 'determinado', 'motivado', 'positivo'],
                    'despair': ['desesperança', 'derrotado', 'sem saída', 'acabado', 'desistir']
                },
                'behavioral_cues': {
                    'cooperative': ['entendo', 'quero resolver', 'posso', 'vou tentar', 'aceito', 'concordo'],
                    'resistant': ['não', 'impossível', 'inaceitável', 'injusto', 'jamais', 'recuso'],
                    'confused': ['não entendo', 'como assim', 'não sei', 'me explica', 'não compreendo']
                }
            },
            'intensity_markers': {
                'high': ['muito', 'extremamente', 'absolutamente', 'totalmente', 'completamente'],
                'medium': ['bastante', 'razoavelmente', 'relativamente', 'moderadamente'],
                'low': ['um pouco', 'meio', 'ligeiramente', 'minimamente']
            }
        }

    def extract_billing_intent(self, text: str, user_id: str = None, context: Dict = None) -> Dict[str, Any]:
        """Extrai intenção com contexto de conversação e memória"""
        text_lower = text.lower().strip()
        
        # Contexto da conversação atual
        conversation_context = self._get_conversation_context(user_id)
        
        # Análise de intenção contextual
        best_intent = None
        max_confidence = 0.0
        
        for intent_name, intent_data in self.intent_contexts.items():
            for pattern in intent_data['patterns']:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    # Calcula confiança com contexto
                    base_confidence = 0.75
                    
                    # Boost baseado em contexto anterior
                    context_boost = self._calculate_context_boost(
                        intent_name, conversation_context
                    )
                    
                    # Boost baseado em urgência/emotion
                    emotion_boost = self._calculate_emotion_boost(text_lower)
                    
                    confidence = min(base_confidence + context_boost + emotion_boost, 1.0)
                    
                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_intent = {
                            'intent': intent_name,
                            'confidence': confidence,
                            'context': intent_data['context'],
                            'match': match.group(),
                            'timestamp': datetime.now().isoformat(),
                            'conversation_context': conversation_context
                        }
        
        # Fallback inteligente com IA
        if not best_intent:
            best_intent = self._intelligent_fallback(text_lower, conversation_context)
        
        # Atualiza memória de conversação
        if user_id:
            self._update_conversation_memory(user_id, best_intent)
        
        return best_intent

    def extract_financial_entities(self, text: str, context: Dict = None) -> Dict[str, List[str]]:
        """Extrai entidades com validação e contexto inteligente"""
        entities = {}
        text_lower = text.lower().strip()
        
        for entity_name, entity_config in self.smart_entities.items():
            entities[entity_name] = []
            
            for pattern in entity_config['patterns']:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                
                for match in matches:
                    if isinstance(match, tuple):
                        # Extrai o grupo correto
                        for group in match:
                            if group and not group.lower() in ['total', 'valor', 'de', 'em']:
                                normalized = self._normalize_entity(
                                    entity_name, group.strip()
                                )
                                if normalized and self._validate_entity(entity_name, normalized):
                                    entities[entity_name].append(normalized)
                                    break
                    else:
                        normalized = self._normalize_entity(entity_name, str(match).strip())
                        if normalized and self._validate_entity(entity_name, normalized):
                            entities[entity_name].append(normalized)
            
            # Remove duplicatas e ordena por relevância
            entities[entity_name] = list(dict.fromkeys(entities[entity_name]))
        
        # Análise contextual de entidades
        entities = self._contextual_entity_analysis(entities, context)
        
        return entities

    def analyze_financial_sentiment(self, text: str, user_id: str = None) -> Dict[str, Any]:
        """Análise emocional profunda nível ChatGPT"""
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Análise multicamadas
        analysis = {
            'surface_sentiment': self._analyze_surface_sentiment(words),
            'deep_emotion': self._analyze_deep_emotion(text_lower),
            'behavioral_analysis': self._analyze_behavioral_patterns(text_lower),
            'intensity_analysis': self._analyze_intensity(text_lower),
            'temporal_emotion': self._analyze_temporal_emotion(user_id, text_lower)
        }
        
        # Score geral de sentimento
        overall_score = self._calculate_comprehensive_sentiment(analysis)
        analysis['overall'] = overall_score
        
        # Insights e recomendações
        analysis['insights'] = self._generate_emotional_insights(analysis)
        
        return analysis

    def _get_conversation_context(self, user_id: str) -> Dict:
        """Recupera contexto de conversação"""
        if not user_id:
            return {}
        
        return self.conversation_memory.get(user_id, {
            'last_intent': None,
            'emotional_state': 'neutral',
            'entities_extracted': [],
            'interaction_count': 0
        })

    def _calculate_context_boost(self, intent: str, context: Dict) -> float:
        """Calcula boost baseado em contexto de conversação"""
        boost = 0.0
        
        # Se o usuário está seguindo uma linha de raciocínio
        if context.get('last_intent') == intent:
            boost += 0.15
        
        # Se há entidades relevantes no contexto
        if context.get('entities_extracted'):
            boost += 0.1
        
        return boost

    def _calculate_emotion_boost(self, text: str) -> float:
        """Calcula boost baseado em intensidade emocional"""
        emotion_words = {
            'urgent': ['urgente', 'imediatamente', 'agora', 'já', 'rápido'],
            'anxious': ['preocupado', 'desesperado', 'medo', 'ansioso'],
            'angry': ['raiva', 'bravo', 'irritado', 'furioso', 'odio']
        }
        
        boost = 0.0
        for category, words in emotion_words.items():
            if any(word in text for word in words):
                boost += 0.1
        
        return boost

    def _intelligent_fallback(self, text: str, context: Dict) -> Dict[str, Any]:
        """Fallback inteligente quando nenhuma intenção específica é detectada"""
        # Análise semântica geral
        billing_indicators = [
            'fatura', 'conta', 'débito', 'cobrança', 'pagamento', 'valor', 'vencimento',
            'boleto', 'pix', 'cartão', 'saldo', 'dívida'
        ]
        
        indicator_count = sum(1 for indicator in billing_indicators if indicator in text)
        
        if indicator_count >= 2:
            return {
                'intent': 'billing_inquiry',
                'confidence': 0.6 + (indicator_count * 0.1),
                'context': {'general_billing': True, 'indicators': indicator_count},
                'match': f'billing_context_{indicator_count}',
                'timestamp': datetime.now().isoformat(),
                'conversation_context': context
            }
        
        return {
            'intent': 'clarification_needed',
            'confidence': 0.4,
            'context': {'unclear': True},
            'match': None,
            'timestamp': datetime.now().isoformat(),
            'conversation_context': context
        }

    def _update_conversation_memory(self, user_id: str, intent_data: Dict):
        """Atualiza memória de conversação"""
        if not user_id:
            return
        
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = {
                'last_intent': None,
                'emotional_state': 'neutral',
                'entities_extracted': [],
                'interaction_count': 0,
                'conversation_history': []
            }
        
        self.conversation_memory[user_id]['last_intent'] = intent_data['intent']
        self.conversation_memory[user_id]['interaction_count'] += 1
        self.conversation_memory[user_id]['conversation_history'].append({
            'timestamp': intent_data['timestamp'],
            'intent': intent_data['intent'],
            'confidence': intent_data['confidence']
        })

    def _normalize_entity(self, entity_type: str, value: str) -> Optional[str]:
        """Normaliza entidades com base no tipo"""
        if not value:
            return None
        
        value = str(value).strip()
        
        if entity_type == 'dynamic_amount':
            # Remove caracteres não numéricos e formata como moeda
            clean_value = re.sub(r'[^\d,]', '', value)
            if clean_value:
                return f"R$ {clean_value}"
        
        elif entity_type == 'contextual_date':
            # Normaliza datas para formato ISO
            return self._normalize_date(value)
        
        elif entity_type == 'payment_preference':
            # Padroniza métodos de pagamento
            return value.lower().replace(' ', '_')
        
        return value

    def _validate_entity(self, entity_type: str, value: str) -> bool:
        """Valida entidades com base em regras específicas"""
        if not value:
            return False
        
        if entity_type == 'dynamic_amount':
            # Valida formato de moeda brasileira
            amount_match = re.search(r'\d+(?:[.,]\d{2})?', value)
            return amount_match is not None
        
        elif entity_type == 'contextual_date':
            # Valida se é uma data válida
            return self._is_valid_date(value)
        
        return True

    def _contextual_entity_analysis(self, entities: Dict[str, List[str]], context: Dict = None) -> Dict[str, List[str]]:
        """Análise contextual das entidades extraídas"""
        if not context:
            return entities
        
        # Prioriza entidades relevantes ao contexto
        prioritized = {}
        
        for entity_type, values in entities.items():
            if values:
                # Ordena por relevância ao contexto
                prioritized[entity_type] = sorted(values, key=lambda x: self._relevance_score(x, context), reverse=True)[:3]
        
        return prioritized

    def _analyze_surface_sentiment(self, words: List[str]) -> Dict[str, float]:
        """Análise de sentimento superficial"""
        surface_layer = self.emotional_intelligence['sentiment_layers']['surface_emotion']
        
        scores = {}
        for category, keywords in surface_layer.items():
            score = sum(1 for word in words if word.lower() in keywords)
            scores[category] = score / max(len(words), 1)
        
        return scores

    def _analyze_deep_emotion(self, text: str) -> Dict[str, float]:
        """Análise de emoções profundas"""
        deep_layer = self.emotional_intelligence['sentiment_layers']['deep_emotion']
        
        scores = {}
        for emotion, keywords in deep_layer.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[emotion] = score / len(keywords)
        
        return scores

    def _analyze_behavioral_patterns(self, text: str) -> Dict[str, float]:
        """Análise de padrões comportamentais"""
        behavioral_layer = self.emotional_intelligence['sentiment_layers']['behavioral_cues']
        
        scores = {}
        for pattern, keywords in behavioral_layer.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[pattern] = score / len(keywords)
        
        return scores

    def _analyze_intensity(self, text: str) -> Dict[str, float]:
        """Análise de intensidade emocional"""
        intensity_markers = self.emotional_intelligence['intensity_markers']
        
        scores = {}
        for level, markers in intensity_markers.items():
            score = sum(1 for marker in markers if marker in text)
            scores[level] = score / len(markers)
        
        return scores

    def _analyze_temporal_emotion(self, user_id: str, text: str) -> Dict[str, Any]:
        """Análise temporal de emoção ao longo da conversa"""
        if not user_id or user_id not in self.conversation_memory:
            return {'trend': 'neutral', 'consistency': 0.0}
        
        history = self.conversation_memory[user_id]['conversation_history']
        if len(history) < 2:
            return {'trend': 'neutral', 'consistency': 0.0}
        
        # Analisa tendência emocional
        recent_emotions = []
        for interaction in history[-5:]:
            # Extrai emoção da interação (simplificado)
            emotion = 'neutral'  # Seria mais sofisticado em produção
            recent_emotions.append(emotion)
        
        return {
            'trend': self._calculate_emotion_trend(recent_emotions),
            'consistency': self._calculate_consistency(recent_emotions),
            'volatility': self._calculate_volatility(recent_emotions)
        }

    def _calculate_comprehensive_sentiment(self, analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calcula sentimento geral baseado em todas as camadas"""
        weights = {
            'surface_sentiment': 0.2,
            'deep_emotion': 0.3,
            'behavioral_analysis': 0.3,
            'intensity_analysis': 0.2
        }
        
        total_score = 0.0
        for layer, weight in weights.items():
            if layer in analysis:
                layer_data = analysis[layer]
                if isinstance(layer_data, dict):
                    # Converte para score numérico
                    positive = layer_data.get('positive', 0)
                    negative = layer_data.get('negative', 0)
                    score = (positive - negative) / max(len(layer_data), 1)
                    total_score += score * weight
        
        return {
            'score': total_score,
            'confidence': min(0.95, len(analysis) / 4.0),
            'interpretation': self._interpret_sentiment_score(total_score),
            'severity': self._calculate_severity(total_score)
        }

    def _interpret_sentiment_score(self, score: float) -> str:
        """Interpreta o score de sentimento"""
        if score > 0.5:
            return 'very_positive'
        elif score > 0.1:
            return 'positive'
        elif score < -0.5:
            return 'very_negative'
        elif score < -0.1:
            return 'negative'
        else:
            return 'neutral'

    def _calculate_severity(self, score: float) -> str:
        """Calcula severidade do sentimento"""
        abs_score = abs(score)
        if abs_score > 0.8:
            return 'critical'
        elif abs_score > 0.5:
            return 'high'
        elif abs_score > 0.2:
            return 'medium'
        else:
            return 'low'

    def _generate_emotional_insights(self, analysis: Dict[str, Any]) -> Dict[str, str]:
        """Gera insights e recomendações baseadas em análise emocional"""
        insights = {}
        
        overall = analysis.get('overall', {})
        interpretation = overall.get('interpretation', 'neutral')
        severity = overall.get('severity', 'low')
        
        if interpretation in ['very_negative', 'negative']:
            insights['approach'] = 'empathetic'
            insights['tone'] = 'supportive'
            insights['priority'] = 'high'
        elif interpretation in ['positive', 'very_positive']:
            insights['approach'] = 'efficient'
            insights['tone'] = 'appreciative'
            insights['priority'] = 'medium'
        else:
            insights['approach'] = 'informative'
            insights['tone'] = 'professional'
            insights['priority'] = 'normal'
        
        return insights


class BillingContextEnforcer:
    """Garante que todas as respostas permaneçam no escopo de cobranças e faturas"""
    
    def __init__(self):
        self.billing_keywords = [
            'pagamento', 'cobrança', 'fatura', 'boleto', 'pix', 'transferência',
            'dívida', 'valor', 'vencimento', 'parcela', 'desconto', 'juros',
            'multa', 'negociação', 'acordo', 'quitado', 'liquidado', 'saldo',
            'conta', 'bancário', 'financeiro', 'cartão', 'crédito', 'débito'
        ]
        
        self.out_of_scope_responses = [
            "Desculpe, mas só posso ajudar com questões relacionadas a cobranças e faturas.",
            "Entendo sua questão, mas meu foco é exclusivamente em cobranças e pagamentos.",
            "Só trabalho com assuntos financeiros e cobranças. Posso ajudar com sua conta?",
            "Infelizmente, só posso auxiliar com questões de cobrança e faturas.",
            "Meu escopo é exclusivamente cobranças. Como posso ajudar com sua situação financeira?"
        ]
    
    def is_billing_related(self, text: str) -> bool:
        """Verifica se o texto está relacionado a cobranças"""
        text_lower = text.lower()
        
        # Verifica palavras-chave de cobrança
        for keyword in self.billing_keywords:
            if keyword in text_lower:
                return True
        
        # Verifica padrões financeiros
        financial_patterns = [
            r'R\$\s*\d',
            r'\d+\s*reais?',
            r'\b\d+[\/\-]\d+[\/\-]\d+\b',  # Datas
            r'\b(pix|boleto|ted|doc)\b'
        ]
        
        for pattern in financial_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def get_out_of_scope_response(self) -> str:
        """Retorna resposta padrão para tópicos fora do escopo"""
        return random.choice(self.out_of_scope_responses)
    
    def enforce_billing_context(self, user_message: str, proposed_response: str) -> str:
        """Garante que a resposta permaneça no contexto de cobranças"""
        
        # Se a mensagem do usuário não for sobre cobrança, redireciona
        if not self.is_billing_related(user_message):
            return self.get_out_of_scope_response()
        
        # Se a resposta proposta não for sobre cobrança, ajusta
        if not self.is_billing_related(proposed_response):
            return f"{proposed_response} Mas voltando ao que importa - sobre sua cobrança, como posso ajudar?"
        
        return proposed_response
        
    def record_interaction(self, user_message: str, bot_response: str, 
                         user_satisfaction: Optional[float] = None):
        """Registra interação para aprendizado"""
        interaction = {
            "timestamp": datetime.now(),
            "user_message": user_message,
            "bot_response": bot_response,
            "satisfaction": user_satisfaction
        }
        
        message_hash = hash(user_message.lower().strip())
        self.interaction_patterns[message_hash].append(interaction)
        
        if user_satisfaction is not None:
            self.success_metrics[message_hash] = user_satisfaction
    
    def get_improved_response(self, user_message: str) -> Optional[str]:
        """Obtém resposta melhorada baseada no aprendizado"""
        message_hash = hash(user_message.lower().strip())
        
        if message_hash in self.interaction_patterns:
            interactions = self.interaction_patterns[message_hash]
            # Retorna a resposta com maior satisfação
            best_interaction = max(interactions, 
                                 key=lambda x: x.get("satisfaction", 0.0))
            if best_interaction.get("satisfaction", 0) > 0.7:
                return best_interaction["bot_response"]
        
        return None

# Classe IntentClassifier só é criada se PyTorch estiver disponível
if TORCH_AVAILABLE:
    class IntentClassifier(torch.nn.Module):
        """Classificador de intenções usando BERT"""
        
        def __init__(self, num_intents: int, hidden_size: int = 768, dropout: float = 0.3):
            super().__init__()
            if TRANSFORMERS_AVAILABLE:
                self.bert = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')
                self.dropout = torch.nn.Dropout(dropout)
                self.classifier = torch.nn.Linear(hidden_size, num_intents)
            else:
                self.bert = None
                self.dropout = None
                self.classifier = None
            
        def forward(self, input_ids, attention_mask):
            outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
            pooled_output = outputs.pooler_output
            output = self.dropout(pooled_output)
            return self.classifier(output)
else:
    # Fallback quando PyTorch não está disponível
    class IntentClassifier:
        """Classificador de intenções simples (fallback sem PyTorch)"""
        
        def __init__(self, *args, **kwargs):
            self.available = False
            
        def forward(self, *args, **kwargs):
            return None

class BillingChatBot:
    """🤖 CLAUDIA DA DESK - BOT CONVERSACIONAL SUPREMO 🚀
    Sistema de IA de Última Geração com:
    - Inteligência Emocional Avançada
    - Memória Conversacional Profunda  
    - Compreensão Semântica Suprema
    - Personalidade Empática e Natural
    - FOCO EXCLUSIVO EM COBRANÇAS E FATURAS
    """
    
    def __init__(self):
        self.config = active_config
        self.device = torch.device(self.config.MODEL_DEVICE) if TORCH_AVAILABLE else None
        
        # 🧠 CONFIGURAÇÕES SUPREMAS DO MODELO
        self.max_length = self.config.MODEL_MAX_LENGTH
        self.temperature = self.config.MODEL_TEMPERATURE
        
        # 🔤 TOKENIZER AVANÇADO PARA PORTUGUÊS
        if TRANSFORMERS_AVAILABLE:
            self.tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
        else:
            self.tokenizer = None
        
        # 🌟 SISTEMAS DE IA SUPREMOS - AGORA COM FOCO EM COBRANÇAS
        self.text_normalizer = BrazilianTextNormalizer()
        self.emotional_intelligence = EmotionalIntelligence()
        self.memory_system = AdvancedMemorySystem()
        self.spell_corrector = SpellCorrector()
        self.billing_nlp = AdvancedBillingNLP()
        self.billing_enforcer = BillingContextEnforcer()
        self.context_enforcer = BillingContextEnforcer()
        
        # 🎯 INTENTS E RESPOSTAS EXPANDIDOS - EXCLUSIVO COBRANÇAS
        self.intents = self._load_advanced_intents()
        self.responses = self._load_claudia_responses()
        self.emotional_responses = self._load_emotional_responses()
        
        # 🧮 MODELOS NEURAIS
        self.intent_model = None
        self.intent_labels = list(self.intents.keys())
        
        # 🚀 CARREGAMENTO AVANÇADO
        self._load_or_initialize_model()
        self.patterns = self._compile_advanced_patterns()
        
        # 💾 SISTEMA DE APRENDIZADO CONTÍNUO
        self.conversation_learning = ConversationLearning()
        
        app_logger.info("🤖 CLAUDIA SUPREMA INICIALIZADA", {
            "emotional_intelligence": True,
            "memory_system": True,
            "advanced_nlp": True,
            "billing_focus": True,
            "context_enforcement": True,
            "device": str(self.device)
        })
        
    def _load_advanced_intents(self) -> Dict[str, List[str]]:
        """Carrega intents expandidos EXCLUSIVOS para cobranças e faturas"""
        return {
            "saudacao": [
                # Formal
                "oi", "olá", "bom dia", "boa tarde", "boa noite", "oi tudo bem",
                # Coloquial e abreviado
                "oi", "ola", "oie", "oii", "oiii", "e ai", "eae", "fala", "fala ai",
                "bd", "bt", "bn", "blz", "beleza", "tudo bem", "td bem", "suave",
                "salve", "opa", "opa blz", "ei", "hey", "alô", "alo",
                # Com erros de digitação
                "bom fis", "boa tards", "tudo bm", "td bm", "tlg", "tmj"
            ],
            "confirmacao_pagamento": [
                # Formal - Pagamentos
                "já paguei", "pagamento feito", "paguei", "fiz o pagamento", "quitei",
                "já foi pago", "transferi", "fiz a transferência", "pix feito",
                "pago via boleto", "compensado", "liquidei", "quitei a dívida",
                # Coloquial/abreviado
                "ja paguei", "paguei ja", "ja pago", "ja foi", "ja ta pago",
                "fiz pix", "mandei pix", "transferi ja", "ja transferi",
                "paguei ontem", "paguei hj", "paguei hoje", "paguei boleto",
                "compensei", "paguei a fatura", "paguei conta", "quitei divida",
                # Com erros
                "ja pagei", "paguie", "ja pagiei", "fis pagamento", "quitei ja",
                "pixi feito", "fis pix", "transferi onti", "baguei",
                # Gírias
                "ja foi esse role", "ja resolvi", "ja era", "mandei a grana",
                "ja mandei", "ja enviei", "ja depositei", "quitei", "paguei tudo"
            ],
            "negociacao": [
                # Formal - Negociação de dívidas
                "posso parcelar", "parcelamento", "desconto", "não posso pagar",
                "dificuldades", "negociar", "prazo", "condições", "renegociar",
                "acordo", "acordo de pagamento", "proposta", "entrada",
                # Coloquial
                "da pra parcelar", "parcela ai", "divide ai", "nao consigo pagar",
                "nao to conseguindo", "ta dificil", "ta apertado", "sem grana",
                "quebrado", "duro", "liso", "zerado", "sem dinheiro", "sem condições",
                "vamo negociar", "da um desconto", "abaixa ai", "faz um preco",
                "parcela minha divida", "entra em acordo", "faz um acordo",
                # Com erros
                "parcelar", "nao consigo", "difficuldades", "negosiar",
                "descontinho", "abaicha", "ta difisil", "sem dinherio",
                # Expressões populares
                "to sem condições", "to liso", "to quebrado", "sem bufunfa",
                "desempregado", "sem trampo", "perdeu emprego", "demitido",
                "nao recebi", "salario atrasado", "esperando pagamento"
            ],
            "informacoes": [
                # Formal - Informações de cobrança
                "qual valor", "quanto devo", "data vencimento", "dados pagamento",
                "como pagar", "número conta", "pix", "dados bancários", "boleto",
                "linha digitavel", "codigo barras", "vencimento", "valor original",
                "valor atualizado", "juros", "multa", "atraso", "saldo devedor",
                # Coloquial
                "quanto é", "quanto ta", "qnto", "valor", "preco", "quanto falta",
                "como que paga", "onde pago", "chave pix", "conta", "boleto",
                "dados", "info", "informação", "detalhes", "situacao", "status",
                # Com erros
                "qunto", "qnto devo", "infomação", "detos", "pixe",
                "conta bancariya", "como q pago", "ond pago", "boletu"
            ],
            "contestacao": [
                # Formal - Contestação de cobrança
                "não devo", "erro", "não reconheço", "contestar", "disputa",
                "duplicata", "cobrança indevida", "valor errado", "duvida da compra",
                "nao fiz essa compra", "nao autorizei", "fraude", "clonaram meu cartao",
                # Coloquial
                "nao devo nada", "isso ta errado", "nunca comprei", "nao fiz compra",
                "nao eh meu", "nao fui eu", "engano", "erro ai", "cobranca errada",
                "ta errado isso", "nao conheço", "quem eh voces", "golpe", "fraude",
                "nao autorizei pagamento", "nao reconheco essa compra",
                # Com raiva/frustração
                "que isso", "que historia eh essa", "golpe", "nao caio",
                "para de ligar", "nao quero", "deixa eu em paz", "assédio",
                # Com erros
                "nao dvo", "tah errado", "nunka comprei", "nao foi eu", "nao autorizei"
            ],
            "agendamento": [
                # Formal - Agendamento de pagamento
                "pagar amanhã", "semana que vem", "próxima semana", "agendar",
                "data para pagar", "quando posso pagar", "prazo", "vencimento",
                "recebo dia", "data do pagamento", "marcar pagamento",
                # Coloquial
                "pago amanha", "pago semana q vem", "semana q vem", "na sexta",
                "no sabado", "segunda feira", "depois do pagamento", "quando cair",
                "recebo dia 5", "quando receber", "fim do mes", "quando der",
                "no outro mes", "daqui uma semana", "daqui 15 dias",
                # Com erros
                "pago amanha", "seman q vem", "seista feira", "sesta",
                "depos", "fim do mex", "quano receber", "daqui huma semana"
            ],
            "despedida": [
                # Formal
                "tchau", "até logo", "obrigado", "valeu", "ok", "até breve",
                # Coloquial
                "vlw", "valew", "brigado", "obrigada", "obg", "obrigadão",
                "tmj", "falou", "flw", "ate mais", "ate logo", "até",
                "blz", "beleza", "suave", "de boa", "ok entendi", "ta certo",
                # Com erros
                "brigadu", "vlws", "falow", "ati mais", "obriqado", "até logu"
            ],
            "pedido_ajuda": [
                # Formal - Ajuda com cobrança
                "help", "ajuda", "não entendi", "como funciona", "dúvida",
                "me ajuda", "nao entendi nada", "como assim", "explica ai",
                "nao to entendendo", "confuso", "perdido", "como que eh",
                "o que significa", "nao sei", "ensina ai", "como faz",
                # Com erros
                "nao intendi", "ajuda ai", "como asim", "esplica",
                "nao to intendendo", "perdidu", "nao seii"
            ],
            "ansiedade_cobranca": [
                # Expressões de ansiedade/preocupação sobre cobrança
                "to preocupado", "to nervoso", "que vai acontecer",
                "vao me processar", "nome sujo", "spc", "serasa",
                "protesto", "negativado", "score baixo", "vai pra justiça",
                "vao me executar", "vao penhorar", "vao tomar meu bem",
                "vai ficar no spc", "vai prejudicar meu nome", "consequencias",
                "multa", "juros", "encargos", "atraso", "vencimento"
            ],
            "situacao_financeira": [
                # Explicações da situação financeira
                "perdi emprego", "desempregado", "sem trabalho", "doente",
                "internado", "hospital", "familia doente", "problemas pessoais",
                "separacao", "divorcio", "morte na familia", "salario reduzido",
                "empresa fechou", "sem renda", "contas atrasadas", "dividas"
            ],
            "status_conta": [
                # Status específico de conta/cobrança
                "status da conta", "minha conta", "situacao da divida", "saldo atual",
                "valor em aberto", "conta em atraso", "conta vencida", "quitacao",
                "baixa", "desconto", "abono", "perdao de divida"
            ],
            "comprovante": [
                # Comprovantes de pagamento
                "comprovante", "comprovante de pagamento", "recibo", "protocolo",
                "confirmação", "comprovante pix", "comprovante boleto", "protocolo atendimento"
            ]
        }
    
    def _load_claudia_responses(self) -> Dict[str, List[str]]:
        """Respostas da Claudia - empática e profissional, mas acessível"""
        return {
            "saudacao": [
                "Oi! Eu sou a Claudia da Desk! 😊 Como posso te ajudar hoje?",
                "Olá! Claudia aqui da Desk. Estou aqui pra resolver sua situação!",
                "E aí! Sou a Claudia da Desk. Vamos conversar sobre seu pagamento?",
                "Oi! Claudia da Desk falando. Como posso facilitar pra você hoje?"
            ],
            "confirmacao_pagamento": [
                "Que ótimo! 🎉 Vou verificar seu pagamento aqui no sistema. Obrigada por avisar!",
                "Perfeito! Já anotei que você pagou. Vou confirmar tudo certinho pra você! ✅",
                "Maravilha! Recebemos sim. Só me dá uns minutinhos pra confirmar no sistema, ok?",
                "Show! Pagamento confirmado. Você é 10! Muito obrigada! 👏"
            ],
            "negociacao": [
                "Olha, eu te entendo perfeitamente! 💙 Vamos achar uma solução boa pra você.",
                "Sem estresse! A gente sempre dá um jeito. Que tal conversarmos sobre as opções?",
                "Imagino como deve estar difícil. Relaxa que vamos resolver isso juntos! 🤝",
                "Entendo sua situação. Aqui na Desk a gente sempre encontra uma saída!"
            ],
            "informacoes": [
                "Claro! Vou te passar tudo certinho! 📋 Qualquer dúvida me fala, ok?",
                "Sem problema! Deixa eu buscar suas informações aqui...",
                "Opa! Vou te explicar tudinho. É só um momento que já te mando os dados!",
                "Pode deixar comigo! Vou te dar todas as informações que você precisa! 💬"
            ],
            "contestacao": [
                "Nossa, que situação! 😮 Vou verificar isso urgente pra você, pode deixar!",
                "Eita! Vamos esclarecer isso já! Me dá só um momento pra investigar...",
                "Que estranho mesmo! Deixa eu ver o que rolou aqui no sistema...",
                "Entendi sua preocupação. Vou apurar tudo direitinho pra gente resolver!"
            ],
            "agendamento": [
                "Tranquilo! 📅 Vamos agendar numa data boa pra você. Quando fica melhor?",
                "Sem problema! A gente agenda certinho. Qual dia você consegue?",
                "Perfeito! Vamos organizar isso. Me fala quando dá pra você!",
                "Ótima ideia! Vamos marcar uma data que funcione no seu orçamento!"
            ],
            "despedida": [
                "Valeu! 👋 Qualquer coisa me chama aqui que a Claudia resolve!",
                "Até logo! Foi um prazer te ajudar! Claudia da Desk sempre à disposição! 😊",
                "Tchau! Lembra que estou sempre aqui quando precisar, viu?",
                "Falou! Claudia da Desk se despede. Até a próxima! 🌟"
            ],
            "pedido_ajuda": [
                "Claro! Deixa a Claudia explicar tudinho pra você! 🤗",
                "Sem problema! Vou te explicar do jeitinho mais fácil!",
                "Opa! Não se preocupa, vou te ensinar passo a passo!",
                "Relaxa! A Claudia tá aqui pra isso mesmo. Vamos lá!"
            ],
            "ansiedade_cobranca": [
                "Ei, calma! 😌 Não precisa ficar preocupado. Vamos resolver isso numa boa!",
                "Relaxa! Aqui na Desk a gente sempre dá um jeito. Sem estresse!",
                "Fica tranquilo! Ninguém vai te prejudicar. Vamos conversar e resolver! 💙"
            ],
            "situacao_financeira": [
                "Nossa, que fase difícil! 😔 Fica tranquilo que vamos encontrar uma saída juntos.",
                "Entendo perfeitamente sua situação. Vamos achar uma solução que caiba no seu bolso!",
                "Imagino como deve estar pesado pra você. A gente vai dar um jeito! 🤝"
            ],
            "default": [
                "Hmm, não entendi muito bem... 🤔 Pode me explicar de outro jeito?",
                "Opa! Não captei direito. Me fala de novo de uma forma diferente?",
                "Desculpa, não consegui entender. Reformula aí pra mim?",
                "Eita! Não peguei a informação. Tenta me explicar novamente?"
            ]
        }
    
    def _load_emotional_responses(self) -> Dict[str, Dict[str, List[str]]]:
        """Respostas da Claudia baseadas no estado emocional do usuário"""
        return {
            "raiva": {
                "saudacao": [
                    "Oi! Percebo que você pode estar um pouco irritado... 😔 Sou a Claudia da Desk, vamos resolver isso juntos!",
                    "Olá! Claudia aqui. Vejo que algo te incomodou, mas relaxa que vamos dar um jeito nisso! 🤗"
                ],
                "geral": [
                    "Entendo sua irritação! 😤 Vamos resolver isso de uma vez por todas!",
                    "Sei que está chateado, e tem todo direito! Deixa a Claudia cuidar disso pra você! 💪",
                    "Fica tranquilo! Quando a gente terminar aqui, você vai sair satisfeito! 🎯"
                ]
            },
            "tristeza": {
                "saudacao": [
                    "Oi... Sou a Claudia da Desk. Percebo que você pode estar passando por um momento difícil 😔 Como posso ajudar?",
                    "Olá! Claudia aqui. Sei que às vezes as coisas ficam complicadas... Vamos conversar numa boa? 💙"
                ],
                "geral": [
                    "Imagino como deve estar sendo difícil pra você... 😔 Mas vamos achar uma solução juntos!",
                    "Entendo perfeitamente sua situação. A Claudia está aqui pra te apoiar! 🤗",
                    "Sei que está pesado, mas você não está sozinho nisso. Vamos resolver! 💙"
                ]
            },
            "alegria": {
                "saudacao": [
                    "Oi! Que energia boa! 😊 Sou a Claudia da Desk! Como posso te ajudar hoje?",
                    "Olá! Claudia aqui! Adorei seu astral! Vamos resolver tudo rapidinho! ✨"
                ],
                "geral": [
                    "Que bom ver você animado! 😊 Isso facilita muito nossa conversa!",
                    "Sua energia positiva é contagiante! Vamos manter esse clima bom! ⭐",
                    "Adorei seu jeito! Com essa disposição, resolvemos tudo rapidinho! 🚀"
                ]
            },
            "medo": {
                "saudacao": [
                    "Oi! Sou a Claudia da Desk. Fica tranquilo, aqui é um ambiente seguro pra gente conversar 😌",
                    "Olá! Claudia aqui. Não precisa se preocupar, vamos esclarecer tudo devagar! 🤲"
                ],
                "geral": [
                    "Relaxa! Não tem nada pra se preocupar. A Claudia vai cuidar de tudo! 😌",
                    "Fica tranquilo! Aqui na Desk a gente resolve tudo numa boa! 🛡️",
                    "Não precisa ter medo! Vou te explicar tudo passo a passo! 🤝"
                ]
            },
            "surpresa": {
                "saudacao": [
                    "Oi! Sou a Claudia da Desk! Alguma coisa te surpreendeu? Vamos esclarecer! 😮",
                    "Olá! Claudia aqui! Parece que você ficou surpreso com algo... Me conta! 🤔"
                ],
                "geral": [
                    "Nossa! Também fiquei surpresa! Vamos entender isso juntos! 😮",
                    "Que situação mesmo! Deixa eu ver o que aconteceu... 🕵️‍♀️",
                    "Realmente é surpreendente! Vamos investigar isso! 🔍"
                ]
            },
            "frustração": {
                "saudacao": [
                    "Oi... Sou a Claudia da Desk. Sei que você deve estar cansado dessa situação 😔 Vamos resolver!",
                    "Olá! Claudia aqui. Percebo sua frustração... Mas agora chegou a hora de resolver de vez! 💪"
                ],
                "geral": [
                    "Entendo sua frustração! Chega de enrolação, vamos resolver isso AGORA! 🎯",
                    "Sei que você já tentou de tudo... Mas comigo vai ser diferente! 💫",
                    "Cansei junto com você! Agora é comigo, e eu não desisto! 🔥"
                ]
            }
        }
    
    def _compile_patterns(self) -> Dict[str, List]:
        """Compila padrões regex para detecção rápida"""
        patterns = {}
        
        # Padrões para valores monetários
        patterns["valor_money"] = [
            re.compile(r'R\$\s*(\d+(?:[.,]\d{2})?)', re.IGNORECASE),
            re.compile(r'(\d+)\s*reais?', re.IGNORECASE),
            re.compile(r'(\d+[.,]\d{2})', re.IGNORECASE)
        ]
        
        # Padrões para datas
        patterns["data"] = [
            re.compile(r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})'),
            re.compile(r'(amanhã|hoje|ontem)', re.IGNORECASE),
            re.compile(r'(segunda|terça|quarta|quinta|sexta|sábado|domingo)', re.IGNORECASE)
        ]
        
        # Padrões para confirmação
        patterns["confirmacao"] = [
            re.compile(r'\b(sim|yes|ok|certo|correto|exato)\b', re.IGNORECASE),
            re.compile(r'\b(não|no|nao|nope|errado)\b', re.IGNORECASE)
        ]
        
        return patterns
    
    def _load_or_initialize_model(self):
        """Carrega modelo existente ou inicializa novo"""
        try:
            model_path = self.config.MODEL_PATH
            if torch.cuda.is_available() and self.device.type == 'cuda':
                checkpoint = torch.load(model_path)
            else:
                checkpoint = torch.load(model_path, map_location='cpu')
            
            self.intent_model = IntentClassifier(len(self.intent_labels))
            self.intent_model.load_state_dict(checkpoint['model_state_dict'])
            self.intent_model.to(self.device)
            self.intent_model.eval()
            
            app_logger.info("CHATBOT_MODEL_LOADED", {"model_path": model_path})
            
        except Exception as e:
            app_logger.warning("CHATBOT_MODEL_LOAD_FAILED", {"error": str(e)})
            # Inicializa modelo vazio para treinamento futuro
            self.intent_model = IntentClassifier(len(self.intent_labels))
            self.intent_model.to(self.device)
    
    async def process_message(self, message: str, context: ConversationContext, user_id: str = None) -> Dict[str, Any]:
        """🚀 PROCESSAMENTO SUPREMO DE MENSAGEM - NÍVEL CHATGPT++"""
        
        result = {
            "response": "",
            "intent": "default",
            "confidence": 0.0,
            "entities": {},
            "actions": [],
            "context_updates": {},
            "emotional_state": None,
            "semantic_understanding": None,
            "memory_context": None
        }
        
        try:
            # 🧠 ANÁLISE EMOCIONAL SUPREMA
            emotional_state = self.emotional_intelligence.analyze_emotion(message)
            result["emotional_state"] = emotional_state
            
            # 🔒 VERIFICAÇÃO DE ESCOPO - 100% COBRANÇAS
            if not self.context_enforcer.is_billing_related(message):
                result["response"] = self.context_enforcer.get_out_of_scope_response()
                result["intent"] = "out_of_scope"
                result["confidence"] = 1.0
                return result
            
            # 💾 RECUPERAÇÃO DE MEMÓRIA CONTEXTUAL
            user_id = user_id or context.user_id or "anonymous"
            memory_context = self.memory_system.get_contextual_information(user_id, message)
            result["memory_context"] = memory_context
            
            # 🔧 PRÉ-PROCESSAMENTO SUPREMO
            clean_message = self._preprocess_message(message)
            
            # 🎯 PROCESSAMENTO NLP AVANÇADO PARA COBRANÇAS
            billing_intent = self.billing_nlp.extract_billing_intent(clean_message)
            financial_entities = self.billing_nlp.extract_financial_entities(clean_message)
            financial_sentiment = self.billing_nlp.analyze_financial_sentiment(clean_message)
            
            # Atualiza resultados com informações financeiras
            result["financial_entities"] = financial_entities
            result["financial_sentiment"] = financial_sentiment
            
            # 📊 ATUALIZA CONTEXTO DE COBRANÇA
            try:
                from backend.models.conversation import conversation_manager
                import datetime as dt
                
                payment_method = None
                if 'payment_method' in financial_entities and financial_entities['payment_method']:
                    payment_method = financial_entities['payment_method'][0]
                
                due_date = None
                if 'due_date' in financial_entities and financial_entities['due_date']:
                    try:
                        due_date = dt.datetime.strptime(financial_entities['due_date'][0], '%Y-%m-%d')
                    except ValueError:
                        try:
                            due_date = dt.datetime.strptime(financial_entities['due_date'][0], '%d/%m/%Y')
                        except ValueError:
                            pass
                
                conversation_manager.update_billing_context(
                    user_id, 
                    financial_entities, 
                    billing_intent['intent'] if billing_intent['confidence'] > 0.7 else intent_result["intent"],
                    payment_method,
                    due_date
                )
            except ImportError:
                app_logger.warning("CONVERSATION_MANAGER_NOT_AVAILABLE", {"user_id": user_id})
            except Exception as e:
                app_logger.error("BILLING_CONTEXT_UPDATE_ERROR", e, {"user_id": user_id})
            
            # 🎯 CLASSIFICAÇÃO DE INTENT INTELIGENTE
            intent_result = await self._classify_intent_supreme(clean_message, emotional_state, memory_context)
            
            # Prioriza intenções de cobrança se detectadas
            if billing_intent['confidence'] > 0.7:
                intent_result["intent"] = billing_intent['intent']
                intent_result["confidence"] = max(intent_result["confidence"], billing_intent['confidence'])
            
            result["intent"] = intent_result["intent"]
            result["confidence"] = intent_result["confidence"]
            
            # 📈 TRACKING DE NEGOCIAÇÃO
            try:
                from backend.models.conversation import conversation_manager
                if intent_result["intent"] in ['negociacao', 'contestacao', 'situacao_financeira']:
                    conversation_manager.increment_negotiation_attempt(user_id)
            except ImportError:
                pass
            
            # 🔍 EXTRAÇÃO DE ENTIDADES AVANÇADA
            result["entities"] = self._extract_entities_advanced(clean_message, emotional_state)
            result["entities"].update(financial_entities)
            
            # 🧮 COMPREENSÃO SEMÂNTICA
            semantic_understanding = self._analyze_semantic_understanding(
                clean_message, result["intent"], emotional_state, memory_context
            )
            result["semantic_understanding"] = semantic_understanding
            
            # 💬 GERAÇÃO DE RESPOSTA SUPREMA
            response_data = await self._generate_supreme_response(
                message,
                clean_message,
                result["intent"],
                result["entities"],
                emotional_state,
                memory_context,
                context
            )
            
            result.update(response_data)
            
            # 🔒 GARANTIA FINAL DE CONTEXTO - 100% COBRANÇAS
            result["response"] = self.context_enforcer.enforce_billing_context(
                message, result["response"]
            )
            
            # 📚 ATUALIZAÇÃO DE MEMÓRIA
            extracted_facts = self._extract_conversation_facts(message, result["response"], result["intent"])
            self.memory_system.update_memory(
                user_id, message, result["response"], emotional_state, extracted_facts
            )
            
            # 📊 APRENDIZADO CONTÍNUO
            self.conversation_learning.record_interaction(message, result["response"])
            
            # 📝 LOG SUPREMO
            conversation_logger.info("🤖 SUPREME_MESSAGE_PROCESSED", {
                "intent": result["intent"],
                "confidence": result["confidence"],
                "emotion": emotional_state.primary_emotion,
                "emotion_intensity": emotional_state.intensity,
                "entities_count": len(result["entities"]),
                "actions_count": len(result["actions"]),
                "semantic_score": semantic_understanding.intent_confidence if semantic_understanding else 0,
                "memory_facts": len(extracted_facts)
            })
            
        except Exception as e:
            app_logger.error("SUPREME_PROCESSING_ERROR", e, {
                "message_length": len(message),
                "user_id": user_id
            })
            result["response"] = "Ai, que problema! 😅 A Claudia deu uma travadinha... Pode repetir pra mim?"
            result["intent"] = "error"
        
        return result
    
    def _preprocess_message(self, message: str) -> str:
        """Pré-processa mensagem com normalização suprema"""
        # Primeiro, normaliza o texto coloquial brasileiro
        normalized = self.text_normalizer.normalize(message)
        
        # Corrige ortografia de palavras importantes
        words = normalized.split()
        corrected_words = []
        
        for word in words:
            corrected_word = self.spell_corrector.correct_word(word)
            corrected_words.append(corrected_word)
        
        final_text = ' '.join(corrected_words)
        
        # Log da transformação para debug
        if message.lower().strip() != final_text:
            app_logger.info("TEXT_NORMALIZATION", {
                "original": message,
                "normalized": final_text,
                "intent_signals": self.text_normalizer.extract_intent_signals(message)
            })
        
        return final_text
    
    async def _classify_intent_supreme(self, message: str, emotional_state: EmotionalState, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """🎯 CLASSIFICAÇÃO DE INTENT SUPREMA COM IA EMOCIONAL"""
        
        # Primeiro verifica aprendizado contínuo
        learned_response = self.conversation_learning.get_improved_response(message)
        if learned_response:
            # Extrai intent da resposta aprendida (simplificado)
            return {"intent": "learned_response", "confidence": 0.95}
        
        # Classificação tradicional melhorada
        rule_intent = self._classify_by_rules(message)
        
        # 🧠 BOOST EMOCIONAL - Ajusta intent baseado na emoção
        emotional_boost = self._apply_emotional_intent_boost(rule_intent, emotional_state)
        
        # 💾 BOOST DE MEMÓRIA - Ajusta baseado no histórico
        memory_boost = self._apply_memory_intent_boost(emotional_boost, memory_context)
        
        # Se modelo neural estiver disponível, combina resultados
        if self.intent_model is not None:
            try:
                neural_intent = await self._classify_by_neural_model(message)
                
                # 🔥 ENSEMBLE SUPREMO - Combina todas as fontes
                final_intent = self._supreme_intent_ensemble(
                    rule_intent, neural_intent, memory_boost, emotional_state
                )
                return final_intent
                
            except Exception as e:
                app_logger.warning("NEURAL_CLASSIFICATION_FAILED", {"error": str(e)})
        
        return memory_boost
    
    def _apply_emotional_intent_boost(self, intent_result: Dict[str, Any], emotional_state: EmotionalState) -> Dict[str, Any]:
        """Aplica boost baseado no estado emocional"""
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        emotion = emotional_state.primary_emotion
        intensity = emotional_state.intensity
        
        # Regras de boost emocional
        emotional_boosts = {
            "raiva": {
                "contestacao": 0.3,
                "negociacao": 0.2,
                "pedido_ajuda": 0.1
            },
            "tristeza": {
                "negociacao": 0.4,
                "situacao_financeira": 0.3,
                "pedido_ajuda": 0.2
            },
            "medo": {
                "ansiedade_cobranca": 0.4,
                "pedido_ajuda": 0.3,
                "informacoes": 0.2
            },
            "frustração": {
                "contestacao": 0.3,
                "negociacao": 0.2,
                "pedido_ajuda": 0.2
            }
        }
        
        if emotion in emotional_boosts and intent in emotional_boosts[emotion]:
            boost = emotional_boosts[emotion][intent] * intensity
            confidence = min(confidence + boost, 1.0)
        
        return {"intent": intent, "confidence": confidence}
    
    def _apply_memory_intent_boost(self, intent_result: Dict[str, Any], memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica boost baseado na memória conversacional"""
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        # Se o usuário já mostrou padrão de comportamento específico
        emotional_pattern = memory_context.get("emotional_pattern", {})
        recent_emotions = emotional_pattern.get("recent_emotion", "neutro")
        
        # Boost baseado em padrões emocionais recentes
        pattern_boosts = {
            "raiva": {"contestacao": 0.2, "negociacao": 0.1},
            "tristeza": {"negociacao": 0.3, "situacao_financeira": 0.2},
            "frustração": {"contestacao": 0.2}
        }
        
        if recent_emotions in pattern_boosts and intent in pattern_boosts[recent_emotions]:
            boost = pattern_boosts[recent_emotions][intent]
            confidence = min(confidence + boost, 1.0)
        
        return {"intent": intent, "confidence": confidence}
    
    def _supreme_intent_ensemble(self, rule_intent: Dict, neural_intent: Dict, memory_intent: Dict, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Combina todos os métodos de classificação"""
        
        # Pesos dos diferentes classificadores
        weights = {
            "rule": 0.4,
            "neural": 0.3,
            "memory": 0.2,
            "emotional": 0.1
        }
        
        # Se emoção é intensa, dá mais peso ao contexto emocional
        if emotional_state.intensity > 0.7:
            weights["memory"] += 0.1
            weights["neural"] -= 0.1
        
        # Calcula score ponderado
        candidates = [
            (rule_intent["intent"], rule_intent["confidence"] * weights["rule"]),
            (neural_intent["intent"], neural_intent["confidence"] * weights["neural"]),
            (memory_intent["intent"], memory_intent["confidence"] * weights["memory"])
        ]
        
        # Escolhe o melhor
        best_intent, best_score = max(candidates, key=lambda x: x[1])
        
        return {"intent": best_intent, "confidence": min(best_score, 1.0)}
    
    def _extract_entities_advanced(self, message: str, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Extração de entidades com consciência emocional"""
        entities = self._extract_entities(message)
        
        # Adiciona contexto emocional
        entities["emotional_intensity"] = emotional_state.intensity
        entities["emotional_indicators"] = emotional_state.indicators
        
        # Extrai entidades específicas por emoção
        if emotional_state.primary_emotion == "raiva":
            # Procura por alvos da raiva
            anger_targets = re.findall(r'(vocês|empresa|sistema|banco|atendimento)', message.lower())
            if anger_targets:
                entities["anger_target"] = anger_targets[0]
        
        elif emotional_state.primary_emotion == "tristeza":
            # Procura por motivos da tristeza
            sadness_reasons = re.findall(r'(desemprego|doente|família|perdeu|morreu)', message.lower())
            if sadness_reasons:
                entities["sadness_reason"] = sadness_reasons[0]
        
        return entities
    
    def _analyze_semantic_understanding(self, message: str, intent: str, emotional_state: EmotionalState, memory_context: Dict[str, Any]) -> SemanticUnderstanding:
        """Análise de compreensão semântica avançada"""
        
        # Calcula métricas de compreensão
        intent_confidence = 0.8  # Placeholder - seria calculado com modelo semântico
        
        # Similaridade semântica com mensagens anteriores
        semantic_similarity = 0.7 if memory_context.get("conversation_count", 0) > 0 else 0.5
        
        # Relevância contextual baseada na emoção
        contextual_relevance = 0.9 if emotional_state.confidence > 0.7 else 0.6
        
        # Alinhamento emocional (se a resposta está adequada à emoção)
        emotional_alignment = 0.8 if emotional_state.primary_emotion != "neutro" else 0.5
        
        # Coerência do tópico
        topic_coherence = 0.8  # Placeholder
        
        return SemanticUnderstanding(
            intent_confidence=intent_confidence,
            semantic_similarity=semantic_similarity,
            contextual_relevance=contextual_relevance,
            emotional_alignment=emotional_alignment,
            topic_coherence=topic_coherence
        )
    
    def _extract_conversation_facts(self, message: str, response: str, intent: str) -> Dict[str, Any]:
        """Extrai fatos importantes da conversa"""
        facts = {}
        
        # Extrai informações sobre situação financeira
        financial_keywords = ["desempregado", "sem trabalho", "doente", "hospital", "divórcio"]
        for keyword in financial_keywords:
            if keyword in message.lower():
                facts["financial_situation"] = keyword
        
        # Extrai preferências de pagamento
        payment_preferences = ["pix", "boleto", "cartão", "dinheiro"]
        for preference in payment_preferences:
            if preference in message.lower():
                facts["payment_preference"] = preference
        
        # Extrai horários preferenciais se mencionados
        time_patterns = re.findall(r'(\d{1,2}h|\d{1,2}:\d{2}|manhã|tarde|noite)', message.lower())
        if time_patterns:
            facts["preferred_time"] = time_patterns[0]
        
        return facts
    
    async def _classify_intent(self, message: str) -> Dict[str, Any]:
        """Classifica intent da mensagem"""
        
        # Primeiro tenta classificação baseada em regras simples
        rule_intent = self._classify_by_rules(message)
        if rule_intent["confidence"] > 0.8:
            return rule_intent
        
        # Se modelo estiver disponível, usa classificação neural
        if self.intent_model is not None:
            try:
                neural_intent = await self._classify_by_neural_model(message)
                
                # Combina resultados (ensemble)
                if neural_intent["confidence"] > rule_intent["confidence"]:
                    return neural_intent
                else:
                    return rule_intent
                    
            except Exception as e:
                app_logger.warning("NEURAL_CLASSIFICATION_FAILED", {"error": str(e)})
                return rule_intent
        
        return rule_intent
    
    def _classify_by_rules(self, message: str) -> Dict[str, Any]:
        """Classificação suprema baseada em regras e padrões brasileiros"""
        best_intent = "default"
        best_score = 0.0
        
        # Extrai sinais de intenção primeiro
        intent_signals = self.text_normalizer.extract_intent_signals(message)
        
        # Se temos sinais claros, damos peso extra
        signal_boost = {
            "payment_confirmed": ("confirmacao_pagamento", 0.8),
            "wants_negotiation": ("negociacao", 0.7),
            "disputes_charge": ("contestacao", 0.9)
        }
        
        for signal in intent_signals:
            if signal in signal_boost:
                intent, confidence = signal_boost[signal]
                if confidence > best_score:
                    best_intent = intent
                    best_score = confidence
        
        # Classificação tradicional por palavras-chave (melhorada)
        for intent, examples in self.intents.items():
            score = 0.0
            matches = 0
            total_match_length = 0
            
            for example in examples:
                if example.lower() in message.lower():
                    matches += 1
                    match_length = len(example)
                    total_match_length += match_length
                    
                    # Pontuação baseada na relevância da palavra
                    if match_length > 3:  # Palavras mais longas são mais específicas
                        score += match_length * 1.5
                    else:
                        score += match_length
            
            # Normaliza score considerando o tamanho da mensagem e exemplos
            if matches > 0:
                # Score baseado na proporção de matches e relevância
                relevance_score = total_match_length / len(message) if len(message) > 0 else 0
                match_density = matches / len(examples) if len(examples) > 0 else 0
                
                normalized_score = min((relevance_score + match_density) / 2, 1.0)
                
                # Boost para intents mais específicos
                if intent in ["confirmacao_pagamento", "contestacao", "ansiedade_cobranca"]:
                    normalized_score *= 1.2
                
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_intent = intent
        
        # Ajuste final de confiança
        confidence = min(best_score, 1.0)
        
        return {
            "intent": best_intent,
            "confidence": confidence
        }
    
    async def _classify_by_neural_model(self, message: str) -> Dict[str, Any]:
        """Classificação usando modelo neural"""
        try:
            # Tokeniza mensagem
            inputs = self.tokenizer(
                message,
                return_tensors="pt",
                max_length=self.max_length,
                truncation=True,
                padding=True
            )
            
            # Move para device apropriado
            input_ids = inputs["input_ids"].to(self.device)
            attention_mask = inputs["attention_mask"].to(self.device)
            
            # Faz predição
            with torch.no_grad():
                outputs = self.intent_model(input_ids, attention_mask)
                probabilities = torch.nn.functional.softmax(outputs, dim=-1)
                
                # Obtém melhor predição
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][predicted_class].item()
                
                intent = self.intent_labels[predicted_class]
                
                return {
                    "intent": intent,
                    "confidence": confidence
                }
                
        except Exception as e:
            app_logger.error("NEURAL_MODEL_PREDICTION_ERROR", e)
            return {"intent": "default", "confidence": 0.0}
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extrai entidades da mensagem"""
        entities = {}
        
        # Extrai valores monetários
        for pattern in self.patterns["valor_money"]:
            matches = pattern.findall(message)
            if matches:
                entities["valor"] = matches[0]
        
        # Extrai datas
        for pattern in self.patterns["data"]:
            matches = pattern.findall(message)
            if matches:
                entities["data"] = matches[0]
        
        # Extrai confirmações
        for pattern in self.patterns["confirmacao"]:
            matches = pattern.findall(message)
            if matches:
                entities["confirmacao"] = matches[0].lower()
        
        return entities
    
    async def _generate_contextual_response(
        self, 
        message: str, 
        intent: str, 
        entities: Dict[str, Any], 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Gera resposta contextual da Claudia - empática e profissional"""
        
        response_data = {
            "response": "",
            "actions": [],
            "context_updates": {}
        }
        
        # Seleciona template base da Claudia
        templates = self.responses.get(intent, self.responses["default"])
        base_response = np.random.choice(templates)
        
        # Personalização especial da Claudia baseada no intent
        if intent == "saudacao":
            # Se é primeira interação, se apresenta
            if not context.last_template_sent:
                response_data["response"] = base_response
            else:
                # Se já conversaram antes, é mais informal
                claudia_followup = [
                    "Oi de novo! Claudia aqui! Como posso te ajudar agora? 😊",
                    "E aí! Claudia da Desk novamente! Em que posso ser útil?",
                    "Olá! A Claudia voltou! Vamos resolver mais alguma coisa?"
                ]
                response_data["response"] = np.random.choice(claudia_followup)
            
        elif intent == "confirmacao_pagamento":
            # Claudia fica empolgada com confirmação
            if "pix" in message.lower():
                response_data["response"] = "Que ótimo! 🎉 PIX é rapidinho! Vou verificar aqui no sistema. Já apareceu na conta da Desk!"
            elif "boleto" in message.lower():
                response_data["response"] = "Perfeito! Boleto confirmado! 📋 Já anotei aqui. Você é super organizado!"
            else:
                response_data["response"] = base_response
            
            response_data["actions"].append("verificar_pagamento")
            response_data["context_updates"]["payment_status"] = "verification_pending"
            
        elif intent == "negociacao":
            # Claudia é super empática com dificuldades
            empathy_phrases = [
                "Imagino como deve estar complicado pra você! 😔",
                "Entendo perfeitamente sua situação! 💙",
                "Nossa, que fase difícil mesmo! ",
                "Fico imaginando como deve estar pesado! "
            ]
            
            empathy = np.random.choice(empathy_phrases)
            
            if context.client_amount:
                amount_str = f"R$ {context.client_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                response_data["response"] = f"{empathy}{base_response}\n\n💡 Para os {amount_str}, olha as opções que tenho:\n\n🔹 Parcelamento em até 6x sem juros\n🔹 15% de desconto à vista\n🔹 Prazo extra de 45 dias\n\nQual funciona melhor pra você?"
            else:
                response_data["response"] = f"{empathy}{base_response}"
            
            response_data["actions"].append("oferecer_negociacao")
            response_data["context_updates"]["payment_status"] = "negotiating"
            
        elif intent == "informacoes":
            if context.client_amount:
                amount_str = f"R$ {context.client_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                response_data["response"] = f"{base_response}\n\n💰 Seu valor em aberto: {amount_str}\n\n📱 Formas de pagamento:\n• PIX: desk.cobranca@pix.com\n• Transferência: Banco 001 Ag. 1234 CC. 56789-0\n• Boleto: Posso gerar um novo se precisar!\n\nQual você prefere? A Claudia te ajuda! 😊"
            else:
                response_data["response"] = base_response + "\n\n📱 PIX: desk.cobranca@pix.com\n🏦 Dados bancários disponíveis\n📄 Boleto sempre disponível!"
            
            response_data["actions"].append("enviar_informacoes_pagamento")
            
        elif intent == "contestacao":
            # Claudia fica preocupada mas quer resolver
            concern_responses = [
                "Nossa, que situação! 😮 Vou investigar isso urgente pra você!",
                "Eita! Que estranho mesmo! Deixa eu ver o que rolou...",
                "Nossa! Isso não pode estar certo! Vou apurar tudo agora!"
            ]
            concern = np.random.choice(concern_responses)
            
            response_data["response"] = f"{concern}\n\nVou transferir você para meu supervisor resolver isso pessoalmente. Ninguém vai te cobrar algo que não deve!"
            response_data["actions"].append("escalate_to_human")
            response_data["context_updates"]["payment_status"] = "disputed"
            
        elif intent == "agendamento":
            response_data["response"] = base_response
            if "data" in entities:
                response_data["response"] += f"\n\nEntão fica marcado para {entities['data']}! Vou anotar aqui na agenda da Desk! 📅"
            else:
                response_data["response"] += "\n\nMe fala que dia fica bom pra você que eu anoto tudo certinho!"
            response_data["actions"].append("agendar_pagamento")
            
        elif intent == "ansiedade_cobranca":
            # Claudia acalma a pessoa
            calming_responses = [
                "Ei, fica tranquilo! 😌 Ninguém vai te prejudicar. A Desk só quer resolver numa boa!",
                "Relaxa! Aqui não tem pegadinha. Vamos achar uma solução boa pra você! 💙",
                "Calma! Não precisa ficar preocupado. A gente sempre dá um jeito! 🤗"
            ]
            response_data["response"] = np.random.choice(calming_responses)
            
        elif intent == "situacao_financeira":
            # Claudia é muito empática
            empathy_responses = [
                "Nossa, que fase complicada! 😔 Fica tranquilo que vamos encontrar uma saída juntos!",
                "Imagino como deve estar difícil pra você! A Desk entende e vai te ajudar! 💙",
                "Que situação pesada! Mas relaxa, vamos resolver isso de um jeito que funcione pra você! 🤝"
            ]
            response_data["response"] = np.random.choice(empathy_responses)
            response_data["actions"].append("oferecer_negociacao_especial")
            
        else:
            # Para outros intents, usa resposta padrão
            response_data["response"] = base_response
        
        # Personalização com nome do cliente
        if context.client_name:
            name = context.client_name.split()[0]  # Só primeiro nome
            # Substitui "você" por nome quando apropriado
            if intent in ["saudacao", "informacoes", "negociacao"]:
                response_data["response"] = response_data["response"].replace(
                    "te ajudar", f"te ajudar, {name}"
                ).replace(
                    "pra você", f"pra você, {name}"
                )
        
        return response_data
    
    async def _generate_supreme_response(
        self,
        original_message: str,
        clean_message: str,
        intent: str,
        entities: Dict[str, Any],
        emotional_state: EmotionalState,
        memory_context: Dict[str, Any],
        context: ConversationContext
    ) -> Dict[str, Any]:
        """🚀 GERAÇÃO ULTRA-SUPREMA - NÍVEL GPT-4++ 🤖✨"""
        
        response_data = {
            "response": "",
            "actions": [],
            "context_updates": {}
        }
        
        # 🧠 ANÁLISE CONTEXTUAL ULTRA-PROFUNDA
        conversation_depth = memory_context.get("conversation_count", 0)
        user_patterns = memory_context.get("behavioral_patterns", {})
        previous_intents = memory_context.get("intent_history", [])
        
        # 🎯 INTELIGÊNCIA CONVERSACIONAL GPT-4
        ultra_context = {
            "conversation_flow": self._analyze_conversation_flow(previous_intents, intent),
            "user_personality": self._detect_user_personality(user_patterns),
            "situational_context": self._analyze_situational_context(entities, emotional_state),
            "temporal_context": self._analyze_temporal_context(memory_context),
            "relationship_depth": conversation_depth
        }
        
        # 🎭 EMOÇÃO ULTRA-NATURAL COM NUANCE HUMANA
        emotion = emotional_state.primary_emotion
        emotion_intensity = emotional_state.intensity
        
        # 🌟 GERAÇÃO DINÂMICA DE PERSONALIDADE
        claudia_personality = self._generate_claudia_personality(ultra_context, emotion)
        
        # 🎯 RESPOSTAS ULTRA-CONTEXTUAIS
        if conversation_depth == 0:
            # Primeira interação - acolhedora e profissional
            base_response = self._generate_first_interaction_response(intent, emotion, ultra_context)
        elif conversation_depth <= 3:
            # Interações iniciais - construindo confiança
            base_response = self._generate_early_interaction_response(intent, emotion, ultra_context)
        else:
            # Relacionamento estabelecido - ultra personalizado
            base_response = self._generate_established_relationship_response(intent, emotion, ultra_context)
        
        # 🧠 PERSONALIZAÇÃO ULTRA-SUPREMA
        base_response = self._ultra_personalize_response(base_response, ultra_context, context, memory_context)
        
        # 💫 GERAÇÃO CONTEXTUAL ULTRA-SOFISTICADA
        response_data["response"] = await self._generate_ultra_contextual_response(
            base_response, intent, entities, emotional_state, ultra_context, context
        )
        
        # 🎯 AÇÕES ULTRA-INTELIGENTES
        response_data["actions"] = self._generate_ultra_smart_actions(
            intent, emotional_state, ultra_context, entities, context
        )
        
        # 📊 ATUALIZAÇÕES DE CONTEXTO ULTRA-AVANÇADAS
        response_data["context_updates"] = self._generate_ultra_context_updates(
            intent, emotional_state, entities, ultra_context, context
        )
        
        # 🎨 ENRIQUECIMENTO FINAL ULTRA-NATURAL
        response_data["response"] = self._apply_ultra_natural_language(
            response_data["response"], ultra_context, emotional_state
        )
        
        return response_data
    
    def _analyze_conversation_flow(self, previous_intents: List[str], current_intent: str) -> Dict[str, Any]:
        """Analisa o fluxo da conversa para contexto ultra-natural"""
        flow_analysis = {
            "is_follow_up": len(previous_intents) > 0,
            "topic_changes": self._count_topic_changes(previous_intents, current_intent),
            "escalation_level": self._calculate_escalation_level(previous_intents),
            "resolution_progress": self._calculate_resolution_progress(previous_intents),
            "user_engagement": self._calculate_user_engagement(previous_intents)
        }
        return flow_analysis
    
    def _detect_user_personality(self, patterns: Dict[str, Any]) -> str:
        """Detecta personalidade do usuário para respostas personalizadas"""
        if not patterns:
            return "unknown"
        
        traits = []
        if patterns.get("formality_score", 0) > 0.7:
            traits.append("formal")
        elif patterns.get("formality_score", 0) < 0.3:
            traits.append("casual")
        
        if patterns.get("emotional_responsiveness", 0) > 0.6:
            traits.append("emotional")
        else:
            traits.append("rational")
        
        if patterns.get("urgency_indicators", 0) > 0.5:
            traits.append("urgent")
        
        return "_".join(traits) if traits else "balanced"
    
    def _generate_claudia_personality(self, context: Dict[str, Any], emotion: str) -> Dict[str, str]:
        """Gera variações da personalidade da Claudia baseadas no contexto"""
        personalities = {
            "first_interaction": {
                "tone": "acolhedora_profissional",
                "language": "formal_educado",
                "empathy": "alta",
                "proactivity": "moderada"
            },
            "casual_user": {
                "tone": "amigavel_descontraida",
                "language": "coloquial_respeitosa",
                "empathy": "muito_alta",
                "proactivity": "alta"
            },
            "formal_user": {
                "tone": "profissional_respeitosa",
                "language": "formal_precisa",
                "empathy": "profissional",
                "proactivity": "moderada"
            },
            "emotional_user": {
                "tone": "empatica_acolhedora",
                "language": "calorosa_apoiante",
                "empathy": "extrema",
                "proactivity": "muito_alta"
            },
            "urgent_user": {
                "tone": "eficiente_direta",
                "language": "clara_objetiva",
                "empathy": "prática",
                "proactivity": "máxima"
            }
        }
        
        user_type = context.get("user_personality", "balanced")
        return personalities.get(user_type, personalities["first_interaction"])
    
    def _generate_first_interaction_response(self, intent: str, emotion: str, context: Dict[str, Any]) -> str:
        """Gera resposta para primeira interação ultra-acolhedora"""
        responses = {
            "saudacao": "Oi! Que prazer te conhecer! 😊 Sou a Claudia, especialista em cobranças da Desk, e estou aqui pra te ajudar com MUITO carinho e paciência!",
            "informacoes": "Olá! Seja muito bem-vindo(a)! 💙 Vejo que está buscando informações - vou te explicar tudo com calma e clareza, tá bom?",
            "negociacao": "Oi! Que bom que você chegou até aqui! 💪 Sei que situações financeiras podem ser desafiadoras, e estou aqui pra encontrar a melhor solução juntos!",
            "contestacao": "Olá! Entendo perfeitamente sua preocupação! 😟 Vamos resolver isso com total transparência e cuidado - sua paz de espírito é minha prioridade!",
            "confirmacao_pagamento": "Oi! Muito obrigada pelo seu pagamento! 🙏 Sua responsabilidade é admirável - vou verificar tudo pra você agora mesmo!",
            "agendamento": "Olá! Que ótimo que está pensando em organizar seu pagamento! 📅 Vamos achar a data perfeita que funcione pra você!"
        }
        return responses.get(intent, "Oi! Muito prazer! 😊 Como posso te ajudar hoje?")
    
    def _generate_early_interaction_response(self, intent: str, emotion: str, context: Dict[str, Any]) -> str:
        """Gera resposta para interações iniciais construindo confiança"""
        responses = {
            "saudacao": "Oi de novo! Que bom te ver por aqui! 😊",
            "informacoes": "Deixa eu te ajudar com essas informações! 💡",
            "negociacao": "Vamos encontrar uma solução que funcione pra você! 🤝",
            "contestacao": "Vamos resolver isso juntos, sem estresse! 💙",
            "confirmacao_pagamento": "Perfeito! Vou confirmar seu pagamento! ✅",
            "agendamento": "Vamos marcar isso direitinho! 📅"
        }
        return responses.get(intent, "Oi! Como posso te ajudar agora?")
    
    def _generate_established_relationship_response(self, intent: str, emotion: str, context: Dict[str, Any]) -> str:
        """Gera resposta ultra-personalizada para relacionamento estabelecido"""
        # Ultra-personalização baseada no histórico
        flow = context.get("conversation_flow", {})
        if flow.get("is_follow_up"):
            return "Continuando nossa conversa... 🔄"
        
        responses = {
            "saudacao": "E aí! Como você está? Sempre um prazer! 😊",
            "informacoes": "Já sei exatamente o que você precisa! 💡",
            "negociacao": "Vou preparar as melhores opções pra você! 🎯",
            "contestacao": "Vou resolver isso imediatamente! 🚀",
            "confirmacao_pagamento": "Confirmado! Você é 10! ⭐",
            "agendamento": "Marcado! Vou lembrar pra você! 📋"
        }
        return responses.get(intent, "Oi! Sempre um prazer te ajudar!")
    
    def _ultra_personalize_response(self, response: str, context: Dict[str, Any], conversation_context: ConversationContext, memory: Dict[str, Any]) -> str:
        """Personalização ultra-avançada baseada em múltiplos fatores"""
        # Nome personalizado
        if conversation_context.client_name:
            name = conversation_context.client_name.split()[0]
            # Evita repetição excessiva
            if name.lower() not in response.lower():
                response = response.replace("você", f"você, {name}")
        
        # Referências contextuais ultra-naturais
        flow = context.get("conversation_flow", {})
        if flow.get("escalation_level", 0) > 2:
            response = "Entendo que está ficando frustrado... " + response
        
        # Adaptação temporal
        current_time = datetime.now()
        if current_time.hour < 12:
            response = "Bom dia! " + response
        elif current_time.hour < 18:
            response = "Boa tarde! " + response
        else:
            response = "Boa noite! " + response
        
        return response
    
    async def _generate_ultra_contextual_response(
        self,
        base_response: str,
        intent: str,
        entities: Dict[str, Any],
        emotional_state: EmotionalState,
        ultra_context: Dict[str, Any],
        context: ConversationContext
    ) -> str:
        """Gera resposta ultra-contextual com profundidade GPT-4"""
        response = base_response
        
        # 💰 Contexto financeiro ultra-sofisticado
        if intent in ["informacoes", "negociacao"] and context.client_amount:
            amount_str = f"R$ {context.client_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            # Análise de contexto temporal
            days_overdue = 0
            if context.due_date:
                days_overdue = (datetime.now() - context.due_date).days
            
            if intent == "informacoes":
                if days_overdue > 30:
                    response += f"\n\n💳 Seu débito de {amount_str} está com {days_overdue} dias de atraso."
                    response += "\n📊 Vou te mostrar exatamente como está composto:"
                    response += f"\n   • Valor original: {amount_str}"
                    if context.late_fee:
                        response += f"\n   • Juros/mora: R$ {context.late_fee:.2f}"
                    response += "\n\n💡 Posso te ajudar a regularizar isso de forma tranquila!"
                else:
                    response += f"\n\n💰 Seu valor atual é {amount_str}"
                    response += "\n\n🎯 Opções de pagamento disponíveis:"
                    response += "\n   • PIX instantâneo: desk.cobranca@pix.com"
                    response += "\n   • Transferência: Banco 001, Ag. 1234, CC. 56789-0"
                    response += "\n   • Boleto: Posso gerar um novo agora mesmo!"
                    
            elif intent == "negociacao":
                # Ofertas ultra-personalizadas
                if emotional_state.primary_emotion in ["tristeza", "medo"] and emotional_state.intensity > 0.6:
                    response += f"\n\n💙 {name}, vendo sua situação, preparei algo especial:"
                    response += f"\n   • Parcelamento em até 12x de R$ {context.client_amount/12:.2f}"
                    response += "\n   • 25% de desconto para pagamento à vista"
                    response += "\n   • 90 dias para primeira parcela"
                    response += "\n   • Sem consulta ao SPC/Serasa"
                else:
                    response += f"\n\n💡 Para os {amount_str}, tenho ótimas opções:"
                    response += f"\n   • Parcelamento em até 8x de R$ {context.client_amount/8:.2f}"
                    response += "\n   • 20% de desconto para pagamento à vista"
                    response += "\n   • 60 dias para primeira parcela"
        
        # 🎭 Adaptação emocional ultra-nuanced
        if emotional_state.intensity > 0.5:
            if emotional_state.primary_emotion == "raiva":
                response += "\n\n💪 Entendo perfeitamente sua frustração! Vou resolver isso AGORA SEM ENROLAÇÃO!"
                response += "\n🎯 Qual é sua prioridade? Vou focar 100% nisso!"
            elif emotional_state.primary_emotion == "tristeza":
                response += "\n\n💙 Sinto muito que esteja passando por isso..."
                response += "\n🤗 Você não está sozinho(a)! Estou aqui pra te apoiar em cada passo!"
                response += "\n✨ Vamos resolver isso juntos, sem pressão e com carinho!"
            elif emotional_state.primary_emotion == "medo":
                response += "\n\n🛡️ Fica tranquilo(a)! Aqui é um ambiente 100% seguro!"
                response += "\n🤝 Nada de ameaças ou pressão - só soluções reais e viáveis!"
                response += "\n💚 Sua paz de espírito é minha prioridade absoluta!"
        
        # 📚 Referências ultra-contextuais à memória
        recent_facts = memory_context.get("relevant_facts", {})
        if recent_facts:
            situation = recent_facts.get("financial_situation")
            if situation == "desempregado":
                response += "\n\n🤝 Sei que estar desempregado é extremamente desafiador..."
                response += "\n💪 Mas sua força em buscar soluções já é um grande primeiro passo!"
                response += "\n🎯 Vamos criar um plano que respeite sua realidade atual!"
            elif situation == "doente":
                response += "\n\n💙 Problemas de saúde são prioridade absoluta..."
                response += "\n🏥 Sua saúde vem primeiro - vamos resolver as pendências sem estresse!"
                response += "\n🕐 Sem pressa, sem pressão. Vamos no seu ritmo!"
        
        return response
    
    def _generate_ultra_smart_actions(self, intent: str, emotional_state: EmotionalState, context: Dict[str, Any], entities: Dict[str, Any], conversation_context: ConversationContext) -> List[str]:
        """Gera ações ultra-inteligentes com previsão de necessidades"""
        actions = []
        
        # Previsão de necessidades baseada em padrões
        flow = context.get("conversation_flow", {})
        
        # Ações ultra-específicas
        if intent == "confirmacao_pagamento":
            actions.extend([
                "verificar_pagamento_com_baixa_prioridade",
                "enviar_confirmacao_por_email",
                "atualizar_status_cliente_com_data",
                "preparar_recibo_digital"
            ])
        elif intent == "negociacao":
            actions.extend([
                "calcular_parcelas_personalizadas",
                "preparar_proposta_visual",
                "verificar_historico_pagamentos",
                "oferecer_desconto_contextual"
            ])
            
            if emotional_state.intensity > 0.7:
                actions.append("ativar_protocolo_empatico")
                actions.append("oferecer_acompanhamento_humano")
        
        # Ações preditivas
        if flow.get("escalation_level", 0) > 3:
            actions.append("preparar_intervencao_especialista")
        
        return actions
    
    def _generate_ultra_context_updates(self, intent: str, emotional_state: EmotionalState, entities: Dict[str, Any], context: Dict[str, Any], conversation_context: ConversationContext) -> Dict[str, Any]:
        """Gera atualizações de contexto ultra-sofisticadas"""
        updates = {}
        
        # Análise preditiva de comportamento
        flow = context.get("conversation_flow", {})
        
        # Atualizações ultra-específicas
        if intent == "negociacao":
            updates.update({
                "payment_status": "ultra_negotiating",
                "negotiation_stage": self._calculate_negotiation_stage(flow),
                "predicted_outcome": self._predict_negotiation_outcome(emotional_state, entities),
                "next_best_action": self._calculate_next_best_action(intent, emotional_state)
            })
        
        # Rastreamento emocional avançado
        updates.update({
            "emotional_trajectory": self._calculate_emotional_trajectory(emotional_state, context),
            "trust_level": self._calculate_trust_level(context),
            "satisfaction_prediction": self._predict_satisfaction(intent, emotional_state)
        })
        
        return updates
    
    def _apply_ultra_natural_language(self, response: str, context: Dict[str, Any], emotional_state: EmotionalState) -> str:
        """Aplica linguagem ultra-natural com variações humanas"""
        
        # Variações naturais de linguagem
        natural_variations = {
            "oi": ["Oi", "Olá", "E aí", "Oi, tudo bem?", "Oi! Como vai?"],
            "tchau": ["Tchau", "Até logo", "Falou", "Até mais", "Beijo!"],
            "obrigado": ["Obrigado", "Valeu", "Agradeço muito", "Muito obrigado", "De coração!"]
        }
        
        # Adiciona emojis contextuais
        if emotional_state.primary_emotion == "alegria":
            response += " 😊✨"
        elif emotional_state.primary_emotion == "tristeza":
            response += " 💙"
        elif emotional_state.primary_emotion == "raiva":
            response += " 💪"
        
        # Variações de pontuação natural
        response = response.replace("!", np.random.choice(["!", "! 😊", "! 🎯"]))
        
        return response
    
    def _personalize_with_memory(self, response: str, memory_context: Dict[str, Any], context: ConversationContext) -> str:
        """Personaliza resposta com base na memória"""
        
        # Adiciona nome se disponível
        if context.client_name:
            name = context.client_name.split()[0]
            response = response.replace("você", f"você, {name}").replace("te ajudar", f"te ajudar, {name}")
        
        # Referência a conversas anteriores
        conversation_count = memory_context.get("conversation_count", 0)
        if conversation_count > 1:
            if "sou a claudia" in response.lower():
                response = response.replace(
                    "Sou a Claudia da Desk", 
                    "É a Claudia da Desk de novo"
                )
        
        # Adapta baseado no padrão emocional
        emotional_pattern = memory_context.get("emotional_pattern", {})
        if emotional_pattern.get("trend") == "declining":
            response = "Oi! Percebi que você tem passado por uns momentos difíceis... " + response
        elif emotional_pattern.get("trend") == "improving":
            response = "Oi! Que bom ver você mais animado! " + response
        
        return response
    
    def _count_topic_changes(self, previous_intents: List[str], current_intent: str) -> int:
        """Conta mudanças de tópico na conversa"""
        if not previous_intents:
            return 0
        
        topic_groups = {
            "financial": ["informacoes", "negociacao", "confirmacao_pagamento"],
            "emotional": ["contestacao", "negociacao"],
            "administrative": ["agendamento", "saudacao", "despedida"]
        }
        
        changes = 0
        current_group = None
        for group, intents in topic_groups.items():
            if current_intent in intents:
                current_group = group
                break
        
        for prev_intent in previous_intents[-3:]:
            prev_group = None
            for group, intents in topic_groups.items():
                if prev_intent in intents:
                    prev_group = group
                    break
            if prev_group != current_group:
                changes += 1
        
        return changes
    
    def _calculate_escalation_level(self, previous_intents: List[str]) -> int:
        """Calcula nível de escalada emocional"""
        if not previous_intents:
            return 0
        
        escalation_indicators = ["contestacao", "negociacao"]
        level = 0
        
        for intent in previous_intents[-5:]:
            if intent in escalation_indicators:
                level += 1
        
        return min(level, 5)
    
    def _calculate_resolution_progress(self, previous_intents: List[str]) -> float:
        """Calcula progresso de resolução"""
        if not previous_intents:
            return 0.0
        
        resolution_indicators = ["confirmacao_pagamento", "agendamento"]
        progress = sum(1 for intent in previous_intents[-10:] if intent in resolution_indicators)
        
        return min(progress * 0.2, 1.0)
    
    def _calculate_user_engagement(self, previous_intents: List[str]) -> float:
        """Calcula engajamento do usuário"""
        if not previous_intents:
            return 0.5
        
        return min(len(previous_intents) * 0.1, 1.0)
    
    def _analyze_situational_context(self, entities: Dict[str, Any], emotional_state: EmotionalState) -> Dict[str, Any]:
        """Analisa contexto situacional"""
        return {
            "urgency_level": emotional_state.intensity,
            "financial_complexity": len(entities),
            "emotional_context": emotional_state.primary_emotion
        }
    
    def _analyze_temporal_context(self, memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa contexto temporal"""
        return {
            "time_of_day": datetime.now().hour,
            "day_of_week": datetime.now().weekday(),
            "conversation_duration": memory_context.get("conversation_count", 0)
        }
    
    def _calculate_negotiation_stage(self, flow: Dict[str, Any]) -> str:
        """Calcula estágio da negociação"""
        escalation = flow.get("escalation_level", 0)
        if escalation == 0:
            return "inicial"
        elif escalation <= 2:
            return "desenvolvimento"
        elif escalation <= 4:
            return "avancado"
        else:
            return "critico"
    
    def _predict_negotiation_outcome(self, emotional_state: EmotionalState, entities: Dict[str, Any]) -> str:
        """Preve resultado da negociação"""
        if emotional_state.intensity > 0.8:
            return "necessita_intervencao"
        elif emotional_state.intensity > 0.5:
            return "provavel_acordo"
        else:
            return "alta_probabilidade"
    
    def _calculate_next_best_action(self, intent: str, emotional_state: EmotionalState) -> str:
        """Calcula próxima melhor ação"""
        if emotional_state.intensity > 0.7:
            return "empatia_intensificada"
        elif intent == "negociacao":
            return "oferta_personalizada"
        else:
            return "continuar_conversa"
    
    def _calculate_emotional_trajectory(self, emotional_state: EmotionalState, context: Dict[str, Any]) -> str:
        """Calcula trajetória emocional"""
        return f"{emotional_state.primary_emotion}_{emotional_state.intensity:.2f}"
    
    def _calculate_trust_level(self, context: Dict[str, Any]) -> float:
        """Calcula nível de confiança"""
        flow = context.get("conversation_flow", {})
        engagement = flow.get("user_engagement", 0)
        return min(engagement * 0.8 + 0.2, 1.0)
    
    def _predict_satisfaction(self, intent: str, emotional_state: EmotionalState) -> float:
        """Preve satisfação do usuário"""
        base = 0.7
        if emotional_state.intensity < 0.3:
            base += 0.2
        elif emotional_state.intensity > 0.7:
            base -= 0.3
        
        return max(0, min(base, 1.0))
    
    async def _generate_contextual_supreme(
        self,
        base_response: str,
        intent: str,
        entities: Dict[str, Any],
        emotional_state: EmotionalState,
        memory_context: Dict[str, Any],
        context: ConversationContext
    ) -> str:
        """Gera resposta contextual suprema"""
        
        response = base_response
        
        # 💰 INFORMAÇÕES FINANCEIRAS INTELIGENTES
        if intent in ["informacoes", "negociacao"] and context.client_amount:
            amount_str = f"R$ {context.client_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            if intent == "informacoes":
                response += f"\n\n💰 Seu valor em aberto: {amount_str}"
                response += "\n\n📱 Formas de pagamento:"
                response += "\n• PIX: desk.cobranca@pix.com"
                response += "\n• Transferência: Banco 001 Ag. 1234 CC. 56789-0"
                response += "\n• Boleto: Posso gerar um novo se precisar!"
                
            elif intent == "negociacao":
                # Ofertas inteligentes baseadas na emoção
                if emotional_state.primary_emotion in ["tristeza", "medo"]:
                    response += f"\n\n💙 Para os {amount_str}, tenho condições especiais:"
                    response += "\n🔹 Parcelamento em até 10x sem juros"
                    response += "\n🔹 20% de desconto à vista"
                    response += "\n🔹 Prazo extra de 60 dias"
                else:
                    response += f"\n\n💡 Para os {amount_str}, olha as opções:"
                    response += "\n🔹 Parcelamento em até 6x sem juros"
                    response += "\n🔹 15% de desconto à vista"
                    response += "\n🔹 Prazo extra de 45 dias"
        
        # 🎭 ADAPTAÇÃO EMOCIONAL DINÂMICA
        if emotional_state.intensity > 0.7:
            if emotional_state.primary_emotion == "raiva":
                response += "\n\n💪 Vou resolver isso AGORA! Sem enrolação!"
            elif emotional_state.primary_emotion == "tristeza":
                response += "\n\n💙 Você não está sozinho nisso. Estou aqui pra te apoiar!"
            elif emotional_state.primary_emotion == "medo":
                response += "\n\n🛡️ Fica tranquilo! Aqui é ambiente seguro e vamos com calma!"
        
        # 📚 REFERÊNCIAS À MEMÓRIA
        recent_facts = memory_context.get("relevant_facts", {})
        if "financial_situation" in recent_facts:
            situation = recent_facts["financial_situation"]
            if situation == "desempregado":
                response += "\n\n🤝 Sei que estar desempregado é difícil. Vamos achar uma solução que funcione!"
            elif situation == "doente":
                response += "\n\n💙 Problemas de saúde são complicados mesmo. Vamos resolver isso sem pressão!"
        
        return response
    
    def _generate_smart_actions(self, intent: str, emotional_state: EmotionalState, memory_context: Dict[str, Any], entities: Dict[str, Any]) -> List[str]:
        """Gera ações inteligentes baseadas no contexto"""
        actions = []
        
        # Ações baseadas no intent
        if intent == "confirmacao_pagamento":
            actions.append("verificar_pagamento")
            actions.append("atualizar_status_cliente")
        elif intent == "negociacao":
            actions.append("oferecer_parcelamento")
            if emotional_state.intensity > 0.6:
                actions.append("oferecer_desconto_especial")
        elif intent == "contestacao":
            actions.append("escalate_to_human")
            actions.append("registrar_disputa")
        elif intent == "informacoes":
            actions.append("enviar_dados_pagamento")
        
        # Ações baseadas na emoção
        if emotional_state.primary_emotion == "raiva" and emotional_state.intensity > 0.7:
            actions.append("priority_handling")
        elif emotional_state.primary_emotion == "tristeza":
            actions.append("empathetic_followup")
        elif emotional_state.primary_emotion == "medo":
            actions.append("reassurance_protocol")
        
        # Ações baseadas na memória
        conversation_count = memory_context.get("conversation_count", 0)
        if conversation_count > 3:
            actions.append("check_satisfaction")
        
        return actions
    
    def _generate_context_updates(self, intent: str, emotional_state: EmotionalState, entities: Dict[str, Any], memory_context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera atualizações de contexto avançadas"""
        updates = {}
        
        # Atualizações baseadas no intent
        if intent == "confirmacao_pagamento":
            updates["payment_status"] = "verification_pending"
            updates["last_interaction_type"] = "payment_confirmation"
        elif intent == "negociacao":
            updates["payment_status"] = "negotiating"
            updates["negotiation_attempts"] = memory_context.get("negotiation_attempts", 0) + 1
        elif intent == "contestacao":
            updates["payment_status"] = "disputed"
            updates["escalation_required"] = True
        
        # Atualizações emocionais
        updates["last_emotion"] = emotional_state.primary_emotion
        updates["emotion_intensity"] = emotional_state.intensity
        
        # Preferências detectadas
        if "payment_preference" in entities:
            updates["preferred_payment"] = entities["payment_preference"]
        
        return updates
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre o modelo"""
        return {
            "model_loaded": self.intent_model is not None,
            "device": str(self.device),
            "num_intents": len(self.intent_labels),
            "intents": self.intent_labels,
            "max_length": self.max_length,
            "temperature": self.temperature
        }
    
    def update_model_with_feedback(self, message: str, true_intent: str, predicted_intent: str):
        """Atualiza modelo com feedback do usuário (para aprendizado contínuo)"""
        # Implementação simplificada - em produção seria mais sofisticada
        conversation_logger.info("MODEL_FEEDBACK_RECEIVED", {
            "message_hash": hash(message),
            "true_intent": true_intent,
            "predicted_intent": predicted_intent,
            "correct": true_intent == predicted_intent
        })
        
        # Aqui seria implementado o re-treinamento online
        # Por enquanto apenas registra para análise posterior

# Instância global do bot
chatbot = BillingChatBot()
