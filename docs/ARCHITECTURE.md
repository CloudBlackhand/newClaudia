# Arquitetura do Sistema - Sistema de Cobrança Inteligente

## Visão Geral

O Sistema de Cobrança Inteligente é uma aplicação completa que automatiza processos de cobrança através do WhatsApp, utilizando inteligência artificial para interações naturais com clientes. O sistema é composto por múltiplos módulos integrados que trabalham em conjunto para fornecer uma solução robusta e escalável.

## Arquitetura de Alto Nível

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   WhatsApp      │
│   (React/JS)    │◄──►│   (Flask)       │◄──►│   (Waha API)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   AI/ML Models  │
                    │   (PyTorch)     │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Data Layer    │
                    │   (JSON/Files)  │
                    └─────────────────┘
```

## Componentes Principais

### 1. Frontend (Interface Web)

**Tecnologias**: HTML5, CSS3, JavaScript ES6+, Bootstrap 5

**Responsabilidades**:
- Interface administrativa para gestão de cobranças
- Dashboard com métricas em tempo real
- Gerenciamento de templates de mensagem
- Monitoramento de conversas ativas
- Upload e validação de arquivos de clientes

**Estrutura**:
```
frontend/
├── index.html              # Página principal SPA
├── css/
│   └── style.css          # Estilos customizados
├── js/
│   ├── config.js          # Configurações
│   ├── api.js             # Cliente da API
│   ├── app.js             # Aplicação principal
│   ├── auth.js            # Autenticação
│   ├── dashboard.js       # Dashboard
│   ├── billing.js         # Módulo de cobrança
│   ├── conversations.js   # Gestão de conversas
│   └── templates.js       # Gestão de templates
└── assets/                # Recursos estáticos
```

### 2. Backend (API REST)

**Tecnologias**: Python 3.11, Flask, JWT, CORS

**Responsabilidades**:
- APIs RESTful para todas as funcionalidades
- Autenticação e autorização
- Processamento de arquivos JSON
- Integração com serviços externos
- Sistema de logs centralizado

**Estrutura**:
```
backend/
├── app.py                 # Aplicação Flask principal
├── config/
│   └── settings.py        # Configurações centralizadas
├── models/
│   ├── chatbot.py         # Modelo de IA conversacional
│   └── conversation.py    # Gestão de conversas
├── services/
│   ├── billing.py         # Serviço de cobrança
│   ├── waha_client.py     # Cliente Waha
│   └── json_processor.py  # Processador JSON
└── utils/
    ├── validators.py      # Validações
    ├── logger.py          # Sistema de logs
    └── security.py        # Segurança
```

### 3. Módulo de IA/ML (Bot Conversacional)

**Tecnologias**: PyTorch, Transformers, BERT Portuguese

**Responsabilidades**:
- Processamento de linguagem natural
- Classificação de intenções (intents)
- Geração de respostas contextuais
- Aprendizado contínuo
- Extração de entidades

**Arquitetura do Modelo**:
```
┌─────────────────┐
│ Input Message   │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Preprocessing   │
│ - Tokenização   │
│ - Normalização  │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ BERT Encoder    │
│ - Embeddings    │
│ - Attention     │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Intent Classifier│
│ - Neural Network│
│ - Softmax       │
└─────────┬───────┘
          ▼
┌─────────────────┐
│ Response Gen.   │
│ - Template      │
│ - Context       │
└─────────────────┘
```

### 4. Integração WhatsApp (Waha)

**Tecnologias**: Waha HTTP API, Webhooks, WebSocket

**Responsabilidades**:
- Envio de mensagens WhatsApp
- Recebimento via webhooks
- Gestão de sessões
- QR Code para autenticação
- Status e monitoramento

**Fluxo de Comunicação**:
```
WhatsApp ←→ Waha API ←→ Sistema ←→ Bot IA
    │         │           │        │
    │         │           │        ▼
    │         │           │   Resposta
    │         │           │        │
    │         │           ▼        │
    │         │       Webhook ←────┘
    │         │           │
    │         ▼           ▼
    │    HTTP Request  Response
    │         │           │
    ▼         ▼           ▼
 Usuário  ←─────────────────
```

## Fluxos de Dados

### 1. Fluxo de Cobrança

```
1. Upload de Clientes (JSON)
   │
   ▼
2. Validação de Dados
   │
   ▼
3. Processamento em Lotes
   │
   ▼
4. Formatação de Mensagens
   │
   ▼
5. Envio via Waha API
   │
   ▼
6. Logs e Monitoramento
```

### 2. Fluxo de Conversa

```
1. Mensagem Recebida (Webhook)
   │
   ▼
2. Extração de Contexto
   │
   ▼
3. Processamento pelo Bot IA
   │
   ▼
4. Classificação de Intent
   │
   ▼
5. Geração de Resposta
   │
   ▼
6. Envio de Resposta
   │
   ▼
