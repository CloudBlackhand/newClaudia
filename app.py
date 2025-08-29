#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDIA COBRANÇAS - Bot de Conversação Inteligente
Aplicação principal FastAPI focada apenas no bot de conversação
"""

import os
import asyncio
from fastapi.websockets import WebSocketDisconnect
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from typing import List, Optional
import logging
import uuid
import json
import time
import httpx
from datetime import datetime, timedelta
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔐 MODELOS PARA SISTEMA DE AUTENTICAÇÃO
class LoginRequest(BaseModel):
    email: str
    password: str
    reason: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None

class SessionValidation(BaseModel):
    token: str

# 🗃️ ARMAZENAMENTO DE AUTENTICAÇÃO (em memória para simplicidade)
pending_auth_requests = {}  # {request_id: {email, timestamp, ip, reason, etc}}
active_sessions = {}       # {token: {email, timestamp, request_id}}
auth_settings = {
    "session_timeout": 3600,  # 1 hora
    "request_timeout": 300,   # 5 minutos
    "max_pending": 10
}

# Importar módulo core essencial
from core.conversation import SuperConversationEngine
from config import Config, CLAUDIA_CONFIG

# Inicializar FastAPI
app = FastAPI(
    title="Claudia Cobranças - Bot de Conversação",
    description="Bot inteligente de conversação da Desktop",
    version="2.2"
)

# Adicionar CORS para WebSockets
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas as origens
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
conversation_engine = SuperConversationEngine()

# Estado do sistema
system_state = {
    "bot_active": True,
    "stats": {
        "messages_processed": 0,
        "conversations": 0
    }
}

@app.get("/health")
async def health_check():
    """Healthcheck para Railway"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
            "version": "2.2",
            "bot_active": system_state["bot_active"],
        "waha_url": os.getenv("WAHA_URL", "Não configurado")
    }

# 🔗 WEBHOOK PARA INTEGRAÇÃO COM WAHA
@app.post("/webhook")
async def waha_webhook(request: Request):
    """Webhook para receber mensagens do WAHA"""
    try:
        data = await request.json()
        logger.info(f"📱 Webhook recebido: {data}")
        
        # Processar mensagem do WhatsApp
        if data.get("event") == "message":
            message_data = data.get("payload", {})
            phone = message_data.get("from")
            message = message_data.get("body", "")
            
            if not message or not phone:
                return {"success": False, "error": "Dados inválidos"}
            
            logger.info(f"💬 Mensagem do WhatsApp: {phone} -> {message}")
            
            # Processar com engine de conversação
            result = conversation_engine.process_message(message, {})
            response = result.get("response", "Desculpe, não entendi.")
            
            # Atualizar estatísticas
            system_state["stats"]["messages_processed"] += 1
            
            # Enviar resposta de volta para WAHA
            await send_waha_response(phone, response)
            
            logger.info(f"✅ Resposta enviada para {phone}: {response}")
            
        elif data.get("event") == "engine.event" and data.get("payload", {}).get("event") == "unread_count":
            # Processar evento de mensagem não lida
            payload = data.get("payload", {}).get("data", {})
            last_message = payload.get("lastMessage", {})
            phone = last_message.get("from")
            message = last_message.get("body", "")
            
            if not message or not phone:
                return {"success": False, "error": "Dados inválidos"}
            
            logger.info(f"💬 Mensagem do WhatsApp: {phone} -> {message}")
            
            # Processar com engine de conversação
            result = conversation_engine.process_message(message, {})
            response = result.get("response", "Desculpe, não entendi.")
            
            # Atualizar estatísticas
            system_state["stats"]["messages_processed"] += 1
            
            # Enviar resposta de volta para WAHA
            await send_waha_response(phone, response)
            
            logger.info(f"✅ Resposta enviada para {phone}: {response}")
            
        return {"success": True}
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}")
        return {"success": False, "error": str(e)}

