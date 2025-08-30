# API Documentation - Sistema de Cobrança Inteligente

## Visão Geral

Esta documentação descreve as APIs do Sistema de Cobrança Inteligente, um sistema automatizado de cobrança com bot conversacional integrado ao WhatsApp via Waha.

**Base URL**: `https://seu-app.railway.app`

**Versão**: 1.0.0

## Autenticação

O sistema utiliza autenticação JWT Bearer Token.

### Login
```http
POST /auth/login
```

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": "admin"
}
```

**Headers para requisições autenticadas**:
```
Authorization: Bearer {access_token}
```

## Endpoints

### Sistema

#### Health Check
```http
GET /health
```

Verifica se o sistema está funcionando.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Cobrança

#### Enviar Lote de Cobrança
```http
POST /api/billing/send-batch
```

Envia mensagens de cobrança para um lote de clientes.

**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "clients_file": "data/clients.json",
  "template_name": "cobranca_simples",
  "filters": {
    "min_amount": 100,
    "max_amount": 1000
  },
  "delay_seconds": 2
}
```

**Response**:
```json
{
  "success": true,
  "batch_id": "batch_20240115_103000",
  "total_clients": 25,
  "processed": 25,
  "successful": 23,
  "failed": 2,
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T10:32:15Z",
  "duration": 135.5
}
```

#### Enviar Mensagem Única
```http
POST /api/billing/send-single
```

Envia mensagem para um cliente específico.

**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "client": {
    "id": "001",
    "name": "João Silva",
    "phone": "5511987654321",
    "amount": 150.50,
    "due_date": "2024-01-15",
    "description": "Mensalidade janeiro"
  },
  "template_name": "cobranca_simples"
}
```

**Response**:
```json
{
  "success": true,
  "message_id": "msg_abc123",
  "error": null
}
```

#### Validar Configuração
```http
POST /api/billing/validate
```

Valida configuração antes de enviar lote.

**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "clients_file": "data/clients.json",
  "template_name": "cobranca_simples"
}
```

**Response**:
```json
{
  "valid": true,
  "issues": [],
  "warnings": ["Lista muito grande (>1000 itens)"],
  "client_stats": {
    "file_exists": true,
    "file_size_mb": 0.5,
    "estimated_count": 250,
    "processing_method": "standard"
  },
  "waha_status": {
    "success": true,
    "status": "WORKING"
  },
  "template_info": {
    "name": "cobranca_simples",
    "length": 256,
    "variables": ["name", "amount", "due_date"]
  }
}
```

#### Status do Lote
```http
GET /api/billing/batch-status
```

Retorna status do lote em execução.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "batch_id": "batch_20240115_103000",
  "total_clients": 100,
  "processed": 45,
  "successful": 43,
  "failed": 2,
  "is_running": true,
  "progress_percentage": 45.0,
  "current_duration": 90.5
}
```

#### Listar Templates
```http
GET /api/billing/templates
```

Lista templates de mensagem disponíveis.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "cobranca_simples": {
    "content": "Olá {name}! 👋\n\nEste é um lembrete...",
    "length": 256,
    "variables": ["name", "amount", "due_date"],
    "valid": true,
    "preview": "Olá {name}! 👋\n\nEste é um lembrete..."
  },
  "cobranca_urgente": {
    "content": "⚠️ {name}, PAGAMENTO EM ATRASO ⚠️...",
    "length": 312,
    "variables": ["name", "amount", "due_date"],
    "valid": true,
    "preview": "⚠️ {name}, PAGAMENTO EM ATRASO ⚠️..."
  }
}
```

#### Adicionar Template
```http
POST /api/billing/templates
```

Adiciona novo template de mensagem.

**Headers**: `Authorization: Bearer {token}`

**Request Body**:
```json
{
  "name": "novo_template",
  "content": "Olá {name}! Seu pagamento de {amount} vence em {due_date}."
}
```

**Response**:
```json
{
  "message": "Template adicionado com sucesso"
}
```

### Chat/Conversas

#### Processar Mensagem
```http
POST /api/chat/process
```

Processa mensagem do chat com o bot.

**Request Body**:
```json
{
  "phone": "5511987654321",
  "message": "Olá, quero negociar minha dívida"
}
```

