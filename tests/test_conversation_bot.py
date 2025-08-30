#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para o Bot de Conversação
"""

import pytest
from datetime import datetime

from backend.modules.conversation_bot import (
    ConversationBot,
    NLPProcessor,
    ResponseGenerator,
    IntentType,
    SentimentType,
    ResponseType,
    ConversationContext
)

class TestNLPProcessor:
    """Testes para o processador de NLP"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.nlp = NLPProcessor()
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_detect_greeting_intent(self):
        """Testa detecção de intenção de cumprimento"""
        greeting_messages = [
            "Oi, tudo bem?",
            "Olá, bom dia!",
            "E aí, beleza?",
            "Boa tarde!"
        ]
        
        for message in greeting_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.intent == IntentType.GREETING
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_detect_payment_confirmation_intent(self):
        """Testa detecção de confirmação de pagamento"""
        payment_messages = [
            "Já paguei a conta",
            "Efetuei o pagamento ontem",
            "Pix foi feito",
            "Já quitei o valor"
        ]
        
        for message in payment_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.intent == IntentType.PAYMENT_CONFIRMATION
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_detect_payment_question_intent(self):
        """Testa detecção de perguntas sobre pagamento"""
        question_messages = [
            "Como posso pagar?",
            "Qual o valor correto?",
            "Onde pago a conta?",
            "Qual a chave PIX?"
        ]
        
        for message in question_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.intent == IntentType.PAYMENT_QUESTION
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_detect_negotiation_intent(self):
        """Testa detecção de intenção de negociação"""
        negotiation_messages = [
            "Posso parcelar?",
            "Não consigo pagar tudo agora",
            "Tem desconto?",
            "Vamos negociar?"
        ]
        
        for message in negotiation_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.intent == IntentType.NEGOTIATION
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_detect_complaint_intent(self):
        """Testa detecção de reclamações"""
        complaint_messages = [
            "Não concordo com essa cobrança",
            "Isso é um absurdo!",
            "Vou processar vocês",
            "Cobrança indevida"
        ]
        
        for message in complaint_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.intent == IntentType.COMPLAINT
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_analyze_positive_sentiment(self):
        """Testa análise de sentimento positivo"""
        positive_messages = [
            "Obrigado pela ajuda!",
            "Excelente atendimento",
            "Muito bom, grato",
            "Perfeito, satisfeito"
        ]
        
        for message in positive_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.sentiment == SentimentType.POSITIVE
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_analyze_negative_sentiment(self):
        """Testa análise de sentimento negativo"""
        negative_messages = [
            "Péssimo atendimento",
            "Muito ruim isso",
            "Terrível experiência",
            "Estou chateado"
        ]
        
        for message in negative_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.sentiment == SentimentType.NEGATIVE
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_analyze_angry_sentiment(self):
        """Testa análise de sentimento de raiva"""
        angry_messages = [
            "Estou furioso com vocês!",
            "Isso é inadmissível!",
            "Que vergonha, absurdo!",
            "Ridículo esse tratamento"
        ]
        
        for message in angry_messages:
            analysis = self.nlp.analyze_message(message)
            assert analysis.sentiment == SentimentType.ANGRY
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_extract_money_entities(self):
        """Testa extração de entidades monetárias"""
        money_messages = [
            "O valor é R$ 150,50",
            "Paguei 200 reais",
            "1.500,00 é muito caro",
            "50,75 está certo"
        ]
        
        for message in money_messages:
            analysis = self.nlp.analyze_message(message)
            assert 'money' in analysis.entities
            assert len(analysis.entities['money']) > 0
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_extract_date_entities(self):
        """Testa extração de entidades de data"""
        date_messages = [
            "Vence em 31/12/2024",
            "Paguei em 15-06-2024",
            "Data limite: 25/12/2024"
        ]
        
        for message in date_messages:
            analysis = self.nlp.analyze_message(message)
            assert 'date' in analysis.entities
            assert len(analysis.entities['date']) > 0
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_extract_keywords(self):
        """Testa extração de palavras-chave"""
        message = "Gostaria de negociar o pagamento da conta vencida"
        
        analysis = self.nlp.analyze_message(message)
        
        # Deve extrair palavras relevantes, ignorando stop words
        assert len(analysis.keywords) > 0
        assert 'negociar' in analysis.keywords
        assert 'pagamento' in analysis.keywords
        assert 'conta' in analysis.keywords
        assert 'vencida' in analysis.keywords
        
        # Não deve incluir stop words
        assert 'de' not in analysis.keywords
        assert 'da' not in analysis.keywords

