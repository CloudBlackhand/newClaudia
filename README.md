# Sistema de Cobrança Avançado 🚀

Sistema modular e escalável para disparo de mensagens de cobrança e conversação inteligente via WhatsApp, desenvolvido especialmente para deploy na Railway.

## 🌟 Características Principais

### 📨 Módulo de Disparo de Mensagens
- **Leitor JSON Otimizado**: Processamento eficiente de dados de clientes
- **Sistema de Envio Automatizado**: Envio em lotes com controle de rate limiting
- **Logging Detalhado**: Registro completo de todas as operações
- **Validação Rigorosa**: Verificação completa de dados antes do processamento

### 🤖 Bot de Conversação Avançado (IA Própria)
- **Processamento de Linguagem Natural**: Sistema próprio comparável ao ChatGPT
- **Análise de Sentimentos**: Detecção automática do humor do cliente
- **Contexto Conversacional**: Memória de conversas e histórico
- **Respostas Inteligentes**: Templates adaptativos baseados na situação
- **Escalação Inteligente**: Identificação automática quando requer humano

### 🎨 Frontend Responsivo
- **Interface Moderna**: Design clean e intuitivo
- **Responsivo**: Compatível com todos os dispositivos
- **Dashboard em Tempo Real**: Monitoramento de estatísticas e logs
- **Upload Drag & Drop**: Interface amigável para arquivos

### 🔗 Integração WhatsApp via Waha
- **Webhooks**: Recebimento automático de mensagens
- **Envio de Mensagens**: API completa para comunicação
- **Status em Tempo Real**: Monitoramento da conexão

## 🏗️ Arquitetura

```
Sistema de Cobrança Avançado/
├── backend/                     # Aplicação Python FastAPI
│   ├── app.py                  # Aplicação principal
│   ├── config/                 # Configurações
│   ├── modules/                # Módulos principais
│   │   ├── billing_dispatcher.py
│   │   ├── conversation_bot.py
│   │   ├── waha_integration.py
│   │   ├── logger_system.py
│   │   └── validation_engine.py
│   └── api/                    # Rotas da API
├── frontend/                   # Interface JavaScript
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── Dockerfile                  # Container para Railway
├── requirements.txt            # Dependências Python
└── railway.json               # Configuração Railway
```

## 🚀 Deploy na Railway

### 1. Preparação

1. **Clone o repositório**:
   ```bash
   git clone <seu-repositorio>
   cd sistema-cobranca-avancado
   ```

2. **Configure as variáveis de ambiente**:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

### 2. Deploy Automático

