"""
Testes para o modelo de chatbot
"""
import pytest
import asyncio
import torch
from unittest.mock import Mock, patch, AsyncMock
from backend.models.chatbot import BillingChatBot, IntentClassifier
from backend.models.conversation import ConversationContext

class TestIntentClassifier:
    """Testes para classificador de intents"""
    
    def test_initialization(self):
        """Testa inicialização do classificador"""
        num_intents = 8
        classifier = IntentClassifier(num_intents)
        
        assert classifier.classifier.out_features == num_intents
        assert hasattr(classifier, 'bert')
        assert hasattr(classifier, 'dropout')
    
    def test_forward_pass(self):
        """Testa passagem forward do modelo"""
        num_intents = 8
        batch_size = 2
        seq_length = 10
        
        classifier = IntentClassifier(num_intents)
        
        # Input tensors simulados
        input_ids = torch.randint(0, 1000, (batch_size, seq_length))
        attention_mask = torch.ones(batch_size, seq_length)
        
        # Forward pass
        with torch.no_grad():
            outputs = classifier(input_ids, attention_mask)
        
        assert outputs.shape == (batch_size, num_intents)
        assert not torch.isnan(outputs).any()

class TestBillingChatBot:
    """Testes para BillingChatBot"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        with patch('backend.models.chatbot.active_config') as mock_config:
            mock_config.MODEL_DEVICE = 'cpu'
            mock_config.MODEL_MAX_LENGTH = 512
            mock_config.MODEL_TEMPERATURE = 0.7
            mock_config.MODEL_PATH = 'test_model.pth'
            
            self.chatbot = BillingChatBot()
    
    def test_initialization(self):
        """Testa inicialização do chatbot"""
        assert self.chatbot.device.type == 'cpu'
        assert self.chatbot.max_length == 512
        assert self.chatbot.temperature == 0.7
        assert len(self.chatbot.intents) > 0
        assert len(self.chatbot.responses) > 0
    
    def test_load_intents(self):
        """Testa carregamento de intents"""
        intents = self.chatbot._load_intents()
        
        # Verifica intents principais
        expected_intents = [
            "saudacao", "confirmacao_pagamento", "negociacao", 
            "informacoes", "contestacao", "agendamento", 
            "despedida", "pedido_ajuda"
        ]
        
        for intent in expected_intents:
            assert intent in intents
            assert isinstance(intents[intent], list)
            assert len(intents[intent]) > 0
    
    def test_load_responses(self):
        """Testa carregamento de respostas"""
        responses = self.chatbot._load_responses()
        
        # Verifica se há respostas para cada intent
        for intent in self.chatbot.intents.keys():
            assert intent in responses
            assert isinstance(responses[intent], list)
            assert len(responses[intent]) > 0
    
    def test_preprocess_message(self):
        """Testa pré-processamento de mensagem"""
        # Mensagem com caracteres especiais e espaços extras
        message = "  Olá!!!   Como  você   está???  "
        
        clean_message = self.chatbot._preprocess_message(message)
        
        assert clean_message == "olá como você está"
        assert not clean_message.startswith(" ")
        assert not clean_message.endswith(" ")
    
    def test_classify_by_rules_saudacao(self):
        """Testa classificação por regras - saudação"""
        message = "oi bom dia"
        
        result = self.chatbot._classify_by_rules(message)
        
        assert result["intent"] == "saudacao"
        assert result["confidence"] > 0
    
    def test_classify_by_rules_confirmacao_pagamento(self):
        """Testa classificação por regras - confirmação de pagamento"""
        message = "já paguei o boleto"
        
        result = self.chatbot._classify_by_rules(message)
        
        assert result["intent"] == "confirmacao_pagamento"
        assert result["confidence"] > 0
    
    def test_classify_by_rules_negociacao(self):
        """Testa classificação por regras - negociação"""
        message = "posso parcelar em 3 vezes"
        
        result = self.chatbot._classify_by_rules(message)
        
        assert result["intent"] == "negociacao"
        assert result["confidence"] > 0
    
    def test_classify_by_rules_default(self):
        """Testa classificação por regras - intent default"""
        message = "xptoekvmslkdnv"  # Texto sem sentido
        
        result = self.chatbot._classify_by_rules(message)
        
        assert result["intent"] == "default"
        assert result["confidence"] == 0.0
    
    def test_extract_entities_valor(self):
        """Testa extração de entidades - valor monetário"""
        message = "quero pagar R$ 150,50"
        
        entities = self.chatbot._extract_entities(message)
        
        assert "valor" in entities
        assert entities["valor"] in ["150,50", "150.50"]
    
    def test_extract_entities_data(self):
        """Testa extração de entidades - data"""
        message = "posso pagar no dia 15/01/2024"
        
        entities = self.chatbot._extract_entities(message)
        
        assert "data" in entities
    
    def test_extract_entities_confirmacao(self):
        """Testa extração de entidades - confirmação"""
        message = "sim, pode parcelar"
        
        entities = self.chatbot._extract_entities(message)
        
        assert "confirmacao" in entities
        assert entities["confirmacao"] == "sim"
    
    @pytest.mark.asyncio
    async def test_process_message_saudacao(self):
        """Testa processamento completo - saudação"""
        context = ConversationContext(phone="5511987654321")
        
        result = await self.chatbot.process_message("oi", context)
        
        assert result["intent"] == "saudacao"
        assert result["confidence"] > 0
        assert len(result["response"]) > 0
        assert isinstance(result["entities"], dict)
        assert isinstance(result["actions"], list)
    
    @pytest.mark.asyncio
    async def test_process_message_confirmacao_pagamento(self):
        """Testa processamento completo - confirmação de pagamento"""
        context = ConversationContext(phone="5511987654321", client_amount=150.50)
        
        result = await self.chatbot.process_message("já paguei", context)
        
        assert result["intent"] == "confirmacao_pagamento"
        assert "verificar_pagamento" in result["actions"]
        assert "verification_pending" in result["context_updates"].values()
    
    @pytest.mark.asyncio
    async def test_process_message_negociacao(self):
        """Testa processamento completo - negociação"""
        context = ConversationContext(
            phone="5511987654321", 
            client_amount=500.00,
            client_name="João Silva"
        )
        
        result = await self.chatbot.process_message("quero parcelar", context)
        
        assert result["intent"] == "negociacao"
        assert "R$ 500,00" in result["response"]
        assert "oferecer_negociacao" in result["actions"]
        assert result["context_updates"]["payment_status"] == "negotiating"
    
    @pytest.mark.asyncio
    async def test_process_message_contestacao(self):
        """Testa processamento completo - contestação"""
        context = ConversationContext(phone="5511987654321")
        
        result = await self.chatbot.process_message("não devo nada", context)
        
        assert result["intent"] == "contestacao"
        assert "escalate_to_human" in result["actions"]
        assert result["context_updates"]["payment_status"] == "disputed"
    
    @pytest.mark.asyncio
    async def test_process_message_informacoes(self):
        """Testa processamento completo - solicitação de informações"""
        context = ConversationContext(
            phone="5511987654321",
            client_amount=200.00
        )
        
        result = await self.chatbot.process_message("como posso pagar", context)
        
        assert result["intent"] == "informacoes"
        assert "R$ 200,00" in result["response"]
        assert "PIX" in result["response"]
        assert "enviar_informacoes_pagamento" in result["actions"]
    
    @pytest.mark.asyncio
    async def test_generate_contextual_response_with_client_name(self):
        """Testa geração de resposta contextual com nome do cliente"""
        context = ConversationContext(
            phone="5511987654321",
            client_name="Maria Silva"
        )
        
        response_data = await self.chatbot._generate_contextual_response(
            "oi", "saudacao", {}, context
        )
        
        # Verifica se o nome foi personalizado na resposta
        assert "Maria Silva" in response_data["response"] or \
               "Como posso ajudá-lo" in response_data["response"]
    
    def test_get_model_info(self):
        """Testa informações do modelo"""
        info = self.chatbot.get_model_info()
        
        assert "model_loaded" in info
        assert "device" in info
        assert "num_intents" in info
        assert "intents" in info
        assert "max_length" in info
        assert "temperature" in info
        
        assert info["device"] == "cpu"
        assert info["num_intents"] == len(self.chatbot.intent_labels)
        assert info["max_length"] == 512
        assert info["temperature"] == 0.7
    
    def test_update_model_with_feedback(self):
        """Testa atualização do modelo com feedback"""
        # Este teste apenas verifica se o método executa sem erro
        # Em implementação real, seria mais complexo
        
        message = "quero negociar"
        true_intent = "negociacao"
        predicted_intent = "informacoes"
        
        # Não deve gerar exceção
        self.chatbot.update_model_with_feedback(
            message, true_intent, predicted_intent
        )
    
    @pytest.mark.asyncio
    async def test_process_message_error_handling(self):
        """Testa tratamento de erros no processamento"""
        context = ConversationContext(phone="5511987654321")
        
        # Simula erro no processamento
        with patch.object(self.chatbot, '_classify_intent', side_effect=Exception("Test error")):
            result = await self.chatbot.process_message("test", context)
            
            assert result["intent"] == "error"
            assert "problema" in result["response"].lower()

class TestChatbotIntegration:
    """Testes de integração do chatbot"""
    
    @pytest.mark.asyncio
    async def test_conversation_flow(self):
        """Testa fluxo completo de conversa"""
        with patch('backend.models.chatbot.active_config') as mock_config:
            mock_config.MODEL_DEVICE = 'cpu'
            mock_config.MODEL_MAX_LENGTH = 512
            mock_config.MODEL_TEMPERATURE = 0.7
            mock_config.MODEL_PATH = 'test_model.pth'
            
            chatbot = BillingChatBot()
            context = ConversationContext(
                phone="5511987654321",
                client_name="João Silva",
                client_amount=300.00
            )
            
            # Simulação de conversa
            messages = [
                "oi",
                "quero negociar minha dívida",
                "posso parcelar em 3 vezes",
                "ok, obrigado"
            ]
            
            responses = []
            for message in messages:
                result = await chatbot.process_message(message, context)
                responses.append(result)
                
                # Atualiza contexto baseado na resposta
                if result["context_updates"]:
                    for key, value in result["context_updates"].items():
                        setattr(context, key, value)
            
            # Verifica sequência lógica
            assert responses[0]["intent"] == "saudacao"
            assert responses[1]["intent"] == "negociacao"
            assert responses[3]["intent"] == "despedida"
            
            # Verifica que contexto foi atualizado
            assert context.payment_status == "negotiating"

if __name__ == "__main__":
    pytest.main([__file__])

