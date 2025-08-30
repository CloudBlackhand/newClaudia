# Sistema de Cobrança Inteligente - Documentação Completa

## 🚀 Visão Geral

O Sistema de Cobrança Inteligente é uma solução completa e moderna para automatização de processos de cobrança via WhatsApp, utilizando inteligência artificial avançada para interações naturais com clientes. Desenvolvido com as melhores práticas de engenharia de software, oferece escalabilidade, segurança e facilidade de uso.

### ✨ Características Principais

- 🤖 **Bot Conversacional Avançado**: IA baseada em PyTorch com processamento de linguagem natural
- 📱 **Integração WhatsApp**: Comunicação direta via API Waha
- 📊 **Disparo Automatizado**: Processamento em lotes de milhares de clientes
- 🎨 **Interface Profissional**: Dashboard responsivo e intuitivo
- 🔒 **Segurança Robusta**: Autenticação JWT, rate limiting e validação rigorosa
- 📈 **Monitoramento Completo**: Logs estruturados e métricas em tempo real
- 🏗️ **Arquitetura Escalável**: Preparado para alto volume de operações

### 🎯 Casos de Uso

1. **Empresas de Cobrança**: Automatização de campanhas de recuperação de crédito
2. **Prestadores de Serviços**: Lembretes de pagamento para clientes
3. **E-commerce**: Follow-up de pagamentos pendentes
4. **Consultórios e Clínicas**: Cobrança de consultas e procedimentos
5. **Academias e Escolas**: Mensalidades e matrículas

## 🏗️ Arquitetura do Sistema

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA DE COBRANÇA                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Frontend   │    │   Backend   │    │  WhatsApp   │     │
│  │ (React/JS)  │◄──►│   (Flask)   │◄──►│   (Waha)    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                             │                               │
│                             ▼                               │
│                    ┌─────────────┐                         │
│                    │ AI/ML Bot   │                         │
│                    │ (PyTorch)   │                         │
│                    └─────────────┘                         │
│                             │                               │
│                             ▼                               │
│                    ┌─────────────┐                         │
│                    │ Data Layer  │                         │
│                    │ (JSON/Logs) │                         │
│                    └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

### Tecnologias Utilizadas

#### Backend
- **Python 3.11**: Linguagem principal
- **Flask**: Framework web leve e flexível
- **PyTorch**: Deep learning para IA conversacional
- **Transformers**: Modelos de linguagem pré-treinados
- **JWT**: Autenticação segura
- **Loguru**: Sistema de logs avançado

#### Frontend
- **HTML5/CSS3**: Estrutura e estilização moderna
- **JavaScript ES6+**: Lógica do cliente
- **Bootstrap 5**: Framework CSS responsivo
- **Font Awesome**: Ícones profissionais

#### Infraestrutura
- **Railway**: Plataforma de deploy
- **Docker**: Containerização
- **Gunicorn**: Servidor WSGI de produção
- **Waha**: API WhatsApp

#### Segurança
- **HTTPS/TLS**: Criptografia em trânsito
- **Rate Limiting**: Proteção contra abuso
- **Input Validation**: Sanitização de dados
- **CORS**: Controle de origem

## 📋 Funcionalidades Detalhadas

### 1. Módulo de Cobrança

#### Processamento de Clientes
- **Upload Inteligente**: Suporte a arquivos JSON com validação automática
- **Processamento em Lotes**: Milhares de clientes processados eficientemente
- **Validação Rigorosa**: Verificação de telefones, valores e dados obrigatórios
- **Filtros Avançados**: Segmentação por valor, data, status

#### Envio de Mensagens
- **Templates Personalizáveis**: Criação e edição de modelos de mensagem
- **Variáveis Dinâmicas**: Substituição automática de {nome}, {valor}, {data}
- **Controle de Velocidade**: Delay configurável entre envios
- **Retry Logic**: Reenvio automático em caso de falha

#### Monitoramento
- **Dashboard em Tempo Real**: Progresso e estatísticas ao vivo
- **Logs Detalhados**: Registro completo de todas as operações
- **Relatórios**: Taxa de entrega, respostas, conversões

### 2. Bot Conversacional IA

