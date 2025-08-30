"""
Módulo de segurança e proteções do sistema
"""
import hashlib
import hmac
import secrets
import time
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, jsonify, current_app
from cryptography.fernet import Fernet
from backend.config.settings import active_config
from backend.utils.logger import app_logger

class SecurityManager:
    """Gerenciador central de segurança"""
    
    def __init__(self):
        self.config = active_config
        self.rate_limiter = RateLimiter()
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key) if self.encryption_key else None
    
    def _get_encryption_key(self) -> Optional[bytes]:
        """Obtém chave de criptografia"""
        try:
            key = self.config.ENCRYPTION_KEY
            if key:
                return key.encode()[:32].ljust(32, b'0')  # Ajusta para 32 bytes
            return None
        except Exception:
            return None
    
    def encrypt_data(self, data: str) -> Optional[str]:
        """Criptografa dados sensíveis"""
        if not self.cipher_suite:
            return data
        
        try:
            encrypted = self.cipher_suite.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            app_logger.error("ENCRYPTION_FAILED", e, {"data_length": len(data)})
            return data
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """Descriptografa dados"""
        if not self.cipher_suite:
            return encrypted_data
        
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            app_logger.error("DECRYPTION_FAILED", e)
            return None
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Gera token seguro"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Dict[str, str]:
        """Hash de senha com salt"""
        if not salt:
            salt = secrets.token_hex(32)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return {
            'hash': hash_obj.hex(),
            'salt': salt
        }
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """Verifica senha"""
        return self.hash_password(password, salt)['hash'] == hash_value
    
    def create_jwt_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """Cria token JWT"""
        payload.update({
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow(),
            'jti': self.generate_secure_token(16)  # JWT ID
        })
        
        return jwt.encode(payload, self.config.JWT_SECRET_KEY, algorithm='HS256')
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica token JWT"""
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            app_logger.warning("JWT_EXPIRED", {"token_prefix": token[:10]})
            return None
        except jwt.InvalidTokenError as e:
            app_logger.warning("JWT_INVALID", {"error": str(e), "token_prefix": token[:10]})
            return None
    
    def create_webhook_signature(self, payload: str, secret: str) -> str:
        """Cria assinatura para webhook"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verifica assinatura de webhook"""
        expected_signature = self.create_webhook_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)

