#!/usr/bin/env python3
"""
Script de inicialização simplificado para Railway
"""
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar ambiente para Railway"""
    # Adicionar backend ao PYTHONPATH
    backend_path = os.path.join(os.getcwd(), 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    # Definir PYTHONPATH
    os.environ['PYTHONPATH'] = backend_path
    
    # Configurações padrão
    os.environ.setdefault('ENVIRONMENT', 'production')
    os.environ.setdefault('SECRET_KEY', 'railway-default-key-change-me')
    os.environ.setdefault('LOG_LEVEL', 'INFO')

def main():
    """Função principal"""
    logger.info("🚀 Iniciando Sistema de Cobrança Avançado na Railway...")
    
    # Configurar ambiente
    setup_environment()
    
    try:
        import uvicorn
        from backend.app import app
        
        # Obter porta do ambiente (Railway define automaticamente)
        port = int(os.environ.get("PORT", 8000))
        
        logger.info(f"🌐 Servidor iniciando na porta {port}")
        
        # Iniciar servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {e}")
        # Tentar importação alternativa
        try:
            import uvicorn
            uvicorn.run(
                "backend.app:app",
                host="0.0.0.0",
                port=int(os.environ.get("PORT", 8000)),
                log_level="info"
            )
        except Exception as e2:
            logger.error(f"❌ Erro crítico: {e2}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
