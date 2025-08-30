# Documentação da API

## Visão Geral

O Sistema de Cobrança Avançado fornece uma API REST completa para gerenciar operações de cobrança e conversação inteligente.

### Base URL
```
https://seu-app.railway.app/api
```

### Autenticação
Atualmente o sistema não requer autenticação para endpoints públicos. Para produção, configure as variáveis de ambiente de segurança.

## Endpoints

### 🏥 Health Check

#### `GET /health`
Verificar saúde do sistema

**Resposta:**
```json
{
  "status": "healthy",
  "modules": {
    "billing_dispatcher": true,
    "conversation_bot": true,
    "waha_integration": true
  }
}
```

### 💰 Endpoints de Cobrança

#### `POST /api/billing/process-json`
Processar arquivo JSON com dados de cobrança

**Parâmetros:**
- `json_data` (form): String JSON com dados dos clientes
- `template` (form, opcional): Template personalizado de mensagem

**Exemplo:**
```bash
curl -X POST "https://seu-app.railway.app/api/billing/process-json" \
  -F "json_data=[{\"nome\":\"João\",\"telefone\":\"+5511999999999\",\"valor\":\"100.00\"}]" \
  -F "template=Olá {nome}, você deve R$ {valor}"
```

**Resposta:**
```json
{
  "success": true,
  "message": "Processamento iniciado",
  "records_count": 1
}
```

#### `POST /api/billing/upload-file`
Upload de arquivo JSON

**Parâmetros:**
- `file` (multipart): Arquivo JSON
- `template` (form, opcional): Template personalizado

**Resposta:**
```json
{
  "success": true,
  "message": "Arquivo processado com sucesso",
  "filename": "clientes.json",
  "records_count": 50
}
```

#### `GET /api/billing/validate-json`
Validar estrutura de JSON

**Parâmetros:**
- `json_data` (query): String JSON para validar

**Resposta:**
```json
{
  "is_valid": true,
  "records_count": 10,
  "data": [...]
}
```

#### `GET /api/billing/validate-template`
Validar template de mensagem

**Parâmetros:**
- `template` (query): Template para validar

**Resposta:**
```json
{
  "is_valid": true,
  "placeholders_found": ["{nome}", "{valor}"],
  "template_length": 50
}
```

#### `GET /api/billing/stats`
Obter estatísticas de processamento

**Resposta:**
```json
{
  "is_healthy": true,
  "queue_size": 0,
  "workers_running": true
}
```

#### `GET /api/billing/logs`
Obter logs de operações

**Parâmetros:**
- `limit` (query, opcional): Número máximo de logs (padrão: 100)

**Resposta:**
```json
{
  "operation_logs": [...],
  "message_logs": [...]
}
```

#### `GET /api/billing/report`
Gerar relatório de atividades

**Parâmetros:**
- `start_date` (query, opcional): Data inicial (ISO format)

**Resposta:**
```json
{
  "report_timestamp": "2024-01-15T10:30:00",
  "operations": {
    "total": 100,
    "successful": 95,
    "failed": 5,
    "success_rate": 95.0
  },
  "messages": {
    "total": 500,
    "successful": 485,
    "failed": 15,
    "success_rate": 97.0
  }
}
```

### 🤖 Endpoints de Conversação

#### `POST /api/conversation/send-message`
Enviar mensagem para o bot

**Parâmetros:**
```json
{
  "user_phone": "+5511999999999",
  "message": "Olá",
  "context": {}
}
```

**Resposta:**
```json
{
  "success": true,
  "bot_response": "Olá! Como posso ajudá-lo?",
  "intent": "saudacao",
  "confidence": 0.95,
  "suggested_actions": ["continuar_conversa"],
  "requires_human": false
}
```

#### `GET /api/conversation/conversation-history/{user_phone}`
Obter histórico de conversa

**Resposta:**
```json
{
  "success": true,
  "user_phone": "+5511999999999",
  "conversation_history": [
    {
      "timestamp": "2024-01-15T10:30:00",
      "type": "user",
      "message": "Olá",
      "intent": "saudacao",
      "sentiment": "neutro"
    },
    {
      "timestamp": "2024-01-15T10:30:01",
      "type": "bot",
      "message": "Olá! Como posso ajudá-lo?",
      "intent": "saudacao",
      "confidence": 0.95
    }
  ]
}
```

#### `GET /api/conversation/active-sessions`
Obter número de sessões ativas

**Resposta:**
```json
{
  "success": true,
  "active_sessions": 25
}
```

#### `GET /api/conversation/conversation-logs`
Obter logs de conversas

**Parâmetros:**
- `session_id` (query, opcional): ID da sessão específica
- `limit` (query, opcional): Número máximo de logs

**Resposta:**
```json
{
  "success": true,
  "conversation_logs": [...]
}
```

#### `GET /api/conversation/bot-stats`
Obter estatísticas do bot

**Resposta:**
```json
{
  "success": true,
  "is_healthy": true,
  "active_sessions": 25,
  "is_initialized": true
}
```

