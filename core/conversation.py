#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Conversação - Claudia Cobranças
Versão simplificada e funcional
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class IntentType(Enum):
    FATURA_SOLICITAR = "fatura_solicitar"
    PAGAMENTO_CONFIRMACAO = "pagamento_confirmacao"
    SAUDACAO = "saudacao"
    DESPEDIDA = "despedida"
    DESCONHECIDO = "desconhecido"

@dataclass
class ConversationIntent:
    intent: IntentType
    confidence: float
    emotional_state: str = "neutro"

class SuperConversationEngine:
    """🧠 Sistema de Conversação - Claudia Cobranças"""
    
    def __init__(self):
        self.name = "Claudia Cobranças"
        logger.info("🧠 SuperConversationEngine inicializado")
    
    def process_message(self, message: str, user_context: Optional[Dict] = None) -> Dict[str, Any]:
        """🔄 Processamento da mensagem"""
        try:
            # Normalizar
            normalized = message.lower().strip()
            
            # Detectar intenção
            if any(word in normalized for word in ['fatura', 'boleto', 'segunda via']):
                intent = IntentType.FATURA_SOLICITAR
                response = "📄 **PERFEITO!** Vou buscar sua fatura! Aguarde um momento..."
                actions = ["enviar_fatura"]
            elif any(word in normalized for word in ['paguei', 'pago', 'pagamento']):
                intent = IntentType.PAGAMENTO_CONFIRMACAO
                response = "✅ **BELEZA!** Vou verificar seu pagamento no sistema!"
                actions = ["verificar_pagamento"]
            elif any(word in normalized for word in ['oi', 'ola', 'bom dia']):
                intent = IntentType.SAUDACAO
                response = "👋 **OLÁ!** Como posso te ajudar hoje?"
                actions = []
            elif any(word in normalized for word in ['tchau', 'obrigado', 'valeu']):
                intent = IntentType.DESPEDIDA
                response = "👋 **VALEU!** Qualquer coisa, me chama!"
                actions = []
            else:
                intent = IntentType.DESCONHECIDO
                response = "🤔 Posso te ajudar com sua **FATURA** ou **PAGAMENTO**!"
                actions = []
            
            return {
                "success": True,
                "response": response,
                "intent": intent.value,
                "confidence": 0.8,
                "actions": actions
            }
            
        except Exception as e:
            logger.error(f"❌ Erro: {e}")
            return {
                "success": False,
                "response": "😅 Pode repetir sua mensagem?",
                "intent": "erro",
                "confidence": 0.0,
                "actions": []
            }

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 SUPER ENGINE DE CONVERSAÇÃO - COMPREENSÃO 100% CONTEXTUAL
Sistema que entende TUDO que o cliente fala - sem IA externa
"""

import re
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum

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
    """Entidade extraída do texto"""
    type: str
    value: str
    confidence: float
    context: str

@dataclass
class ContextualIntent:
    """Intenção com contexto completo"""
    intent: IntentType
    confidence: float
    entities: List[ExtractedEntity]
    temporal_context: str  # passado, presente, futuro
    emotional_state: str   # neutro, frustrado, satisfeito, urgente
    negation: bool        # se há negação
    multiple_intents: List[IntentType]  # intenções secundárias

class SuperConversationEngine:
    """🧠 SUPER ENGINE - Compreensão contextual revolucionária"""
    
    def __init__(self):
        self.user_contexts = {}
        self.conversation_cache = {}
        
        # Banco de conhecimento linguístico brasileiro
        self.brazilian_language_db = self._load_brazilian_language_patterns()
        self.entity_extractors = self._load_entity_extractors()
        self.context_analyzers = self._load_context_analyzers()
        self.emotion_patterns = self._load_emotion_patterns()
        self.temporal_patterns = self._load_temporal_patterns()
        self.negation_patterns = self._load_negation_patterns()
        
        # Respostas contextuais avançadas
        self.contextual_responses = self._load_contextual_responses()
        
        logger.info("🧠 Super Engine de Conversação inicializada!")
        
    def _load_brazilian_language_patterns(self) -> Dict[str, List[Dict]]:
        """Padrões específicos da linguagem coloquial brasileira"""
        return {
            'gírias_fatura': [
                {'pattern': r'(conta|boleto|fatura|cobrança)', 'weight': 1.0},
                {'pattern': r'(segunda via|2ª via)', 'weight': 1.0},
                {'pattern': r'(pagar|pagamento|quitar)', 'weight': 0.8},
                {'pattern': r'(dever|deve|devo)', 'weight': 0.7},
                {'pattern': r'(vencimento|vence|prazo)', 'weight': 0.6},
            ],
            'gírias_negociação': [
                {'pattern': r'(parcelar|dividir|fatiar)', 'weight': 1.0},
                {'pattern': r'(acordo|negociar|conversar)', 'weight': 0.9},
                {'pattern': r'(desconto|abatimento|reduzir)', 'weight': 0.8},
                {'pattern': r'(condições|facilitar)', 'weight': 0.7},
                {'pattern': r'(apertar|apertado|dificuldade)', 'weight': 0.6},
            ],
            'gírias_reclamação': [
                {'pattern': r'(errado|incorreto|equivocado)', 'weight': 1.0},
                {'pattern': r'(nunca (usei|contratei|pedi))', 'weight': 0.9},
                {'pattern': r'(cobrança indevida|não devo)', 'weight': 0.9},
                {'pattern': r'(contestar|discordar|reclamar)', 'weight': 0.8},
                {'pattern': r'(problema|erro|confusão)', 'weight': 0.7},
            ],
            'linguagem_coloquial': [
                # Brasileirismos comuns
                {'pattern': r'(oi|olá|e aí|beleza)', 'intent': 'saudacao', 'weight': 1.0},
                {'pattern': r'(valeu|obrigad[ao]|vlw)', 'intent': 'agradecimento', 'weight': 1.0},
                {'pattern': r'(tchau|falou|até|flw)', 'intent': 'despedida', 'weight': 1.0},
                {'pattern': r'(né|né não|num é)', 'intent': 'confirmacao', 'weight': 0.5},
                {'pattern': r'(tá bom|ok|certo)', 'intent': 'confirmacao', 'weight': 0.8},
                {'pattern': r'(não|num|nope)', 'intent': 'negacao', 'weight': 0.9},
                {'pattern': r'(como assim|que isso|ué)', 'intent': 'duvida', 'weight': 0.8},
            ]
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
    
    # Função assíncrona removida para evitar conflito com a função síncrona
    
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
        """Análise de intenções base com linguagem brasileira MELHORADA"""
        intent_scores = {}
        
        # ANÁLISE FATURA - Separando subcategorias
        fatura_solicitar_score = 0.0
        fatura_valor_score = 0.0  # NOVA CATEGORIA
        fatura_vencimento_score = 0.0  # NOVA CATEGORIA
        
        # Solicitações DIRETAS de fatura
        if re.search(r'(preciso|quero|gostaria).*(fatura|conta|boleto)', text, re.IGNORECASE):
            fatura_solicitar_score += 0.9
        if re.search(r'(mandar?|enviar?).*(fatura|conta)', text, re.IGNORECASE):
            fatura_solicitar_score += 0.85
        if re.search(r'(segunda|2ª).*(via)', text, re.IGNORECASE):
            fatura_solicitar_score += 0.95
        
        # Perguntas sobre VALOR (nova categoria específica)
        if re.search(r'(quanto|valor).*(devo|pagar|deve)', text, re.IGNORECASE):
            fatura_valor_score += 0.9  # MELHORADO
        if re.search(r'(quanto.*mesmo|valor.*conta)', text, re.IGNORECASE):
            fatura_valor_score += 0.8
        if re.search(r'(devo.*quanto|pagar.*quanto)', text, re.IGNORECASE):
            fatura_valor_score += 0.85
        
        # Perguntas sobre VENCIMENTO (nova categoria específica)
        if re.search(r'(vencimento|prazo).*(pagamento)', text, re.IGNORECASE):
            fatura_vencimento_score += 0.8
        if re.search(r'(quando.*vence|prazo.*conta)', text, re.IGNORECASE):
            fatura_vencimento_score += 0.85
        
        # Contextos indiretos mas claros
        if re.search(r'(situação|status).*(conta)', text, re.IGNORECASE):
            fatura_solicitar_score += 0.65
        
        # Linguagem coloquial brasileira
        if re.search(r'(pagar|quitar)', text, re.IGNORECASE):
            # Se tem "quanto", é valor, senão é solicitação geral
            if re.search(r'(quanto)', text, re.IGNORECASE):
                fatura_valor_score += 0.6
            else:
                fatura_solicitar_score += 0.5
        if re.search(r'(minha conta|meu boleto)', text, re.IGNORECASE):
            fatura_solicitar_score += 0.6
        
        intent_scores['fatura_solicitar'] = fatura_solicitar_score
        intent_scores['fatura_valor'] = fatura_valor_score  # NOVA
        intent_scores['fatura_vencimento'] = fatura_vencimento_score  # NOVA
        
        # ANÁLISE NEGOCIAÇÃO - Separando subcategorias
        negociacao_parcelamento_score = 0.0
        negociacao_desconto_score = 0.0
        
        if re.search(r'(parcelar|dividir|fatiar)', text, re.IGNORECASE):
            negociacao_parcelamento_score += 0.9
        if re.search(r'(acordo|negociar)', text, re.IGNORECASE):
            negociacao_parcelamento_score += 0.6  # Pode ser tanto parcelamento quanto desconto
            negociacao_desconto_score += 0.4
        if re.search(r'(desconto|abatimento)', text, re.IGNORECASE):
            negociacao_desconto_score += 0.9
        if re.search(r'(dificuldade|apertado|difícil).*(pagar)', text, re.IGNORECASE):
            negociacao_parcelamento_score += 0.7  # Mais provável parcelamento
        if re.search(r'(condições|facilitar)', text, re.IGNORECASE):
            negociacao_parcelamento_score += 0.6
        
        intent_scores['negociacao_parcelamento'] = negociacao_parcelamento_score
        intent_scores['negociacao_desconto'] = negociacao_desconto_score
        
        # ANÁLISE CONFIRMAÇÃO PAGAMENTO  
        pagamento_score = 0.0
        
        if re.search(r'(já\s+paguei|quitei|paguei)', text, re.IGNORECASE):
            pagamento_score += 0.9
        if re.search(r'(efetuei|realizei).*(pagamento|transferência)', text, re.IGNORECASE):
            pagamento_score += 0.85
        if re.search(r'(pix|transferência|depósito)', text, re.IGNORECASE):
            pagamento_score += 0.7
        if re.search(r'(comprovante|anexo)', text, re.IGNORECASE):
            pagamento_score += 0.6
        
        intent_scores['pagamento_confirmacao'] = pagamento_score
        
        # ANÁLISE RECLAMAÇÃO - Melhorada para detectar frustração
        reclamacao_indevida_score = 0.0
        reclamacao_valor_score = 0.0
        
        if re.search(r'(errado|incorreto|equivocado)', text, re.IGNORECASE):
            reclamacao_valor_score += 0.8
        if re.search(r'(nunca\s+(usei|contratei|pedi))', text, re.IGNORECASE):
            reclamacao_indevida_score += 0.9
        if re.search(r'(indevid[ao]|não\s+devo)', text, re.IGNORECASE):
            reclamacao_indevida_score += 0.85
        if re.search(r'(contestar|discordar)', text, re.IGNORECASE):
            reclamacao_indevida_score += 0.8
        
        intent_scores['reclamacao_cobranca_indevida'] = reclamacao_indevida_score
        intent_scores['reclamacao_valor_incorreto'] = reclamacao_valor_score
        
        # BOOST BASEADO EM ENTIDADES
        if any(e.type == 'valores_monetarios' for e in entities):
            intent_scores['fatura_valor'] = intent_scores.get('fatura_valor', 0) + 0.4
            intent_scores['pagamento_confirmacao'] = intent_scores.get('pagamento_confirmacao', 0) + 0.3
        
        if any(e.type == 'datas' for e in entities):
            intent_scores['fatura_vencimento'] = intent_scores.get('fatura_vencimento', 0) + 0.4
        
        # BOOST BASEADO EM EMOÇÃO - CORRIGIDO
        if emotion == 'frustrado':
            intent_scores['reclamacao_cobranca_indevida'] = intent_scores.get('reclamacao_cobranca_indevida', 0) + 0.3
            intent_scores['reclamacao_valor_incorreto'] = intent_scores.get('reclamacao_valor_incorreto', 0) + 0.3
        
        if emotion == 'urgente':
            intent_scores['fatura_solicitar'] = intent_scores.get('fatura_solicitar', 0) + 0.2
        
        # Detectar saudações e despedidas
        if re.search(r'(oi|olá|bom\s+dia|boa\s+(tarde|noite)|e\s+aí)', text, re.IGNORECASE):
            intent_scores['saudacao'] = 0.9
        
        if re.search(r'(tchau|até|obrigad[ao]|valeu|flw)', text, re.IGNORECASE):
            intent_scores['despedida'] = 0.8
        
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
        """Normalização super inteligente"""
        # Preservar acentos e características brasileiras
        text = text.lower()
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        # Remover pontuação excessiva mas preservar sentido
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
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
        """Gerar resposta super contextual"""
        
        # Responses baseadas na análise completa
        if intent.intent == IntentType.FATURA_SOLICITAR:
            if intent.emotional_state == 'urgente':
                response_text = "🚨 Entendi que é urgente! Vou localizar sua fatura agora mesmo."
            elif intent.negation:
                response_text = "🤔 Vi que você mencionou 'não' - pode esclarecer o que precisa sobre a fatura?"
            else:
                response_text = "📄 Claro! Vou providenciar sua fatura."
        
        elif intent.intent == IntentType.NEGOCIACAO_PARCELAMENTO:
            if any(e.type == 'valores_monetarios' for e in entities):
                valor = next(e.value for e in entities if e.type == 'valores_monetarios')
                response_text = f"💰 Entendi que você quer parcelar o valor de R$ {valor}. Vamos encontrar uma solução!"
            else:
                response_text = "🤝 Vamos conversar sobre as opções de parcelamento disponíveis!"
        
        elif intent.intent == IntentType.PAGAMENTO_CONFIRMACAO:
            if intent.temporal_context == 'passado':
                response_text = "✅ Você mencionou que já pagou. Vou verificar o status do seu pagamento!"
            else:
                response_text = "💳 Vou confirmar o status do seu pagamento."
        
        elif intent.intent == IntentType.RECLAMACAO_COBRANCA_INDEVIDA:
            if intent.emotional_state == 'frustrado':
                response_text = "😔 Entendo sua frustração com essa cobrança. Vamos resolver isso imediatamente!"
            else:
                response_text = "🔍 Vou analisar essa cobrança para você."
        
        else:
            response_text = "🤖 Entendi seu contexto. Como posso ajudar especificamente?"
        
        # Adicionar informações sobre múltiplas intenções
        if intent.multiple_intents:
            response_text += f"\n\n📋 Também percebi que você quer: {', '.join([i.value.replace('_', ' ') for i in intent.multiple_intents])}"
        
        return {
            'text': response_text,
            'intent': intent.intent.value,
            'confidence': intent.confidence,
            'entities_detected': len(entities),
            'emotional_state': intent.emotional_state,
            'multiple_intents': len(intent.multiple_intents),
            'context_enhanced': True
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