#### Processamento de Linguagem Natural
```python
# Exemplo de classificação de intenções
intents = {
    "saudacao": ["oi", "olá", "bom dia"],
    "confirmacao_pagamento": ["já paguei", "quitei", "transferi"],
    "negociacao": ["parcelar", "desconto", "acordo"],
    "informacoes": ["como pagar", "dados bancários", "pix"]
}
```

#### Capacidades do Bot
- **Classificação de Intenções**: 8+ intenções pré-configuradas
- **Extração de Entidades**: Valores, datas, confirmações
- **Respostas Contextuais**: Baseadas no histórico da conversa
- **Escalabilidade**: Múltiplas conversas simultâneas
- **Aprendizado**: Feedback loop para melhorias

#### Fluxo de Conversa
1. **Recebimento**: Webhook processa mensagem
2. **Análise**: IA classifica intenção e extrai dados
3. **Contexto**: Sistema recupera histórico do cliente
4. **Resposta**: Geração de resposta personalizada
5. **Ação**: Execução de ações automáticas quando necessário

### 3. Integração WhatsApp

#### Waha API
- **Sessões Persistentes**: Conexão estável com WhatsApp
- **QR Code**: Autenticação via escaneamento
- **Webhooks**: Recebimento de mensagens em tempo real
- **Status Monitoring**: Verificação contínua da conexão

#### Recursos de Mensagens
- **Texto Simples**: Mensagens tradicionais
- **Templates**: Mensagens com formatação
- **Emojis**: Suporte completo a caracteres especiais
- **Formatação**: Negrito, itálico, quebras de linha

### 4. Interface Web

#### Dashboard Principal
- **Métricas em Tempo Real**: Cards com estatísticas importantes
- **Gráficos**: Visualização de performance e tendências
- **Status do Sistema**: Monitoramento de componentes
- **Atividade Recente**: Feed de eventos importantes

#### Gestão de Cobrança
- **Upload de Arquivos**: Drag-and-drop com validação
- **Configuração de Lotes**: Seleção de templates e filtros
- **Progresso Visual**: Barra de progresso em tempo real
- **Histórico**: Registro de campanhas anteriores

#### Gestão de Conversas
- **Lista de Conversas**: Visão geral de interações ativas
- **Chat Interface**: Visualização do histórico completo
- **Filtros**: Busca por status, data, cliente
- **Analytics**: Métricas de engagement

#### Templates de Mensagem
- **Editor Visual**: Interface para criação/edição
- **Pré-visualização**: Teste antes do envio
- **Validação**: Verificação de variáveis obrigatórias
- **Biblioteca**: Gestão de templates salvos

## 🔧 Instalação e Configuração

### Pré-requisitos

```bash
# Verificar Python
python --version  # Deve ser 3.11+

# Verificar Git
git --version

# Verificar pip
pip --version
```

### Instalação Local

#### 1. Clone do Repositório
```bash
git clone https://github.com/seu-usuario/cobranca-inteligente.git
cd cobranca-inteligente
```

#### 2. Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Linux/Mac)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate
```

#### 3. Dependências
```bash
# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

#### 4. Configuração
```bash
# Copiar arquivo de configuração
cp env.example .env

# Editar configurações
nano .env
```

#### 5. Estrutura de Diretórios
```bash
# Criar diretórios necessários
mkdir -p data/uploads
mkdir -p logs
mkdir -p models
```

#### 6. Executar
```bash
# Modo desenvolvimento
python backend/app.py

# Modo produção
gunicorn --bind 0.0.0.0:8000 backend.app:app
```

### Configuração do Waha

#### Docker Compose (Recomendado)
```yaml
version: '3.8'
services:
  waha:
    image: devlikeapro/waha:latest
    ports:
      - "3000:3000"
    environment:
      - WHATSAPP_HOOK_URL=http://localhost:8000/webhook/waha
      - WHATSAPP_HOOK_EVENTS=message,message.any,state.change
    volumes:
      - ./waha-data:/app/session
    restart: unless-stopped
```

#### Configuração Manual
```bash
# Baixar e executar Waha
docker run -d \
  --name waha \
  -p 3000:3000 \
  -e WHATSAPP_HOOK_URL=http://localhost:8000/webhook/waha \
  -v $(pwd)/waha-data:/app/session \
  devlikeapro/waha:latest
```

