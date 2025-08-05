#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar importações e identificar problemas
"""

import sys
import traceback

def test_imports():
    print("🧪 TESTE DE IMPORTAÇÕES - Claudia Cobranças")
    print("=" * 50)
    
    modules_to_test = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("playwright", "Playwright"),
        ("pandas", "Pandas"),
        ("openpyxl", "OpenPyXL"),
        ("requests", "Requests"),
        ("aiohttp", "AioHTTP"),
        ("websockets", "WebSockets"),
        ("qrcode", "QRCode"),
        ("PIL", "Pillow"),
        ("speech_recognition", "SpeechRecognition"),
        ("pydub", "Pydub"),
        ("structlog", "StructLog"),
    ]
    
    print("📦 Testando dependências principais...")
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
        except Exception as e:
            print(f"⚠️ {display_name}: {e}")
    
    print("\n🧠 Testando módulos core...")
    core_modules = [
        ("core.excel_processor", "ExcelProcessor"),
        ("core.whatsapp_client", "WhatsAppClient"),
        ("core.conversation", "SuperConversationEngine"),
        ("core.fatura_downloader", "FaturaDownloader"),
        ("core.captcha_solver", "CaptchaSolver"),
        ("core.storage_manager", "StorageManager"),
        ("core.logger", "Logger"),
    ]
    
    for module_name, display_name in core_modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
        except Exception as e:
            print(f"⚠️ {display_name}: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
    
    print("\n🚀 Testando aplicação principal...")
    try:
        from app import app
        print("✅ App principal")
    except Exception as e:
        print(f"❌ App principal: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    print("\n🎭 Testando Playwright especificamente...")
    try:
        from playwright.async_api import async_playwright
        print("✅ Playwright async_api")
    except Exception as e:
        print(f"❌ Playwright async_api: {e}")
    
    try:
        import subprocess
        result = subprocess.run(["playwright", "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Playwright CLI: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Playwright CLI: {e}")
    
    print("\n📊 RESUMO:")
    print("=" * 50)
    print("✅ Teste de importações concluído")
    print("🔍 Verifique os erros acima para identificar problemas")

if __name__ == "__main__":
    test_imports() 