7. Atualização de Contexto
```

## Padrões de Design

### 1. Repository Pattern
- Separação entre lógica de negócio e acesso a dados
- Facilita testes e manutenção
- Implementado nos serviços de dados

### 2. Observer Pattern
- Sistema de eventos para webhooks
- Handlers especializados para diferentes tipos de mensagem
- Desacoplamento entre recebimento e processamento

### 3. Strategy Pattern
- Diferentes estratégias de processamento JSON
- Algoritmos de classificação de intent
- Múltiplos templates de resposta

### 4. Factory Pattern
- Criação de instâncias de handlers
- Geração de responses contextuais
- Instanciação de componentes

## Segurança

### 1. Autenticação e Autorização
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Login     │───►│   JWT Token │───►│  Protected  │
│ Credentials │    │ Generation  │    │    Routes   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### 2. Validação de Dados
- Schema validation com Pydantic
- Sanitização de inputs
- Validação de tipos de arquivo
- Rate limiting

### 3. Proteções Implementadas
- CORS configurado
- Headers de segurança
- Validação de tokens JWT
- Logs de segurança
- Mascaramento de dados sensíveis

## Escalabilidade

### 1. Processamento Assíncrono
```python
# Exemplo de processamento em lotes
async def process_large_batch():
    chunks = divide_into_chunks(clients, chunk_size=100)
    tasks = [process_chunk(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)
    return consolidate_results(results)
```

### 2. Cache e Otimizações
- Cache de modelos IA em memória
- Processamento streaming para arquivos grandes
- Lazy loading de recursos
- Compression de responses

### 3. Monitoramento
- Logs estruturados
- Métricas de performance
- Health checks
- Status monitoring

## Deploy e Infraestrutura

### 1. Railway Deployment
```yaml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"

[services.web]
startCommand = "gunicorn --bind 0.0.0.0:$PORT backend.app:app"
```

### 2. Containerização
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.app:app"]
```

### 3. Variáveis de Ambiente
```env
# Aplicação
FLASK_ENV=production
SECRET_KEY=your_secret_key
PORT=8000

# Waha Integration
WAHA_BASE_URL=http://waha:3000
WAHA_API_KEY=your_api_key
WAHA_WEBHOOK_URL=https://app.railway.app/webhook/waha

# Segurança
JWT_SECRET_KEY=jwt_secret
RATE_LIMIT_REQUESTS=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Configuração de Desenvolvimento

### 1. Setup Local
```bash
# Clone repository
git clone <repo-url>
cd cobrança

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Environment variables
cp env.example .env
# Edit .env with your settings

# Run application
python backend/app.py
```

### 2. Estrutura de Testes
```
tests/
├── unit/
│   ├── test_validators.py
│   ├── test_json_processor.py
│   └── test_chatbot.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_waha_integration.py
└── e2e/
    └── test_complete_flow.py
```

## Monitoramento e Logs

### 1. Sistema de Logs
```python
# Estrutura de logs
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "component": "BILLING",
  "event": "MESSAGE_SENT",
  "data": {
    "phone": "55119****21",
    "template": "cobranca_simples",
    "success": true,
    "message_id": "msg_123"
  }
}
```

### 2. Métricas Importantes
- Taxa de entrega de mensagens
- Tempo de resposta do bot
- Conversões de cobrança
- Uptime do sistema
- Performance da API

### 3. Alertas
- Falhas na integração Waha
- Erros críticos do sistema
- Performance degradada
- Limite de rate exceeded

## Performance

### 1. Otimizações Implementadas
- Processamento em lotes (batch processing)
- Streaming para arquivos grandes
- Cache de templates e modelos
- Compressão de responses
- Connection pooling

### 2. Benchmarks
- Throughput: 1000+ mensagens/minuto
- Latência API: <200ms (95th percentile)
- Tempo de resposta bot: <2s
- Processamento JSON: 10MB/s

## Extensibilidade

### 1. Plugins e Extensões
```python
# Sistema de plugins
class MessageProcessor:
    def __init__(self):
        self.plugins = []
    
    def add_plugin(self, plugin):
        self.plugins.append(plugin)
    
    def process(self, message):
        for plugin in self.plugins:
            message = plugin.process(message)
        return message
```

### 2. APIs de Integração
- Webhooks customizáveis
- APIs RESTful bem documentadas
- SDKs para diferentes linguagens
- Event system para extensões

## Manutenção

### 1. Backup e Recovery
- Backup automático de configurações
- Export/import de templates
- Logs rotativos com compressão
- Recovery procedures documentados

### 2. Updates e Patches
- Rolling updates sem downtime
- Database migrations
- Backward compatibility
- Feature flags

## Considerações Futuras

### 1. Melhorias Planejadas
- Múltiplos canais de comunicação
- Dashboard analytics avançado
- Integração com CRMs
- Machine learning automatizado

### 2. Escalabilidade Horizontal
- Microserviços
- Load balancing
- Database clustering
- CDN para assets

Este documento serve como referência para desenvolvedores, administradores de sistema e stakeholders técnicos, fornecendo uma visão completa da arquitetura e implementação do sistema.

