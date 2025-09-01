#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Validação de Dados JSON
Sistema robusto de validação para dados de clientes
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Níveis de validação"""
    BASIC = "basic"
    STRICT = "strict"
    PARANOID = "paranoid"

@dataclass
class ValidationError:
    """Estrutura para erros de validação"""
    field: str
    message: str
    value: Any
    severity: str = "error"

@dataclass
class ValidationResult:
    """Resultado da validação"""
    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    sanitized_data: Optional[Dict[str, Any]] = None

class ClientDataValidator:
    """Validador especializado para dados de clientes"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        self.validation_level = validation_level
        self.phone_regex = re.compile(r'^(?:\+?55)?(?:\d{2})?[6-9]\d{8}$')
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.cpf_regex = re.compile(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$|^\d{11}$')
        
    def validate_client_list(self, json_data: str) -> ValidationResult:
        """Validar lista completa de clientes"""
        try:
            # Parse inicial do JSON
            try:
                data = json.loads(json_data)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    is_valid=False,
                    errors=[ValidationError("json", f"JSON inválido: {e}", json_data)],
                    warnings=[]
                )
            
            # Validar estrutura base
            structure_result = self._validate_structure(data)
            if not structure_result.is_valid:
                return structure_result
            
            # Validar cada cliente
            errors = []
            warnings = []
            sanitized_clients = []
            
            for idx, client in enumerate(data.get('clients', [])):
                client_result = self.validate_client(client, idx)
                errors.extend(client_result.errors)
                warnings.extend(client_result.warnings)
                
                if client_result.is_valid and client_result.sanitized_data:
                    sanitized_clients.append(client_result.sanitized_data)
            
            # Verificar duplicatas
            duplicate_errors = self._check_duplicates(sanitized_clients)
            errors.extend(duplicate_errors)
            
            is_valid = len(errors) == 0
            sanitized_data = None
            
            if is_valid:
                sanitized_data = {
                    'clients': sanitized_clients,
                    'metadata': {
                        'total_clients': len(sanitized_clients),
                        'validation_timestamp': datetime.now().isoformat(),
                        'validation_level': self.validation_level.value
                    }
                }
            
            logger.info(f"Validação concluída: {len(sanitized_clients)} clientes válidos, {len(errors)} erros")
            
            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                sanitized_data=sanitized_data
            )
            
        except Exception as e:
            logger.error(f"Erro durante validação: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("system", f"Erro interno: {e}", None)],
                warnings=[]
            )
    
    def validate_client(self, client_data: Dict[str, Any], index: int = 0) -> ValidationResult:
        """Validar dados de um cliente individual"""
        errors = []
        warnings = []
        sanitized = {}
        
        # Campos obrigatórios
        required_fields = ['name', 'phone', 'amount', 'due_date']
        
        for field in required_fields:
            if field not in client_data or not client_data[field]:
                errors.append(ValidationError(
                    f"client[{index}].{field}",
                    f"Campo obrigatório ausente ou vazio",
                    client_data.get(field)
                ))
                continue
            
            # Validar cada campo específico
            validation_method = getattr(self, f'_validate_{field}', None)
            if validation_method:
                field_errors, field_warnings, sanitized_value = validation_method(
                    client_data[field], index
                )
                errors.extend(field_errors)
                warnings.extend(field_warnings)
                if not field_errors:
                    sanitized[field] = sanitized_value
            else:
                sanitized[field] = client_data[field]
        
        # Campos opcionais
        optional_fields = ['email', 'cpf', 'description', 'tags']
        for field in optional_fields:
            if field in client_data and client_data[field]:
                validation_method = getattr(self, f'_validate_{field}', None)
                if validation_method:
                    field_errors, field_warnings, sanitized_value = validation_method(
                        client_data[field], index
                    )
                    errors.extend(field_errors)
                    warnings.extend(field_warnings)
                    if not field_errors:
                        sanitized[field] = sanitized_value
                else:
                    sanitized[field] = client_data[field]
        
        # Adicionar ID único se não existir
        if 'id' not in sanitized:
            sanitized['id'] = f"client_{index}_{hash(str(client_data))}"
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            sanitized_data=sanitized if len(errors) == 0 else None
        )
    
    def _validate_structure(self, data: Any) -> ValidationResult:
        """Validar estrutura básica do JSON"""
        errors = []
        
        if not isinstance(data, dict):
            errors.append(ValidationError("root", "Root deve ser um objeto JSON", type(data)))
            return ValidationResult(False, errors, [])
        
        if 'clients' not in data:
            errors.append(ValidationError("clients", "Campo 'clients' obrigatório", None))
            return ValidationResult(False, errors, [])
        
        if not isinstance(data['clients'], list):
            errors.append(ValidationError("clients", "Campo 'clients' deve ser uma lista", type(data['clients'])))
            return ValidationResult(False, errors, [])
        
        if len(data['clients']) == 0:
            errors.append(ValidationError("clients", "Lista de clientes não pode estar vazia", 0))
            return ValidationResult(False, errors, [])
        
        return ValidationResult(True, [], [])
    
    def _validate_name(self, value: Any, index: int) -> Tuple[List[ValidationError], List[ValidationError], str]:
        """Validar nome do cliente"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append(ValidationError(f"client[{index}].name", "Nome deve ser string", value))
            return errors, warnings, value
        
        # Limpar e sanitizar
        sanitized = value.strip().title()
        
        if len(sanitized) < 2:
            errors.append(ValidationError(f"client[{index}].name", "Nome muito curto (mínimo 2 caracteres)", sanitized))
        
        if len(sanitized) > 100:
            warnings.append(ValidationError(f"client[{index}].name", "Nome muito longo", sanitized, "warning"))
            sanitized = sanitized[:100]
        
        # Verificar caracteres especiais suspeitos
        if re.search(r'[<>{}[\]\\|`~]', sanitized):
            warnings.append(ValidationError(f"client[{index}].name", "Nome contém caracteres suspeitos", sanitized, "warning"))
        
        return errors, warnings, sanitized
    
    def _validate_phone(self, value: Any, index: int) -> Tuple[List[ValidationError], List[ValidationError], str]:
        """Validar telefone do cliente"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append(ValidationError(f"client[{index}].phone", "Telefone deve ser string", value))
            return errors, warnings, value
        
        # Limpar telefone
        cleaned = re.sub(r'[^\d+]', '', value)
        
        # Normalizar formato brasileiro
        if cleaned.startswith('+55'):
            cleaned = cleaned[3:]
        elif cleaned.startswith('55') and len(cleaned) > 11:
            cleaned = cleaned[2:]
        
        # Adicionar DDD padrão se necessário (11 - São Paulo)
        if len(cleaned) == 9 and cleaned[0] in '6789':
            cleaned = '11' + cleaned
            warnings.append(ValidationError(f"client[{index}].phone", "DDD 11 adicionado automaticamente", cleaned, "warning"))
        
        # Validar formato
        if not self.phone_regex.match(cleaned):
            errors.append(ValidationError(f"client[{index}].phone", "Formato de telefone inválido", cleaned))
        
        # Formatação final
        if len(cleaned) == 11:
            sanitized = f"+55{cleaned}"
        else:
            sanitized = cleaned
        
        return errors, warnings, sanitized
    
    def _validate_amount(self, value: Any, index: int) -> Tuple[List[ValidationError], List[ValidationError], float]:
        """Validar valor da cobrança"""
        errors = []
        warnings = []
        
        try:
            if isinstance(value, str):
                # Remover formatação monetária
                cleaned = re.sub(r'[R$\s.,]', '', value)
                cleaned = cleaned.replace(',', '.')
                amount = float(cleaned) / 100 if '.' not in value and len(cleaned) > 2 else float(cleaned)
            else:
                amount = float(value)
            
            if amount <= 0:
                errors.append(ValidationError(f"client[{index}].amount", "Valor deve ser positivo", amount))
            
            if amount > 1000000:
                warnings.append(ValidationError(f"client[{index}].amount", "Valor muito alto", amount, "warning"))
            
            # Arredondar para 2 casas decimais
            sanitized = round(amount, 2)
            
            return errors, warnings, sanitized
            
        except (ValueError, TypeError):
            errors.append(ValidationError(f"client[{index}].amount", "Valor inválido", value))
            return errors, warnings, 0.0
    
    def _validate_due_date(self, value: Any, index: int) -> Tuple[List[ValidationError], List[ValidationError], str]:
        """Validar data de vencimento"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append(ValidationError(f"client[{index}].due_date", "Data deve ser string", value))
            return errors, warnings, value
        
        # Tentar diferentes formatos de data
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        parsed_date = None
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            errors.append(ValidationError(f"client[{index}].due_date", "Formato de data inválido", value))
            return errors, warnings, value
        
        # Verificar se a data é futura
        if parsed_date.date() < datetime.now().date():
            warnings.append(ValidationError(f"client[{index}].due_date", "Data de vencimento no passado", value, "warning"))
        
        # Padronizar formato
        sanitized = parsed_date.strftime('%Y-%m-%d')
        
        return errors, warnings, sanitized
    
    def _validate_email(self, value: Any, index: int) -> Tuple[List[ValidationError], List[ValidationError], str]:
        """Validar email do cliente"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append(ValidationError(f"client[{index}].email", "Email deve ser string", value))
            return errors, warnings, value
        
        sanitized = value.strip().lower()
        
        if not self.email_regex.match(sanitized):
            errors.append(ValidationError(f"client[{index}].email", "Formato de email inválido", sanitized))
        
        return errors, warnings, sanitized
    
    def _validate_cpf(self, value: Any, index: int) -> Tuple[List[ValidationError], List[ValidationError], str]:
        """Validar CPF do cliente"""
        errors = []
        warnings = []
        
        if not isinstance(value, str):
            errors.append(ValidationError(f"client[{index}].cpf", "CPF deve ser string", value))
            return errors, warnings, value
        
        # Limpar CPF
        cleaned = re.sub(r'[^\d]', '', value)
        
        if len(cleaned) != 11:
            errors.append(ValidationError(f"client[{index}].cpf", "CPF deve ter 11 dígitos", cleaned))
            return errors, warnings, cleaned
        
        # Validar dígitos verificadores (simplificado)
        if cleaned == cleaned[0] * 11:
            errors.append(ValidationError(f"client[{index}].cpf", "CPF inválido (todos dígitos iguais)", cleaned))
        
        # Formatação
        sanitized = f"{cleaned[:3]}.{cleaned[3:6]}.{cleaned[6:9]}-{cleaned[9:]}"
        
        return errors, warnings, sanitized
    
    def _check_duplicates(self, clients: List[Dict[str, Any]]) -> List[ValidationError]:
        """Verificar clientes duplicados"""
        errors = []
        seen_phones = set()
        seen_cpfs = set()
        
        for idx, client in enumerate(clients):
            phone = client.get('phone', '')
            if phone in seen_phones:
                errors.append(ValidationError(f"client[{idx}].phone", "Telefone duplicado", phone))
            seen_phones.add(phone)
            
            cpf = client.get('cpf', '')
            if cpf and cpf in seen_cpfs:
                errors.append(ValidationError(f"client[{idx}].cpf", "CPF duplicado", cpf))
            if cpf:
                seen_cpfs.add(cpf)
        
        return errors

class JSONProcessor:
    """Processador avançado de arquivos JSON"""
    
    def __init__(self):
        self.validator = ClientDataValidator()
    
    def process_file(self, file_path: str) -> ValidationResult:
        """Processar arquivo JSON completo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.validator.validate_client_list(content)
            
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("file", f"Arquivo não encontrado: {file_path}", file_path)],
                warnings=[]
            )
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[ValidationError("file", f"Erro ao ler arquivo: {e}", file_path)],
                warnings=[]
            )
    
    def process_json_string(self, json_string: str) -> ValidationResult:
        """Processar string JSON"""
        return self.validator.validate_client_list(json_string)
