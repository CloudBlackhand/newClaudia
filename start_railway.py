#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Cobrança Inteligente
Versão otimizada para Railway
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_environment():
    """Configurar ambiente de execução"""
    # Criar diretórios necessários
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    
    # Verificar variáveis de ambiente obrigatórias
    required_vars = ['SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Variáveis de ambiente obrigatórias não encontradas: {missing_vars}")
        return False
    
    return True

def main():
    """Função principal de inicialização"""
    logger.info("🚀 Iniciando Sistema de Cobrança Inteligente...")
    
    if not setup_environment():
        logger.error("❌ Falha na configuração do ambiente")
        sys.exit(1)
    
    try:
        # Configurar path para importações
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        
        logger.info(f"📁 Diretório atual: {current_dir}")
        logger.info(f"📁 Conteúdo: {os.listdir(current_dir)}")
        
        if 'backend' in os.listdir(current_dir):
            logger.info("✅ Diretório backend encontrado")
            logger.info(f"📁 Conteúdo backend: {os.listdir('backend')}")
        else:
            logger.error("❌ Diretório backend não encontrado")
            return
        
        # Importar e inicializar a aplicação
        from backend.app import create_app
        
        app = create_app()
        
        # Configurações do servidor
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"🌐 Servidor iniciando em http://{host}:{port}")
        logger.info(f"🔧 Modo debug: {debug}")
        
        # Iniciar servidor
        if os.getenv('RAILWAY_ENVIRONMENT'):
            # Usar Gunicorn no Railway
            import gunicorn.app.wsgiapp as wsgi
            sys.argv = [
                'gunicorn',
                '--bind', f'{host}:{port}',
                '--workers', '2',
                '--worker-class', 'sync',
                '--timeout', '120',
                '--access-logfile', '-',
                '--error-logfile', '-',
                'backend.app:create_app()'
            ]
            wsgi.run()
        else:
            # Usar Flask dev server localmente
            app.run(host=host, port=port, debug=debug)
            
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar aplicação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
