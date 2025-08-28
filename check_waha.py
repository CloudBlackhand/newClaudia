#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Status do WAHA - Claudia Cobranças
Script para testar se o WAHA está funcionando
"""

import requests
import os
import sys

def check_waha_status():
    """Verificar se o WAHA está funcionando"""
    
    # URL do WAHA
    waha_url = os.getenv('WAHA_URL', 'https://waha-claudia.up.railway.app')
    
    print(f"🔍 Verificando WAHA em: {waha_url}")
    
    try:
        # Testar endpoint básico
        response = requests.get(f"{waha_url}/api/instances", timeout=10)
        
        if response.status_code == 200:
            print("✅ WAHA está funcionando!")
            print(f"📊 Status Code: {response.status_code}")
            
            # Tentar obter informações das instâncias
            try:
                instances = response.json()
                print(f"📱 Instâncias encontradas: {len(instances.get('instances', []))}")
                
                for instance in instances.get('instances', []):
                    print(f"   - {instance.get('instanceName', 'N/A')}: {instance.get('status', 'N/A')}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao parsear resposta: {e}")
                
            return True
        else:
            print(f"❌ WAHA respondeu com status: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: WAHA não está acessível")
        print("💡 Verifique se o WAHA está deployado no Railway")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ Timeout: WAHA demorou muito para responder")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_waha_connection():
    """Testar conexão completa com WAHA"""
    
    waha_url = os.getenv('WAHA_URL', 'https://waha-claudia.up.railway.app')
    
    print(f"\n🧪 Testando conexão completa...")
    
    try:
        # Testar criação de instância
        instance_data = {
            "instanceName": "test-claudia",
            "webhook": f"{waha_url}/webhook",
            "webhookByEvents": False,
            "webhookBase64": False
        }
        
        response = requests.post(
            f"{waha_url}/api/instances/create",
            json=instance_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Instância criada com sucesso!")
            
            # Iniciar instância
            start_response = requests.post(
                f"{waha_url}/api/instances/test-claudia/start",
                timeout=10
            )
            
            if start_response.status_code == 200:
                print("✅ Instância iniciada com sucesso!")
                
                # Verificar status
                info_response = requests.get(
                    f"{waha_url}/api/instances/test-claudia/info",
                    timeout=10
                )
                
                if info_response.status_code == 200:
                    info = info_response.json()
                    print(f"📊 Status da instância: {info.get('status', 'N/A')}")
                    
                # Limpar instância de teste
                requests.delete(f"{waha_url}/api/instances/test-claudia")
                print("🧹 Instância de teste removida")
                
            else:
                print(f"❌ Erro ao iniciar instância: {start_response.status_code}")
                
        else:
            print(f"❌ Erro ao criar instância: {response.status_code}")
            print(f"📄 Resposta: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Erro no teste de conexão: {e}")

def main():
    """Função principal"""
    print("🚀 VERIFICADOR WAHA - CLAUDIA COBRANÇAS")
    print("=" * 50)
    
    # Verificar status básico
    if check_waha_status():
        # Se WAHA está funcionando, testar conexão completa
        test_waha_connection()
    else:
        print("\n💡 SOLUÇÕES:")
        print("1. Verifique se o WAHA está deployado no Railway")
        print("2. Confirme a URL: https://waha-claudia.up.railway.app")
        print("3. Verifique as variáveis de ambiente")
        print("4. Aguarde alguns minutos após o deploy")
    
    print("\n✅ Verificação concluída!")

if __name__ == "__main__":
    main()
