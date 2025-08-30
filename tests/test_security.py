"""
Testes para o módulo de segurança
"""
import pytest
import time
import jwt
from unittest.mock import Mock, patch
from backend.utils.security import (
    SecurityManager, RateLimiter, InputValidator, 
    WebhookSecurity, security_manager
)
from backend.config.settings import TestingConfig

class TestSecurityManager:
    """Testes para SecurityManager"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        with patch('backend.utils.security.active_config', TestingConfig):
            self.security_manager = SecurityManager()
    
    def test_initialization(self):
        """Testa inicialização do SecurityManager"""
        assert self.security_manager.rate_limiter is not None
        assert hasattr(self.security_manager, 'config')
    
    def test_generate_secure_token(self):
        """Testa geração de token seguro"""
        token1 = self.security_manager.generate_secure_token()
        token2 = self.security_manager.generate_secure_token()
        
        # Tokens devem ser diferentes
        assert token1 != token2
        # Comprimento padrão
        assert len(token1) > 30
    
    def test_hash_password(self):
        """Testa hash de senha"""
        password = "test_password_123"
        
        result = self.security_manager.hash_password(password)
        
        assert "hash" in result
        assert "salt" in result
        assert len(result["hash"]) > 0
        assert len(result["salt"]) > 0
        
        # Hash deve ser diferente a cada chamada (devido ao salt)
        result2 = self.security_manager.hash_password(password)
        assert result["hash"] != result2["hash"]
    
    def test_verify_password_correct(self):
        """Testa verificação de senha correta"""
        password = "test_password_123"
        hash_result = self.security_manager.hash_password(password)
        
        is_valid = self.security_manager.verify_password(
            password, hash_result["hash"], hash_result["salt"]
        )
        
        assert is_valid is True
    
    def test_verify_password_incorrect(self):
        """Testa verificação de senha incorreta"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hash_result = self.security_manager.hash_password(password)
        
        is_valid = self.security_manager.verify_password(
            wrong_password, hash_result["hash"], hash_result["salt"]
        )
        
        assert is_valid is False
    
    def test_create_jwt_token(self):
        """Testa criação de token JWT"""
        payload = {"user_id": "123", "username": "test_user"}
        
        token = self.security_manager.create_jwt_token(payload)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Deve conter 3 partes separadas por ponto
        parts = token.split('.')
        assert len(parts) == 3
    
    def test_verify_jwt_token_valid(self):
        """Testa verificação de token JWT válido"""
        payload = {"user_id": "123", "username": "test_user"}
        
        token = self.security_manager.create_jwt_token(payload)
        decoded = self.security_manager.verify_jwt_token(token)
        
        assert decoded is not None
        assert decoded["user_id"] == "123"
        assert decoded["username"] == "test_user"
        assert "exp" in decoded
        assert "iat" in decoded
        assert "jti" in decoded
    
    def test_verify_jwt_token_invalid(self):
        """Testa verificação de token JWT inválido"""
        invalid_token = "invalid.token.here"
        
        decoded = self.security_manager.verify_jwt_token(invalid_token)
        
        assert decoded is None
    
    def test_verify_jwt_token_expired(self):
        """Testa verificação de token JWT expirado"""
        payload = {"user_id": "123", "username": "test_user"}
        
        # Cria token que expira imediatamente
        token = self.security_manager.create_jwt_token(payload, expires_in=-1)
        
        # Aguarda um pouco para garantir expiração
        time.sleep(0.1)
        
        decoded = self.security_manager.verify_jwt_token(token)
        
        assert decoded is None
    
    def test_create_webhook_signature(self):
        """Testa criação de assinatura de webhook"""
        payload = '{"event": "test", "data": "example"}'
        secret = "webhook_secret_key"
        
        signature = self.security_manager.create_webhook_signature(payload, secret)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex digest
    
    def test_verify_webhook_signature_valid(self):
        """Testa verificação de assinatura válida"""
        payload = '{"event": "test", "data": "example"}'
        secret = "webhook_secret_key"
        
        signature = self.security_manager.create_webhook_signature(payload, secret)
        is_valid = self.security_manager.verify_webhook_signature(payload, signature, secret)
        
        assert is_valid is True
    
    def test_verify_webhook_signature_invalid(self):
        """Testa verificação de assinatura inválida"""
        payload = '{"event": "test", "data": "example"}'
        secret = "webhook_secret_key"
        wrong_signature = "invalid_signature"
        
        is_valid = self.security_manager.verify_webhook_signature(payload, wrong_signature, secret)
        
        assert is_valid is False

