#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para executar testes do sistema
"""

import subprocess
import sys
import argparse
import os
from pathlib import Path

def run_command(cmd, description):
    """Executar comando e exibir resultado"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCESSO")
        else:
            print(f"❌ {description} - FALHOU")
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar {description}: {e}")
        return False

def check_requirements():
    """Verificar se as dependências estão instaladas"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'pytest',
        'pytest-cov',
        'flask',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Pacotes ausentes: {', '.join(missing_packages)}")
        print("💡 Instale com: pip install -r requirements.txt")
        return False
    
    print("✅ Todas as dependências estão instaladas")
    return True

def run_unit_tests():
    """Executar testes unitários"""
    cmd = "python -m pytest tests/ -m unit -v --tb=short"
    return run_command(cmd, "Executando testes unitários")

def run_integration_tests():
    """Executar testes de integração"""
    cmd = "python -m pytest tests/ -m integration -v --tb=short"
    return run_command(cmd, "Executando testes de integração")

def run_api_tests():
    """Executar testes de API"""
    cmd = "python -m pytest tests/ -m api -v --tb=short"
    return run_command(cmd, "Executando testes de API")

def run_all_tests():
    """Executar todos os testes"""
    cmd = "python -m pytest tests/ -v --tb=short"
    return run_command(cmd, "Executando todos os testes")

def run_coverage_tests():
    """Executar testes com cobertura"""
    cmd = "python -m pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing -v"
    return run_command(cmd, "Executando testes com análise de cobertura")

def run_specific_module(module):
    """Executar testes de um módulo específico"""
    cmd = f"python -m pytest tests/test_{module}.py -v --tb=short"
    return run_command(cmd, f"Executando testes do módulo {module}")

def run_linting():
    """Executar análise de código"""
    print("\n🔍 Executando análise de código...")
    
    # Verificar se existe configuração do flake8
    flake8_config = Path(".flake8")
    if not flake8_config.exists():
        create_flake8_config()
    
    # Executar flake8
    cmd = "python -m flake8 backend/ tests/ --count --statistics"
    flake8_result = run_command(cmd, "Análise de estilo (flake8)")
    
    return flake8_result

def create_flake8_config():
    """Criar configuração básica do flake8"""
    config_content = """[flake8]
max-line-length = 120
exclude = 
    .git,
    __pycache__,
    .pytest_cache,
    .coverage,
    htmlcov,
    dist,
    build,
    *.egg-info
ignore = 
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
    F401,  # imported but unused (comum em __init__.py)
per-file-ignores =
    __init__.py:F401
"""
    
    with open(".flake8", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    print("📝 Configuração do flake8 criada")

def run_security_check():
    """Executar verificação de segurança"""
    print("\n🔒 Executando verificações de segurança...")
    
    # Verificar se bandit está disponível
    try:
        import bandit
        cmd = "python -m bandit -r backend/ -f json -o security_report.json"
        result = run_command(cmd, "Análise de segurança (bandit)")
        
        if result:
            print("📄 Relatório de segurança salvo em: security_report.json")
        
        return result
        
    except ImportError:
        print("⚠️  Bandit não instalado - pulando verificação de segurança")
        print("💡 Instale com: pip install bandit")
        return True

def generate_test_report():
    """Gerar relatório de testes"""
    print("\n📊 Gerando relatório de testes...")
    
    cmd = "python -m pytest tests/ --html=test_report.html --self-contained-html --tb=short"
    result = run_command(cmd, "Gerando relatório HTML")
    
    if result:
        print("📄 Relatório HTML salvo em: test_report.html")
    
    return result

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executar testes do Sistema de Cobrança Inteligente")
    parser.add_argument('--unit', action='store_true', help='Executar apenas testes unitários')
    parser.add_argument('--integration', action='store_true', help='Executar apenas testes de integração')
    parser.add_argument('--api', action='store_true', help='Executar apenas testes de API')
    parser.add_argument('--coverage', action='store_true', help='Executar testes com cobertura')
    parser.add_argument('--lint', action='store_true', help='Executar análise de código')
    parser.add_argument('--security', action='store_true', help='Executar verificação de segurança')
    parser.add_argument('--report', action='store_true', help='Gerar relatório HTML')
    parser.add_argument('--module', type=str, help='Executar testes de um módulo específico')
    parser.add_argument('--all', action='store_true', help='Executar todos os testes e verificações')
    
    args = parser.parse_args()
    
    print("🚀 Sistema de Testes - Sistema de Cobrança Inteligente")
    print("=" * 60)
    
    # Verificar dependências
    if not check_requirements():
        sys.exit(1)
    
    # Verificar se estamos no diretório correto
    if not Path("backend").exists() or not Path("tests").exists():
        print("❌ Execute este script a partir do diretório raiz do projeto")
        sys.exit(1)
    
    results = []
    
    # Executar testes baseado nos argumentos
    if args.unit:
        results.append(run_unit_tests())
    elif args.integration:
        results.append(run_integration_tests())
    elif args.api:
        results.append(run_api_tests())
    elif args.coverage:
        results.append(run_coverage_tests())
    elif args.module:
        results.append(run_specific_module(args.module))
    elif args.all:
        results.extend([
            run_all_tests(),
            run_linting(),
            run_security_check(),
            run_coverage_tests()
        ])
    else:
        # Padrão: executar todos os testes
        results.append(run_all_tests())
    
    # Executar verificações adicionais se solicitadas
    if args.lint or args.all:
        results.append(run_linting())
    
    if args.security or args.all:
        results.append(run_security_check())
    
    if args.report or args.all:
        results.append(generate_test_report())
    
    # Resumo final
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    total_tests = len(results)
    successful_tests = sum(results)
    failed_tests = total_tests - successful_tests
    
    if failed_tests == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
        exit_code = 0
    else:
        print(f"❌ {failed_tests} de {total_tests} verificações falharam")
        exit_code = 1
    
    print(f"✅ Sucessos: {successful_tests}")
    print(f"❌ Falhas: {failed_tests}")
    print(f"📊 Taxa de sucesso: {(successful_tests/total_tests)*100:.1f}%")
    
    # Dicas para melhorar
    if failed_tests > 0:
        print("\n💡 DICAS PARA CORRIGIR:")
        print("  • Verifique os logs de erro acima")
        print("  • Execute testes específicos: python run_tests.py --module <nome_modulo>")
        print("  • Verifique a cobertura: python run_tests.py --coverage")
        print("  • Analise o código: python run_tests.py --lint")
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
