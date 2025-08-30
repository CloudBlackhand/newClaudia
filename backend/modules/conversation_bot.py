"""
Bot de Conversação Avançado - IA Própria Suprema
Sistema de IA conversacional comparável ao ChatGPT
Desenvolvido para ser a Claudia da Desk transformada em sistema SUPREMO
"""
import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
from collections import defaultdict, deque
import unicodedata

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    """Contexto da conversa"""
    session_id: str
    user_phone: str
    conversation_history: List[Dict[str, Any]]
    user_intent: str
    sentiment: str
    entities: Dict[str, Any]
    last_interaction: datetime
    conversation_stage: str
    user_profile: Dict[str, Any]

@dataclass
class BotResponse:
    """Resposta do bot"""
    message: str
    intent: str
    confidence: float
    suggested_actions: List[str]
    requires_human: bool
    context_update: Dict[str, Any]

class NaturalLanguageProcessor:
    """Processador de linguagem natural avançado"""
    
    def __init__(self):
        # Padrões de intenção - expandidos para ser mais inteligente
        self.intent_patterns = {
            "pagamento_realizado": [
                r"j[aá]\s*pagu?ei",
                r"fiz\s*o\s*pagamento",
                r"efetuei\s*o\s*pagamento",
                r"quitei",
                r"acabei\s*de\s*pagar",
                r"transferi",
                r"depositei",
                r"pix\s*feito",
                r"boleto\s*pago",
                r"cart[aã]o\s*debitado"
            ],
            "solicitacao_dados": [
                r"dados\s*banc[aá]rios",
                r"como\s*pagar",
                r"onde\s*pagar",
                r"n[uú]mero\s*da\s*conta",
                r"chave\s*pix",
                r"qr\s*code",
                r"boleto",
                r"forma\s*de\s*pagamento"
            ],
            "questionamento_divida": [
                r"n[aã]o\s*devo",
                r"erro",
                r"engano",
                r"n[aã]o\s*[eé]\s*minha",
                r"contestar",
                r"n[aã]o\s*comprei",
                r"fraude",
                r"cancelei"
            ],
            "negociacao": [
                r"desconto",
                r"parcel[ao]",
                r"negociar",
                r"condi[cç][oõ]es",
                r"prazo",
                r"entrada",
                r"facilitar",
                r"acordo"
            ],
            "dificuldade_financeira": [
                r"sem\s*dinheiro",
                r"desempregado",
                r"dificuldade",
                r"crise",
                r"n[aã]o\s*consigo",
                r"impossível",
                r"parado",
                r"sem\s*renda"
            ],
            "prazo_pagamento": [
                r"quando\s*vence",
                r"prazo",
                r"at[eé]\s*quando",
                r"data\s*limite",
                r"vencimento",
                r"urgente"
            ],
            "informacoes_gerais": [
                r"o\s*que\s*[eé]",
                r"explica",
                r"n[aã]o\s*entendi",
                r"como\s*assim",
                r"que\s*hist[oó]ria",
                r"detalhes"
            ],
            "saudacao": [
                r"ol[aá]",
                r"oi",
                r"bom\s*dia",
                r"boa\s*tarde",
                r"boa\s*noite",
                r"e\s*a[ií]"
            ],
            "despedida": [
                r"tchau",
                r"valeu",
                r"obrigad[oa]",
                r"brigad[oa]",
                r"falou",
                r"at[eé]\s*mais"
            ],
            "confirmacao": [
                r"sim",
                r"claro",
                r"[eé]\s*isso",
                r"correto",
                r"perfeito",
                r"ok",
                r"certo"
            ],
            "negacao": [
                r"n[aã]o",
                r"nunca",
                r"jamais",
                r"nem",
                r"nada"
            ]
        }
        
        # Entidades que o bot pode extrair
        self.entity_patterns = {
            "valor": r"R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)",
            "data": r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            "cpf": r"(\d{3}\.?\d{3}\.?\d{3}\-?\d{2})",
            "telefone": r"(\(?(?:\+55\s?)?(?:\d{2})\)?\s?\d{4,5}\-?\d{4})",
            "email": r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        }
        
        # Análise de sentimentos
        self.positive_words = [
            "bom", "ótimo", "perfeito", "certo", "sim", "claro", "obrigado",
            "valeu", "beleza", "tranquilo", "ok", "legal", "massa"
        ]
        
        self.negative_words = [
            "não", "ruim", "péssimo", "erro", "problema", "dificuldade",
            "impossível", "nunca", "jamais", "odio", "raiva", "chato"
        ]
        
        self.neutral_words = [
            "talvez", "pode", "ser", "quem", "sabe", "depende", "veremos"
        ]
    
    def analyze_intent(self, message: str) -> Tuple[str, float]:
        """Analisar intenção da mensagem"""
        message_clean = self._clean_text(message)
        
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, message_clean, re.IGNORECASE))
                score += matches
            
            if score > 0:
                # Normalizar score
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return "informacoes_gerais", 0.5
        
        # Retornar intenção com maior score
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent], 1.0)
        
        return best_intent, confidence
    
    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Extrair entidades da mensagem"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, message, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        
        return entities
    
    def analyze_sentiment(self, message: str) -> str:
        """Analisar sentimento da mensagem"""
        message_clean = self._clean_text(message)
        words = message_clean.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        if positive_count > negative_count:
            return "positivo"
        elif negative_count > positive_count:
            return "negativo"
        else:
            return "neutro"
    
    def _clean_text(self, text: str) -> str:
        """Limpar e normalizar texto"""
        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Remover caracteres especiais, manter espaços e hífens
        text = re.sub(r'[^\w\s\-]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

class ConversationBot:
    """Bot de conversação avançado com IA própria"""
    
    def __init__(self, logger_system):
        self.logger_system = logger_system
        self.nlp = NaturalLanguageProcessor()
        self.active_sessions = {}
        self.conversation_memory = defaultdict(deque)
        self.is_initialized = False
        
        # Templates de resposta inteligentes
        self.response_templates = {
            "saudacao": [
                "Olá! 👋 Sou a Claudia, assistente de cobrança da empresa. Como posso ajudá-lo hoje?",
                "Oi! 😊 Aqui é a Claudia. Estou aqui para esclarecer sobre seu pagamento pendente.",
                "Olá! Tudo bem? Sou a Claudia e vou te ajudar com as informações sobre sua conta."
            ],
            "pagamento_realizado": [
                "Que ótima notícia! 🎉 Você confirma que realizou o pagamento? Se puder, me envie o comprovante para agilizarmos a baixa.",
                "Perfeito! 👏 Para confirmarmos rapidamente, você poderia me enviar uma foto do comprovante?",
                "Excelente! 😊 Vou registrar seu pagamento. Caso tenha o comprovante, seria ótimo para confirmarmos mais rápido."
            ],
            "solicitacao_dados": [
                "Claro! Aqui estão os dados para pagamento:\n\n💳 **Dados PIX:**\nChave: empresa@exemplo.com\n\n🏦 **Dados Bancários:**\nBanco: 123\nAgência: 1234\nConta: 12345-6\n\nPrefere qual forma?",
                "Sem problemas! Temos as seguintes opções:\n\n📱 **PIX** (mais rápido)\nChave: empresa@exemplo.com\n\n🏦 **Transferência**\nBanco 123 | Ag: 1234 | CC: 12345-6\n\nQual prefere?",
                "Posso te ajudar com os dados! 😊\n\n**Para PIX:** empresa@exemplo.com\n**Para transferência:** Banco 123, Ag 1234, CC 12345-6\n\nQual forma é melhor para você?"
            ],
            "questionamento_divida": [
                "Entendo sua preocupação. 🤔 Vamos esclarecer isso! Você pode me informar seu CPF para verificarmos os detalhes da conta?",
                "Sem problemas! 😊 Vamos verificar essa informação. Pode me passar seu CPF ou email cadastrado para localizarmos sua conta?",
                "Claro, vamos esclarecer! 👍 Para verificar sua situação, preciso do seu CPF ou dados cadastrais. Pode me informar?"
            ],
            "negociacao": [
                "Entendo! 😊 Temos algumas opções que podem te ajudar. Que tipo de negociação você tinha em mente?",
                "Perfeito! 👍 Vamos encontrar uma solução que funcione para você. Me conta qual seria a melhor condição?",
                "Ótimo! 🤝 Queremos facilitar para você. Que tipo de acordo seria ideal? Parcelamento, desconto, prazo?"
            ],
            "dificuldade_financeira": [
                "Compreendo sua situação. 🤗 Todos passamos por momentos difíceis. Vamos encontrar uma solução juntos, ok?",
                "Entendo perfeitamente. 😔 Vamos ver como podemos te ajudar a resolver isso de forma mais tranquila.",
                "Sei como é difícil. 💙 Queremos encontrar uma forma de resolver que não comprometa ainda mais seu orçamento."
            ],
            "prazo_pagamento": [
                "Sua conta vence no dia {vencimento}. ⏰ Ainda temos alguns dias para resolver, não se preocupe!",
                "O vencimento é {vencimento}. 📅 Que tal acertarmos antes para evitar juros?",
                "Vence em {vencimento}. ⌛ Prefere pagar à vista ou negociar condições?"
            ],
            "informacoes_gerais": [
                "Claro! 😊 Estou aqui para esclarecer qualquer dúvida. O que exatamente você gostaria de saber?",
                "Sem problemas! 👍 Pode me perguntar o que quiser sobre sua conta ou pagamento.",
                "Claro! 🤓 Estou aqui para isso. Qual informação específica você precisa?"
            ],
            "despedida": [
                "Foi um prazer ajudar! 😊 Qualquer dúvida, estarei aqui. Tenha um ótimo dia!",
                "Obrigada! 👋 Estou sempre aqui se precisar. Cuide-se!",
                "Até mais! 😊 Espero ter ajudado. Volte sempre que precisar!"
            ],
            "confirmacao": [
                "Perfeito! 👍 Entendi. Vamos prosseguir então!",
                "Ótimo! 😊 Vamos continuar.",
                "Beleza! 👏 Entendido!"
            ],
            "negacao": [
                "Entendo. 🤔 Que tal me contar mais sobre a situação?",
                "Ok, sem problemas. 😊 Como posso te ajudar então?",
                "Tudo bem! 👍 Vamos encontrar outra solução."
            ],
            "default": [
                "Interessante! 🤔 Me conta mais sobre isso para eu entender melhor como posso ajudar.",
                "Hmm, entendi! 😊 Você pode me dar mais detalhes para eu te ajudar da melhor forma?",
                "Legal! 👍 Explica mais um pouquinho para eu entender sua situação."
            ]
        }
        
        # Estágios da conversa
        self.conversation_stages = {
            "inicial": "apresentacao",
            "identificacao": "coletando_dados",
            "esclarecimento": "resolvendo_duvidas",
            "negociacao": "discutindo_termos",
            "finalizacao": "concluindo"
        }
    
    async def initialize(self):
        """Inicializar o bot"""
        try:
            logger.info("Inicializando ConversationBot...")
            
            # Carregar contextos salvos se existirem
            await self._load_conversation_contexts()
            
            self.is_initialized = True
            logger.info("ConversationBot inicializado com sucesso!")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar ConversationBot: {str(e)}")
            raise
    
    async def cleanup(self):
        """Limpeza do bot"""
        # Salvar contextos ativos
        await self._save_conversation_contexts()
        self.is_initialized = False
        logger.info("ConversationBot finalizado")
    
    def is_healthy(self) -> bool:
        """Verificação de saúde"""
        return self.is_initialized
    
    async def process_message(self, user_phone: str, message: str, context: Optional[Dict[str, Any]] = None) -> BotResponse:
        """
        Processar mensagem do usuário e gerar resposta inteligente
        
        Args:
            user_phone: Telefone do usuário
            message: Mensagem recebida
            context: Contexto adicional (dados de cobrança, etc.)
            
        Returns:
            Resposta do bot com contexto atualizado
        """
        try:
            # Obter ou criar contexto da conversa
            session_id = f"session_{user_phone}"
            conversation_context = await self._get_or_create_context(session_id, user_phone)
            
            # Processar mensagem com NLP
            intent, confidence = self.nlp.analyze_intent(message)
            entities = self.nlp.extract_entities(message)
            sentiment = self.nlp.analyze_sentiment(message)
            
            # Atualizar contexto
            conversation_context.user_intent = intent
            conversation_context.sentiment = sentiment
            conversation_context.entities.update(entities)
            conversation_context.last_interaction = datetime.now()
            
            # Adicionar mensagem ao histórico
            conversation_context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "user",
                "message": message,
                "intent": intent,
                "sentiment": sentiment,
                "entities": entities
            })
            
            # Gerar resposta inteligente
            response = await self._generate_intelligent_response(
                conversation_context, 
                intent, 
                confidence,
                context
            )
            
            # Adicionar resposta ao histórico
            conversation_context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "type": "bot",
                "message": response.message,
                "intent": response.intent,
                "confidence": response.confidence
            })
            
            # Atualizar contexto
            conversation_context.conversation_stage = self._determine_next_stage(
                conversation_context.conversation_stage, intent
            )
            
            # Salvar contexto atualizado
            self.active_sessions[session_id] = conversation_context
            
            # Log da conversa
            await self.logger_system.log_conversation(
                session_id, message, response.message, asdict(conversation_context)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return BotResponse(
                message="Desculpe, tive um problema técnico. Pode repetir sua mensagem?",
                intent="erro",
                confidence=0.0,
                suggested_actions=["repetir_mensagem"],
                requires_human=True,
                context_update={}
            )
    
    async def _get_or_create_context(self, session_id: str, user_phone: str) -> ConversationContext:
        """Obter ou criar contexto da conversa"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            # Verificar se a sessão não expirou (24 horas)
            if datetime.now() - context.last_interaction < timedelta(hours=24):
                return context
        
        # Criar novo contexto
        return ConversationContext(
            session_id=session_id,
            user_phone=user_phone,
            conversation_history=[],
            user_intent="",
            sentiment="neutro",
            entities={},
            last_interaction=datetime.now(),
            conversation_stage="inicial",
            user_profile={}
        )
    
    async def _generate_intelligent_response(
        self, 
        context: ConversationContext, 
        intent: str, 
        confidence: float,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> BotResponse:
        """Gerar resposta inteligente baseada no contexto"""
        
        # Determinar template base
        templates = self.response_templates.get(intent, self.response_templates["default"])
        
        # Selecionar template baseado no histórico (evitar repetição)
        recent_responses = [
            msg["message"] for msg in context.conversation_history[-3:] 
            if msg["type"] == "bot"
        ]
        
        available_templates = [t for t in templates if t not in recent_responses]
        if not available_templates:
            available_templates = templates
        
        # Escolher template mais apropriado
        base_response = self._select_best_template(available_templates, context, intent)
        
        # Personalizar resposta com contexto
        personalized_response = await self._personalize_response(
            base_response, context, additional_context
        )
        
        # Determinar ações sugeridas
        suggested_actions = self._get_suggested_actions(intent, context)
        
        # Determinar se precisa de humano
        requires_human = self._should_escalate_to_human(intent, confidence, context)
        
        return BotResponse(
            message=personalized_response,
            intent=intent,
            confidence=confidence,
            suggested_actions=suggested_actions,
            requires_human=requires_human,
            context_update={}
        )
    
    def _select_best_template(self, templates: List[str], context: ConversationContext, intent: str) -> str:
        """Selecionar melhor template baseado no contexto"""
        # Por agora, usar o primeiro disponível
        # Futuramente, implementar lógica mais sofisticada
        return templates[0] if templates else "Como posso ajudá-lo?"
    
    async def _personalize_response(
        self, 
        base_response: str, 
        context: ConversationContext,
        additional_context: Optional[Dict[str, Any]]
    ) -> str:
        """Personalizar resposta com informações do usuário"""
        response = base_response
        
        # Substituir placeholders se tivermos dados de cobrança
        if additional_context:
            for key, value in additional_context.items():
                placeholder = f"{{{key}}}"
                if placeholder in response:
                    response = response.replace(placeholder, str(value))
        
        # Adaptar tom baseado no sentimento
        if context.sentiment == "negativo":
            response = self._make_more_empathetic(response)
        elif context.sentiment == "positivo":
            response = self._make_more_enthusiastic(response)
        
        return response
    
    def _make_more_empathetic(self, response: str) -> str:
        """Tornar resposta mais empática"""
        empathetic_prefixes = [
            "Compreendo sua situação. ",
            "Entendo como deve estar se sentindo. ",
            "Sei que pode ser frustrante. "
        ]
        
        # Adicionar prefixo empático se não tiver
        if not any(prefix.lower() in response.lower() for prefix in empathetic_prefixes):
            return empathetic_prefixes[0] + response
        
        return response
    
    def _make_more_enthusiastic(self, response: str) -> str:
        """Tornar resposta mais entusiasmada"""
        # Adicionar mais emojis positivos se necessário
        if "😊" not in response and "👍" not in response:
            response += " 😊"
        
        return response
    
    def _get_suggested_actions(self, intent: str, context: ConversationContext) -> List[str]:
        """Obter ações sugeridas baseadas na intenção"""
        action_mapping = {
            "pagamento_realizado": ["solicitar_comprovante", "confirmar_dados"],
            "solicitacao_dados": ["enviar_dados_bancarios", "gerar_boleto"],
            "questionamento_divida": ["verificar_conta", "solicitar_cpf"],
            "negociacao": ["propor_parcelamento", "calcular_desconto"],
            "dificuldade_financeira": ["propor_acordo", "agendar_contato"],
            "prazo_pagamento": ["informar_vencimento", "propor_antecipacao"]
        }
        
        return action_mapping.get(intent, ["continuar_conversa"])
    
    def _should_escalate_to_human(self, intent: str, confidence: float, context: ConversationContext) -> bool:
        """Determinar se deve escalar para atendente humano"""
        # Escalar se confiança for muito baixa
        if confidence < 0.3:
            return True
        
        # Escalar em casos específicos
        escalation_intents = ["questionamento_divida", "dificuldade_financeira"]
        if intent in escalation_intents and len(context.conversation_history) > 6:
            return True
        
        # Escalar se usuário expressar frustração repetidamente
        recent_sentiments = [
            msg.get("sentiment", "neutro") for msg in context.conversation_history[-3:]
            if msg["type"] == "user"
        ]
        if recent_sentiments.count("negativo") >= 2:
            return True
        
        return False
    
    def _determine_next_stage(self, current_stage: str, intent: str) -> str:
        """Determinar próximo estágio da conversa"""
        stage_transitions = {
            "inicial": {
                "saudacao": "identificacao",
                "pagamento_realizado": "finalizacao",
                "questionamento_divida": "esclarecimento"
            },
            "identificacao": {
                "solicitacao_dados": "esclarecimento",
                "confirmacao": "esclarecimento"
            },
            "esclarecimento": {
                "negociacao": "negociacao",
                "pagamento_realizado": "finalizacao"
            },
            "negociacao": {
                "confirmacao": "finalizacao",
                "pagamento_realizado": "finalizacao"
            }
        }
        
        return stage_transitions.get(current_stage, {}).get(intent, current_stage)
    
    async def _load_conversation_contexts(self):
        """Carregar contextos de conversa salvos"""
        # Implementar carregamento de contextos persistidos
        pass
    
    async def _save_conversation_contexts(self):
        """Salvar contextos de conversa"""
        # Implementar persistência de contextos
        pass
    
    async def get_conversation_history(self, user_phone: str) -> List[Dict[str, Any]]:
        """Obter histórico de conversa"""
        session_id = f"session_{user_phone}"
        if session_id in self.active_sessions:
            return self.active_sessions[session_id].conversation_history
        return []
    
    async def get_active_sessions_count(self) -> int:
        """Obter número de sessões ativas"""
        # Limpar sessões expiradas
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, context in self.active_sessions.items()
            if current_time - context.last_interaction > timedelta(hours=24)
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(self.active_sessions)
