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
