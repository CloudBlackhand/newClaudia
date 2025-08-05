#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Dependências - Claudia Cobranças
"""

import sys

def test_dependencies():
    """Testar todas as dependências"""
    print("🧪 TESTE DE DEPENDÊNCIAS")
    print("=" * 40)
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("playwright", "Playwright"),
        ("pandas", "Pandas"),
        ("openpyxl", "OpenPyXL"),
        ("speech_recognition", "SpeechRecognition"),
        ("requests", "Requests"),
        ("structlog", "StructLog"),
        ("python_dateutil", "DateUtil"),
        ("python_dotenv", "DotEnv"),
        ("jinja2", "Jinja2"),
        ("aiohttp", "AioHTTP"),
        ("websockets", "WebSockets"),
        ("qrcode", "QRCode"),
        ("PIL", "Pillow")
    ]
    
    results = []
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
            results.append(True)
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            results.append(False)
    
    print(f"\n📊 RESULTADO: {sum(results)}/{len(results)} dependências OK")
    
    if all(results):
        print("🎉 TODAS AS DEPENDÊNCIAS FUNCIONANDO!")
        return True
    else:
        print("❌ ALGUMAS DEPENDÊNCIAS FALTANDO!")
        return False

if __name__ == "__main__":
    success = test_dependencies()
    sys.exit(0 if success else 1) 