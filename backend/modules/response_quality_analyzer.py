#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Análise de Qualidade de Respostas
Analisa qualidade das respostas para melhorar futuras cobranças
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import re

from backend.modules.logger_system import LogManager, LogCategory

logger = LogManager.get_logger('response_quality_analyzer')

class ResponseQualityAnalyzer:
    """Analisa qualidade das respostas para melhorar futuras cobranças"""
    
    def __init__(self):
        self.quality_metrics = {}
        self.performance_history = []
        
        # Palavras-chave para análise
        self.empathy_words = [
            'entendo', 'compreendo', 'sei que', 'imagino', 'posso ajudar',
            'claro', 'perfeito', 'tudo bem', 'sem problemas', 'tranquilo'
        ]
        
        self.action_words = [
            'clique', 'acesse', 'envie', 'ligue', 'responda', 'pague',
            'entre em contato', 'procure', 'verifique', 'confirme'
        ]
        
        self.urgency_words = [
            'urgente', 'imediatamente', 'hoje', 'agora', 'último dia',
            'prazo', 'vencimento', 'importante', 'necessário'
        ]
        
        self.informal_words = [
            'beleza', 'valeu', 'flw', 'tchau', 'eae', 'opa', 'salve',
            'blz', 'ok', 'certo', 'tranquilo', 'suave'
        ]
        
        logger.info(LogCategory.CONVERSATION, "✅ Sistema de Análise de Qualidade inicializado")
    
    def analyze_response_quality(self, response_data: Dict[str, Any]) -> Dict[str, float]:
        """Analisa qualidade de uma resposta"""
        try:
            text = response_data.get('text', '')
            intent = response_data.get('intent', 'unknown')
            sentiment = response_data.get('sentiment', 'neutral')
            
            quality_scores = {
                'clarity': self._score_clarity(text),
                'empathy': self._score_empathy(text),
                'actionability': self._score_actionability(text),
                'urgency': self._score_urgency(text, intent),
                'professionalism': self._score_professionalism(text),
                'context_appropriateness': self._score_context_appropriateness(text, intent, sentiment)
            }
            
            # Score geral ponderado
            weights = {
                'clarity': 0.25,
                'empathy': 0.20,
                'actionability': 0.20,
                'urgency': 0.15,
                'professionalism': 0.10,
                'context_appropriateness': 0.10
            }
            
            quality_scores['overall'] = sum(
                quality_scores[metric] * weights[metric] 
                for metric in weights.keys()
            )
            
            # Salvar métricas para análise
            self._save_quality_metrics(intent, quality_scores)
            
            logger.debug(LogCategory.CONVERSATION, 
                        f"Qualidade analisada - Overall: {quality_scores['overall']:.2f}")
            
            return quality_scores
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro na análise de qualidade: {e}")
            return {'overall': 0.5}  # Score neutro em caso de erro
    
    def _score_clarity(self, text: str) -> float:
        """Score de clareza da mensagem"""
        try:
            # Remover pontuação e quebras de linha
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            sentences = [s.strip() for s in clean_text.split('.') if s.strip()]
            
            if not sentences:
                return 0.3
            
            # Calcular comprimento médio das frases
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            
            # Score baseado no comprimento ideal (6-12 palavras)
            if avg_sentence_length <= 6:
                return 0.8  # Muito claro
            elif avg_sentence_length <= 12:
                return 0.9  # Ideal
            elif avg_sentence_length <= 18:
                return 0.7  # Aceitável
            else:
                return 0.5  # Muito longo
            
        except Exception:
            return 0.5
    
    def _score_empathy(self, text: str) -> float:
        """Score de empatia"""
        try:
            text_lower = text.lower()
            empathy_count = sum(1 for word in self.empathy_words if word in text_lower)
            
            # Score baseado na presença de palavras empáticas
            if empathy_count == 0:
                return 0.4  # Sem empatia
            elif empathy_count == 1:
                return 0.7  # Empatia básica
            elif empathy_count == 2:
                return 0.8  # Boa empatia
            else:
                return 0.9  # Excelente empatia
            
        except Exception:
            return 0.5
    
    def _score_actionability(self, text: str) -> float:
        """Score de ação concreta"""
        try:
            text_lower = text.lower()
            action_count = sum(1 for word in self.action_words if word in text_lower)
            
            # Verificar se tem instruções claras
            has_instructions = any(phrase in text_lower for phrase in [
                'como fazer', 'passo a passo', 'instruções', 'procedimento'
            ])
            
            base_score = min(0.9, 0.3 + (action_count * 0.15))
            
            if has_instructions:
                base_score = min(0.95, base_score + 0.1)
            
            return base_score
            
        except Exception:
            return 0.5
    
    def _score_urgency(self, text: str, intent: str) -> float:
        """Score de urgência apropriada"""
        try:
            text_lower = text.lower()
            urgency_count = sum(1 for word in self.urgency_words if word in text_lower)
            
            # Ajustar baseado na intenção
            urgency_multiplier = 1.0
            if intent in ['urgency', 'payment_question']:
                urgency_multiplier = 1.2  # Mais urgência é apropriada
            elif intent in ['greeting', 'goodbye']:
                urgency_multiplier = 0.5  # Menos urgência é apropriada
            
            # Score baseado na quantidade de palavras de urgência
            if urgency_count == 0:
                base_score = 0.6  # Neutro
            elif urgency_count == 1:
                base_score = 0.8  # Ideal
            elif urgency_count == 2:
                base_score = 0.7  # Aceitável
            else:
                base_score = 0.4  # Muito agressivo
            
            return min(0.95, base_score * urgency_multiplier)
            
        except Exception:
            return 0.5
    
    def _score_professionalism(self, text: str) -> float:
        """Score de profissionalismo"""
        try:
            text_lower = text.lower()
            
            # Contar palavras informais
            informal_count = sum(1 for word in self.informal_words if word in text_lower)
            
            # Verificar erros de ortografia básicos
            spelling_errors = self._count_spelling_errors(text)
            
            # Verificar uso de emojis excessivo
            emoji_count = len(re.findall(r'[😀-🙏]', text))
            
            # Score base
            base_score = 0.8
            
            # Penalizar informalidade excessiva
            if informal_count > 2:
                base_score -= 0.2
            elif informal_count > 0:
                base_score -= 0.1
            
            # Penalizar erros de ortografia
            if spelling_errors > 0:
                base_score -= 0.1 * min(spelling_errors, 3)
            
            # Penalizar emojis excessivos
            if emoji_count > 3:
                base_score -= 0.1
            
            return max(0.3, base_score)
            
        except Exception:
            return 0.5
    
    def _score_context_appropriateness(self, text: str, intent: str, sentiment: str) -> float:
        """Score de adequação ao contexto"""
        try:
            text_lower = text.lower()
            
            # Verificar se a resposta é apropriada para a intenção
            appropriateness_score = 0.7  # Base
            
            # Ajustar baseado na intenção
            if intent == 'greeting' and any(word in text_lower for word in ['olá', 'oi', 'bom dia']):
                appropriateness_score = 0.9
            elif intent == 'payment_question' and any(word in text_lower for word in ['pagar', 'pagamento', 'valor']):
                appropriateness_score = 0.9
            elif intent == 'complaint' and any(word in text_lower for word in ['entendo', 'lamento', 'resolver']):
                appropriateness_score = 0.9
            elif intent == 'goodbye' and any(word in text_lower for word in ['tchau', 'até', 'obrigado']):
                appropriateness_score = 0.9
            
            # Ajustar baseado no sentimento
            if sentiment == 'negative' and any(word in text_lower for word in ['entendo', 'lamento', 'ajudar']):
                appropriateness_score = min(0.95, appropriateness_score + 0.1)
            elif sentiment == 'positive' and any(word in text_lower for word in ['ótimo', 'perfeito', 'excelente']):
                appropriateness_score = min(0.95, appropriateness_score + 0.1)
            
            return appropriateness_score
            
        except Exception:
            return 0.5
    
    def _count_spelling_errors(self, text: str) -> int:
        """Conta erros básicos de ortografia"""
        # Lista básica de palavras comuns mal escritas
        common_errors = [
            'vc', 'pq', 'tb', 'q', 'n', 'd', 't', 'c', 'b', 'm',
            'nao', 'voce', 'tambem', 'porque', 'que', 'de', 'te', 'ce', 'be', 'me'
        ]
        
        text_lower = text.lower()
        error_count = 0
        
        for error in common_errors:
            if error in text_lower:
                error_count += 1
        
        return error_count
    
    def _save_quality_metrics(self, intent: str, quality_scores: Dict[str, float]):
        """Salva métricas de qualidade para análise"""
        try:
            if intent not in self.quality_metrics:
                self.quality_metrics[intent] = []
            
            self.quality_metrics[intent].append({
                'timestamp': datetime.utcnow(),
                'scores': quality_scores
            })
            
            # Manter apenas últimas 100 análises por intenção
            if len(self.quality_metrics[intent]) > 100:
                self.quality_metrics[intent] = self.quality_metrics[intent][-100:]
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro ao salvar métricas: {e}")
    
    def get_quality_insights(self) -> Dict[str, Any]:
        """Obtém insights sobre qualidade das respostas"""
        try:
            insights = {
                'total_analyses': sum(len(metrics) for metrics in self.quality_metrics.values()),
                'intent_quality': {},
                'overall_quality_trend': [],
                'recommendations': []
            }
            
            # Analisar qualidade por intenção
            for intent, metrics in self.quality_metrics.items():
                if metrics:
                    avg_scores = {}
                    for score_type in ['clarity', 'empathy', 'actionability', 'urgency', 'professionalism', 'overall']:
                        avg_scores[score_type] = sum(m['scores'][score_type] for m in metrics) / len(metrics)
                    
                    insights['intent_quality'][intent] = {
                        'count': len(metrics),
                        'avg_scores': avg_scores,
                        'trend': self._calculate_quality_trend(metrics)
                    }
            
            # Gerar recomendações
            insights['recommendations'] = self._generate_quality_recommendations(insights['intent_quality'])
            
            return insights
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro ao obter insights: {e}")
            return {}
    
    def _calculate_quality_trend(self, metrics: List[Dict]) -> str:
        """Calcula tendência de qualidade"""
        if len(metrics) < 5:
            return 'insufficient_data'
        
        recent_scores = [m['scores']['overall'] for m in metrics[-5:]]
        older_scores = [m['scores']['overall'] for m in metrics[-10:-5]] if len(metrics) >= 10 else recent_scores
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)
        
        if recent_avg > older_avg + 0.05:
            return 'improving'
        elif recent_avg < older_avg - 0.05:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_quality_recommendations(self, intent_quality: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na qualidade"""
        recommendations = []
        
        for intent, data in intent_quality.items():
            scores = data['avg_scores']
            
            if scores['clarity'] < 0.7:
                recommendations.append(f"Melhorar clareza das respostas para '{intent}'")
            
            if scores['empathy'] < 0.6:
                recommendations.append(f"Aumentar empatia nas respostas para '{intent}'")
            
            if scores['actionability'] < 0.6:
                recommendations.append(f"Adicionar mais ações concretas para '{intent}'")
            
            if scores['professionalism'] < 0.7:
                recommendations.append(f"Melhorar profissionalismo para '{intent}'")
        
        return recommendations
