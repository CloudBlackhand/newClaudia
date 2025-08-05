#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway Start Script - Blacktemplar Bolter
Inicialização otimizada para Railway com controle de recursos
"""

import os
import asyncio
import uvicorn
from app import app

def start_railway():
    """Inicialização otimizada para Railway"""
    port = int(os.environ.get("PORT", 8000))
    
    print("🚂 Iniciando Blacktemplar Bolter na Railway...")
    print(f"📡 Porta: {port}")
    print(f"🔧 Modo Railway: {os.getenv('RAILWAY_DEPLOY', 'False')}")
    
    # Configurações conservadoras para Railway
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        workers=1,  # Apenas 1 worker para economizar RAM
        loop="asyncio",
        access_log=False,  # Reduzir I/O
        log_level="warning"  # Menos logs = menos custos
    )

if __name__ == "__main__":
    start_railway()