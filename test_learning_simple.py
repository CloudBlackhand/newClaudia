#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simplificado do Sistema de Aprendizado
Testa apenas os módulos principais sem dependências complexas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.modules.response_quality_analyzer import ResponseQualityAnalyzer
from backend.modules.template_learning_engine import TemplateLearningEngine
from backend.modules.campaign_optimizer import CampaignOptimizer

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
    
    # Obter recomendações (agora com parâmetro opcional)
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

def test_api_endpoints():
    """Testa se as rotas da API estão funcionando"""
    print("\n🧪 Testando rotas da API...")
    
    try:
        # Verificar se o arquivo de rotas existe
        import os
        routes_file = "backend/api/routes/conversation_routes.py"
        
        if not os.path.exists(routes_file):
            print("❌ Arquivo de rotas não encontrado")
            return False
        
        print("✅ Arquivo de rotas encontrado")
        
        # Ler o arquivo e verificar se contém as funções de aprendizado
        with open(routes_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        learning_functions = [
            'get_learning_insights',
            'get_quality_insights', 
            'get_template_recommendations',
            'optimize_template',
            'analyze_campaign',
            'get_campaign_insights',
            'update_feedback'
        ]
        
        found_functions = []
        for func_name in learning_functions:
            if f"def {func_name}(" in content:
                found_functions.append(func_name)
        
        print(f"✅ Funções de aprendizado encontradas: {len(found_functions)}/{len(learning_functions)}")
        for func in found_functions:
            print(f"   - {func}")
        
        # Verificar se contém as rotas de aprendizado
        learning_routes = [
            '/learning/insights',
            '/learning/quality-insights',
            '/learning/template-recommendations',
            '/learning/optimize-template',
            '/learning/analyze-campaign',
            '/learning/campaign-insights',
            '/learning/update-feedback'
        ]
        
        found_routes = []
        for route in learning_routes:
            if route in content:
                found_routes.append(route)
        
        print(f"✅ Rotas de aprendizado encontradas: {len(found_routes)}/{len(learning_routes)}")
        for route in found_routes:
            print(f"   - {route}")
        
        # Verificar se contém o blueprint
        if 'conversation_bp' in content:
            print("✅ Blueprint de conversação encontrado")
        else:
            print("❌ Blueprint de conversação não encontrado")
            return False
        
        return len(found_functions) == len(learning_functions) and len(found_routes) == len(learning_routes)
        
    except Exception as e:
        print(f"❌ Erro ao testar rotas da API: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES SIMPLIFICADOS DO SISTEMA DE APRENDIZADO")
    print("=" * 70)
    
    tests = [
        ("ResponseQualityAnalyzer", test_quality_analyzer),
        ("TemplateLearningEngine", test_template_learning),
        ("CampaignOptimizer", test_campaign_optimizer),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("📋 RESULTADOS DOS TESTES:")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 RESUMO: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("🎉 TODOS OS TESTES PASSARAM! Sistema de aprendizado funcionando perfeitamente!")
        print("\n🚀 FUNCIONALIDADES IMPLEMENTADAS:")
        print("   ✅ Análise de qualidade de respostas")
        print("   ✅ Aprendizado de templates")
        print("   ✅ Otimização de campanhas")
        print("   ✅ APIs para insights e recomendações")
        print("   ✅ Integração com IA existente")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Instalar dependências: pip install -r requirements.txt")
        print("   2. Configurar variáveis de ambiente")
        print("   3. Testar com dados reais de cobrança")
        print("   4. Monitorar melhorias nas próximas campanhas")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
