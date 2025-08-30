"""
Testes para o módulo de validação
"""
import pytest
import asyncio
from backend.modules.validation_engine import ValidationEngine

@pytest.fixture
def validation_engine():
    return ValidationEngine()

@pytest.mark.asyncio
async def test_validate_json_structure_valid(validation_engine):
    """Teste de validação de JSON válido"""
    json_data = '[{"nome": "João", "telefone": "+5511999999999", "valor": "100.00"}]'
    
    result = await validation_engine.validate_json_structure(json_data)
    
    assert result["is_valid"] == True
    assert result["records_count"] == 1

@pytest.mark.asyncio
async def test_validate_json_structure_invalid(validation_engine):
    """Teste de validação de JSON inválido"""
    json_data = '{"nome": "João", invalid}'
    
    result = await validation_engine.validate_json_structure(json_data)
    
    assert result["is_valid"] == False
    assert "error" in result

@pytest.mark.asyncio
async def test_validate_billing_data_valid(validation_engine):
    """Teste de validação de dados de cobrança válidos"""
    data = [
        {
            "nome": "João Silva",
            "telefone": "+5511999999999",
            "valor": "150.00"
        }
    ]
    
    result = await validation_engine.validate_billing_data(data)
    
    assert result.is_valid == True
    assert result.valid_records == 1
    assert len(result.valid_data) == 1

@pytest.mark.asyncio
async def test_validate_billing_data_missing_fields(validation_engine):
    """Teste de validação com campos obrigatórios ausentes"""
    data = [
        {
            "nome": "João Silva"
            # Telefone e valor ausentes
        }
    ]
    
    result = await validation_engine.validate_billing_data(data)
    
    assert result.is_valid == False
    assert result.valid_records == 0
    assert len(result.errors) > 0

@pytest.mark.asyncio
async def test_validate_template_valid(validation_engine):
    """Teste de validação de template válido"""
    template = "Olá {nome}, você deve R$ {valor}"
    
    result = await validation_engine.validate_template(template)
    
    assert result["is_valid"] == True
    assert "{nome}" in result["placeholders_found"]
    assert "{valor}" in result["placeholders_found"]

@pytest.mark.asyncio
async def test_validate_template_invalid_placeholder(validation_engine):
    """Teste de validação de template com placeholder inválido"""
    template = "Olá {nome_invalido}, você deve R$ {valor}"
    
    result = await validation_engine.validate_template(template)
    
    assert result["is_valid"] == False
    assert "invalid_placeholders" in result["error"] or "Placeholders inválidos" in result["error"]

def test_phone_validation(validation_engine):
    """Teste de validação de telefone"""
    # Telefones válidos
    valid_phones = [
        "+5511999999999",
        "11999999999",
        "+55 11 99999-9999",
        "5511999999999"
    ]
    
    for phone in valid_phones:
        error = validation_engine._validate_phone(phone)
        assert error is None, f"Telefone {phone} deveria ser válido"
    
    # Telefones inválidos
    invalid_phones = [
        "",
        "123",
        "abc",
        "99999"
    ]
    
    for phone in invalid_phones:
        error = validation_engine._validate_phone(phone)
        assert error is not None, f"Telefone {phone} deveria ser inválido"

def test_value_validation(validation_engine):
    """Teste de validação de valores"""
    # Valores válidos
    valid_values = [
        "100.00",
        "1500,50",
        "R$ 200,00",
        150.75,
        100
    ]
    
    for value in valid_values:
        error = validation_engine._validate_value(value)
        assert error is None, f"Valor {value} deveria ser válido"
    
    # Valores inválidos
    invalid_values = [
        "",
        "abc",
        -100,
        0,
        None
    ]
    
    for value in invalid_values:
        error = validation_engine._validate_value(value)
        assert error is not None, f"Valor {value} deveria ser inválido"
