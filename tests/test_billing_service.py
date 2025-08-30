"""
Testes para o serviço de cobrança
"""
import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from backend.services.billing import BillingService, MessageTemplate
from backend.utils.validators import ClientData
from backend.config.settings import TestingConfig

class TestMessageTemplate:
    """Testes para MessageTemplate"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.template = MessageTemplate()
    
    def test_load_default_templates(self):
        """Testa carregamento de templates padrão"""
        assert len(self.template.templates) > 0
        assert "cobranca_simples" in self.template.templates
        assert "cobranca_urgente" in self.template.templates
    
    def test_get_template(self):
        """Testa obtenção de template"""
        template_content = self.template.get_template("cobranca_simples")
        assert template_content is not None
        assert "{name}" in template_content
        assert "{amount}" in template_content
    
    def test_get_nonexistent_template(self):
        """Testa obtenção de template inexistente"""
        template_content = self.template.get_template("inexistente")
        assert template_content is None
    
    def test_add_valid_template(self):
        """Testa adição de template válido"""
        template_name = "test_template"
        template_content = "Olá {name}, valor: {amount}"
        
        result = self.template.add_template(template_name, template_content)
        assert result is True
        assert self.template.get_template(template_name) == template_content
    
    def test_add_invalid_template(self):
        """Testa adição de template inválido"""
        template_name = "invalid_template"
        template_content = "Template sem variáveis obrigatórias"
        
        result = self.template.add_template(template_name, template_content)
        assert result is False
    
    def test_format_message_success(self):
        """Testa formatação de mensagem com sucesso"""
        client = ClientData(
            id="001",
            name="João Silva", 
            phone="5511987654321",
            amount=150.50,
            due_date="2024-01-15",
            description="Teste"
        )
        
        result = self.template.format_message("cobranca_simples", client)
        
        assert result["success"] is True
        assert "João Silva" in result["message"]
        assert "R$ 150,50" in result["message"]
        assert "2024-01-15" in result["message"]
    
    def test_format_message_invalid_template(self):
        """Testa formatação com template inexistente"""
        client = ClientData(
            id="001",
            name="João Silva",
            phone="5511987654321", 
            amount=150.50
        )
        
        result = self.template.format_message("inexistente", client)
        
        assert result["success"] is False
        assert "não encontrado" in result["error"]

class TestBillingService:
    """Testes para BillingService"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.billing_service = BillingService()
    
    @patch('backend.services.billing.WahaClient')
    @patch('backend.services.billing.JSONProcessor')
    def test_initialization(self, mock_json_processor, mock_waha_client):
        """Testa inicialização do serviço"""
        service = BillingService()
        
        assert service.waha_client is not None
        assert service.json_processor is not None
        assert service.message_template is not None
        assert service.current_batch is None
    
    @pytest.mark.asyncio
    async def test_send_single_message_success(self):
        """Testa envio de mensagem única com sucesso"""
        # Mock do WahaClient
        mock_waha_client = AsyncMock()
        mock_waha_client.send_text_message.return_value = {
            "success": True,
            "message_id": "msg_123"
        }
        self.billing_service.waha_client = mock_waha_client
        
        client_data = {
            "id": "001",
            "name": "João Silva",
            "phone": "5511987654321",
            "amount": 150.50
        }
        
        result = await self.billing_service.send_single_message(
            client_data, 
            "cobranca_simples"
        )
        
        assert result["success"] is True
        assert result["message_id"] == "msg_123"
        mock_waha_client.send_text_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_single_message_invalid_client(self):
        """Testa envio com dados de cliente inválidos"""
        client_data = {
            "id": "001",
            # name missing - campo obrigatório
            "phone": "invalid_phone",
            "amount": -10  # valor inválido
        }
        
        result = await self.billing_service.send_single_message(
            client_data,
            "cobranca_simples"
        )
        
        assert result["success"] is False
        assert "erro" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_validate_before_sending_success(self):
        """Testa validação antes de envio com configuração válida"""
        # Mock do JSON processor
        mock_json_processor = Mock()
        mock_json_processor.get_processing_stats.return_value = {
            "file_exists": True,
            "file_size_mb": 0.5,
            "estimated_count": 10
        }
        self.billing_service.json_processor = mock_json_processor
        
        # Mock do Waha client
        mock_waha_client = AsyncMock()
        mock_waha_client.get_session_status.return_value = {
            "success": True,
            "status": "WORKING"
        }
        self.billing_service.waha_client = mock_waha_client
        
        result = await self.billing_service.validate_before_sending(
            "test_file.json",
            "cobranca_simples"
        )
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["waha_status"]["success"] is True
    
    @pytest.mark.asyncio
    async def test_validate_before_sending_missing_file(self):
        """Testa validação com arquivo inexistente"""
        # Mock do JSON processor
        mock_json_processor = Mock()
        mock_json_processor.get_processing_stats.return_value = {
            "file_exists": False,
            "file_size_mb": 0,
            "estimated_count": 0
        }
        self.billing_service.json_processor = mock_json_processor
        
        # Mock do Waha client
        mock_waha_client = AsyncMock()
        mock_waha_client.get_session_status.return_value = {
            "success": True,
            "status": "WORKING"
        }
        self.billing_service.waha_client = mock_waha_client
        
        result = await self.billing_service.validate_before_sending(
            "nonexistent.json",
            "cobranca_simples"
        )
        
        assert result["valid"] is False
        assert "não encontrado" in str(result["issues"])
    
    @pytest.mark.asyncio
    async def test_validate_before_sending_waha_offline(self):
        """Testa validação com Waha offline"""
        # Mock do JSON processor
        mock_json_processor = Mock()
        mock_json_processor.get_processing_stats.return_value = {
            "file_exists": True,
            "file_size_mb": 0.5,
            "estimated_count": 10
        }
        self.billing_service.json_processor = mock_json_processor
        
        # Mock do Waha client
        mock_waha_client = AsyncMock()
        mock_waha_client.get_session_status.return_value = {
            "success": False,
            "error": "Connection failed"
        }
        self.billing_service.waha_client = mock_waha_client
        
        result = await self.billing_service.validate_before_sending(
            "test_file.json",
            "cobranca_simples"
        )
        
        assert result["valid"] is False
        assert "waha não disponível" in str(result["issues"]).lower()
    
    def test_get_available_templates(self):
        """Testa obtenção de templates disponíveis"""
        templates = self.billing_service.get_available_templates()
        
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        for name, info in templates.items():
            assert "content" in info
            assert "length" in info
            assert "variables" in info
            assert "valid" in info
            assert "preview" in info
    
    def test_get_batch_status_no_batch(self):
        """Testa status quando não há lote em execução"""
        status = self.billing_service.get_batch_status()
        assert status is None
    
    def test_get_batch_status_with_batch(self):
        """Testa status com lote em execução"""
        # Simula lote em execução
        self.billing_service.current_batch = {
            "batch_id": "test_batch",
            "total_clients": 100,
            "processed": 50,
            "successful": 45,
            "failed": 5,
            "start_time": datetime.utcnow()
        }
        
        status = self.billing_service.get_batch_status()
        
        assert status is not None
        assert status["batch_id"] == "test_batch"
        assert status["is_running"] is True
        assert status["progress_percentage"] == 50.0
        assert "current_duration" in status
    
    @pytest.mark.asyncio
    async def test_test_message_sending(self):
        """Testa envio de mensagem de teste"""
        # Mock do Waha client
        mock_waha_client = AsyncMock()
        mock_waha_client.send_text_message.return_value = {
            "success": True,
            "message_id": "test_msg_123"
        }
        self.billing_service.waha_client = mock_waha_client
        
        result = await self.billing_service.test_message_sending(
            "5511987654321",
            "cobranca_simples"
        )
        
        assert result["success"] is True
        assert result["message_id"] == "test_msg_123"
        mock_waha_client.send_text_message.assert_called_once()

