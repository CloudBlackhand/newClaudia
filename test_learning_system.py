#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Sistema de Aprendizado Real
Testa todas as funcionalidades implementadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.response_quality_analyzer import ResponseQualityAnalyzer
from backend.modules.template_learning_engine import TemplateLearningEngine
from backend.modules.campaign_optimizer import CampaignOptimizer
from backend.modules.conversation_bot import ConversationBot

def test_quality_analyzer():
    """Testa o analisador de qualidade"""
    print("🧪 Testando ResponseQualityAnalyzer...")
    
    analyzer = ResponseQualityAnalyzer()
    
    # Teste com resposta de boa qualidade
    good_response = {
        'text': 'Olá! Entendo sua situação. Para efetuar o pagamento, acesse nosso site ou ligue para nós.',
        'intent': 'payment_question',
        'sentiment': 'neutral'
    }
    
    quality_scores = analyzer.analyze_response_quality(good_response)
    print(f"✅ Qualidade da resposta boa: {quality_scores['overall']:.2f}")
    
    # Teste com resposta de baixa qualidade
    bad_response = {
        'text': 'vc tem q pagar agora ou vai dar problema',
        'intent': 'payment_question',
        'sentiment': 'negative'
    }
    
    quality_scores = analyzer.analyze_response_quality(bad_response)
    print(f"❌ Qualidade da resposta ruim: {quality_scores['overall']:.2f}")
    
    # Obter insights
    insights = analyzer.get_quality_insights()
    print(f"📊 Total de análises: {insights.get('total_analyses', 0)}")
    
    return True

def test_template_learning():
    """Testa o engine de aprendizado de templates"""
    print("\n🧪 Testando TemplateLearningEngine...")
    
    learner = TemplateLearningEngine()
    
    # Simular aprendizado com respostas
    test_responses = [
        {
            'intent': 'greeting',
            'template_id': 'greeting_v1',
            'response': 'Olá! Como posso ajudá-lo hoje?',
            'client_reaction': 'positive',
            'quality_scores': {'overall': 0.9}
        },
        {
            'intent': 'greeting',
            'template_id': 'greeting_v2',
            'response': 'Oi, tudo bem?',
            'client_reaction': 'neutral',
            'quality_scores': {'overall': 0.7}
        },
        {
            'intent': 'payment_question',
            'template_id': 'payment_v1',
            'response': 'Para pagar, acesse nosso site ou use o PIX.',
            'client_reaction': 'positive',
            'quality_scores': {'overall': 0.8}
        }
    ]
    
    # Aprender com as respostas
    for response_data in test_responses:
        success = learner.learn_from_response(response_data)
        print(f"📚 Aprendizado: {response_data['intent']} - {'✅' if success else '❌'}")
    
    # Obter recomendações
    recommendations = learner.get_template_recommendations('greeting')
    print(f"💡 Recomendações para 'greeting': {len(recommendations)}")
    
    # Obter melhores templates
    best_templates = learner.get_best_templates('greeting')
    print(f"🏆 Melhores templates para 'greeting': {len(best_templates)}")
    
    # Resumo de performance
    summary = learner.get_template_performance_summary()
    print(f"📈 Templates analisados: {summary.get('total_templates', 0)}")
    
    return True

def test_campaign_optimizer():
    """Testa o otimizador de campanhas"""
    print("\n🧪 Testando CampaignOptimizer...")
    
    optimizer = CampaignOptimizer()
    
    # Simular dados de campanha
    campaign_data = {
        'campaign_id': 'test_campaign_001',
        'messages': [
            {
                'template_id': 'initial_br',
                'client_response': True,
                'payment_made': True,
                'escalated': False,
                'response_time_minutes': 30,
                'quality_score': 0.8,
                'timestamp': '2024-01-01T10:00:00'
            },
            {
                'template_id': 'reminder_br',
                'client_response': True,
                'payment_made': False,
                'escalated': True,
                'response_time_minutes': 120,
                'quality_score': 0.6,
                'timestamp': '2024-01-01T14:00:00'
            },
            {
                'template_id': 'urgent_br',
                'client_response': False,
                'payment_made': False,
                'escalated': False,
                'response_time_minutes': None,
                'quality_score': 0.4,
                'timestamp': '2024-01-01T18:00:00'
            }
        ]
    }
    
    # Analisar campanha
    analysis = optimizer.analyze_campaign_performance(campaign_data)
    print(f"📊 Análise da campanha:")
    print(f"   - Taxa de resposta: {analysis['response_rate']:.1%}")
    print(f"   - Taxa de pagamento: {analysis['payment_rate']:.1%}")
    print(f"   - Taxa de escalação: {analysis['escalation_rate']:.1%}")
    print(f"   - Templates bem-sucedidos: {len(analysis['best_performing_templates'])}")
    print(f"   - Recomendações: {len(analysis['recommendations'])}")
    
    # Obter insights gerais
    insights = optimizer.get_campaign_insights()
    print(f"🎯 Insights gerais:")
    print(f"   - Campanhas analisadas: {insights.get('total_campaigns_analyzed', 0)}")
    print(f"   - Taxa média de resposta: {insights.get('average_response_rate', 0):.1%}")
    print(f"   - Taxa média de pagamento: {insights.get('average_payment_rate', 0):.1%}")
    
    return True

def test_conversation_bot_integration():
    """Testa a integração com o ConversationBot"""
    print("\n🧪 Testando integração com ConversationBot...")
    
    try:
        # Inicializar bot (pode demorar um pouco)
        print("🤖 Inicializando ConversationBot...")
        bot = ConversationBot()
        print("✅ ConversationBot inicializado com sistemas de aprendizado!")
        
        # Testar processamento de mensagem
        print("💬 Testando processamento de mensagem...")
        response = bot.process_message("+5511999999999", "Oi, como posso pagar minha conta?")
        print(f"✅ Resposta gerada: {response.text[:50]}...")
        
        # Obter estatísticas de aprendizado
        print("📊 Obtendo estatísticas de aprendizado...")
        learning_stats = bot.get_learning_stats()
        print(f"✅ Estatísticas obtidas: {learning_stats.get('learning_active', False)}")
        
        # Testar insights de qualidade
        print("🎯 Obtendo insights de qualidade...")
        quality_insights = bot.get_quality_insights()
        print(f"✅ Insights de qualidade obtidos: {len(quality_insights)} campos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO SISTEMA DE APRENDIZADO REAL")
    print("=" * 60)
    
    tests = [
        ("ResponseQualityAnalyzer", test_quality_analyzer),
        ("TemplateLearningEngine", test_template_learning),
        ("CampaignOptimizer", test_campaign_optimizer),
        ("ConversationBot Integration", test_conversation_bot_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📋 RESULTADOS DOS TESTES:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESUMO: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 TODOS OS TESTES PASSARAM! Sistema de aprendizado funcionando perfeitamente!")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
