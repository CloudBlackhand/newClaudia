#!/usr/bin/env python3
"""
Script para executar testes automatizados
"""
import subprocess
import sys
import os

def run_tests():
    """Executar todos os testes"""
    print("🧪 Executando testes automatizados...")
    
    # Adicionar backend ao PYTHONPATH
    backend_path = os.path.join(os.getcwd(), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    try:
        # Executar pytest
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--asyncio-mode=auto'
        ], capture_output=True, text=True)
        
        print("📊 Resultado dos testes:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Avisos/Erros:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Todos os testes passaram!")
        else:
            print("❌ Alguns testes falharam!")
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ pytest não encontrado. Instale com: pip install pytest pytest-asyncio")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
