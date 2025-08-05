#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Playwright para Railway
"""

import asyncio
import sys
import os
import subprocess

async def test_playwright():
    """Testar se o Playwright está funcionando"""
    print("🎭 TESTE DO PLAYWRIGHT")
    print("=" * 40)
    
    try:
        # Testar import
        print("📦 Testando import do Playwright...")
        from playwright.async_api import async_playwright
        print("✅ Playwright importado com sucesso")
        
        # Testar inicialização
        print("🚀 Testando inicialização...")
        playwright = await async_playwright().start()
        print("✅ Playwright inicializado")
        
        # Testar navegador
        print("🌐 Testando navegador...")
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        print("✅ Navegador Chromium inicializado")
        
        # Testar página
        print("📄 Testando página...")
        page = await browser.new_page()
        await page.goto('https://www.google.com')
        title = await page.title()
        print(f"✅ Página carregada: {title}")
        
        # Fechar
        await browser.close()
        await playwright.stop()
        print("✅ Playwright fechado corretamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def install_playwright():
    """Instalar Playwright se necessário"""
    print("🔧 Instalando Playwright...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        print("✅ Playwright instalado")
        
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Chromium instalado")
        
        return True
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False

async def main():
    """Função principal"""
    print("🧪 TESTE COMPLETO DO PLAYWRIGHT")
    print("=" * 50)
    
    # Verificar se Playwright está instalado
    try:
        import playwright
        print("✅ Playwright já instalado")
    except ImportError:
        print("📦 Playwright não encontrado, instalando...")
        if not install_playwright():
            print("❌ Falha na instalação")
            return False
    
    # Executar teste
    success = await test_playwright()
    
    if success:
        print("\n🎉 TESTE PASSOU!")
        print("✅ Playwright está funcionando corretamente")
        return True
    else:
        print("\n❌ TESTE FALHOU!")
        print("❌ Playwright não está funcionando")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 