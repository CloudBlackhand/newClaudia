import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
from backend.modules.billing_dispatcher import BillingDispatcher
from backend.modules.conversation_bot import ConversationBot
from backend.modules.logger_system import SmartLogger, LogCategory

logger = SmartLogger("campaign_processor")

class CampaignProcessor:
    """Processa campanhas em massa a partir de arquivos JSON de cruzamento"""
    
    def __init__(self):
        self.billing_dispatcher = BillingDispatcher()
        self.conversation_bot = ConversationBot()
        self.processed_campaigns = {}
        self.campaign_stats = {
            'total_contacts': 0,
            'valid_contacts': 0,
            'messages_sent': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        # SISTEMA DE APRENDIZADO INTEGRADO
        self.learning_enabled = True
        self.adaptive_campaigns = {}
        self.client_behavior_analysis = {}
        self.campaign_optimization_data = {}
        self.real_time_adaptation = {}
    
    def process_campaign_file(self, file_path: str, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Processa arquivo de campanha e dispara mensagens"""
        try:
            logger.info(LogCategory.BILLING, f"🚀 Iniciando processamento de campanha: {file_path}")
            self.campaign_stats['start_time'] = datetime.now()
            
            # Carrega dados do arquivo
            campaign_data = self._load_campaign_data(file_path)
            if not campaign_data:
                raise ValueError("Arquivo de campanha vazio ou inválido")
            
            # Filtra contatos válidos
            valid_contacts = self._filter_valid_contacts(campaign_data, campaign_config)
            self.campaign_stats['total_contacts'] = len(campaign_data)
            self.campaign_stats['valid_contacts'] = len(valid_contacts)
            
            logger.info(LogCategory.BILLING, f"📊 Contatos válidos encontrados: {len(valid_contacts)}")
            
            # Processa cada contato
            results = []
            for contact in valid_contacts:
                try:
                    result = self._process_single_contact(contact, campaign_config)
                    results.append(result)
                    if result['success']:
                        self.campaign_stats['messages_sent'] += 1
                    else:
                        self.campaign_stats['errors'] += 1
                except Exception as e:
                    logger.error(LogCategory.BILLING, f"❌ Erro ao processar contato: {str(e)}")
                    self.campaign_stats['errors'] += 1
                    results.append({
                        'contact_id': contact.get('protocolo', 'N/A'),
                        'success': False,
                        'error': str(e)
                    })
            
            # Finaliza estatísticas
            self.campaign_stats['end_time'] = datetime.now()
            duration = self.campaign_stats['end_time'] - self.campaign_stats['start_time']
            
            # Salva resultados
            campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.processed_campaigns[campaign_id] = {
                'config': campaign_config,
                'stats': self.campaign_stats,
                'results': results,
                'duration_seconds': duration.total_seconds()
            }
            
            logger.info(LogCategory.BILLING, f"✅ Campanha finalizada: {campaign_id}")
            logger.info(LogCategory.BILLING, f"📈 Estatísticas: {self.campaign_stats['messages_sent']} mensagens enviadas, {self.campaign_stats['errors']} erros")
            
            return {
                'campaign_id': campaign_id,
                'success': True,
                'stats': self.campaign_stats,
                'results': results
            }
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"❌ Erro fatal na campanha: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _load_campaign_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Carrega dados da campanha do arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            if not isinstance(data, list):
                raise ValueError("Arquivo deve conter uma lista de contatos")
            
            logger.info(LogCategory.BILLING, f"📁 Carregados {len(data)} registros do arquivo")
            return data
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"❌ Erro ao carregar arquivo: {str(e)}")
            raise
    
    def _filter_valid_contacts(self, contacts: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filtra contatos válidos baseado na configuração da campanha"""
        valid_contacts = []
        
        for contact in contacts:
            try:
                # Extrai dados do contato
                contact_info = self._extract_contact_info(contact)
                
                if not contact_info:
                    continue
                
                # Aplica filtros da campanha
                if self._apply_campaign_filters(contact_info, config):
                    valid_contacts.append(contact_info)
                    
            except Exception as e:
                logger.warning(LogCategory.BILLING, f"⚠️ Erro ao filtrar contato: {str(e)}")
                continue
        
        return valid_contacts
    
    def _extract_contact_info(self, contact: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extrai informações do contato do formato JSON"""
        try:
            # Estrutura esperada: {tipo, protocolo, dados_fpd, dados_vendas}
            if 'dados_vendas' not in contact or not contact['dados_vendas']:
                return None
            
            # Pega o primeiro registro de vendas (mais completo)
            venda = contact['dados_vendas'][0]
            
            # Extrai telefone principal
            telefone = self._extract_phone(venda.get('TELEFONE1', ''))
            if not telefone:
                return None
            
            # Extrai nome
            nome = venda.get('NOME', '').strip()
            if not nome:
                return None
            
            # Monta objeto de contato
            contact_info = {
                'protocolo': contact.get('protocolo', ''),
                'contrato': venda.get('CONTRATO', ''),
                'nome': nome,
                'telefone': telefone,
                'telefone2': self._extract_phone(venda.get('TELEFONE 2', '')),
                'email': venda.get('EMAIL', ''),
                'documento': venda.get('DOCUMENTO', ''),
                'cidade': venda.get('CIDADE', ''),
                'estado': venda.get('ESTADO', ''),
                'cep': venda.get('CEP', ''),
                'plano': venda.get('INTERNET', ''),
                'valor': venda.get('PREÇO', 0),
                'vendedor': venda.get('VENDEDOR', ''),
                'status': venda.get('STATUS', ''),
                'data_ativacao': venda.get('DATA AGENDA', ''),
                'dados_fpd': contact.get('dados_fpd', {}),
                'tipo_campanha': contact.get('tipo', '')
            }
            
            return contact_info
            
        except Exception as e:
            logger.warning(LogCategory.BILLING, f"⚠️ Erro ao extrair dados do contato: {str(e)}")
            return None
    
    def _extract_phone(self, phone_str: str) -> Optional[str]:
        """Extrai e formata número de telefone"""
        if not phone_str or phone_str.strip() == '':
            return None
        
        # Remove caracteres especiais
        phone = re.sub(r'[^\d]', '', str(phone_str))
        
        # Valida formato brasileiro
        if len(phone) >= 10 and len(phone) <= 11:
            # Adiciona código do país se não tiver
            if len(phone) == 10:
                phone = '55' + phone
            elif len(phone) == 11 and phone.startswith('0'):
                phone = '55' + phone[1:]
            
            return phone
        
        return None
    
    def _apply_campaign_filters(self, contact: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Aplica filtros da campanha ao contato"""
        try:
            # Filtro por status
            if 'status_filter' in config:
                allowed_statuses = config['status_filter']
                if contact['status'] not in allowed_statuses:
                    return False
            
            # Filtro por tipo de campanha
            if 'tipo_filter' in config:
                allowed_tipos = config['tipo_filter']
                if contact['tipo_campanha'] not in allowed_tipos:
                    return False
            
            # Filtro por valor mínimo
            if 'valor_minimo' in config:
                if contact['valor'] < config['valor_minimo']:
                    return False
            
            # Filtro por cidade
            if 'cidades' in config:
                if contact['cidade'] not in config['cidades']:
                    return False
            
            # Filtro por vendedor
            if 'vendedores' in config:
                if contact['vendedor'] not in config['vendedores']:
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(LogCategory.BILLING, f"⚠️ Erro ao aplicar filtros: {str(e)}")
            return False
    
    def _process_single_contact(self, contact: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um contato individual"""
        try:
            # Gera mensagem personalizada
            message = self._generate_personalized_message(contact, config)
            
            # Envia mensagem via WhatsApp
            result = self.billing_dispatcher.send_whatsapp_message(
                phone=contact['telefone'],
                message=message,
                contact_name=contact['nome']
            )
            
            # Registra resultado
            return {
                'contact_id': contact['protocolo'],
                'nome': contact['nome'],
                'telefone': contact['telefone'],
                'success': result.get('success', False),
                'message_id': result.get('message_id'),
                'error': result.get('error'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"❌ Erro ao processar contato {contact.get('protocolo', 'N/A')}: {str(e)}")
            return {
                'contact_id': contact.get('protocolo', 'N/A'),
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_personalized_message(self, contact: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Gera mensagem personalizada para o contato"""
        try:
            # Template base da campanha
            template = config.get('message_template', '')
            
            # Substitui variáveis
            message = template
            
            # Dados pessoais
            message = message.replace('{NOME}', contact['nome'])
            message = message.replace('{CIDADE}', contact['cidade'])
            message = message.replace('{PLANO}', contact['plano'])
            message = message.replace('{VALOR}', str(contact['valor']))
            message = message.replace('{VENDEDOR}', contact['vendedor'])
            
            # Dados FPD se disponível
            if contact.get('dados_fpd'):
                fpd = contact['dados_fpd']
                message = message.replace('{DIAS_FPD}', str(fpd.get('dias_fpd', 'N/A')))
                message = message.replace('{VALOR_COBRADO}', str(fpd.get('cobrado_fpd', 'N/A')))
                message = message.replace('{DATA_VENCIMENTO}', str(fpd.get('data_vencimento_fpd', 'N/A')))
            
            # Dados do contrato
            message = message.replace('{CONTRATO}', str(contact['contrato']))
            message = message.replace('{PROTOCOLO}', str(contact['protocolo']))
            
            return message
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"❌ Erro ao gerar mensagem: {str(e)}")
            return config.get('fallback_message', 'Olá! Temos uma mensagem importante para você.')
    
    def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Retorna status de uma campanha específica"""
        return self.processed_campaigns.get(campaign_id)
    
    def get_all_campaigns(self) -> Dict[str, Any]:
        """Retorna todas as campanhas processadas"""
        return {
            'total_campaigns': len(self.processed_campaigns),
            'campaigns': self.processed_campaigns
        }
    
    def get_campaign_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas gerais das campanhas"""
        total_stats = {
            'total_campaigns': len(self.processed_campaigns),
            'total_contacts_processed': 0,
            'total_messages_sent': 0,
            'total_errors': 0,
            'average_duration': 0
        }
        
        if self.processed_campaigns:
            for campaign in self.processed_campaigns.values():
                stats = campaign['stats']
                total_stats['total_contacts_processed'] += stats['total_contacts']
                total_stats['total_messages_sent'] += stats['messages_sent']
                total_stats['total_errors'] += stats['errors']
                total_stats['average_duration'] += stats.get('duration_seconds', 0)
            
            total_stats['average_duration'] /= len(self.processed_campaigns)
        
        return total_stats
    
    # ===== SISTEMA DE APRENDIZADO INTEGRADO =====
    
    def process_adaptive_campaign(self, file_path: str, campaign_config: Dict[str, Any]) -> Dict[str, Any]:
        """Processa campanha com aprendizado adaptativo"""
        try:
            logger.info(LogCategory.BILLING, f"🧠 Iniciando campanha adaptativa: {file_path}")
            
            # Carregar dados da campanha
            campaign_data = self._load_campaign_data(file_path)
            if not campaign_data:
                raise ValueError("Arquivo de campanha vazio ou inválido")
            
            # Aplicar aprendizado prévio
            optimized_config = self._apply_learning_to_campaign_config(campaign_config)
            
            # Filtrar contatos com análise comportamental
            valid_contacts = self._filter_contacts_with_behavior_analysis(campaign_data, optimized_config)
            
            # Processar com adaptação em tempo real
            results = self._process_with_real_time_adaptation(valid_contacts, optimized_config)
            
            # Analisar resultados para aprendizado
            learning_insights = self._analyze_campaign_for_learning(results, optimized_config)
            
            # Salvar dados de aprendizado
            campaign_id = f"adaptive_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.adaptive_campaigns[campaign_id] = {
                'config': optimized_config,
                'results': results,
                'learning_insights': learning_insights,
                'adaptations_applied': self.real_time_adaptation.get(campaign_id, [])
            }
            
            logger.info(LogCategory.BILLING, f"✅ Campanha adaptativa finalizada: {campaign_id}")
            
            return {
                'campaign_id': campaign_id,
                'success': True,
                'results': results,
                'learning_insights': learning_insights,
                'adaptations_applied': len(self.real_time_adaptation.get(campaign_id, []))
            }
            
        except Exception as e:
            logger.error(LogCategory.BILLING, f"❌ Erro na campanha adaptativa: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _apply_learning_to_campaign_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica aprendizado à configuração da campanha"""
        optimized_config = config.copy()
        
        # Obter insights do sistema de conversação
        if hasattr(self.conversation_bot, 'get_adaptive_insights'):
            insights = self.conversation_bot.get_adaptive_insights()
            
            # Otimizar templates baseado no aprendizado
            if 'response_effectiveness' in insights:
                best_templates = self._get_best_templates_from_learning(insights['response_effectiveness'])
                if best_templates:
                    optimized_config['optimized_templates'] = best_templates
            
            # Otimizar timing baseado no aprendizado
            if 'nlp_learning' in insights:
                optimal_timing = self._get_optimal_timing_from_learning(insights['nlp_learning'])
                if optimal_timing:
                    optimized_config['optimal_timing'] = optimal_timing
        
        return optimized_config
    
    def _get_best_templates_from_learning(self, response_effectiveness: Dict[str, Any]) -> List[str]:
        """Obtém melhores templates baseado no aprendizado"""
        best_templates = []
        
        for template, data in response_effectiveness.items():
            if data.get('success_rate', 0) > 0.7:
                best_templates.append(template)
        
        # Ordenar por taxa de sucesso
        best_templates.sort(key=lambda x: response_effectiveness[x]['success_rate'], reverse=True)
        return best_templates[:3]  # Top 3
    
    def _get_optimal_timing_from_learning(self, nlp_learning: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém timing ótimo baseado no aprendizado"""
        # Implementar lógica de timing baseada no aprendizado
        return {
            'best_hours': [9, 10, 14, 15, 16],
            'best_days': [1, 2, 3, 4, 5],  # Segunda a sexta
            'avoid_hours': [12, 13, 18, 19, 20]
        }
    
    def _filter_contacts_with_behavior_analysis(self, contacts: List[Dict[str, Any]], 
                                             config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filtra contatos com análise comportamental"""
        valid_contacts = []
        
        for contact in contacts:
            try:
                contact_info = self._extract_contact_info(contact)
                if not contact_info:
                    continue
                
                # Aplicar filtros padrão
                if not self._apply_campaign_filters(contact_info, config):
                    continue
                
                # Análise comportamental
                behavior_analysis = self._analyze_contact_behavior(contact_info)
                contact_info['behavior_analysis'] = behavior_analysis
                
                # Aplicar filtros baseados em comportamento
                if self._apply_behavioral_filters(contact_info, config):
                    valid_contacts.append(contact_info)
                    
            except Exception as e:
                logger.warning(LogCategory.BILLING, f"⚠️ Erro na análise comportamental: {str(e)}")
                continue
        
        return valid_contacts
    
    def _analyze_contact_behavior(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa comportamento do contato baseado em dados históricos"""
        phone = contact.get('telefone', '')
        
        # Obter perfil do cliente se existir
        if hasattr(self.conversation_bot, 'nlp_processor'):
            if phone in self.conversation_bot.nlp_processor.client_behavior_profiles:
                profile = self.conversation_bot.nlp_processor.client_behavior_profiles[phone]
                return {
                    'has_profile': True,
                    'cooperation_level': profile.get('cooperation_level', 0.5),
                    'payment_likelihood': profile.get('payment_likelihood', 0.3),
                    'escalation_risk': profile.get('escalation_frequency', 0.0),
                    'total_conversations': profile.get('total_conversations', 0),
                    'recommended_approach': self._get_recommended_approach(profile)
                }
        
        # Perfil padrão para novos contatos
        return {
            'has_profile': False,
            'cooperation_level': 0.5,
            'payment_likelihood': 0.3,
            'escalation_risk': 0.1,
            'total_conversations': 0,
            'recommended_approach': 'cobranca_educada'
        }
    
    def _get_recommended_approach(self, profile: Dict[str, Any]) -> str:
        """Obtém abordagem recomendada baseada no perfil"""
        cooperation_level = profile.get('cooperation_level', 0.5)
        escalation_risk = profile.get('escalation_frequency', 0.0)
        
        if escalation_risk > 0.3:
            return 'cobranca_educada'  # Abordagem mais cuidadosa
        elif cooperation_level > 0.7:
            return 'cobranca_educada'  # Cliente cooperativo
        elif cooperation_level < 0.3:
            return 'cobranca_direta'   # Cliente resistente
        else:
            return 'cobranca_informativa'  # Abordagem balanceada
    
    def _apply_behavioral_filters(self, contact: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Aplica filtros baseados em comportamento"""
        behavior = contact.get('behavior_analysis', {})
        
        # Filtrar clientes com alto risco de escalação se configurado
        if config.get('exclude_high_escalation_risk', False):
            if behavior.get('escalation_risk', 0.0) > 0.5:
                return False
        
        # Filtrar clientes com baixa probabilidade de pagamento se configurado
        if config.get('exclude_low_payment_likelihood', False):
            if behavior.get('payment_likelihood', 0.3) < 0.2:
                return False
        
        # Priorizar clientes cooperativos se configurado
        if config.get('prioritize_cooperative_clients', False):
            if behavior.get('cooperation_level', 0.5) > 0.6:
                contact['priority'] = 'high'
        
        return True
    
    def _process_with_real_time_adaptation(self, contacts: List[Dict[str, Any]], 
                                        config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processa contatos com adaptação em tempo real"""
        results = []
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.real_time_adaptation[campaign_id] = []
        
        for i, contact in enumerate(contacts):
            try:
                # Adaptar mensagem baseada no comportamento
                adapted_message = self._generate_adaptive_message(contact, config)
                
                # Enviar mensagem
                result = self.billing_dispatcher.send_whatsapp_message(
                    phone=contact['telefone'],
                    message=adapted_message,
                    contact_name=contact['nome']
                )
                
                # Registrar resultado
                contact_result = {
                    'contact_id': contact['protocolo'],
                    'nome': contact['nome'],
                    'telefone': contact['telefone'],
                    'success': result.get('success', False),
                    'message_id': result.get('message_id'),
                    'error': result.get('error'),
                    'timestamp': datetime.now().isoformat(),
                    'behavior_analysis': contact.get('behavior_analysis', {}),
                    'adaptive_message_used': True
                }
                
                results.append(contact_result)
                
                # Adaptação em tempo real baseada nos resultados
                if i % 10 == 0 and i > 0:  # A cada 10 contatos
                    adaptation = self._analyze_real_time_performance(results[-10:])
                    if adaptation:
                        self.real_time_adaptation[campaign_id].append(adaptation)
                        logger.info(LogCategory.BILLING, f"🔄 Adaptação aplicada: {adaptation}")
                
            except Exception as e:
                logger.error(LogCategory.BILLING, f"❌ Erro ao processar contato {contact.get('protocolo', 'N/A')}: {str(e)}")
                results.append({
                    'contact_id': contact.get('protocolo', 'N/A'),
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        return results
    
    def _generate_adaptive_message(self, contact: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Gera mensagem adaptativa baseada no comportamento"""
        behavior = contact.get('behavior_analysis', {})
        recommended_approach = behavior.get('recommended_approach', 'cobranca_educada')
        
        # Selecionar template baseado na abordagem recomendada
        template = config.get('message_template', '')
        
        # Personalizar baseado no comportamento
        if recommended_approach == 'cobranca_educada':
            template = template.replace('Olá', 'Olá! Espero que esteja bem')
        elif recommended_approach == 'cobranca_direta':
            template = template.replace('Oi', 'Bom dia')
        
        # Personalizar com dados do contato
        message = template
        message = message.replace('{NOME}', contact['nome'])
        message = message.replace('{CIDADE}', contact['cidade'])
        message = message.replace('{PLANO}', contact['plano'])
        message = message.replace('{VALOR}', str(contact['valor']))
        message = message.replace('{CONTRATO}', str(contact['contrato']))
        
        return message
    
    def _analyze_real_time_performance(self, recent_results: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analisa performance em tempo real e sugere adaptações"""
        if not recent_results:
            return None
        
        success_rate = len([r for r in recent_results if r.get('success', False)]) / len(recent_results)
        
        # Se taxa de sucesso for baixa, sugerir adaptação
        if success_rate < 0.7:
            return {
                'type': 'template_optimization',
                'reason': f'Taxa de sucesso baixa: {success_rate:.1%}',
                'suggestion': 'Usar templates mais educados',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _analyze_campaign_for_learning(self, results: List[Dict[str, Any]], 
                                    config: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa campanha para aprendizado futuro"""
        insights = {
            'total_contacts': len(results),
            'success_rate': 0.0,
            'behavior_analysis_summary': {},
            'template_effectiveness': {},
            'timing_analysis': {},
            'recommendations': []
        }
        
        if not results:
            return insights
        
        # Calcular taxa de sucesso
        successful = len([r for r in results if r.get('success', False)])
        insights['success_rate'] = successful / len(results)
        
        # Análise comportamental
        behavior_summary = {
            'cooperative_clients': 0,
            'resistant_clients': 0,
            'high_payment_likelihood': 0,
            'high_escalation_risk': 0
        }
        
        for result in results:
            behavior = result.get('behavior_analysis', {})
            if behavior.get('cooperation_level', 0.5) > 0.7:
                behavior_summary['cooperative_clients'] += 1
            elif behavior.get('cooperation_level', 0.5) < 0.3:
                behavior_summary['resistant_clients'] += 1
            
            if behavior.get('payment_likelihood', 0.3) > 0.6:
                behavior_summary['high_payment_likelihood'] += 1
            
            if behavior.get('escalation_risk', 0.0) > 0.3:
                behavior_summary['high_escalation_risk'] += 1
        
        insights['behavior_analysis_summary'] = behavior_summary
        
        # Gerar recomendações
        if insights['success_rate'] < 0.8:
            insights['recommendations'].append("Melhorar templates de mensagem")
        
        if behavior_summary['high_escalation_risk'] > len(results) * 0.2:
            insights['recommendations'].append("Reduzir frequência de contato para clientes com risco de escalação")
        
        if behavior_summary['cooperative_clients'] > len(results) * 0.6:
            insights['recommendations'].append("Focar em abordagem educada - maioria dos clientes são cooperativos")
        
        return insights
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Retorna status do sistema de aprendizado"""
        return {
            'learning_enabled': self.learning_enabled,
            'adaptive_campaigns_count': len(self.adaptive_campaigns),
            'client_behavior_analysis_count': len(self.client_behavior_analysis),
            'campaign_optimization_data_count': len(self.campaign_optimization_data),
            'real_time_adaptations_count': len(self.real_time_adaptation),
            'learning_confidence': self._calculate_learning_confidence()
        }
    
    def _calculate_learning_confidence(self) -> float:
        """Calcula confiança no sistema de aprendizado"""
        confidence = 0.0
        
        if self.adaptive_campaigns:
            confidence += 0.3
        if self.client_behavior_analysis:
            confidence += 0.3
        if self.campaign_optimization_data:
            confidence += 0.2
        if self.real_time_adaptation:
            confidence += 0.2
        
        return confidence
