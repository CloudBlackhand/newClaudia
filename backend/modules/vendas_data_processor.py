import json
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from backend.modules.logger_system import SmartLogger, LogCategory

logger = SmartLogger()

@dataclass
class VendasData:
    """Dados de vendas processados"""
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
        self.logger = logger
    
    def process_vendas_file(self, file_path: str) -> Tuple[List[VendasData], List[str]]:
        """Processa arquivo JSON de vendas"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.process_vendas_json(content)
            
        except Exception as e:
            self.logger.error(LogCategory.SYSTEM, f"Erro ao processar arquivo de vendas: {e}")
            return [], [f"Erro ao ler arquivo: {str(e)}"]
    
    def process_vendas_json(self, json_content: str) -> Tuple[List[VendasData], List[str]]:
        """Processa conteúdo JSON de vendas"""
        try:
            data = json.loads(json_content)
            vendas_data = []
            errors = []
            
            if not isinstance(data, list):
                return [], ["Formato inválido: deve ser uma lista"]
            
            for idx, item in enumerate(data):
                try:
                    # Extrair dados de vendas
                    if 'dados_vendas' not in item or not item['dados_vendas']:
                        continue
                    
                    for venda in item['dados_vendas']:
                        vendas_item = self._process_venda_item(venda, idx)
                        if vendas_item.is_valid:
                            vendas_data.append(vendas_item)
                        else:
                            errors.extend(vendas_item.validation_errors)
                            
                except Exception as e:
                    errors.append(f"Erro ao processar item {idx}: {str(e)}")
            
            self.logger.info(LogCategory.SYSTEM, f"Processamento concluído: {len(vendas_data)} vendas válidas, {len(errors)} erros")
            return vendas_data, errors
            
        except json.JSONDecodeError as e:
            return [], [f"JSON inválido: {str(e)}"]
        except Exception as e:
            return [], [f"Erro ao processar JSON: {str(e)}"]
    
    def _process_venda_item(self, venda: Dict[str, Any], index: int) -> VendasData:
        """Processa item individual de venda"""
        errors = []
        
        # Extrair e validar campos
        nome = self._clean_string(venda.get('NOME', ''))
        if not nome:
            errors.append(f"Item {index}: NOME é obrigatório")
        
        documento = self._clean_documento(venda.get('DOCUMENTO', ''))
        if not documento:
            errors.append(f"Item {index}: DOCUMENTO é obrigatório")
        
        telefone1 = self._clean_telefone(venda.get('TELEFONE1', ''))
        telefone2 = self._clean_telefone(venda.get('TELEFONE2', ''))
        
        email = self._clean_email(venda.get('EMAIL', ''))
        endereco = self._clean_string(venda.get('RUA / ENDEREÇO', ''))
        cidade = self._clean_string(venda.get('CIDADE', ''))
        cep = self._clean_cep(venda.get('CEP', ''))
        data_nascimento = self._clean_data_nascimento(venda.get('DATA NASCIMENTO', ''))
        status = self._clean_string(venda.get('STATUS', ''))
        aba_origem = self._clean_string(venda.get('aba_origem', ''))
        fpd = self._clean_string(venda.get('fpd', ''))
        
        # Validar FPD
        if fpd not in ['1', '2', '3']:
            errors.append(f"Item {index}: FPD deve ser 1, 2 ou 3")
        
        # Validar telefone principal
        if not telefone1 or telefone1 == '#ERROR!':
            errors.append(f"Item {index}: TELEFONE1 é obrigatório e válido")
        
        return VendasData(
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
            is_valid=len(errors) == 0,
            validation_errors=errors
        )
    
    def _clean_string(self, value: Any) -> str:
        """Limpa string"""
        if not value:
            return ""
        return str(value).strip()
    
    def _clean_documento(self, value: str) -> str:
        """Limpa documento (CPF/CNPJ)"""
        if not value:
            return ""
        # Remove caracteres especiais
        cleaned = re.sub(r'[^\d]', '', str(value))
        return cleaned
    
    def _clean_telefone(self, value: str) -> str:
        """Limpa telefone"""
        if not value or value == '#ERROR!':
            return ""
        # Remove caracteres especiais
        cleaned = re.sub(r'[^\d]', '', str(value))
        return cleaned
    
    def _clean_email(self, value: str) -> str:
        """Limpa email"""
        if not value:
            return ""
        return str(value).strip().lower()
    
    def _clean_cep(self, value: str) -> str:
        """Limpa CEP"""
        if not value:
            return ""
        # Remove caracteres especiais
        cleaned = re.sub(r'[^\d]', '', str(value))
        return cleaned
    
    def _clean_data_nascimento(self, value: str) -> str:
        """Limpa data de nascimento"""
        if not value:
            return ""
        # Tenta converter para formato padrão
        try:
            # Formato: DD/MM/YYYY ou YYYY/MM/DD
            if '/' in str(value):
                parts = str(value).split('/')
                if len(parts) == 3:
                    if len(parts[0]) == 4:  # YYYY/MM/DD
                        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                    else:  # DD/MM/YYYY
                        return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        except:
            pass
        return str(value)
    
    def get_processing_summary(self, vendas_data: List[VendasData]) -> Dict[str, Any]:
        """Gera resumo do processamento"""
        total = len(vendas_data)
        valid = len([v for v in vendas_data if v.is_valid])
        invalid = total - valid
        
        # Estatísticas por cidade
        cidades = {}
        for venda in vendas_data:
            cidade = venda.cidade or 'Sem cidade'
            if cidade not in cidades:
                cidades[cidade] = {'total': 0, 'fpd1': 0, 'fpd2': 0, 'fpd3': 0}
            cidades[cidade]['total'] += 1
            if venda.fpd == '1':
                cidades[cidade]['fpd1'] += 1
            elif venda.fpd == '2':
                cidades[cidade]['fpd2'] += 1
            elif venda.fpd == '3':
                cidades[cidade]['fpd3'] += 1
        
        # Estatísticas por FPD
        fpd_stats = {'1': 0, '2': 0, '3': 0}
        for venda in vendas_data:
            if venda.fpd in fpd_stats:
                fpd_stats[venda.fpd] += 1
        
        return {
            'total_records': total,
            'valid_records': valid,
            'invalid_records': invalid,
            'validation_rate': (valid / total * 100) if total > 0 else 0,
            'cidades': cidades,
            'fpd_distribution': fpd_stats,
            'processing_timestamp': datetime.now().isoformat()
        }