class TestBillingServiceIntegration:
    """Testes de integração para BillingService"""
    
    @pytest.mark.asyncio
    async def test_send_billing_batch_full_flow(self):
        """Testa fluxo completo de envio de lote"""
        # Este teste seria executado com dados reais em ambiente de teste
        # Por enquanto, mock dos componentes externos
        
        billing_service = BillingService()
        
        # Mock do JSON processor
        mock_clients = [
            ClientData(
                id="001",
                name="João Silva",
                phone="5511987654321", 
                amount=150.50
            ),
            ClientData(
                id="002",
                name="Maria Santos",
                phone="5511976543210",
                amount=225.00
            )
        ]
        
        mock_json_processor = Mock()
        mock_json_processor.load_clients_from_file.return_value = {
            "success": True,
            "clients": mock_clients,
            "total": 2,
            "valid": 2,
            "invalid": 0
        }
        billing_service.json_processor = mock_json_processor
        
        # Mock do Waha client
        mock_waha_client = AsyncMock()
        mock_waha_client.send_text_message.return_value = {
            "success": True,
            "message_id": "msg_123"
        }
        billing_service.waha_client = mock_waha_client
        
        # Executa envio de lote
        result = await billing_service.send_billing_batch(
            clients_file="test_clients.json",
            template_name="cobranca_simples",
            delay_seconds=0  # Sem delay para teste
        )
        
        assert result["success"] is True
        assert result["total_clients"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0
        assert mock_waha_client.send_text_message.call_count == 2

if __name__ == "__main__":
    pytest.main([__file__])

