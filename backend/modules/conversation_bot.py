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
    UNKNOWN = "unknown"

class SentimentType(Enum):
    """Tipos de sentimento da mensagem"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"

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
    
    def __post_init__(self):
        if self.topics_discussed is None:
            self.topics_discussed = set()
        if self.sentiment_history is None:
            self.sentiment_history = []
        if self.intent_history is None:
            self.intent_history = []

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
            ],
            IntentType.PAYMENT_CONFIRMATION: [
                r'\b(já paguei|paguei|efetuei o pagamento|quitei|pix feito)\b',
                r'\b(comprovante|recibo|transferência realizada)\b',
                r'\b(pagamento efetuado|conta quitada|valor pago)\b',
                r'\b(enviei o pix|mandei o dinheiro|transferi)\b',
            ],
            IntentType.PAYMENT_QUESTION: [
                r'\b(como pagar|onde pagar|forma de pagamento|chave pix)\b',
                r'\b(dados bancários|conta para depósito|qr code)\b',
                r'\b(valor|quanto|qual o valor|valor correto)\b',
                r'\b(vencimento|quando vence|prazo)\b',
            ],
            IntentType.NEGOTIATION: [
                r'\b(negociar|parcelar|dividir|desconto|abatimento)\b',
                r'\b(condições|facilitar|reduzir|diminuir)\b',
                r'\b(não consigo pagar|difícil situação|sem condições)\b',
                r'\b(proposta|acordo|acerto|combinar)\b',
            ],
            IntentType.COMPLAINT: [
                r'\b(reclamação|problema|erro|não concordo|injusto)\b',
                r'\b(absurdo|revoltante|inadmissível|inaceitável)\b',
                r'\b(não devo|não é meu|cobrança indevida)\b',
                r'\b(advogado|procon|justiça|processo)\b',
            ],
            IntentType.INFORMATION_REQUEST: [
                r'\b(informação|detalhe|esclarecimento|dúvida)\b',
                r'\b(referente a|sobre|relativo|concernente)\b',
                r'\b(o que é|do que se trata|qual o motivo)\b',
                r'\b(histórico|extrato|demonstrativo)\b',
            ],
            IntentType.GOODBYE: [
                r'\b(tchau|até|obrigad|valeu|flw|falou)\b',
                r'\b(até logo|até mais|nos falamos)\b',
                r'^(ok|certo|entendi|beleza)$',
            ]
        }
    
    def _load_sentiment_words(self) -> Dict[SentimentType, List[str]]:
        """Carregar palavras de sentimento"""
        return {
            SentimentType.POSITIVE: [
                'obrigado', 'grato', 'excelente', 'ótimo', 'bom', 'legal', 'show',
                'perfeito', 'maravilhoso', 'agradável', 'satisfeito', 'feliz',
                'positivo', 'correto', 'certo', 'bem', 'melhor', 'sucesso'
            ],
            SentimentType.NEGATIVE: [
                'ruim', 'péssimo', 'horrível', 'terrível', 'difícil', 'complicado',
                'problema', 'erro', 'falha', 'insatisfeito', 'chateado', 'triste',
                'preocupado', 'nervoso', 'estressado', 'desempregado'
            ],
            SentimentType.ANGRY: [
                'raiva', 'irritado', 'furioso', 'revoltado', 'indignado', 'bravo',
                'absurdo', 'inadmissível', 'inaceitável', 'ridículo', 'vergonha',
                'escândalo', 'safado', 'ladrão', 'roubo', 'enganação', 'palhaçada',
                'filho da puta', 'desgraçado', 'merda', 'porra'
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, str]:
        """Carregar padrões de entidades"""
        return {
            'money': r'(?:R\$\s*)?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            'date': r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            'phone': r'(\d{2}\s*\d{4,5}\-?\d{4})',
            'pix_key': r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|\d{11}|\d{14})',
            'time': r'(\d{1,2}:\d{2})',
            'percentage': r'(\d+(?:,\d+)?%)'
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
        """Analisar sentimento da mensagem"""
        words = message.split()
        sentiment_scores = {
            SentimentType.POSITIVE: 0,
            SentimentType.NEGATIVE: 0,
            SentimentType.ANGRY: 0
        }
        
        # Contar palavras de cada sentimento
        for word in words:
            for sentiment, word_list in self.sentiment_words.items():
                if any(sentiment_word in word for sentiment_word in word_list):
                    sentiment_scores[sentiment] += 1
        
        # Peso extra para palavras de raiva
        sentiment_scores[SentimentType.ANGRY] *= 2
        
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
        """Atualizar contexto da conversa"""
        context.last_activity = datetime.now().isoformat()
        context.message_count += 1
        
        # Adicionar ao histórico
        context.intent_history.append(analysis.intent)
        context.sentiment_history.append(analysis.sentiment)
        
        # Limitar histórico
        if len(context.intent_history) > 20:
            context.intent_history = context.intent_history[-20:]
        if len(context.sentiment_history) > 20:
            context.sentiment_history = context.sentiment_history[-20:]
        
        # Extrair e armazenar informações relevantes
        if 'money' in analysis.entities:
            amounts = analysis.entities['money']
            if amounts:
                try:
                    # Converter primeiro valor encontrado
                    amount_str = amounts[0].replace('.', '').replace(',', '.')
                    context.payment_amount = float(amount_str)
                except ValueError:
                    pass
        
        if 'date' in analysis.entities:
            dates = analysis.entities['date']
            if dates:
                context.due_date = dates[0]
        
        # Adicionar tópicos discutidos
        context.topics_discussed.add(analysis.intent.value)
    
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
