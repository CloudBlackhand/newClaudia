"""
Motor de Validação Rigorosa
Sistema de validação avançada para dados de entrada
"""
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Resultado da validação"""
    is_valid: bool
    valid_data: List[Dict[str, Any]]
    errors: List[str]
    warnings: List[str]
    total_records: int
    valid_records: int

class ValidationEngine:
    """Motor de validação rigorosa de dados"""
    
    def __init__(self):
        # Configurações de validação
        self.phone_patterns = [
            r'^\+?55\s?\d{2}\s?\d{4,5}-?\d{4}$',  # Padrão brasileiro
            r'^\d{10,11}$',  # Apenas números
            r'^\+?\d{12,15}$'  # Internacional
        ]
        
        # Campos obrigatórios para cobrança
        self.required_billing_fields = ["nome", "telefone", "valor"]
        
        # Campos opcionais mas recomendados
        self.optional_billing_fields = ["vencimento", "descricao", "email"]
        
        # Mapeamento de campos alternativos
        self.field_mapping = {
            "name": "nome",
            "phone": "telefone", 
            "amount": "valor",
            "due_date": "vencimento",
            "description": "descricao"
        }
    
    async def validate_billing_data(self, data: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validar dados de cobrança
        
        Args:
            data: Lista de dados de clientes
            
        Returns:
            Resultado da validação com dados válidos e erros
        """
        valid_data = []
        errors = []
        warnings = []
        
        if not data:
            return ValidationResult(
                is_valid=False,
                valid_data=[],
                errors=["Nenhum dado fornecido"],
                warnings=[],
                total_records=0,
                valid_records=0
            )
        
        for i, record in enumerate(data):
            record_errors = []
            record_warnings = []
            
            # Normalizar campos
            normalized_record = self._normalize_record(record)
            
            # Validar campos obrigatórios
            missing_fields = self._validate_required_fields(normalized_record)
            if missing_fields:
                record_errors.extend([f"Registro {i+1}: Campo obrigatório ausente - {field}" 
                                    for field in missing_fields])
            
            # Validar tipos de dados
            type_errors = self._validate_data_types(normalized_record)
            if type_errors:
                record_errors.extend([f"Registro {i+1}: {error}" for error in type_errors])
            
            # Validar telefone
            phone_error = self._validate_phone(normalized_record.get("telefone", ""))
            if phone_error:
                record_errors.append(f"Registro {i+1}: {phone_error}")
            
            # Validar valor
            value_error = self._validate_value(normalized_record.get("valor"))
            if value_error:
                record_errors.append(f"Registro {i+1}: {value_error}")
            
            # Validar data de vencimento se presente
            if "vencimento" in normalized_record:
                date_error = self._validate_date(normalized_record["vencimento"])
                if date_error:
                    record_warnings.append(f"Registro {i+1}: {date_error}")
            
            # Validar email se presente
            if "email" in normalized_record:
                email_error = self._validate_email(normalized_record["email"])
                if email_error:
                    record_warnings.append(f"Registro {i+1}: {email_error}")
            
            # Se não há erros críticos, adicionar aos dados válidos
            if not record_errors:
                # Aplicar formatações padrão
                formatted_record = self._format_record(normalized_record)
                valid_data.append(formatted_record)
            
            errors.extend(record_errors)
            warnings.extend(record_warnings)
        
        is_valid = len(valid_data) > 0
        
        return ValidationResult(
            is_valid=is_valid,
            valid_data=valid_data,
            errors=errors,
            warnings=warnings,
            total_records=len(data),
            valid_records=len(valid_data)
        )
    
    def _normalize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizar campos do registro"""
        normalized = {}
        
        for key, value in record.items():
            # Converter chave para minúscula
            lower_key = key.lower().strip()
            
            # Mapear campos alternativos
            mapped_key = self.field_mapping.get(lower_key, lower_key)
            
            # Limpar valor se for string
            if isinstance(value, str):
                value = value.strip()
            
            normalized[mapped_key] = value
        
        return normalized
    
    def _validate_required_fields(self, record: Dict[str, Any]) -> List[str]:
        """Validar campos obrigatórios"""
        missing_fields = []
        
        for field in self.required_billing_fields:
            if field not in record or not record[field] or str(record[field]).strip() == "":
                missing_fields.append(field)
        
        return missing_fields
    
    def _validate_data_types(self, record: Dict[str, Any]) -> List[str]:
        """Validar tipos de dados"""
        errors = []
        
        # Nome deve ser string não vazia
        if "nome" in record and not isinstance(record["nome"], str):
            errors.append("Nome deve ser um texto")
        
        # Telefone deve ser string
        if "telefone" in record and not isinstance(record["telefone"], (str, int)):
            errors.append("Telefone deve ser um texto ou número")
        
        return errors
    
    def _validate_phone(self, phone: str) -> Optional[str]:
        """Validar número de telefone"""
        if not phone:
            return "Telefone é obrigatório"
        
        # Converter para string se for número
        phone_str = str(phone).strip()
        
        # Remover caracteres especiais para validação
        clean_phone = re.sub(r'[^\d+]', '', phone_str)
        
        # Verificar padrões válidos
        for pattern in self.phone_patterns:
            if re.match(pattern, phone_str) or re.match(pattern, clean_phone):
                return None
        
        return "Formato de telefone inválido"
    
    def _validate_value(self, value: Any) -> Optional[str]:
        """Validar valor monetário"""
        if value is None or value == "":
            return "Valor é obrigatório"
        
        # Converter string para número se necessário
        if isinstance(value, str):
            # Remover formatação monetária comum
            clean_value = re.sub(r'[R$\s.,]', '', value.replace(',', '.'))
            try:
                float_value = float(clean_value)
            except ValueError:
                return "Valor deve ser um número válido"
        elif isinstance(value, (int, float)):
            float_value = float(value)
        else:
            return "Valor deve ser um número"
        
        if float_value < 0:
            return "Valor não pode ser negativo"
        
        if float_value == 0:
            return "Valor deve ser maior que zero"
        
        return None
    
    def _validate_date(self, date_value: Any) -> Optional[str]:
        """Validar data de vencimento"""
        if not date_value:
            return None
        
        date_str = str(date_value).strip()
        
        # Tentar diferentes formatos de data
        date_formats = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%y",
            "%Y/%m/%d"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # Verificar se a data não é muito no passado
                if parsed_date.year < 2020:
                    return "Data de vencimento muito antiga"
                return None
            except ValueError:
                continue
        
        return "Formato de data inválido (use DD/MM/AAAA)"
    
    def _validate_email(self, email: str) -> Optional[str]:
        """Validar email"""
        if not email:
            return None
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return "Formato de email inválido"
        
        return None
    
    def _format_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Aplicar formatações padrão ao registro"""
        formatted = record.copy()
        
        # Formatar telefone
        if "telefone" in formatted:
            formatted["telefone"] = self._format_phone(formatted["telefone"])
        
        # Formatar valor
        if "valor" in formatted:
            formatted["valor"] = self._format_value(formatted["valor"])
        
        # Formatar nome
        if "nome" in formatted:
            formatted["nome"] = str(formatted["nome"]).strip().title()
        
        return formatted
    
    def _format_phone(self, phone: Any) -> str:
        """Formatar número de telefone"""
        phone_str = str(phone).strip()
        
        # Remover caracteres especiais
        clean_phone = re.sub(r'[^\d+]', '', phone_str)
        
        # Garantir que tenha código do país
        if not clean_phone.startswith('+'):
            if clean_phone.startswith('55'):
                clean_phone = '+' + clean_phone
            elif len(clean_phone) in [10, 11]:  # Número brasileiro sem código
                clean_phone = '+55' + clean_phone
        
        return clean_phone
    
    def _format_value(self, value: Any) -> str:
        """Formatar valor monetário"""
        if isinstance(value, str):
            # Remover formatação e converter
            clean_value = re.sub(r'[R$\s]', '', value.replace(',', '.'))
            try:
                float_value = float(clean_value)
            except ValueError:
                return str(value)
        else:
            float_value = float(value)
        
        # Formatar como moeda brasileira
        return f"{float_value:.2f}".replace('.', ',')
    
    async def validate_json_structure(self, json_data: str) -> Dict[str, Any]:
        """Validar estrutura do JSON"""
        try:
            data = json.loads(json_data)
            
            if not isinstance(data, (list, dict)):
                return {
                    "is_valid": False,
                    "error": "JSON deve conter uma lista ou objeto"
                }
            
            if isinstance(data, dict):
                data = [data]
            
            if len(data) == 0:
                return {
                    "is_valid": False,
                    "error": "JSON não contém dados"
                }
            
            if len(data) > 10000:  # Limite para Railway
                return {
                    "is_valid": False,
                    "error": "Muitos registros (máximo 10.000)"
                }
            
            return {
                "is_valid": True,
                "records_count": len(data),
                "data": data
            }
            
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "error": f"JSON inválido: {str(e)}"
            }
    
    async def validate_template(self, template: str) -> Dict[str, Any]:
        """Validar template de mensagem"""
        if not template or not template.strip():
            return {
                "is_valid": False,
                "error": "Template não pode estar vazio"
            }
        
        # Verificar placeholders válidos
        valid_placeholders = ["{nome}", "{valor}", "{vencimento}", "{descricao}"]
        found_placeholders = re.findall(r'\{[^}]+\}', template)
        
        invalid_placeholders = [p for p in found_placeholders if p not in valid_placeholders]
        
        if invalid_placeholders:
            return {
                "is_valid": False,
                "error": f"Placeholders inválidos: {', '.join(invalid_placeholders)}",
                "valid_placeholders": valid_placeholders
            }
        
        # Verificar tamanho (WhatsApp tem limite)
        if len(template) > 4096:
            return {
                "is_valid": False,
                "error": "Template muito longo (máximo 4096 caracteres)"
            }
        
        return {
            "is_valid": True,
            "placeholders_found": found_placeholders,
            "template_length": len(template)
        }
