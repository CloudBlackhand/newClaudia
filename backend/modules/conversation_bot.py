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
    """Resultado da análise de mensagem"""
    intent: IntentType
    sentiment: SentimentType
    confidence: float
    entities: Dict[str, Any]
    keywords: List[str]

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
    """Processador de linguagem natural"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.sentiment_words = self._load_sentiment_words()
        self.entity_patterns = self._load_entity_patterns()
        
        logger.info(LogCategory.CONVERSATION, "NLP Processor inicializado")
    
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
    
    def analyze_message(self, message: str) -> AnalysisResult:
        """Analisar mensagem do usuário"""
        message_clean = self._clean_text(message)
        
        # Detectar intenção
        intent, intent_confidence = self._detect_intent(message_clean)
        
        # Analisar sentimento
        sentiment = self._analyze_sentiment(message_clean)
        
        # Extrair entidades
        entities = self._extract_entities(message_clean)
        
        # Extrair palavras-chave
        keywords = self._extract_keywords(message_clean)
        
        # Calcular confiança geral
        confidence = intent_confidence
        
        result = AnalysisResult(
            intent=intent,
            sentiment=sentiment,
            confidence=confidence,
            entities=entities,
            keywords=keywords
        )
        
        logger.debug(LogCategory.CONVERSATION, 
                    f"Mensagem analisada: {intent.value}/{sentiment.value}",
                    details={
                        'confidence': confidence,
                        'entities_count': len(entities),
                        'keywords': keywords[:5]  # Primeiras 5 palavras-chave
                    })
        
        return result
    
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
            'unknown': {
                'neutral': [
                    "Desculpe, não entendi completamente sua mensagem. Pode reformular sua pergunta?",
                    "Não consegui compreender exatamente o que precisa. Pode ser mais específico?",
                    "Perdão, mas não ficou claro. Pode explicar melhor sua dúvida?"
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
