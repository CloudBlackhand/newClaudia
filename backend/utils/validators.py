"""
Sistema de validação rigorosa de dados
"""
import re
import json
import phonenumbers
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, validator, Field
from backend.utils.logger import app_logger

class ClientValidator:
    """Validador para dados de clientes"""
    
    @staticmethod
    def validate_phone(phone: str) -> Dict[str, Any]:
        """Valida número de telefone brasileiro"""
        result = {"valid": False, "formatted": None, "errors": []}
        
        if not phone:
            result["errors"].append("Telefone é obrigatório")
            return result
        
        # Remove caracteres não numéricos
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        # Verifica formato brasileiro
        if not clean_phone.startswith('55'):
            clean_phone = '55' + clean_phone
        
        try:
            parsed = phonenumbers.parse(clean_phone, None)
            
            if phonenumbers.is_valid_number(parsed):
                result["valid"] = True
                result["formatted"] = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
            else:
                result["errors"].append("Número de telefone inválido")
                
        except phonenumbers.NumberParseException as e:
            result["errors"].append(f"Erro ao processar telefone: {e}")
        
        return result
    
    @staticmethod
    def validate_amount(amount: Union[str, float, int]) -> Dict[str, Any]:
        """Valida valor monetário"""
        result = {"valid": False, "value": None, "errors": []}
        
        if amount is None:
            result["errors"].append("Valor é obrigatório")
            return result
        
        try:
            # Converte string para Decimal para precisão
            if isinstance(amount, str):
                # Remove caracteres não numéricos exceto vírgula e ponto
                clean_amount = re.sub(r'[^\d,.]', '', amount)
                # Substitui vírgula por ponto
                clean_amount = clean_amount.replace(',', '.')
                decimal_amount = Decimal(clean_amount)
            else:
                decimal_amount = Decimal(str(amount))
            
            if decimal_amount <= 0:
                result["errors"].append("Valor deve ser maior que zero")
            elif decimal_amount > Decimal('999999.99'):
                result["errors"].append("Valor muito alto")
            else:
                result["valid"] = True
                result["value"] = float(decimal_amount)
                
        except (InvalidOperation, ValueError) as e:
            result["errors"].append(f"Valor inválido: {e}")
        
        return result
    
    @staticmethod
    def validate_name(name: str) -> Dict[str, Any]:
        """Valida nome do cliente"""
        result = {"valid": False, "formatted": None, "errors": []}
        
        if not name or not name.strip():
            result["errors"].append("Nome é obrigatório")
            return result
        
        clean_name = name.strip()
        
        # Verifica comprimento
        if len(clean_name) < 2:
            result["errors"].append("Nome deve ter pelo menos 2 caracteres")
        elif len(clean_name) > 100:
            result["errors"].append("Nome muito longo (máximo 100 caracteres)")
        # Verifica caracteres válidos
        elif not re.match(r'^[a-zA-ZÀ-ÿ\s\-\'\.]+$', clean_name):
            result["errors"].append("Nome contém caracteres inválidos")
        else:
            result["valid"] = True
            result["formatted"] = clean_name.title()
        
        return result

class ClientData(BaseModel):
    """Modelo Pydantic para dados de cliente"""
    
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    amount: float = Field(..., gt=0, le=999999.99)
    due_date: Optional[str] = None
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('name')
    def validate_name(cls, v):
        validation = ClientValidator.validate_name(v)
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))
        return validation["formatted"]
    
    @validator('phone')
    def validate_phone(cls, v):
        validation = ClientValidator.validate_phone(v)
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))
        return validation["formatted"]
    
    @validator('amount')
    def validate_amount(cls, v):
        validation = ClientValidator.validate_amount(v)
        if not validation["valid"]:
            raise ValueError("; ".join(validation["errors"]))
        return validation["value"]
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v is None:
            return v
        
        try:
            # Tenta diferentes formatos de data
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    parsed_date = datetime.strptime(v, fmt)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            raise ValueError("Formato de data inválido")
        except Exception:
            raise ValueError("Data de vencimento inválida")

