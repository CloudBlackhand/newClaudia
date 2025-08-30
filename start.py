#!/usr/bin/env python3
"""
Script de inicialização do Sistema de Cobrança Avançado
"""
import os
import sys
import subprocess

def main():
    """Função principal de inicialização"""
    print("🚀 Iniciando Sistema de Cobrança Avançado...")
    
    # Verificar se está no diretório correto
    if not os.path.exists("backend/app.py"):
        print("❌ Execute este script no diretório raiz do projeto")
        sys.exit(1)
    
    # Verificar se as dependências estão instaladas
    try:
        import fastapi
        import uvicorn
        print("✅ Dependências verificadas")
    except ImportError:
        print("📦 Instalando dependências...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Configurar PYTHONPATH
    backend_path = os.path.join(os.getcwd(), "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    # Definir variáveis de ambiente padrão se não existirem
    env_defaults = {
        "PORT": "8000",
        "HOST": "0.0.0.0", 
        "SECRET_KEY": "dev-secret-key-change-in-production",
        "LOG_LEVEL": "INFO",
        "ENVIRONMENT": "development"
    }
    
    for key, value in env_defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print(f"🌐 Servidor será iniciado em http://localhost:{os.environ['PORT']}")
    print("📖 Documentação da API: http://localhost:8000/docs")
    print("🎨 Interface Web: http://localhost:8000/")
    print("\n⚡ Iniciando servidor...")
    
    # Iniciar servidor
    try:
        import uvicorn
        uvicorn.run(
            "backend.app:app",
            host=os.environ.get("HOST", "0.0.0.0"),
            port=int(os.environ.get("PORT", 8000)),
            reload=True,
            log_level=os.environ.get("LOG_LEVEL", "info").lower()
        )
    except KeyboardInterrupt:
        print("\n👋 Sistema finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