## 🚀 Deploy em Produção

### Railway (Recomendado)

#### 1. Preparação
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar projeto
railway init
```

#### 2. Configuração
```bash
# Variáveis de ambiente
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=seu_secret_super_seguro
railway variables set WAHA_BASE_URL=https://seu-waha.com
railway variables set WAHA_API_KEY=sua_api_key

# Deploy
railway up
```

#### 3. Domínio
```bash
# Gerar domínio
railway domain

# URL: https://seu-projeto.railway.app
```

### Outras Plataformas

#### Heroku
```bash
heroku create seu-app-cobranca
heroku config:set FLASK_ENV=production
git push heroku main
```

#### DigitalOcean App Platform
```yaml
name: cobranca-inteligente
services:
- name: web
  source_dir: /
  run_command: gunicorn --bind 0.0.0.0:$PORT backend.app:app
  environment_slug: python
```

#### AWS Elastic Beanstalk
```bash
eb init
eb create cobranca-production
eb deploy
```

## 📊 Uso do Sistema

### Fluxo Básico de Cobrança

#### 1. Preparação dos Dados
```json
[
  {
    "id": "001",
    "name": "João Silva",
    "phone": "5511987654321",
    "amount": 150.50,
    "due_date": "2024-01-15",
    "description": "Mensalidade janeiro"
  }
]
```

#### 2. Upload e Validação
1. Acesse o sistema via navegador
2. Faça login (admin/admin123 por padrão)
3. Vá para seção "Cobrança"
4. Faça upload do arquivo JSON
5. Sistema valida automaticamente

#### 3. Configuração do Envio
1. Selecione o arquivo carregado
2. Escolha template de mensagem
3. Configure delay entre envios
4. Execute validação prévia

#### 4. Execução
1. Inicie o envio em lote
2. Monitore progresso em tempo real
3. Acompanhe estatísticas de entrega

#### 5. Gestão de Respostas
1. Clientes respondem via WhatsApp
2. Bot IA processa automaticamente
3. Escalação para humano quando necessário

### Criação de Templates

#### Template Básico
```
Olá {name}! 👋

Este é um lembrete sobre seu pagamento:
💰 Valor: {amount}
📅 Vencimento: {due_date}

Para facilitar, responda esta mensagem.

Obrigado! 🙏
```

#### Variáveis Disponíveis
- `{name}`: Nome do cliente
- `{amount}`: Valor formatado (R$ 150,50)
- `{phone}`: Telefone do cliente
- `{due_date}`: Data de vencimento
- `{description}`: Descrição da cobrança
- `{current_date}`: Data atual
- `{current_time}`: Hora atual

### Exemplos de Uso via API

#### Autenticação
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

#### Envio de Lote
```bash
curl -X POST http://localhost:8000/api/billing/send-batch \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clients_file": "data/clients.json",
    "template_name": "cobranca_simples",
    "delay_seconds": 2
  }'
```

#### Status do Lote
```bash
curl -X GET http://localhost:8000/api/billing/batch-status \
  -H "Authorization: Bearer SEU_TOKEN"
