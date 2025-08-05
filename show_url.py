#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mostrar a URL do Railway
"""

import os

def main():
    print("🌐 CLAUDIA COBRANÇAS - URL DO RAILWAY")
    print("=" * 50)
    
    # Verificar variáveis de ambiente do Railway
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    railway_url = os.getenv('RAILWAY_URL')
    port = os.getenv('PORT', '8000')
    
    print(f"🔍 Verificando variáveis de ambiente...")
    print(f"   RAILWAY_PUBLIC_DOMAIN: {railway_domain}")
    print(f"   RAILWAY_URL: {railway_url}")
    print(f"   PORT: {port}")
    
    if railway_domain:
        base_url = f"https://{railway_domain}"
        print(f"\n✅ URL ENCONTRADA!")
        print(f"🌐 URL Base: {base_url}")
        print(f"🔐 Login: {base_url}/login")
        print(f"📊 Dashboard: {base_url}/dashboard")
        print(f"🏠 Página Principal: {base_url}/")
    elif railway_url:
        print(f"\n✅ URL ENCONTRADA!")
        print(f"🌐 URL Base: {railway_url}")
        print(f"🔐 Login: {railway_url}/login")
        print(f"📊 Dashboard: {railway_url}/dashboard")
        print(f"🏠 Página Principal: {railway_url}/")
    else:
        print(f"\n⚠️ URL não encontrada nas variáveis de ambiente")
        print(f"💡 Verifique o painel do Railway em: https://railway.app")
        print(f"🔍 Procure por 'Domains' ou 'Settings' no seu projeto")
    
    print(f"\n📋 ROTAS DISPONÍVEIS:")
    print(f"   / - Página principal")
    print(f"   /login - Sistema de login")
    print(f"   /dashboard - Painel de controle")
    print(f"   /api/auth/approve/{'{request_id}'} - Aprovar login")
    print(f"   /api/auth/deny/{'{request_id}'} - Negar login")
    
    print(f"\n🎯 PRÓXIMOS PASSOS:")
    print(f"1. Acesse a URL encontrada acima")
    print(f"2. Vá para /login")
    print(f"3. Tente fazer login")
    print(f"4. Aprove o login no terminal")
    print(f"5. Acesse o dashboard")

if __name__ == "__main__":
    main() 