class TestRateLimiter:
    """Testes para RateLimiter"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        # Configura rate limiter com limites baixos para teste
        self.rate_limiter = RateLimiter()
        self.rate_limiter.max_requests = 5
        self.rate_limiter.time_window = 60
    
    def test_first_request_allowed(self):
        """Testa que primeira requisição é permitida"""
        result = self.rate_limiter.is_allowed("test_user")
        
        assert result["allowed"] is True
        assert result["remaining"] == 4
        assert result["limit"] == 5
    
    def test_multiple_requests_within_limit(self):
        """Testa múltiplas requisições dentro do limite"""
        user_id = "test_user"
        
        for i in range(5):
            result = self.rate_limiter.is_allowed(user_id)
            assert result["allowed"] is True
            assert result["remaining"] == 4 - i
    
    def test_requests_exceed_limit(self):
        """Testa quando requisições excedem o limite"""
        user_id = "test_user"
        
        # Faz 5 requisições (limite)
        for i in range(5):
            result = self.rate_limiter.is_allowed(user_id)
            assert result["allowed"] is True
        
        # Sexta requisição deve ser bloqueada
        result = self.rate_limiter.is_allowed(user_id)
        assert result["allowed"] is False
        assert result["remaining"] == 0
    
    def test_different_users_independent(self):
        """Testa que usuários diferentes têm contadores independentes"""
        # Esgota limite para user1
        for i in range(5):
            self.rate_limiter.is_allowed("user1")
        
        result_user1 = self.rate_limiter.is_allowed("user1")
        assert result_user1["allowed"] is False
        
        # user2 ainda deve poder fazer requisições
        result_user2 = self.rate_limiter.is_allowed("user2")
        assert result_user2["allowed"] is True
    
    def test_cleanup_old_entries(self):
        """Testa limpeza de entradas antigas"""
        user_id = "test_user"
        
        # Simula requisições antigas
        old_time = time.time() - 120  # 2 minutos atrás
        self.rate_limiter.requests[user_id] = [(old_time, 5)]
        
        # Nova requisição deve ser permitida (entradas antigas limpas)
        result = self.rate_limiter.is_allowed(user_id)
        assert result["allowed"] is True
        assert result["remaining"] == 4

class TestInputValidator:
    """Testes para InputValidator"""
    
    def test_sanitize_string_input(self):
        """Testa sanitização de string"""
        dangerous_input = "Normal text\x00\x01\x02"
        
        sanitized = InputValidator.sanitize_input(dangerous_input)
        
        assert "\x00" not in sanitized
        assert "\x01" not in sanitized
        assert "\x02" not in sanitized
        assert "Normal text" in sanitized
    
    def test_sanitize_dict_input(self):
        """Testa sanitização de dicionário"""
        input_dict = {
            "safe_key": "safe_value",
            "dangerous_key": "value\x00with\x01control\x02chars"
        }
        
        sanitized = InputValidator.sanitize_input(input_dict)
        
        assert sanitized["safe_key"] == "safe_value"
        assert "\x00" not in sanitized["dangerous_key"]
        assert "valuewithcontrolchars" == sanitized["dangerous_key"]
    
    def test_sanitize_list_input(self):
        """Testa sanitização de lista"""
        input_list = ["safe_item", "dangerous\x00item", {"nested": "value\x01"}]
        
        sanitized = InputValidator.sanitize_input(input_list)
        
        assert sanitized[0] == "safe_item"
        assert "\x00" not in sanitized[1]
        assert "\x01" not in sanitized[2]["nested"]
    
    def test_validate_phone_number_valid(self):
        """Testa validação de telefone válido"""
        valid_phones = [
            "5511987654321",
            "551198765432",
            "+5511987654321",
            "(11) 98765-4321"
        ]
        
        for phone in valid_phones:
            assert InputValidator.validate_phone_number(phone) is True
    
    def test_validate_phone_number_invalid(self):
        """Testa validação de telefone inválido"""
        invalid_phones = [
            "11987654321",    # Sem código do país
            "123456789",      # Muito curto
            "abcdefghijk",    # Não numérico
            "1234567890123456"  # Muito longo
        ]
        
        for phone in invalid_phones:
            assert InputValidator.validate_phone_number(phone) is False
    
    def test_validate_email_valid(self):
        """Testa validação de email válido"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk"
        ]
        
        for email in valid_emails:
            assert InputValidator.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Testa validação de email inválido"""
        invalid_emails = [
            "invalid_email",
            "@example.com",
            "user@",
            "user@domain",
            "user name@example.com"
        ]
        
        for email in invalid_emails:
            assert InputValidator.validate_email(email) is False
    
    def test_check_sql_injection_attack(self):
        """Testa detecção de SQL injection"""
        sql_attacks = [
            "'; DROP TABLE users; --",
            "1' UNION SELECT * FROM passwords",
            "admin'--",
            "1; UPDATE users SET admin=1",
            "/* comment */ SELECT * FROM"
        ]
        
        for attack in sql_attacks:
            assert InputValidator.check_sql_injection(attack) is True
    
    def test_check_sql_injection_safe(self):
        """Testa texto seguro para SQL injection"""
        safe_texts = [
            "Normal user input",
            "Email: user@domain.com",
            "Price: $19.99",
            "Date: 2024-01-15"
        ]
        
        for text in safe_texts:
            assert InputValidator.check_sql_injection(text) is False
    
    def test_check_xss_attempt_attack(self):
        """Testa detecção de XSS"""
        xss_attacks = [
            "<script>alert('xss')</script>",
            "javascript:alert(1)",
            "<img onload='alert(1)'>",
            "<iframe src='evil.com'>",
            "onclick='malicious()'"
        ]
        
        for attack in xss_attacks:
            assert InputValidator.check_xss_attempt(attack) is True
    
    def test_check_xss_attempt_safe(self):
        """Testa texto seguro para XSS"""
        safe_texts = [
            "Normal user input",
            "Html entities: &lt;script&gt;",
            "Regular text with <em>emphasis</em>",
            "Email link: mailto:user@domain.com"
        ]
        
        for text in safe_texts:
            assert InputValidator.check_xss_attempt(text) is False

class TestWebhookSecurity:
    """Testes para WebhookSecurity"""
    
    @patch('backend.utils.security.active_config')
    def test_verify_waha_webhook_with_key(self, mock_config):
        """Testa verificação de webhook Waha com chave"""
        mock_config.WAHA_API_KEY = "test_secret_key"
        
        payload = '{"event": "message", "data": "test"}'
        
        # Cria assinatura válida
        signature = security_manager.create_webhook_signature(payload, "test_secret_key")
        
        is_valid = WebhookSecurity.verify_waha_webhook(payload, signature)
        assert is_valid is True
        
        # Testa assinatura inválida
        is_valid = WebhookSecurity.verify_waha_webhook(payload, "invalid_signature")
        assert is_valid is False
    
    @patch('backend.utils.security.active_config')
    def test_verify_waha_webhook_no_key(self, mock_config):
        """Testa verificação de webhook Waha sem chave configurada"""
        mock_config.WAHA_API_KEY = None
        
        payload = '{"event": "message", "data": "test"}'
        
        # Deve permitir se não há chave configurada
        is_valid = WebhookSecurity.verify_waha_webhook(payload, "any_signature")
        assert is_valid is True
    
    @patch('backend.utils.security.active_config')
    def test_validate_webhook_source_debug_mode(self, mock_config):
        """Testa validação de origem em modo debug"""
        mock_config.DEBUG = True
        
        # Em modo debug, deve permitir qualquer IP
        assert WebhookSecurity.validate_webhook_source("192.168.1.100") is True
        assert WebhookSecurity.validate_webhook_source("10.0.0.1") is True
    
    @patch('backend.utils.security.active_config')
    def test_validate_webhook_source_production(self, mock_config):
        """Testa validação de origem em produção"""
        mock_config.DEBUG = False
        
        # Deve permitir IPs locais
        assert WebhookSecurity.validate_webhook_source("127.0.0.1") is True
        assert WebhookSecurity.validate_webhook_source("::1") is True
        
        # Deve bloquear IPs externos
        assert WebhookSecurity.validate_webhook_source("192.168.1.100") is False
        assert WebhookSecurity.validate_webhook_source("8.8.8.8") is False

class TestSecurityIntegration:
    """Testes de integração de segurança"""
    
    def test_complete_auth_flow(self):
        """Testa fluxo completo de autenticação"""
        # 1. Hash da senha
        password = "secure_password_123"
        hash_result = security_manager.hash_password(password)
        
        # 2. Verifica senha
        is_valid = security_manager.verify_password(
            password, hash_result["hash"], hash_result["salt"]
        )
        assert is_valid is True
        
        # 3. Cria token JWT
        payload = {"user_id": "123", "username": "test"}
        token = security_manager.create_jwt_token(payload)
        
        # 4. Verifica token
        decoded = security_manager.verify_jwt_token(token)
        assert decoded["user_id"] == "123"
        assert decoded["username"] == "test"
    
    def test_rate_limiting_and_validation(self):
        """Testa rate limiting combinado com validação"""
        rate_limiter = RateLimiter()
        rate_limiter.max_requests = 3
        
        user_id = "test_user"
        
        # Requisições normais
        for i in range(3):
            result = rate_limiter.is_allowed(user_id)
            assert result["allowed"] is True
        
        # Quarta requisição bloqueada
        result = rate_limiter.is_allowed(user_id)
        assert result["allowed"] is False
        
        # Valida input malicioso
        malicious_input = "<script>alert('xss')</script>"
        assert InputValidator.check_xss_attempt(malicious_input) is True

if __name__ == "__main__":
    pytest.main([__file__])