1. **Conecte com Railway**:
   - Acesse [railway.app](https://railway.app)
   - Conecte seu repositório GitHub
   - O deploy será automático usando o Dockerfile

2. **Configurar Variáveis de Ambiente**:
   No painel da Railway, configure:
   ```
   WAHA_BASE_URL=https://sua-instancia-waha.com
   WAHA_API_KEY=sua-api-key
   SECRET_KEY=chave-super-secreta
   WEBHOOK_SECRET=secret-para-webhooks
   ```

### 3. Deploy Manual (CLI)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

## 🔧 Configuração

### Variáveis de Ambiente Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `WAHA_BASE_URL` | URL da instância Waha | `https://waha.example.com` |
| `SECRET_KEY` | Chave secreta da aplicação | `sua-chave-super-segura` |

### Variáveis Opcionais

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `PORT` | `8000` | Porta do servidor |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `BATCH_SIZE` | `50` | Tamanho do lote de mensagens |
| `MAX_CONCURRENT_REQUESTS` | `100` | Máximo de requisições simultâneas |

## 📖 Como Usar

### 1. Upload de Dados

1. Acesse a interface web
2. Vá para a aba "Cobrança"
3. Faça upload de um arquivo JSON com os dados dos clientes

**Formato do JSON**:
```json
[
  {
    "nome": "João Silva",
    "telefone": "+5511999999999",
    "valor": "150,00",
    "vencimento": "15/12/2024",
    "descricao": "Mensalidade dezembro"
  }
]
```

### 2. Configurar Template

Personalize a mensagem usando placeholders:
- `{nome}` - Nome do cliente
- `{valor}` - Valor a pagar
- `{vencimento}` - Data de vencimento
- `{descricao}` - Descrição da cobrança

### 3. Processar e Enviar

1. Clique em "Validar Dados"
2. Verifique os resultados da validação
3. Clique em "Iniciar Envio"
4. Acompanhe o progresso em tempo real

### 4. Monitorar Conversas

- Acesse a aba "Conversas" para ver interações
- O bot responderá automaticamente aos clientes
- Conversas complexas são escaladas para humanos

## 🔍 Monitoramento

### Logs Disponíveis

- **Operações**: Todas as operações do sistema
- **Mensagens**: Envios e recebimentos
- **Conversas**: Interações do bot
- **Erros**: Problemas e falhas

### Estatísticas

- Taxa de sucesso de envios
- Número de conversas ativas
- Performance dos módulos
- Relatórios detalhados

## 🤖 Bot de Conversação

### Funcionalidades da IA Própria

**Análise de Intenções**:
- Pagamento realizado
- Solicitação de dados
- Questionamento de dívida
- Negociação
- Dificuldade financeira

**Análise de Sentimentos**:
- Positivo, negativo, neutro
- Adaptação do tom de resposta
- Escalação baseada em frustração

**Contexto Conversacional**:
- Histórico de mensagens
- Perfil do usuário
- Estágio da conversa
- Memória de interações

## 🔒 Segurança

- **Autenticação**: Tokens seguros para APIs
- **Validação**: Verificação rigorosa de dados
- **Sanitização**: Limpeza de inputs
- **Rate Limiting**: Proteção contra abuso
- **Logs Auditáveis**: Rastro completo de operações

## 📊 Performance

### Otimizações para Railway

- **Startup rápido**: Inicialização otimizada
- **Baixo uso de memória**: Gestão eficiente de recursos
- **Processamento assíncrono**: Operações não bloqueantes
- **Cache inteligente**: Redução de latência

### Limites Recomendados

- **Arquivo JSON**: Máximo 10MB
- **Lote de mensagens**: 50 mensagens simultâneas
- **Sessões ativas**: 1000 conversas
- **Logs**: 30 dias de retenção

## 🛠️ Desenvolvimento Local

### Requisitos

- Python 3.11+
- Node.js (para desenvolvimento frontend)

### Instalação

```bash
# Backend
pip install -r requirements.txt

# Executar
cd backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Estrutura de Desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install pytest pytest-asyncio httpx

# Executar testes
pytest

# Executar com reload automático
uvicorn backend.app:app --reload
```

## 🐛 Troubleshooting

### Problemas Comuns

**1. Erro de conexão com Waha**
- Verifique a variável `WAHA_BASE_URL`
- Confirme se a instância Waha está funcionando
- Verifique logs de conectividade

**2. Falha no envio de mensagens**
- Verifique permissões da API
- Confirme formato dos números de telefone
- Verifique rate limits

**3. Bot não responde**
- Verifique configuração de webhooks
- Confirme se o bot está inicializado
- Analise logs de conversação

### Logs Úteis

```bash
# Visualizar logs no Railway
railway logs

# Logs específicos
railway logs --tail
```

## 📄 Licença

Este projeto foi desenvolvido especificamente para sua empresa. Todos os direitos reservados.

## 🤝 Suporte

Para suporte técnico, consulte:
- Logs do sistema na interface web
- Documentação da API em `/docs`
- Status dos módulos na aba "Estatísticas"

---

**Sistema desenvolvido com ❤️ para transformar a Claudia da Desk em uma IA SUPREMA! 🚀**