class RateLimiter:
    """Limitador de taxa de requisições"""
    
    def __init__(self):
        self.requests = {}  # {ip: [(timestamp, count), ...]}
        self.max_requests = active_config.RATE_LIMIT_REQUESTS
        self.time_window = active_config.RATE_LIMIT_PERIOD
    
    def is_allowed(self, identifier: str) -> Dict[str, Any]:
        """Verifica se requisição é permitida"""
        current_time = time.time()
        
        # Limpa entradas antigas
        self._cleanup_old_entries(current_time)
        
        # Verifica entradas do identificador
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        user_requests = self.requests[identifier]
        
        # Remove requisições antigas para este usuário
        user_requests[:] = [
            (timestamp, count) for timestamp, count in user_requests
            if current_time - timestamp < self.time_window
        ]
        
        # Conta requisições no período
        total_requests = sum(count for _, count in user_requests)
        
        if total_requests >= self.max_requests:
            app_logger.security("RATE_LIMIT_EXCEEDED", {
                "identifier": identifier,
                "requests": total_requests,
                "limit": self.max_requests
            })
            
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": current_time + self.time_window,
                "limit": self.max_requests
            }
        
        # Adiciona nova requisição
        user_requests.append((current_time, 1))
        
        return {
            "allowed": True,
            "remaining": self.max_requests - total_requests - 1,
            "reset_time": current_time + self.time_window,
            "limit": self.max_requests
        }
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove entradas antigas para economizar memória"""
        cutoff_time = current_time - self.time_window
        
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                (timestamp, count) for timestamp, count in self.requests[identifier]
                if timestamp > cutoff_time
            ]
            
            # Remove usuários sem requisições recentes
            if not self.requests[identifier]:
                del self.requests[identifier]

class InputValidator:
    """Validador de entrada para segurança"""
    
    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """Sanitiza entrada removendo caracteres perigosos"""
        if isinstance(data, str):
            # Remove caracteres de controle
            sanitized = ''.join(char for char in data if ord(char) >= 32 or char in '\n\r\t')
            # Limita tamanho
            return sanitized[:10000]  # Máximo 10KB
        elif isinstance(data, dict):
            return {key: InputValidator.sanitize_input(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [InputValidator.sanitize_input(item) for item in data]
        else:
            return data
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """Valida número de telefone brasileiro"""
        import re
        # Remove caracteres não numéricos
        clean_phone = re.sub(r'\D', '', phone)
        # Verifica formato brasileiro (+55)
        return re.match(r'^55\d{10,11}$', clean_phone) is not None
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def check_sql_injection(text: str) -> bool:
        """Verifica possíveis tentativas de SQL injection"""
        dangerous_patterns = [
            r'\bunion\b.*\bselect\b',
            r'\bselect\b.*\bfrom\b',
            r'\binsert\b.*\binto\b',
            r'\bupdate\b.*\bset\b',
            r'\bdelete\b.*\bfrom\b',
            r'\bdrop\b.*\btable\b',
            r'--\s*$',
            r'/\*.*\*/',
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            import re
            if re.search(pattern, text_lower):
                return True
        return False
    
    @staticmethod
    def check_xss_attempt(text: str) -> bool:
        """Verifica tentativas de XSS"""
        dangerous_patterns = [
            r'<script.*?>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?>',
            r'<object.*?>',
            r'<embed.*?>',
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            import re
            if re.search(pattern, text_lower):
                return True
        return False

class SecurityDecorators:
    """Decoradores de segurança"""
    
    @staticmethod
    def rate_limit(per_second: int = None):
        """Decorador para rate limiting"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Obtém identificador (IP + User-Agent)
                identifier = f"{request.remote_addr}:{request.headers.get('User-Agent', '')[:50]}"
                
                # Verifica rate limit
                rate_check = security_manager.rate_limiter.is_allowed(identifier)
                
                if not rate_check["allowed"]:
                    response = jsonify({
                        "error": "Muitas requisições. Tente novamente mais tarde.",
                        "retry_after": int(rate_check["reset_time"] - time.time())
                    })
                    response.status_code = 429
                    response.headers["X-RateLimit-Limit"] = str(rate_check["limit"])
                    response.headers["X-RateLimit-Remaining"] = "0"
                    response.headers["X-RateLimit-Reset"] = str(int(rate_check["reset_time"]))
                    return response
                
                # Adiciona headers de rate limit à resposta
                response = f(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers["X-RateLimit-Limit"] = str(rate_check["limit"])
                    response.headers["X-RateLimit-Remaining"] = str(rate_check["remaining"])
                    response.headers["X-RateLimit-Reset"] = str(int(rate_check["reset_time"]))
                
                return response
            return wrapper
        return decorator
    
    @staticmethod
    def validate_input():
        """Decorador para validação de entrada"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                # Valida JSON se presente
                if request.is_json:
                    try:
                        data = request.get_json()
                        
                        # Verifica tentativas de ataque
                        for key, value in data.items():
                            if isinstance(value, str):
                                if InputValidator.check_sql_injection(value):
                                    app_logger.security("SQL_INJECTION_ATTEMPT", {
                                        "ip": request.remote_addr,
                                        "endpoint": request.endpoint,
                                        "key": key
                                    })
                                    return jsonify({"error": "Entrada inválida"}), 400
                                
                                if InputValidator.check_xss_attempt(value):
                                    app_logger.security("XSS_ATTEMPT", {
                                        "ip": request.remote_addr,
                                        "endpoint": request.endpoint,
                                        "key": key
                                    })
                                    return jsonify({"error": "Entrada inválida"}), 400
                        
                        # Sanitiza dados
                        sanitized_data = InputValidator.sanitize_input(data)
                        request._cached_json = sanitized_data
                        
                    except Exception as e:
                        app_logger.warning("INPUT_VALIDATION_ERROR", {"error": str(e)})
                        return jsonify({"error": "Dados inválidos"}), 400
                
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def require_auth():
        """Decorador para exigir autenticação"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                auth_header = request.headers.get('Authorization')
                
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Token de acesso requerido"}), 401
                
                token = auth_header.split(' ')[1]
                payload = security_manager.verify_jwt_token(token)
                
                if not payload:
                    return jsonify({"error": "Token inválido ou expirado"}), 401
                
                # Adiciona payload ao contexto da requisição
                request.jwt_payload = payload
                
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def log_security_event():
        """Decorador para log de eventos de segurança"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    response = f(*args, **kwargs)
                    
                    # Log evento de segurança bem-sucedido
                    app_logger.security("SECURITY_EVENT_SUCCESS", {
                        "endpoint": request.endpoint,
                        "method": request.method,
                        "ip": request.remote_addr,
                        "user_agent": request.headers.get('User-Agent', '')[:100],
                        "duration": time.time() - start_time
                    })
                    
                    return response
                    
                except Exception as e:
                    # Log evento de segurança com falha
                    app_logger.security("SECURITY_EVENT_FAILURE", {
                        "endpoint": request.endpoint,
                        "method": request.method,
                        "ip": request.remote_addr,
                        "error": str(e),
                        "duration": time.time() - start_time
                    })
                    raise
                    
            return wrapper
        return decorator

class WebhookSecurity:
    """Segurança específica para webhooks"""
    
    @staticmethod
    def verify_waha_webhook(payload: str, signature: str) -> bool:
        """Verifica assinatura de webhook da Waha"""
        if not active_config.WAHA_API_KEY:
            app_logger.warning("WEBHOOK_NO_SECRET", {"source": "waha"})
            return True  # Permite se não há chave configurada
        
        return security_manager.verify_webhook_signature(
            payload, signature, active_config.WAHA_API_KEY
        )
    
    @staticmethod
    def validate_webhook_source(source_ip: str) -> bool:
        """Valida origem do webhook"""
        # Lista de IPs permitidos (configurável)
        allowed_ips = [
            '127.0.0.1',
            '::1',
            # Adicionar IPs da Waha se conhecidos
        ]
        
        # Em desenvolvimento, permite qualquer IP
        if active_config.DEBUG:
            return True
        
        return source_ip in allowed_ips

class SecurityHeaders:
    """Headers de segurança HTTP"""
    
    @staticmethod
    def add_security_headers(response):
        """Adiciona headers de segurança à resposta"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

# Instância global do gerenciador de segurança
security_manager = SecurityManager()

# Decoradores para uso direto
rate_limit = SecurityDecorators.rate_limit
validate_input = SecurityDecorators.validate_input
require_auth = SecurityDecorators.require_auth
log_security_event = SecurityDecorators.log_security_event

