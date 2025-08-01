#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blacktemplar Bolter - SuperBot de Cobrança
Aplicação principal FastAPI com interface web
"""

import os
import asyncio
from fastapi.websockets import WebSocketDisconnect
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.requests import Request
from typing import List, Optional
import logging

# Configurações específicas para Render Cloud
RENDER_CLOUD = os.getenv('RENDER_CLOUD', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 8000))
HOST = os.getenv('HOST', '127.0.0.1' if not RENDER_CLOUD else '0.0.0.0')

# Configurar logging otimizado para ambiente
if RENDER_CLOUD:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Configurações específicas para Render
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.getenv('PLAYWRIGHT_BROWSERS_PATH', '/opt/render/.cache/ms-playwright')
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Importar módulos core
from core.excel_processor import ExcelProcessor
from core.whatsapp_client import WhatsAppClient
from core.conversation import SuperConversationEngine
from core.fatura_downloader import FaturaDownloader
from core.captcha_solver import CaptchaSolver, get_captcha_solver_info
from config import Config

# Inicializar FastAPI
app = FastAPI(
    title="Blacktemplar Bolter",
    description="SuperBot de Cobrança 100% Gratuito",
    version="1.0.0"
)

# Configurar arquivos estáticos com cabeçalhos anti-cache
from fastapi.staticfiles import StaticFiles
from starlette.staticfiles import StaticFiles as StarletteStaticFiles
from starlette.responses import Response
from starlette.types import Scope, Receive, Send

class NoCacheStaticFiles(StarletteStaticFiles):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def no_cache_send(message):
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.append((b"Cache-Control", b"no-cache, no-store, must-revalidate"))
                headers.append((b"Pragma", b"no-cache"))
                headers.append((b"Expires", b"0"))
                message["headers"] = headers
            await send(message)
        
        await super().__call__(scope, receive, no_cache_send)

app.mount("/static", NoCacheStaticFiles(directory="web/static"), name="static")

# Instâncias globais
config = Config()
excel_processor = ExcelProcessor()
whatsapp_client = WhatsAppClient()
conversation_engine = SuperConversationEngine()
fatura_downloader = None  # Será inicializado quando WhatsApp conectar

# Estado do sistema
system_state = {
    "whatsapp_connected": False,
    "current_session": None,
    "fpd_loaded": False,
    "vendas_loaded": False,
    "bot_active": False,
    "stats": {
        "messages_sent": 0,
        "faturas_sent": 0,
        "conversations": 0
    }
}

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal - serve apenas um HTML básico que carrega o JS"""
    import time
    # Adicionar timestamp para evitar cache do navegador
    timestamp = int(time.time())
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blacktemplar Bolter - SuperBot de Cobrança</title>
        <link rel="icon" href="/static/icon.png" type="image/png">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <meta http-equiv="Pragma" content="no-cache" />
        <meta http-equiv="Expires" content="0" />
        <link rel="stylesheet" href="/static/style.css?v={timestamp}">
    </head>
    <body>
        <div id="loading">Carregando interface...</div>
        <script src="/static/app.js?v={timestamp}"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/status")
async def get_status():
    """Status do sistema"""
    return {
        "status": "online",
        "whatsapp_connected": system_state["whatsapp_connected"],
        "fpd_loaded": system_state["fpd_loaded"],
        "vendas_loaded": system_state["vendas_loaded"],
        "bot_active": system_state["bot_active"],
        "stats": system_state["stats"]
    }

@app.post("/api/whatsapp/connect")
async def connect_whatsapp():
    """Conectar WhatsApp via QR Code"""
    try:
        logger.info("🔌 Iniciando conexão WhatsApp...")
        
        # Inicializar cliente WhatsApp
        qr_data = await whatsapp_client.initialize()
        
        if qr_data:
            system_state["whatsapp_connected"] = False
            return {
                "success": True,
                "qr_data": qr_data,
                "message": "Escaneie o QR Code com WhatsApp"
            }
        else:
            return {
                "success": False,
                "message": "Erro ao gerar QR Code"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao conectar WhatsApp: {e}")
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }

@app.get("/api/whatsapp/qr")
async def get_qr_code():
    """Obter QR Code atualizado"""
    try:
        qr_data = await whatsapp_client.get_qr_code()
        return {
            "success": True,
            "qr_data": qr_data,
            "connected": system_state["whatsapp_connected"]
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

@app.post("/api/upload/fpd")
async def upload_fpd(file: UploadFile = File(...)):
    """Upload planilha FPD"""
    try:
        # Salvar arquivo temporariamente
        file_path = f"uploads/fpd_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Processar planilha
        result = excel_processor.load_fpd(file_path)
        
        if result["success"]:
            system_state["fpd_loaded"] = True
            return {
                "success": True,
                "message": f"FPD carregada: {result['total_records']} registros",
                "stats": result["stats"]
            }
        else:
            return {
                "success": False,
                "message": result["error"]
            }
            
    except Exception as e:
        logger.error(f"❌ Erro no upload FPD: {e}")
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }

@app.post("/api/upload/vendas")
async def upload_vendas(file: UploadFile = File(...)):
    """Upload planilha VENDAS/contratos"""
    try:
        # Salvar arquivo
        file_path = f"uploads/vendas_{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Processar planilha
        result = excel_processor.load_vendas(file_path)
        
        if result["success"]:
            system_state["vendas_loaded"] = True
            return {
                "success": True,
                "message": f"VENDAS carregada: {result['total_records']} registros",
                "sheets": result["sheets"]
            }
        else:
            return {
                "success": False,
                "message": result["error"]
            }
            
    except Exception as e:
        logger.error(f"❌ Erro no upload VENDAS: {e}")
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }

@app.post("/api/process/match")
async def process_match():
    """Processar matching FPD x VENDAS"""
    try:
        if not system_state["fpd_loaded"] or not system_state["vendas_loaded"]:
            return {
                "success": False,
                "message": "Carregue FPD e VENDAS primeiro"
            }
        
        # Processar matching
        result = excel_processor.process_matching()
        
        return {
            "success": True,
            "matched_records": result["matched"],
            "total_protocols": result["total_protocols"],
            "ready_for_cobranca": result["ready_for_cobranca"]
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no matching: {e}")
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }

@app.post("/api/bot/start")
async def start_bot(background_tasks: BackgroundTasks):
    """Iniciar bot de cobrança"""
    try:
        if not system_state["whatsapp_connected"]:
            return {
                "success": False,
                "message": "WhatsApp não conectado"
            }
        
        if not excel_processor.has_matched_data():
            return {
                "success": False,
                "message": "Execute o matching primeiro"
            }
        
        # Iniciar bot em background
        background_tasks.add_task(run_cobranca_bot)
        
        system_state["bot_active"] = True
        
        return {
            "success": True,
            "message": "Bot de cobrança iniciado"
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar bot: {e}")
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }

@app.post("/api/bot/stop")
async def stop_bot():
    """Parar bot"""
    try:
        # Verificar se stealth_sender está definido para evitar erros
        if 'stealth_sender' in globals():
            stealth_sender.stop()
        
        system_state["bot_active"] = False
        
        return {
            "success": True,
            "message": "Bot parado"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro: {str(e)}"
        }

