#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar e configurar a conexão com Waha
Verifica se o WhatsApp está funcionando e configura a sessão
"""

import asyncio
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from backend.modules.waha_integration import WahaIntegration, SessionStatus

async def test_waha_connection():
    """Testar conexão com Waha"""
    print("🚀 TESTANDO CONEXÃO COM WAHA")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    waha_url = os.getenv('WAHA_BASE_URL', 'https://waha-production-e3dd.up.railway.app')
    session_name = os.getenv('WAHA_SESSION_NAME', 'claudia-cobrancas')
    
    print(f"✅ URL do Waha: {waha_url}")
    print(f"✅ Nome da sessão: {session_name}")
    
    # Criar instância do Waha
    waha = WahaIntegration(waha_url, session_name)
    
    try:
        # 1. Testar health check
        print("\n🔍 Testando health check...")
        health_ok = await waha.health_check()
        if health_ok:
            print("✅ Waha está funcionando!")
        else:
            print("❌ Waha não está respondendo")
            return False
        
        # 2. Verificar status da sessão
        print(f"\n🔍 Verificando status da sessão '{session_name}'...")
        status = await waha.get_session_status(force_refresh=True)
        
        if status:
            print(f"✅ Status da sessão: {status.value}")
            
            if status == SessionStatus.STOPPED:
                print("🔄 Iniciando sessão do WhatsApp...")
                started = await waha.start_whatsapp_session()
                if started:
                    print("✅ Sessão iniciada com sucesso!")
                    # Aguardar um pouco e verificar novamente
                    await asyncio.sleep(3)
                    status = await waha.get_session_status(force_refresh=True)
                    print(f"✅ Novo status: {status.value if status else 'Desconhecido'}")
                else:
                    print("❌ Falha ao iniciar sessão")
                    return False
            
            elif status == SessionStatus.SCAN_QR_CODE:
                print("📱 QR Code necessário para autenticação")
                qr_code = await waha.get_qr_code()
                if qr_code:
                    print("✅ QR Code obtido!")
                    print("📱 Escaneie o QR Code com seu WhatsApp:")
                    print(f"🔗 {qr_code}")
                    print("\n⏳ Aguardando autenticação...")
                    print("   (Aguarde até que o status mude para 'WORKING')")
                else:
                    print("❌ Não foi possível obter QR Code")
                    return False
            
            elif status == SessionStatus.WORKING:
                print("✅ WhatsApp está funcionando e pronto para enviar mensagens!")
                return True
            
            elif status == SessionStatus.FAILED:
                print("❌ Sessão falhou. Tentando reiniciar...")
                await waha.stop_whatsapp_session()
                await asyncio.sleep(2)
                started = await waha.start_whatsapp_session()
                if started:
                    print("✅ Sessão reiniciada!")
                else:
                    print("❌ Falha ao reiniciar sessão")
                    return False
            
            else:
                print(f"⚠️  Status desconhecido: {status.value}")
                return False
        else:
            print("❌ Não foi possível obter status da sessão")
            return False
        
        # 3. Testar envio de mensagem (opcional)
        test_phone = input("\n📱 Digite um número para testar envio (ou Enter para pular): ").strip()
        if test_phone:
            print(f"📤 Enviando mensagem de teste para {test_phone}...")
            test_message = "🤖 Teste de conexão - Sistema Claudia funcionando!"
            sent = await waha.send_text_message(test_phone, test_message)
            if sent:
                print("✅ Mensagem de teste enviada com sucesso!")
            else:
                print("❌ Falha ao enviar mensagem de teste")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        return False
    
    finally:
        await waha.close_session()

async def main():
    """Função principal"""
    print("🎯 CONFIGURAÇÃO DO WAHA PARA CLAUDIA")
    print("=" * 60)
    
    # Verificar se estamos no Railway
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        print("⚠️  Este script deve ser executado no ambiente Railway")
        print("   Execute: railway run python test_waha_connection.py")
        return False
    
    print(f"✅ Ambiente Railway detectado: {os.getenv('RAILWAY_ENVIRONMENT')}")
    
    # Executar teste
    success = await test_waha_connection()
    
    if success:
        print("\n🎉 CONFIGURAÇÃO COMPLETA!")
        print("✅ Waha conectado e funcionando")
        print("✅ Sessão WhatsApp configurada")
        print("✅ Sistema pronto para enviar mensagens")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("1. A Claudia agora pode enviar mensagens via WhatsApp")
        print("2. Use /api/campaigns/process para criar campanhas")
        print("3. Processe seu arquivo JSON de cruzamento")
        print("4. Dispare mensagens em massa!")
        
        return True
    else:
        print("\n❌ FALHA NA CONFIGURAÇÃO")
        print("Verifique os logs e tente novamente")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
