"""
Aplicação principal Flask - API para sistema de cobrança
"""
import asyncio
import json
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.utils import secure_filename
from pathlib import Path

# Imports do sistema
from backend.config.settings import active_config
from backend.services.billing import BillingService
from backend.services.waha_client import WahaClient, WahaWebhookHandler
from backend.models.chatbot import chatbot
from backend.models.conversation import conversation_manager, ConversationContext
from backend.utils.logger import app_logger, billing_logger, conversation_logger, waha_logger
from backend.utils.validators import SecurityValidator

# Inicialização da aplicação
app = Flask(__name__)
app.config.from_object(active_config)

# Configurações adicionais
app.config['MAX_CONTENT_LENGTH'] = active_config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = active_config.UPLOAD_FOLDER

# Extensões
CORS(app)
jwt = JWTManager(app)

# Serviços
billing_service = BillingService()
waha_client = WahaClient()
webhook_handler = WahaWebhookHandler()

# Middleware para logs de requisições
@app.before_request
def log_request():
    """Log todas as requisições"""
    app_logger.info("REQUEST_RECEIVED", {
        "method": request.method,
        "endpoint": request.endpoint,
        "remote_addr": request.remote_addr,
        "user_agent": request.headers.get("User-Agent", "")[:100]
    })

# Handlers de erro
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    app_logger.error("INTERNAL_SERVER_ERROR", error)
    return jsonify({"error": "Erro interno do servidor"}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "Arquivo muito grande"}), 413

# Decorador para endpoints assíncronos
def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# === ROTAS PRINCIPAIS ===

@app.route("/", methods=["GET"])
def index():
    """Página inicial com informações do sistema"""
    return jsonify({
        "name": "Sistema de Cobrança Inteligente",
        "version": "1.0.0",
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "Disparo automatizado de mensagens",
            "Bot conversacional avançado",
            "Integração WhatsApp via Waha",
            "Processamento inteligente de dados"
        ]
    })

@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint de health check para Railway"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

# === AUTENTICAÇÃO ===

@app.route("/auth/login", methods=["POST"])
def login():
    """Login básico (para demonstração)"""
    data = request.get_json()
    
    # Validação simples - em produção usar sistema mais robusto
    username = data.get("username")
    password = data.get("password")
    
    if username == "admin" and password == "admin123":  # Credenciais demo
        access_token = create_access_token(identity=username)
        return jsonify({
            "access_token": access_token,
            "user": username
        })
    
    return jsonify({"error": "Credenciais inválidas"}), 401

# === WEBHOOKS WAHA ===

@app.route("/webhook/waha", methods=["POST"])
@async_route
async def waha_webhook():
    """Recebe webhooks da Waha"""
    try:
        webhook_data = request.get_json()
        
        # Processa webhook
        result = await webhook_handler.process_webhook(webhook_data)
        
        if result["success"]:
            return jsonify({"status": "processed"}), 200
        else:
            return jsonify({"error": result["error"]}), 400
            
    except Exception as e:
        waha_logger.error("WEBHOOK_PROCESSING_ERROR", e)
        return jsonify({"error": "Erro ao processar webhook"}), 500

# === API DE COBRANÇA ===