### 📱 Endpoints de WhatsApp (Webhooks)

#### `POST /api/webhooks/waha`
Receber webhooks do Waha

**Headers:**
- `X-Signature` (opcional): Assinatura do webhook
- `Authorization` (opcional): Token de autorização

**Body:**
```json
{
  "event": "message.text",
  "payload": {
    "from": "+5511999999999",
    "body": "Olá",
    "fromMe": false,
    "type": "text"
  }
}
```

**Resposta:**
```json
{
  "success": true,
  "processed": true,
  "result": {
    "processed": true,
    "user_phone": "+5511999999999",
    "user_message": "Olá",
    "bot_response": "Olá! Como posso ajudá-lo?",
    "requires_human": false
  }
}
```

#### `GET /api/webhooks/waha/status`
Obter status da integração Waha

**Resposta:**
```json
{
  "success": true,
  "waha_status": {
    "status": "WORKING",
    "connected": true
  },
  "integration_stats": {
    "is_initialized": true,
    "connection_status": "connected",
    "base_url": "https://waha.example.com",
    "session_name": "default"
  }
}
```

#### `POST /api/webhooks/send-message`
Enviar mensagem via WhatsApp

**Parâmetros:**
- `to_number` (query): Número de destino
- `message` (query): Mensagem a ser enviada

**Resposta:**
```json
{
  "success": true,
  "message_id": "msg_123456789",
  "result": {
    "success": true,
    "message_id": "msg_123456789"
  }
}
```

#### `POST /api/webhooks/send-bulk`
Enviar múltiplas mensagens

**Body:**
```json
[
  {
    "to": "+5511999999999",
    "message": "Mensagem 1"
  },
  {
    "to": "+5511888888888",
    "message": "Mensagem 2"
  }
]
```

**Resposta:**
```json
{
  "success": true,
  "bulk_result": {
    "total_messages": 2,
    "successful_sends": 2,
    "failed_sends": 0,
    "results": [...]
  }
}
```

#### `GET /api/webhooks/webhook-logs`
Obter logs de webhooks

**Parâmetros:**
- `limit` (query, opcional): Número máximo de logs

**Resposta:**
```json
{
  "success": true,
  "webhook_logs": [...]
}
```

## Códigos de Status

- `200` - Sucesso
- `400` - Erro na requisição (dados inválidos)
- `401` - Não autorizado
- `404` - Recurso não encontrado
- `500` - Erro interno do servidor

## Estrutura de Dados

### Cliente (JSON de entrada)
```json
{
  "nome": "João Silva",           // Obrigatório
  "telefone": "+5511999999999",   // Obrigatório
  "valor": "150,00",              // Obrigatório
  "vencimento": "15/12/2024",     // Opcional
  "descricao": "Mensalidade",     // Opcional
  "email": "joao@email.com"       // Opcional
}
```

### Placeholders do Template
- `{nome}` - Nome do cliente
- `{valor}` - Valor formatado
- `{vencimento}` - Data de vencimento
- `{descricao}` - Descrição da cobrança

### Eventos de Webhook Suportados
- `message.text` - Mensagem de texto recebida
- `session.status` - Status da sessão
- `state.change` - Mudança de estado
- `qr` - QR Code para autenticação
- `ready` - WhatsApp pronto
- `auth_failure` - Falha na autenticação

## Exemplos de Uso

### Upload e Processamento Completo
```bash
# 1. Validar JSON
curl -G "https://seu-app.railway.app/api/billing/validate-json" \
  --data-urlencode 'json_data=[{"nome":"João","telefone":"+5511999999999","valor":"100.00"}]'

# 2. Validar template
curl -G "https://seu-app.railway.app/api/billing/validate-template" \
  --data-urlencode 'template=Olá {nome}, você deve R$ {valor}'

# 3. Processar dados
curl -X POST "https://seu-app.railway.app/api/billing/process-json" \
  -F "json_data=[{\"nome\":\"João\",\"telefone\":\"+5511999999999\",\"valor\":\"100.00\"}]" \
  -F "template=Olá {nome}, você deve R$ {valor}"

# 4. Acompanhar progresso
curl "https://seu-app.railway.app/api/billing/stats"
```

### Simulação de Conversa
```bash
# 1. Enviar mensagem do usuário
curl -X POST "https://seu-app.railway.app/api/conversation/send-message" \
  -H "Content-Type: application/json" \
  -d '{"user_phone":"+5511999999999","message":"Olá"}'

# 2. Ver histórico
curl "https://seu-app.railway.app/api/conversation/conversation-history/+5511999999999"
```

## Monitoramento

### Verificar Saúde
```bash
curl "https://seu-app.railway.app/health"
```

### Obter Relatórios
```bash
# Relatório geral
curl "https://seu-app.railway.app/api/billing/report"

# Logs recentes
curl "https://seu-app.railway.app/api/billing/logs?limit=50"

# Estatísticas do bot
curl "https://seu-app.railway.app/api/conversation/bot-stats"
```