async def send_waha_response(phone: str, message: str):
    """Enviar resposta para WAHA - Usando método que funciona"""
    waha_url = os.getenv("WAHA_URL")
    
    if not waha_url:
        logger.error("❌ WAHA_URL não configurado")
        return
    
    try:
        # Endpoint correto para WEBJS (documentação oficial)
        endpoint = f"https://{waha_url}/api/sendText"
        
        # Limpar formato do telefone (remover @c.us para evitar erro do WAHA)
        clean_phone = phone.replace("@c.us", "") if "@c.us" in phone else phone
        
        # Tentar diferentes formatos para contornar bug do WAHA
        phone_formats = [
            clean_phone,  # 5521971364919
            f"+{clean_phone}",  # +5521971364919
            f"{clean_phone}@c.us",  # 5521971364919@c.us
            f"+{clean_phone}@c.us"  # +5521971364919@c.us
        ]
        
        success = False
        for phone_format in phone_formats:
            try:
                # Formato correto do payload para WEBJS
                response_data = {
                    "session": "default",
                    "to": phone_format,
                    "text": message
                }
                
                logger.info(f"🔄 Tentando formato: {phone_format}")
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(endpoint, json=response_data)
                    
                if response.status_code == 200:
                    logger.info(f"✅ Resposta enviada com sucesso para {phone} via {endpoint}")
                    success = True
                    break
                else:
                    logger.warning(f"⚠️ Formato {phone_format} retornou: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro com formato {phone_format}: {str(e)}")
                continue
        
        if not success:
            logger.error(f"❌ Nenhum formato de telefone funcionou para {phone}")
            # Log da resposta do bot para debug
            logger.info(f"🤖 Resposta do bot (não enviada): {message}")
        
    except Exception as e:
        logger.error(f"❌ Erro geral ao enviar resposta para WAHA: {e}")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard principal - carrega o sistema JavaScript completo"""
    import time
    # Adicionar timestamp para evitar cache do navegador
    timestamp = int(time.time())
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
        <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Claudia Cobranças - Bot de Conversação</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="/static/style.css?v={timestamp}" rel="stylesheet">
    </head>
    <body>
        <div id="loading" class="loading-overlay">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>

        <div class="container-fluid">
            <div class="row">
                <!-- Sidebar -->
                <nav class="col-md-3 col-lg-2 d-md-block bg-dark sidebar collapse">
                    <div class="position-sticky pt-3">
                        <div class="text-center mb-4">
                            <h4 class="text-white">🤖 Claudia Cobranças</h4>
                            <p class="text-muted">Bot de Conversação</p>
                        </div>
                        
                        <ul class="nav flex-column">
                            <li class="nav-item">
                                <a class="nav-link active" href="#" onclick="showSection('dashboard')">
                                    <i class="fas fa-tachometer-alt"></i> Dashboard
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showSection('conversation')">
                                    <i class="fas fa-comments"></i> Conversação
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showSection('waha')">
                                    <i class="fab fa-whatsapp"></i> WAHA Status
                                </a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="#" onclick="showSection('logs')">
                                    <i class="fas fa-list"></i> Logs
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>

                <!-- Main content -->
                <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
                    <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                        <h1 class="h2">Dashboard</h1>
                        <div class="btn-toolbar mb-2 mb-md-0">
                            <div class="btn-group me-2">
                                <button type="button" class="btn btn-sm btn-outline-secondary" onclick="refreshStats()">
                                    <i class="fas fa-sync-alt"></i> Atualizar
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Dashboard Section -->
                    <div id="dashboard-section" class="content-section">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card text-white bg-primary mb-3">
                                    <div class="card-body">
                                        <h5 class="card-title">Status do Bot</h5>
                                        <p class="card-text" id="botStatus">Carregando...</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card text-white bg-success mb-3">
                                    <div class="card-body">
                                        <h5 class="card-title">Mensagens Processadas</h5>
                                        <p class="card-text" id="messagesCount">0</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card text-white bg-info mb-3">
                                    <div class="card-body">
                                        <h5 class="card-title">Conversações</h5>
                                        <p class="card-text" id="conversationsCount">0</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Conversation Section -->
                    <div id="conversation-section" class="content-section" style="display: none;">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-comments"></i> Teste de Conversação</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="testMessage" class="form-label">Digite uma mensagem para testar:</label>
                                    <textarea class="form-control" id="testMessage" rows="3" placeholder="Ex: quanto eu devo?"></textarea>
                                </div>
                                <button type="button" class="btn btn-primary" onclick="testConversation()">
                                    <i class="fas fa-paper-plane"></i> Testar Resposta
                                </button>
                                <div id="conversationResult" class="mt-3"></div>
                            </div>
                        </div>
                    </div>

                    <!-- WAHA Status Section -->
                    <div id="waha-section" class="content-section" style="display: none;">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fab fa-whatsapp"></i> Status WAHA</h5>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Configuração WAHA:</h6>
                                        <p><strong>URL:</strong> <span id="wahaUrl">Carregando...</span></p>
                                        <p><strong>Instance:</strong> <span id="wahaInstance">Carregando...</span></p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Status:</h6>
                                        <p><strong>Webhook:</strong> <span id="webhookStatus">Carregando...</span></p>
                                        <button type="button" class="btn btn-sm btn-outline-primary" onclick="testWebhook()">
                                            <i class="fas fa-test"></i> Testar Webhook
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Logs Section -->
                    <div id="logs-section" class="content-section" style="display: none;">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-list"></i> Logs do Sistema</h5>
                            </div>
                            <div class="card-body">
                                <div id="logsContainer" style="max-height: 400px; overflow-y: auto;">
                                    <p class="text-muted">Nenhum log disponível</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="/static/app.js?v={timestamp}"></script>
    </body>
    </html>
    """)