class TestResponseGenerator:
    """Testes para o gerador de respostas"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.generator = ResponseGenerator()
        self.nlp = NLPProcessor()
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_generate_greeting_response(self):
        """Testa geração de resposta para cumprimento"""
        analysis = self.nlp.analyze_message("Oi, tudo bem?")
        context = ConversationContext(
            user_phone="+5511999999999",
            session_id="test_session",
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            message_count=1
        )
        
        response = self.generator.generate_response(analysis, context)
        
        assert response.response_type in [ResponseType.INFORMATIVE, ResponseType.EMPATHETIC]
        assert len(response.text) > 0
        assert "olá" in response.text.lower() or "oi" in response.text.lower()
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_generate_payment_confirmation_response(self):
        """Testa resposta para confirmação de pagamento"""
        analysis = self.nlp.analyze_message("Já paguei a conta")
        context = ConversationContext(
            user_phone="+5511999999999",
            session_id="test_session",
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            message_count=2
        )
        
        response = self.generator.generate_response(analysis, context)
        
        assert response.response_type == ResponseType.CONFIRMATION
        assert len(response.text) > 0
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_generate_negotiation_response(self):
        """Testa resposta para negociação"""
        analysis = self.nlp.analyze_message("Posso parcelar em 3x?")
        context = ConversationContext(
            user_phone="+5511999999999",
            session_id="test_session",
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            message_count=3
        )
        
        response = self.generator.generate_response(analysis, context)
        
        assert response.response_type == ResponseType.EMPATHETIC
        assert len(response.suggested_actions) > 0
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_escalation_for_angry_customer(self):
        """Testa escalação para cliente irritado"""
        analysis = self.nlp.analyze_message("Isso é um absurdo, ridículo!")
        context = ConversationContext(
            user_phone="+5511999999999",
            session_id="test_session",
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            message_count=5
        )
        
        response = self.generator.generate_response(analysis, context)
        
        assert response.should_escalate
        assert response.response_type == ResponseType.EMPATHETIC
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_escalation_for_complaint(self):
        """Testa escalação para reclamação"""
        analysis = self.nlp.analyze_message("Vou processar vocês!")
        context = ConversationContext(
            user_phone="+5511999999999",
            session_id="test_session",
            started_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
            message_count=3
        )
        
        response = self.generator.generate_response(analysis, context)
        
        assert response.should_escalate
        assert response.response_type == ResponseType.ESCALATION

class TestConversationBot:
    """Testes para o bot completo"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.bot = ConversationBot()
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_process_first_message(self):
        """Testa processamento da primeira mensagem"""
        phone = "+5511999999999"
        message = "Olá, recebi uma cobrança"
        
        response = self.bot.process_message(phone, message, "João Silva")
        
        # Deve criar contexto
        assert phone in self.bot.active_contexts
        context = self.bot.active_contexts[phone]
        assert context.user_name == "João Silva"
        assert context.message_count == 1
        
        # Deve gerar resposta
        assert response.text is not None
        assert len(response.text) > 0
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_process_multiple_messages(self):
        """Testa processamento de múltiplas mensagens"""
        phone = "+5511999999999"
        messages = [
            "Oi, tudo bem?",
            "Recebi uma cobrança de R$ 150",
            "Posso parcelar?",
            "Ok, obrigado"
        ]
        
        for i, message in enumerate(messages):
            response = self.bot.process_message(phone, message)
            
            # Contexto deve existir e ser atualizado
            assert phone in self.bot.active_contexts
            context = self.bot.active_contexts[phone]
            assert context.message_count == i + 1
            
            # Deve ter resposta
            assert response.text is not None
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_context_updates_with_entities(self):
        """Testa atualização do contexto com entidades"""
        phone = "+5511999999999"
        
        # Mensagem com valor
        self.bot.process_message(phone, "A cobrança é de R$ 250,00")
        context = self.bot.active_contexts[phone]
        assert context.payment_amount == 250.0
        
        # Mensagem com data
        self.bot.process_message(phone, "Vence em 31/12/2024")
        context = self.bot.active_contexts[phone]
        assert context.due_date == "31/12/2024"
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_intent_and_sentiment_history(self):
        """Testa histórico de intenções e sentimentos"""
        phone = "+5511999999999"
        
        # Sequência de mensagens com diferentes intenções
        messages_and_expected = [
            ("Olá", IntentType.GREETING),
            ("Quanto devo?", IntentType.PAYMENT_QUESTION),
            ("Já paguei", IntentType.PAYMENT_CONFIRMATION),
            ("Isso é absurdo!", IntentType.COMPLAINT)
        ]
        
        for message, expected_intent in messages_and_expected:
            self.bot.process_message(phone, message)
        
        context = self.bot.active_contexts[phone]
        
        # Verificar histórico de intenções
        assert len(context.intent_history) == 4
        assert context.intent_history[-1] == IntentType.COMPLAINT
        assert IntentType.GREETING in context.intent_history
        assert IntentType.PAYMENT_QUESTION in context.intent_history
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_topics_discussed(self):
        """Testa rastreamento de tópicos discutidos"""
        phone = "+5511999999999"
        
        # Diferentes tipos de mensagem
        self.bot.process_message(phone, "Olá")
        self.bot.process_message(phone, "Quanto devo?")
        self.bot.process_message(phone, "Posso parcelar?")
        
        context = self.bot.active_contexts[phone]
        
        # Deve ter registrado os tópicos
        assert 'greeting' in context.topics_discussed
        assert 'payment_question' in context.topics_discussed
        assert 'negotiation' in context.topics_discussed
    
    @pytest.mark.unit
    @pytest.mark.conversation
    def test_get_context_stats(self):
        """Testa obtenção de estatísticas"""
        # Criar algumas conversas
        phones = ["+5511999999999", "+5511888888888", "+5511777777777"]
        
        for i, phone in enumerate(phones):
            for j in range(i + 1):  # Número diferente de mensagens
                self.bot.process_message(phone, f"Mensagem {j}")
        
        stats = self.bot.get_context_stats()
        
        assert stats['total_contexts'] == 3
        assert stats['total_messages'] == 6  # 1 + 2 + 3
        assert stats['average_messages_per_context'] == 2.0