class JSONValidator:
    """Validador para arquivos JSON"""
    
    @staticmethod
    def validate_json_structure(data: Any) -> Dict[str, Any]:
        """Valida estrutura básica do JSON"""
        result = {"valid": False, "errors": [], "warnings": []}
        
        if not isinstance(data, list):
            result["errors"].append("JSON deve ser uma lista de clientes")
            return result
        
        if not data:
            result["errors"].append("Lista de clientes não pode estar vazia")
            return result
        
        if len(data) > 10000:
            result["warnings"].append("Lista muito grande (>10000 itens), considere processar em lotes")
        
        result["valid"] = True
        return result
    
    @staticmethod
    def validate_clients_batch(clients_data: List[Dict]) -> Dict[str, Any]:
        """Valida lote de clientes"""
        result = {
            "valid": True,
            "total": len(clients_data),
            "valid_clients": [],
            "invalid_clients": [],
            "errors": [],
            "warnings": []
        }
        
        seen_ids = set()
        seen_phones = set()
        
        for idx, client_data in enumerate(clients_data):
            client_result = JSONValidator.validate_single_client(client_data, idx)
            
            if client_result["valid"]:
                # Verifica duplicatas
                client_id = client_data.get("id")
                phone = client_result["data"].phone
                
                if client_id in seen_ids:
                    client_result["valid"] = False
                    client_result["errors"].append(f"ID duplicado: {client_id}")
                
                if phone in seen_phones:
                    client_result["valid"] = False
                    client_result["errors"].append(f"Telefone duplicado: {phone}")
                
                if client_result["valid"]:
                    seen_ids.add(client_id)
                    seen_phones.add(phone)
                    result["valid_clients"].append(client_result["data"])
                else:
                    result["invalid_clients"].append(client_result)
            else:
                result["invalid_clients"].append(client_result)
        
        # Se muitos clientes inválidos, marca lote como inválido
        invalid_percentage = len(result["invalid_clients"]) / result["total"] * 100
        if invalid_percentage > 20:  # Mais de 20% inválidos
            result["valid"] = False
            result["errors"].append(f"Muitos clientes inválidos ({invalid_percentage:.1f}%)")
        elif invalid_percentage > 10:  # Entre 10-20% inválidos
            result["warnings"].append(f"Percentual alto de clientes inválidos ({invalid_percentage:.1f}%)")
        
        return result
    
    @staticmethod
    def validate_single_client(client_data: Dict, index: int = None) -> Dict[str, Any]:
        """Valida um único cliente"""
        result = {"valid": False, "data": None, "errors": [], "index": index}
        
        try:
            # Usa Pydantic para validação
            validated_client = ClientData(**client_data)
            result["valid"] = True
            result["data"] = validated_client
            
        except Exception as e:
            result["errors"].append(str(e))
            app_logger.warning("CLIENT_VALIDATION_FAILED", {
                "index": index,
                "errors": result["errors"],
                "client_data_keys": list(client_data.keys()) if isinstance(client_data, dict) else "not_dict"
            })
        
        return result

class MessageValidator:
    """Validador para mensagens e templates"""
    
    @staticmethod
    def validate_template(template: str, required_vars: List[str] = None) -> Dict[str, Any]:
        """Valida template de mensagem"""
        result = {"valid": False, "variables": [], "errors": []}
        
        if not template or not template.strip():
            result["errors"].append("Template não pode estar vazio")
            return result
        
        # Encontra variáveis no template (formato {variavel})
        variables = re.findall(r'\{(\w+)\}', template)
        result["variables"] = variables
        
        # Verifica se todas as variáveis obrigatórias estão presentes
        if required_vars:
            missing_vars = set(required_vars) - set(variables)
            if missing_vars:
                result["errors"].append(f"Variáveis obrigatórias ausentes: {', '.join(missing_vars)}")
        
        # Verifica comprimento
        if len(template) > 4096:  # Limite do WhatsApp
            result["errors"].append("Template muito longo (máximo 4096 caracteres)")
        
        if not result["errors"]:
            result["valid"] = True
        
        return result
    
    @staticmethod
    def validate_message_content(message: str) -> Dict[str, Any]:
        """Valida conteúdo de mensagem"""
        result = {"valid": False, "errors": []}
        
        if not message or not message.strip():
            result["errors"].append("Mensagem não pode estar vazia")
            return result
        
        # Verifica comprimento
        if len(message) > 4096:
            result["errors"].append("Mensagem muito longa (máximo 4096 caracteres)")
        
        # Verifica caracteres problemáticos
        if '\x00' in message:  # Null bytes
            result["errors"].append("Mensagem contém caracteres inválidos")
        
        if not result["errors"]:
            result["valid"] = True
        
        return result

class SecurityValidator:
    """Validadores de segurança"""
    
    @staticmethod
    def validate_file_upload(filename: str, content: bytes, allowed_extensions: List[str]) -> Dict[str, Any]:
        """Valida upload de arquivo"""
        result = {"valid": False, "errors": []}
        
        # Verifica extensão
        if '.' not in filename:
            result["errors"].append("Arquivo deve ter extensão")
            return result
        
        extension = filename.rsplit('.', 1)[1].lower()
        if extension not in allowed_extensions:
            result["errors"].append(f"Extensão não permitida. Permitidas: {', '.join(allowed_extensions)}")
        
        # Verifica tamanho
        if len(content) > 16 * 1024 * 1024:  # 16MB
            result["errors"].append("Arquivo muito grande (máximo 16MB)")
        
        # Verifica se é JSON válido (para arquivos .json)
        if extension == 'json':
            try:
                json.loads(content.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                result["errors"].append("Arquivo JSON inválido")
        
        if not result["errors"]:
            result["valid"] = True
        
        return result
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitiza entrada de texto"""
        if not text:
            return ""
        
        # Remove caracteres perigosos
        sanitized = re.sub(r'[<>"\'\x00-\x1f\x7f-\x9f]', '', text)
        
        # Limita comprimento
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()