**Response**:
```json
{
  "response": "Olá! Entendo que você gostaria de negociar. Temos opções de parcelamento disponíveis!",
  "intent": "negociacao",
  "confidence": 0.87,
  "actions": ["oferecer_negociacao"]
}
```

#### Histórico da Conversa
```http
GET /api/chat/conversation/{phone}?limit=50
```

Obtém histórico de conversa com um cliente.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "phone": "5511987654321",
  "messages": [
    {
      "role": "user",
      "content": "Olá",
      "timestamp": "2024-01-15T10:30:00Z",
      "message_id": null,
      "intent": null,
      "confidence": null
    },
    {
      "role": "assistant", 
      "content": "Olá! Como posso ajudá-lo hoje?",
      "timestamp": "2024-01-15T10:30:05Z",
      "message_id": "msg_123",
      "intent": "saudacao",
      "confidence": 0.95
    }
  ],
  "summary": {
    "exists": true,
    "total_messages": 10,
    "user_messages": 5,
    "bot_messages": 5,
    "last_message_time": "2024-01-15T10:35:00Z",
    "last_intent": "negociacao",
    "last_confidence": 0.87,
    "context": {
      "phone": "5511987654321",
      "client_name": "João Silva",
      "client_amount": 150.50,
      "payment_status": "negotiating"
    }
  }
}
```

#### Estatísticas das Conversas
```http
GET /api/chat/conversations/stats
```

Estatísticas das conversas ativas.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "total_conversations": 45,
  "total_messages": 320,
  "conversations_by_status": {
    "pending": 20,
    "negotiating": 15,
    "paid": 8,
    "disputed": 2
  },
  "recent_activity": 12
}
```

### WhatsApp (Waha)

#### Status da Sessão
```http
GET /api/waha/status
```

Verifica status da sessão WhatsApp.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "status": "WORKING",
  "data": {
    "name": "default",
    "status": "WORKING",
    "config": {
      "webhooks": [
        {
          "url": "https://seu-app.railway.app/webhook/waha",
          "events": ["message", "message.any", "state.change"]
        }
      ]
    }
  }
}
```

#### Iniciar Sessão
```http
POST /api/waha/start
```

Inicia sessão WhatsApp.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "error": null
}
```

#### Parar Sessão  
```http
POST /api/waha/stop
```

Para sessão WhatsApp.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "error": null
}
```

#### Obter QR Code
```http
GET /api/waha/qr
```

Obtém QR code para autenticação.

**Headers**: `Authorization: Bearer {token}`

**Response**:
```json
{
  "success": true,
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "error": null
}
```

### Upload

#### Upload de Arquivo de Clientes
```http
POST /api/upload/clients
```

Faz upload de arquivo JSON com dados dos clientes.

**Headers**: 
- `Authorization: Bearer {token}`
- `Content-Type: multipart/form-data`

**Request Body**: FormData com campo `file`

**Response**:
```json
{
  "message": "Arquivo enviado com sucesso",
  "filename": "20240115_103000_clients.json",
  "path": "data/uploads/20240115_103000_clients.json"
}
```

### Webhooks

#### Webhook Waha
```http
POST /webhook/waha
```

Recebe webhooks do Waha (chamado automaticamente).

**Request Body**:
```json
{
  "event": "message",
  "session": "default",
  "payload": {
    "id": "msg_abc123",
    "from": "5511987654321",
    "to": "5511888888888",
    "body": "Olá, quero negociar",
    "type": "text",
    "timestamp": 1705312200
  }
}
```

**Response**:
```json
{
  "status": "processed"
}
```

## Códigos de Status

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Requisição inválida
- `401` - Não autorizado
- `403` - Proibido
- `404` - Não encontrado
- `413` - Arquivo muito grande
- `500` - Erro interno do servidor

## Modelos de Dados

### Cliente
```json
{
  "id": "string", // Identificador único
  "name": "string", // Nome do cliente (2-100 caracteres)
  "phone": "string", // Telefone no formato +55XXXXXXXXXXX
  "amount": "number", // Valor da cobrança (> 0, <= 999999.99)
  "due_date": "string", // Data de vencimento (YYYY-MM-DD) [opcional]
  "description": "string" // Descrição da cobrança [opcional]
}
```

### Mensagem de Conversa
```json
{
  "role": "string", // "user" ou "assistant"
  "content": "string", // Conteúdo da mensagem
  "timestamp": "string", // ISO 8601 timestamp
  "message_id": "string", // ID da mensagem [opcional]
  "intent": "string", // Intenção detectada [opcional]
  "confidence": "number" // Confiança da classificação [opcional]
}
```

### Template de Mensagem
```json
{
  "name": "string", // Nome do template
  "content": "string", // Conteúdo com variáveis {name}, {amount}, etc.
  "variables": ["string"], // Lista de variáveis encontradas
  "valid": "boolean", // Se o template é válido
  "length": "number" // Tamanho em caracteres
}
```

## Tratamento de Erros

Todas as respostas de erro seguem o formato:

```json
{
  "error": "Descrição do erro"
}
```

### Exemplos de Erros Comuns

**400 - Dados inválidos**:
```json
{
  "error": "clients_file e template_name são obrigatórios"
}
```

**401 - Token inválido**:
```json
{
  "error": "Token de acesso inválido"
}
```

**404 - Recurso não encontrado**:
```json
{
  "error": "Template 'inexistente' não encontrado"
}
```

**500 - Erro interno**:
```json
{
  "error": "Erro interno do servidor"
}
```

## Rate Limiting

O sistema implementa rate limiting para proteger contra abuso:

- **100 requisições por hora** por IP
- Headers de resposta incluem informações sobre limite:
  - `X-RateLimit-Limit`: Limite total
  - `X-RateLimit-Remaining`: Requisições restantes
  - `X-RateLimit-Reset`: Timestamp do reset

## Webhooks

### Configuração
Para receber webhooks do Waha, configure:

1. **URL**: `https://seu-app.railway.app/webhook/waha`
2. **Eventos**: `["message", "message.any", "state.change"]`
3. **Método**: `POST`

