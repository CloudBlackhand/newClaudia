#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Segurança para Oracle Cloud
Hardening, validação e proteção contra ataques
"""

import os
import re
import hashlib
import secrets
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import bcrypt
from cryptography.fernet import Fernet
import ipaddress
from .logger import logger, security_event

class SecurityManager:
    """Gerenciador de segurança central"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
        self.rate_limits = {}
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Configurações de segurança
        self.max_failed_attempts = int(os.getenv('MAX_FAILED_ATTEMPTS', 5))
        self.lockout_duration = int(os.getenv('LOCKOUT_DURATION', 900))  # 15 minutos
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # 1 minuto
        self.max_requests_per_window = int(os.getenv('MAX_REQUESTS_PER_WINDOW', 100))
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Obter ou criar chave de criptografia"""
        key_file = os.path.join('sessions', '.encryption_key')
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Could not read encryption key: {e}")
        
        # Criar nova chave
        key = Fernet.generate_key()
        
        try:
            os.makedirs('sessions', exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Apenas proprietário pode ler
            logger.info("New encryption key generated")
        except Exception as e:
            logger.error(f"Could not save encryption key: {e}")
            
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Criptografar dados sensíveis"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Fallback - retorna dados originais
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografar dados"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Fallback
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validar chave API"""
        expected_key = os.getenv('API_KEY', 'default_key_change_me')
        
        if expected_key == 'default_key_change_me':
            security_event("default_api_key_used", "high")
            logger.warning("Using default API key - security risk!")
        
        # Usar comparação segura para evitar timing attacks
        return secrets.compare_digest(provided_key.encode(), expected_key.encode())
    
    def hash_password(self, password: str) -> str:
        """Hash seguro de senha"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar senha com hash"""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def check_rate_limit(self, identifier: str, max_requests: Optional[int] = None) -> bool:
        """Verificar rate limiting"""
        if max_requests is None:
            max_requests = self.max_requests_per_window
            
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # Limpar registros antigos
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                timestamp for timestamp in self.rate_limits[identifier]
                if timestamp > window_start
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Verificar limite
        if len(self.rate_limits[identifier]) >= max_requests:
            security_event("rate_limit_exceeded", "medium", identifier=identifier)
            return False
        
        # Registrar nova requisição
        self.rate_limits[identifier].append(now)
        return True
    
    def register_failed_attempt(self, identifier: str) -> bool:
        """Registrar tentativa de login falhada"""
        now = time.time()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Limpar tentativas antigas
        cutoff = now - self.lockout_duration
        self.failed_attempts[identifier] = [
            timestamp for timestamp in self.failed_attempts[identifier]
            if timestamp > cutoff
        ]
        
        # Adicionar nova tentativa
        self.failed_attempts[identifier].append(now)
        
        # Verificar se deve bloquear
        if len(self.failed_attempts[identifier]) >= self.max_failed_attempts:
            self.blocked_ips[identifier] = now + self.lockout_duration
            security_event("account_locked", "high", identifier=identifier)
            return False
        
        security_event("failed_login_attempt", "medium", identifier=identifier)
        return True
    
    def is_blocked(self, identifier: str) -> bool:
        """Verificar se IP/usuário está bloqueado"""
        if identifier in self.blocked_ips:
            if time.time() < self.blocked_ips[identifier]:
                return True
            else:
                # Remover bloqueio expirado
                del self.blocked_ips[identifier]
        return False
    
    def validate_file_upload(self, filename: str, content: bytes, max_size: int = 50 * 1024 * 1024) -> Dict[str, Any]:
        """Validar upload de arquivo"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar tamanho
        if len(content) > max_size:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File too large: {len(content)} bytes")
        
        # Verificar extensão
        allowed_extensions = {'.xlsx', '.xls', '.csv', '.pdf', '.png', '.jpg', '.jpeg'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid file extension: {file_ext}")
        
        # Verificar nome do arquivo
        if not self._is_safe_filename(filename):
            validation_result['valid'] = False
            validation_result['errors'].append("Invalid filename characters")
        
        # Verificar conteúdo suspeito
        suspicious_patterns = [b'<script', b'javascript:', b'<?php', b'#!/bin/bash']
        for pattern in suspicious_patterns:
            if pattern in content.lower():
                validation_result['valid'] = False
                validation_result['errors'].append("Suspicious content detected")
                security_event("malicious_upload_attempt", "high", filename=filename)
                break
        
        if not validation_result['valid']:
            security_event("file_upload_rejected", "medium", filename=filename, errors=validation_result['errors'])
        
        return validation_result
    
    def _is_safe_filename(self, filename: str) -> bool:
        """Verificar se nome do arquivo é seguro"""
        # Padrão para caracteres seguros
        safe_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        
        # Verificar tamanho
        if len(filename) > 255:
            return False
        
        # Verificar caracteres
        if not safe_pattern.match(filename):
            return False
        
        # Verificar nomes reservados
        reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4',
                         'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2',
                         'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
        
        name_without_ext = os.path.splitext(filename)[0].lower()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    def sanitize_input(self, user_input: str, max_length: int = 1000) -> str:
        """Sanitizar entrada do usuário"""
        if not isinstance(user_input, str):
            return ""
        
        # Truncar se muito longo
        sanitized = user_input[:max_length]
        
        # Remover caracteres de controle
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        # Escapar caracteres HTML básicos
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        
        for char, escape in html_escape_table.items():
            sanitized = sanitized.replace(char, escape)
        
        return sanitized
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validar número de telefone"""
        if not phone:
            return False
        
        # Remover caracteres não numéricos
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Verificar comprimento (brasileiro: 10 ou 11 dígitos)
        if len(digits_only) not in [10, 11]:
            return False
        
        # Verificar padrões válidos brasileiros
        if len(digits_only) == 11:
            # Celular: (XX) 9XXXX-XXXX
            if not digits_only[2] == '9':
                return False
        
        return True
    
    def validate_cpf(self, cpf: str) -> bool:
        """Validar CPF"""
        if not cpf:
            return False
        
        # Remover caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcular dígitos verificadores
        def calculate_digit(cpf_partial):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, range(len(cpf_partial) + 1, 1, -1)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        return (calculate_digit(cpf[:9]) == int(cpf[9]) and 
                calculate_digit(cpf[:10]) == int(cpf[10]))
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Gerar token seguro"""
        return secrets.token_urlsafe(length)
    
    def check_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Verificar headers de segurança"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        missing_headers = []
        for header, expected_value in security_headers.items():
            if header not in headers:
                missing_headers.append(header)
        
        return {
            'missing_headers': missing_headers,
            'recommendations': security_headers
        }
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Obter métricas de segurança"""
        now = time.time()
        
        # Contar tentativas falhadas recentes (última hora)
        recent_failures = 0
        for attempts in self.failed_attempts.values():
            recent_failures += sum(1 for attempt in attempts if now - attempt < 3600)
        
        # Contar IPs bloqueados ativos
        active_blocks = sum(1 for block_time in self.blocked_ips.values() if block_time > now)
        
        return {
            'recent_failed_attempts': recent_failures,
            'active_ip_blocks': active_blocks,
            'total_tracked_ips': len(self.failed_attempts),
            'rate_limit_active': len(self.rate_limits),
            'encryption_active': bool(self.encryption_key),
            'security_events_last_hour': recent_failures  # Simplificado
        }

