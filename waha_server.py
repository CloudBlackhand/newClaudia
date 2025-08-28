#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAHA Server Embutido - Claudia Cobranças
Servidor WAHA que roda junto com a aplicação principal
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Modelos WAHA
class InstanceCreate(BaseModel):
    instanceName: str
    webhook: Optional[str] = None
    webhookByEvents: bool = False
    webhookBase64: bool = False

class AuthVerify(BaseModel):
    code: str
    phoneNumber: str

class SendCode(BaseModel):
    phoneNumber: str

class SendMessage(BaseModel):
    chatId: str
    text: str

# Estado global do WAHA
waha_state = {
    "instances": {},
    "connections": {},
    "messages": []
}

class WAHAServer:
    """Servidor WAHA embutido"""
    
    def __init__(self):
        self.app = FastAPI(title="WAHA Embutido", version="1.0")
        self.setup_routes()
        
    def setup_routes(self):
        """Configurar rotas WAHA"""
        
        @self.app.get("/api/instances")
        async def list_instances():
            """Listar instâncias"""
            return {
                "instances": list(waha_state["instances"].keys()),
                "count": len(waha_state["instances"])
            }
        
        @self.app.post("/api/instances/create")
        async def create_instance(data: InstanceCreate):
            """Criar instância"""
            instance_name = data.instanceName
            
            if instance_name in waha_state["instances"]:
                return {"success": False, "error": "Instância já existe"}
            
            waha_state["instances"][instance_name] = {
                "name": instance_name,
                "webhook": data.webhook,
                "webhookByEvents": data.webhookByEvents,
                "webhookBase64": data.webhookBase64,
                "status": "created",
                "created_at": time.time()
            }
            
            logger.info(f"✅ Instância WAHA criada: {instance_name}")
            return {"success": True, "instance": waha_state["instances"][instance_name]}
        
        @self.app.post("/api/instances/{instance_name}/start")
        async def start_instance(instance_name: str):
            """Iniciar instância"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            waha_state["instances"][instance_name]["status"] = "started"
            waha_state["instances"][instance_name]["started_at"] = time.time()
            
            logger.info(f"✅ Instância WAHA iniciada: {instance_name}")
            return {"success": True, "status": "started"}
        
        @self.app.get("/api/instances/{instance_name}/info")
        async def get_instance_info(instance_name: str):
            """Obter informações da instância"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            instance = waha_state["instances"][instance_name]
            is_connected = instance_name in waha_state["connections"]
            
            return {
                "name": instance_name,
                "status": "qr" if is_connected else "disconnected",
                "connected": is_connected,
                "webhook": instance.get("webhook"),
                "created_at": instance.get("created_at"),
                "started_at": instance.get("started_at")
            }
        
        @self.app.post("/api/instances/{instance_name}/auth/send-code")
        async def send_code(instance_name: str, data: SendCode):
            """Enviar código de verificação"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            phone_number = data.phoneNumber
            
            # Simular envio de código (em produção, seria via SMS)
            code = "123456"  # Código fixo para teste
            
            waha_state["connections"][instance_name] = {
                "phone_number": phone_number,
                "code": code,
                "verified": False,
                "connected_at": None
            }
            
            logger.info(f"📱 Código enviado para {phone_number}: {code}")
            return {"success": True, "message": "Código enviado"}
        
        @self.app.post("/api/instances/{instance_name}/auth/verify")
        async def verify_code(instance_name: str, data: AuthVerify):
            """Verificar código"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            if instance_name not in waha_state["connections"]:
                raise HTTPException(status_code=400, detail="Código não foi enviado")
            
            connection = waha_state["connections"][instance_name]
            
            if data.code == connection["code"] and data.phoneNumber == connection["phone_number"]:
                connection["verified"] = True
                connection["connected_at"] = time.time()
                
                logger.info(f"✅ WhatsApp conectado: {data.phoneNumber}")
                return {"success": True, "message": "Código verificado"}
            else:
                return {"success": False, "error": "Código inválido"}
        
        @self.app.post("/api/instances/{instance_name}/messages/sendText")
        async def send_message(instance_name: str, data: SendMessage):
            """Enviar mensagem"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            if instance_name not in waha_state["connections"] or not waha_state["connections"][instance_name]["verified"]:
                raise HTTPException(status_code=400, detail="WhatsApp não conectado")
            
            # Simular envio de mensagem
            message_data = {
                "id": f"msg_{int(time.time())}",
                "chatId": data.chatId,
                "text": data.text,
                "timestamp": time.time(),
                "fromMe": True
            }
            
            waha_state["messages"].append(message_data)
            
            logger.info(f"📤 Mensagem enviada: {data.text}")
            return {"success": True, "message": "Mensagem enviada"}
        
        @self.app.get("/api/instances/{instance_name}/messages")
        async def get_messages(instance_name: str):
            """Obter mensagens"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            return {
                "messages": waha_state["messages"],
                "count": len(waha_state["messages"])
            }
        
        @self.app.delete("/api/instances/{instance_name}")
        async def delete_instance(instance_name: str):
            """Deletar instância"""
            if instance_name in waha_state["instances"]:
                del waha_state["instances"][instance_name]
            
            if instance_name in waha_state["connections"]:
                del waha_state["connections"][instance_name]
            
            logger.info(f"🗑️ Instância WAHA deletada: {instance_name}")
            return {"success": True, "message": "Instância deletada"}
    
    def get_app(self):
        """Retornar aplicação FastAPI"""
        return self.app

# Instância global
waha_server = WAHAServer()

def start_waha_server(port: int = 3000):
    """Iniciar servidor WAHA"""
    app = waha_server.get_app()
    
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    
    server = uvicorn.Server(config)
    return server

if __name__ == "__main__":
    # Teste do servidor
    server = start_waha_server()
    server.run()
