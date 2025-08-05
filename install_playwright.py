#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para instalar Playwright no Railway
"""

import subprocess
import sys
import os

def main():
    print("🎭 INSTALANDO PLAYWRIGHT NO RAILWAY")
    print("=" * 50)
    
    try:
        # Instalar playwright via pip
        print("📦 Instalando Playwright...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
        print("✅ Playwright instalado")
        
        # Instalar browsers
        print("🌐 Instalando browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("✅ Chromium instalado")
        
        # Verificar instalação
        print("🔍 Verificando instalação...")
        result = subprocess.run([sys.executable, "-m", "playwright", "install", "--dry-run"], 
                              capture_output=True, text=True)
        
        if "chromium" in result.stdout:
            print("✅ Playwright configurado corretamente")
            return True
        else:
            print("❌ Erro na verificação")
            return False
            
    except Exception as e:
        print(f"❌ Erro na instalação: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 