### Segurança
- Valide origem dos webhooks
- Use HTTPS sempre
- Implemente retry logic para failures

## Exemplos de Uso

### Fluxo Completo de Cobrança

1. **Upload de clientes**:
```bash
curl -X POST https://seu-app.railway.app/api/upload/clients \
  -H "Authorization: Bearer {token}" \
  -F "file=@clients.json"
```

2. **Validar configuração**:
```bash
curl -X POST https://seu-app.railway.app/api/billing/validate \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"clients_file": "uploaded_file.json", "template_name": "cobranca_simples"}'
```

3. **Enviar lote**:
```bash
curl -X POST https://seu-app.railway.app/api/billing/send-batch \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"clients_file": "uploaded_file.json", "template_name": "cobranca_simples", "delay_seconds": 2}'
```

4. **Monitorar progresso**:
```bash
curl -X GET https://seu-app.railway.app/api/billing/batch-status \
  -H "Authorization: Bearer {token}"
```

### Interação com Bot

```bash
curl -X POST https://seu-app.railway.app/api/chat/process \
  -H "Content-Type: application/json" \
  -d '{"phone": "5511987654321", "message": "Quero parcelar minha dívida"}'
```

## SDKs e Bibliotecas

### JavaScript/Node.js
```javascript
const API_BASE = 'https://seu-app.railway.app';
let authToken = null;

async function login(username, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  authToken = data.access_token;
  return data;
}

async function sendBatch(clientsFile, templateName) {
  const response = await fetch(`${API_BASE}/api/billing/send-batch`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${authToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      clients_file: clientsFile,
      template_name: templateName
    })
  });
  return response.json();
}
```

### Python
```python
import requests

class BillingAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(f"{self.base_url}/auth/login", 
                               json={"username": username, "password": password})
        data = response.json()
        self.token = data.get("access_token")
        return data
    
    def send_batch(self, clients_file, template_name):
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"clients_file": clients_file, "template_name": template_name}
        response = requests.post(f"{self.base_url}/api/billing/send-batch",
                               json=data, headers=headers)
        return response.json()

# Uso
api = BillingAPI("https://seu-app.railway.app")
api.login("admin", "admin123")
result = api.send_batch("clients.json", "cobranca_simples")
```

## Notas de Versão

### v1.0.0
- Implementação inicial
- APIs de cobrança e chat
- Integração com Waha
- Sistema de templates
- Autenticação JWT

## Suporte

Para suporte técnico ou dúvidas sobre a API, entre em contato através dos canais disponíveis.

