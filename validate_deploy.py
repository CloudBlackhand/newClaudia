#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validação para Deploy na Railway
Verifica se o sistema está pronto para produção
"""

import os
import json
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Tuple

class Color:
    """Cores para output no terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DeployValidator:
    """Validador para deploy na Railway"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checks_passed = 0
        self.total_checks = 0
        
    def log_success(self, message: str):
        """Log de sucesso"""
        print(f"{Color.GREEN}✅ {message}{Color.END}")
        self.checks_passed += 1
        
    def log_error(self, message: str):
        """Log de erro"""
        print(f"{Color.RED}❌ {message}{Color.END}")
        self.errors.append(message)
        
    def log_warning(self, message: str):
        """Log de aviso"""
        print(f"{Color.YELLOW}⚠️  {message}{Color.END}")
        self.warnings.append(message)
        
    def log_info(self, message: str):
        """Log de informação"""
        print(f"{Color.BLUE}ℹ️  {message}{Color.END}")
    
    def check_file_exists(self, file_path: str, description: str) -> bool:
        """Verificar se arquivo existe"""
        self.total_checks += 1
        if Path(file_path).exists():
            self.log_success(f"{description}: {file_path}")
            return True
        else:
            self.log_error(f"{description} não encontrado: {file_path}")
            return False
    
    def check_directory_structure(self) -> None:
        """Verificar estrutura de diretórios"""
        print(f"\n{Color.BOLD}📁 Verificando Estrutura do Projeto{Color.END}")
        
        required_files = [
            ("requirements.txt", "Dependências Python"),
            ("start.py", "Script de inicialização"),
            ("railway.json", "Configuração Railway"),
            ("README.md", "Documentação principal"),
            ("environment.example", "Exemplo de configuração"),
        ]
        
        required_dirs = [
            ("backend", "Diretório backend"),
            ("frontend", "Diretório frontend"),
            ("tests", "Diretório de testes"),
            ("docs", "Diretório de documentação"),
        ]
        
        for file_path, description in required_files:
            self.check_file_exists(file_path, description)
            
        for dir_path, description in required_dirs:
            self.total_checks += 1
            if Path(dir_path).is_dir():
                self.log_success(f"{description}: {dir_path}/")
            else:
                self.log_error(f"{description} não encontrado: {dir_path}/")
    
    def check_backend_structure(self) -> None:
        """Verificar estrutura do backend"""
        print(f"\n{Color.BOLD}🖥️  Verificando Backend{Color.END}")
        
        backend_files = [
            ("backend/app.py", "Aplicação Flask"),
            ("backend/config/settings.py", "Configurações"),
            ("backend/modules/billing_dispatcher.py", "Sistema de cobrança"),
            ("backend/modules/conversation_bot.py", "Bot de conversação"),
            ("backend/modules/validation_engine.py", "Engine de validação"),
            ("backend/modules/logger_system.py", "Sistema de logs"),
            ("backend/modules/waha_integration.py", "Integração Waha"),
            ("backend/api/routes/billing_routes.py", "Rotas de cobrança"),
            ("backend/api/routes/conversation_routes.py", "Rotas de conversação"),
            ("backend/api/routes/webhook_routes.py", "Rotas de webhook"),
        ]
        
        for file_path, description in backend_files:
            self.check_file_exists(file_path, description)
    
    def check_frontend_structure(self) -> None:
        """Verificar estrutura do frontend"""
        print(f"\n{Color.BOLD}🎨 Verificando Frontend{Color.END}")
        
        frontend_files = [
            ("frontend/index.html", "Página principal"),
            ("frontend/styles.css", "Estilos CSS"),
            ("frontend/app.js", "Aplicação JavaScript"),
        ]
        
        for file_path, description in frontend_files:
            self.check_file_exists(file_path, description)
    
    def check_dependencies(self) -> None:
        """Verificar dependências"""
        print(f"\n{Color.BOLD}📦 Verificando Dependências{Color.END}")
        
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                
            required_packages = [
                'Flask',
                'Flask-CORS',
                'requests',
                'python-dotenv',
                'gunicorn',
                'fastapi',
                'pydantic',
                'aiohttp'
            ]
            
            for package in required_packages:
                self.total_checks += 1
                if package in requirements:
                    self.log_success(f"Dependência encontrada: {package}")
                else:
                    self.log_error(f"Dependência ausente: {package}")
                    
        except FileNotFoundError:
            self.log_error("requirements.txt não encontrado")
    
    def check_railway_config(self) -> None:
        """Verificar configuração da Railway"""
        print(f"\n{Color.BOLD}🚂 Verificando Configuração Railway{Color.END}")
        
        try:
            with open('railway.json', 'r') as f:
                config = json.load(f)
            
            self.total_checks += 1
            if 'deploy' in config:
                deploy_config = config['deploy']
                
                # Verificar startCommand
                if 'startCommand' in deploy_config:
                    start_command = deploy_config['startCommand']
                    if 'python start.py' in start_command:
                        self.log_success(f"Comando de inicialização: {start_command}")
                    else:
                        self.log_warning(f"Comando de inicialização não padrão: {start_command}")
                else:
                    self.log_error("startCommand não definido em railway.json")
                
                # Verificar healthcheck
                if 'healthcheckPath' in deploy_config:
                    health_path = deploy_config['healthcheckPath']
                    self.log_success(f"Health check: {health_path}")
                else:
                    self.log_warning("healthcheckPath não definido")
                    
            else:
                self.log_error("Seção 'deploy' não encontrada em railway.json")
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.log_error(f"Erro ao ler railway.json: {e}")
    
    def check_environment_variables(self) -> None:
        """Verificar variáveis de ambiente"""
        print(f"\n{Color.BOLD}🔧 Verificando Variáveis de Ambiente{Color.END}")
        
        required_vars = [
            'SECRET_KEY',
            'WAHA_BASE_URL',
            'API_KEY',
            'WEBHOOK_SECRET'
        ]
        
        optional_vars = [
            'DEBUG',
            'LOG_LEVEL',
            'MESSAGE_RATE_LIMIT',
            'AI_CONFIDENCE_THRESHOLD'
        ]
        
        try:
            with open('environment.example', 'r') as f:
                env_example = f.read()
            
            for var in required_vars:
                self.total_checks += 1
                if var in env_example:
                    self.log_success(f"Variável obrigatória documentada: {var}")
                else:
                    self.log_error(f"Variável obrigatória não documentada: {var}")
            
            for var in optional_vars:
                if var in env_example:
                    self.log_info(f"Variável opcional documentada: {var}")
                    
        except FileNotFoundError:
            self.log_error("environment.example não encontrado")
    
    def check_python_syntax(self) -> None:
        """Verificar sintaxe Python"""
        print(f"\n{Color.BOLD}🐍 Verificando Sintaxe Python{Color.END}")
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            # Pular diretórios desnecessários
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        syntax_errors = 0
        for file_path in python_files:
            self.total_checks += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                self.log_success(f"Sintaxe válida: {file_path}")
            except SyntaxError as e:
                self.log_error(f"Erro de sintaxe em {file_path}: {e}")
                syntax_errors += 1
            except Exception as e:
                self.log_warning(f"Erro ao verificar {file_path}: {e}")
        
        if syntax_errors == 0:
            self.log_info(f"✅ Todos os {len(python_files)} arquivos Python têm sintaxe válida")
    
    def check_imports(self) -> None:
        """Verificar se imports estão corretos"""
        print(f"\n{Color.BOLD}📥 Verificando Imports{Color.END}")
        
        # Adicionar diretório atual ao path para imports locais
        sys.path.insert(0, os.getcwd())
        
        critical_modules = [
            ('backend.app', 'Aplicação principal'),
            ('backend.config.settings', 'Configurações'),
            ('backend.modules.validation_engine', 'Engine de validação'),
            ('backend.modules.conversation_bot', 'Bot de conversação'),
        ]
        
        for module_name, description in critical_modules:
            self.total_checks += 1
            try:
                __import__(module_name)
                self.log_success(f"Import válido: {description}")
            except ImportError as e:
                self.log_error(f"Erro de import em {description}: {e}")
            except Exception as e:
                self.log_warning(f"Erro ao testar import {description}: {e}")
    
    def check_tests(self) -> None:
        """Verificar estrutura de testes"""
        print(f"\n{Color.BOLD}🧪 Verificando Testes{Color.END}")
        
        test_files = [
            ("tests/test_validation_engine.py", "Testes de validação"),
            ("tests/test_conversation_bot.py", "Testes do bot"),
            ("tests/test_api.py", "Testes de API"),
            ("run_tests.py", "Script de execução de testes"),
            ("pytest.ini", "Configuração pytest"),
        ]
        
        for file_path, description in test_files:
            self.check_file_exists(file_path, description)
        
        # Verificar se pytest está disponível
        self.total_checks += 1
        try:
            import pytest
            self.log_success("Pytest disponível")
        except ImportError:
            self.log_error("Pytest não encontrado - execute: pip install pytest")
    
    def check_documentation(self) -> None:
        """Verificar documentação"""
        print(f"\n{Color.BOLD}📚 Verificando Documentação{Color.END}")
        
        doc_files = [
            ("README.md", "Documentação principal"),
            ("docs/API.md", "Documentação da API"),
            ("docs/DEPLOY_RAILWAY.md", "Guia de deploy"),
            ("RESUMO_PROJETO.md", "Resumo do projeto"),
        ]
        
        for file_path, description in doc_files:
            self.check_file_exists(file_path, description)
    
    def check_example_data(self) -> None:
        """Verificar dados de exemplo"""
        print(f"\n{Color.BOLD}📄 Verificando Dados de Exemplo{Color.END}")
        
        if self.check_file_exists("example_clients.json", "Exemplo de dados de clientes"):
            try:
                with open("example_clients.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.total_checks += 1
                if 'clients' in data and isinstance(data['clients'], list) and len(data['clients']) > 0:
                    self.log_success(f"JSON de exemplo válido com {len(data['clients'])} clientes")
                else:
                    self.log_error("Estrutura inválida no JSON de exemplo")
                    
            except json.JSONDecodeError as e:
                self.log_error(f"JSON de exemplo inválido: {e}")
    
    def run_quick_tests(self) -> None:
        """Executar testes rápidos"""
        print(f"\n{Color.BOLD}⚡ Executando Testes Rápidos{Color.END}")
        
        self.total_checks += 1
        try:
            # Tentar executar testes unitários básicos
            result = subprocess.run([
                sys.executable, 'run_tests.py', '--unit'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_success("Testes unitários passaram")
            else:
                self.log_warning("Alguns testes unitários falharam - verifique antes do deploy")
                
        except subprocess.TimeoutExpired:
            self.log_warning("Testes levaram muito tempo - pulando")
        except FileNotFoundError:
            self.log_warning("Script de testes não encontrado - pulando")
        except Exception as e:
            self.log_warning(f"Erro ao executar testes: {e}")
    
    def generate_report(self) -> bool:
        """Gerar relatório final"""
        print(f"\n{Color.BOLD}📊 RELATÓRIO DE VALIDAÇÃO{Color.END}")
        print("=" * 60)
        
        success_rate = (self.checks_passed / self.total_checks) * 100 if self.total_checks > 0 else 0
        
        print(f"✅ Verificações passaram: {Color.GREEN}{self.checks_passed}{Color.END}")
        print(f"❌ Erros encontrados: {Color.RED}{len(self.errors)}{Color.END}")
        print(f"⚠️  Avisos: {Color.YELLOW}{len(self.warnings)}{Color.END}")
        print(f"📊 Taxa de sucesso: {Color.BLUE}{success_rate:.1f}%{Color.END}")
        
        if self.errors:
            print(f"\n{Color.RED}🚨 ERROS CRÍTICOS:{Color.END}")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
        
        if self.warnings:
            print(f"\n{Color.YELLOW}⚠️  AVISOS:{Color.END}")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # Determinar se está pronto para deploy
        is_ready = len(self.errors) == 0 and success_rate >= 80
        
        print(f"\n{'='*60}")
        if is_ready:
            print(f"{Color.GREEN}{Color.BOLD}🎉 SISTEMA PRONTO PARA DEPLOY NA RAILWAY!{Color.END}")
            print(f"{Color.GREEN}Todos os requisitos foram atendidos.{Color.END}")
        else:
            print(f"{Color.RED}{Color.BOLD}❌ SISTEMA NÃO ESTÁ PRONTO PARA DEPLOY{Color.END}")
            print(f"{Color.RED}Corrija os erros antes de fazer o deploy.{Color.END}")
        
        print(f"\n{Color.BLUE}🚀 Para fazer o deploy:{Color.END}")
        print(f"  1. railway login")
        print(f"  2. railway init")
        print(f"  3. Configure as variáveis de ambiente")
        print(f"  4. railway up")
        print(f"\n{Color.BLUE}📖 Consulte docs/DEPLOY_RAILWAY.md para instruções detalhadas{Color.END}")
        
        return is_ready

def main():
    """Função principal"""
    print(f"{Color.BOLD}🔍 VALIDADOR DE DEPLOY PARA RAILWAY{Color.END}")
    print(f"{Color.BLUE}Sistema de Cobrança Inteligente{Color.END}")
    print("=" * 60)
    
    validator = DeployValidator()
    
    # Executar todas as verificações
    validator.check_directory_structure()
    validator.check_backend_structure()
    validator.check_frontend_structure()
    validator.check_dependencies()
    validator.check_railway_config()
    validator.check_environment_variables()
    validator.check_python_syntax()
    validator.check_imports()
    validator.check_tests()
    validator.check_documentation()
    validator.check_example_data()
    validator.run_quick_tests()
    
    # Gerar relatório final
    is_ready = validator.generate_report()
    
    # Exit code baseado no resultado
    sys.exit(0 if is_ready else 1)

if __name__ == '__main__':
    main()
