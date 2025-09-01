#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine de Aprendizado de Templates
Aprende com respostas para melhorar templates futuros
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib

from backend.modules.logger_system import LogManager, LogCategory

logger = LogManager.get_logger('template_learning_engine')

class TemplateLearningEngine:
    """Aprende com respostas para melhorar templates futuros"""
    
    def __init__(self):
        self.template_performance = {}
        self.intent_effectiveness = {}
        self.response_patterns = {}
        self.success_metrics = {}
        
        logger.info(LogCategory.CONVERSATION, "✅ Engine de Aprendizado de Templates inicializado")
    
    def learn_from_response(self, response_data: Dict[str, Any]) -> bool:
        """Aprende com uma resposta para melhorar futuras cobranças"""
        try:
            intent = response_data.get('intent', 'unknown')
            template_id = response_data.get('template_id', 'dynamic_generated')
            response_text = response_data.get('response', '')
            client_reaction = response_data.get('client_reaction', 'pending')
            quality_scores = response_data.get('quality_scores', {})
            
            # Analisar performance do template
            if template_id not in self.template_performance:
                self.template_performance[template_id] = {
                    'total_uses': 0,
                    'positive_reactions': 0,
                    'negative_reactions': 0,
                    'neutral_reactions': 0,
                    'avg_response_time': 0,
                    'payment_conversion_rate': 0,
                    'quality_scores_history': [],
                    'last_updated': datetime.utcnow()
                }
            
            # Atualizar estatísticas
            template_stats = self.template_performance[template_id]
            template_stats['total_uses'] += 1
            template_stats['last_updated'] = datetime.utcnow()
            
            # Atualizar reações
            if client_reaction == 'positive':
                template_stats['positive_reactions'] += 1
            elif client_reaction == 'negative':
                template_stats['negative_reactions'] += 1
            else:
                template_stats['neutral_reactions'] += 1
            
            # Salvar scores de qualidade
            if quality_scores:
                template_stats['quality_scores_history'].append({
                    'timestamp': datetime.utcnow(),
                    'scores': quality_scores
                })
                
                # Manter apenas últimas 50 análises
                if len(template_stats['quality_scores_history']) > 50:
                    template_stats['quality_scores_history'] = template_stats['quality_scores_history'][-50:]
            
            # Analisar efetividade da intenção
            if intent not in self.intent_effectiveness:
                self.intent_effectiveness[intent] = {
                    'total_responses': 0,
                    'successful_responses': 0,
                    'response_variations': [],
                    'best_approaches': [],
                    'quality_trend': [],
                    'last_updated': datetime.utcnow()
                }
            
            intent_data = self.intent_effectiveness[intent]
            intent_data['total_responses'] += 1
            intent_data['last_updated'] = datetime.utcnow()
            
            # Identificar padrões de resposta bem-sucedidos
            if client_reaction == 'positive' or (quality_scores and quality_scores.get('overall', 0) > 0.8):
                intent_data['successful_responses'] += 1
                
                # Salvar variação bem-sucedida
                response_hash = self._hash_response(response_text)
                if response_hash not in [r['hash'] for r in intent_data['response_variations']]:
                    intent_data['response_variations'].append({
                        'hash': response_hash,
                        'text': response_text,
                        'quality_score': quality_scores.get('overall', 0.5),
                        'timestamp': datetime.utcnow(),
                        'usage_count': 1
                    })
                else:
                    # Atualizar contador de uso
                    for variation in intent_data['response_variations']:
                        if variation['hash'] == response_hash:
                            variation['usage_count'] += 1
                            variation['timestamp'] = datetime.utcnow()
                            break
            
            # Atualizar tendência de qualidade
            if quality_scores:
                intent_data['quality_trend'].append({
                    'timestamp': datetime.utcnow(),
                    'overall_score': quality_scores.get('overall', 0.5)
                })
                
                # Manter apenas últimas 100 medições
                if len(intent_data['quality_trend']) > 100:
                    intent_data['quality_trend'] = intent_data['quality_trend'][-100:]
            
            logger.info(LogCategory.CONVERSATION, 
                       f"Template {template_id} aprendido - reação: {client_reaction}, qualidade: {quality_scores.get('overall', 0):.2f}")
            
            return True
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro no aprendizado de template: {e}")
            return False
    
    def _hash_response(self, response_text: str) -> str:
        """Gera hash único para a resposta"""
        return hashlib.md5(response_text.encode('utf-8')).hexdigest()
    
    def get_template_recommendations(self, intent: str, context: Dict[str, Any] = None) -> List[str]:
        """Obtém recomendações para melhorar templates"""
        recommendations = []
        
        if context is None:
            context = {}
            
        if intent not in self.intent_effectiveness:
            recommendations.append(f"Novo intent '{intent}' - coletar mais dados para análise")
            return recommendations
        
        intent_data = self.intent_effectiveness[intent]
        
        # Se tem poucas respostas bem-sucedidas
        if intent_data['successful_responses'] < 3:
            recommendations.append(f"Template para '{intent}' precisa de mais variações bem-sucedidas")
        
        # Se taxa de sucesso é baixa
        if intent_data['total_responses'] > 0:
            success_rate = intent_data['successful_responses'] / intent_data['total_responses']
            if success_rate < 0.5:
                recommendations.append(f"Template para '{intent}' tem baixa efetividade ({success_rate:.1%})")
        
        # Analisar tendência de qualidade
        if len(intent_data['quality_trend']) >= 10:
            recent_quality = sum(t['overall_score'] for t in intent_data['quality_trend'][-5:]) / 5
            older_quality = sum(t['overall_score'] for t in intent_data['quality_trend'][-10:-5]) / 5
            
            if recent_quality < older_quality - 0.1:
                recommendations.append(f"Qualidade das respostas para '{intent}' está declinando")
            elif recent_quality > older_quality + 0.1:
                recommendations.append(f"Qualidade das respostas para '{intent}' está melhorando")
        
        # Sugerir melhores abordagens
        if intent_data['response_variations']:
            top_variations = sorted(
                intent_data['response_variations'],
                key=lambda x: x['quality_score'],
                reverse=True
            )[:3]
            
            recommendations.append(f"Usar as {len(top_variations)} melhores variações de '{intent}'")
        
        return recommendations
    
    def get_best_templates(self, intent: str) -> List[Dict[str, Any]]:
        """Obtém melhores templates para uma intenção"""
        if intent not in self.intent_effectiveness:
            return []
        
        intent_data = self.intent_effectiveness[intent]
        
        # Ordenar variações por qualidade e uso
        best_variations = sorted(
            intent_data['response_variations'],
            key=lambda x: (x['quality_score'], x['usage_count']),
            reverse=True
        )
        
        return best_variations[:5]  # Top 5
    
    def get_template_performance_summary(self) -> Dict[str, Any]:
        """Obtém resumo de performance dos templates"""
        try:
            summary = {
                'total_templates': len(self.template_performance),
                'total_intents': len(self.intent_effectiveness),
                'template_performance': {},
                'intent_effectiveness': {},
                'overall_insights': []
            }
            
            # Analisar performance dos templates
            for template_id, performance in self.template_performance.items():
                if performance['total_uses'] > 0:
                    success_rate = performance['positive_reactions'] / performance['total_uses']
                    summary['template_performance'][template_id] = {
                        'total_uses': performance['total_uses'],
                        'success_rate': success_rate,
                        'avg_quality': self._calculate_avg_quality(performance['quality_scores_history']),
                        'last_used': performance['last_updated']
                    }
            
            # Analisar efetividade das intenções
            for intent, data in self.intent_effectiveness.items():
                if data['total_responses'] > 0:
                    success_rate = data['successful_responses'] / data['total_responses']
                    avg_quality = self._calculate_avg_quality(data['quality_trend'])
                    
                    summary['intent_effectiveness'][intent] = {
                        'total_responses': data['total_responses'],
                        'success_rate': success_rate,
                        'avg_quality': avg_quality,
                        'variations_count': len(data['response_variations']),
                        'last_updated': data['last_updated']
                    }
            
            # Gerar insights gerais
            summary['overall_insights'] = self._generate_overall_insights(summary)
            
            return summary
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro ao obter resumo de performance: {e}")
            return {}
    
    def _calculate_avg_quality(self, quality_history: List[Dict]) -> float:
        """Calcula qualidade média"""
        if not quality_history:
            return 0.5
        
        if 'overall_score' in quality_history[0]:
            # Para quality_trend
            return sum(t['overall_score'] for t in quality_history) / len(quality_history)
        else:
            # Para quality_scores_history
            return sum(t['scores']['overall'] for t in quality_history) / len(quality_history)
    
    def _generate_overall_insights(self, summary: Dict[str, Any]) -> List[str]:
        """Gera insights gerais"""
        insights = []
        
        # Analisar templates com baixa performance
        low_performance_templates = [
            t for t, p in summary['template_performance'].items()
            if p['success_rate'] < 0.4 and p['total_uses'] >= 5
        ]
        
        if low_performance_templates:
            insights.append(f"{len(low_performance_templates)} templates com baixa performance precisam de revisão")
        
        # Analisar intenções com baixa efetividade
        low_effectiveness_intents = [
            i for i, e in summary['intent_effectiveness'].items()
            if e['success_rate'] < 0.5 and e['total_responses'] >= 10
        ]
        
        if low_effectiveness_intents:
            insights.append(f"{len(low_effectiveness_intents)} intenções com baixa efetividade")
        
        # Analisar qualidade geral
        all_qualities = []
        for intent_data in summary['intent_effectiveness'].values():
            all_qualities.append(intent_data['avg_quality'])
        
        if all_qualities:
            avg_overall_quality = sum(all_qualities) / len(all_qualities)
            if avg_overall_quality > 0.8:
                insights.append("Qualidade geral das respostas está excelente")
            elif avg_overall_quality > 0.7:
                insights.append("Qualidade geral das respostas está boa")
            elif avg_overall_quality > 0.6:
                insights.append("Qualidade geral das respostas está aceitável")
            else:
                insights.append("Qualidade geral das respostas precisa melhorar")
        
        return insights
    
    def optimize_template_for_intent(self, intent: str) -> Dict[str, Any]:
        """Otimiza template para uma intenção específica"""
        if intent not in self.intent_effectiveness:
            return {'status': 'no_data', 'message': f'Sem dados suficientes para {intent}'}
        
        intent_data = self.intent_effectiveness[intent]
        
        if not intent_data['response_variations']:
            return {'status': 'no_variations', 'message': f'Sem variações para {intent}'}
        
        # Encontrar melhor variação
        best_variation = max(
            intent_data['response_variations'],
            key=lambda x: (x['quality_score'], x['usage_count'])
        )
        
        # Analisar padrões de sucesso
        success_patterns = self._analyze_success_patterns(intent_data['response_variations'])
        
        optimization = {
            'status': 'optimized',
            'intent': intent,
            'best_variation': best_variation,
            'success_patterns': success_patterns,
            'recommendations': self._generate_optimization_recommendations(intent_data, success_patterns)
        }
        
        return optimization
    
    def _analyze_success_patterns(self, variations: List[Dict]) -> Dict[str, Any]:
        """Analisa padrões de sucesso nas variações"""
        if not variations:
            return {}
        
        # Agrupar por qualidade
        high_quality = [v for v in variations if v['quality_score'] > 0.8]
        medium_quality = [v for v in variations if 0.6 <= v['quality_score'] <= 0.8]
        low_quality = [v for v in variations if v['quality_score'] < 0.6]
        
        patterns = {
            'high_quality_count': len(high_quality),
            'medium_quality_count': len(medium_quality),
            'low_quality_count': len(low_quality),
            'avg_quality': sum(v['quality_score'] for v in variations) / len(variations),
            'most_used': max(variations, key=lambda x: x['usage_count']) if variations else None
        }
        
        return patterns
    
    def _generate_optimization_recommendations(self, intent_data: Dict, success_patterns: Dict) -> List[str]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        if success_patterns['high_quality_count'] == 0:
            recommendations.append("Criar variações de alta qualidade")
        
        if success_patterns['avg_quality'] < 0.7:
            recommendations.append("Melhorar qualidade geral das respostas")
        
        if intent_data['successful_responses'] / intent_data['total_responses'] < 0.6:
            recommendations.append("Aumentar taxa de sucesso das respostas")
        
        if len(intent_data['response_variations']) < 5:
            recommendations.append("Criar mais variações de resposta")
        
        return recommendations