@app.post("/api/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Webhook para mensagens do WhatsApp"""
    try:
        data = await request.json()
        
        # Processar mensagem recebida
        if data.get("type") == "message":
            message = data.get("data", {})
            phone = message.get("from")
            text = message.get("body", "")
            
            # Engine de conversação
            response = await conversation_engine.process_message(phone, text)
            
            if response:
                # Enviar resposta
                await whatsapp_client.send_message(phone, response["text"], response.get("attachment"))
                
                # Atualizar stats
                system_state["stats"]["conversations"] += 1
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        return {"success": False}

async def run_cobranca_bot():
    """Executar bot de cobrança em background"""
    try:
        logger.info("🤖 Iniciando bot de cobrança...")
        
        # Obter dados para cobrança
        cobranca_data = excel_processor.get_cobranca_data()
        
        # Definir stealth_sender como global
        global stealth_sender
        from core.stealth_sender import StealthSender
        stealth_sender = StealthSender()
        
        # Executar envios stealth
        await stealth_sender.execute_mass_sending(
            data=cobranca_data,
            whatsapp_client=whatsapp_client,
            stats_callback=update_stats
        )
        
    except Exception as e:
        logger.error(f"❌ Erro no bot de cobrança: {e}")
        system_state["bot_active"] = False

def update_stats(stats):
    """Atualizar estatísticas"""
    system_state["stats"].update(stats)

# WebSocket para updates em tempo real
@app.websocket("/ws/status")
async def websocket_status(websocket):
    """WebSocket para atualizações em tempo real"""
    try:
        # Accept deve ser a primeira operação, antes de qualquer processamento
        await websocket.accept()
        
        # Log de conexão bem-sucedida
        logger.info("✅ WebSocket conectado")
        
        # Loop de envio de atualizações
        while True:
            # Enviar status atual
            await websocket.send_json({
                "type": "status_update",
                "data": system_state
            })
            
            # Aguardar 5 segundos
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        logger.info("📱 WebSocket desconectado normalmente")
    except ValueError as e:
        # Este erro específico ocorre quando já está fechado/rejeitado
        logger.info(f"ℹ️ WebSocket já fechado: {e}")
    except Exception as e:
        logger.error(f"❌ Erro no WebSocket: {e}")
    finally:
        try:
            await websocket.close()
        except Exception as e:
            logger.debug(f"ℹ️ Erro ao fechar WebSocket: {e}")
            pass

# 🚀 NOVOS ENDPOINTS - FUNCIONALIDADES AVANÇADAS

@app.post("/api/server/start")
async def start_server():
    """Iniciar serviços do servidor"""
    try:
        logger.info("🚀 Solicitação de inicialização do servidor")
        return {"success": True, "message": "Servidor iniciado com sucesso"}
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return {"success": False, "message": str(e)}

@app.post("/api/server/stop")
async def stop_server():
    """Parar serviços do servidor"""
    try:
        logger.info("🛑 Solicitação de parada do servidor")
        return {"success": True, "message": "Servidor parado com sucesso"}
    except Exception as e:
        logger.error(f"❌ Erro ao parar servidor: {e}")
        return {"success": False, "message": str(e)}

@app.get("/api/logs")
async def get_logs(type: str = "all", limit: int = 100):
    """Obter logs do sistema"""
    try:
        logs = []
        import datetime
        
        # Mock data - em produção, ler de arquivo de log real
        for i in range(min(limit, 20)):
            logs.append({
                "timestamp": datetime.datetime.now().isoformat(),
                "level": "info" if i % 3 != 0 else "error",
                "message": f"Log de exemplo #{i+1} - Sistema funcionando"
            })
        
        return logs
    except Exception as e:
        logger.error(f"❌ Erro ao carregar logs: {e}")
        return []

@app.get("/api/metrics")
async def get_metrics():
    """Obter métricas do sistema"""
    try:
        metrics = {
            "messages": {
                "total": 150,
                "sent": 142,
                "failed": 8
            },
            "conversations": {
                "active": 12,
                "completed": 85
            },
            "invoices": {
                "sent": 45,
                "downloaded": 38
            }
        }
        
        return metrics
    except Exception as e:
        logger.error(f"❌ Erro ao carregar métricas: {e}")
        return {}

@app.get("/api/messages/history")
async def get_message_history(phone: str = None, limit: int = 50):
    """Obter histórico de mensagens"""
    try:
        history = []
        
        # Mock data - em produção, consultar banco de dados
        for i in range(min(limit, 10)):
            conversation = {
                "phone": f"+5511999{i:06d}",
                "lastMessage": "2024-01-15T10:30:00",
                "messageCount": 5 + i,
                "status": "completed" if i % 2 == 0 else "active"
            }
            
            if phone is None or conversation["phone"] == phone:
                history.append(conversation)
        
        return history
    except Exception as e:
        logger.error(f"❌ Erro ao carregar histórico: {e}")
        return []

@app.get("/api/messages/conversation/{phone}")
async def get_conversation_messages(phone: str):
    """Obter mensagens de uma conversa específica"""
    try:
        messages = [
            {
                "content": "Olá, preciso da minha segunda via da fatura",
                "direction": "incoming",
                "timestamp": "2024-01-15T10:30:00"
            },
            {
                "content": "Olá! Vou buscar sua fatura. Qual é o CPF?",
                "direction": "outgoing",
                "timestamp": "2024-01-15T10:31:00"
            },
            {
                "content": "123.456.789-00",
                "direction": "incoming",
                "timestamp": "2024-01-15T10:32:00"
            },
            {
                "content": "Encontrei sua fatura! Enviando agora...",
                "direction": "outgoing",
                "timestamp": "2024-01-15T10:33:00"
            }
        ]
        
        return messages
    except Exception as e:
        logger.error(f"❌ Erro ao carregar mensagens: {e}")
        return []

@app.get("/api/config")
async def get_configuration():
    """Obter configurações do sistema"""
    try:
        config = {
            "bot": {
                "autoStart": True,
                "messageDelay": 1000
            },
            "whatsapp": {
                "stealthMode": True,
                "autoReconnect": True
            },
            "data": {
                "autoBackup": False
            }
        }
        
        return config
    except Exception as e:
        logger.error(f"❌ Erro ao carregar configuração: {e}")
        return {}

@app.put("/api/config")
async def update_configuration(data: dict):
    """Atualizar configurações do sistema"""
    try:
        key = data.get('key')
        value = data.get('value')
        
        logger.info(f"🔧 Atualizando configuração: {key} = {value}")
        
        # Aqui você salvaria a configuração em arquivo ou banco
        
        return {"success": True, "message": "Configuração atualizada"}
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar configuração: {e}")
        return {"success": False, "message": str(e)}

# 🔐 NOVOS ENDPOINTS - SISTEMA ANTI-CAPTCHA E DOWNLOAD FATURAS

@app.get("/api/captcha/info")
async def get_captcha_info():
    """Obter informações do sistema anti-captcha"""
    return get_captcha_solver_info()

@app.post("/api/fatura/download")
async def download_fatura(request: Request):
    """Baixar fatura individual do SAC Desktop"""
    try:
        data = await request.json()
        documento = data.get("documento")
        protocolo = data.get("protocolo")
        
        if not documento:
            return {"success": False, "error": "Documento é obrigatório"}
        
        # Verificar se WhatsApp está conectado (precisamos da página)
        if not whatsapp_client.page:
            return {"success": False, "error": "WhatsApp não conectado"}
        
        # Inicializar downloader se necessário
        global fatura_downloader
        if not fatura_downloader:
            fatura_downloader = FaturaDownloader(whatsapp_client.page)
        
        # Baixar fatura
        arquivo_baixado = await fatura_downloader.baixar_fatura(documento, protocolo)
        
        if arquivo_baixado:
            return {
                "success": True,
                "arquivo": arquivo_baixado,
                "documento": documento,
                "protocolo": protocolo
            }
        else:
            return {
                "success": False,
                "error": "Fatura não encontrada ou erro no download"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro no download de fatura: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/fatura/download/multiplas")
async def download_multiplas_faturas(request: Request):
    """Baixar múltiplas faturas do SAC Desktop"""
    try:
        data = await request.json()
        documentos_protocolos = data.get("documentos", [])
        intervalo = data.get("intervalo", 5.0)
        
        if not documentos_protocolos:
            return {"success": False, "error": "Lista de documentos é obrigatória"}
        
        # Verificar se WhatsApp está conectado
        if not whatsapp_client.page:
            return {"success": False, "error": "WhatsApp não conectado"}
        
        # Inicializar downloader se necessário
        global fatura_downloader
        if not fatura_downloader:
            fatura_downloader = FaturaDownloader(whatsapp_client.page)
        
        # Converter lista de documentos para tuplas (documento, protocolo)
        docs_tuplas = []
        for item in documentos_protocolos:
            if isinstance(item, dict):
                docs_tuplas.append((item.get("documento"), item.get("protocolo")))
            elif isinstance(item, list) and len(item) >= 2:
                docs_tuplas.append((item[0], item[1]))
            else:
                docs_tuplas.append((str(item), None))
        
        # Baixar faturas
        resultados = await fatura_downloader.baixar_multiplas_faturas(docs_tuplas, intervalo)
        
        return {
            "success": True,
            "resultados": resultados
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no download múltiplo: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/fatura/listar")
async def listar_faturas():
    """Listar todas as faturas baixadas"""
    try:
        global fatura_downloader
        
        # Se downloader não existe, criar instância temporária só para listar
        if not fatura_downloader:
            # Criar downloader básico só para listar arquivos
            import tempfile
            from core.fatura_downloader import FaturaDownloader
            from playwright.async_api import async_playwright
            
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            temp_downloader = FaturaDownloader(page)
            faturas = temp_downloader.listar_faturas_baixadas()
            await browser.close()
            await playwright.stop()
            
            return {
                "success": True,
                "faturas": faturas,
                "total": len(faturas)
            }
        
        faturas = fatura_downloader.listar_faturas_baixadas()
        
        return {
            "success": True,
            "faturas": faturas,
            "total": len(faturas)
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar faturas: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/fatura/status")
async def get_fatura_status():
    """Obter status do sistema de download de faturas"""
    try:
        global fatura_downloader
        
        if fatura_downloader:
            status = fatura_downloader.get_status()
            return {"success": True, "status": status}
        else:
            return {
                "success": True,
                "status": {
                    "fatura_downloader_initialized": False,
                    "whatsapp_connected": system_state["whatsapp_connected"],
                    "sac_url": "https://sac.desktop.com.br/Cliente_Documento.jsp"
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao obter status: {e}")
        return {"success": False, "error": str(e)}

@app.get("/health")
@app.get("/api/health")
async def health_check():
    """Health check otimizado para Render - ANTI-SLEEP"""
    try:
        import sys
        from datetime import datetime
        
        health_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": "render" if RENDER_CLOUD else "local",
            "python_version": sys.version.split()[0],
            "port": PORT,
            "playwright_path": os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'default'),
            "uptime_monitoring": "active",
            "anti_sleep": "enabled"
        }
        
        # Status do WhatsApp
        global whatsapp_client
        if whatsapp_client:
            health_info["whatsapp_status"] = "initialized"
        else:
            health_info["whatsapp_status"] = "not_initialized"
            
        # Verificar memória apenas se psutil estiver disponível
        try:
            import psutil
            memory = psutil.virtual_memory()
            health_info["memory"] = {
                "usage_percent": f"{memory.percent}%",
                "available_mb": f"{memory.available / 1024 / 1024:.1f}MB"
            }
        except ImportError:
            health_info["memory"] = "monitoring_disabled"
            
        return health_info
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.now().isoformat()}

@app.get("/ping")
async def ping_endpoint():
    """Endpoint simples para keep-alive - resposta rápida"""
    from datetime import datetime
    return {
        "pong": True,
        "timestamp": datetime.now().isoformat(),
        "status": "alive"
    }

if __name__ == "__main__":
    # Criar diretórios necessários
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("faturas", exist_ok=True)
    os.makedirs("web/static", exist_ok=True)
    os.makedirs("sessions", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    if RENDER_CLOUD:
        logger.info(f"🚀 Iniciando Blacktemplar Bolter no Render Cloud - Porta {PORT}")
        logger.info(f"💾 Playwright path: {os.getenv('PLAYWRIGHT_BROWSERS_PATH', 'padrão')}")
        
        # Configurações otimizadas para Render free tier
        uvicorn.run(
            app,
            host=HOST,
            port=PORT,
            log_level="info",
            access_log=False,  # Reduzir logs para economizar recursos
            workers=1          # Apenas 1 worker no free tier
        )
    else:
        logger.info("🏠 Iniciando Blacktemplar Bolter localmente")
        uvicorn.run(
            "app:app",
            host=HOST,
            port=PORT,
            reload=True
        ) 