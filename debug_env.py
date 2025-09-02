#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para depurar variáveis de ambiente
"""

import os
import sys
import json
# Não usar dotenv para simplificar

def print_header(title):
    """Imprimir cabeçalho"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_env_var(name, value=None):
    """Imprimir variável de ambiente"""
    if value is None:
        value = os.getenv(name, "NÃO DEFINIDO")
    
    print(f"{name:30} = {value}")

def main():
    """Função principal"""
    print_header("INFORMAÇÕES DO SISTEMA")
    print(f"Python: {sys.version}")
    print(f"Diretório atual: {os.getcwd()}")
    
    print_header("VARIÁVEIS DE AMBIENTE WAHA")
    print_env_var("WAHA_BASE_URL")
    print_env_var("WAHA_SESSION_NAME")
    print_env_var("WAHA_WEBHOOK_URL")
    print_env_var("WAHA_API_KEY")
    
    print_header("VARIÁVEIS DE AMBIENTE WHATSAPP")
    print_env_var("WHATSAPP_API_KEY")
    print_env_var("WHATSAPP_DEFAULT_ENGINE")
    print_env_var("WHATSAPP_HOOK_EVENTS")
    print_env_var("WHATSAPP_HOOK_URL")
    print_env_var("WHATSAPP_START_SESSION")
    
    print_header("VARIÁVEIS DE AMBIENTE RAILWAY")
    print_env_var("RAILWAY_ENVIRONMENT")
    print_env_var("RAILWAY_PUBLIC_DOMAIN")
    print_env_var("RAILWAY_SERVICE_WAHAWA_URL")
    
    print_header("OUTRAS VARIÁVEIS DE AMBIENTE")
    print_env_var("API_KEY")
    print_env_var("DEBUG")
    print_env_var("SECRET_KEY")
    
    print_header("TESTE DE IMPORTAÇÃO DO CONFIG")
    try:
        from backend.config.settings import Config
        print("✅ Importação do Config bem-sucedida")
        print(f"WAHA_BASE_URL (Config): {Config.WAHA_BASE_URL}")
        print(f"WAHA_SESSION_NAME (Config): {Config.WAHA_SESSION_NAME}")
        print(f"WAHA_API_KEY (Config): {'*' * len(Config.WAHA_API_KEY) if Config.WAHA_API_KEY else 'NÃO DEFINIDO'}")
        
        print("\nConfigurações do Waha:")
        print(json.dumps(Config.get_waha_config(), indent=2))
    except Exception as e:
        print(f"❌ Erro ao importar Config: {e}")

if __name__ == "__main__":
    main()