# Instância global do gerenciador de segurança
security_manager = SecurityManager()

# Funções de conveniência
def validate_api_key(key: str) -> bool:
    return security_manager.validate_api_key(key)

def check_rate_limit(identifier: str) -> bool:
    return security_manager.check_rate_limit(identifier)

def validate_file_upload(filename: str, content: bytes) -> Dict[str, Any]:
    return security_manager.validate_file_upload(filename, content)

def sanitize_input(user_input: str) -> str:
    return security_manager.sanitize_input(user_input)

def is_blocked(identifier: str) -> bool:
    return security_manager.is_blocked(identifier)

def register_failed_attempt(identifier: str) -> bool:
    return security_manager.register_failed_attempt(identifier)
# -*- coding: utf-8 -*-
"""
Sistema de Segurança para Oracle Cloud
Hardening, validação e proteção contra ataques
"""

import os
import re
import hashlib
import secrets
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import bcrypt
from cryptography.fernet import Fernet
import ipaddress
from .logger import logger, security_event

class SecurityManager:
    """Gerenciador de segurança central"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.blocked_ips = {}
        self.rate_limits = {}
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Configurações de segurança
        self.max_failed_attempts = int(os.getenv('MAX_FAILED_ATTEMPTS', 5))
        self.lockout_duration = int(os.getenv('LOCKOUT_DURATION', 900))  # 15 minutos
        self.rate_limit_window = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # 1 minuto
        self.max_requests_per_window = int(os.getenv('MAX_REQUESTS_PER_WINDOW', 100))
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Obter ou criar chave de criptografia"""
        key_file = os.path.join('sessions', '.encryption_key')
        
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Could not read encryption key: {e}")
        
        # Criar nova chave
        key = Fernet.generate_key()
        
        try:
            os.makedirs('sessions', exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Apenas proprietário pode ler
            logger.info("New encryption key generated")
        except Exception as e:
            logger.error(f"Could not save encryption key: {e}")
            
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Criptografar dados sensíveis"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return data  # Fallback - retorna dados originais
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Descriptografar dados"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data  # Fallback
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validar chave API"""
        expected_key = os.getenv('API_KEY', 'default_key_change_me')
        
        if expected_key == 'default_key_change_me':
            security_event("default_api_key_used", "high")
            logger.warning("Using default API key - security risk!")
        
        # Usar comparação segura para evitar timing attacks
        return secrets.compare_digest(provided_key.encode(), expected_key.encode())
    
    def hash_password(self, password: str) -> str:
        """Hash seguro de senha"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verificar senha com hash"""
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def check_rate_limit(self, identifier: str, max_requests: Optional[int] = None) -> bool:
        """Verificar rate limiting"""
        if max_requests is None:
            max_requests = self.max_requests_per_window
            
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # Limpar registros antigos
        if identifier in self.rate_limits:
            self.rate_limits[identifier] = [
                timestamp for timestamp in self.rate_limits[identifier]
                if timestamp > window_start
            ]
        else:
            self.rate_limits[identifier] = []
        
        # Verificar limite
        if len(self.rate_limits[identifier]) >= max_requests:
            security_event("rate_limit_exceeded", "medium", identifier=identifier)
            return False
        
        # Registrar nova requisição
        self.rate_limits[identifier].append(now)
        return True
    
    def register_failed_attempt(self, identifier: str) -> bool:
        """Registrar tentativa de login falhada"""
        now = time.time()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        
        # Limpar tentativas antigas
        cutoff = now - self.lockout_duration
        self.failed_attempts[identifier] = [
            timestamp for timestamp in self.failed_attempts[identifier]
            if timestamp > cutoff
        ]
        
        # Adicionar nova tentativa
        self.failed_attempts[identifier].append(now)
        
        # Verificar se deve bloquear
        if len(self.failed_attempts[identifier]) >= self.max_failed_attempts:
            self.blocked_ips[identifier] = now + self.lockout_duration
            security_event("account_locked", "high", identifier=identifier)
            return False
        
        security_event("failed_login_attempt", "medium", identifier=identifier)
        return True
    
    def is_blocked(self, identifier: str) -> bool:
        """Verificar se IP/usuário está bloqueado"""
        if identifier in self.blocked_ips:
            if time.time() < self.blocked_ips[identifier]:
                return True
            else:
                # Remover bloqueio expirado
                del self.blocked_ips[identifier]
        return False
    
    def validate_file_upload(self, filename: str, content: bytes, max_size: int = 50 * 1024 * 1024) -> Dict[str, Any]:
        """Validar upload de arquivo"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Verificar tamanho
        if len(content) > max_size:
            validation_result['valid'] = False
            validation_result['errors'].append(f"File too large: {len(content)} bytes")
        
        # Verificar extensão
        allowed_extensions = {'.xlsx', '.xls', '.csv', '.pdf', '.png', '.jpg', '.jpeg'}
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Invalid file extension: {file_ext}")
        
        # Verificar nome do arquivo
        if not self._is_safe_filename(filename):
            validation_result['valid'] = False
            validation_result['errors'].append("Invalid filename characters")
        
        # Verificar conteúdo suspeito
        suspicious_patterns = [b'<script', b'javascript:', b'<?php', b'#!/bin/bash']
        for pattern in suspicious_patterns:
            if pattern in content.lower():
                validation_result['valid'] = False
                validation_result['errors'].append("Suspicious content detected")
                security_event("malicious_upload_attempt", "high", filename=filename)
                break
        
        if not validation_result['valid']:
            security_event("file_upload_rejected", "medium", filename=filename, errors=validation_result['errors'])
        
        return validation_result
    
    def _is_safe_filename(self, filename: str) -> bool:
        """Verificar se nome do arquivo é seguro"""
        # Padrão para caracteres seguros
        safe_pattern = re.compile(r'^[a-zA-Z0-9._-]+$')
        
        # Verificar tamanho
        if len(filename) > 255:
            return False
        
        # Verificar caracteres
        if not safe_pattern.match(filename):
            return False
        
        # Verificar nomes reservados
        reserved_names = {'con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4',
                         'com5', 'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2',
                         'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'}
        
        name_without_ext = os.path.splitext(filename)[0].lower()
        if name_without_ext in reserved_names:
            return False
        
        return True
    
    def sanitize_input(self, user_input: str, max_length: int = 1000) -> str:
        """Sanitizar entrada do usuário"""
        if not isinstance(user_input, str):
            return ""
        
        # Truncar se muito longo
        sanitized = user_input[:max_length]
        
        # Remover caracteres de controle
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        # Escapar caracteres HTML básicos
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        
        for char, escape in html_escape_table.items():
            sanitized = sanitized.replace(char, escape)
        
        return sanitized
    
    def validate_phone_number(self, phone: str) -> bool:
        """Validar número de telefone"""
        if not phone:
            return False
        
        # Remover caracteres não numéricos
        digits_only = ''.join(filter(str.isdigit, phone))
        
        # Verificar comprimento (brasileiro: 10 ou 11 dígitos)
        if len(digits_only) not in [10, 11]:
            return False
        
        # Verificar padrões válidos brasileiros
        if len(digits_only) == 11:
            # Celular: (XX) 9XXXX-XXXX
            if not digits_only[2] == '9':
                return False
        
        return True
    
    def validate_cpf(self, cpf: str) -> bool:
        """Validar CPF"""
        if not cpf:
            return False
        
        # Remover caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Calcular dígitos verificadores
        def calculate_digit(cpf_partial):
            total = sum(int(digit) * weight for digit, weight in zip(cpf_partial, range(len(cpf_partial) + 1, 1, -1)))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder
        
        return (calculate_digit(cpf[:9]) == int(cpf[9]) and 
                calculate_digit(cpf[:10]) == int(cpf[10]))
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Gerar token seguro"""
        return secrets.token_urlsafe(length)
    
    def check_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Verificar headers de segurança"""
        security_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        missing_headers = []
        for header, expected_value in security_headers.items():
            if header not in headers:
                missing_headers.append(header)
        
        return {
            'missing_headers': missing_headers,
            'recommendations': security_headers
        }
    
    def get_security_metrics(self) -> Dict[str, Any]:
        """Obter métricas de segurança"""
        now = time.time()
        
        # Contar tentativas falhadas recentes (última hora)
        recent_failures = 0
        for attempts in self.failed_attempts.values():
            recent_failures += sum(1 for attempt in attempts if now - attempt < 3600)
        
        # Contar IPs bloqueados ativos
        active_blocks = sum(1 for block_time in self.blocked_ips.values() if block_time > now)
        
        return {
            'recent_failed_attempts': recent_failures,
            'active_ip_blocks': active_blocks,
            'total_tracked_ips': len(self.failed_attempts),
            'rate_limit_active': len(self.rate_limits),
            'encryption_active': bool(self.encryption_key),
            'security_events_last_hour': recent_failures  # Simplificado
        }

# Instância global do gerenciador de segurança
security_manager = SecurityManager()

# Funções de conveniência
def validate_api_key(key: str) -> bool:
    return security_manager.validate_api_key(key)

def check_rate_limit(identifier: str) -> bool:
    return security_manager.check_rate_limit(identifier)

def validate_file_upload(filename: str, content: bytes) -> Dict[str, Any]:
    return security_manager.validate_file_upload(filename, content)

def sanitize_input(user_input: str) -> str:
    return security_manager.sanitize_input(user_input)

def is_blocked(identifier: str) -> bool:
    return security_manager.is_blocked(identifier)

def register_failed_attempt(identifier: str) -> bool:
    return security_manager.register_failed_attempt(identifier)
 