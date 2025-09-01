#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para as APIs REST
"""

import pytest
import json
from unittest.mock import Mock, patch

from backend.app import create_app

class TestBillingAPI:
    """Testes para a API de cobrança"""
    
    @pytest.fixture
    def client(self):
        """Fixture para client de teste"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def valid_client_data(self):
        """Fixture com dados válidos de cliente"""
        return {
            "clients": [
                {
                    "name": "João Silva",
                    "phone": "11999999999",
                    "amount": 150.50,
                    "due_date": "2024-12-31",
                    "email": "joao@email.com"
                },
                {
                    "name": "Maria Santos",
                    "phone": "11888888888",
                    "amount": 200.00,
                    "due_date": "2024-12-25"
                }
            ]
        }
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_billing_health_check(self, client):
        """Testa health check da API de cobrança"""
        response = client.get('/api/billing/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['module'] == 'billing'
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_validate_clients_valid_data(self, client, valid_client_data):
        """Testa validação com dados válidos"""
        response = client.post('/api/billing/validate-clients',
                             json=valid_client_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['valid'] == True
        assert data['client_count'] == 2
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_validate_clients_invalid_data(self, client):
        """Testa validação com dados inválidos"""
        invalid_data = {
            "clients": [
                {
                    "name": "",  # Nome vazio
                    "phone": "invalid_phone",
                    "amount": -100,  # Valor negativo
                    "due_date": "invalid_date"
                }
            ]
        }
        
        response = client.post('/api/billing/validate-clients',
                             json=invalid_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['valid'] == False
        assert len(data['errors']) > 0
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_validate_clients_missing_content_type(self, client):
        """Testa validação sem Content-Type correto"""
        response = client.post('/api/billing/validate-clients',
                             data='{"test": "data"}')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Content-Type' in data['error']
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_validate_clients_missing_clients_field(self, client):
        """Testa validação sem campo clients"""
        invalid_data = {"data": []}
        
        response = client.post('/api/billing/validate-clients',
                             json=invalid_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'clients' in data['error']
    
    @pytest.mark.api
    @pytest.mark.billing
    @patch('backend.api.routes.billing_routes.asyncio')
    def test_send_batch_valid_data(self, mock_asyncio, client, valid_client_data):
        """Testa envio de lote com dados válidos"""
        # Mock do resultado do dispatcher
        mock_result = Mock()
        mock_result.total_messages = 2
        mock_result.successful = 2
        mock_result.failed = 0
        mock_result.skipped = 0
        mock_result.execution_time = 1.5
        mock_result.errors = []
        
        mock_loop = Mock()
        mock_loop.run_until_complete.return_value = mock_result
        mock_asyncio.new_event_loop.return_value = mock_loop
        mock_asyncio.set_event_loop = Mock()
        
        response = client.post('/api/billing/send-batch',
                             json=valid_client_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['result']['total_messages'] == 2
        assert data['result']['successful'] == 2
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_send_batch_with_template(self, client, valid_client_data):
        """Testa envio com template específico"""
        valid_client_data['template_id'] = 'reminder_br'
        
        with patch('backend.api.routes.billing_routes.asyncio') as mock_asyncio:
            mock_result = Mock()
            mock_result.total_messages = 2
            mock_result.successful = 1
            mock_result.failed = 1
            mock_result.skipped = 0
            mock_result.execution_time = 2.0
            mock_result.errors = ['Erro de teste']
            
            mock_loop = Mock()
            mock_loop.run_until_complete.return_value = mock_result
            mock_asyncio.new_event_loop.return_value = mock_loop
            
            response = client.post('/api/billing/send-batch',
                                 json=valid_client_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['result']['failed'] == 1
            assert len(data['result']['errors']) == 1
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_get_templates(self, client):
        """Testa obtenção de templates"""
        response = client.get('/api/billing/templates')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'templates' in data
        assert 'count' in data
        assert data['count'] > 0
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_get_statistics(self, client):
        """Testa obtenção de estatísticas"""
        response = client.get('/api/billing/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'billing_stats' in data
        assert 'logger_stats' in data
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_test_template(self, client):
        """Testa renderização de template"""
        test_data = {
            "template_id": "initial_br",
            "variables": {
                "client_name": "João Silva",
                "amount": "150.50",
                "due_date": "31/12/2024"
            }
        }
        
        response = client.post('/api/billing/test-template',
                             json=test_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rendered' in data
        assert 'João Silva' in data['rendered']
        assert '150.50' in data['rendered']
    
    @pytest.mark.api
    @pytest.mark.billing
    def test_test_template_not_found(self, client):
        """Testa template inexistente"""
        test_data = {
            "template_id": "template_inexistente",
            "variables": {}
        }
        
        response = client.post('/api/billing/test-template',
                             json=test_data,
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'não encontrado' in data['error']

class TestConversationAPI:
    """Testes para a API de conversação"""
    
    @pytest.fixture
    def client(self):
        """Fixture para client de teste"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_conversation_health_check(self, client):
        """Testa health check da API de conversação"""
        response = client.get('/api/conversation/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['module'] == 'conversation'
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_process_message_valid(self, client):
        """Testa processamento de mensagem válida"""
        message_data = {
            "phone": "+5511999999999",
            "message": "Olá, recebi uma cobrança",
            "user_name": "João Silva",
            "auto_reply": False
        }
        
        response = client.post('/api/conversation/process-message',
                             json=message_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'response' in data
        assert 'text' in data['response']
        assert len(data['response']['text']) > 0
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_process_message_missing_fields(self, client):
        """Testa processamento sem campos obrigatórios"""
        incomplete_data = {
            "phone": "+5511999999999"
            # Faltando message
        }
        
        response = client.post('/api/conversation/process-message',
                             json=incomplete_data,
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'obrigatórios ausentes' in data['error']
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_analyze_message(self, client):
        """Testa análise de mensagem"""
        analysis_data = {
            "message": "Posso parcelar em 3 vezes?"
        }
        
        response = client.post('/api/conversation/analyze-message',
                             json=analysis_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'analysis' in data
        assert 'intent' in data['analysis']
        assert 'sentiment' in data['analysis']
        assert 'confidence' in data['analysis']
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_get_contexts(self, client):
        """Testa obtenção de contextos"""
        # Primeiro criar alguns contextos processando mensagens
        test_messages = [
            {"phone": "+5511999999999", "message": "Oi", "auto_reply": False},
            {"phone": "+5511888888888", "message": "Olá", "auto_reply": False}
        ]
        
        for msg in test_messages:
            client.post('/api/conversation/process-message',
                       json=msg,
                       content_type='application/json')
        
        response = client.get('/api/conversation/contexts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'contexts' in data
        assert len(data['contexts']) >= 2
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_get_context_details(self, client):
        """Testa obtenção de detalhes de contexto"""
        phone = "+5511999999999"
        
        # Criar contexto
        client.post('/api/conversation/process-message',
                   json={"phone": phone, "message": "Teste", "auto_reply": False},
                   content_type='application/json')
        
        response = client.get(f'/api/conversation/contexts/{phone}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'context' in data
        assert data['context']['phone'] == phone
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_get_context_not_found(self, client):
        """Testa contexto não encontrado"""
        response = client.get('/api/conversation/contexts/+5511000000000')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'não encontrado' in data['error']
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_delete_context(self, client):
        """Testa exclusão de contexto"""
        phone = "+5511999999999"
        
        # Criar contexto
        client.post('/api/conversation/process-message',
                   json={"phone": phone, "message": "Teste", "auto_reply": False},
                   content_type='application/json')
        
        # Excluir contexto
        response = client.delete(f'/api/conversation/contexts/{phone}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        
        # Verificar que foi excluído
        get_response = client.get(f'/api/conversation/contexts/{phone}')
        assert get_response.status_code == 404
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_get_statistics(self, client):
        """Testa obtenção de estatísticas de conversação"""
        response = client.get('/api/conversation/statistics')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'conversation_stats' in data
        assert 'logger_stats' in data
    
    @pytest.mark.api
    @pytest.mark.conversation
    def test_test_nlp(self, client):
        """Testa funcionalidades de NLP"""
        test_data = {
            "messages": [
                "Olá, tudo bem?",
                "Quanto devo pagar?",
                "Posso parcelar?",
                "Já paguei ontem"
            ]
        }
        
        response = client.post('/api/conversation/test-nlp',
                             json=test_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'results' in data
        assert len(data['results']) == 4
        
        for result in data['results']:
            assert 'intent' in result
            assert 'sentiment' in result
            assert 'confidence' in result

class TestWebhookAPI:
    """Testes para a API de webhooks"""
    
    @pytest.fixture
    def client(self):
        """Fixture para client de teste"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.mark.api
    def test_webhook_health_check(self, client):
        """Testa health check da API de webhooks"""
        response = client.get('/api/webhook/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['module'] == 'webhook'
    
    @pytest.mark.api
    def test_webhook_test_endpoint(self, client):
        """Testa endpoint de teste de webhook"""
        test_data = {
            "test": "data",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        response = client.post('/api/webhook/test',
                             json=test_data,
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'test_successful'
        assert data['received_data'] == test_data
    
    @pytest.mark.api
    def test_webhook_test_invalid_content_type(self, client):
        """Testa webhook de teste com Content-Type inválido"""
        response = client.post('/api/webhook/test',
                             data='test data')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Content-Type' in data['error']
    
    @pytest.mark.api
    @patch('backend.api.routes.webhook_routes.verify_webhook_signature')
    def test_whatsapp_webhook_message(self, mock_verify, client):
        """Testa webhook de mensagem do WhatsApp"""
        mock_verify.return_value = True
        
        webhook_data = {
            "event": "message",
            "session": "default",
            "payload": {
                "id": "msg_123",
                "timestamp": 1640995200,
                "fromMe": False,
                "from": "5511999999999@c.us",
                "chatId": "5511999999999@c.us",
                "type": "text",
                "body": "Olá, recebi uma cobrança"
            }
        }
        
        with patch('backend.api.routes.webhook_routes.asyncio') as mock_asyncio:
            mock_loop = Mock()
            mock_loop.run_until_complete.return_value = True
            mock_asyncio.new_event_loop.return_value = mock_loop
            
            response = client.post('/api/webhook/whatsapp',
                                 json=webhook_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'processed'
    
    @pytest.mark.api
    def test_whatsapp_webhook_session_status(self, client):
        """Testa webhook de status de sessão"""
        webhook_data = {
            "event": "session.status",
            "session": "default",
            "payload": {
                "name": "default",
                "status": "WORKING"
            }
        }
        
        with patch('backend.api.routes.webhook_routes.verify_webhook_signature', return_value=True):
            response = client.post('/api/webhook/whatsapp',
                                 json=webhook_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'processed'
            assert data['new_status'] == 'WORKING'
    
    @pytest.mark.api
    def test_whatsapp_webhook_unknown_event(self, client):
        """Testa webhook com evento desconhecido"""
        webhook_data = {
            "event": "unknown_event",
            "session": "default",
            "payload": {}
        }
        
        with patch('backend.api.routes.webhook_routes.verify_webhook_signature', return_value=True):
            response = client.post('/api/webhook/whatsapp',
                                 json=webhook_data,
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'ignored'

class TestMainApp:
    """Testes para a aplicação principal"""
    
    @pytest.fixture
    def client(self):
        """Fixture para client de teste"""
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.mark.api
    def test_health_check_endpoint(self, client):
        """Testa endpoint principal de health check"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'Sistema de Cobrança Inteligente'
    
    @pytest.mark.api
    def test_index_page(self, client):
        """Testa página inicial"""
        response = client.get('/')
        
        assert response.status_code == 200
        assert 'Sistema de Cobrança Inteligente'.encode('utf-8') in response.data
    
    @pytest.mark.api
    def test_404_error_handler(self, client):
        """Testa handler de erro 404"""
        response = client.get('/endpoint/inexistente')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 404
        assert 'não encontrado' in data['error']
    
    @pytest.mark.api
    def test_cors_headers(self, client):
        """Testa cabeçalhos CORS"""
        response = client.options('/api/billing/health')
        
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
