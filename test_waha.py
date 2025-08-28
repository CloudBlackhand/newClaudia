#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da Integração WAHA - Claudia Cobranças
Script para testar a conexão com WAHA
"""

import asyncio
import os
import sys
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_waha_connection():
    """Testar conexão com WAHA"""
    try:
        from core.whatsapp_client import WAHAWhatsAppClient
        
        # Configurar URL do WAHA
        waha_url = os.getenv('WAHA_URL', 'http://localhost:3000')
        logger.info(f"🔗 Testando conexão com WAHA: {waha_url}")
        
        # Criar cliente
        client = WAHAWhatsAppClient(waha_url)
        
        # Inicializar
        qr_code = await client.initialize()
        
        if qr_code == "CONNECTED":
            logger.info("✅ WAHA já conectado!")
            return True
        elif qr_code:
            logger.info("📱 QR Code gerado - escaneie para conectar")
            logger.info(f"QR Code: {qr_code[:100]}...")
            return True
        else:
            logger.error("❌ Falha ao inicializar WAHA")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste WAHA: {e}")
        return False

async def test_waha_send_message():
    """Testar envio de mensagem via WAHA"""
    try:
        from core.whatsapp_client import WAHAWhatsAppClient
        
        client = WAHAWhatsAppClient()
        
        # Verificar conexão
        if not await client.check_connection():
            logger.error("❌ WAHA não conectado")
            return False
        
        # Testar envio
        test_phone = "5511999999999"  # Número de teste
        test_message = "🧪 Teste da Claudia Cobranças via WAHA!"
        
        success = await client.send_message(test_phone, test_message)
        
        if success:
            logger.info("✅ Mensagem de teste enviada com sucesso!")
            return True
        else:
            logger.error("❌ Falha ao enviar mensagem de teste")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro no teste de envio: {e}")
        return False

async def main():
    """Função principal de teste"""
    logger.info("🧪 INICIANDO TESTES WAHA - CLAUDIA COBRANÇAS")
    
    # Teste 1: Conexão
    logger.info("\n🔗 TESTE 1: Conexão WAHA")
    connection_ok = await test_waha_connection()
    
    if connection_ok:
        # Teste 2: Envio de mensagem
        logger.info("\n📤 TESTE 2: Envio de mensagem")
        await test_waha_send_message()
    
    logger.info("\n✅ Testes WAHA concluídos!")

if __name__ == "__main__":
    asyncio.run(main())
