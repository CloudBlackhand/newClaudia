"""
🤖 CLAUDIA DA DESK - VERSÃO SIMPLIFICADA PARA RAILWAY
Sistema de IA conversacional otimizado sem PyTorch
"""
import json
import re
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from backend.config.settings import active_config
from backend.utils.logger import conversation_logger, app_logger
from backend.models.conversation import ConversationContext

class SimpleBrazilianNormalizer:
    """Normalizador simples de texto brasileiro"""
    
    def __init__(self):
        self.abbreviations = {
            "vc": "você", "q": "que", "td": "tudo", "mt": "muito",
            "blz": "beleza", "vlw": "valeu", "obg": "obrigado",
            "hj": "hoje", "onti": "ontem", "nao": "não", "eh": "é",
            "pra": "para", "ta": "está", "to": "estou",
            "paguei": "paguei", "pix": "pix", "boleto": "boleto"
        }
    
    def normalize(self, text: str) -> str:
        """Normaliza texto básico"""
        if not text:
            return ""
        
        normalized = text.lower().strip()
        
        # Aplica abreviações
        words = normalized.split()
        corrected_words = []
        
        for word in words:
            clean_word = re.sub(r'[.,!?]', '', word)
            if clean_word in self.abbreviations:
                corrected_word = self.abbreviations[clean_word]
                if word != clean_word:
                    corrected_word += word[len(clean_word):]
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)

class SimpleEmotionalAnalyzer:
    """Analisador emocional simples"""
    
    def __init__(self):
        self.emotions = {
            "raiva": ["puto", "irritado", "raiva", "bravo", "nervoso"],
            "tristeza": ["triste", "down", "deprimido", "difícil"],
            "alegria": ["feliz", "ótimo", "perfeito", "show", "massa"],
            "medo": ["preocupado", "nervoso", "ansioso", "medo"]
        }
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analisa emoção simples"""
        text_lower = text.lower()
        
        for emotion, keywords in self.emotions.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return {
                        "primary_emotion": emotion,
                        "intensity": 0.7,
                        "confidence": 0.8,
                        "indicators": [keyword]
                    }
        
        return {
            "primary_emotion": "neutro",
            "intensity": 0.0,
            "confidence": 0.8,
            "indicators": []
        }

class SimpleBillingChatBot:
    """🤖 CLAUDIA DA DESK SIMPLIFICADA - SEM PYTORCH"""
    
    def __init__(self):
        self.config = active_config
        self.normalizer = SimpleBrazilianNormalizer()
        self.emotion_analyzer = SimpleEmotionalAnalyzer()
        
        # Intents simples
        self.intents = {
            "saudacao": ["oi", "ola", "bom dia", "boa tarde", "e ai", "eae"],
            "confirmacao_pagamento": ["paguei", "pix", "transferi", "ja pago", "quitei"],
            "negociacao": ["parcelar", "desconto", "sem dinheiro", "negociar", "acordo"],
            "informacoes": ["quanto", "valor", "como pagar", "dados", "info"],
            "contestacao": ["erro", "nao devo", "golpe", "engano", "fraude"],
            "despedida": ["tchau", "obrigado", "valeu", "vlw", "ate logo"]
        }
        
        # Respostas da Claudia
        self.responses = {
            "saudacao": [
                "Oi! Sou a Claudia da Desk! 😊 Como posso te ajudar hoje?",
                "Olá! Claudia aqui! Estou aqui pra resolver sua situação!"
            ],
            "confirmacao_pagamento": [
                "Que ótimo! 🎉 Vou verificar seu pagamento no sistema!",
                "Perfeito! Já anotei. Vou confirmar tudo pra você!"
            ],
            "negociacao": [
                "Entendo sua situação! 💙 Vamos achar uma solução boa pra você.",
                "Sem estresse! A gente sempre dá um jeito!"
            ],
            "informacoes": [
                "Claro! Vou te passar todas as informações! 📋",
                "Sem problema! Deixa eu buscar seus dados..."
            ],
            "contestacao": [
                "Nossa! 😮 Vou verificar isso urgente pra você!",
                "Que estranho! Vamos esclarecer isso já!"
            ],
            "despedida": [
                "Valeu! 👋 Qualquer coisa me chama!",
                "Até logo! Foi um prazer te ajudar! 😊"
            ],
            "default": [
                "Hmm, não entendi muito bem... 🤔 Pode me explicar de outro jeito?",
                "Desculpa, pode reformular sua pergunta?"
            ]
        }
        
        app_logger.info("🤖 CLAUDIA SIMPLIFICADA INICIALIZADA", {
            "version": "simple",
            "pytorch": False
        })
    
    async def process_message(self, message: str, context: ConversationContext, user_id: str = None) -> Dict[str, Any]:
        """Processa mensagem de forma simplificada"""
        
        result = {
            "response": "",
            "intent": "default",
            "confidence": 0.0,
            "entities": {},
            "actions": []
        }
        
        try:
            # Normalização simples
            clean_message = self.normalizer.normalize(message)
            
            # Análise emocional
            emotional_state = self.emotion_analyzer.analyze(clean_message)
            
            # Classificação de intent simples
            intent = self._classify_intent(clean_message)
            result["intent"] = intent
            result["confidence"] = 0.8
            
            # Geração de resposta
            response = self._generate_response(intent, emotional_state, context)
            result["response"] = response
            
            # Ações simples
            result["actions"] = self._get_actions(intent)
            
            conversation_logger.info("SIMPLE_MESSAGE_PROCESSED", {
                "intent": intent,
                "emotion": emotional_state["primary_emotion"]
            })
            
        except Exception as e:
            app_logger.error("SIMPLE_PROCESSING_ERROR", e)
            result["response"] = "Desculpe, tive um problema. Pode repetir?"
            result["intent"] = "error"
        
        return result
    
    def _classify_intent(self, message: str) -> str:
        """Classificação simples de intent"""
        message_lower = message.lower()
        
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return "default"
    
    def _generate_response(self, intent: str, emotional_state: Dict, context: ConversationContext) -> str:
        """Gera resposta simples"""
        templates = self.responses.get(intent, self.responses["default"])
        base_response = random.choice(templates)
        
        # Adaptação emocional básica
        emotion = emotional_state["primary_emotion"]
        
        if emotion == "raiva":
            base_response = "Entendo sua irritação! " + base_response
        elif emotion == "tristeza":
            base_response = "Imagino como deve estar difícil... " + base_response
        elif emotion == "alegria":
            base_response = "Que bom ver você animado! " + base_response
        
        # Personalização com nome
        if context.client_name:
            name = context.client_name.split()[0]
            base_response = base_response.replace("você", f"você, {name}")
        
        return base_response
    
    def _get_actions(self, intent: str) -> List[str]:
        """Retorna ações simples"""
        actions_map = {
            "confirmacao_pagamento": ["verificar_pagamento"],
            "negociacao": ["oferecer_parcelamento"],
            "contestacao": ["escalate_to_human"],
            "informacoes": ["enviar_dados"]
        }
        
        return actions_map.get(intent, [])

# Instância global
simple_chatbot = SimpleBillingChatBot()