# 🔐 SISTEMA DE AUTENTICAÇÃO
@app.post("/api/auth/request")
async def request_auth(request: LoginRequest, req: Request):
    """Solicitar autenticação - gera ID para aprovação manual"""
    try:
        # Limpar requests antigos
        current_time = time.time()
        pending_auth_requests = {k: v for k, v in pending_auth_requests.items() 
                               if current_time - v["timestamp"] < auth_settings["request_timeout"]}
        
        if len(pending_auth_requests) >= auth_settings["max_pending"]:
            raise HTTPException(status_code=429, detail="Muitas solicitações pendentes")
        
        # Gerar ID único
        request_id = str(uuid.uuid4())
        
        # Capturar IP real
        client_ip = req.client.host
        if "x-forwarded-for" in req.headers:
            client_ip = req.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Salvar request
        pending_auth_requests[request_id] = {
            "email": request.email,
            "password": request.password,
            "reason": request.reason,
            "ip": client_ip,
            "user_agent": request.user_agent or req.headers.get("user-agent", ""),
            "timestamp": current_time
        }
        
        # Log para aprovação manual
        print(f"\n🔐 NOVA SOLICITAÇÃO DE LOGIN:")
        print(f"   ID: {request_id}")
        print(f"   Email: {request.email}")
        print(f"   Motivo: {request.reason}")
        print(f"   IP: {client_ip}")
        print(f"   User-Agent: {request.user_agent or req.headers.get('user-agent', '')}")
        print(f"   Timestamp: {datetime.fromtimestamp(current_time)}")
        print(f"   Para aprovar, execute: python -c \"from app import approve_auth; approve_auth('{request_id}')\"")
        print(f"   Para rejeitar, execute: python -c \"from app import reject_auth; reject_auth('{request_id}')\"")
        print(f"   Ou acesse: http://localhost:8000/api/auth/approve/{request_id}")
        print(f"   Ou acesse: http://localhost:8000/api/auth/reject/{request_id}")
        print()
        
        return {
            "success": True,
            "request_id": request_id,
            "message": "Solicitação enviada. Aguarde aprovação manual no terminal.",
            "status": "pending"
        }
        
    except Exception as e:
        logger.error(f"Erro na solicitação de auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/status/{request_id}")
