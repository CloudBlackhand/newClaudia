import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from backend.modules.logger_system import LogCategory

@dataclass
class VendasData:
    """Dados de vendas extraídos do JSON"""
    nome: str
    documento: str
    telefone1: str
    telefone2: str
    email: str
    endereco: str
    cidade: str
    cep: str
    data_nascimento: str
    status: str
    aba_origem: str
    fpd: str
    is_valid: bool = True
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

class VendasDataProcessor:
    """Processador de dados de vendas do novo formato JSON"""
    
    def __init__(self):
        self.logger = None  # Será configurado externamente
    
    def set_logger(self, logger):
        """Configurar logger"""
        self.logger = logger
    
    def process_vendas_json(self, json_data: str) -> List[VendasData]:
        """Processar JSON de vendas e extrair dados válidos"""
        try:
            # Parse do JSON
            data = json.loads(json_data)
            
            if not isinstance(data, list):
                raise ValueError("JSON deve ser uma lista de registros")
            
            vendas_list = []
            
            for idx, record in enumerate(data):
                try:
                    # Verificar se tem dados_vendas
                    if 'dados_vendas' not in record or not record['dados_vendas']:
                        continue
                    
                    # Processar cada item em dados_vendas
                    for vendas_idx, vendas_item in enumerate(record['dados_vendas']):
                        try:
                            vendas_data = self._extract_vendas_data(vendas_item, idx, vendas_idx)
                            if vendas_data.is_valid:
                                vendas_list.append(vendas_data)
                        except Exception as e:
                            if self.logger:
                                self.logger.warning(LogCategory.SYSTEM, 
                                                   f"Erro ao processar item de vendas {vendas_idx} do registro {idx}: {e}")
                            continue
                            
                except Exception as e:
                    if self.logger:
                        self.logger.warning(LogCategory.SYSTEM, 
                                           f"Erro ao processar registro {idx}: {e}")
                    continue
            
            if self.logger:
                self.logger.info(LogCategory.SYSTEM, f"Processamento concluído: {len(vendas_list)} registros de vendas válidos")
            
            return vendas_list
            
        except Exception as e:
            if self.logger:
                self.logger.error(LogCategory.SYSTEM, f"Erro ao processar JSON de vendas: {e}")
            raise
    
    def _extract_vendas_data(self, vendas_item: Dict[str, Any], record_idx: int, vendas_idx: int) -> VendasData:
        """Extrair dados de vendas de um item individual"""
        validation_errors = []
        
        # Extrair campos básicos
        nome = str(vendas_item.get('NOME', '')).strip()
        documento = str(vendas_item.get('DOCUMENTO', '')).strip()
        telefone1 = str(vendas_item.get('TELEFONE1', '')).strip()
        telefone2 = str(vendas_item.get('TELEFONE2', '')).strip()
        email = str(vendas_item.get('EMAIL', '')).strip()
        endereco = str(vendas_item.get('RUA / ENDEREÇO', '')).strip()
        cidade = str(vendas_item.get('CIDADE', '')).strip()
        cep = str(vendas_item.get('CEP', '')).strip()
        data_nascimento = str(vendas_item.get('DATA NASCIMENTO', '')).strip()
        status = str(vendas_item.get('STATUS', '')).strip()
        aba_origem = str(vendas_item.get('aba_origem', '')).strip()
        fpd = str(vendas_item.get('fpd', '')).strip()
        
        # Validações básicas
        if not nome or nome == 'nan' or nome == 'NaN':
            validation_errors.append("Nome inválido ou ausente")
        
        if not documento or documento == 'nan' or documento == 'NaN':
            validation_errors.append("Documento inválido ou ausente")
        
        if not telefone1 or telefone1 == '#ERROR!' or telefone1 == 'nan' or telefone1 == 'NaN':
            validation_errors.append("Telefone principal inválido")
        
        # Limpar telefone
        telefone1 = self._clean_phone(telefone1)
        telefone2 = self._clean_phone(telefone2)
        
        # Limpar documento
        documento = self._clean_document(documento)
        
        # Limpar email
        email = self._clean_email(email)
        
        # Limpar CEP
        cep = self._clean_cep(cep)
        
        # Validar FPD
        if not fpd or fpd not in ['0', '1']:
            validation_errors.append("FPD deve ser 0 ou 1")
        
        # Criar objeto de dados
        vendas_data = VendasData(
            nome=nome,
            documento=documento,
            telefone1=telefone1,
            telefone2=telefone2,
            email=email,
            endereco=endereco,
            cidade=cidade,
            cep=cep,
            data_nascimento=data_nascimento,
            status=status,
            aba_origem=aba_origem,
            fpd=fpd,
            is_valid=len(validation_errors) == 0,
            validation_errors=validation_errors
        )
        
        return vendas_data
    
    def _clean_phone(self, phone: str) -> str:
        """Limpar e formatar telefone"""
        if not phone or phone in ['#ERROR!', 'nan', 'NaN', '0']:
            return ''
        
        # Remover caracteres especiais
        cleaned = re.sub(r'[^\d]', '', phone)
        
        # Verificar se tem pelo menos 10 dígitos
        if len(cleaned) >= 10:
            return cleaned
        else:
            return ''
    
    def _clean_document(self, document: str) -> str:
        """Limpar e formatar documento"""
        if not document or document in ['nan', 'NaN', '0']:
            return ''
        
        # Remover caracteres especiais
        cleaned = re.sub(r'[^\d]', '', document)
        
        # Verificar se tem pelo menos 11 dígitos (CPF) ou 14 (CNPJ)
        if len(cleaned) >= 11:
            return cleaned
        else:
            return ''
    
    def _clean_email(self, email: str) -> str:
        """Limpar e formatar email"""
        if not email or email in ['nan', 'NaN', '0', 'mailto:']:
            return ''
        
        # Remover 'mailto:' se presente
        if email.startswith('mailto:'):
            email = email[7:]
        
        # Verificar formato básico de email
        if '@' in email and '.' in email:
            return email.lower().strip()
        else:
            return ''
    
    def _clean_cep(self, cep: str) -> str:
        """Limpar e formatar CEP"""
        if not cep or cep in ['nan', 'NaN', '0', 'Oioo']:
            return ''
        
        # Remover caracteres especiais
        cleaned = re.sub(r'[^\d]', '', cep)
        
        # Verificar se tem 8 dígitos
        if len(cleaned) == 8:
            return cleaned
        else:
            return ''
    
    def get_processing_summary(self, vendas_list: List[VendasData]) -> Dict[str, Any]:
        """Obter resumo do processamento"""
        total = len(vendas_list)
        valid = len([v for v in vendas_list if v.is_valid])
        invalid = total - valid
        
        # Estatísticas por cidade
        cidades = {}
        for vendas in vendas_list:
            if vendas.is_valid:
                cidade = vendas.cidade.upper() if vendas.cidade else 'NÃO INFORMADO'
                cidades[cidade] = cidades.get(cidade, 0) + 1
        
        # Estatísticas por FPD
        fpd_stats = {}
        for vendas in vendas_list:
            if vendas.is_valid:
                fpd_val = vendas.fpd
                fpd_stats[fpd_val] = fpd_stats.get(fpd_val, 0) + 1
        
        return {
            'total_records': total,
            'valid_records': valid,
            'invalid_records': invalid,
            'success_rate': (valid / total * 100) if total > 0 else 0,
            'cities_distribution': cidades,
            'fpd_distribution': fpd_stats,
            'processing_timestamp': datetime.now().isoformat()
        }
    
    def convert_to_customer_format(self, vendas_data: VendasData) -> Dict[str, Any]:
        """Converter dados de vendas para formato de cliente"""
        return {
            'name': vendas_data.nome,
            'documento': vendas_data.documento,
            'phone': vendas_data.telefone1,
            'phone2': vendas_data.telefone2,
            'email': vendas_data.email,
            'endereco': vendas_data.endereco,
            'cidade': vendas_data.cidade,
            'cep': vendas_data.cep,
            'data_nascimento': vendas_data.data_nascimento,
            'status': vendas_data.status,
            'aba_origem': vendas_data.aba_origem,
            'fpd': vendas_data.fpd,
            'is_customer': True,
            'priority': 'high' if vendas_data.fpd == '1' else 'medium'
        }