@app.route("/api/billing/send-batch", methods=["POST"])
@jwt_required()
@async_route
async def send_billing_batch():
    """Envia lote de cobrança"""
    try:
        data = request.get_json()
        
        clients_file = data.get("clients_file")
        template_name = data.get("template_name")
        filters = data.get("filters", {})
        delay_seconds = data.get("delay_seconds", 2)
        
        if not clients_file or not template_name:
            return jsonify({"error": "clients_file e template_name são obrigatórios"}), 400
        
        # Envia lote
        result = await billing_service.send_billing_batch(
            clients_file=clients_file,
            template_name=template_name,
            filters=filters,
            delay_seconds=delay_seconds
        )
        
        return jsonify(result)
        
    except Exception as e:
        billing_logger.error("BATCH_SEND_API_ERROR", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/billing/send-single", methods=["POST"])
@jwt_required()
@async_route
async def send_single_message():
    """Envia mensagem para cliente único"""
    try:
        data = request.get_json()
        
        client_data = data.get("client")
        template_name = data.get("template_name")
        
        if not client_data or not template_name:
            return jsonify({"error": "client e template_name são obrigatórios"}), 400
        
        result = await billing_service.send_single_message(client_data, template_name)
        return jsonify(result)
        
    except Exception as e:
        billing_logger.error("SINGLE_MESSAGE_API_ERROR", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/billing/validate", methods=["POST"])
@jwt_required()
@async_route
async def validate_billing_config():
    """Valida configuração antes de enviar"""
    try:
        data = request.get_json()
        
        clients_file = data.get("clients_file")
        template_name = data.get("template_name")
        
        if not clients_file or not template_name:
            return jsonify({"error": "clients_file e template_name são obrigatórios"}), 400
        
        result = await billing_service.validate_before_sending(clients_file, template_name)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/billing/batch-status", methods=["GET"])
@jwt_required()
def get_batch_status():
    """Retorna status do lote atual"""
    status = billing_service.get_batch_status()
    
    if status:
        return jsonify(status)
    else:
        return jsonify({"message": "Nenhum lote em execução"}), 404

@app.route("/api/billing/templates", methods=["GET"])
@jwt_required()
def get_templates():
    """Lista templates disponíveis"""
    templates = billing_service.get_available_templates()
    return jsonify(templates)

@app.route("/api/billing/templates", methods=["POST"])
@jwt_required()
def add_template():
    """Adiciona novo template"""
    try:
        data = request.get_json()
        
        name = data.get("name")
        content = data.get("content")
        
        if not name or not content:
            return jsonify({"error": "name e content são obrigatórios"}), 400
        
        success = billing_service.message_template.add_template(name, content)
        
        if success:
            return jsonify({"message": "Template adicionado com sucesso"})
        else:
            return jsonify({"error": "Template inválido"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === API DO CHATBOT ===

@app.route("/api/chat/process", methods=["POST"])
@async_route
async def process_chat_message():
    """Processa mensagem do chat"""
    try:
        data = request.get_json()
        
        phone = data.get("phone")
        message = data.get("message")
        
        if not phone or not message:
            return jsonify({"error": "phone e message são obrigatórios"}), 400
        
        # Obtém ou cria contexto da conversa
        context = conversation_manager.start_conversation(phone)
        
        # Adiciona mensagem do usuário
        conversation_manager.add_message(phone, "user", message)
        
        # Processa mensagem com o bot
        response_data = await chatbot.process_message(message, context)
        
        # Adiciona resposta do bot
        conversation_manager.add_message(
            phone, 
            "assistant", 
            response_data["response"],
            intent=response_data["intent"],
            confidence=response_data["confidence"]
        )
        
        # Atualiza contexto se necessário
        if response_data["context_updates"]:
            conversation_manager.update_context(phone, **response_data["context_updates"])
        
        return jsonify({
            "response": response_data["response"],
            "intent": response_data["intent"],
            "confidence": response_data["confidence"],
            "actions": response_data["actions"]
        })
        
    except Exception as e:
        conversation_logger.error("CHAT_PROCESSING_API_ERROR", e)
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/conversation/<phone>", methods=["GET"])
@jwt_required()
def get_conversation_history(phone):
    """Obtém histórico da conversa"""
    try:
        limit = request.args.get("limit", type=int)
        history = conversation_manager.get_conversation_history(phone, limit)
        
        return jsonify({
            "phone": phone,
            "messages": [msg.to_dict() for msg in history],
            "summary": conversation_manager.get_conversation_summary(phone)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat/conversations/stats", methods=["GET"])
@jwt_required()
def get_conversations_stats():
    """Estatísticas das conversas ativas"""
    stats = conversation_manager.get_active_conversations_stats()
    return jsonify(stats)

# === API WAHA ===

@app.route("/api/waha/status", methods=["GET"])
@jwt_required()
@async_route
async def waha_status():
    """Status da sessão Waha"""
    result = await waha_client.get_session_status()
    return jsonify(result)

@app.route("/api/waha/start", methods=["POST"])
@jwt_required()
@async_route
async def start_waha_session():
    """Inicia sessão Waha"""
    result = await waha_client.start_session()
    return jsonify(result)

@app.route("/api/waha/stop", methods=["POST"])
@jwt_required()
@async_route
async def stop_waha_session():
    """Para sessão Waha"""
    result = await waha_client.stop_session()
    return jsonify(result)

@app.route("/api/waha/qr", methods=["GET"])
@jwt_required()
@async_route
async def get_qr_code():
    """Obtém QR code para autenticação"""
    result = await waha_client.get_qr_code()
    return jsonify(result)

# === UPLOAD DE ARQUIVOS ===

@app.route("/api/upload/clients", methods=["POST"])
@jwt_required()
def upload_clients_file():
    """Upload de arquivo de clientes"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Nome de arquivo vazio"}), 400
        
        # Valida arquivo
        validation = SecurityValidator.validate_file_upload(
            file.filename,
            file.read(),
            active_config.ALLOWED_EXTENSIONS
        )
        
        file.seek(0)  # Reset file pointer
        
        if not validation["valid"]:
            return jsonify({"error": "; ".join(validation["errors"])}), 400
        
        # Salva arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        
        file_path = Path(active_config.UPLOAD_FOLDER) / safe_filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file.save(str(file_path))
        
        app_logger.info("FILE_UPLOADED", {
            "filename": safe_filename,
            "size": file_path.stat().st_size
        })
        
        return jsonify({
            "message": "Arquivo enviado com sucesso",
            "filename": safe_filename,
            "path": str(file_path)
        })
        
    except Exception as e:
        app_logger.error("FILE_UPLOAD_ERROR", e)
        return jsonify({"error": str(e)}), 500

# === CONFIGURAÇÃO DE HANDLERS ===

async def handle_incoming_message(message_data):
    """Handler para mensagens recebidas via webhook"""
    try:
        phone = message_data.get("from")
        content = message_data.get("body", "")
        
        if not phone or not content:
            return
        
        # Processa mensagem com o bot
        context = conversation_manager.start_conversation(phone)
        
        # Adiciona mensagem do usuário
        conversation_manager.add_message(phone, "user", content)
        
        # Gera resposta do bot
        response_data = await chatbot.process_message(content, context)
        
        # Envia resposta via Waha
        if response_data["response"]:
            await waha_client.send_text_message(phone, response_data["response"])
            
            # Adiciona resposta do bot ao histórico
            conversation_manager.add_message(
                phone, 
                "assistant", 
                response_data["response"],
                intent=response_data["intent"],
                confidence=response_data["confidence"]
            )
        
        # Executa ações se necessário
        for action in response_data.get("actions", []):
            await execute_bot_action(action, phone, context)
            
    except Exception as e:
        conversation_logger.error("INCOMING_MESSAGE_HANDLER_ERROR", e, message_data)

async def execute_bot_action(action: str, phone: str, context: ConversationContext):
    """Executa ações do bot"""
    try:
        if action == "verificar_pagamento":
            # Lógica para verificar pagamento
            await waha_client.send_text_message(
                phone, 
                "Estou verificando seu pagamento. Em breve retorno com uma confirmação."
            )
            
        elif action == "escalate_to_human":
            # Transfere para atendente humano
            await waha_client.send_text_message(
                phone,
                "Transferindo você para um atendente humano. Aguarde um momento."
            )
            
        elif action == "enviar_informacoes_pagamento":
            # Envia informações detalhadas de pagamento
            info_msg = """📋 Informações para pagamento:

🏦 Dados bancários:
Banco: 001 - Banco do Brasil
Agência: 1234-5
Conta: 12345-6
Favorecido: Sua Empresa

📱 PIX:
Chave: suaempresa@email.com

💳 Cartão de crédito:
Acesse nosso link de pagamento: [link]"""
            
            await waha_client.send_text_message(phone, info_msg)
            
    except Exception as e:
        app_logger.error("BOT_ACTION_EXECUTION_ERROR", e, {"action": action, "phone": phone})

# Registra handlers
webhook_handler.add_message_handler(handle_incoming_message)

# === INICIALIZAÇÃO ===

@app.before_first_request
def initialize_app():
    """Inicialização da aplicação"""
    
    # Valida configuração
    config_validation = active_config.validate_config()
    
    if not config_validation["valid"]:
        app_logger.error("INVALID_CONFIGURATION", data={"issues": config_validation["issues"]})
    else:
        app_logger.info("APPLICATION_INITIALIZED", {
            "debug_mode": config_validation["debug_mode"],
            "waha_configured": config_validation["waha_configured"]
        })

if __name__ == "__main__":
    app.run(
        host=active_config.HOST,
        port=active_config.PORT,
        debug=active_config.DEBUG
    )

