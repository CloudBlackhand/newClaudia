#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para o Engine de Validação
"""

import pytest
import json
from datetime import datetime

from backend.modules.validation_engine import (
    ClientDataValidator, 
    JSONProcessor, 
    ValidationLevel,
    ValidationError,
    ValidationResult
)

class TestClientDataValidator:
    """Testes para o validador de dados de clientes"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.validator = ClientDataValidator(ValidationLevel.STRICT)
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_client_valid_data(self):
        """Testa validação de cliente com dados válidos"""
        client_data = {
            'name': 'João Silva',
            'phone': '+5511999999999',
            'amount': 150.50,
            'due_date': '2024-12-31',
            'email': 'joao@email.com'
        }
        
        result = self.validator.validate_client(client_data, 0)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.sanitized_data is not None
        assert result.sanitized_data['name'] == 'João Silva'
        assert result.sanitized_data['phone'] == '+5511999999999'
        assert result.sanitized_data['amount'] == 150.50
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_client_missing_required_fields(self):
        """Testa validação com campos obrigatórios ausentes"""
        client_data = {
            'name': 'João Silva'
            # Faltando phone, amount, due_date
        }
        
        result = self.validator.validate_client(client_data, 0)
        
        assert not result.is_valid
        assert len(result.errors) == 3  # phone, amount, due_date
        assert result.sanitized_data is None
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_phone_normalization(self):
        """Testa normalização de telefones"""
        test_cases = [
            ('11999999999', '+5511999999999'),
            ('5511999999999', '+5511999999999'),
            ('+5511999999999', '+5511999999999'),
            ('(11) 99999-9999', '+5511999999999'),
        ]
        
        for input_phone, expected in test_cases:
            errors, warnings, sanitized = self.validator._validate_phone(input_phone, 0)
            assert len(errors) == 0
            assert sanitized == expected
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_phone_invalid(self):
        """Testa validação de telefones inválidos"""
        invalid_phones = [
            '123',
            '11888888888',  # Número fixo
            'abc123',
            ''
        ]
        
        for phone in invalid_phones:
            errors, warnings, sanitized = self.validator._validate_phone(phone, 0)
            assert len(errors) > 0
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_amount_formats(self):
        """Testa validação de diferentes formatos de valor"""
        test_cases = [
            (150.50, 150.50),
            ('150.50', 150.50),
            ('150,50', 150.50),
            ('R$ 150,50', 150.50),
            (100, 100.0)
        ]
        
        for input_amount, expected in test_cases:
            errors, warnings, sanitized = self.validator._validate_amount(input_amount, 0)
            assert len(errors) == 0
            assert sanitized == expected
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_amount_invalid(self):
        """Testa valores inválidos"""
        invalid_amounts = [
            -100,
            0,
            'abc',
            '',
            None
        ]
        
        for amount in invalid_amounts:
            errors, warnings, sanitized = self.validator._validate_amount(amount, 0)
            assert len(errors) > 0
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_date_formats(self):
        """Testa validação de diferentes formatos de data"""
        test_cases = [
            ('2024-12-31', '2024-12-31'),
            ('31/12/2024', '2024-12-31'),
            ('31-12-2024', '2024-12-31')
        ]
        
        for input_date, expected in test_cases:
            errors, warnings, sanitized = self.validator._validate_due_date(input_date, 0)
            assert len(errors) == 0
            assert sanitized == expected
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_email_valid(self):
        """Testa validação de emails válidos"""
        valid_emails = [
            'joao@email.com',
            'teste.email@empresa.com.br',
            'user123@domain.co'
        ]
        
        for email in valid_emails:
            errors, warnings, sanitized = self.validator._validate_email(email, 0)
            assert len(errors) == 0
            assert sanitized == email.lower()
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_email_invalid(self):
        """Testa validação de emails inválidos"""
        invalid_emails = [
            'email_invalido',
            '@domain.com',
            'email@',
            'email.domain.com'
        ]
        
        for email in invalid_emails:
            errors, warnings, sanitized = self.validator._validate_email(email, 0)
            assert len(errors) > 0
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_validate_cpf_format(self):
        """Testa validação de formato de CPF"""
        test_cases = [
            ('12345678901', '123.456.789-01'),
            ('123.456.789-01', '123.456.789-01')
        ]
        
        for input_cpf, expected in test_cases:
            errors, warnings, sanitized = self.validator._validate_cpf(input_cpf, 0)
            assert sanitized == expected
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_check_duplicates(self):
        """Testa detecção de duplicatas"""
        clients = [
            {'phone': '+5511999999999', 'name': 'Cliente 1'},
            {'phone': '+5511999999999', 'name': 'Cliente 2'},  # Duplicate phone
            {'phone': '+5511888888888', 'cpf': '123.456.789-01', 'name': 'Cliente 3'},
            {'phone': '+5511777777777', 'cpf': '123.456.789-01', 'name': 'Cliente 4'}  # Duplicate CPF
        ]
        
        errors = self.validator._check_duplicates(clients)
        
        # Deve detectar telefone e CPF duplicados
        assert len(errors) == 2
        assert any('telefone duplicado' in error.message.lower() for error in errors)
        assert any('cpf duplicado' in error.message.lower() for error in errors)

