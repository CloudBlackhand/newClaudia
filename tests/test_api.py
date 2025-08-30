"""
Testes para as APIs
"""
import pytest
import json
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health_endpoint():
    """Teste do endpoint de saúde"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "modules" in data

def test_root_endpoint():
    """Teste do endpoint raiz"""
    response = client.get("/")
    
    assert response.status_code == 200

def test_validate_json_endpoint():
    """Teste do endpoint de validação de JSON"""
    valid_json = '[{"nome": "João", "telefone": "+5511999999999", "valor": "100.00"}]'
    
    response = client.get(
        "/api/billing/validate-json",
        params={"json_data": valid_json}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True

def test_validate_template_endpoint():
    """Teste do endpoint de validação de template"""
    template = "Olá {nome}, você deve R$ {valor}"
    
    response = client.get(
        "/api/billing/validate-template",
        params={"template": template}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True

def test_billing_stats_endpoint():
    """Teste do endpoint de estatísticas de cobrança"""
    response = client.get("/api/billing/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "is_healthy" in data

def test_conversation_stats_endpoint():
    """Teste do endpoint de estatísticas do bot"""
    response = client.get("/api/conversation/bot-stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data

def test_waha_status_endpoint():
    """Teste do endpoint de status do Waha"""
    response = client.get("/api/webhooks/waha/status")
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data

def test_process_json_endpoint():
    """Teste do endpoint de processamento de JSON"""
    json_data = '[{"nome": "João", "telefone": "+5511999999999", "valor": "100.00"}]'
    
    response = client.post(
        "/api/billing/process-json",
        data={
            "json_data": json_data,
            "template": "Olá {nome}, você deve R$ {valor}"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

def test_send_message_endpoint():
    """Teste do endpoint de envio de mensagem"""
    response = client.post(
        "/api/webhooks/send-message",
        params={
            "to_number": "+5511999999999",
            "message": "Teste de mensagem"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "success" in data

def test_webhook_endpoint():
    """Teste do endpoint de webhook"""
    webhook_data = {
        "event": "message.text",
        "payload": {
            "from": "+5511999999999",
            "body": "Olá",
            "fromMe": False,
            "type": "text"
        }
    }
    
    response = client.post(
        "/api/webhooks/waha",
        json=webhook_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
