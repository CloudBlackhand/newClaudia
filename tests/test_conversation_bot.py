"""
Testes para o bot de conversação
"""
import pytest
import asyncio
from unittest.mock import AsyncMock
from backend.modules.conversation_bot import ConversationBot
from backend.modules.logger_system import LoggerSystem

@pytest.fixture
async def conversation_bot():
    logger_system = LoggerSystem()
    bot = ConversationBot(logger_system)
    await bot.initialize()
    return bot

@pytest.mark.asyncio
async def test_process_message_greeting(conversation_bot):
    """Teste de processamento de saudação"""
    response = await conversation_bot.process_message(
        user_phone="+5511999999999",
        message="Olá"
    )
    
    assert response.intent == "saudacao"
    assert response.confidence > 0
    assert "Olá" in response.message or "Oi" in response.message

@pytest.mark.asyncio
async def test_process_message_payment_confirmation(conversation_bot):
    """Teste de confirmação de pagamento"""
    response = await conversation_bot.process_message(
        user_phone="+5511999999999",
        message="Já paguei a conta"
    )
    
    assert response.intent == "pagamento_realizado"
    assert response.confidence > 0
    assert len(response.message) > 0

@pytest.mark.asyncio
async def test_process_message_data_request(conversation_bot):
    """Teste de solicitação de dados"""
    response = await conversation_bot.process_message(
        user_phone="+5511999999999",
        message="Como posso pagar? Preciso dos dados bancários"
    )
    
    assert response.intent == "solicitacao_dados"
    assert "PIX" in response.message or "dados" in response.message

@pytest.mark.asyncio
async def test_conversation_context(conversation_bot):
    """Teste de contexto de conversa"""
    user_phone = "+5511888888888"
    
    # Primeira mensagem
    response1 = await conversation_bot.process_message(user_phone, "Oi")
    
    # Segunda mensagem - deve manter contexto
    response2 = await conversation_bot.process_message(user_phone, "Preciso pagar")
    
    # Verificar se o histórico foi mantido
    history = await conversation_bot.get_conversation_history(user_phone)
    assert len(history) >= 4  # 2 mensagens do usuário + 2 respostas do bot

def test_nlp_intent_analysis(conversation_bot):
    """Teste de análise de intenções"""
    nlp = conversation_bot.nlp
    
    test_cases = [
        ("Olá", "saudacao"),
        ("Já paguei", "pagamento_realizado"),
        ("Como pagar?", "solicitacao_dados"),
        ("Não devo nada", "questionamento_divida"),
        ("Posso parcelar?", "negociacao"),
        ("Estou desempregado", "dificuldade_financeira")
    ]
    
    for message, expected_intent in test_cases:
        intent, confidence = nlp.analyze_intent(message)
        assert intent == expected_intent, f"Mensagem '{message}' deveria ter intenção '{expected_intent}', mas foi '{intent}'"
        assert confidence > 0

def test_nlp_sentiment_analysis(conversation_bot):
    """Teste de análise de sentimentos"""
    nlp = conversation_bot.nlp
    
    test_cases = [
        ("Obrigado, muito bom!", "positivo"),
        ("Estou muito irritado", "negativo"),
        ("Ok, entendi", "neutro")
    ]
    
    for message, expected_sentiment in test_cases:
        sentiment = nlp.analyze_sentiment(message)
        assert sentiment == expected_sentiment, f"Mensagem '{message}' deveria ter sentimento '{expected_sentiment}', mas foi '{sentiment}'"

def test_nlp_entity_extraction(conversation_bot):
    """Teste de extração de entidades"""
    nlp = conversation_bot.nlp
    
    message = "Meu CPF é 123.456.789-00 e o valor é R$ 150,00"
    entities = nlp.extract_entities(message)
    
    assert "cpf" in entities
    assert "valor" in entities
    assert "123.456.789-00" in entities["cpf"]
    assert "150,00" in entities["valor"]
