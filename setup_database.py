#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para configurar o banco de dados no Railway
Execute este script após o deploy para inicializar toda a infraestrutura
"""

import os
import sys
from pathlib import Path

def main():
    """Script principal de configuração"""
    print("🚀 CONFIGURANDO INFRAESTRUTURA CLAUDIA NO RAILWAY")
    print("=" * 60)
    
    # Verificar se estamos no Railway
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        print("⚠️  Este script deve ser executado no ambiente Railway")
        print("   Execute: railway run python setup_database.py")
        return False
    
    print(f"✅ Ambiente Railway detectado: {os.getenv('RAILWAY_ENVIRONMENT')}")
    
    # Verificar variáveis de ambiente
    required_vars = ['DATABASE_URL', 'REDIS_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing_vars)}")
        print("   Configure-as no painel do Railway antes de continuar")
        return False
    
    print("✅ Todas as variáveis de ambiente configuradas")
    
    # Executar inicialização do banco
    try:
        from backend.database.init_database import main as init_db
        print("\n🔧 Inicializando banco de dados...")
        success = init_db()
        
        if success:
            print("\n🎉 INFRAESTRUTURA CONFIGURADA COM SUCESSO!")
            print("✅ PostgreSQL com todas as tabelas criadas")
            print("✅ Redis com estruturas de cache configuradas")
            print("✅ Sistema pronto para processar campanhas")
            print("✅ IA funcionando com persistência de dados")
            
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. Teste a IA: /api/conversation/process-message")
            print("2. Crie uma campanha: /api/campaigns/process")
            print("3. Use seu arquivo JSON de cruzamento")
            print("4. Dispare mensagens em massa!")
            
            return True
        else:
            print("❌ Falha na inicialização do banco de dados")
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("   Certifique-se de que todas as dependências estão instaladas")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
