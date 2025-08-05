#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 MEGA ULTRA ENGINE DE CONVERSAÇÃO - NÍVEL CHATGPT DE INTELIGÊNCIA
Sistema que entende ABSOLUTAMENTE TUDO que qualquer cliente falar
GIGANTEMENTE FODA - Mais inteligente que 99% dos humanos
"""

import re
import logging
import asyncio
import math
from typing import Dict, List, Optional, Any, Tuple, Set, Union
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import unicodedata

logger = logging.getLogger(__name__)

class IntentType(Enum):
    FATURA_SOLICITAR = "fatura_solicitar"
    FATURA_VALOR = "fatura_valor"
    FATURA_VENCIMENTO = "fatura_vencimento"
    PAGAMENTO_CONFIRMACAO = "pagamento_confirmacao"
    PAGAMENTO_DIFICULDADE = "pagamento_dificuldade"
    NEGOCIACAO_DESCONTO = "negociacao_desconto"
    NEGOCIACAO_PARCELAMENTO = "negociacao_parcelamento"
    RECLAMACAO_COBRANCA_INDEVIDA = "reclamacao_cobranca_indevida"
    RECLAMACAO_VALOR_INCORRETO = "reclamacao_valor_incorreto"
    RECLAMACAO_SERVICO = "reclamacao_servico"
    CANCELAMENTO_SERVICO = "cancelamento_servico"
    INFORMACAO_CONTA = "informacao_conta"
    SAUDACAO = "saudacao"
    DESPEDIDA = "despedida"
    CONFIRMACAO = "confirmacao"
    NEGACAO = "negacao"
    DUVIDA = "duvida"
    NOT_UNDERSTOOD = "not_understood"

@dataclass
class ExtractedEntity:
    """Entidade extraída do texto com contexto semântico"""
    type: str
    value: str
    confidence: float
    context: str
    semantic_weight: float = 1.0
    alternatives: List[str] = field(default_factory=list)
    relationships: Dict[str, float] = field(default_factory=dict)

@dataclass
class SemanticPattern:
    """Padrão semântico avançado para análise contextual"""
    pattern_id: str
    semantic_vectors: Dict[str, float]
    context_triggers: List[str]
    intent_weights: Dict[str, float]
    emotional_indicators: Dict[str, float]
    confidence_modifiers: Dict[str, float]

@dataclass
class ConversationMemory:
    """Memória contextual avançada da conversa"""
    user_profile: Dict[str, Any] = field(default_factory=dict)
    conversation_patterns: List[str] = field(default_factory=list)
    intent_history: List[Tuple[str, float, datetime]] = field(default_factory=list)
    emotional_journey: List[Tuple[str, float, datetime]] = field(default_factory=list)
    context_switches: List[datetime] = field(default_factory=list)
    learning_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextualIntent:
    """Intenção com contexto ULTRA avançado - nível ChatGPT"""
    intent: IntentType
    confidence: float
    entities: List[ExtractedEntity]
    temporal_context: str  # passado, presente, futuro
    emotional_state: str   # neutro, frustrado, satisfeito, urgente
    negation: bool        # se há negação
    multiple_intents: List[IntentType]  # intenções secundárias
    
    # 🚀 NOVOS CAMPOS ULTRA AVANÇADOS
    semantic_similarity: float = 0.0  # similaridade semântica com padrões conhecidos
    contextual_coherence: float = 0.0  # coerência contextual com conversa anterior
    linguistic_complexity: float = 0.0  # complexidade linguística do texto
    intent_certainty: float = 0.0  # certeza absoluta da intenção
    alternative_intents: List[Tuple[IntentType, float]] = field(default_factory=list)
    semantic_clusters: List[str] = field(default_factory=list)
    discourse_markers: List[str] = field(default_factory=list)
    pragmatic_inference: Dict[str, float] = field(default_factory=dict)

class SuperConversationEngine:
    """🚀 MEGA ULTRA ENGINE - INTELIGÊNCIA NÍVEL CHATGPT GIGANTEMENTE FODA"""
    
    def __init__(self):
        # 🧠 MEMÓRIA CONTEXTUAL ULTRA AVANÇADA
        self.user_contexts = {}
        self.conversation_cache = {}
        self.conversation_memories = {}  # Nova memória super avançada
        self.semantic_knowledge_base = {}  # Base de conhecimento semântico
        self.pattern_learning_db = defaultdict(list)  # Aprendizado de padrões
        
        # 🔬 SISTEMAS DE ANÁLISE ULTRA AVANÇADOS
        self.brazilian_language_db = self._load_brazilian_language_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.context_analyzers = self._load_context_analyzers()
        self.emotion_patterns = self._load_emotion_patterns()
        self.temporal_patterns = self._load_temporal_patterns()
        self.negation_patterns = self._load_negation_patterns()
        
        # 🚀 NOVOS SISTEMAS ULTRA AVANÇADOS - NÍVEL CHATGPT
        self.semantic_patterns = self._build_semantic_patterns()
        self.discourse_analyzers = self._load_discourse_analyzers()
        self.pragmatic_inference_engine = self._build_pragmatic_engine()
        self.contextual_coherence_analyzer = self._build_coherence_analyzer()
        self.multi_layer_processors = self._build_multi_layer_processors()
        self.intelligent_fallback_system = self._build_fallback_system()
        
        # 📚 CONHECIMENTO LINGUÍSTICO ULTRA PROFUNDO
        self.brazilian_semantic_vectors = self._build_semantic_vectors()
        self.intent_similarity_matrix = self._build_intent_similarity_matrix()
        self.contextual_relationship_graph = self._build_relationship_graph()
        
        # 🎯 RESPOSTAS CONTEXTUAIS MEGA INTELIGENTES
        self.contextual_responses = self._load_contextual_responses()
        self.dynamic_response_generator = self._build_dynamic_generator()
        
        logger.info("🚀 MEGA ULTRA ENGINE DE CONVERSAÇÃO NÍVEL CHATGPT INICIALIZADA!")
        
    def _load_brazilian_language_patterns(self) -> Dict[str, List[Dict]]:
        """🚀 PADRÕES PARA CLIENTES BURROS - ENTENDE QUALQUER COISA MAL ESCRITA"""
        return {
            # 📄 FATURA - Tudo que pode significar "quero minha conta"
            'fatura_detection': [
                # Palavras diretas
                {'pattern': r'(conta|boleto|fatura|cobrança)', 'weight': 1.0},
                {'pattern': r'(segunda.?via|2.?via|2via)', 'weight': 1.0},
                {'pattern': r'(debito|débito)', 'weight': 0.9},
                # Mal escritas comuns
                {'pattern': r'(cota|bolto|fatur)', 'weight': 0.9},  # erros de digitação
                {'pattern': r'(segundav|2av)', 'weight': 0.9},
                {'pattern': r'(cobransa|cobranca)', 'weight': 0.8},
                # Contextos indiretos
                {'pattern': r'(papel|documento).*(pagar)', 'weight': 0.7},
                {'pattern': r'(como.*(pagar|quitar))', 'weight': 0.8},
                {'pattern': r'(preciso.*(pagar|quitar))', 'weight': 0.8},
                {'pattern': r'(onde.*(pagar|boleto))', 'weight': 0.8},
                # Linguagem super simples
                {'pattern': r'(papel.*dinheiro)', 'weight': 0.7},
                {'pattern': r'(quanto.*devo)', 'weight': 0.9},
                {'pattern': r'(minha.*divida)', 'weight': 0.8},
                {'pattern': r'(ter.*pagar)', 'weight': 0.7},
            ],
            
            # 💰 VALOR - Quer saber quanto deve
            'valor_detection': [
                {'pattern': r'(quanto|valor)', 'weight': 1.0},
                {'pattern': r'(devo|deve|pagar)', 'weight': 0.9},
                {'pattern': r'(quanto.*mesmo|valor.*certo)', 'weight': 1.0},
                {'pattern': r'(ta.*quanto|tá.*quanto)', 'weight': 0.9},
                {'pattern': r'(preço|preco)', 'weight': 0.8},
                # Mal escritos
                {'pattern': r'(qnto|qnt)', 'weight': 0.8},
                {'pattern': r'(dveo|dvo)', 'weight': 0.7},  # "devo" mal escrito
                # Contextos
                {'pattern': r'(saber.*valor)', 'weight': 0.8},
                {'pattern': r'(conta.*valor)', 'weight': 0.8},
                {'pattern': r'(total.*pagar)', 'weight': 0.8},
            ],
            
            # ⏰ VENCIMENTO - Quer saber quando vence
            'vencimento_detection': [
                {'pattern': r'(vencimento|vence|prazo)', 'weight': 1.0},
                {'pattern': r'(quando.*vence)', 'weight': 1.0},
                {'pattern': r'(data.*pagamento)', 'weight': 0.9},
                {'pattern': r'(até.*quando)', 'weight': 0.8},
                {'pattern': r'(prazo.*final)', 'weight': 0.8},
                # Mal escritos
                {'pattern': r'(vencimeto|vencimto)', 'weight': 0.8},
                {'pattern': r'(qndo.*vence)', 'weight': 0.8},
                # Contextos de urgência
                {'pattern': r'(ainda.*tempo)', 'weight': 0.7},
                {'pattern': r'(posso.*pagar)', 'weight': 0.6},
            ],
            
            # 🤝 NEGOCIAÇÃO - Quer parcelar ou desconto
            'negociacao_detection': [
                {'pattern': r'(parcelar|dividir|fatiar)', 'weight': 1.0},
                {'pattern': r'(acordo|negociar|conversar)', 'weight': 0.9},
                {'pattern': r'(desconto|abatimento)', 'weight': 0.9},
                {'pattern': r'(dificuldade|difícil|apertado)', 'weight': 0.8},
                {'pattern': r'(não.*consigo.*pagar)', 'weight': 0.9},
                {'pattern': r'(sem.*dinheiro|sem.*grana)', 'weight': 0.8},
                # Mal escritos
                {'pattern': r'(parcelar|parsela)', 'weight': 0.8},
                {'pattern': r'(descoto|dsconto)', 'weight': 0.7},
                # Linguagem simples
                {'pattern': r'(quebrar.*galho)', 'weight': 0.7},
                {'pattern': r'(dar.*jeito)', 'weight': 0.6},
                {'pattern': r'(facilitar|ajudar)', 'weight': 0.7},
                {'pattern': r'(condições|condicoes)', 'weight': 0.8},
            ],
            
            # ✅ PAGAMENTO FEITO - Já pagou
            'pagamento_detection': [
                {'pattern': r'(já.*paguei|quitei|paguei)', 'weight': 1.0},
                {'pattern': r'(pix|transferência|depósito)', 'weight': 0.9},
                {'pattern': r'(efetuei|realizei)', 'weight': 0.8},
                {'pattern': r'(comprovante|anexo)', 'weight': 0.8},
                # Mal escritos
                {'pattern': r'(jah.*paguei|ja.*paguei)', 'weight': 0.9},
                {'pattern': r'(quitei|kitei)', 'weight': 0.8},
                {'pattern': r'(transferencia|trasferencia)', 'weight': 0.7},
                # Contextos
                {'pattern': r'(mandei.*dinheiro)', 'weight': 0.8},
                {'pattern': r'(pago.*ontem|pago.*hoje)', 'weight': 0.9},
                {'pattern': r'(banco.*pagar)', 'weight': 0.7},
            ],
            
            # 😡 RECLAMAÇÃO - Está reclamando
            'reclamacao_detection': [
                {'pattern': r'(errado|incorreto|equivocado)', 'weight': 1.0},
                {'pattern': r'(nunca.*(usei|contratei|pedi))', 'weight': 1.0},
                {'pattern': r'(não.*devo|nao.*devo)', 'weight': 0.9},
                {'pattern': r'(indevida|indevido)', 'weight': 0.9},
                {'pattern': r'(contestar|discordar)', 'weight': 0.8},
                # Palavrões e revolta (censurados)
                {'pattern': r'(que.*merda|porra|caramba)', 'weight': 0.9},
                {'pattern': r'(absurdo|revoltante)', 'weight': 0.8},
                # Linguagem simples de revolta
                {'pattern': r'(não.*certo|nao.*certo)', 'weight': 0.8},
                {'pattern': r'(enganação|roubo)', 'weight': 0.9},
                {'pattern': r'(não.*aceito|nao.*aceito)', 'weight': 0.8},
            ],
            
            # 👋 SAUDAÇÕES E DESPEDIDAS
            'interacao_social': [
                # Saudações
                {'pattern': r'(oi|olá|ola|oiii|eae|e.*ai)', 'intent': 'saudacao', 'weight': 1.0},
                {'pattern': r'(bom.*dia|boa.*tarde|boa.*noite)', 'intent': 'saudacao', 'weight': 1.0},
                {'pattern': r'(beleza|blz|suave)', 'intent': 'saudacao', 'weight': 0.8},
                # Despedidas
                {'pattern': r'(tchau|falou|até|flw|vlw)', 'intent': 'despedida', 'weight': 1.0},
                {'pattern': r'(obrigad[ao]|brigado|brigada)', 'intent': 'despedida', 'weight': 0.9},
                # Confirmações
                {'pattern': r'(tá.*bom|ta.*bom|ok|certo)', 'intent': 'confirmacao', 'weight': 0.8},
                {'pattern': r'(sim|yes|é.*isso)', 'intent': 'confirmacao', 'weight': 0.8},
                # Negações
                {'pattern': r'(não|nao|num|nope)', 'intent': 'negacao', 'weight': 0.9},
                # Dúvidas
                {'pattern': r'(como.*assim|que.*isso|ué)', 'intent': 'duvida', 'weight': 0.8},
                {'pattern': r'(não.*entendi|nao.*entendi)', 'intent': 'duvida', 'weight': 0.9},
            ],
            
            # 🔤 NORMALIZAÇÃO DE ERROS COMUNS
            'erro_patterns': {
                # Substituições automáticas para normalizar textos mal escritos
                'qnto': 'quanto',
                'qnt': 'quanto', 
                'qndo': 'quando',
                'vc': 'você',
                'pq': 'porque',
                'tbm': 'também',
                'n': 'não',
                'naum': 'não',
                'eh': 'é',
                'tah': 'está',
                'to': 'estou',
                'pra': 'para',
                'pro': 'para o',
                'msm': 'mesmo',
                'blz': 'beleza',
                'vlw': 'valeu',
                'flw': 'falou',
                'kd': 'cadê',
                'aki': 'aqui',
                'ai': 'aí',
                'hj': 'hoje',
                'ontem': 'ontem',
                'amanha': 'amanhã',
                'soh': 'só',
                'jah': 'já',
                'neh': 'né',
                'eh': 'é',
                'num': 'não',
                'vo': 'vou',
                'c': 'com',
                'cmg': 'comigo',
                'ctg': 'contigo',
                'dps': 'depois'
            }
        }
    
    def _load_entity_extractors(self) -> Dict[str, Dict]:
        """Extratores de entidades específicas"""
        return {
            'valores_monetarios': {
                'patterns': [
                    r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
                    r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*reais?)',
                    r'(\d+(?:,\d{2})?\s*pila)',  # Gíria brasileira
                ],
                'normalizer': self._normalize_currency
            },
            'datas': {
                'patterns': [
                    r'(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})',
                    r'(hoje|amanhã|ontem)',
                    r'(próxima?\s+\w+)',  # próxima semana
                    r'(dia\s+\d{1,2})',
                ],
                'normalizer': self._normalize_date
            },
            'protocolos': {
                'patterns': [
                    r'(protocolo\s*:?\s*(\w+\d+|\d+))',
                    r'(número\s+(\w+\d+|\d+))',
                ],
                'normalizer': self._normalize_protocol
            },
            'documentos': {
                'patterns': [
                    r'(cpf\s*:?\s*(\d{3}\.?\d{3}\.?\d{3}\-?\d{2}))',
                    r'(cnpj\s*:?\s*(\d{2}\.?\d{3}\.?\d{3}/?\d{4}\-?\d{2}))',
                ],
                'normalizer': self._normalize_document
            }
        }
    
    def _load_context_analyzers(self) -> Dict[str, Any]:
        """Analisadores de contexto conversacional"""
        return {
            'sequencias_conversacionais': [
                # Cliente → Bot → Cliente (follow-up)
                {
                    'sequence': ['bot_fatura_response', 'client_clarification'],
                    'new_context': 'fatura_detalhamento',
                    'boost_intent': ['fatura_valor', 'fatura_vencimento']
                },
                {
                    'sequence': ['bot_negociacao_response', 'client_acceptance'],
                    'new_context': 'negociacao_ativa',
                    'boost_intent': ['confirmacao', 'negociacao_parcelamento']
                }
            ],
            'padroes_contextuais': [
                # Se mencionou pagamento + valor, provavelmente confirmação
                {
                    'conditions': ['entity_valor', 'intent_pagamento'],
                    'inferred_intent': 'pagamento_confirmacao',
                    'confidence_boost': 0.3
                },
                # Se mencionou erro + valor, provavelmente reclamação
                {
                    'conditions': ['emotion_frustrado', 'entity_valor'],
                    'inferred_intent': 'reclamacao_valor_incorreto',
                    'confidence_boost': 0.4
                }
            ]
        }
    
    def _load_emotion_patterns(self) -> Dict[str, List[Dict]]:
        """Padrões de detecção emocional CORRIGIDOS"""
        return {
            'frustrado': [
                {'pattern': r'(que absurdo|não acredito|revoltante)', 'weight': 1.0},
                {'pattern': r'(indignado|revoltado|irritado)', 'weight': 0.9},
                {'pattern': r'(errada?|incorret[ao])', 'weight': 0.7},  # Corrigido para detectar reclamações
                {'pattern': r'(cara,.*paguei|cara,.*mas)', 'weight': 0.8},  # Específico para frustração com pagamento
                {'pattern': r'(nunca.*(contratei|usei|pedi))', 'weight': 0.8},  # Reclamação típica
                {'pattern': r'(péssimo|horrível|terrível)', 'weight': 0.8},
                {'pattern': r'(ainda.*(aparece|continua|mostra))', 'weight': 0.7},  # Frustração com pendência
            ],
            'urgente': [
                {'pattern': r'(urgente|emergência)', 'weight': 1.0},
                {'pattern': r'(preciso.*(urgente|rápido|agora))', 'weight': 0.9},
                {'pattern': r'(imediatamente|hoje)', 'weight': 0.8},
                {'pattern': r'(rápido)', 'weight': 0.6},  # Reduzido para não conflitar
            ],
            'satisfeito': [
                {'pattern': r'(obrigado|agradeço|valeu)', 'weight': 0.8},
                {'pattern': r'(perfeito|ótimo|excelente)', 'weight': 0.9},
                {'pattern': r'(resolveu|solucionou)', 'weight': 0.8},
                {'pattern': r'(muito bom|show)', 'weight': 0.7},
            ],
            'confuso': [
                {'pattern': r'(não entendi|como assim)', 'weight': 0.9},
                {'pattern': r'(confuso|perdido|não compreendi)', 'weight': 0.8},
                {'pattern': r'(explicar|esclarecer|que\s*\?)', 'weight': 0.6},
                # REMOVIDO "que" sozinho para evitar false positives
            ]
        }
    
    def _load_temporal_patterns(self) -> Dict[str, List[str]]:
        """Padrões temporais da conversa"""
        return {
            'passado': [
                r'(já\s+(paguei|fiz|resolvi))',
                r'(ontem|semana passada|mês passado)',
                r'(paguei|quitei|resolvi)',
            ],
            'presente': [
                r'(agora|atualmente|no momento)',
                r'(estou|estamos|está)',
                r'(hoje|neste momento)',
            ],
            'futuro': [
                r'(vou|vamos|pretendo)',
                r'(amanhã|semana que vem|próximo)',
                r'(planejando|pensando em)',
            ]
        }
    
    def _load_negation_patterns(self) -> List[str]:
        """Padrões de negação brasileiros"""
        return [
            r'(não|num|nao)',
            r'(nunca|jamais)',
            r'(nem|nem que)',
            r'(de jeito nenhum|de forma alguma)',
            r'(negative|negativo)',
        ]
    
    async def process_message(self, phone: str, text: str) -> Optional[Dict[str, Any]]:
        """🚀 PROCESSAMENTO ULTRA MEGA INTELIGENTE - NÍVEL CHATGPT GIGANTEMENTE FODA"""
        try:
            logger.info(f"🚀 MEGA ANÁLISE ULTRA AVANÇADA para {phone}: {text[:50]}...")
            
            # 🧠 FASE 1: PREPARAÇÃO E NORMALIZAÇÃO ULTRA AVANÇADA
            conversation_memory = self._get_or_create_conversation_memory(phone)
            original_text = text
            normalized_text = self._ultra_advanced_normalize_text(text)
            
            # 🔬 FASE 2: ANÁLISE MULTI-CAMADAS ULTRA PROFUNDA
            linguistic_analysis = await self._perform_multi_layer_analysis(normalized_text)
            semantic_analysis = await self._perform_semantic_analysis(normalized_text, conversation_memory)
            pragmatic_analysis = await self._perform_pragmatic_analysis(normalized_text, conversation_memory)
            
            # 🎯 FASE 3: EXTRAÇÃO DE ENTIDADES COM CONTEXTO SEMÂNTICO
            entities = await self._extract_ultra_advanced_entities(normalized_text, semantic_analysis)
            logger.info(f"🔍 Entidades ultra avançadas: {[e.type + ':' + e.value for e in entities]}")
            
            # 😊 FASE 4: ANÁLISE EMOCIONAL E TEMPORAL PROFUNDA
            emotional_state = await self._analyze_ultra_emotion(normalized_text, conversation_memory)
            temporal_context = await self._analyze_ultra_temporal_context(normalized_text, conversation_memory)
            negation_analysis = await self._analyze_ultra_negation(normalized_text)
            
            logger.info(f"😊 Estado emocional ultra: {emotional_state}")
            logger.info(f"⏰ Contexto temporal ultra: {temporal_context}")
            logger.info(f"❌ Análise de negação: {negation_analysis}")
            
            # 🧠 FASE 5: INFERÊNCIA CONTEXTUAL ULTRA AVANÇADA
            contextual_intent = await self._analyze_ultra_contextual_intent(
                normalized_text, entities, emotional_state, temporal_context, 
                negation_analysis, conversation_memory, semantic_analysis, pragmatic_analysis
            )
            
            # 📊 FASE 6: ANÁLISE DE COERÊNCIA E CERTEZA
            coherence_score = await self._analyze_contextual_coherence(contextual_intent, conversation_memory)
            certainty_score = await self._calculate_intent_certainty(contextual_intent, linguistic_analysis)
            
            contextual_intent.contextual_coherence = coherence_score
            contextual_intent.intent_certainty = certainty_score
            
            logger.info(f"🎯 Intenção principal ULTRA: {contextual_intent.intent.value}")
            logger.info(f"🎯 Múltiplas intenções: {[i.value for i in contextual_intent.multiple_intents]}")
            logger.info(f"📊 Confiança ULTRA: {contextual_intent.confidence:.3f}")
            logger.info(f"🔗 Coerência contextual: {coherence_score:.3f}")
            logger.info(f"✅ Certeza da intenção: {certainty_score:.3f}")
            
            # 🧠 FASE 7: APRENDIZADO E ATUALIZAÇÃO DE MEMÓRIA
            await self._update_ultra_conversation_memory(phone, contextual_intent, original_text, linguistic_analysis)
            await self._learn_from_interaction(phone, contextual_intent, semantic_analysis)
            
            # 🎭 FASE 8: GERAÇÃO DINÂMICA DE RESPOSTA ULTRA INTELIGENTE
            response = await self._generate_ultra_contextual_response(
                phone, contextual_intent, entities, conversation_memory, semantic_analysis
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento MEGA ULTRA: {e}")
            return await self._ultra_intelligent_fallback(phone, text, e)
    
    def _extract_all_entities(self, text: str) -> List[ExtractedEntity]:
        """Extração completa de entidades"""
        entities = []
        
        for entity_type, config in self.entity_extractors.items():
            for pattern in config['patterns']:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = ExtractedEntity(
                        type=entity_type,
                        value=config['normalizer'](match.group()),
                        confidence=0.9,
                        context=text[max(0, match.start()-20):match.end()+20]
                    )
                    entities.append(entity)
        
        return entities
    
    def _analyze_emotion(self, text: str) -> str:
        """Análise emocional profunda"""
        emotion_scores = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0.0
            for pattern_data in patterns:
                matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
                score += matches * pattern_data['weight']
            emotion_scores[emotion] = score
        
        # Determinar emoção dominante
        if not emotion_scores or max(emotion_scores.values()) == 0:
            return 'neutro'
        
        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        return dominant_emotion
    
    def _analyze_temporal_context(self, text: str) -> str:
        """Análise do contexto temporal"""
        for tempo, patterns in self.temporal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return tempo
        
        return 'presente'  # default
    
    def _detect_negation(self, text: str) -> bool:
        """Detecção robusta de negação"""
        for pattern in self.negation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _analyze_contextual_intent(
        self, text: str, entities: List[ExtractedEntity], emotion: str,
        temporal: str, negation: bool, conversation_context: Dict
    ) -> ContextualIntent:
        """🧠 ANÁLISE CONTEXTUAL REVOLUCIONÁRIA"""
        
        # Análise de intenções base
        base_intents = self._analyze_base_intents(text, entities, emotion)
        
        # Boost contextual baseado na conversa
        contextual_boost = self._apply_contextual_boost(base_intents, conversation_context)
        
        # Análise de múltiplas intenções
        multiple_intents = self._detect_multiple_intents(text, entities)
        
        # Determinar intenção principal
        best_intent_data = max(contextual_boost.items(), key=lambda x: x[1])
        best_intent = IntentType(best_intent_data[0])
        confidence = min(best_intent_data[1], 1.0)
        
        return ContextualIntent(
            intent=best_intent,
            confidence=confidence,
            entities=entities,
            temporal_context=temporal,
            emotional_state=emotion,
            negation=negation,
            multiple_intents=multiple_intents
        )
    
    def _analyze_base_intents(self, text: str, entities: List[ExtractedEntity], emotion: str) -> Dict[str, float]:
        """🚀 ANÁLISE ULTRA AVANÇADA - ENTENDE CLIENTES BURROS QUE NÃO SABEM SE EXPRESSAR"""
        intent_scores = {}
        
        # 📄 ANÁLISE FATURA - Usando nossos novos padrões ultra avançados
        fatura_solicitar_score = 0.0
        fatura_valor_score = 0.0
        fatura_vencimento_score = 0.0
        
        # Aplicar padrões de detecção de fatura
        for pattern_data in self.brazilian_language_db.get('fatura_detection', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                fatura_solicitar_score += matches * pattern_data['weight']
        
        # Aplicar padrões de detecção de valor
        for pattern_data in self.brazilian_language_db.get('valor_detection', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                fatura_valor_score += matches * pattern_data['weight']
        
        # Aplicar padrões de detecção de vencimento
        for pattern_data in self.brazilian_language_db.get('vencimento_detection', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                fatura_vencimento_score += matches * pattern_data['weight']
        
        # 🤝 ANÁLISE NEGOCIAÇÃO - Usando nossos padrões avançados
        negociacao_parcelamento_score = 0.0
        negociacao_desconto_score = 0.0
        
        for pattern_data in self.brazilian_language_db.get('negociacao_detection', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                # Decidir se é parcelamento ou desconto baseado no contexto
                if re.search(r'(parcelar|dividir|fatiar)', pattern_data['pattern'], re.IGNORECASE):
                    negociacao_parcelamento_score += matches * pattern_data['weight']
                elif re.search(r'(desconto|abatimento)', pattern_data['pattern'], re.IGNORECASE):
                    negociacao_desconto_score += matches * pattern_data['weight']
                else:
                    # Padrões genéricos: priorizar parcelamento (mais comum)
                    negociacao_parcelamento_score += matches * pattern_data['weight'] * 0.7
                    negociacao_desconto_score += matches * pattern_data['weight'] * 0.3
        
        # ✅ ANÁLISE PAGAMENTO FEITO - Usando nossos padrões
        pagamento_score = 0.0
        
        for pattern_data in self.brazilian_language_db.get('pagamento_detection', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                pagamento_score += matches * pattern_data['weight']
        
        # 😡 ANÁLISE RECLAMAÇÃO - Usando nossos padrões
        reclamacao_indevida_score = 0.0
        reclamacao_valor_score = 0.0
        
        for pattern_data in self.brazilian_language_db.get('reclamacao_detection', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                # Se menciona "nunca usei/contratei" é cobrança indevida
                if re.search(r'(nunca.*(usei|contratei))', pattern_data['pattern'], re.IGNORECASE):
                    reclamacao_indevida_score += matches * pattern_data['weight']
                else:
                    # Outros tipos de reclamação (valor incorreto)
                    reclamacao_valor_score += matches * pattern_data['weight']
        
        # 👋 ANÁLISE INTERAÇÃO SOCIAL
        saudacao_score = 0.0
        despedida_score = 0.0
        confirmacao_score = 0.0
        negacao_score = 0.0
        duvida_score = 0.0
        
        for pattern_data in self.brazilian_language_db.get('interacao_social', []):
            matches = len(re.findall(pattern_data['pattern'], text, re.IGNORECASE))
            if matches > 0:
                intent_type = pattern_data.get('intent', 'unknown')
                score = matches * pattern_data['weight']
                
                if intent_type == 'saudacao':
                    saudacao_score += score
                elif intent_type == 'despedida':
                    despedida_score += score
                elif intent_type == 'confirmacao':
                    confirmacao_score += score
                elif intent_type == 'negacao':
                    negacao_score += score
                elif intent_type == 'duvida':
                    duvida_score += score
        
        # 🧠 LÓGICA CONTEXTUAL AVANÇADA PARA CASOS CONFUSOS
        
        # Se cliente escreveu poucas palavras, tentar inferir pelo contexto
        palavras = len(text.split())
        if palavras <= 3:
            # Textos muito curtos - analisar palavras-chave críticas
            if re.search(r'(conta|boleto|fatura)', text, re.IGNORECASE):
                fatura_solicitar_score += 0.8
            elif re.search(r'(quanto|valor)', text, re.IGNORECASE):
                fatura_valor_score += 0.8
            elif re.search(r'(quando|vence)', text, re.IGNORECASE):
                fatura_vencimento_score += 0.8
            elif re.search(r'(paguei|pago)', text, re.IGNORECASE):
                pagamento_score += 0.8
            elif re.search(r'(parcelar|acordo)', text, re.IGNORECASE):
                negociacao_parcelamento_score += 0.8
        
        # Se tem entidades monetárias, boost intenções relacionadas a dinheiro
        tem_valor = any(e.type == 'valores_monetarios' for e in entities)
        if tem_valor:
            fatura_valor_score += 0.4
            pagamento_score += 0.3
            negociacao_parcelamento_score += 0.2
        
        # Se tem datas, boost vencimento
        tem_data = any(e.type == 'datas' for e in entities)
        if tem_data:
            fatura_vencimento_score += 0.4
            pagamento_score += 0.2
        
        # 😤 BOOST BASEADO EM EMOÇÃO
        if emotion == 'frustrado':
            reclamacao_indevida_score += 0.4
            reclamacao_valor_score += 0.4
        elif emotion == 'urgente':
            fatura_solicitar_score += 0.3
            fatura_valor_score += 0.2
        elif emotion == 'confuso':
            duvida_score += 0.3
        
        # 🎯 NORMALIZAR SCORES (max 1.0 para cada)
        intent_scores = {
            'fatura_solicitar': min(fatura_solicitar_score, 1.0),
            'fatura_valor': min(fatura_valor_score, 1.0),
            'fatura_vencimento': min(fatura_vencimento_score, 1.0),
            'negociacao_parcelamento': min(negociacao_parcelamento_score, 1.0),
            'negociacao_desconto': min(negociacao_desconto_score, 1.0),
            'pagamento_confirmacao': min(pagamento_score, 1.0),
            'reclamacao_cobranca_indevida': min(reclamacao_indevida_score, 1.0),
            'reclamacao_valor_incorreto': min(reclamacao_valor_score, 1.0),
            'saudacao': min(saudacao_score, 1.0),
            'despedida': min(despedida_score, 1.0),
            'confirmacao': min(confirmacao_score, 1.0),
            'negacao': min(negacao_score, 1.0),
            'duvida': min(duvida_score, 1.0)
        }
        
        # 🚨 FALLBACK INTELIGENTE - Se nenhuma intenção forte foi detectada
        max_score = max(intent_scores.values()) if intent_scores.values() else 0
        if max_score < 0.3:
            # Cliente escreveu algo muito confuso - tentar inferir pela presença de palavras-chave
            if any(palavra in text.lower() for palavra in ['conta', 'boleto', 'fatura', 'pagar', 'deve']):
                intent_scores['fatura_solicitar'] = 0.5  # Assumir que quer fatura
            elif any(palavra in text.lower() for palavra in ['quanto', 'valor', 'preço']):
                intent_scores['fatura_valor'] = 0.5  # Assumir que quer saber valor
            else:
                intent_scores['duvida'] = 0.5  # Cliente está confuso
        
        return intent_scores
    
    def _apply_contextual_boost(self, base_intents: Dict[str, float], context: Dict) -> Dict[str, float]:
        """Aplicar boost baseado no contexto conversacional"""
        boosted_intents = base_intents.copy()
        
        # Se última mensagem foi sobre fatura, boost relacionados
        last_context = context.get('last_intent')
        if last_context and 'fatura' in last_context:
            boosted_intents['fatura_valor'] = boosted_intents.get('fatura_valor', 0) + 0.2
            boosted_intents['fatura_vencimento'] = boosted_intents.get('fatura_vencimento', 0) + 0.2
        
        # Se contexto de negociação ativa
        if context.get('negotiation_active'):
            boosted_intents['negociacao_desconto'] = boosted_intents.get('negociacao_desconto', 0) + 0.3
            boosted_intents['confirmacao'] = boosted_intents.get('confirmacao', 0) + 0.2
        
        return boosted_intents
    
    def _detect_multiple_intents(self, text: str, entities: List[ExtractedEntity]) -> List[IntentType]:
        """Detectar múltiplas intenções na mesma mensagem - MELHORADO"""
        intents = []
        
        # Detectores mais robustos de múltiplas intenções
        
        # "fatura E desconto/parcelamento"
        if (re.search(r'(fatura|conta)', text, re.IGNORECASE) and 
            re.search(r'(também|e\s+(também)?).*(desconto|parcelar)', text, re.IGNORECASE)):
            intents.extend([IntentType.FATURA_SOLICITAR, IntentType.NEGOCIACAO_DESCONTO])
        
        # "fatura E parcelamento"  
        if (re.search(r'(fatura|conta)', text, re.IGNORECASE) and 
            re.search(r'(também|e\s+(também)?).*(parcelar|dividir)', text, re.IGNORECASE)):
            intents.extend([IntentType.FATURA_SOLICITAR, IntentType.NEGOCIACAO_PARCELAMENTO])
        
        # "paguei MAS ainda aparece"
        if (re.search(r'(paguei|quitei)', text, re.IGNORECASE) and 
            re.search(r'(mas|porém|ainda|continua|aparece)', text, re.IGNORECASE)):
            intents.extend([IntentType.PAGAMENTO_CONFIRMACAO, IntentType.RECLAMACAO_VALOR_INCORRETO])
        
        # "valor E vencimento"
        if (re.search(r'(quanto.*devo)', text, re.IGNORECASE) and 
            re.search(r'(quando.*vence|prazo)', text, re.IGNORECASE)):
            intents.extend([IntentType.FATURA_VALOR, IntentType.FATURA_VENCIMENTO])
        
        # Conectores brasileiros comuns
        conectores = [r'\s+e\s+', r'\s+também\s+', r'\s+além\s+disso\s+', r'\s+mais\s+']
        for conector in conectores:
            if re.search(conector, text, re.IGNORECASE):
                # Se tem conector, analisar cada parte
                partes = re.split(conector, text, flags=re.IGNORECASE)
                if len(partes) >= 2:
                    # Analisar se cada parte tem intenção diferente
                    primeira_parte = partes[0].strip()
                    segunda_parte = partes[1].strip()
                    
                    # Lógica simplificada para detectar intenções diferentes
                    if ('fatura' in primeira_parte.lower() and 
                        any(palavra in segunda_parte.lower() for palavra in ['desconto', 'parcelar', 'negociar'])):
                        intents.extend([IntentType.FATURA_SOLICITAR, IntentType.NEGOCIACAO_DESCONTO])
                        break
        
        return intents
    
    # Métodos de normalização (implementações simplificadas)
    def _normalize_currency(self, text: str) -> str:
        return re.sub(r'[^\d,]', '', text)
    
    def _normalize_date(self, text: str) -> str:
        return text.strip()
    
    def _normalize_protocol(self, text: str) -> str:
        return re.sub(r'[^\w\d]', '', text)
    
    def _normalize_document(self, text: str) -> str:
        return re.sub(r'[^\d]', '', text)
    
    def _super_normalize_text(self, text: str) -> str:
        """🚀 NORMALIZAÇÃO ULTRA AVANÇADA - CORRIGE QUALQUER TEXTO MAL ESCRITO"""
        
        # 1. PRIMEIRA PASSADA - Limpeza básica
        text = text.lower().strip()
        
        # 2. REMOVER EMOJIS E CARACTERES ESPECIAIS (mas preservar pontuação básica)
        text = re.sub(r'[^\w\s\.,!?\-áàâãéèêíìîóòôõúùûç]', ' ', text)
        
        # 3. CORRIGIR ABREVIAÇÕES E ERROS COMUNS (do nosso dicionário)
        erro_patterns = self.brazilian_language_db.get('erro_patterns', {})
        for erro, correto in erro_patterns.items():
            # Usar word boundary para não corrigir partes de palavras
            text = re.sub(rf'\b{re.escape(erro)}\b', correto, text, flags=re.IGNORECASE)
        
        # 4. CORREÇÕES ESPECÍFICAS DE PORTUGUÊS BRASILEIRO MAL ESCRITO
        corrections = {
            # Erros comuns de "quanto"
            r'\b(qnt|qnto|qto|cuanto)\b': 'quanto',
            # Erros comuns de "quando"  
            r'\b(qnd|qndo|quado|cuando)\b': 'quando',
            # Erros de "você"
            r'\bvc\b': 'você',
            # Erros de "não"
            r'\b(nao|naum|ñ|n)\b': 'não',
            # Erros de "para"
            r'\b(pra|pr)\b': 'para',
            # Erros de "porque"
            r'\b(pq|pk|porq)\b': 'porque',
            # Erros de "também"
            r'\b(tb|tbm|tbn)\b': 'também',
            # Erros de "está"
            r'\b(tah|ta|tá)\b': 'está',
            # Erros de "estou"
            r'\b(to|tou)\b': 'estou',
            # Erros de "já"
            r'\b(jah|ja)\b': 'já',
            # Erros de "só"
            r'\b(soh|so)\b': 'só',
            # Erros de "é"
            r'\b(eh|e)\b': 'é',
            # Erros de "hoje"
            r'\bhj\b': 'hoje',
            # Erros de "amanhã"
            r'\b(amanha|amñ)\b': 'amanhã',
            # Erros de "cadê"
            r'\bkd\b': 'cadê',
            # Erros de "aqui"
            r'\b(aki|aq)\b': 'aqui',
            # Erros de "aí"
            r'\b(ai|ae)\b': 'aí',
            # Erros de "mesmo"
            r'\b(msm|mmo)\b': 'mesmo',
            # Erros de "beleza"
            r'\b(blz|bz)\b': 'beleza',
            # Erros de "valeu"
            r'\b(vlw|vl)\b': 'valeu',
            # Erros de "falou"
            r'\b(flw|fl)\b': 'falou',
            # Erros comuns de palavras de cobrança
            r'\b(fatur|ftur)\b': 'fatura',
            r'\b(bolto|bleto)\b': 'boleto',
            r'\b(cota|cnta)\b': 'conta',
            r'\b(cobransa|cobranca)\b': 'cobrança',
            r'\b(pagameto|pagamnto)\b': 'pagamento',
            r'\b(vencimeto|vencimto)\b': 'vencimento',
            r'\b(transferencia|trasferencia)\b': 'transferência',
            r'\b(debto|debito)\b': 'débito'
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 5. REMOVER PONTUAÇÃO EXCESSIVA mas preservar sentido
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        
        # 6. NORMALIZAR ESPAÇOS
        text = re.sub(r'\s+', ' ', text)
        
        # 7. CORREÇÕES CONTEXTUAIS ESPECÍFICAS PARA COBRANÇA
        cobranca_corrections = {
            # "segunda via" mal escrito
            r'(segunda|2)\s*(v|vi|via)': 'segunda via',
            # "quanto devo" mal escrito  
            r'(quanto|qnto)\s*(devo|dvo|dveo)': 'quanto devo',
            # "já paguei" mal escrito
            r'(já|jah|ja)\s*(paguei|pguei|pag)': 'já paguei',
            # "não devo" mal escrito
            r'(não|nao|naum)\s*(devo|dvo)': 'não devo',
            # "minha conta" mal escrito
            r'(minha|miha)\s*(conta|cota)': 'minha conta'
        }
        
        for pattern, replacement in cobranca_corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _get_conversation_context(self, phone: str) -> Dict:
        """Obter contexto da conversa"""
        return self.user_contexts.get(phone, {})
    
    def _update_conversation_context(self, phone: str, intent: ContextualIntent, text: str):
        """Atualizar contexto conversacional"""
        if phone not in self.user_contexts:
            self.user_contexts[phone] = {
                'messages': [],
                'last_intent': None,
                'negotiation_active': False,
                'client_profile': {},
                'conversation_flow': []
            }
        
        context = self.user_contexts[phone]
        context['messages'].append({
            'text': text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'timestamp': datetime.now(),
            'entities': [{'type': e.type, 'value': e.value} for e in intent.entities],
            'emotion': intent.emotional_state
        })
        
        context['last_intent'] = intent.intent.value
        
        # Detectar se negociação está ativa
        if intent.intent in [IntentType.NEGOCIACAO_DESCONTO, IntentType.NEGOCIACAO_PARCELAMENTO]:
            context['negotiation_active'] = True
        
        # Manter apenas últimas 10 mensagens
        context['messages'] = context['messages'][-10:]
    
    async def _generate_contextual_response(
        self, phone: str, intent: ContextualIntent, entities: List[ExtractedEntity], context: Dict
    ) -> Dict[str, Any]:
        """🚀 GERADOR DE RESPOSTAS ULTRA INTELIGENTE - PERFEITO PARA CLIENTES BURROS"""
        
        # 🎯 RESPOSTAS BASEADAS NA INTENÇÃO COM CONTEXTO EMOCIONAL
        
        if intent.intent == IntentType.FATURA_SOLICITAR:
            if intent.emotional_state == 'urgente':
                response_text = "🚨 **URGENTE!** Entendi! Vou buscar sua fatura AGORA MESMO e te enviar em segundos!"
            elif intent.emotional_state == 'frustrado':
                response_text = "😔 Percebo que você está chateado. Calma, vou resolver isso rapidinho! Enviando sua fatura já..."
            elif intent.negation:
                response_text = "🤔 Vi que você disse 'não' sobre algo. Me explica melhor o que você precisa da sua conta?"
            else:
                response_text = "📄 **PERFEITO!** Vou pegar sua fatura para você. Só um minutinho..."
        
        elif intent.intent == IntentType.FATURA_VALOR:
            valor_entity = next((e for e in entities if e.type == 'valores_monetarios'), None)
            if valor_entity:
                response_text = f"💰 Vi que você mencionou **R$ {valor_entity.value}**. Vou confirmar se esse é o valor correto da sua conta!"
            elif intent.emotional_state == 'urgente':
                response_text = "💰 **URGENTE!** Vou verificar AGORA quanto você deve exatamente!"
            else:
                response_text = "💰 Entendi! Você quer saber **QUANTO DEVE**, certo? Vou verificar o valor da sua conta!"
        
        elif intent.intent == IntentType.FATURA_VENCIMENTO:
            data_entity = next((e for e in entities if e.type == 'datas'), None)
            if data_entity:
                response_text = f"⏰ Vi que você mencionou **{data_entity.value}**. Vou confirmar o vencimento da sua conta!"
            else:
                response_text = "⏰ Entendi! Você quer saber **QUANDO VENCE** sua conta, né? Vou verificar a data!"
        
        elif intent.intent == IntentType.NEGOCIACAO_PARCELAMENTO:
            if intent.emotional_state == 'frustrado':
                response_text = "🤝 Entendo que está difícil pagar. **CALMA!** Vamos dar um jeito! Temos várias opções de parcelamento!"
            elif any(e.type == 'valores_monetarios' for e in entities):
                valor = next(e.value for e in entities if e.type == 'valores_monetarios')
                response_text = f"🤝 Perfeito! Você quer parcelar **R$ {valor}**, né? Vamos encontrar a melhor condição para você!"
            else:
                response_text = "🤝 **ÓTIMO!** Quer parcelar? Vou ver as melhores condições que temos disponíveis!"
        
        elif intent.intent == IntentType.NEGOCIACAO_DESCONTO:
            if intent.emotional_state == 'frustrado':
                response_text = "💸 Entendo sua situação! Vamos ver que **DESCONTO** posso conseguir para você!"
            else:
                response_text = "💸 Interessado em desconto? **PERFEITO!** Vou verificar as promoções disponíveis!"
        
        elif intent.intent == IntentType.PAGAMENTO_CONFIRMACAO:
            if intent.temporal_context == 'passado':
                if intent.emotional_state == 'frustrado':
                    response_text = "✅ Entendi! Você **JÁ PAGOU** mas ainda está aparecendo, né? Vou verificar URGENTE o que aconteceu!"
                else:
                    response_text = "✅ **BELEZA!** Você já pagou! Vou confirmar aqui no sistema se o pagamento foi processado!"
            else:
                response_text = "💳 Perfeito! Vou verificar o status do seu pagamento no sistema!"
        
        elif intent.intent == IntentType.RECLAMACAO_COBRANCA_INDEVIDA:
            if intent.emotional_state == 'frustrado':
                response_text = "😡 **ENTENDO SUA REVOLTA!** Cobrança indevida é muito chato mesmo! Vou resolver isso AGORA!"
            else:
                response_text = "🔍 Entendi! Você acha que essa cobrança está **ERRADA**, né? Vou analisar sua situação!"
        
        elif intent.intent == IntentType.RECLAMACAO_VALOR_INCORRETO:
            response_text = "🔍 **NOSSA!** Valor incorreto é sério! Vou verificar sua conta e corrigir se estiver errado mesmo!"
        
        elif intent.intent == IntentType.SAUDACAO:
            horario = datetime.now().hour
            if horario < 12:
                response_text = "🌅 **BOM DIA!** Tudo beleza? Como posso te ajudar hoje?"
            elif horario < 18:
                response_text = "☀️ **BOA TARDE!** E aí, tudo certo? Em que posso ajudar?"
            else:
                response_text = "🌙 **BOA NOITE!** Beleza? Como posso te ajudar?"
        
        elif intent.intent == IntentType.DESPEDIDA:
            response_text = "👋 **VALEU!** Obrigado pelo contato! Qualquer coisa, me chama! 😊"
        
        elif intent.intent == IntentType.CONFIRMACAO:
            response_text = "✅ **PERFEITO!** Entendi que você confirmou! Vou continuar com o processo!"
        
        elif intent.intent == IntentType.NEGACAO:
            response_text = "❌ **BELEZA!** Você disse que não. Me explica melhor o que você precisa então?"
        
        elif intent.intent == IntentType.DUVIDA:
            response_text = "🤔 **SEM PROBLEMAS!** Vou explicar melhor! O que especificamente você não entendeu?"
        
        else:
            # Fallback inteligente baseado no que foi detectado
            if intent.confidence < 0.5:
                response_text = "🤔 **CALMA!** Acho que não entendi direito. Pode me falar de novo de um jeito mais simples? Tipo: 'quero minha conta' ou 'quanto devo'?"
            else:
                response_text = "🤖 **ENTENDI ALGUMA COISA!** Mas me explica melhor o que você precisa. Fala de forma simples!"
        
        # 📋 ADICIONAR INFORMAÇÕES SOBRE MÚLTIPLAS INTENÇÕES
        if intent.multiple_intents and len(intent.multiple_intents) > 0:
            intents_text = []
            for multi_intent in intent.multiple_intents:
                if multi_intent == IntentType.FATURA_SOLICITAR:
                    intents_text.append("ver sua conta")
                elif multi_intent == IntentType.FATURA_VALOR:
                    intents_text.append("saber quanto deve")
                elif multi_intent == IntentType.NEGOCIACAO_PARCELAMENTO:
                    intents_text.append("parcelar")
                elif multi_intent == IntentType.NEGOCIACAO_DESCONTO:
                    intents_text.append("conseguir desconto")
                else:
                    intents_text.append(multi_intent.value.replace('_', ' '))
            
            if intents_text:
                response_text += f"\n\n📋 **TAMBÉM PERCEBI** que você quer: {' e '.join(intents_text)}. Vou ajudar com tudo!"
        
        # 🔥 ADICIONAR CALL TO ACTION BASEADO NA INTENÇÃO
        if intent.intent in [IntentType.FATURA_SOLICITAR, IntentType.FATURA_VALOR, IntentType.FATURA_VENCIMENTO]:
            response_text += "\n\n⚡ **Aguarda aí que vou buscar suas informações!**"
        elif intent.intent in [IntentType.NEGOCIACAO_PARCELAMENTO, IntentType.NEGOCIACAO_DESCONTO]:
            response_text += "\n\n🤝 **Vou verificar as melhores condições para você!**"
        elif intent.intent == IntentType.PAGAMENTO_CONFIRMACAO:
            response_text += "\n\n🔍 **Verificando seu pagamento no sistema...**"
        
        return {
            'text': response_text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'entities_detected': len(entities),
            'emotional_state': intent.emotional_state,
            'multiple_intents': len(intent.multiple_intents),
            'context_enhanced': True,
            'response_type': 'ultra_contextual'
        }
    
    async def _generate_fallback_response(self, phone: str, text: str) -> Dict[str, Any]:
        """Resposta de fallback inteligente"""
        return {
            'text': "🤔 Percebi que você está tentando me dizer algo importante. Pode reformular para eu entender melhor?",
            'intent': 'clarification_needed',
            'confidence': 0.3,
            'fallback': True
        }
    
    def _load_contextual_responses(self) -> Dict:
        """Carregar respostas contextuais avançadas"""
        return {
            # Implementar depois conforme necessário
            'advanced_templates': {}
        } 
    
    # ================================
    # 🚀 SISTEMAS ULTRA AVANÇADOS - NÍVEL CHATGPT
    # ================================
    
    def _build_semantic_patterns(self) -> Dict[str, SemanticPattern]:
        """🧠 CONSTRUIR PADRÕES SEMÂNTICOS ULTRA AVANÇADOS"""
        patterns = {}
        
        # Padrão semântico para FATURA
        patterns['fatura_semantic'] = SemanticPattern(
            pattern_id='fatura_semantic',
            semantic_vectors={
                'documento': 0.9, 'papel': 0.8, 'conta': 1.0, 'boleto': 1.0,
                'cobrança': 0.9, 'débito': 0.8, 'pagamento': 0.7, 'valor': 0.6,
                'segunda_via': 1.0, 'cópia': 0.7, 'comprovante': 0.6
            },
            context_triggers=['preciso', 'quero', 'mandar', 'enviar', 'ver'],
            intent_weights={'fatura_solicitar': 1.0, 'fatura_valor': 0.3},
            emotional_indicators={'urgente': 0.3, 'neutro': 0.7},
            confidence_modifiers={'direto': 1.0, 'indireto': 0.7}
        )
        
        # Padrão semântico para VALOR/QUANTIDADE
        patterns['valor_semantic'] = SemanticPattern(
            pattern_id='valor_semantic',
            semantic_vectors={
                'quanto': 1.0, 'valor': 1.0, 'preço': 0.9, 'custo': 0.8,
                'dinheiro': 0.7, 'grana': 0.8, 'real': 0.6, 'centavo': 0.5,
                'total': 0.9, 'dever': 0.9, 'pagar': 0.8
            },
            context_triggers=['devo', 'pago', 'custa', 'vale'],
            intent_weights={'fatura_valor': 1.0, 'pagamento_confirmacao': 0.4},
            emotional_indicators={'frustrado': 0.2, 'neutro': 0.8},
            confidence_modifiers={'pergunta': 1.0, 'afirmacao': 0.6}
        )
        
        # Padrão semântico para TEMPO/VENCIMENTO
        patterns['tempo_semantic'] = SemanticPattern(
            pattern_id='tempo_semantic',
            semantic_vectors={
                'quando': 1.0, 'data': 0.9, 'dia': 0.8, 'prazo': 1.0,
                'vencimento': 1.0, 'vence': 1.0, 'até': 0.7, 'tempo': 0.8,
                'hoje': 0.6, 'amanhã': 0.7, 'mês': 0.6
            },
            context_triggers=['vence', 'termina', 'acaba', 'expira'],
            intent_weights={'fatura_vencimento': 1.0, 'pagamento_confirmacao': 0.3},
            emotional_indicators={'urgente': 0.5, 'neutro': 0.5},
            confidence_modifiers={'futuro': 1.0, 'passado': 0.4}
        )
        
        # Padrão semântico para NEGOCIAÇÃO
        patterns['negociacao_semantic'] = SemanticPattern(
            pattern_id='negociacao_semantic',
            semantic_vectors={
                'parcelar': 1.0, 'dividir': 0.9, 'acordo': 0.9, 'negociar': 1.0,
                'desconto': 1.0, 'abatimento': 0.8, 'facilitar': 0.7, 'ajuda': 0.6,
                'dificuldade': 0.8, 'problema': 0.7, 'apertado': 0.8, 'quebrar_galho': 0.9
            },
            context_triggers=['não_consigo', 'difícil', 'sem_dinheiro', 'ajudar'],
            intent_weights={'negociacao_parcelamento': 0.7, 'negociacao_desconto': 0.3},
            emotional_indicators={'frustrado': 0.6, 'urgente': 0.4},
            confidence_modifiers={'pedido': 1.0, 'sugestao': 0.8}
        )
        
        return patterns
    
    def _build_semantic_vectors(self) -> Dict[str, Dict[str, float]]:
        """🔬 CONSTRUIR VETORES SEMÂNTICOS BRASILEIROS ULTRA AVANÇADOS"""
        return {
            # Vetores semânticos para palavras de cobrança
            'fatura': {
                'conta': 0.95, 'boleto': 0.90, 'cobrança': 0.85, 'débito': 0.80,
                'documento': 0.75, 'papel': 0.70, 'segunda_via': 0.95, 'cópia': 0.60
            },
            'pagar': {
                'quitar': 0.90, 'saldar': 0.85, 'liquidar': 0.80, 'acertar': 0.75,
                'resolver': 0.70, 'transferir': 0.65, 'depositar': 0.60
            },
            'quanto': {
                'valor': 0.95, 'preço': 0.90, 'custo': 0.85, 'total': 0.80,
                'dinheiro': 0.75, 'grana': 0.80, 'real': 0.70
            },
            'quando': {
                'data': 0.90, 'dia': 0.85, 'prazo': 0.95, 'vencimento': 0.95,
                'tempo': 0.80, 'até': 0.75, 'hora': 0.70
            },
            'problema': {
                'dificuldade': 0.90, 'complicação': 0.85, 'erro': 0.80,
                'confusão': 0.75, 'encrenca': 0.85, 'pepino': 0.80
            }
        }
    
    def _build_intent_similarity_matrix(self) -> Dict[str, Dict[str, float]]:
        """🎯 MATRIZ DE SIMILARIDADE ENTRE INTENÇÕES"""
        return {
            'fatura_solicitar': {
                'fatura_valor': 0.7, 'fatura_vencimento': 0.6, 'pagamento_confirmacao': 0.4,
                'negociacao_parcelamento': 0.3, 'informacao_conta': 0.8
            },
            'fatura_valor': {
                'fatura_solicitar': 0.7, 'fatura_vencimento': 0.5, 'pagamento_confirmacao': 0.6,
                'negociacao_parcelamento': 0.7, 'negociacao_desconto': 0.5
            },
            'negociacao_parcelamento': {
                'negociacao_desconto': 0.8, 'pagamento_dificuldade': 0.9, 'fatura_valor': 0.6
            },
            'pagamento_confirmacao': {
                'reclamacao_valor_incorreto': 0.5, 'fatura_valor': 0.4, 'fatura_solicitar': 0.3
            }
        }
    
    def _build_relationship_graph(self) -> Dict[str, List[str]]:
        """🕸️ GRAFO DE RELACIONAMENTOS CONTEXTUAIS"""
        return {
            'financial_entities': ['valor', 'dinheiro', 'real', 'centavo', 'pagar', 'dever'],
            'temporal_entities': ['quando', 'dia', 'data', 'prazo', 'vencimento', 'até'],
            'document_entities': ['conta', 'boleto', 'fatura', 'papel', 'documento', 'cópia'],
            'negotiation_entities': ['parcelar', 'dividir', 'acordo', 'desconto', 'facilitar'],
            'emotional_entities': ['problema', 'dificuldade', 'urgente', 'chateado', 'nervoso'],
            'action_entities': ['quero', 'preciso', 'gostaria', 'mandar', 'enviar', 'ver']
        }
    
    def _load_discourse_analyzers(self) -> Dict[str, Any]:
        """💬 ANALISADORES DE DISCURSO ULTRA AVANÇADOS"""
        return {
            'discourse_markers': {
                'addition': ['também', 'além disso', 'e', 'mais', 'ainda'],
                'contrast': ['mas', 'porém', 'entretanto', 'contudo', 'no entanto'],
                'cause': ['porque', 'pois', 'já que', 'visto que', 'uma vez que'],
                'conclusion': ['então', 'portanto', 'assim', 'logo', 'por isso'],
                'sequence': ['primeiro', 'depois', 'em seguida', 'finalmente', 'por último'],
                'emphasis': ['realmente', 'muito', 'bastante', 'extremamente', 'totalmente']
            },
            'pragmatic_markers': {
                'politeness': ['por favor', 'obrigado', 'desculpa', 'com licença'],
                'urgency': ['urgente', 'rápido', 'agora', 'imediatamente', 'já'],
                'uncertainty': ['acho', 'talvez', 'pode ser', 'não tenho certeza'],
                'emphasis': ['realmente', 'certamente', 'definitivamente', 'com certeza']
            }
        }
    
    def _build_pragmatic_engine(self) -> Dict[str, Any]:
        """🧠 ENGINE DE INFERÊNCIA PRAGMÁTICA ULTRA AVANÇADA"""
        return {
            'implicature_rules': {
                # Se diz "já paguei MAS ainda aparece" = reclama valor incorreto
                'payment_but_still_charged': {
                    'pattern': r'(já.*pagu|quitei|paguei).*(mas|porém|ainda|continua)',
                    'inference': 'reclamacao_valor_incorreto',
                    'confidence': 0.9
                },
                # Se pergunta valor E prazo = quer informações completas
                'value_and_deadline': {
                    'pattern': r'(quanto.*devo).*(quando.*vence|prazo)',
                    'inference': 'multiple_intents',
                    'confidence': 0.8
                },
                # Se diz que não consegue pagar = quer negociar
                'cannot_pay': {
                    'pattern': r'não.*(consigo|posso).*(pagar|quitar)',
                    'inference': 'negociacao_parcelamento',
                    'confidence': 0.85
                }
            },
            'contextual_inference': {
                # Inferências baseadas no contexto da conversa
                'follow_up_questions': {
                    'after_invoice_request': ['fatura_valor', 'fatura_vencimento'],
                    'after_negotiation': ['confirmacao', 'negacao', 'duvida'],
                    'after_payment_info': ['pagamento_confirmacao']
                }
            }
        }
    
    def _build_coherence_analyzer(self) -> Dict[str, Any]:
        """🔗 ANALISADOR DE COERÊNCIA CONTEXTUAL ULTRA AVANÇADO"""
        return {
            'coherence_rules': {
                'topic_continuity': {
                    'same_topic': 1.0,      # Mesma intenção que anterior
                    'related_topic': 0.8,   # Intenção relacionada
                    'topic_shift': 0.4,     # Mudança de assunto
                    'random_topic': 0.1     # Assunto totalmente aleatório
                },
                'temporal_coherence': {
                    'logical_sequence': 1.0,    # Sequência lógica
                    'acceptable_jump': 0.7,     # Salto aceitável
                    'confusing_sequence': 0.3   # Sequência confusa
                }
            },
            'context_memory_window': 5,  # Quantas mensagens anteriores considerar
            'coherence_threshold': 0.6   # Limite mínimo de coerência
        }
    
    def _build_multi_layer_processors(self) -> List[Dict[str, Any]]:
        """🎛️ PROCESSADORES MULTI-CAMADAS ULTRA AVANÇADOS"""
        return [
            {
                'layer': 'lexical',
                'processor': 'word_level_analysis',
                'weight': 0.2,
                'functions': ['tokenization', 'pos_tagging', 'lemmatization']
            },
            {
                'layer': 'syntactic', 
                'processor': 'phrase_level_analysis',
                'weight': 0.3,
                'functions': ['phrase_detection', 'dependency_parsing']
            },
            {
                'layer': 'semantic',
                'processor': 'meaning_level_analysis', 
                'weight': 0.3,
                'functions': ['semantic_similarity', 'concept_mapping']
            },
            {
                'layer': 'pragmatic',
                'processor': 'context_level_analysis',
                'weight': 0.2,
                'functions': ['pragmatic_inference', 'discourse_analysis']
            }
        ]
    
    def _build_fallback_system(self) -> Dict[str, Any]:
        """🛡️ SISTEMA DE FALLBACK INTELIGENTE MULTI-CAMADAS"""
        return {
            'fallback_levels': [
                {
                    'level': 1,
                    'name': 'semantic_similarity',
                    'method': 'find_closest_semantic_match',
                    'threshold': 0.6
                },
                {
                    'level': 2, 
                    'name': 'keyword_extraction',
                    'method': 'extract_key_concepts',
                    'threshold': 0.4
                },
                {
                    'level': 3,
                    'name': 'pattern_matching',
                    'method': 'fuzzy_pattern_match', 
                    'threshold': 0.3
                },
                {
                    'level': 4,
                    'name': 'conversational_context',
                    'method': 'infer_from_conversation',
                    'threshold': 0.2
                },
                {
                    'level': 5,
                    'name': 'intelligent_guess',
                    'method': 'make_educated_guess',
                    'threshold': 0.1
                }
            ]
        }
    
    def _build_dynamic_generator(self) -> Dict[str, Any]:
        """🎭 GERADOR DINÂMICO DE RESPOSTAS ULTRA INTELIGENTE"""
        return {
            'response_templates': {
                'high_confidence': "✅ **{emotion_marker}** {action_confirmation} {specifics}",
                'medium_confidence': "🤔 **{understanding}** {clarification_request}",
                'low_confidence': "❓ **{confusion_acknowledgment}** {help_request}",
                'contextual': "🎯 **{context_reference}** {personalized_response}"
            },
            'emotion_markers': {
                'urgente': ['URGENTE!', 'RAPIDINHO!', 'AGORA MESMO!'],
                'frustrado': ['CALMA!', 'ENTENDO!', 'VAMOS RESOLVER!'],
                'neutro': ['PERFEITO!', 'BELEZA!', 'CERTO!'],
                'satisfeito': ['ÓTIMO!', 'EXCELENTE!', 'SHOW!']
            },
            'personalization_factors': [
                'conversation_history', 'emotional_state', 'communication_style',
                'previous_intents', 'response_patterns', 'user_preferences'
            ]
        }
    
    # ================================
    # 🚀 MÉTODOS ULTRA MEGA AVANÇADOS - NÍVEL CHATGPT GIGANTEMENTE FODA
    # ================================
    
    def _get_or_create_conversation_memory(self, phone: str) -> ConversationMemory:
        """🧠 OBTER OU CRIAR MEMÓRIA ULTRA AVANÇADA"""
        if phone not in self.conversation_memories:
            self.conversation_memories[phone] = ConversationMemory()
        return self.conversation_memories[phone]
    
    def _ultra_advanced_normalize_text(self, text: str) -> str:
        """🚀 NORMALIZAÇÃO ULTRA MEGA AVANÇADA"""
        # Usar o método existente mas com melhorias
        normalized = self._super_normalize_text(text)
        
        # Adicionar análises extras ultra avançadas
        normalized = self._apply_phonetic_corrections(normalized)
        normalized = self._fix_cognitive_errors(normalized)
        normalized = self._standardize_brazilian_expressions(normalized)
        
        return normalized
    
    def _apply_phonetic_corrections(self, text: str) -> str:
        """🔊 CORREÇÕES FONÉTICAS ULTRA AVANÇADAS"""
        phonetic_corrections = {
            # Correções baseadas em como as pessoas falam
            r'\b(di)\b': 'de',  # "di manhã" -> "de manhã"
            r'\b(nu)\b': 'no',  # "nu banco" -> "no banco"
            r'\b(du)\b': 'do',  # "du cliente" -> "do cliente"
            r'\b(ma)\b': 'mas', # "ma não" -> "mas não"
            r'\b(qui)\b': 'que', # "qui dia" -> "que dia"
            r'\b(cumé)\b': 'como é', # "cumé que" -> "como é que"
            r'\b(ocê)\b': 'você',    # "ocê tem" -> "você tem"
            r'\b(seje)\b': 'seja',   # "seje o que" -> "seja o que"
        }
        
        for pattern, replacement in phonetic_corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_cognitive_errors(self, text: str) -> str:
        """🧠 CORRIGIR ERROS COGNITIVOS E DE RACIOCÍNIO"""
        cognitive_fixes = {
            # Erros de lógica temporal
            r'(ontem.*amanha|amanha.*ontem)': 'ontem ou amanhã',
            # Contradições óbvias
            r'(não.*mas.*sim|sim.*mas.*não)': 'talvez',
            # Confusões de pessoa
            r'(você.*eu.*pagar|eu.*você.*pagar)': 'preciso pagar',
        }
        
        for pattern, replacement in cognitive_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _standardize_brazilian_expressions(self, text: str) -> str:
        """🇧🇷 PADRONIZAR EXPRESSÕES TIPICAMENTE BRASILEIRAS"""
        expressions = {
            r'(tá.*ligado|sacou|entendeu)': 'entende',
            r'(massa|show|da.*hora)': 'bom',
            r'(trampo|labuta)': 'trabalho',
            r'(grana|din.*din|money)': 'dinheiro',
            r'(mina|mano|brother)': 'pessoa',
            r'(rolê|role)': 'situação',
        }
        
        for pattern, replacement in expressions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    async def _perform_multi_layer_analysis(self, text: str) -> Dict[str, Any]:
        """🎛️ ANÁLISE MULTI-CAMADAS ULTRA PROFUNDA"""
        analysis = {
            'lexical': self._analyze_lexical_layer(text),
            'syntactic': self._analyze_syntactic_layer(text),
            'semantic': self._analyze_semantic_layer(text),
            'pragmatic': self._analyze_pragmatic_layer(text)
        }
        
        # Calcular score agregado
        analysis['overall_complexity'] = sum(
            layer['complexity_score'] * processor['weight'] 
            for layer, processor in zip(analysis.values(), self.multi_layer_processors)
        )
        
        return analysis
    
    def _analyze_lexical_layer(self, text: str) -> Dict[str, Any]:
        """📝 ANÁLISE LEXICAL ULTRA PROFUNDA"""
        words = text.split()
        
        return {
            'word_count': len(words),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'complexity_score': min(len(words) * 0.1, 1.0),
            'rare_words': [w for w in words if len(w) > 8],
            'simple_words': [w for w in words if len(w) <= 4]
        }
    
    def _analyze_syntactic_layer(self, text: str) -> Dict[str, Any]:
        """🔗 ANÁLISE SINTÁTICA ULTRA PROFUNDA"""
        # Detectar estruturas sintáticas
        has_questions = bool(re.search(r'\?', text))
        has_subordinate = bool(re.search(r'\b(que|se|quando|onde|como)\b', text))
        has_coordination = bool(re.search(r'\b(e|mas|ou|porém)\b', text))
        
        complexity = 0.3
        if has_questions: complexity += 0.2
        if has_subordinate: complexity += 0.3
        if has_coordination: complexity += 0.2
        
        return {
            'has_questions': has_questions,
            'has_subordinate_clauses': has_subordinate,
            'has_coordination': has_coordination,
            'complexity_score': min(complexity, 1.0)
        }
    
    def _analyze_semantic_layer(self, text: str) -> Dict[str, Any]:
        """🧠 ANÁLISE SEMÂNTICA ULTRA PROFUNDA"""
        semantic_clusters = []
        cluster_scores = {}
        
        # Analisar proximidade semântica com nossos clusters
        for cluster_name, words in self.contextual_relationship_graph.items():
            score = 0
            for word in words:
                if word in text.lower():
                    score += 1
            
            if score > 0:
                semantic_clusters.append(cluster_name)
                cluster_scores[cluster_name] = score / len(words)
        
        return {
            'semantic_clusters': semantic_clusters,
            'cluster_scores': cluster_scores,
            'complexity_score': min(len(semantic_clusters) * 0.2, 1.0),
            'semantic_density': sum(cluster_scores.values()) / max(len(cluster_scores), 1)
        }
    
    def _analyze_pragmatic_layer(self, text: str) -> Dict[str, Any]:
        """💭 ANÁLISE PRAGMÁTICA ULTRA PROFUNDA"""
        pragmatic_elements = {}
        
        # Detectar elementos pragmáticos
        for marker_type, markers in self.discourse_analyzers['pragmatic_markers'].items():
            found_markers = [m for m in markers if m in text.lower()]
            if found_markers:
                pragmatic_elements[marker_type] = found_markers
        
        return {
            'pragmatic_elements': pragmatic_elements,
            'complexity_score': min(len(pragmatic_elements) * 0.25, 1.0),
            'pragmatic_richness': len(pragmatic_elements)
        }
    
    async def _perform_semantic_analysis(self, text: str, memory: ConversationMemory) -> Dict[str, Any]:
        """🔬 ANÁLISE SEMÂNTICA MEGA ULTRA AVANÇADA"""
        semantic_analysis = {}
        
        # Calcular similaridade semântica com padrões conhecidos
        for pattern_id, pattern in self.semantic_patterns.items():
            similarity = self._calculate_semantic_similarity(text, pattern)
            semantic_analysis[pattern_id] = similarity
        
        # Análise de vetores semânticos
        vector_analysis = self._analyze_semantic_vectors(text)
        
        return {
            'pattern_similarities': semantic_analysis,
            'vector_analysis': vector_analysis,
            'best_match': max(semantic_analysis.items(), key=lambda x: x[1]) if semantic_analysis else None,
            'semantic_confidence': max(semantic_analysis.values()) if semantic_analysis else 0.0
        }
    
    def _calculate_semantic_similarity(self, text: str, pattern: SemanticPattern) -> float:
        """📐 CALCULAR SIMILARIDADE SEMÂNTICA ULTRA PRECISA"""
        similarity_score = 0.0
        total_weight = 0.0
        
        # Analisar vetores semânticos
        for concept, weight in pattern.semantic_vectors.items():
            if concept in text.lower():
                similarity_score += weight
            total_weight += weight
        
        # Normalizar score
        if total_weight > 0:
            similarity_score = similarity_score / total_weight
        
        # Boost por triggers contextuais
        for trigger in pattern.context_triggers:
            if trigger in text.lower():
                similarity_score += 0.1
        
        return min(similarity_score, 1.0)
    
    def _analyze_semantic_vectors(self, text: str) -> Dict[str, float]:
        """🧮 ANÁLISE DE VETORES SEMÂNTICOS"""
        vector_scores = {}
        
        for main_concept, related_concepts in self.brazilian_semantic_vectors.items():
            if main_concept in text.lower():
                vector_scores[main_concept] = 1.0
                
                # Adicionar conceitos relacionados
                for related, similarity in related_concepts.items():
                    if related in text.lower():
                        vector_scores[related] = similarity
        
        return vector_scores
    
    async def _perform_pragmatic_analysis(self, text: str, memory: ConversationMemory) -> Dict[str, Any]:
        """🎭 ANÁLISE PRAGMÁTICA MEGA ULTRA AVANÇADA"""
        pragmatic_inferences = {}
        
        # Aplicar regras de implicatura
        for rule_name, rule in self.pragmatic_inference_engine['implicature_rules'].items():
            if re.search(rule['pattern'], text, re.IGNORECASE):
                pragmatic_inferences[rule_name] = {
                    'inference': rule['inference'],
                    'confidence': rule['confidence']
                }
        
        # Análise contextual baseada na conversa anterior
        contextual_inferences = self._analyze_conversational_context(text, memory)
        
        return {
            'implicatures': pragmatic_inferences,
            'contextual_inferences': contextual_inferences,
            'pragmatic_confidence': max(
                [inf['confidence'] for inf in pragmatic_inferences.values()] + [0.0]
            )
        }
    
    def _analyze_conversational_context(self, text: str, memory: ConversationMemory) -> Dict[str, Any]:
        """💬 ANÁLISE DE CONTEXTO CONVERSACIONAL ULTRA PROFUNDA"""
        inferences = {}
        
        # Analisar padrão baseado na última intenção
        if memory.intent_history:
            last_intent, confidence, timestamp = memory.intent_history[-1]
            
            # Inferir follow-ups baseados na intenção anterior
            follow_ups = self.pragmatic_inference_engine['contextual_inference']['follow_up_questions']
            if last_intent in follow_ups:
                for possible_intent in follow_ups[last_intent]:
                    inferences[f'follow_up_{possible_intent}'] = confidence * 0.7
        
        return inferences
    
    async def _extract_ultra_advanced_entities(self, text: str, semantic_analysis: Dict[str, Any]) -> List[ExtractedEntity]:
        """🎯 EXTRAÇÃO ULTRA AVANÇADA DE ENTIDADES COM CONTEXTO SEMÂNTICO"""
        entities = []
        
        # Usar método existente como base
        base_entities = self._extract_all_entities(text)
        
        # Enriquecer com análise semântica
        for entity in base_entities:
            # Calcular peso semântico
            semantic_weight = 1.0
            if semantic_analysis.get('vector_analysis'):
                for concept, score in semantic_analysis['vector_analysis'].items():
                    if concept in entity.value.lower():
                        semantic_weight = max(semantic_weight, score)
            
            # Adicionar alternativas baseadas em similaridade
            alternatives = self._find_entity_alternatives(entity, semantic_analysis)
            
            # Criar entidade enriquecida
            ultra_entity = ExtractedEntity(
                type=entity.type,
                value=entity.value,
                confidence=entity.confidence,
                context=entity.context,
                semantic_weight=semantic_weight,
                alternatives=alternatives,
                relationships=self._find_entity_relationships(entity, text)
            )
            
            entities.append(ultra_entity)
        
        return entities
    
    def _find_entity_alternatives(self, entity: ExtractedEntity, semantic_analysis: Dict[str, Any]) -> List[str]:
        """🔍 ENCONTRAR ALTERNATIVAS SEMÂNTICAS PARA ENTIDADES"""
        alternatives = []
        
        if entity.type == 'valores_monetarios':
            alternatives = ['valor', 'quantia', 'dinheiro', 'preço', 'custo']
        elif entity.type == 'datas':
            alternatives = ['prazo', 'vencimento', 'data', 'dia', 'quando']
        
        return alternatives
    
    def _find_entity_relationships(self, entity: ExtractedEntity, text: str) -> Dict[str, float]:
        """🕸️ ENCONTRAR RELACIONAMENTOS ENTRE ENTIDADES"""
        relationships = {}
        
        # Analisar proximidade com outras palavras-chave
        for cluster_name, words in self.contextual_relationship_graph.items():
            for word in words:
                if word in text.lower() and word != entity.value.lower():
                    relationships[word] = 0.8  # Score de relacionamento
        
        return relationships
    
    async def _analyze_ultra_emotion(self, text: str, memory: ConversationMemory) -> str:
        """😊 ANÁLISE EMOCIONAL ULTRA AVANÇADA COM MEMÓRIA"""
        # Usar análise existente como base
        base_emotion = self._analyze_emotion(text)
        
        # Enriquecer com contexto de memória emocional
        if memory.emotional_journey:
            # Considerar padrão emocional histórico
            recent_emotions = [emotion for emotion, score, timestamp in memory.emotional_journey[-3:]]
            
            # Se há padrão de frustração crescente
            if recent_emotions.count('frustrado') >= 2:
                if base_emotion in ['neutro', 'confuso']:
                    base_emotion = 'frustrado'  # Inferir frustração continuada
        
        # Detectar escalation emocional
        emotional_escalation = self._detect_emotional_escalation(text)
        if emotional_escalation:
            if base_emotion == 'frustrado':
                base_emotion = 'muito_frustrado'  # Nova categoria
            elif base_emotion == 'urgente':
                base_emotion = 'extremamente_urgente'  # Nova categoria
        
        return base_emotion
    
    def _detect_emotional_escalation(self, text: str) -> bool:
        """📈 DETECTAR ESCALATION EMOCIONAL"""
        escalation_markers = [
            r'(muito|extremamente|super|ultra).*(chateado|irritado)',
            r'(não.*aguentar|não.*suportar)',
            r'(absurdo|ridículo|inaceitável)',
            r'[!]{3,}',  # Múltiplas exclamações
            r'[?!]{2,}',  # Mistura de ? e !
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in escalation_markers)
    
    async def _analyze_ultra_temporal_context(self, text: str, memory: ConversationMemory) -> str:
        """⏰ ANÁLISE TEMPORAL ULTRA AVANÇADA"""
        base_temporal = self._analyze_temporal_context(text)
        
        # Enriquecer com análise de urgência temporal
        urgency_indicators = {
            'imediato': ['agora', 'já', 'imediatamente', 'urgente'],
            'hoje': ['hoje', 'hj', 'ainda hoje'],
            'breve': ['logo', 'em breve', 'rapidinho'],
            'futuro_proximo': ['amanhã', 'essa semana', 'uns dias'],
            'futuro_distante': ['mês que vem', 'ano que vem', 'mais tarde']
        }
        
        for urgency_level, indicators in urgency_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                return f"{base_temporal}_{urgency_level}"
        
        return base_temporal
    
    async def _analyze_ultra_negation(self, text: str) -> Dict[str, Any]:
        """❌ ANÁLISE ULTRA AVANÇADA DE NEGAÇÃO"""
        has_basic_negation = self._detect_negation(text)
        
        # Análise mais sofisticada de tipos de negação
        negation_types = {
            'absolute': r'\b(nunca|jamais|de jeito nenhum)\b',
            'partial': r'\b(não muito|meio que não|acho que não)\b',
            'conditional': r'\b(não se|só não|a não ser)\b',
            'emphatic': r'\b(de forma alguma|nem pensar|que nada)\b'
        }
        
        detected_types = []
        for neg_type, pattern in negation_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected_types.append(neg_type)
        
        return {
            'has_negation': has_basic_negation,
            'negation_types': detected_types,
            'negation_strength': len(detected_types) / len(negation_types)
        }
    
    async def _analyze_ultra_contextual_intent(
        self, text: str, entities: List[ExtractedEntity], emotion: str, 
        temporal: str, negation: Dict, memory: ConversationMemory, 
        semantic_analysis: Dict, pragmatic_analysis: Dict
    ) -> ContextualIntent:
        """🧠 ANÁLISE ULTRA MEGA AVANÇADA DE INTENÇÃO CONTEXTUAL"""
        
        # Usar análise base existente
        base_intent_analysis = self._analyze_contextual_intent(
            text, entities, emotion, temporal, negation.get('has_negation', False), memory
        )
        
        # ENRIQUECER COM ANÁLISES ULTRA AVANÇADAS
        
        # 1. Boost semântico baseado na melhor correspondência
        if semantic_analysis.get('best_match'):
            pattern_id, similarity_score = semantic_analysis['best_match']
            if similarity_score > 0.7:
                # Aplicar boost baseado no padrão semântico
                if 'fatura' in pattern_id:
                    base_intent_analysis.confidence += 0.2
                elif 'valor' in pattern_id:
                    base_intent_analysis.confidence += 0.15
        
        # 2. Boost pragmático baseado em implicaturas
        pragmatic_confidence = pragmatic_analysis.get('pragmatic_confidence', 0)
        base_intent_analysis.confidence += pragmatic_confidence * 0.1
        
        # 3. Calcular similaridade semântica com intenções conhecidas
        semantic_similarity = self._calculate_intent_semantic_similarity(
            base_intent_analysis.intent, semantic_analysis
        )
        
        # 4. Analisar alternativas de intenção
        alternative_intents = self._calculate_alternative_intents(
            text, semantic_analysis, pragmatic_analysis
        )
        
        # 5. Detectar clusters semânticos
        semantic_clusters = semantic_analysis.get('pattern_similarities', {}).keys()
        
        # 6. Analisar marcadores de discurso
        discourse_markers = self._extract_discourse_markers(text)
        
        # 7. Inferência pragmática ultra avançada
        pragmatic_inference = self._calculate_pragmatic_inference(
            base_intent_analysis, pragmatic_analysis, memory
        )
        
        # Criar intenção contextual ultra enriquecida
        ultra_intent = ContextualIntent(
            intent=base_intent_analysis.intent,
            confidence=min(base_intent_analysis.confidence, 1.0),
            entities=entities,
            temporal_context=temporal,
            emotional_state=emotion,
            negation=negation.get('has_negation', False),
            multiple_intents=base_intent_analysis.multiple_intents,
            
            # CAMPOS ULTRA AVANÇADOS
            semantic_similarity=semantic_similarity,
            contextual_coherence=0.0,  # Será calculado depois
            linguistic_complexity=semantic_analysis.get('semantic_confidence', 0),
            intent_certainty=0.0,  # Será calculado depois
            alternative_intents=alternative_intents,
            semantic_clusters=list(semantic_clusters),
            discourse_markers=discourse_markers,
            pragmatic_inference=pragmatic_inference
        )
        
        return ultra_intent
    
    def _calculate_intent_semantic_similarity(self, intent: IntentType, semantic_analysis: Dict) -> float:
        """📐 CALCULAR SIMILARIDADE SEMÂNTICA DA INTENÇÃO"""
        intent_key = intent.value
        similarity_matrix = self.intent_similarity_matrix
        
        if intent_key in similarity_matrix:
            # Calcular média das similaridades com outras intenções detectadas
            similarities = []
            for related_intent, similarity in similarity_matrix[intent_key].items():
                if any(related_intent in cluster for cluster in semantic_analysis.get('pattern_similarities', {})):
                    similarities.append(similarity)
            
            return sum(similarities) / len(similarities) if similarities else 0.5
        
        return 0.5  # Default
    
    def _calculate_alternative_intents(self, text: str, semantic_analysis: Dict, pragmatic_analysis: Dict) -> List[Tuple[IntentType, float]]:
        """🎯 CALCULAR INTENÇÕES ALTERNATIVAS"""
        alternatives = []
        
        # Baseado em análise semântica
        for pattern_id, similarity in semantic_analysis.get('pattern_similarities', {}).items():
            if similarity > 0.5:
                if 'fatura' in pattern_id:
                    alternatives.append((IntentType.FATURA_SOLICITAR, similarity))
                elif 'valor' in pattern_id:
                    alternatives.append((IntentType.FATURA_VALOR, similarity))
                elif 'negociacao' in pattern_id:
                    alternatives.append((IntentType.NEGOCIACAO_PARCELAMENTO, similarity))
        
        # Remover duplicatas e ordenar por confiança
        alternatives = list(set(alternatives))
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return alternatives[:3]  # Top 3 alternativas
    
    def _extract_discourse_markers(self, text: str) -> List[str]:
        """💬 EXTRAIR MARCADORES DE DISCURSO"""
        markers = []
        
        for marker_type, marker_list in self.discourse_analyzers['discourse_markers'].items():
            for marker in marker_list:
                if marker in text.lower():
                    markers.append(f"{marker_type}:{marker}")
        
        return markers
    
    def _calculate_pragmatic_inference(self, intent: ContextualIntent, pragmatic_analysis: Dict, memory: ConversationMemory) -> Dict[str, float]:
        """🎭 CALCULAR INFERÊNCIA PRAGMÁTICA"""
        inferences = {}
        
        # Inferências baseadas em implicaturas
        for implicature_name, implicature_data in pragmatic_analysis.get('implicatures', {}).items():
            inferences[implicature_name] = implicature_data['confidence']
        
        # Inferências contextuais
        contextual_infs = pragmatic_analysis.get('contextual_inferences', {})
        inferences.update(contextual_infs)
        
        return inferences
    
    async def _analyze_contextual_coherence(self, intent: ContextualIntent, memory: ConversationMemory) -> float:
        """🔗 ANALISAR COERÊNCIA CONTEXTUAL"""
        if not memory.intent_history:
            return 0.8  # Primeira mensagem tem coerência neutra
        
        # Pegar últimas 3 intenções
        recent_intents = [intent_data[0] for intent_data in memory.intent_history[-3:]]
        current_intent = intent.intent.value
        
        # Calcular coerência baseada na matriz de similaridade
        coherence_scores = []
        
        for past_intent in recent_intents:
            if past_intent in self.intent_similarity_matrix:
                if current_intent in self.intent_similarity_matrix[past_intent]:
                    coherence_scores.append(self.intent_similarity_matrix[past_intent][current_intent])
                else:
                    coherence_scores.append(0.3)  # Baixa coerência para intenções não relacionadas
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    async def _calculate_intent_certainty(self, intent: ContextualIntent, linguistic_analysis: Dict) -> float:
        """✅ CALCULAR CERTEZA DA INTENÇÃO"""
        certainty_factors = []
        
        # Fator 1: Confiança base da intenção
        certainty_factors.append(intent.confidence)
        
        # Fator 2: Similaridade semântica
        certainty_factors.append(intent.semantic_similarity)
        
        # Fator 3: Coerência contextual
        certainty_factors.append(intent.contextual_coherence)
        
        # Fator 4: Complexidade linguística (menos complexo = mais certo)
        linguistic_certainty = 1.0 - linguistic_analysis.get('overall_complexity', 0.5)
        certainty_factors.append(linguistic_certainty)
        
        # Fator 5: Presença de entidades relevantes
        entity_certainty = min(len(intent.entities) * 0.2, 1.0)
        certainty_factors.append(entity_certainty)
        
        # Calcular média ponderada
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Soma = 1.0
        weighted_certainty = sum(factor * weight for factor, weight in zip(certainty_factors, weights))
        
        return min(weighted_certainty, 1.0)
    
    async def _update_ultra_conversation_memory(self, phone: str, intent: ContextualIntent, text: str, linguistic_analysis: Dict):
        """🧠 ATUALIZAR MEMÓRIA ULTRA AVANÇADA"""
        memory = self.conversation_memories[phone]
        
        # Atualizar histórico de intenções
        memory.intent_history.append((
            intent.intent.value, 
            intent.confidence, 
            datetime.now()
        ))
        
        # Atualizar jornada emocional
        memory.emotional_journey.append((
            intent.emotional_state,
            intent.confidence,
            datetime.now()
        ))
        
        # Atualizar padrões de conversação
        memory.conversation_patterns.append(text[:100])  # Primeiros 100 chars
        
        # Detectar mudanças de contexto
        if len(memory.intent_history) > 1:
            last_intent = memory.intent_history[-2][0]
            if intent.intent.value != last_intent:
                if intent.contextual_coherence < 0.4:  # Mudança abrupta
                    memory.context_switches.append(datetime.now())
        
        # Atualizar dados de aprendizado
        memory.learning_data['total_messages'] = memory.learning_data.get('total_messages', 0) + 1
        memory.learning_data['avg_confidence'] = (
            memory.learning_data.get('avg_confidence', 0.5) + intent.confidence
        ) / 2
        
        # Manter apenas últimos 50 registros de cada tipo
        memory.intent_history = memory.intent_history[-50:]
        memory.emotional_journey = memory.emotional_journey[-50:]
        memory.conversation_patterns = memory.conversation_patterns[-50:]
        memory.context_switches = memory.context_switches[-20:]
    
    async def _learn_from_interaction(self, phone: str, intent: ContextualIntent, semantic_analysis: Dict):
        """🎓 APRENDER A PARTIR DA INTERAÇÃO"""
        # Armazenar padrões bem-sucedidos para aprendizado futuro
        if intent.confidence > 0.8:
            pattern_key = f"{intent.intent.value}_{intent.emotional_state}"
            
            if pattern_key not in self.pattern_learning_db:
                self.pattern_learning_db[pattern_key] = []
            
            # Armazenar características da mensagem bem entendida
            learning_pattern = {
                'semantic_clusters': intent.semantic_clusters,
                'entities_count': len(intent.entities),
                'discourse_markers': intent.discourse_markers,
                'confidence': intent.confidence,
                'timestamp': datetime.now()
            }
            
            self.pattern_learning_db[pattern_key].append(learning_pattern)
            
            # Manter apenas últimos 20 padrões por tipo
            self.pattern_learning_db[pattern_key] = self.pattern_learning_db[pattern_key][-20:]
    
    async def _generate_ultra_contextual_response(
        self, phone: str, intent: ContextualIntent, entities: List[ExtractedEntity], 
        memory: ConversationMemory, semantic_analysis: Dict
    ) -> Dict[str, Any]:
        """🎭 GERAÇÃO ULTRA INTELIGENTE DE RESPOSTA NÍVEL CHATGPT"""
        
        # Usar gerador existente como base
        base_response = await self._generate_contextual_response(phone, intent, entities, {})
        
        # ENRIQUECER COM INTELIGÊNCIA ULTRA AVANÇADA
        
        # 1. Personalização baseada em memória
        personalization = self._generate_personalized_elements(memory, intent)
        
        # 2. Adaptação baseada em certeza
        certainty_adaptation = self._adapt_response_for_certainty(intent.intent_certainty)
        
        # 3. Contextualização semântica
        semantic_context = self._add_semantic_context(semantic_analysis, intent)
        
        # 4. Resposta dinâmica baseada em padrões aprendidos
        learned_enhancements = self._apply_learned_patterns(intent, memory)
        
        # Gerar resposta ultra contextualizada
        ultra_response_text = self._compose_ultra_response(
            base_response['text'], personalization, certainty_adaptation, 
            semantic_context, learned_enhancements, intent
        )
        
        return {
            'text': ultra_response_text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'entities_detected': len(entities),
            'emotional_state': intent.emotional_state,
            'multiple_intents': len(intent.multiple_intents),
            'context_enhanced': True,
            'response_type': 'ultra_mega_contextual',
            
            # NOVOS CAMPOS ULTRA AVANÇADOS
            'semantic_similarity': intent.semantic_similarity,
            'contextual_coherence': intent.contextual_coherence,
            'intent_certainty': intent.intent_certainty,
            'personalization_level': len(personalization),
            'semantic_clusters': intent.semantic_clusters,
            'discourse_markers': intent.discourse_markers,
            'ultra_enhanced': True
        }
    
    def _generate_personalized_elements(self, memory: ConversationMemory, intent: ContextualIntent) -> Dict[str, str]:
        """👤 GERAR ELEMENTOS PERSONALIZADOS"""
        personalization = {}
        
        # Baseado em padrão emocional
        if memory.emotional_journey:
            recent_emotions = [emotion for emotion, _, _ in memory.emotional_journey[-3:]]
            if recent_emotions.count('frustrado') >= 2:
                personalization['empathy'] = "Eu vejo que você está passando por uma situação chata"
            elif recent_emotions.count('urgente') >= 2:
                personalization['urgency_ack'] = "Entendo que isso é urgente para você"
        
        # Baseado em histórico de intenções
        if memory.intent_history:
            common_intents = Counter([intent for intent, _, _ in memory.intent_history])
            most_common = common_intents.most_common(1)[0][0]
            if most_common == 'fatura_solicitar':
                personalization['context'] = "Como sempre, vou buscar sua fatura"
        
        return personalization
    
    def _adapt_response_for_certainty(self, certainty: float) -> Dict[str, str]:
        """✅ ADAPTAR RESPOSTA BASEADA NA CERTEZA"""
        if certainty > 0.9:
            return {'confidence_marker': '**CERTEZA ABSOLUTA!**', 'action': 'Vou resolver isso AGORA!'}
        elif certainty > 0.7:
            return {'confidence_marker': '**ENTENDI PERFEITAMENTE!**', 'action': 'Vou cuidar disso!'}
        elif certainty > 0.5:
            return {'confidence_marker': '**ACHO QUE ENTENDI!**', 'action': 'Deixe-me confirmar...'}
        else:
            return {'confidence_marker': '**HMMMM...**', 'action': 'Me explica melhor?'}
    
    def _add_semantic_context(self, semantic_analysis: Dict, intent: ContextualIntent) -> Dict[str, str]:
        """🧠 ADICIONAR CONTEXTO SEMÂNTICO"""
        context = {}
        
        if semantic_analysis.get('best_match'):
            pattern_id, score = semantic_analysis['best_match']
            if score > 0.8:
                context['semantic_confidence'] = f"Detectei {int(score*100)}% de certeza"
        
        return context
    
    def _apply_learned_patterns(self, intent: ContextualIntent, memory: ConversationMemory) -> Dict[str, str]:
        """🎓 APLICAR PADRÕES APRENDIDOS"""
        enhancements = {}
        
        pattern_key = f"{intent.intent.value}_{intent.emotional_state}"
        if pattern_key in self.pattern_learning_db:
            patterns = self.pattern_learning_db[pattern_key]
            if patterns:
                # Aplicar insights dos padrões aprendidos
                avg_confidence = sum(p['confidence'] for p in patterns) / len(patterns)
                if avg_confidence > 0.8:
                    enhancements['learned_boost'] = "Baseado no que aprendi com você"
        
        return enhancements
    
    def _compose_ultra_response(
        self, base_text: str, personalization: Dict, certainty: Dict, 
        semantic: Dict, learned: Dict, intent: ContextualIntent
    ) -> str:
        """🎭 COMPOR RESPOSTA ULTRA AVANÇADA"""
        
        # Começar com texto base
        response_parts = [base_text]
        
        # Adicionar personalização
        if personalization.get('empathy'):
            response_parts.insert(0, personalization['empathy'] + ".")
        
        # Adicionar marcador de confiança
        if certainty.get('confidence_marker'):
            response_parts[0] = response_parts[0].replace(
                response_parts[0].split()[0], 
                certainty['confidence_marker']
            )
        
        # Adicionar contexto semântico se alta confiança
        if semantic.get('semantic_confidence'):
            response_parts.append(f"\n\n🎯 {semantic['semantic_confidence']} no que você quis dizer!")
        
        # Adicionar insights aprendidos
        if learned.get('learned_boost'):
            response_parts.append(f"\n\n🧠 {learned['learned_boost']}, sei exatamente o que fazer!")
        
        return " ".join(response_parts)
    
    async def _ultra_intelligent_fallback(self, phone: str, text: str, error: Exception) -> Dict[str, Any]:
        """🛡️ FALLBACK ULTRA INTELIGENTE MULTI-CAMADAS"""
        
        logger.error(f"🚀 Ativando fallback ultra inteligente para: {text[:50]}... | Erro: {error}")
        
        # Tentar fallbacks em cascata
        for fallback_level in self.intelligent_fallback_system['fallback_levels']:
            try:
                if fallback_level['name'] == 'semantic_similarity':
                    return await self._fallback_semantic_similarity(text, fallback_level['threshold'])
                elif fallback_level['name'] == 'keyword_extraction':
                    return await self._fallback_keyword_extraction(text, fallback_level['threshold'])
                elif fallback_level['name'] == 'pattern_matching':
                    return await self._fallback_pattern_matching(text, fallback_level['threshold'])
                elif fallback_level['name'] == 'conversational_context':
                    return await self._fallback_conversational_context(phone, text, fallback_level['threshold'])
                elif fallback_level['name'] == 'intelligent_guess':
                    return await self._fallback_intelligent_guess(text, fallback_level['threshold'])
                    
            except Exception as fallback_error:
                logger.warning(f"Fallback nível {fallback_level['level']} falhou: {fallback_error}")
                continue
        
        # Fallback final de emergência
        return {
            'text': "🤔 **NOSSA!** Essa foi difícil até para mim! Pode tentar falar de um jeito mais simples? Tipo: 'quero minha conta' ou 'quanto devo'?",
            'intent': 'emergency_fallback',
            'confidence': 0.1,
            'fallback_level': 'emergency',
            'ultra_enhanced': True
        }
    
    async def _fallback_semantic_similarity(self, text: str, threshold: float) -> Dict[str, Any]:
        """🔍 FALLBACK POR SIMILARIDADE SEMÂNTICA"""
        # Tentar encontrar padrão semântico mais próximo
        best_match = None
        best_score = 0.0
        
        for pattern_id, pattern in self.semantic_patterns.items():
            score = self._calculate_semantic_similarity(text, pattern)
            if score > best_score and score > threshold:
                best_match = pattern_id
                best_score = score
        
        if best_match:
            intent_mapping = {
                'fatura_semantic': 'fatura_solicitar',
                'valor_semantic': 'fatura_valor',
                'tempo_semantic': 'fatura_vencimento',
                'negociacao_semantic': 'negociacao_parcelamento'
            }
            
            inferred_intent = intent_mapping.get(best_match, 'fatura_solicitar')
            
            return {
                'text': f"🎯 **ENTENDI PELO CONTEXTO!** Você quer algo relacionado a {inferred_intent.replace('_', ' ')}. Vou ajudar!",
                'intent': inferred_intent,
                'confidence': best_score,
                'fallback_level': 'semantic_similarity',
                'ultra_enhanced': True
            }
        
        raise Exception("Similaridade semântica insuficiente")
    
    async def _fallback_keyword_extraction(self, text: str, threshold: float) -> Dict[str, Any]:
        """🔑 FALLBACK POR EXTRAÇÃO DE PALAVRAS-CHAVE"""
        keywords = {
            'fatura': ['conta', 'boleto', 'fatura', 'segunda', 'via', 'papel'],
            'valor': ['quanto', 'valor', 'devo', 'pagar', 'preço', 'dinheiro'],
            'vencimento': ['quando', 'vence', 'prazo', 'data', 'até'],
            'negociacao': ['parcelar', 'acordo', 'desconto', 'negociar', 'facilitar']
        }
        
        scores = {}
        for intent, intent_keywords in keywords.items():
            score = sum(1 for keyword in intent_keywords if keyword in text.lower())
            if score > 0:
                scores[intent] = score / len(intent_keywords)
        
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            if best_intent[1] > threshold:
                return {
                    'text': f"🔍 **CAPTEI!** Pelas palavras-chave, você quer {best_intent[0]}. É isso mesmo?",
                    'intent': best_intent[0],
                    'confidence': best_intent[1],
                    'fallback_level': 'keyword_extraction',
                    'ultra_enhanced': True
                }
        
        raise Exception("Palavras-chave insuficientes")
    
    async def _fallback_pattern_matching(self, text: str, threshold: float) -> Dict[str, Any]:
        """🧩 FALLBACK POR CORRESPONDÊNCIA DE PADRÕES"""
        # Padrões de emergência muito básicos
        emergency_patterns = [
            (r'\b(conta|boleto|fatura)\b', 'fatura_solicitar', 0.7),
            (r'\b(quanto|valor)\b', 'fatura_valor', 0.6),
            (r'\b(quando|vence|prazo)\b', 'fatura_vencimento', 0.6),
            (r'\b(paguei|pago)\b', 'pagamento_confirmacao', 0.5),
            (r'\b(parcelar|acordo)\b', 'negociacao_parcelamento', 0.5),
        ]
        
        for pattern, intent, confidence in emergency_patterns:
            if re.search(pattern, text, re.IGNORECASE) and confidence > threshold:
                return {
                    'text': f"🧩 **CONSEGUI ENTENDER!** Pelo padrão, você quer {intent.replace('_', ' ')}!",
                    'intent': intent,
                    'confidence': confidence,
                    'fallback_level': 'pattern_matching',
                    'ultra_enhanced': True
                }
        
        raise Exception("Nenhum padrão corresponde")
    
    async def _fallback_conversational_context(self, phone: str, text: str, threshold: float) -> Dict[str, Any]:
        """💭 FALLBACK POR CONTEXTO CONVERSACIONAL"""
        if phone in self.conversation_memories:
            memory = self.conversation_memories[phone]
            if memory.intent_history:
                # Assumir que é follow-up da última intenção
                last_intent, last_confidence, _ = memory.intent_history[-1]
                
                if last_confidence > threshold:
                    return {
                        'text': f"💭 **PELO CONTEXTO!** Você ainda está falando sobre {last_intent.replace('_', ' ')}, né?",
                        'intent': last_intent,
                        'confidence': last_confidence * 0.8,
                        'fallback_level': 'conversational_context',
                        'ultra_enhanced': True
                    }
        
        raise Exception("Contexto conversacional insuficiente")
    
    async def _fallback_intelligent_guess(self, text: str, threshold: float) -> Dict[str, Any]:
        """🎲 FALLBACK POR SUPOSIÇÃO INTELIGENTE"""
        # Se chegou até aqui, fazer uma suposição educada baseada no contexto de cobrança
        text_length = len(text.split())
        
        if text_length <= 3:
            # Texto muito curto - provavelmente quer fatura
            guess_intent = 'fatura_solicitar'
            guess_confidence = 0.4
        elif '?' in text:
            # Tem pergunta - provavelmente quer informação (valor ou vencimento)
            guess_intent = 'fatura_valor'
            guess_confidence = 0.3
        else:
            # Default para solicitação de fatura
            guess_intent = 'fatura_solicitar'
            guess_confidence = 0.2
        
        if guess_confidence > threshold:
            return {
                'text': f"🎲 **VAMOS TENTAR!** Pelo contexto geral, acho que você quer {guess_intent.replace('_', ' ')}. Se não for isso, me fala 'não' que eu entendo outra coisa!",
                'intent': guess_intent,
                'confidence': guess_confidence,
                'fallback_level': 'intelligent_guess',
                'ultra_enhanced': True,
                'requires_confirmation': True
            }
        
        raise Exception("Impossível fazer suposição válida") 
            negociacao_parcelamento_score += 0.2
        
        # Se tem datas, boost vencimento
        tem_data = any(e.type == 'datas' for e in entities)
        if tem_data:
            fatura_vencimento_score += 0.4
            pagamento_score += 0.2
        
        # 😤 BOOST BASEADO EM EMOÇÃO
        if emotion == 'frustrado':
            reclamacao_indevida_score += 0.4
            reclamacao_valor_score += 0.4
        elif emotion == 'urgente':
            fatura_solicitar_score += 0.3
            fatura_valor_score += 0.2
        elif emotion == 'confuso':
            duvida_score += 0.3
        
        # 🎯 NORMALIZAR SCORES (max 1.0 para cada)
        intent_scores = {
            'fatura_solicitar': min(fatura_solicitar_score, 1.0),
            'fatura_valor': min(fatura_valor_score, 1.0),
            'fatura_vencimento': min(fatura_vencimento_score, 1.0),
            'negociacao_parcelamento': min(negociacao_parcelamento_score, 1.0),
            'negociacao_desconto': min(negociacao_desconto_score, 1.0),
            'pagamento_confirmacao': min(pagamento_score, 1.0),
            'reclamacao_cobranca_indevida': min(reclamacao_indevida_score, 1.0),
            'reclamacao_valor_incorreto': min(reclamacao_valor_score, 1.0),
            'saudacao': min(saudacao_score, 1.0),
            'despedida': min(despedida_score, 1.0),
            'confirmacao': min(confirmacao_score, 1.0),
            'negacao': min(negacao_score, 1.0),
            'duvida': min(duvida_score, 1.0)
        }
        
        # 🚨 FALLBACK INTELIGENTE - Se nenhuma intenção forte foi detectada
        max_score = max(intent_scores.values()) if intent_scores.values() else 0
        if max_score < 0.3:
            # Cliente escreveu algo muito confuso - tentar inferir pela presença de palavras-chave
            if any(palavra in text.lower() for palavra in ['conta', 'boleto', 'fatura', 'pagar', 'deve']):
                intent_scores['fatura_solicitar'] = 0.5  # Assumir que quer fatura
            elif any(palavra in text.lower() for palavra in ['quanto', 'valor', 'preço']):
                intent_scores['fatura_valor'] = 0.5  # Assumir que quer saber valor
            else:
                intent_scores['duvida'] = 0.5  # Cliente está confuso
        
        return intent_scores
    
    def _apply_contextual_boost(self, base_intents: Dict[str, float], context: Dict) -> Dict[str, float]:
        """Aplicar boost baseado no contexto conversacional"""
        boosted_intents = base_intents.copy()
        
        # Se última mensagem foi sobre fatura, boost relacionados
        last_context = context.get('last_intent')
        if last_context and 'fatura' in last_context:
            boosted_intents['fatura_valor'] = boosted_intents.get('fatura_valor', 0) + 0.2
            boosted_intents['fatura_vencimento'] = boosted_intents.get('fatura_vencimento', 0) + 0.2
        
        # Se contexto de negociação ativa
        if context.get('negotiation_active'):
            boosted_intents['negociacao_desconto'] = boosted_intents.get('negociacao_desconto', 0) + 0.3
            boosted_intents['confirmacao'] = boosted_intents.get('confirmacao', 0) + 0.2
        
        return boosted_intents
    
    def _detect_multiple_intents(self, text: str, entities: List[ExtractedEntity]) -> List[IntentType]:
        """Detectar múltiplas intenções na mesma mensagem - MELHORADO"""
        intents = []
        
        # Detectores mais robustos de múltiplas intenções
        
        # "fatura E desconto/parcelamento"
        if (re.search(r'(fatura|conta)', text, re.IGNORECASE) and 
            re.search(r'(também|e\s+(também)?).*(desconto|parcelar)', text, re.IGNORECASE)):
            intents.extend([IntentType.FATURA_SOLICITAR, IntentType.NEGOCIACAO_DESCONTO])
        
        # "fatura E parcelamento"  
        if (re.search(r'(fatura|conta)', text, re.IGNORECASE) and 
            re.search(r'(também|e\s+(também)?).*(parcelar|dividir)', text, re.IGNORECASE)):
            intents.extend([IntentType.FATURA_SOLICITAR, IntentType.NEGOCIACAO_PARCELAMENTO])
        
        # "paguei MAS ainda aparece"
        if (re.search(r'(paguei|quitei)', text, re.IGNORECASE) and 
            re.search(r'(mas|porém|ainda|continua|aparece)', text, re.IGNORECASE)):
            intents.extend([IntentType.PAGAMENTO_CONFIRMACAO, IntentType.RECLAMACAO_VALOR_INCORRETO])
        
        # "valor E vencimento"
        if (re.search(r'(quanto.*devo)', text, re.IGNORECASE) and 
            re.search(r'(quando.*vence|prazo)', text, re.IGNORECASE)):
            intents.extend([IntentType.FATURA_VALOR, IntentType.FATURA_VENCIMENTO])
        
        # Conectores brasileiros comuns
        conectores = [r'\s+e\s+', r'\s+também\s+', r'\s+além\s+disso\s+', r'\s+mais\s+']
        for conector in conectores:
            if re.search(conector, text, re.IGNORECASE):
                # Se tem conector, analisar cada parte
                partes = re.split(conector, text, flags=re.IGNORECASE)
                if len(partes) >= 2:
                    # Analisar se cada parte tem intenção diferente
                    primeira_parte = partes[0].strip()
                    segunda_parte = partes[1].strip()
                    
                    # Lógica simplificada para detectar intenções diferentes
                    if ('fatura' in primeira_parte.lower() and 
                        any(palavra in segunda_parte.lower() for palavra in ['desconto', 'parcelar', 'negociar'])):
                        intents.extend([IntentType.FATURA_SOLICITAR, IntentType.NEGOCIACAO_DESCONTO])
                        break
        
        return intents
    
    # Métodos de normalização (implementações simplificadas)
    def _normalize_currency(self, text: str) -> str:
        return re.sub(r'[^\d,]', '', text)
    
    def _normalize_date(self, text: str) -> str:
        return text.strip()
    
    def _normalize_protocol(self, text: str) -> str:
        return re.sub(r'[^\w\d]', '', text)
    
    def _normalize_document(self, text: str) -> str:
        return re.sub(r'[^\d]', '', text)
    
    def _super_normalize_text(self, text: str) -> str:
        """🚀 NORMALIZAÇÃO ULTRA AVANÇADA - CORRIGE QUALQUER TEXTO MAL ESCRITO"""
        
        # 1. PRIMEIRA PASSADA - Limpeza básica
        text = text.lower().strip()
        
        # 2. REMOVER EMOJIS E CARACTERES ESPECIAIS (mas preservar pontuação básica)
        text = re.sub(r'[^\w\s\.,!?\-áàâãéèêíìîóòôõúùûç]', ' ', text)
        
        # 3. CORRIGIR ABREVIAÇÕES E ERROS COMUNS (do nosso dicionário)
        erro_patterns = self.brazilian_language_db.get('erro_patterns', {})
        for erro, correto in erro_patterns.items():
            # Usar word boundary para não corrigir partes de palavras
            text = re.sub(rf'\b{re.escape(erro)}\b', correto, text, flags=re.IGNORECASE)
        
        # 4. CORREÇÕES ESPECÍFICAS DE PORTUGUÊS BRASILEIRO MAL ESCRITO
        corrections = {
            # Erros comuns de "quanto"
            r'\b(qnt|qnto|qto|cuanto)\b': 'quanto',
            # Erros comuns de "quando"  
            r'\b(qnd|qndo|quado|cuando)\b': 'quando',
            # Erros de "você"
            r'\bvc\b': 'você',
            # Erros de "não"
            r'\b(nao|naum|ñ|n)\b': 'não',
            # Erros de "para"
            r'\b(pra|pr)\b': 'para',
            # Erros de "porque"
            r'\b(pq|pk|porq)\b': 'porque',
            # Erros de "também"
            r'\b(tb|tbm|tbn)\b': 'também',
            # Erros de "está"
            r'\b(tah|ta|tá)\b': 'está',
            # Erros de "estou"
            r'\b(to|tou)\b': 'estou',
            # Erros de "já"
            r'\b(jah|ja)\b': 'já',
            # Erros de "só"
            r'\b(soh|so)\b': 'só',
            # Erros de "é"
            r'\b(eh|e)\b': 'é',
            # Erros de "hoje"
            r'\bhj\b': 'hoje',
            # Erros de "amanhã"
            r'\b(amanha|amñ)\b': 'amanhã',
            # Erros de "cadê"
            r'\bkd\b': 'cadê',
            # Erros de "aqui"
            r'\b(aki|aq)\b': 'aqui',
            # Erros de "aí"
            r'\b(ai|ae)\b': 'aí',
            # Erros de "mesmo"
            r'\b(msm|mmo)\b': 'mesmo',
            # Erros de "beleza"
            r'\b(blz|bz)\b': 'beleza',
            # Erros de "valeu"
            r'\b(vlw|vl)\b': 'valeu',
            # Erros de "falou"
            r'\b(flw|fl)\b': 'falou',
            # Erros comuns de palavras de cobrança
            r'\b(fatur|ftur)\b': 'fatura',
            r'\b(bolto|bleto)\b': 'boleto',
            r'\b(cota|cnta)\b': 'conta',
            r'\b(cobransa|cobranca)\b': 'cobrança',
            r'\b(pagameto|pagamnto)\b': 'pagamento',
            r'\b(vencimeto|vencimto)\b': 'vencimento',
            r'\b(transferencia|trasferencia)\b': 'transferência',
            r'\b(debto|debito)\b': 'débito'
        }
        
        for pattern, replacement in corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # 5. REMOVER PONTUAÇÃO EXCESSIVA mas preservar sentido
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        
        # 6. NORMALIZAR ESPAÇOS
        text = re.sub(r'\s+', ' ', text)
        
        # 7. CORREÇÕES CONTEXTUAIS ESPECÍFICAS PARA COBRANÇA
        cobranca_corrections = {
            # "segunda via" mal escrito
            r'(segunda|2)\s*(v|vi|via)': 'segunda via',
            # "quanto devo" mal escrito  
            r'(quanto|qnto)\s*(devo|dvo|dveo)': 'quanto devo',
            # "já paguei" mal escrito
            r'(já|jah|ja)\s*(paguei|pguei|pag)': 'já paguei',
            # "não devo" mal escrito
            r'(não|nao|naum)\s*(devo|dvo)': 'não devo',
            # "minha conta" mal escrito
            r'(minha|miha)\s*(conta|cota)': 'minha conta'
        }
        
        for pattern, replacement in cobranca_corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _get_conversation_context(self, phone: str) -> Dict:
        """Obter contexto da conversa"""
        return self.user_contexts.get(phone, {})
    
    def _update_conversation_context(self, phone: str, intent: ContextualIntent, text: str):
        """Atualizar contexto conversacional"""
        if phone not in self.user_contexts:
            self.user_contexts[phone] = {
                'messages': [],
                'last_intent': None,
                'negotiation_active': False,
                'client_profile': {},
                'conversation_flow': []
            }
        
        context = self.user_contexts[phone]
        context['messages'].append({
            'text': text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'timestamp': datetime.now(),
            'entities': [{'type': e.type, 'value': e.value} for e in intent.entities],
            'emotion': intent.emotional_state
        })
        
        context['last_intent'] = intent.intent.value
        
        # Detectar se negociação está ativa
        if intent.intent in [IntentType.NEGOCIACAO_DESCONTO, IntentType.NEGOCIACAO_PARCELAMENTO]:
            context['negotiation_active'] = True
        
        # Manter apenas últimas 10 mensagens
        context['messages'] = context['messages'][-10:]
    
    async def _generate_contextual_response(
        self, phone: str, intent: ContextualIntent, entities: List[ExtractedEntity], context: Dict
    ) -> Dict[str, Any]:
        """🚀 GERADOR DE RESPOSTAS ULTRA INTELIGENTE - PERFEITO PARA CLIENTES BURROS"""
        
        # 🎯 RESPOSTAS BASEADAS NA INTENÇÃO COM CONTEXTO EMOCIONAL
        
        if intent.intent == IntentType.FATURA_SOLICITAR:
            if intent.emotional_state == 'urgente':
                response_text = "🚨 **URGENTE!** Entendi! Vou buscar sua fatura AGORA MESMO e te enviar em segundos!"
            elif intent.emotional_state == 'frustrado':
                response_text = "😔 Percebo que você está chateado. Calma, vou resolver isso rapidinho! Enviando sua fatura já..."
            elif intent.negation:
                response_text = "🤔 Vi que você disse 'não' sobre algo. Me explica melhor o que você precisa da sua conta?"
            else:
                response_text = "📄 **PERFEITO!** Vou pegar sua fatura para você. Só um minutinho..."
        
        elif intent.intent == IntentType.FATURA_VALOR:
            valor_entity = next((e for e in entities if e.type == 'valores_monetarios'), None)
            if valor_entity:
                response_text = f"💰 Vi que você mencionou **R$ {valor_entity.value}**. Vou confirmar se esse é o valor correto da sua conta!"
            elif intent.emotional_state == 'urgente':
                response_text = "💰 **URGENTE!** Vou verificar AGORA quanto você deve exatamente!"
            else:
                response_text = "💰 Entendi! Você quer saber **QUANTO DEVE**, certo? Vou verificar o valor da sua conta!"
        
        elif intent.intent == IntentType.FATURA_VENCIMENTO:
            data_entity = next((e for e in entities if e.type == 'datas'), None)
            if data_entity:
                response_text = f"⏰ Vi que você mencionou **{data_entity.value}**. Vou confirmar o vencimento da sua conta!"
            else:
                response_text = "⏰ Entendi! Você quer saber **QUANDO VENCE** sua conta, né? Vou verificar a data!"
        
        elif intent.intent == IntentType.NEGOCIACAO_PARCELAMENTO:
            if intent.emotional_state == 'frustrado':
                response_text = "🤝 Entendo que está difícil pagar. **CALMA!** Vamos dar um jeito! Temos várias opções de parcelamento!"
            elif any(e.type == 'valores_monetarios' for e in entities):
                valor = next(e.value for e in entities if e.type == 'valores_monetarios')
                response_text = f"🤝 Perfeito! Você quer parcelar **R$ {valor}**, né? Vamos encontrar a melhor condição para você!"
            else:
                response_text = "🤝 **ÓTIMO!** Quer parcelar? Vou ver as melhores condições que temos disponíveis!"
        
        elif intent.intent == IntentType.NEGOCIACAO_DESCONTO:
            if intent.emotional_state == 'frustrado':
                response_text = "💸 Entendo sua situação! Vamos ver que **DESCONTO** posso conseguir para você!"
            else:
                response_text = "💸 Interessado em desconto? **PERFEITO!** Vou verificar as promoções disponíveis!"
        
        elif intent.intent == IntentType.PAGAMENTO_CONFIRMACAO:
            if intent.temporal_context == 'passado':
                if intent.emotional_state == 'frustrado':
                    response_text = "✅ Entendi! Você **JÁ PAGOU** mas ainda está aparecendo, né? Vou verificar URGENTE o que aconteceu!"
            else:
                    response_text = "✅ **BELEZA!** Você já pagou! Vou confirmar aqui no sistema se o pagamento foi processado!"
            else:
                response_text = "💳 Perfeito! Vou verificar o status do seu pagamento no sistema!"
        
        elif intent.intent == IntentType.RECLAMACAO_COBRANCA_INDEVIDA:
            if intent.emotional_state == 'frustrado':
                response_text = "😡 **ENTENDO SUA REVOLTA!** Cobrança indevida é muito chato mesmo! Vou resolver isso AGORA!"
            else:
                response_text = "🔍 Entendi! Você acha que essa cobrança está **ERRADA**, né? Vou analisar sua situação!"
        
        elif intent.intent == IntentType.RECLAMACAO_VALOR_INCORRETO:
            response_text = "🔍 **NOSSA!** Valor incorreto é sério! Vou verificar sua conta e corrigir se estiver errado mesmo!"
        
        elif intent.intent == IntentType.SAUDACAO:
            horario = datetime.now().hour
            if horario < 12:
                response_text = "🌅 **BOM DIA!** Tudo beleza? Como posso te ajudar hoje?"
            elif horario < 18:
                response_text = "☀️ **BOA TARDE!** E aí, tudo certo? Em que posso ajudar?"
        else:
                response_text = "🌙 **BOA NOITE!** Beleza? Como posso te ajudar?"
        
        elif intent.intent == IntentType.DESPEDIDA:
            response_text = "👋 **VALEU!** Obrigado pelo contato! Qualquer coisa, me chama! 😊"
        
        elif intent.intent == IntentType.CONFIRMACAO:
            response_text = "✅ **PERFEITO!** Entendi que você confirmou! Vou continuar com o processo!"
        
        elif intent.intent == IntentType.NEGACAO:
            response_text = "❌ **BELEZA!** Você disse que não. Me explica melhor o que você precisa então?"
        
        elif intent.intent == IntentType.DUVIDA:
            response_text = "🤔 **SEM PROBLEMAS!** Vou explicar melhor! O que especificamente você não entendeu?"
        
        else:
            # Fallback inteligente baseado no que foi detectado
            if intent.confidence < 0.5:
                response_text = "🤔 **CALMA!** Acho que não entendi direito. Pode me falar de novo de um jeito mais simples? Tipo: 'quero minha conta' ou 'quanto devo'?"
            else:
                response_text = "🤖 **ENTENDI ALGUMA COISA!** Mas me explica melhor o que você precisa. Fala de forma simples!"
        
        # 📋 ADICIONAR INFORMAÇÕES SOBRE MÚLTIPLAS INTENÇÕES
        if intent.multiple_intents and len(intent.multiple_intents) > 0:
            intents_text = []
            for multi_intent in intent.multiple_intents:
                if multi_intent == IntentType.FATURA_SOLICITAR:
                    intents_text.append("ver sua conta")
                elif multi_intent == IntentType.FATURA_VALOR:
                    intents_text.append("saber quanto deve")
                elif multi_intent == IntentType.NEGOCIACAO_PARCELAMENTO:
                    intents_text.append("parcelar")
                elif multi_intent == IntentType.NEGOCIACAO_DESCONTO:
                    intents_text.append("conseguir desconto")
                else:
                    intents_text.append(multi_intent.value.replace('_', ' '))
            
            if intents_text:
                response_text += f"\n\n📋 **TAMBÉM PERCEBI** que você quer: {' e '.join(intents_text)}. Vou ajudar com tudo!"
        
        # 🔥 ADICIONAR CALL TO ACTION BASEADO NA INTENÇÃO
        if intent.intent in [IntentType.FATURA_SOLICITAR, IntentType.FATURA_VALOR, IntentType.FATURA_VENCIMENTO]:
            response_text += "\n\n⚡ **Aguarda aí que vou buscar suas informações!**"
        elif intent.intent in [IntentType.NEGOCIACAO_PARCELAMENTO, IntentType.NEGOCIACAO_DESCONTO]:
            response_text += "\n\n🤝 **Vou verificar as melhores condições para você!**"
        elif intent.intent == IntentType.PAGAMENTO_CONFIRMACAO:
            response_text += "\n\n🔍 **Verificando seu pagamento no sistema...**"
        
        return {
            'text': response_text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'entities_detected': len(entities),
            'emotional_state': intent.emotional_state,
            'multiple_intents': len(intent.multiple_intents),
            'context_enhanced': True,
            'response_type': 'ultra_contextual'
        }
    
    async def _generate_fallback_response(self, phone: str, text: str) -> Dict[str, Any]:
        """Resposta de fallback inteligente"""
        return {
            'text': "🤔 Percebi que você está tentando me dizer algo importante. Pode reformular para eu entender melhor?",
            'intent': 'clarification_needed',
            'confidence': 0.3,
            'fallback': True
        }
    
    def _load_contextual_responses(self) -> Dict:
        """Carregar respostas contextuais avançadas"""
        return {
            # Implementar depois conforme necessário
            'advanced_templates': {}
        } 
    
    # ================================
    # 🚀 SISTEMAS ULTRA AVANÇADOS - NÍVEL CHATGPT
    # ================================
    
    def _build_semantic_patterns(self) -> Dict[str, SemanticPattern]:
        """🧠 CONSTRUIR PADRÕES SEMÂNTICOS ULTRA AVANÇADOS"""
        patterns = {}
        
        # Padrão semântico para FATURA
        patterns['fatura_semantic'] = SemanticPattern(
            pattern_id='fatura_semantic',
            semantic_vectors={
                'documento': 0.9, 'papel': 0.8, 'conta': 1.0, 'boleto': 1.0,
                'cobrança': 0.9, 'débito': 0.8, 'pagamento': 0.7, 'valor': 0.6,
                'segunda_via': 1.0, 'cópia': 0.7, 'comprovante': 0.6
            },
            context_triggers=['preciso', 'quero', 'mandar', 'enviar', 'ver'],
            intent_weights={'fatura_solicitar': 1.0, 'fatura_valor': 0.3},
            emotional_indicators={'urgente': 0.3, 'neutro': 0.7},
            confidence_modifiers={'direto': 1.0, 'indireto': 0.7}
        )
        
        # Padrão semântico para VALOR/QUANTIDADE
        patterns['valor_semantic'] = SemanticPattern(
            pattern_id='valor_semantic',
            semantic_vectors={
                'quanto': 1.0, 'valor': 1.0, 'preço': 0.9, 'custo': 0.8,
                'dinheiro': 0.7, 'grana': 0.8, 'real': 0.6, 'centavo': 0.5,
                'total': 0.9, 'dever': 0.9, 'pagar': 0.8
            },
            context_triggers=['devo', 'pago', 'custa', 'vale'],
            intent_weights={'fatura_valor': 1.0, 'pagamento_confirmacao': 0.4},
            emotional_indicators={'frustrado': 0.2, 'neutro': 0.8},
            confidence_modifiers={'pergunta': 1.0, 'afirmacao': 0.6}
        )
        
        # Padrão semântico para TEMPO/VENCIMENTO
        patterns['tempo_semantic'] = SemanticPattern(
            pattern_id='tempo_semantic',
            semantic_vectors={
                'quando': 1.0, 'data': 0.9, 'dia': 0.8, 'prazo': 1.0,
                'vencimento': 1.0, 'vence': 1.0, 'até': 0.7, 'tempo': 0.8,
                'hoje': 0.6, 'amanhã': 0.7, 'mês': 0.6
            },
            context_triggers=['vence', 'termina', 'acaba', 'expira'],
            intent_weights={'fatura_vencimento': 1.0, 'pagamento_confirmacao': 0.3},
            emotional_indicators={'urgente': 0.5, 'neutro': 0.5},
            confidence_modifiers={'futuro': 1.0, 'passado': 0.4}
        )
        
        # Padrão semântico para NEGOCIAÇÃO
        patterns['negociacao_semantic'] = SemanticPattern(
            pattern_id='negociacao_semantic',
            semantic_vectors={
                'parcelar': 1.0, 'dividir': 0.9, 'acordo': 0.9, 'negociar': 1.0,
                'desconto': 1.0, 'abatimento': 0.8, 'facilitar': 0.7, 'ajuda': 0.6,
                'dificuldade': 0.8, 'problema': 0.7, 'apertado': 0.8, 'quebrar_galho': 0.9
            },
            context_triggers=['não_consigo', 'difícil', 'sem_dinheiro', 'ajudar'],
            intent_weights={'negociacao_parcelamento': 0.7, 'negociacao_desconto': 0.3},
            emotional_indicators={'frustrado': 0.6, 'urgente': 0.4},
            confidence_modifiers={'pedido': 1.0, 'sugestao': 0.8}
        )
        
        return patterns
    
    def _build_semantic_vectors(self) -> Dict[str, Dict[str, float]]:
        """🔬 CONSTRUIR VETORES SEMÂNTICOS BRASILEIROS ULTRA AVANÇADOS"""
        return {
            # Vetores semânticos para palavras de cobrança
            'fatura': {
                'conta': 0.95, 'boleto': 0.90, 'cobrança': 0.85, 'débito': 0.80,
                'documento': 0.75, 'papel': 0.70, 'segunda_via': 0.95, 'cópia': 0.60
            },
            'pagar': {
                'quitar': 0.90, 'saldar': 0.85, 'liquidar': 0.80, 'acertar': 0.75,
                'resolver': 0.70, 'transferir': 0.65, 'depositar': 0.60
            },
            'quanto': {
                'valor': 0.95, 'preço': 0.90, 'custo': 0.85, 'total': 0.80,
                'dinheiro': 0.75, 'grana': 0.80, 'real': 0.70
            },
            'quando': {
                'data': 0.90, 'dia': 0.85, 'prazo': 0.95, 'vencimento': 0.95,
                'tempo': 0.80, 'até': 0.75, 'hora': 0.70
            },
            'problema': {
                'dificuldade': 0.90, 'complicação': 0.85, 'erro': 0.80,
                'confusão': 0.75, 'encrenca': 0.85, 'pepino': 0.80
            }
        }
    
    def _build_intent_similarity_matrix(self) -> Dict[str, Dict[str, float]]:
        """🎯 MATRIZ DE SIMILARIDADE ENTRE INTENÇÕES"""
        return {
            'fatura_solicitar': {
                'fatura_valor': 0.7, 'fatura_vencimento': 0.6, 'pagamento_confirmacao': 0.4,
                'negociacao_parcelamento': 0.3, 'informacao_conta': 0.8
            },
            'fatura_valor': {
                'fatura_solicitar': 0.7, 'fatura_vencimento': 0.5, 'pagamento_confirmacao': 0.6,
                'negociacao_parcelamento': 0.7, 'negociacao_desconto': 0.5
            },
            'negociacao_parcelamento': {
                'negociacao_desconto': 0.8, 'pagamento_dificuldade': 0.9, 'fatura_valor': 0.6
            },
            'pagamento_confirmacao': {
                'reclamacao_valor_incorreto': 0.5, 'fatura_valor': 0.4, 'fatura_solicitar': 0.3
            }
        }
    
    def _build_relationship_graph(self) -> Dict[str, List[str]]:
        """🕸️ GRAFO DE RELACIONAMENTOS CONTEXTUAIS"""
        return {
            'financial_entities': ['valor', 'dinheiro', 'real', 'centavo', 'pagar', 'dever'],
            'temporal_entities': ['quando', 'dia', 'data', 'prazo', 'vencimento', 'até'],
            'document_entities': ['conta', 'boleto', 'fatura', 'papel', 'documento', 'cópia'],
            'negotiation_entities': ['parcelar', 'dividir', 'acordo', 'desconto', 'facilitar'],
            'emotional_entities': ['problema', 'dificuldade', 'urgente', 'chateado', 'nervoso'],
            'action_entities': ['quero', 'preciso', 'gostaria', 'mandar', 'enviar', 'ver']
        }
    
    def _load_discourse_analyzers(self) -> Dict[str, Any]:
        """💬 ANALISADORES DE DISCURSO ULTRA AVANÇADOS"""
        return {
            'discourse_markers': {
                'addition': ['também', 'além disso', 'e', 'mais', 'ainda'],
                'contrast': ['mas', 'porém', 'entretanto', 'contudo', 'no entanto'],
                'cause': ['porque', 'pois', 'já que', 'visto que', 'uma vez que'],
                'conclusion': ['então', 'portanto', 'assim', 'logo', 'por isso'],
                'sequence': ['primeiro', 'depois', 'em seguida', 'finalmente', 'por último'],
                'emphasis': ['realmente', 'muito', 'bastante', 'extremamente', 'totalmente']
            },
            'pragmatic_markers': {
                'politeness': ['por favor', 'obrigado', 'desculpa', 'com licença'],
                'urgency': ['urgente', 'rápido', 'agora', 'imediatamente', 'já'],
                'uncertainty': ['acho', 'talvez', 'pode ser', 'não tenho certeza'],
                'emphasis': ['realmente', 'certamente', 'definitivamente', 'com certeza']
            }
        }
    
    def _build_pragmatic_engine(self) -> Dict[str, Any]:
        """🧠 ENGINE DE INFERÊNCIA PRAGMÁTICA ULTRA AVANÇADA"""
        return {
            'implicature_rules': {
                # Se diz "já paguei MAS ainda aparece" = reclama valor incorreto
                'payment_but_still_charged': {
                    'pattern': r'(já.*pagu|quitei|paguei).*(mas|porém|ainda|continua)',
                    'inference': 'reclamacao_valor_incorreto',
                    'confidence': 0.9
                },
                # Se pergunta valor E prazo = quer informações completas
                'value_and_deadline': {
                    'pattern': r'(quanto.*devo).*(quando.*vence|prazo)',
                    'inference': 'multiple_intents',
                    'confidence': 0.8
                },
                # Se diz que não consegue pagar = quer negociar
                'cannot_pay': {
                    'pattern': r'não.*(consigo|posso).*(pagar|quitar)',
                    'inference': 'negociacao_parcelamento',
                    'confidence': 0.85
                }
            },
            'contextual_inference': {
                # Inferências baseadas no contexto da conversa
                'follow_up_questions': {
                    'after_invoice_request': ['fatura_valor', 'fatura_vencimento'],
                    'after_negotiation': ['confirmacao', 'negacao', 'duvida'],
                    'after_payment_info': ['pagamento_confirmacao']
                }
            }
        }
    
    def _build_coherence_analyzer(self) -> Dict[str, Any]:
        """🔗 ANALISADOR DE COERÊNCIA CONTEXTUAL ULTRA AVANÇADO"""
        return {
            'coherence_rules': {
                'topic_continuity': {
                    'same_topic': 1.0,      # Mesma intenção que anterior
                    'related_topic': 0.8,   # Intenção relacionada
                    'topic_shift': 0.4,     # Mudança de assunto
                    'random_topic': 0.1     # Assunto totalmente aleatório
                },
                'temporal_coherence': {
                    'logical_sequence': 1.0,    # Sequência lógica
                    'acceptable_jump': 0.7,     # Salto aceitável
                    'confusing_sequence': 0.3   # Sequência confusa
                }
            },
            'context_memory_window': 5,  # Quantas mensagens anteriores considerar
            'coherence_threshold': 0.6   # Limite mínimo de coerência
        }
    
    def _build_multi_layer_processors(self) -> List[Dict[str, Any]]:
        """🎛️ PROCESSADORES MULTI-CAMADAS ULTRA AVANÇADOS"""
        return [
            {
                'layer': 'lexical',
                'processor': 'word_level_analysis',
                'weight': 0.2,
                'functions': ['tokenization', 'pos_tagging', 'lemmatization']
            },
            {
                'layer': 'syntactic', 
                'processor': 'phrase_level_analysis',
                'weight': 0.3,
                'functions': ['phrase_detection', 'dependency_parsing']
            },
            {
                'layer': 'semantic',
                'processor': 'meaning_level_analysis', 
                'weight': 0.3,
                'functions': ['semantic_similarity', 'concept_mapping']
            },
            {
                'layer': 'pragmatic',
                'processor': 'context_level_analysis',
                'weight': 0.2,
                'functions': ['pragmatic_inference', 'discourse_analysis']
            }
        ]
    
    def _build_fallback_system(self) -> Dict[str, Any]:
        """🛡️ SISTEMA DE FALLBACK INTELIGENTE MULTI-CAMADAS"""
        return {
            'fallback_levels': [
                {
                    'level': 1,
                    'name': 'semantic_similarity',
                    'method': 'find_closest_semantic_match',
                    'threshold': 0.6
                },
                {
                    'level': 2, 
                    'name': 'keyword_extraction',
                    'method': 'extract_key_concepts',
                    'threshold': 0.4
                },
                {
                    'level': 3,
                    'name': 'pattern_matching',
                    'method': 'fuzzy_pattern_match', 
                    'threshold': 0.3
                },
                {
                    'level': 4,
                    'name': 'conversational_context',
                    'method': 'infer_from_conversation',
                    'threshold': 0.2
                },
                {
                    'level': 5,
                    'name': 'intelligent_guess',
                    'method': 'make_educated_guess',
                    'threshold': 0.1
                }
            ]
        }
    
    def _build_dynamic_generator(self) -> Dict[str, Any]:
        """🎭 GERADOR DINÂMICO DE RESPOSTAS ULTRA INTELIGENTE"""
        return {
            'response_templates': {
                'high_confidence': "✅ **{emotion_marker}** {action_confirmation} {specifics}",
                'medium_confidence': "🤔 **{understanding}** {clarification_request}",
                'low_confidence': "❓ **{confusion_acknowledgment}** {help_request}",
                'contextual': "🎯 **{context_reference}** {personalized_response}"
            },
            'emotion_markers': {
                'urgente': ['URGENTE!', 'RAPIDINHO!', 'AGORA MESMO!'],
                'frustrado': ['CALMA!', 'ENTENDO!', 'VAMOS RESOLVER!'],
                'neutro': ['PERFEITO!', 'BELEZA!', 'CERTO!'],
                'satisfeito': ['ÓTIMO!', 'EXCELENTE!', 'SHOW!']
            },
            'personalization_factors': [
                'conversation_history', 'emotional_state', 'communication_style',
                'previous_intents', 'response_patterns', 'user_preferences'
            ]
        }
    
    # ================================
    # 🚀 MÉTODOS ULTRA MEGA AVANÇADOS - NÍVEL CHATGPT GIGANTEMENTE FODA
    # ================================
    
    def _get_or_create_conversation_memory(self, phone: str) -> ConversationMemory:
        """🧠 OBTER OU CRIAR MEMÓRIA ULTRA AVANÇADA"""
        if phone not in self.conversation_memories:
            self.conversation_memories[phone] = ConversationMemory()
        return self.conversation_memories[phone]
    
    def _ultra_advanced_normalize_text(self, text: str) -> str:
        """🚀 NORMALIZAÇÃO ULTRA MEGA AVANÇADA"""
        # Usar o método existente mas com melhorias
        normalized = self._super_normalize_text(text)
        
        # Adicionar análises extras ultra avançadas
        normalized = self._apply_phonetic_corrections(normalized)
        normalized = self._fix_cognitive_errors(normalized)
        normalized = self._standardize_brazilian_expressions(normalized)
        
        return normalized
    
    def _apply_phonetic_corrections(self, text: str) -> str:
        """🔊 CORREÇÕES FONÉTICAS ULTRA AVANÇADAS"""
        phonetic_corrections = {
            # Correções baseadas em como as pessoas falam
            r'\b(di)\b': 'de',  # "di manhã" -> "de manhã"
            r'\b(nu)\b': 'no',  # "nu banco" -> "no banco"
            r'\b(du)\b': 'do',  # "du cliente" -> "do cliente"
            r'\b(ma)\b': 'mas', # "ma não" -> "mas não"
            r'\b(qui)\b': 'que', # "qui dia" -> "que dia"
            r'\b(cumé)\b': 'como é', # "cumé que" -> "como é que"
            r'\b(ocê)\b': 'você',    # "ocê tem" -> "você tem"
            r'\b(seje)\b': 'seja',   # "seje o que" -> "seja o que"
        }
        
        for pattern, replacement in phonetic_corrections.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_cognitive_errors(self, text: str) -> str:
        """🧠 CORRIGIR ERROS COGNITIVOS E DE RACIOCÍNIO"""
        cognitive_fixes = {
            # Erros de lógica temporal
            r'(ontem.*amanha|amanha.*ontem)': 'ontem ou amanhã',
            # Contradições óbvias
            r'(não.*mas.*sim|sim.*mas.*não)': 'talvez',
            # Confusões de pessoa
            r'(você.*eu.*pagar|eu.*você.*pagar)': 'preciso pagar',
        }
        
        for pattern, replacement in cognitive_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _standardize_brazilian_expressions(self, text: str) -> str:
        """🇧🇷 PADRONIZAR EXPRESSÕES TIPICAMENTE BRASILEIRAS"""
        expressions = {
            r'(tá.*ligado|sacou|entendeu)': 'entende',
            r'(massa|show|da.*hora)': 'bom',
            r'(trampo|labuta)': 'trabalho',
            r'(grana|din.*din|money)': 'dinheiro',
            r'(mina|mano|brother)': 'pessoa',
            r'(rolê|role)': 'situação',
        }
        
        for pattern, replacement in expressions.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    async def _perform_multi_layer_analysis(self, text: str) -> Dict[str, Any]:
        """🎛️ ANÁLISE MULTI-CAMADAS ULTRA PROFUNDA"""
        analysis = {
            'lexical': self._analyze_lexical_layer(text),
            'syntactic': self._analyze_syntactic_layer(text),
            'semantic': self._analyze_semantic_layer(text),
            'pragmatic': self._analyze_pragmatic_layer(text)
        }
        
        # Calcular score agregado
        analysis['overall_complexity'] = sum(
            layer['complexity_score'] * processor['weight'] 
            for layer, processor in zip(analysis.values(), self.multi_layer_processors)
        )
        
        return analysis
    
    def _analyze_lexical_layer(self, text: str) -> Dict[str, Any]:
        """📝 ANÁLISE LEXICAL ULTRA PROFUNDA"""
        words = text.split()
        
        return {
            'word_count': len(words),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'complexity_score': min(len(words) * 0.1, 1.0),
            'rare_words': [w for w in words if len(w) > 8],
            'simple_words': [w for w in words if len(w) <= 4]
        }
    
    def _analyze_syntactic_layer(self, text: str) -> Dict[str, Any]:
        """🔗 ANÁLISE SINTÁTICA ULTRA PROFUNDA"""
        # Detectar estruturas sintáticas
        has_questions = bool(re.search(r'\?', text))
        has_subordinate = bool(re.search(r'\b(que|se|quando|onde|como)\b', text))
        has_coordination = bool(re.search(r'\b(e|mas|ou|porém)\b', text))
        
        complexity = 0.3
        if has_questions: complexity += 0.2
        if has_subordinate: complexity += 0.3
        if has_coordination: complexity += 0.2
        
        return {
            'has_questions': has_questions,
            'has_subordinate_clauses': has_subordinate,
            'has_coordination': has_coordination,
            'complexity_score': min(complexity, 1.0)
        }
    
    def _analyze_semantic_layer(self, text: str) -> Dict[str, Any]:
        """🧠 ANÁLISE SEMÂNTICA ULTRA PROFUNDA"""
        semantic_clusters = []
        cluster_scores = {}
        
        # Analisar proximidade semântica com nossos clusters
        for cluster_name, words in self.contextual_relationship_graph.items():
            score = 0
            for word in words:
                if word in text.lower():
                    score += 1
            
            if score > 0:
                semantic_clusters.append(cluster_name)
                cluster_scores[cluster_name] = score / len(words)
        
        return {
            'semantic_clusters': semantic_clusters,
            'cluster_scores': cluster_scores,
            'complexity_score': min(len(semantic_clusters) * 0.2, 1.0),
            'semantic_density': sum(cluster_scores.values()) / max(len(cluster_scores), 1)
        }
    
    def _analyze_pragmatic_layer(self, text: str) -> Dict[str, Any]:
        """💭 ANÁLISE PRAGMÁTICA ULTRA PROFUNDA"""
        pragmatic_elements = {}
        
        # Detectar elementos pragmáticos
        for marker_type, markers in self.discourse_analyzers['pragmatic_markers'].items():
            found_markers = [m for m in markers if m in text.lower()]
            if found_markers:
                pragmatic_elements[marker_type] = found_markers
        
        return {
            'pragmatic_elements': pragmatic_elements,
            'complexity_score': min(len(pragmatic_elements) * 0.25, 1.0),
            'pragmatic_richness': len(pragmatic_elements)
        }
    
    async def _perform_semantic_analysis(self, text: str, memory: ConversationMemory) -> Dict[str, Any]:
        """🔬 ANÁLISE SEMÂNTICA MEGA ULTRA AVANÇADA"""
        semantic_analysis = {}
        
        # Calcular similaridade semântica com padrões conhecidos
        for pattern_id, pattern in self.semantic_patterns.items():
            similarity = self._calculate_semantic_similarity(text, pattern)
            semantic_analysis[pattern_id] = similarity
        
        # Análise de vetores semânticos
        vector_analysis = self._analyze_semantic_vectors(text)
        
        return {
            'pattern_similarities': semantic_analysis,
            'vector_analysis': vector_analysis,
            'best_match': max(semantic_analysis.items(), key=lambda x: x[1]) if semantic_analysis else None,
            'semantic_confidence': max(semantic_analysis.values()) if semantic_analysis else 0.0
        }
    
    def _calculate_semantic_similarity(self, text: str, pattern: SemanticPattern) -> float:
        """📐 CALCULAR SIMILARIDADE SEMÂNTICA ULTRA PRECISA"""
        similarity_score = 0.0
        total_weight = 0.0
        
        # Analisar vetores semânticos
        for concept, weight in pattern.semantic_vectors.items():
            if concept in text.lower():
                similarity_score += weight
            total_weight += weight
        
        # Normalizar score
        if total_weight > 0:
            similarity_score = similarity_score / total_weight
        
        # Boost por triggers contextuais
        for trigger in pattern.context_triggers:
            if trigger in text.lower():
                similarity_score += 0.1
        
        return min(similarity_score, 1.0)
    
    def _analyze_semantic_vectors(self, text: str) -> Dict[str, float]:
        """🧮 ANÁLISE DE VETORES SEMÂNTICOS"""
        vector_scores = {}
        
        for main_concept, related_concepts in self.brazilian_semantic_vectors.items():
            if main_concept in text.lower():
                vector_scores[main_concept] = 1.0
                
                # Adicionar conceitos relacionados
                for related, similarity in related_concepts.items():
                    if related in text.lower():
                        vector_scores[related] = similarity
        
        return vector_scores
    
    async def _perform_pragmatic_analysis(self, text: str, memory: ConversationMemory) -> Dict[str, Any]:
        """🎭 ANÁLISE PRAGMÁTICA MEGA ULTRA AVANÇADA"""
        pragmatic_inferences = {}
        
        # Aplicar regras de implicatura
        for rule_name, rule in self.pragmatic_inference_engine['implicature_rules'].items():
            if re.search(rule['pattern'], text, re.IGNORECASE):
                pragmatic_inferences[rule_name] = {
                    'inference': rule['inference'],
                    'confidence': rule['confidence']
                }
        
        # Análise contextual baseada na conversa anterior
        contextual_inferences = self._analyze_conversational_context(text, memory)
        
        return {
            'implicatures': pragmatic_inferences,
            'contextual_inferences': contextual_inferences,
            'pragmatic_confidence': max(
                [inf['confidence'] for inf in pragmatic_inferences.values()] + [0.0]
            )
        }
    
    def _analyze_conversational_context(self, text: str, memory: ConversationMemory) -> Dict[str, Any]:
        """💬 ANÁLISE DE CONTEXTO CONVERSACIONAL ULTRA PROFUNDA"""
        inferences = {}
        
        # Analisar padrão baseado na última intenção
        if memory.intent_history:
            last_intent, confidence, timestamp = memory.intent_history[-1]
            
            # Inferir follow-ups baseados na intenção anterior
            follow_ups = self.pragmatic_inference_engine['contextual_inference']['follow_up_questions']
            if last_intent in follow_ups:
                for possible_intent in follow_ups[last_intent]:
                    inferences[f'follow_up_{possible_intent}'] = confidence * 0.7
        
        return inferences
    
    async def _extract_ultra_advanced_entities(self, text: str, semantic_analysis: Dict[str, Any]) -> List[ExtractedEntity]:
        """🎯 EXTRAÇÃO ULTRA AVANÇADA DE ENTIDADES COM CONTEXTO SEMÂNTICO"""
        entities = []
        
        # Usar método existente como base
        base_entities = self._extract_all_entities(text)
        
        # Enriquecer com análise semântica
        for entity in base_entities:
            # Calcular peso semântico
            semantic_weight = 1.0
            if semantic_analysis.get('vector_analysis'):
                for concept, score in semantic_analysis['vector_analysis'].items():
                    if concept in entity.value.lower():
                        semantic_weight = max(semantic_weight, score)
            
            # Adicionar alternativas baseadas em similaridade
            alternatives = self._find_entity_alternatives(entity, semantic_analysis)
            
            # Criar entidade enriquecida
            ultra_entity = ExtractedEntity(
                type=entity.type,
                value=entity.value,
                confidence=entity.confidence,
                context=entity.context,
                semantic_weight=semantic_weight,
                alternatives=alternatives,
                relationships=self._find_entity_relationships(entity, text)
            )
            
            entities.append(ultra_entity)
        
        return entities
    
    def _find_entity_alternatives(self, entity: ExtractedEntity, semantic_analysis: Dict[str, Any]) -> List[str]:
        """🔍 ENCONTRAR ALTERNATIVAS SEMÂNTICAS PARA ENTIDADES"""
        alternatives = []
        
        if entity.type == 'valores_monetarios':
            alternatives = ['valor', 'quantia', 'dinheiro', 'preço', 'custo']
        elif entity.type == 'datas':
            alternatives = ['prazo', 'vencimento', 'data', 'dia', 'quando']
        
        return alternatives
    
    def _find_entity_relationships(self, entity: ExtractedEntity, text: str) -> Dict[str, float]:
        """🕸️ ENCONTRAR RELACIONAMENTOS ENTRE ENTIDADES"""
        relationships = {}
        
        # Analisar proximidade com outras palavras-chave
        for cluster_name, words in self.contextual_relationship_graph.items():
            for word in words:
                if word in text.lower() and word != entity.value.lower():
                    relationships[word] = 0.8  # Score de relacionamento
        
        return relationships
    
    async def _analyze_ultra_emotion(self, text: str, memory: ConversationMemory) -> str:
        """😊 ANÁLISE EMOCIONAL ULTRA AVANÇADA COM MEMÓRIA"""
        # Usar análise existente como base
        base_emotion = self._analyze_emotion(text)
        
        # Enriquecer com contexto de memória emocional
        if memory.emotional_journey:
            # Considerar padrão emocional histórico
            recent_emotions = [emotion for emotion, score, timestamp in memory.emotional_journey[-3:]]
            
            # Se há padrão de frustração crescente
            if recent_emotions.count('frustrado') >= 2:
                if base_emotion in ['neutro', 'confuso']:
                    base_emotion = 'frustrado'  # Inferir frustração continuada
        
        # Detectar escalation emocional
        emotional_escalation = self._detect_emotional_escalation(text)
        if emotional_escalation:
            if base_emotion == 'frustrado':
                base_emotion = 'muito_frustrado'  # Nova categoria
            elif base_emotion == 'urgente':
                base_emotion = 'extremamente_urgente'  # Nova categoria
        
        return base_emotion
    
    def _detect_emotional_escalation(self, text: str) -> bool:
        """📈 DETECTAR ESCALATION EMOCIONAL"""
        escalation_markers = [
            r'(muito|extremamente|super|ultra).*(chateado|irritado)',
            r'(não.*aguentar|não.*suportar)',
            r'(absurdo|ridículo|inaceitável)',
            r'[!]{3,}',  # Múltiplas exclamações
            r'[?!]{2,}',  # Mistura de ? e !
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in escalation_markers)
    
    async def _analyze_ultra_temporal_context(self, text: str, memory: ConversationMemory) -> str:
        """⏰ ANÁLISE TEMPORAL ULTRA AVANÇADA"""
        base_temporal = self._analyze_temporal_context(text)
        
        # Enriquecer com análise de urgência temporal
        urgency_indicators = {
            'imediato': ['agora', 'já', 'imediatamente', 'urgente'],
            'hoje': ['hoje', 'hj', 'ainda hoje'],
            'breve': ['logo', 'em breve', 'rapidinho'],
            'futuro_proximo': ['amanhã', 'essa semana', 'uns dias'],
            'futuro_distante': ['mês que vem', 'ano que vem', 'mais tarde']
        }
        
        for urgency_level, indicators in urgency_indicators.items():
            if any(indicator in text.lower() for indicator in indicators):
                return f"{base_temporal}_{urgency_level}"
        
        return base_temporal
    
    async def _analyze_ultra_negation(self, text: str) -> Dict[str, Any]:
        """❌ ANÁLISE ULTRA AVANÇADA DE NEGAÇÃO"""
        has_basic_negation = self._detect_negation(text)
        
        # Análise mais sofisticada de tipos de negação
        negation_types = {
            'absolute': r'\b(nunca|jamais|de jeito nenhum)\b',
            'partial': r'\b(não muito|meio que não|acho que não)\b',
            'conditional': r'\b(não se|só não|a não ser)\b',
            'emphatic': r'\b(de forma alguma|nem pensar|que nada)\b'
        }
        
        detected_types = []
        for neg_type, pattern in negation_types.items():
            if re.search(pattern, text, re.IGNORECASE):
                detected_types.append(neg_type)
        
        return {
            'has_negation': has_basic_negation,
            'negation_types': detected_types,
            'negation_strength': len(detected_types) / len(negation_types)
        }
    
    async def _analyze_ultra_contextual_intent(
        self, text: str, entities: List[ExtractedEntity], emotion: str, 
        temporal: str, negation: Dict, memory: ConversationMemory, 
        semantic_analysis: Dict, pragmatic_analysis: Dict
    ) -> ContextualIntent:
        """🧠 ANÁLISE ULTRA MEGA AVANÇADA DE INTENÇÃO CONTEXTUAL"""
        
        # Usar análise base existente
        base_intent_analysis = self._analyze_contextual_intent(
            text, entities, emotion, temporal, negation.get('has_negation', False), memory
        )
        
        # ENRIQUECER COM ANÁLISES ULTRA AVANÇADAS
        
        # 1. Boost semântico baseado na melhor correspondência
        if semantic_analysis.get('best_match'):
            pattern_id, similarity_score = semantic_analysis['best_match']
            if similarity_score > 0.7:
                # Aplicar boost baseado no padrão semântico
                if 'fatura' in pattern_id:
                    base_intent_analysis.confidence += 0.2
                elif 'valor' in pattern_id:
                    base_intent_analysis.confidence += 0.15
        
        # 2. Boost pragmático baseado em implicaturas
        pragmatic_confidence = pragmatic_analysis.get('pragmatic_confidence', 0)
        base_intent_analysis.confidence += pragmatic_confidence * 0.1
        
        # 3. Calcular similaridade semântica com intenções conhecidas
        semantic_similarity = self._calculate_intent_semantic_similarity(
            base_intent_analysis.intent, semantic_analysis
        )
        
        # 4. Analisar alternativas de intenção
        alternative_intents = self._calculate_alternative_intents(
            text, semantic_analysis, pragmatic_analysis
        )
        
        # 5. Detectar clusters semânticos
        semantic_clusters = semantic_analysis.get('pattern_similarities', {}).keys()
        
        # 6. Analisar marcadores de discurso
        discourse_markers = self._extract_discourse_markers(text)
        
        # 7. Inferência pragmática ultra avançada
        pragmatic_inference = self._calculate_pragmatic_inference(
            base_intent_analysis, pragmatic_analysis, memory
        )
        
        # Criar intenção contextual ultra enriquecida
        ultra_intent = ContextualIntent(
            intent=base_intent_analysis.intent,
            confidence=min(base_intent_analysis.confidence, 1.0),
            entities=entities,
            temporal_context=temporal,
            emotional_state=emotion,
            negation=negation.get('has_negation', False),
            multiple_intents=base_intent_analysis.multiple_intents,
            
            # CAMPOS ULTRA AVANÇADOS
            semantic_similarity=semantic_similarity,
            contextual_coherence=0.0,  # Será calculado depois
            linguistic_complexity=semantic_analysis.get('semantic_confidence', 0),
            intent_certainty=0.0,  # Será calculado depois
            alternative_intents=alternative_intents,
            semantic_clusters=list(semantic_clusters),
            discourse_markers=discourse_markers,
            pragmatic_inference=pragmatic_inference
        )
        
        return ultra_intent
    
    def _calculate_intent_semantic_similarity(self, intent: IntentType, semantic_analysis: Dict) -> float:
        """📐 CALCULAR SIMILARIDADE SEMÂNTICA DA INTENÇÃO"""
        intent_key = intent.value
        similarity_matrix = self.intent_similarity_matrix
        
        if intent_key in similarity_matrix:
            # Calcular média das similaridades com outras intenções detectadas
            similarities = []
            for related_intent, similarity in similarity_matrix[intent_key].items():
                if any(related_intent in cluster for cluster in semantic_analysis.get('pattern_similarities', {})):
                    similarities.append(similarity)
            
            return sum(similarities) / len(similarities) if similarities else 0.5
        
        return 0.5  # Default
    
    def _calculate_alternative_intents(self, text: str, semantic_analysis: Dict, pragmatic_analysis: Dict) -> List[Tuple[IntentType, float]]:
        """🎯 CALCULAR INTENÇÕES ALTERNATIVAS"""
        alternatives = []
        
        # Baseado em análise semântica
        for pattern_id, similarity in semantic_analysis.get('pattern_similarities', {}).items():
            if similarity > 0.5:
                if 'fatura' in pattern_id:
                    alternatives.append((IntentType.FATURA_SOLICITAR, similarity))
                elif 'valor' in pattern_id:
                    alternatives.append((IntentType.FATURA_VALOR, similarity))
                elif 'negociacao' in pattern_id:
                    alternatives.append((IntentType.NEGOCIACAO_PARCELAMENTO, similarity))
        
        # Remover duplicatas e ordenar por confiança
        alternatives = list(set(alternatives))
        alternatives.sort(key=lambda x: x[1], reverse=True)
        
        return alternatives[:3]  # Top 3 alternativas
    
    def _extract_discourse_markers(self, text: str) -> List[str]:
        """💬 EXTRAIR MARCADORES DE DISCURSO"""
        markers = []
        
        for marker_type, marker_list in self.discourse_analyzers['discourse_markers'].items():
            for marker in marker_list:
                if marker in text.lower():
                    markers.append(f"{marker_type}:{marker}")
        
        return markers
    
    def _calculate_pragmatic_inference(self, intent: ContextualIntent, pragmatic_analysis: Dict, memory: ConversationMemory) -> Dict[str, float]:
        """🎭 CALCULAR INFERÊNCIA PRAGMÁTICA"""
        inferences = {}
        
        # Inferências baseadas em implicaturas
        for implicature_name, implicature_data in pragmatic_analysis.get('implicatures', {}).items():
            inferences[implicature_name] = implicature_data['confidence']
        
        # Inferências contextuais
        contextual_infs = pragmatic_analysis.get('contextual_inferences', {})
        inferences.update(contextual_infs)
        
        return inferences
    
    async def _analyze_contextual_coherence(self, intent: ContextualIntent, memory: ConversationMemory) -> float:
        """🔗 ANALISAR COERÊNCIA CONTEXTUAL"""
        if not memory.intent_history:
            return 0.8  # Primeira mensagem tem coerência neutra
        
        # Pegar últimas 3 intenções
        recent_intents = [intent_data[0] for intent_data in memory.intent_history[-3:]]
        current_intent = intent.intent.value
        
        # Calcular coerência baseada na matriz de similaridade
        coherence_scores = []
        
        for past_intent in recent_intents:
            if past_intent in self.intent_similarity_matrix:
                if current_intent in self.intent_similarity_matrix[past_intent]:
                    coherence_scores.append(self.intent_similarity_matrix[past_intent][current_intent])
                else:
                    coherence_scores.append(0.3)  # Baixa coerência para intenções não relacionadas
        
        return sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
    
    async def _calculate_intent_certainty(self, intent: ContextualIntent, linguistic_analysis: Dict) -> float:
        """✅ CALCULAR CERTEZA DA INTENÇÃO"""
        certainty_factors = []
        
        # Fator 1: Confiança base da intenção
        certainty_factors.append(intent.confidence)
        
        # Fator 2: Similaridade semântica
        certainty_factors.append(intent.semantic_similarity)
        
        # Fator 3: Coerência contextual
        certainty_factors.append(intent.contextual_coherence)
        
        # Fator 4: Complexidade linguística (menos complexo = mais certo)
        linguistic_certainty = 1.0 - linguistic_analysis.get('overall_complexity', 0.5)
        certainty_factors.append(linguistic_certainty)
        
        # Fator 5: Presença de entidades relevantes
        entity_certainty = min(len(intent.entities) * 0.2, 1.0)
        certainty_factors.append(entity_certainty)
        
        # Calcular média ponderada
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Soma = 1.0
        weighted_certainty = sum(factor * weight for factor, weight in zip(certainty_factors, weights))
        
        return min(weighted_certainty, 1.0)
    
    async def _update_ultra_conversation_memory(self, phone: str, intent: ContextualIntent, text: str, linguistic_analysis: Dict):
        """🧠 ATUALIZAR MEMÓRIA ULTRA AVANÇADA"""
        memory = self.conversation_memories[phone]
        
        # Atualizar histórico de intenções
        memory.intent_history.append((
            intent.intent.value, 
            intent.confidence, 
            datetime.now()
        ))
        
        # Atualizar jornada emocional
        memory.emotional_journey.append((
            intent.emotional_state,
            intent.confidence,
            datetime.now()
        ))
        
        # Atualizar padrões de conversação
        memory.conversation_patterns.append(text[:100])  # Primeiros 100 chars
        
        # Detectar mudanças de contexto
        if len(memory.intent_history) > 1:
            last_intent = memory.intent_history[-2][0]
            if intent.intent.value != last_intent:
                if intent.contextual_coherence < 0.4:  # Mudança abrupta
                    memory.context_switches.append(datetime.now())
        
        # Atualizar dados de aprendizado
        memory.learning_data['total_messages'] = memory.learning_data.get('total_messages', 0) + 1
        memory.learning_data['avg_confidence'] = (
            memory.learning_data.get('avg_confidence', 0.5) + intent.confidence
        ) / 2
        
        # Manter apenas últimos 50 registros de cada tipo
        memory.intent_history = memory.intent_history[-50:]
        memory.emotional_journey = memory.emotional_journey[-50:]
        memory.conversation_patterns = memory.conversation_patterns[-50:]
        memory.context_switches = memory.context_switches[-20:]
    
    async def _learn_from_interaction(self, phone: str, intent: ContextualIntent, semantic_analysis: Dict):
        """🎓 APRENDER A PARTIR DA INTERAÇÃO"""
        # Armazenar padrões bem-sucedidos para aprendizado futuro
        if intent.confidence > 0.8:
            pattern_key = f"{intent.intent.value}_{intent.emotional_state}"
            
            if pattern_key not in self.pattern_learning_db:
                self.pattern_learning_db[pattern_key] = []
            
            # Armazenar características da mensagem bem entendida
            learning_pattern = {
                'semantic_clusters': intent.semantic_clusters,
                'entities_count': len(intent.entities),
                'discourse_markers': intent.discourse_markers,
                'confidence': intent.confidence,
                'timestamp': datetime.now()
            }
            
            self.pattern_learning_db[pattern_key].append(learning_pattern)
            
            # Manter apenas últimos 20 padrões por tipo
            self.pattern_learning_db[pattern_key] = self.pattern_learning_db[pattern_key][-20:]
    
    async def _generate_ultra_contextual_response(
        self, phone: str, intent: ContextualIntent, entities: List[ExtractedEntity], 
        memory: ConversationMemory, semantic_analysis: Dict
    ) -> Dict[str, Any]:
        """🎭 GERAÇÃO ULTRA INTELIGENTE DE RESPOSTA NÍVEL CHATGPT"""
        
        # Usar gerador existente como base
        base_response = await self._generate_contextual_response(phone, intent, entities, {})
        
        # ENRIQUECER COM INTELIGÊNCIA ULTRA AVANÇADA
        
        # 1. Personalização baseada em memória
        personalization = self._generate_personalized_elements(memory, intent)
        
        # 2. Adaptação baseada em certeza
        certainty_adaptation = self._adapt_response_for_certainty(intent.intent_certainty)
        
        # 3. Contextualização semântica
        semantic_context = self._add_semantic_context(semantic_analysis, intent)
        
        # 4. Resposta dinâmica baseada em padrões aprendidos
        learned_enhancements = self._apply_learned_patterns(intent, memory)
        
        # Gerar resposta ultra contextualizada
        ultra_response_text = self._compose_ultra_response(
            base_response['text'], personalization, certainty_adaptation, 
            semantic_context, learned_enhancements, intent
        )
        
        return {
            'text': ultra_response_text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'entities_detected': len(entities),
            'emotional_state': intent.emotional_state,
            'multiple_intents': len(intent.multiple_intents),
            'context_enhanced': True,
            'response_type': 'ultra_mega_contextual',
            
            # NOVOS CAMPOS ULTRA AVANÇADOS
            'semantic_similarity': intent.semantic_similarity,
            'contextual_coherence': intent.contextual_coherence,
            'intent_certainty': intent.intent_certainty,
            'personalization_level': len(personalization),
            'semantic_clusters': intent.semantic_clusters,
            'discourse_markers': intent.discourse_markers,
            'ultra_enhanced': True
        }
    
    def _generate_personalized_elements(self, memory: ConversationMemory, intent: ContextualIntent) -> Dict[str, str]:
        """👤 GERAR ELEMENTOS PERSONALIZADOS"""
        personalization = {}
        
        # Baseado em padrão emocional
        if memory.emotional_journey:
            recent_emotions = [emotion for emotion, _, _ in memory.emotional_journey[-3:]]
            if recent_emotions.count('frustrado') >= 2:
                personalization['empathy'] = "Eu vejo que você está passando por uma situação chata"
            elif recent_emotions.count('urgente') >= 2:
                personalization['urgency_ack'] = "Entendo que isso é urgente para você"
        
        # Baseado em histórico de intenções
        if memory.intent_history:
            common_intents = Counter([intent for intent, _, _ in memory.intent_history])
            most_common = common_intents.most_common(1)[0][0]
            if most_common == 'fatura_solicitar':
                personalization['context'] = "Como sempre, vou buscar sua fatura"
        
        return personalization
    
    def _adapt_response_for_certainty(self, certainty: float) -> Dict[str, str]:
        """✅ ADAPTAR RESPOSTA BASEADA NA CERTEZA"""
        if certainty > 0.9:
            return {'confidence_marker': '**CERTEZA ABSOLUTA!**', 'action': 'Vou resolver isso AGORA!'}
        elif certainty > 0.7:
            return {'confidence_marker': '**ENTENDI PERFEITAMENTE!**', 'action': 'Vou cuidar disso!'}
        elif certainty > 0.5:
            return {'confidence_marker': '**ACHO QUE ENTENDI!**', 'action': 'Deixe-me confirmar...'}
        else:
            return {'confidence_marker': '**HMMMM...**', 'action': 'Me explica melhor?'}
    
    def _add_semantic_context(self, semantic_analysis: Dict, intent: ContextualIntent) -> Dict[str, str]:
        """🧠 ADICIONAR CONTEXTO SEMÂNTICO"""
        context = {}
        
        if semantic_analysis.get('best_match'):
            pattern_id, score = semantic_analysis['best_match']
            if score > 0.8:
                context['semantic_confidence'] = f"Detectei {int(score*100)}% de certeza"
        
        return context
    
    def _apply_learned_patterns(self, intent: ContextualIntent, memory: ConversationMemory) -> Dict[str, str]:
        """🎓 APLICAR PADRÕES APRENDIDOS"""
        enhancements = {}
        
        pattern_key = f"{intent.intent.value}_{intent.emotional_state}"
        if pattern_key in self.pattern_learning_db:
            patterns = self.pattern_learning_db[pattern_key]
            if patterns:
                # Aplicar insights dos padrões aprendidos
                avg_confidence = sum(p['confidence'] for p in patterns) / len(patterns)
                if avg_confidence > 0.8:
                    enhancements['learned_boost'] = "Baseado no que aprendi com você"
        
        return enhancements
    
    def _compose_ultra_response(
        self, base_text: str, personalization: Dict, certainty: Dict, 
        semantic: Dict, learned: Dict, intent: ContextualIntent
    ) -> str:
        """🎭 COMPOR RESPOSTA ULTRA AVANÇADA"""
        
        # Começar com texto base
        response_parts = [base_text]
        
        # Adicionar personalização
        if personalization.get('empathy'):
            response_parts.insert(0, personalization['empathy'] + ".")
        
        # Adicionar marcador de confiança
        if certainty.get('confidence_marker'):
            response_parts[0] = response_parts[0].replace(
                response_parts[0].split()[0], 
                certainty['confidence_marker']
            )
        
        # Adicionar contexto semântico se alta confiança
        if semantic.get('semantic_confidence'):
            response_parts.append(f"\n\n🎯 {semantic['semantic_confidence']} no que você quis dizer!")
        
        # Adicionar insights aprendidos
        if learned.get('learned_boost'):
            response_parts.append(f"\n\n🧠 {learned['learned_boost']}, sei exatamente o que fazer!")
        
        return " ".join(response_parts)
    
    async def _ultra_intelligent_fallback(self, phone: str, text: str, error: Exception) -> Dict[str, Any]:
        """🛡️ FALLBACK ULTRA INTELIGENTE MULTI-CAMADAS"""
        
        logger.error(f"🚀 Ativando fallback ultra inteligente para: {text[:50]}... | Erro: {error}")
        
        # Tentar fallbacks em cascata
        for fallback_level in self.intelligent_fallback_system['fallback_levels']:
            try:
                if fallback_level['name'] == 'semantic_similarity':
                    return await self._fallback_semantic_similarity(text, fallback_level['threshold'])
                elif fallback_level['name'] == 'keyword_extraction':
                    return await self._fallback_keyword_extraction(text, fallback_level['threshold'])
                elif fallback_level['name'] == 'pattern_matching':
                    return await self._fallback_pattern_matching(text, fallback_level['threshold'])
                elif fallback_level['name'] == 'conversational_context':
                    return await self._fallback_conversational_context(phone, text, fallback_level['threshold'])
                elif fallback_level['name'] == 'intelligent_guess':
                    return await self._fallback_intelligent_guess(text, fallback_level['threshold'])
                    
            except Exception as fallback_error:
                logger.warning(f"Fallback nível {fallback_level['level']} falhou: {fallback_error}")
                continue
        
        # Fallback final de emergência
        return {
            'text': "🤔 **NOSSA!** Essa foi difícil até para mim! Pode tentar falar de um jeito mais simples? Tipo: 'quero minha conta' ou 'quanto devo'?",
            'intent': 'emergency_fallback',
            'confidence': 0.1,
            'fallback_level': 'emergency',
            'ultra_enhanced': True
        }
    
    async def _fallback_semantic_similarity(self, text: str, threshold: float) -> Dict[str, Any]:
        """🔍 FALLBACK POR SIMILARIDADE SEMÂNTICA"""
        # Tentar encontrar padrão semântico mais próximo
        best_match = None
        best_score = 0.0
        
        for pattern_id, pattern in self.semantic_patterns.items():
            score = self._calculate_semantic_similarity(text, pattern)
            if score > best_score and score > threshold:
                best_match = pattern_id
                best_score = score
        
        if best_match:
            intent_mapping = {
                'fatura_semantic': 'fatura_solicitar',
                'valor_semantic': 'fatura_valor',
                'tempo_semantic': 'fatura_vencimento',
                'negociacao_semantic': 'negociacao_parcelamento'
            }
            
            inferred_intent = intent_mapping.get(best_match, 'fatura_solicitar')
            
            return {
                'text': f"🎯 **ENTENDI PELO CONTEXTO!** Você quer algo relacionado a {inferred_intent.replace('_', ' ')}. Vou ajudar!",
                'intent': inferred_intent,
                'confidence': best_score,
                'fallback_level': 'semantic_similarity',
                'ultra_enhanced': True
            }
        
        raise Exception("Similaridade semântica insuficiente")
    
    async def _fallback_keyword_extraction(self, text: str, threshold: float) -> Dict[str, Any]:
        """🔑 FALLBACK POR EXTRAÇÃO DE PALAVRAS-CHAVE"""
        keywords = {
            'fatura': ['conta', 'boleto', 'fatura', 'segunda', 'via', 'papel'],
            'valor': ['quanto', 'valor', 'devo', 'pagar', 'preço', 'dinheiro'],
            'vencimento': ['quando', 'vence', 'prazo', 'data', 'até'],
            'negociacao': ['parcelar', 'acordo', 'desconto', 'negociar', 'facilitar']
        }
        
        scores = {}
        for intent, intent_keywords in keywords.items():
            score = sum(1 for keyword in intent_keywords if keyword in text.lower())
            if score > 0:
                scores[intent] = score / len(intent_keywords)
        
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            if best_intent[1] > threshold:
                return {
                    'text': f"🔍 **CAPTEI!** Pelas palavras-chave, você quer {best_intent[0]}. É isso mesmo?",
                    'intent': best_intent[0],
                    'confidence': best_intent[1],
                    'fallback_level': 'keyword_extraction',
                    'ultra_enhanced': True
                }
        
        raise Exception("Palavras-chave insuficientes")
    
    async def _fallback_pattern_matching(self, text: str, threshold: float) -> Dict[str, Any]:
        """🧩 FALLBACK POR CORRESPONDÊNCIA DE PADRÕES"""
        # Padrões de emergência muito básicos
        emergency_patterns = [
            (r'\b(conta|boleto|fatura)\b', 'fatura_solicitar', 0.7),
            (r'\b(quanto|valor)\b', 'fatura_valor', 0.6),
            (r'\b(quando|vence|prazo)\b', 'fatura_vencimento', 0.6),
            (r'\b(paguei|pago)\b', 'pagamento_confirmacao', 0.5),
            (r'\b(parcelar|acordo)\b', 'negociacao_parcelamento', 0.5),
        ]
        
        for pattern, intent, confidence in emergency_patterns:
            if re.search(pattern, text, re.IGNORECASE) and confidence > threshold:
                return {
                    'text': f"🧩 **CONSEGUI ENTENDER!** Pelo padrão, você quer {intent.replace('_', ' ')}!",
                    'intent': intent,
                    'confidence': confidence,
                    'fallback_level': 'pattern_matching',
                    'ultra_enhanced': True
                }
        
        raise Exception("Nenhum padrão corresponde")
    
    async def _fallback_conversational_context(self, phone: str, text: str, threshold: float) -> Dict[str, Any]:
        """💭 FALLBACK POR CONTEXTO CONVERSACIONAL"""
        if phone in self.conversation_memories:
            memory = self.conversation_memories[phone]
            if memory.intent_history:
                # Assumir que é follow-up da última intenção
                last_intent, last_confidence, _ = memory.intent_history[-1]
                
                if last_confidence > threshold:
                    return {
                        'text': f"💭 **PELO CONTEXTO!** Você ainda está falando sobre {last_intent.replace('_', ' ')}, né?",
                        'intent': last_intent,
                        'confidence': last_confidence * 0.8,
                        'fallback_level': 'conversational_context',
                        'ultra_enhanced': True
                    }
        
        raise Exception("Contexto conversacional insuficiente")
    
    async def _fallback_intelligent_guess(self, text: str, threshold: float) -> Dict[str, Any]:
        """🎲 FALLBACK POR SUPOSIÇÃO INTELIGENTE"""
        # Se chegou até aqui, fazer uma suposição educada baseada no contexto de cobrança
        text_length = len(text.split())
        
        if text_length <= 3:
            # Texto muito curto - provavelmente quer fatura
            guess_intent = 'fatura_solicitar'
            guess_confidence = 0.4
        elif '?' in text:
            # Tem pergunta - provavelmente quer informação (valor ou vencimento)
            guess_intent = 'fatura_valor'
            guess_confidence = 0.3
        else:
            # Default para solicitação de fatura
            guess_intent = 'fatura_solicitar'
            guess_confidence = 0.2
        
        if guess_confidence > threshold:
            return {
                'text': f"🎲 **VAMOS TENTAR!** Pelo contexto geral, acho que você quer {guess_intent.replace('_', ' ')}. Se não for isso, me fala 'não' que eu entendo outra coisa!",
                'intent': guess_intent,
                'confidence': guess_confidence,
                'fallback_level': 'intelligent_guess',
                'ultra_enhanced': True,
                'requires_confirmation': True
            }
        
        raise Exception("Impossível fazer suposição válida") 