```

## 🛡️ Segurança

### Autenticação e Autorização
- **JWT Tokens**: Tokens seguros com expiração
- **Rate Limiting**: 100 requisições por hora por IP
- **Session Management**: Controle de sessões ativas

### Proteção de Dados
- **Input Validation**: Sanitização rigorosa de entradas
- **SQL Injection**: Proteção contra ataques
- **XSS Protection**: Headers de segurança automáticos
- **Data Masking**: Logs não expõem dados sensíveis

### Headers de Segurança
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

### Webhook Security
```python
def verify_webhook_signature(payload, signature, secret):
    expected = hmac.new(
        secret.encode(), 
        payload.encode(), 
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

## 📈 Monitoramento e Logs

### Sistema de Logs Estruturados

#### Tipos de Log
```python
# Logs de cobrança
billing_logger.message_sent(phone, template, success, message_id)
billing_logger.batch_completed(total, successful, failed, duration)

# Logs de conversa
conversation_logger.message_received(phone, message)
conversation_logger.bot_response(phone, response, intent, confidence)

# Logs de segurança
app_logger.security("RATE_LIMIT_EXCEEDED", {"ip": "192.168.1.1"})
```

#### Configuração de Logs
```python
# Rotação automática
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip"
)
```

### Métricas e KPIs

#### Métricas de Cobrança
- Taxa de entrega de mensagens
- Taxa de resposta dos clientes
- Tempo médio de processamento
- Volume de mensagens por hora

#### Métricas de Conversa
- Precisão da classificação de intenções
- Tempo médio de resposta do bot
- Taxa de escalação para humano
- Satisfação do cliente (NPS)

#### Métricas de Sistema
- Uptime da aplicação
- Latência da API
- Uso de memória e CPU
- Taxa de erros

### Alertas e Notificações

#### Configuração de Alertas
```python
# Alerta de falha crítica
if error_rate > 5:
    send_alert("Sistema com alta taxa de erro")

# Alerta de performance
if response_time > 2000:
    send_alert("API com latência alta")
```

## 🧪 Testes

### Estrutura de Testes
```
tests/
├── unit/
│   ├── test_validators.py      # Testes de validação
│   ├── test_billing_service.py # Testes de cobrança
│   └── test_chatbot.py         # Testes do bot
├── integration/
│   ├── test_api_endpoints.py   # Testes de API
│   └── test_waha_integration.py # Testes Waha
└── e2e/
    └── test_complete_flow.py   # Testes end-to-end
```

### Executar Testes
```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/test_billing_service.py

# Com cobertura
pytest --cov=backend

# Relatório HTML
pytest --cov=backend --cov-report=html
```

### Exemplos de Testes

#### Teste de Validação
```python
def test_validate_phone_number():
    validator = ClientValidator()
    
    # Teste válido
    result = validator.validate_phone("5511987654321")
    assert result["valid"] is True
    
    # Teste inválido
    result = validator.validate_phone("invalid")
    assert result["valid"] is False
```

#### Teste de API
```python
@pytest.mark.asyncio
async def test_send_billing_batch():
    response = await api_client.post("/api/billing/send-batch", {
        "clients_file": "test.json",
        "template_name": "test_template"
    })
    
    assert response.status_code == 200
    assert response.json()["success"] is True
```

## 🔧 Desenvolvimento

### Ambiente de Desenvolvimento

#### Setup do Ambiente
```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Linting
black backend/
flake8 backend/
isort backend/
```

#### Estrutura do Código
```
backend/
├── app.py                  # Aplicação principal
├── config/
│   └── settings.py         # Configurações
├── models/
│   ├── chatbot.py         # Modelo IA
│   └── conversation.py    # Gestão de conversas
├── services/
│   ├── billing.py         # Serviço de cobrança
│   └── waha_client.py     # Cliente Waha
├── utils/
│   ├── validators.py      # Validações
│   ├── logger.py          # Sistema de logs
│   └── security.py        # Segurança
└── __init__.py
```

### Contribuindo

#### Guidelines de Código
1. **PEP 8**: Seguir padrões Python
2. **Type Hints**: Usar anotações de tipo
3. **Docstrings**: Documentar funções e classes
4. **Tests**: Cobertura mínima de 80%

#### Process de Contribuição
1. Fork do repositório
2. Criar branch feature
3. Implementar mudanças
4. Adicionar testes
5. Submeter Pull Request

#### Exemplo de Contribuição
```python
def validate_client_data(data: Dict[str, Any]) -> ValidationResult:
    """
    Valida dados de cliente para cobrança.
    
    Args:
        data: Dicionário com dados do cliente
        
    Returns:
        ValidationResult com status e erros
        
    Raises:
        ValueError: Se dados estão malformados
    """
    # Implementação aqui
    pass
```

## 📚 Documentação Técnica

### APIs Disponíveis

#### Autenticação
- `POST /auth/login` - Login do usuário
- `POST /auth/refresh` - Renovar token

#### Cobrança
- `POST /api/billing/send-batch` - Enviar lote
- `POST /api/billing/send-single` - Enviar individual
- `GET /api/billing/batch-status` - Status do lote
- `GET /api/billing/templates` - Listar templates

#### Chat
- `POST /api/chat/process` - Processar mensagem
- `GET /api/chat/conversation/{phone}` - Histórico
- `GET /api/chat/conversations/stats` - Estatísticas

#### WhatsApp
- `GET /api/waha/status` - Status da sessão
- `POST /api/waha/start` - Iniciar sessão
- `POST /api/waha/stop` - Parar sessão

### Modelos de Dados

#### Cliente
```typescript
interface Client {
  id: string;              // Identificador único
  name: string;            // Nome completo
  phone: string;           // Telefone (+55...)
  amount: number;          // Valor da cobrança
  due_date?: string;       // Data vencimento (YYYY-MM-DD)
  description?: string;    // Descrição
}
```

#### Conversa
```typescript
interface Conversation {
  phone: string;
  messages: Message[];
  context: ConversationContext;
  created_at: string;
  updated_at: string;
}
```

### Configurações Avançadas

#### Environment Variables
```env
# Aplicação
FLASK_ENV=production|development|testing
SECRET_KEY=chave_super_secreta
DEBUG=True|False
PORT=8000

# Waha
WAHA_BASE_URL=https://waha.exemplo.com
WAHA_API_KEY=sua_api_key
WAHA_SESSION_NAME=sessao_cobranca
WAHA_WEBHOOK_URL=https://app.railway.app/webhook

# Segurança
JWT_SECRET_KEY=jwt_secret
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Modelo IA
MODEL_DEVICE=cpu|cuda
MODEL_MAX_LENGTH=512
MODEL_TEMPERATURE=0.7
```

#### Configuração de Cache
```python
# Redis para cache (opcional)
REDIS_URL=redis://localhost:6379
CACHE_TIMEOUT=3600
MODEL_CACHE_SIZE=100
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Falha na Conexão Waha
```bash
# Verificar status
curl http://localhost:3000/api/sessions

# Reiniciar sessão
curl -X POST http://localhost:3000/api/sessions/restart
```

#### 2. Erro de Memória
```python
# Configurar workers
WEB_CONCURRENCY=2
MAX_WORKERS=2

# Otimizar modelo
MODEL_CACHE_SIZE=50
```

#### 3. Rate Limit Atingido
```python
# Aumentar limites
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_PERIOD=3600

# Implementar retry
@retry(stop_max_attempt_number=3)
def send_message():
    pass
```

#### 4. Logs Não Aparecendo
```bash
# Verificar permissões
chmod 755 logs/
chown user:user logs/

# Configurar logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/debug.log
```

### Debugging

#### Modo Debug
```python
# Ativar debug
app.run(debug=True)

# Logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Profiling
```python
# Performance profiling
from werkzeug.middleware.profiler import ProfilerMiddleware
app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

# Memory profiling
import memory_profiler
@memory_profiler.profile
def processo_intensivo():
    pass
```

## 📞 Suporte

### Canais de Suporte
- **Issues GitHub**: Para bugs e melhorias
- **Documentação**: Consulte os arquivos em `/docs`
- **Email**: suporte@exemplo.com
- **Discord**: Comunidade de desenvolvedores

### FAQ

#### Como personalizar o bot?
Edite os intents e responses em `backend/models/chatbot.py`

#### Como adicionar novos templates?
Use a API ou interface web em "Templates"

#### Como escalar o sistema?
Configure mais workers no Gunicorn e use load balancer

#### Como fazer backup?
Export das configurações via API e backup do repositório

### Roadmap

#### Próximas Versões
- [ ] Múltiplos canais (Telegram, SMS)
- [ ] Dashboard analytics avançado  
- [ ] Integração com CRMs
- [ ] Machine learning automatizado
- [ ] API pública para integrações
- [ ] Mobile app para gestão

---

## 📄 Licença

MIT License - Veja arquivo LICENSE para detalhes.

## 🙏 Agradecimentos

- Comunidade Python e Flask
- Desenvolvedores do PyTorch
- Projeto Waha para WhatsApp
- Contribuidores e testadores

---

**Desenvolvido com ❤️ para automatizar e humanizar a cobrança**