class TestJSONProcessor:
    """Testes para o processador de JSON"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.processor = JSONProcessor()
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_process_valid_json(self):
        """Testa processamento de JSON válido"""
        valid_json = {
            "clients": [
                {
                    "name": "João Silva",
                    "phone": "11999999999",
                    "amount": 150.50,
                    "due_date": "2024-12-31"
                },
                {
                    "name": "Maria Santos",
                    "phone": "11888888888",
                    "amount": 200.00,
                    "due_date": "2024-12-25"
                }
            ]
        }
        
        json_string = json.dumps(valid_json)
        result = self.processor.process_json_string(json_string)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.sanitized_data is not None
        assert len(result.sanitized_data['clients']) == 2
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_process_invalid_json(self):
        """Testa processamento de JSON inválido"""
        invalid_json = '{"clients": [invalid json}'
        
        result = self.processor.process_json_string(invalid_json)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert 'JSON inválido' in result.errors[0].message
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_process_missing_clients_field(self):
        """Testa JSON sem campo clients"""
        json_without_clients = '{"data": []}'
        
        result = self.processor.process_json_string(json_without_clients)
        
        assert not result.is_valid
        assert any('clients' in error.message for error in result.errors)
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_process_empty_clients(self):
        """Testa JSON com lista de clientes vazia"""
        empty_clients_json = '{"clients": []}'
        
        result = self.processor.process_json_string(empty_clients_json)
        
        assert not result.is_valid
        assert any('vazia' in error.message for error in result.errors)
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_process_mixed_valid_invalid_clients(self):
        """Testa JSON com mix de clientes válidos e inválidos"""
        mixed_json = {
            "clients": [
                {
                    "name": "Cliente Válido",
                    "phone": "11999999999",
                    "amount": 150.50,
                    "due_date": "2024-12-31"
                },
                {
                    "name": "",  # Nome vazio - inválido
                    "phone": "11888888888",
                    "amount": 200.00,
                    "due_date": "2024-12-25"
                },
                {
                    "name": "Outro Cliente Válido",
                    "phone": "11777777777",
                    "amount": 300.00,
                    "due_date": "2024-12-20"
                }
            ]
        }
        
        json_string = json.dumps(mixed_json)
        result = self.processor.process_json_string(json_string)
        
        assert not result.is_valid  # Falha por ter cliente inválido
        assert len(result.errors) > 0

class TestValidationEdgeCases:
    """Testes para casos extremos de validação"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.validator = ClientDataValidator(ValidationLevel.PARANOID)
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_very_long_name(self):
        """Testa nome muito longo"""
        long_name = "A" * 150
        
        errors, warnings, sanitized = self.validator._validate_name(long_name, 0)
        
        assert len(warnings) > 0  # Deve gerar warning
        assert len(sanitized) <= 100  # Deve ser truncado
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_suspicious_characters_in_name(self):
        """Testa caracteres suspeitos no nome"""
        suspicious_name = "João <script>alert('hack')</script>"
        
        errors, warnings, sanitized = self.validator._validate_name(suspicious_name, 0)
        
        assert len(warnings) > 0  # Deve gerar warning sobre caracteres suspeitos
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_very_high_amount(self):
        """Testa valor muito alto"""
        high_amount = 2000000.00
        
        errors, warnings, sanitized = self.validator._validate_amount(high_amount, 0)
        
        assert len(warnings) > 0  # Deve gerar warning sobre valor alto
        assert sanitized == high_amount
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_past_due_date(self):
        """Testa data de vencimento no passado"""
        past_date = "2020-01-01"
        
        errors, warnings, sanitized = self.validator._validate_due_date(past_date, 0)
        
        assert len(warnings) > 0  # Deve gerar warning sobre data no passado
    
    @pytest.mark.unit
    @pytest.mark.validation
    def test_cpf_all_same_digits(self):
        """Testa CPF com todos os dígitos iguais"""
        invalid_cpf = "11111111111"
        
        errors, warnings, sanitized = self.validator._validate_cpf(invalid_cpf, 0)
        
        assert len(errors) > 0  # Deve rejeitar CPF inválido

@pytest.mark.integration
@pytest.mark.validation
class TestValidationIntegration:
    """Testes de integração para validação"""
    
    def test_complete_validation_workflow(self):
        """Testa fluxo completo de validação"""
        processor = JSONProcessor()
        
        # JSON de teste completo
        test_json = {
            "clients": [
                {
                    "name": "João Silva",
                    "phone": "(11) 99999-9999",
                    "amount": "R$ 150,50",
                    "due_date": "31/12/2024",
                    "email": "JOAO@EMAIL.COM",
                    "cpf": "123.456.789-01"
                },
                {
                    "name": "maria santos",
                    "phone": "11888888888",
                    "amount": 200,
                    "due_date": "2024-12-25"
                }
            ]
        }
        
        json_string = json.dumps(test_json)
        result = processor.process_json_string(json_string)
        
        assert result.is_valid
        assert len(result.sanitized_data['clients']) == 2
        
        # Verificar normalização
        client1 = result.sanitized_data['clients'][0]
        assert client1['name'] == 'João Silva'  # Capitalizado
        assert client1['phone'] == '+5511999999999'  # Normalizado
        assert client1['amount'] == 150.50  # Convertido
        assert client1['due_date'] == '2024-12-31'  # Formato padrão
        assert client1['email'] == 'joao@email.com'  # Minúsculo
        
        client2 = result.sanitized_data['clients'][1]
        assert client2['name'] == 'Maria Santos'  # Capitalizado
        assert client2['phone'] == '+5511888888888'  # Normalizado

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
