# Documentação da API - Sistema de Cobrança Inteligente

Esta documentação detalha todos os endpoints disponíveis no sistema.

## 📋 Índice

- [Autenticação](#autenticação)
- [API de Cobrança](#api-de-cobrança)
- [API de Conversação](#api-de-conversação)
- [API de Webhooks](#api-de-webhooks)
- [Códigos de Erro](#códigos-de-erro)
- [Exemplos Práticos](#exemplos-práticos)

## 🔐 Autenticação

### Headers Obrigatórios
```http
Content-Type: application/json
X-API-Key: sua_api_key_aqui (opcional, se configurada)
```

### Webhooks
```http
X-Hub-Signature-256: sha256=hash_hmac_sha256 (se WEBHOOK_SECRET configurado)
```

## 💰 API de Cobrança

Base URL: `/api/billing`

### Health Check
Verifica status do módulo de cobrança.

```http
GET /api/billing/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "billing",
  "statistics": {
    "total_messages": 150,
    "sent_messages": 142,
    "pending_messages": 8
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### Validar Clientes
Valida estrutura e dados de clientes sem enviar mensagens.

```http
POST /api/billing/validate-clients
```

**Request Body:**
```json
{
  "clients": [
    {
      "name": "João Silva",
      "phone": "11999999999",
      "amount": 150.50,
      "due_date": "2024-12-31",
      "email": "joao@email.com",
      "cpf": "123.456.789-01",
      "description": "Mensalidade dezembro"
    }
  ]
}
```

**Response (Sucesso):**
```json
{
  "valid": true,
  "client_count": 1,
  "clients_preview": [
    {
      "id": "client_0_123456",
      "name": "João Silva",
      "phone": "+5511999999999",
      "amount": 150.50,
      "due_date": "2024-12-31",
      "email": "joao@email.com"
    }
  ],
  "message": "1 clientes validados com sucesso"
}
```

**Response (Erro):**
```json
{
  "valid": false,
  "errors": [
    "client[0].phone: Formato de telefone inválido",
    "client[0].amount: Valor deve ser positivo"
  ],
  "client_count": 0
}
```

### Enviar Lote de Cobranças
Processa e envia mensagens de cobrança para lista de clientes.

```http
POST /api/billing/send-batch
```

**Request Body:**
```json
{
  "clients": [
    {
      "name": "João Silva",
      "phone": "11999999999",
      "amount": 150.50,
      "due_date": "2024-12-31"
    }
  ],
  "template_id": "initial_br",
  "schedule_time": "2024-12-25T10:00:00"
}
```

**Parâmetros:**
- `clients` (array, obrigatório): Lista de clientes
- `template_id` (string, opcional): ID do template (padrão: "initial_br")
- `schedule_time` (string, opcional): Data/hora para agendamento (ISO 8601)

**Response:**
```json
{
  "success": true,
  "message": "Lote de cobrança processado",
  "result": {
    "total_messages": 1,
    "successful": 1,
    "failed": 0,
    "skipped": 0,
    "execution_time": 1.25,
    "errors": []
  }
}
```

### Obter Templates
Lista todos os templates de mensagem disponíveis.

```http
GET /api/billing/templates
```

**Response:**
```json
{
  "templates": {
    "initial_br": {
      "id": "initial_br",
      "type": "initial",
      "subject": "Cobrança - Vencimento {due_date}",
      "content": "Olá {client_name}! Temos uma cobrança...",
      "variables": ["client_name", "amount", "due_date"],
      "priority": 1
    }
  },
  "count": 4
}
```

### Testar Template
Renderiza template com variáveis fornecidas.

```http
POST /api/billing/test-template
```

**Request Body:**
```json
{
  "template_id": "initial_br",
  "variables": {
    "client_name": "João Silva",
    "amount": "150.50",
    "due_date": "31/12/2024"
  }
}
```

**Response:**
```json
{
  "template_id": "initial_br",
  "variables": {
    "client_name": "João Silva",
    "amount": "150.50",
    "due_date": "31/12/2024"
  },
  "rendered": "Olá João Silva! Temos uma cobrança pendente..."
}
```

### Reenviar Mensagens Falhadas
Reprocessa mensagens que falharam anteriormente.

```http
POST /api/billing/retry-failed
```

**Response:**
```json
{
  "success": true,
  "message": "Retry de mensagens concluído",
  "result": {
    "total_messages": 5,
    "successful": 3,
    "failed": 2,
    "execution_time": 2.1,
    "errors": [
      "Falha ao enviar para +5511888888888"
    ]
  }
}
```

### Obter Estatísticas
Retorna estatísticas detalhadas do sistema de cobrança.

```http
GET /api/billing/statistics
```

**Response:**
```json
{
  "billing_stats": {
    "total_messages": 500,
    "sent_messages": 475,
    "pending_messages": 25,
    "status_breakdown": {
      "sent": 475,
      "pending": 20,
      "failed": 5
    },
    "templates_available": 4
  },
  "logger_stats": {
    "total_logs": 1250,
    "errors": 15,
    "warnings": 45,
    "uptime_seconds": 86400
  }
}
```

## 💬 API de Conversação

Base URL: `/api/conversation`

### Health Check
Verifica status do módulo de conversação.

```http
GET /api/conversation/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "conversation",
  "statistics": {
    "total_contexts": 25,
    "active_contexts": 18,
    "total_messages": 342,
    "average_messages_per_context": 13.7
  }
}
```

### Processar Mensagem
Processa mensagem do usuário com IA e gera resposta.

```http
POST /api/conversation/process-message
```

**Request Body:**
```json
{
  "phone": "+5511999999999",
  "message": "Oi, recebi uma cobrança de vocês",
  "user_name": "João Silva",
  "auto_reply": true
}
```

**Parâmetros:**
- `phone` (string, obrigatório): Telefone do usuário
- `message` (string, obrigatório): Mensagem do usuário
- `user_name` (string, opcional): Nome do usuário
- `auto_reply` (boolean, opcional): Enviar resposta automaticamente (padrão: true)

**Response:**
```json
{
  "success": true,
  "response": {
    "text": "Olá João! Obrigado por entrar em contato. Como posso ajudá-lo?",
    "type": "informative",
    "confidence": 0.95,
    "should_escalate": false,
    "suggested_actions": [
      "Verificar dados da cobrança",
      "Fornecer informações de pagamento"
    ]
  },
  "auto_reply_sent": true,
  "phone": "+5511999999999"
}
```

### Analisar Mensagem
Analisa mensagem sem gerar resposta ou atualizar contexto.

```http
POST /api/conversation/analyze-message
```

**Request Body:**
```json
{
  "message": "Posso parcelar em 3 vezes?"
}
```

**Response:**
```json
{
  "analysis": {
    "intent": "negotiation",
    "sentiment": "neutral",
    "confidence": 0.87,
    "entities": {
      "money": ["3"]
    },
    "keywords": ["parcelar", "vezes"]
  },
  "message": "Posso parcelar em 3 vezes?"
}
```

### Obter Contextos Ativos
Lista conversas ativas no sistema.

```http
GET /api/conversation/contexts?phone=11999&limit=20
```

**Parâmetros de Query:**
- `phone` (string, opcional): Filtro por telefone
- `limit` (integer, opcional): Limite de resultados (padrão: 50)

**Response:**
```json
{
  "contexts": [
    {
      "phone": "+5511999999999",
      "session_id": "session_123",
      "user_name": "João Silva",
      "started_at": "2024-01-01T09:00:00Z",
      "last_activity": "2024-01-01T09:15:00Z",
      "message_count": 5,
      "topics_discussed": ["greeting", "payment_question"],
      "recent_intents": ["greeting", "payment_question", "negotiation"],
      "recent_sentiments": ["neutral", "positive", "neutral"]
    }
  ],
  "total_count": 25,
  "filtered_count": 1
}
```

### Obter Detalhes do Contexto
Retorna informações detalhadas de uma conversa específica.

```http
GET /api/conversation/contexts/{phone}
```

**Response:**
```json
{
  "context": {
    "phone": "+5511999999999",
    "session_id": "session_123",
    "user_name": "João Silva",
    "started_at": "2024-01-01T09:00:00Z",
    "last_activity": "2024-01-01T09:15:00Z",
    "message_count": 5,
    "payment_amount": 150.50,
    "due_date": "2024-12-31",
    "topics_discussed": ["greeting", "payment_question", "negotiation"],
    "intent_history": ["greeting", "payment_question", "negotiation", "payment_confirmation"],
    "sentiment_history": ["neutral", "positive", "neutral", "positive"]
  }
}
```

### Excluir Contexto
Remove contexto de conversa do sistema.

```http
DELETE /api/conversation/contexts/{phone}
```

**Response:**
```json
{
  "success": true,
  "message": "Contexto de +5511999999999 excluído com sucesso"
}
```

### Testar NLP
Testa capacidades de processamento de linguagem natural.

```http
POST /api/conversation/test-nlp
```

**Request Body:**
```json
{
  "messages": [
    "Olá, tudo bem?",
    "Quanto devo pagar?",
    "Já paguei ontem via PIX"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "message": "Olá, tudo bem?",
      "intent": "greeting",
      "sentiment": "positive",
      "confidence": 0.92,
      "entities": {},
      "keywords": ["olá", "tudo", "bem"]
    }
  ],
  "count": 3
}
```

## 🔗 API de Webhooks

Base URL: `/api/webhook`

### Health Check
Verifica status do módulo de webhooks.

```http
GET /api/webhook/health
```

**Response:**
```json
{
  "status": "healthy",
  "module": "webhook",
  "services": {
    "conversation_bot": "initialized",
    "waha_integration": "healthy"
  },
  "configuration": {
    "webhook_secret_configured": true,
    "waha_url_configured": true
  }
}
```

### Webhook do WhatsApp
Recebe webhooks do Waha para processar mensagens.

```http
POST /api/webhook/whatsapp
```

**Headers:**
```http
Content-Type: application/json
X-Hub-Signature-256: sha256=hash_calculado_com_webhook_secret
```

**Request Body (Mensagem):**
```json
{
  "event": "message",
  "session": "default",
  "payload": {
    "id": "msg_123456",
    "timestamp": 1640995200,
    "fromMe": false,
    "from": "5511999999999@c.us",
    "chatId": "5511999999999@c.us",
    "type": "text",
    "body": "Olá, recebi uma cobrança"
  }
}
```

**Response:**
```json
{
  "status": "processed",
  "message": "Mensagem processada com sucesso",
  "response_sent": true,
  "should_escalate": false,
  "phone": "5511999999999"
}
```

**Request Body (Status da Sessão):**
```json
{
  "event": "session.status",
  "session": "default",
  "payload": {
    "name": "default",
    "status": "WORKING"
  }
}
```

**Response:**
```json
{
  "status": "processed",
  "session": "default",
  "new_status": "WORKING"
}
```

### Webhook de Teste
Endpoint para testar funcionalidade de webhooks.

```http
POST /api/webhook/test
```

**Request Body:**
```json
{
  "test": "data",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

**Response:**
```json
{
  "status": "test_successful",
  "message": "Webhook de teste processado",
  "received_data": {
    "test": "data",
    "timestamp": "2024-01-01T10:00:00Z"
  },
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## 🏥 Health Check Geral
Verifica status geral da aplicação.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Sistema de Cobrança Inteligente",
  "version": "1.0.0"
}
```

## ❌ Códigos de Erro

### Códigos HTTP
- `200` - Sucesso
- `400` - Requisição inválida
- `401` - Não autorizado
- `404` - Recurso não encontrado
- `500` - Erro interno do servidor

### Estrutura de Erro
```json
{
  "error": "Descrição breve do erro",
  "message": "Descrição detalhada do que aconteceu",
  "status": 400,
  "details": {
    "field": "campo_com_erro",
    "validation_errors": ["Lista de erros específicos"]
  }
}
```

### Erros Comuns

#### 400 - Bad Request
```json
{
  "error": "Dados inválidos",
  "message": "Os dados fornecidos não passaram na validação",
  "status": 400,
  "validation_errors": [
    "client[0].phone: Formato de telefone inválido",
    "client[0].amount: Valor deve ser positivo"
  ]
}
```

#### 401 - Unauthorized
```json
{
  "error": "Não autorizado",
  "message": "API Key inválida ou ausente",
  "status": 401
}
```

#### 404 - Not Found
```json
{
  "error": "Recurso não encontrado",
  "message": "O contexto solicitado não existe",
  "status": 404
}
```

#### 500 - Internal Server Error
```json
{
  "error": "Erro interno do servidor",
  "message": "Ocorreu um erro inesperado no processamento",
  "status": 500
}
```

## 📝 Exemplos Práticos

### Fluxo Completo de Cobrança

#### 1. Validar Dados
```bash
curl -X POST https://seu-app.railway.app/api/billing/validate-clients \
  -H "Content-Type: application/json" \
  -d '{
    "clients": [
      {
        "name": "João Silva",
        "phone": "11999999999",
        "amount": 150.50,
        "due_date": "2024-12-31"
      }
    ]
  }'
```

#### 2. Enviar Cobranças
```bash
curl -X POST https://seu-app.railway.app/api/billing/send-batch \
  -H "Content-Type: application/json" \
  -d '{
    "clients": [
      {
        "name": "João Silva",
        "phone": "11999999999",
        "amount": 150.50,
        "due_date": "2024-12-31"
      }
    ],
    "template_id": "initial_br"
  }'
```

#### 3. Monitorar Estatísticas
```bash
curl -X GET https://seu-app.railway.app/api/billing/statistics
```

### Interação com Conversação

#### 1. Processar Mensagem
```bash
curl -X POST https://seu-app.railway.app/api/conversation/process-message \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5511999999999",
    "message": "Oi, quero negociar minha dívida",
    "user_name": "João Silva",
    "auto_reply": false
  }'
```

#### 2. Analisar Intent
```bash
curl -X POST https://seu-app.railway.app/api/conversation/analyze-message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Posso parcelar em 5 vezes?"
  }'
```

#### 3. Verificar Contextos
```bash
curl -X GET "https://seu-app.railway.app/api/conversation/contexts?limit=10"
```

### Configuração de Webhook

#### 1. Configurar no Waha
```bash
curl -X POST https://sua-waha.com/api/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default",
    "config": {
      "webhooks": [
        {
          "url": "https://seu-app.railway.app/api/webhook/whatsapp",
          "events": ["message", "session.status"]
        }
      ]
    }
  }'
```

#### 2. Testar Webhook
```bash
curl -X POST https://seu-app.railway.app/api/webhook/test \
  -H "Content-Type: application/json" \
  -d '{
    "test": "webhook funcionando",
    "timestamp": "2024-01-01T10:00:00Z"
  }'
```

## 🔧 Rate Limiting

### Limites Padrão
- **Cobrança**: 10 mensagens/minuto
- **Conversação**: 60 mensagens/minuto
- **Webhooks**: 100 requisições/minuto

### Headers de Rate Limit
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995260
```

### Erro de Rate Limit
```json
{
  "error": "Rate limit excedido",
  "message": "Muitas requisições. Tente novamente em 60 segundos",
  "status": 429,
  "retry_after": 60
}
```

## 📊 Paginação

Para endpoints que retornam listas, use os parâmetros:
- `limit`: Número máximo de itens (padrão: 50, máximo: 100)
- `offset`: Número de itens para pular (padrão: 0)

**Response com Paginação:**
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 150,
    "has_next": true
  }
}
```

---

Esta documentação é mantida atualizada com cada versão do sistema. Para dúvidas ou sugestões, consulte o [README.md](../README.md) principal.
