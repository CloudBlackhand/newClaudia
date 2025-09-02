#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Otimizador de Campanhas
Otimiza campanhas de cobrança baseado no aprendizado
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import statistics

from backend.modules.logger_system import LogManager, LogCategory

logger = LogManager.get_logger('campaign_optimizer')

class CampaignOptimizer:
    """Otimiza campanhas de cobrança baseado no aprendizado"""
    
    def __init__(self):
        self.campaign_performance = {}
        self.timing_optimization = {}
        self.message_effectiveness = {}
        self.optimization_history = []
        
        logger.info(LogCategory.CONVERSATION, "✅ Otimizador de Campanhas inicializado")
    
    def analyze_campaign_performance(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa performance de uma campanha de cobrança"""
        try:
            campaign_id = campaign_data.get('campaign_id', f"campaign_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}")
            
            analysis = {
                'campaign_id': campaign_id,
                'timestamp': datetime.utcnow(),
                'total_messages': len(campaign_data.get('messages', [])),
                'response_rate': 0.0,
                'payment_rate': 0.0,
                'escalation_rate': 0.0,
                'avg_response_time': 0.0,
                'best_performing_templates': [],
                'worst_performing_templates': [],
                'optimal_timing': {},
                'recommendations': [],
                'quality_metrics': {},
                'success_factors': []
            }
            
            messages = campaign_data.get('messages', [])
            if not messages:
                analysis['recommendations'].append("Campanha sem mensagens para análise")
                return analysis
            
            # Calcular métricas básicas
            responses = [m for m in messages if m.get('client_response')]
            payments = [m for m in messages if m.get('payment_made')]
            escalations = [m for m in messages if m.get('escalated')]
            
            analysis['response_rate'] = len(responses) / len(messages)
            analysis['payment_rate'] = len(payments) / len(messages)
            analysis['escalation_rate'] = len(escalations) / len(messages)
            
            # Calcular tempo médio de resposta
            response_times = [m.get('response_time_minutes', 0) for m in responses if m.get('response_time_minutes')]
            if response_times:
                analysis['avg_response_time'] = statistics.mean(response_times)
            
            # Analisar templates
            template_performance = self._analyze_template_performance(messages)
            analysis['best_performing_templates'] = template_performance['best']
            analysis['worst_performing_templates'] = template_performance['worst']
            
            # Analisar timing
            analysis['optimal_timing'] = self._analyze_timing_effectiveness(messages)
            
            # Analisar qualidade
            analysis['quality_metrics'] = self._analyze_quality_metrics(messages)
            
            # Identificar fatores de sucesso
            analysis['success_factors'] = self._identify_success_factors(messages)
            
            # Gerar recomendações
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            # Salvar análise
            self.campaign_performance[campaign_id] = analysis
            self.optimization_history.append({
                'campaign_id': campaign_id,
                'timestamp': datetime.utcnow(),
                'analysis': analysis
            })
            
            logger.info(LogCategory.CONVERSATION, 
                       f"Campanha {campaign_id} analisada - Taxa resposta: {analysis['response_rate']:.1%}, Pagamento: {analysis['payment_rate']:.1%}")
            
            return analysis
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro na análise de campanha: {e}")
            return {'error': str(e)}
    
    def _analyze_template_performance(self, messages: List[Dict]) -> Dict[str, List[Dict]]:
        """Analisa performance dos templates"""
        template_stats = {}
        
        for message in messages:
            template_id = message.get('template_id', 'unknown')
            if template_id not in template_stats:
                template_stats[template_id] = {
                    'uses': 0,
                    'responses': 0,
                    'payments': 0,
                    'escalations': 0,
                    'avg_quality': 0.0,
                    'quality_scores': []
                }
            
            stats = template_stats[template_id]
            stats['uses'] += 1
            
            if message.get('client_response'):
                stats['responses'] += 1
            if message.get('payment_made'):
                stats['payments'] += 1
            if message.get('escalated'):
                stats['escalations'] += 1
            
            # Coletar scores de qualidade
            quality_score = message.get('quality_score', 0.5)
            stats['quality_scores'].append(quality_score)
        
        # Calcular métricas finais
        best_templates = []
        worst_templates = []
        
        for template_id, stats in template_stats.items():
            if stats['uses'] >= 3:  # Mínimo de 3 usos para análise
                response_rate = stats['responses'] / stats['uses']
                payment_rate = stats['payments'] / stats['uses']
                escalation_rate = stats['escalations'] / stats['uses']
                avg_quality = statistics.mean(stats['quality_scores']) if stats['quality_scores'] else 0.5
                
                template_analysis = {
                    'template_id': template_id,
                    'uses': stats['uses'],
                    'response_rate': response_rate,
                    'payment_rate': payment_rate,
                    'escalation_rate': escalation_rate,
                    'avg_quality': avg_quality,
                    'success_score': (response_rate * 0.4 + payment_rate * 0.6) - (escalation_rate * 0.2)
                }
                
                if template_analysis['success_score'] > 0.6:
                    best_templates.append(template_analysis)
                elif template_analysis['success_score'] < 0.3:
                    worst_templates.append(template_analysis)
        
        # Ordenar por score de sucesso
        best_templates.sort(key=lambda x: x['success_score'], reverse=True)
        worst_templates.sort(key=lambda x: x['success_score'])
        
        return {
            'best': best_templates[:5],  # Top 5
            'worst': worst_templates[:5]  # Bottom 5
        }
    
    def _analyze_timing_effectiveness(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analisa efetividade do timing"""
        timing_stats = {
            'hourly_distribution': {},
            'daily_distribution': {},
            'optimal_hours': [],
            'optimal_days': [],
            'response_time_by_hour': {},
            'payment_time_by_hour': {}
        }
        
        for message in messages:
            timestamp = message.get('timestamp')
            if not timestamp:
                continue
            
            # Converter timestamp se necessário
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    continue
            
            hour = timestamp.hour
            weekday = timestamp.weekday()  # 0 = segunda, 6 = domingo
            
            # Distribuição por hora
            if hour not in timing_stats['hourly_distribution']:
                timing_stats['hourly_distribution'][hour] = {'sent': 0, 'responses': 0, 'payments': 0}
            
            timing_stats['hourly_distribution'][hour]['sent'] += 1
            if message.get('client_response'):
                timing_stats['hourly_distribution'][hour]['responses'] += 1
            if message.get('payment_made'):
                timing_stats['hourly_distribution'][hour]['payments'] += 1
            
            # Distribuição por dia da semana
            if weekday not in timing_stats['daily_distribution']:
                timing_stats['daily_distribution'][weekday] = {'sent': 0, 'responses': 0, 'payments': 0}
            
            timing_stats['daily_distribution'][weekday]['sent'] += 1
            if message.get('client_response'):
                timing_stats['daily_distribution'][weekday]['responses'] += 1
            if message.get('payment_made'):
                timing_stats['daily_distribution'][weekday]['payments'] += 1
        
        # Identificar horários ótimos
        for hour, stats in timing_stats['hourly_distribution'].items():
            if stats['sent'] >= 5:  # Mínimo de 5 envios
                response_rate = stats['responses'] / stats['sent']
                payment_rate = stats['payments'] / stats['sent']
                
                if response_rate > 0.6 or payment_rate > 0.3:
                    timing_stats['optimal_hours'].append({
                        'hour': hour,
                        'response_rate': response_rate,
                        'payment_rate': payment_rate
                    })
        
        # Identificar dias ótimos
        day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for weekday, stats in timing_stats['daily_distribution'].items():
            if stats['sent'] >= 10:  # Mínimo de 10 envios
                response_rate = stats['responses'] / stats['sent']
                payment_rate = stats['payments'] / stats['sent']
                
                if response_rate > 0.5 or payment_rate > 0.2:
                    timing_stats['optimal_days'].append({
                        'day': day_names[weekday],
                        'weekday': weekday,
                        'response_rate': response_rate,
                        'payment_rate': payment_rate
                    })
        
        return timing_stats
    
    def _analyze_quality_metrics(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analisa métricas de qualidade"""
        quality_scores = [m.get('quality_score', 0.5) for m in messages if m.get('quality_score')]
        
        if not quality_scores:
            return {'avg_quality': 0.5, 'quality_distribution': {}}
        
        quality_metrics = {
            'avg_quality': statistics.mean(quality_scores),
            'median_quality': statistics.median(quality_scores),
            'min_quality': min(quality_scores),
            'max_quality': max(quality_scores),
            'quality_distribution': {
                'high': len([s for s in quality_scores if s > 0.8]),
                'medium': len([s for s in quality_scores if 0.6 <= s <= 0.8]),
                'low': len([s for s in quality_scores if s < 0.6])
            }
        }
        
        return quality_metrics
    
    def _identify_success_factors(self, messages: List[Dict]) -> List[Dict[str, Any]]:
        """Identifica fatores de sucesso"""
        success_factors = []
        
        # Analisar correlação entre qualidade e sucesso
        high_quality_messages = [m for m in messages if m.get('quality_score', 0) > 0.8]
        if high_quality_messages:
            high_quality_success_rate = len([m for m in high_quality_messages if m.get('payment_made')]) / len(high_quality_messages)
            success_factors.append({
                'factor': 'high_quality_responses',
                'description': 'Respostas de alta qualidade',
                'success_rate': high_quality_success_rate,
                'sample_size': len(high_quality_messages)
            })
        
        # Analisar templates específicos
        template_success = {}
        for message in messages:
            template_id = message.get('template_id', 'unknown')
            if template_id not in template_success:
                template_success[template_id] = {'total': 0, 'successful': 0}
            
            template_success[template_id]['total'] += 1
            if message.get('payment_made'):
                template_success[template_id]['successful'] += 1
        
        for template_id, stats in template_success.items():
            if stats['total'] >= 5:  # Mínimo de 5 usos
                success_rate = stats['successful'] / stats['total']
                if success_rate > 0.4:  # Taxa de sucesso alta
                    success_factors.append({
                        'factor': f'template_{template_id}',
                        'description': f'Template {template_id}',
                        'success_rate': success_rate,
                        'sample_size': stats['total']
                    })
        
        return success_factors
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Gera recomendações para melhorar campanhas futuras"""
        recommendations = []
        
        # Taxa de resposta baixa
        if analysis['response_rate'] < 0.5:
            recommendations.append("Taxa de resposta baixa - revisar templates e timing de envio")
        
        # Taxa de pagamento baixa
        if analysis['payment_rate'] < 0.2:
            recommendations.append("Taxa de pagamento baixa - melhorar call-to-action e clareza das instruções")
        
        # Taxa de escalação alta
        if analysis['escalation_rate'] > 0.3:
            recommendations.append("Taxa de escalação alta - IA precisa de ajustes na abordagem")
        
        # Templates com baixa performance
        if analysis['worst_performing_templates']:
            recommendations.append(f"Revisar {len(analysis['worst_performing_templates'])} templates com baixa performance")
        
        # Usar templates bem-sucedidos
        if analysis['best_performing_templates']:
            recommendations.append(f"Replicar {len(analysis['best_performing_templates'])} templates bem-sucedidos em futuras campanhas")
        
        # Timing otimizado
        if analysis['optimal_timing']['optimal_hours']:
            best_hours = [h['hour'] for h in analysis['optimal_timing']['optimal_hours'][:3]]
            recommendations.append(f"Enviar mensagens nos horários: {', '.join(map(str, best_hours))}h")
        
        # Qualidade das respostas
        if analysis['quality_metrics']['avg_quality'] < 0.7:
            recommendations.append("Melhorar qualidade geral das respostas da IA")
        
        # Fatores de sucesso
        if analysis['success_factors']:
            top_factor = max(analysis['success_factors'], key=lambda x: x['success_rate'])
            recommendations.append(f"Focar no fator de sucesso: {top_factor['description']}")
        
        return recommendations
    
    def get_campaign_insights(self) -> Dict[str, Any]:
        """Obtém insights gerais para otimizar campanhas futuras"""
        if not self.campaign_performance:
            return {'message': 'Nenhuma campanha analisada ainda'}
        
        try:
            total_campaigns = len(self.campaign_performance)
            
            # Calcular médias gerais
            avg_response_rate = sum(c['response_rate'] for c in self.campaign_performance.values()) / total_campaigns
            avg_payment_rate = sum(c['payment_rate'] for c in self.campaign_performance.values()) / total_campaigns
            avg_escalation_rate = sum(c['escalation_rate'] for c in self.campaign_performance.values()) / total_campaigns
            
            insights = {
                'total_campaigns_analyzed': total_campaigns,
                'average_response_rate': avg_response_rate,
                'average_payment_rate': avg_payment_rate,
                'average_escalation_rate': avg_escalation_rate,
                'top_performing_templates': self._get_top_templates(),
                'optimal_timing_patterns': self._get_optimal_timing_patterns(),
                'common_issues': self._identify_common_issues(),
                'optimization_suggestions': self._generate_optimization_suggestions(),
                'quality_trends': self._analyze_quality_trends()
            }
            
            return insights
            
        except Exception as e:
            logger.error(LogCategory.CONVERSATION, f"Erro ao obter insights: {e}")
            return {'error': str(e)}
    
    def _get_top_templates(self) -> List[Dict[str, Any]]:
        """Obtém templates com melhor performance geral"""
        template_scores = {}
        
        for campaign in self.campaign_performance.values():
            for template in campaign.get('best_performing_templates', []):
                template_id = template['template_id']
                if template_id not in template_scores:
                    template_scores[template_id] = []
                
                template_scores[template_id].append({
                    'response_rate': template['response_rate'],
                    'payment_rate': template['payment_rate'],
                    'success_score': template['success_score']
                })
        
        # Calcular score médio
        top_templates = []
        for template_id, scores in template_scores.items():
            avg_response = sum(s['response_rate'] for s in scores) / len(scores)
            avg_payment = sum(s['payment_rate'] for s in scores) / len(scores)
            avg_success = sum(s['success_score'] for s in scores) / len(scores)
            
            top_templates.append({
                'template_id': template_id,
                'avg_response_rate': avg_response,
                'avg_payment_rate': avg_payment,
                'avg_success_score': avg_success,
                'usage_count': len(scores)
            })
        
        # Ordenar por score de sucesso
        top_templates.sort(key=lambda x: x['avg_success_score'], reverse=True)
        
        return top_templates[:10]  # Top 10
    
    def _get_optimal_timing_patterns(self) -> Dict[str, Any]:
        """Obtém padrões de timing ótimos"""
        all_optimal_hours = []
        all_optimal_days = []
        
        for campaign in self.campaign_performance.values():
            timing = campaign.get('optimal_timing', {})
            all_optimal_hours.extend(timing.get('optimal_hours', []))
            all_optimal_days.extend(timing.get('optimal_days', []))
        
        # Agrupar e calcular médias
        hour_performance = {}
        for hour_data in all_optimal_hours:
            hour = hour_data['hour']
            if hour not in hour_performance:
                hour_performance[hour] = []
            hour_performance[hour].append(hour_data)
        
        day_performance = {}
        for day_data in all_optimal_days:
            weekday = day_data['weekday']
            if weekday not in day_performance:
                day_performance[weekday] = []
            day_performance[weekday].append(day_data)
        
        # Calcular médias
        optimal_hours = []
        for hour, data_list in hour_performance.items():
            avg_response = sum(d['response_rate'] for d in data_list) / len(data_list)
            avg_payment = sum(d['payment_rate'] for d in data_list) / len(data_list)
            optimal_hours.append({
                'hour': hour,
                'avg_response_rate': avg_response,
                'avg_payment_rate': avg_payment,
                'campaigns_count': len(data_list)
            })
        
        optimal_days = []
        day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        for weekday, data_list in day_performance.items():
            avg_response = sum(d['response_rate'] for d in data_list) / len(data_list)
            avg_payment = sum(d['payment_rate'] for d in data_list) / len(data_list)
            optimal_days.append({
                'day': day_names[weekday],
                'weekday': weekday,
                'avg_response_rate': avg_response,
                'avg_payment_rate': avg_payment,
                'campaigns_count': len(data_list)
            })
        
        # Ordenar por performance
        optimal_hours.sort(key=lambda x: x['avg_payment_rate'], reverse=True)
        optimal_days.sort(key=lambda x: x['avg_payment_rate'], reverse=True)
        
        return {
            'best_hours': optimal_hours[:5],
            'best_days': optimal_days[:3]
        }
    
    def _identify_common_issues(self) -> List[str]:
        """Identifica problemas comuns nas campanhas"""
        issues = []
        
        low_response_campaigns = [c for c in self.campaign_performance.values() if c['response_rate'] < 0.5]
        low_payment_campaigns = [c for c in self.campaign_performance.values() if c['payment_rate'] < 0.2]
        high_escalation_campaigns = [c for c in self.campaign_performance.values() if c['escalation_rate'] > 0.3]
        
        total_campaigns = len(self.campaign_performance)
        
        if len(low_response_campaigns) > total_campaigns * 0.5:
            issues.append("Taxa de resposta baixa em mais de 50% das campanhas")
        
        if len(low_payment_campaigns) > total_campaigns * 0.6:
            issues.append("Taxa de pagamento baixa em mais de 60% das campanhas")
        
        if len(high_escalation_campaigns) > total_campaigns * 0.4:
            issues.append("Taxa de escalação alta em mais de 40% das campanhas")
        
        return issues
    
    def _generate_optimization_suggestions(self) -> List[str]:
        """Gera sugestões de otimização"""
        suggestions = []
        
        if self.campaign_performance:
            # Analisar tendências recentes
            recent_campaigns = sorted(
                self.campaign_performance.values(),
                key=lambda x: x['timestamp'],
                reverse=True
            )[:3]
            
            if recent_campaigns:
                recent_avg_response = sum(c['response_rate'] for c in recent_campaigns) / len(recent_campaigns)
                recent_avg_payment = sum(c['payment_rate'] for c in recent_campaigns) / len(recent_campaigns)
                
                if recent_avg_response < 0.4:
                    suggestions.append("Implementar A/B testing em templates")
                
                if recent_avg_payment < 0.15:
                    suggestions.append("Adicionar mais call-to-actions nos templates")
                
                suggestions.append("Revisar timing de envio das mensagens")
                suggestions.append("Implementar sequência de follow-up automático")
                suggestions.append("Personalizar mensagens baseado no perfil do cliente")
        
        return suggestions
    
    def _analyze_quality_trends(self) -> Dict[str, Any]:
        """Analisa tendências de qualidade"""
        quality_trends = {
            'overall_quality_trend': 'stable',
            'quality_improvement_rate': 0.0,
            'quality_issues': []
        }
        
        if len(self.optimization_history) >= 2:
            recent_quality = []
            older_quality = []
            
            for history in self.optimization_history[-3:]:  # Últimas 3 campanhas
                quality = history['analysis'].get('quality_metrics', {}).get('avg_quality', 0.5)
                recent_quality.append(quality)
            
            for history in self.optimization_history[-6:-3]:  # 3 campanhas anteriores
                quality = history['analysis'].get('quality_metrics', {}).get('avg_quality', 0.5)
                older_quality.append(quality)
            
            if recent_quality and older_quality:
                recent_avg = statistics.mean(recent_quality)
                older_avg = statistics.mean(older_quality)
                
                improvement_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
                quality_trends['quality_improvement_rate'] = improvement_rate
                
                if improvement_rate > 0.1:
                    quality_trends['overall_quality_trend'] = 'improving'
                elif improvement_rate < -0.1:
                    quality_trends['overall_quality_trend'] = 'declining'
        
        return quality_trends
