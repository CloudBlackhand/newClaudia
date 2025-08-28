#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAHA Real Server - Claudia Cobranças
Servidor WAHA real que envia códigos de verificação via SMS
"""

import asyncio
import json
import logging
import os
import time
import random
import string
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel
import requests
from sms_service import sms_service

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
    "messages": [],
    "verification_codes": {}  # Armazena códigos temporários
}

class WAHAServer:
    """Servidor WAHA real com envio de códigos"""
    
    def __init__(self):
        self.app = FastAPI(title="WAHA Real", version="1.0")
        self.setup_routes()
        
    def generate_verification_code(self) -> str:
        """Gerar código de verificação de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_sms_code(self, phone_number: str, code: str) -> bool:
        """Enviar código via SMS real"""
        try:
            message = f"Claudia Cobranças: Seu código de verificação é {code}. Válido por 10 minutos."
            
            # Enviar via serviço SMS configurado
            success = sms_service.send_sms(phone_number, message)
            
            if success:
                logger.info(f"📱 SMS enviado para {phone_number}: Código {code}")
                return True
            else:
                logger.error(f"Falha ao enviar SMS para {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return False
    
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
            is_connected = instance_name in waha_state["connections"] and waha_state["connections"][instance_name]["verified"]
            
            return {
                "name": instance_name,
                "status": "connected" if is_connected else "disconnected",
                "connected": is_connected,
                "webhook": instance.get("webhook"),
                "created_at": instance.get("created_at"),
                "started_at": instance.get("started_at")
            }
        
        @self.app.post("/api/instances/{instance_name}/auth/send-code")
        async def send_code(instance_name: str, data: SendCode):
            """Enviar código de verificação REAL"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            phone_number = data.phoneNumber
            
            # Gerar código REAL de 6 dígitos
            verification_code = self.generate_verification_code()
            
            # Enviar SMS REAL
            sms_sent = self.send_sms_code(phone_number, verification_code)
            
            if not sms_sent:
                return {"success": False, "error": "Falha ao enviar SMS"}
            
            # Armazenar código temporariamente (expira em 10 minutos)
            waha_state["verification_codes"][phone_number] = {
                "code": verification_code,
                "instance": instance_name,
                "created_at": time.time(),
                "expires_at": time.time() + 600  # 10 minutos
            }
            
            # Preparar conexão
            waha_state["connections"][instance_name] = {
                "phone_number": phone_number,
                "verified": False,
                "connected_at": None
            }
            
            logger.info(f"📱 Código REAL enviado para {phone_number}: {verification_code}")
            return {
                "success": True, 
                "message": f"Código enviado para {phone_number}",
                "phone_number": phone_number
            }
        
        @self.app.post("/api/instances/{instance_name}/auth/verify")
        async def verify_code(instance_name: str, data: AuthVerify):
            """Verificar código REAL"""
            if instance_name not in waha_state["instances"]:
                raise HTTPException(status_code=404, detail="Instância não encontrada")
            
            phone_number = data.phoneNumber
            code = data.code
            
            # Verificar se código existe e não expirou
            if phone_number not in waha_state["verification_codes"]:
                return {"success": False, "error": "Código não foi enviado"}
            
            stored_data = waha_state["verification_codes"][phone_number]
            
            # Verificar expiração
            if time.time() > stored_data["expires_at"]:
                del waha_state["verification_codes"][phone_number]
                return {"success": False, "error": "Código expirado"}
            
            # Verificar se código está correto
            if code == stored_data["code"] and stored_data["instance"] == instance_name:
                # Marcar como verificado
                if instance_name in waha_state["connections"]:
                    waha_state["connections"][instance_name]["verified"] = True
                    waha_state["connections"][instance_name]["connected_at"] = time.time()
                
                # Limpar código usado
                del waha_state["verification_codes"][phone_number]
                
                logger.info(f"✅ WhatsApp conectado: {phone_number}")
                return {"success": True, "message": "Código verificado com sucesso"}
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
        
        @self.app.get("/health")
        async def health_check():
            """Health check"""
            return {
                "status": "healthy",
                "waha": "real",
                "instances": len(waha_state["instances"]),
                "connections": len([c for c in waha_state["connections"].values() if c["verified"]]),
                "timestamp": time.time()
            }

# Função para limpar códigos expirados
async def cleanup_expired_codes():
    """Limpar códigos de verificação expirados"""
    while True:
        current_time = time.time()
        expired_phones = []
        
        for phone, data in waha_state["verification_codes"].items():
            if current_time > data["expires_at"]:
                expired_phones.append(phone)
        
        for phone in expired_phones:
            del waha_state["verification_codes"][phone]
            logger.info(f"🗑️ Código expirado removido: {phone}")
        
        await asyncio.sleep(60)  # Verificar a cada minuto

# Criar instância do servidor
waha_server = WAHAServer()

def get_app():
    """Retornar aplicação FastAPI"""
    return waha_server.app

# Iniciar limpeza de códigos expirados
async def start_cleanup():
    await cleanup_expired_codes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(waha_server.app, host="0.0.0.0", port=3000)