async def check_auth_status(request_id: str):
    """Verificar status da solicitação de autenticação"""
    try:
        if request_id in pending_auth_requests:
            return {
                "status": "pending",
                "message": "Aguardando aprovação manual"
            }
        elif request_id in active_sessions:
            return {
                "status": "approved",
                "message": "Acesso aprovado",
                "token": request_id
            }
        else:
            return {
                "status": "rejected",
                "message": "Acesso rejeitado ou expirado"
            }
    except Exception as e:
        logger.error(f"Erro ao verificar status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/approve/{request_id}")
async def approve_auth_web(request_id: str):
    """Aprovar autenticação via web"""
    return await approve_auth(request_id)

@app.get("/api/auth/reject/{request_id}")
async def reject_auth_web(request_id: str):
    """Rejeitar autenticação via web"""
    return await reject_auth(request_id)

async def approve_auth(request_id: str):
    """Aprovar autenticação"""
    try:
        if request_id not in pending_auth_requests:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada")
        
        # Mover para sessões ativas
        request_data = pending_auth_requests.pop(request_id)
        active_sessions[request_id] = {
            "email": request_data["email"],
            "timestamp": time.time(),
            "request_id": request_id
        }
        
        logger.info(f"✅ Acesso aprovado para {request_data['email']}")
        return {"success": True, "message": "Acesso aprovado", "token": request_id}
        
    except Exception as e:
        logger.error(f"Erro ao aprovar auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def reject_auth(request_id: str):
    """Rejeitar autenticação"""
    try:
        if request_id in pending_auth_requests:
            request_data = pending_auth_requests.pop(request_id)
            logger.info(f"❌ Acesso rejeitado para {request_data['email']}")
            return {"success": True, "message": "Acesso rejeitado"}
        else:
            return {"success": False, "message": "Solicitação não encontrada"}
            
    except Exception as e:
        logger.error(f"Erro ao rejeitar auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def validate_session(token: str) -> bool:
    """Validar sessão ativa"""
    if token not in active_sessions:
        return False
    
    session = active_sessions[token]
    if time.time() - session["timestamp"] > auth_settings["session_timeout"]:
        del active_sessions[token]
        return False
    
    return True

# 📊 API ENDPOINTS
@app.get("/api/stats")
async def get_stats():
    """Obter estatísticas do sistema"""
    return {
        "success": True,
        "stats": system_state["stats"],
        "bot_active": system_state["bot_active"],
        "waha_url": os.getenv("WAHA_URL", "Não configurado"),
        "waha_instance": os.getenv("WAHA_INSTANCE_NAME", "Não configurado")
    }

@app.post("/api/conversation/test")
async def test_conversation(request: Request):
    """Testar conversação"""
    try:
        data = await request.json()
        message = data.get("message", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Mensagem é obrigatória")
        
        # Processar com engine de conversação
        result = conversation_engine.process_message(message, {})
        response = result.get("response", "Desculpe, não entendi.")
        
        # Atualizar estatísticas
        system_state["stats"]["messages_processed"] += 1
        
        return {
            "success": True,
            "response": response,
            "original_message": message
        }
        
    except Exception as e:
        logger.error(f"Erro no teste de conversação: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs():
    """Obter logs do sistema"""
    try:
        # Logs básicos do sistema
        logs = [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Sistema iniciado"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Bot ativo"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": f"WAHA URL: {os.getenv('WAHA_URL', 'Não configurado')}"}
        ]
        
        return {
            "success": True,
            "logs": logs
        }
            
    except Exception as e:
        logger.error(f"Erro ao obter logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 