@pytest.mark.integration
@pytest.mark.conversation
class TestConversationIntegration:
    """Testes de integração para conversação"""
    
    def test_complete_conversation_flow(self):
        """Testa fluxo completo de conversa"""
        bot = ConversationBot()
        phone = "+5511999999999"
        user_name = "João Silva"
        
        # Fluxo típico de conversa sobre cobrança
        conversation_flow = [
            ("Oi, recebi uma mensagem de vocês", IntentType.GREETING),
            ("É sobre uma cobrança de R$ 150", IntentType.INFORMATION_REQUEST),
            ("Quando vence?", IntentType.PAYMENT_QUESTION),
            ("Já paguei ontem via PIX", IntentType.PAYMENT_CONFIRMATION),
            ("Obrigado pelo atendimento", IntentType.GOODBYE)
        ]
        
        responses = []
        for message, expected_intent in conversation_flow:
            response = bot.process_message(phone, message, user_name)
            responses.append(response)
            
            # Verificar que a resposta é apropriada
            assert response.text is not None
            assert len(response.text) > 0
            assert response.confidence > 0
        
        # Verificar contexto final
        context = bot.active_contexts[phone]
        assert context.user_name == user_name
        assert context.message_count == 5
        assert context.payment_amount == 150.0
        
        # Deve ter discutido vários tópicos
        assert len(context.topics_discussed) >= 3
        
        # Último intent deve ser goodbye
        assert context.intent_history[-1] == IntentType.GOODBYE
    
    def test_escalation_scenario(self):
        """Testa cenário que deve resultar em escalação"""
        bot = ConversationBot()
        phone = "+5511999999999"
        
        # Conversa que escala rapidamente
        escalation_messages = [
            "Essa cobrança está errada!",
            "Não devo nada para vocês!",
            "Isso é um absurdo total!",
            "Vou processar essa empresa!"
        ]
        
        escalated = False
        for message in escalation_messages:
            response = bot.process_message(phone, message)
            if response.should_escalate:
                escalated = True
                break
        
        assert escalated, "Conversa deveria ter sido escalada"
    
    def test_payment_information_extraction(self):
        """Testa extração de informações de pagamento"""
        bot = ConversationBot()
        phone = "+5511999999999"
        
        # Mensagens com informações de pagamento
        bot.process_message(phone, "A cobrança é de R$ 1.250,75")
        bot.process_message(phone, "Vence no dia 25/12/2024")
        bot.process_message(phone, "Meu nome é João Silva")
        
        context = bot.active_contexts[phone]
        
        # Deve ter extraído as informações
        assert context.payment_amount == 1250.75
        assert context.due_date == "25/12/2024"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
