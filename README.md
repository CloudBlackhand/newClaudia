# Sistema de Cobrança Inteligente 🤖💰

Um sistema completo e inteligente para automação de cobrança via WhatsApp, desenvolvido especificamente para hospedagem na Railway.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple.svg)

## 🎯 Características Principais

### 🚀 Sistema de Disparo de Mensagens
- **Leitor JSON otimizado** para processamento eficiente de dados de clientes
- **Envio automatizado** com registro detalhado de logs
- **Validação rigorosa** de dados antes do processamento
- **Rate limiting** para respeitar limites de API
- **Sistema de retry** para mensagens falhadas

### 🧠 Bot de Conversação Avançado
- **IA própria** com capacidades comparáveis ao ChatGPT
- **Processamento de linguagem natural** para compreensão contextual
- **Arquitetura escalável** para alto volume de requisições
- **Design modular** para fácil expansão
- **Sistema de aprendizado** baseado em interações

### 🎨 Frontend Profissional
- **JavaScript puro** sem dependências externas
- **Design responsivo** para todos os dispositivos
- **Interface intuitiva** e moderna
- **Experiência otimizada** do usuário

### 🔧 Recursos Técnicos
- **Padrões de engenharia** de software rigorosos
- **Segurança robusta** para proteção de dados
- **APIs bem documentadas** para integração
- **Testes automatizados** abrangentes
- **Logs estruturados** para monitoramento

## 📋 Pré-requisitos

- Python 3.11+
- Node.js (para Waha - deploy separado)
- Conta Railway
- Instância Waha configurada

## 🚀 Instalação e Configuração

### 1. Clone o Repositório
```bash
git clone <repository-url>
cd sistema-cobranca-inteligente
```

### 2. Configuração do Ambiente
```bash
# Copiar arquivo de configuração
cp environment.example .env

# Editar variáveis de ambiente
nano .env
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```env
# Configurações da aplicação
APP_NAME=Sistema de Cobrança Inteligente
DEBUG=False
SECRET_KEY=sua_chave_secreta_super_forte_aqui

# Configurações do WhatsApp (Waha)
WAHA_BASE_URL=https://sua-instancia-waha.com
WAHA_SESSION_NAME=default
WAHA_WEBHOOK_URL=https://seu-dominio.railway.app/api/webhook/whatsapp

# Configurações de segurança
API_KEY=sua_api_key_aqui
WEBHOOK_SECRET=seu_webhook_secret_aqui
```

## 🏃‍♂️ Execução Local

### Desenvolvimento
```bash
python start.py
```

### Executar Testes
```bash
# Todos os testes
python run_tests.py

# Testes específicos
python run_tests.py --unit
python run_tests.py --api
python run_tests.py --coverage
```

## 📚 Estrutura do Projeto

```
sistema-cobranca-inteligente/
├── backend/
│   ├── app.py                 # Aplicação Flask principal
│   ├── config/
│   │   └── settings.py        # Configurações centralizadas
│   ├── modules/
│   │   ├── billing_dispatcher.py    # Sistema de cobrança
│   │   ├── conversation_bot.py      # Bot de conversação
│   │   ├── validation_engine.py     # Validação de dados
│   │   ├── logger_system.py         # Sistema de logs
│   │   └── waha_integration.py      # Integração WhatsApp
│   └── api/
│       └── routes/
│           ├── billing_routes.py    # Rotas de cobrança
│           ├── conversation_routes.py # Rotas de conversação
│           └── webhook_routes.py     # Rotas de webhooks
├── frontend/
│   ├── index.html            # Interface principal
│   ├── styles.css           # Estilos responsivos
│   └── app.js              # Lógica da aplicação
├── tests/                  # Testes automatizados
├── docs/                   # Documentação
├── start.py               # Script de inicialização
├── requirements.txt       # Dependências Python
├── railway.json          # Configuração Railway
└── README.md             # Esta documentação
```

## 📖 Documentação da API

### Endpoints de Cobrança

#### `POST /api/billing/send-batch`
Envia lote de mensagens de cobrança.

**Request:**
```json
{
  "clients": [
    {
      "name": "João Silva",
      "phone": "11999999999",
      "amount": 150.50,
      "due_date": "2024-12-31",
      "email": "joao@email.com"
    }
  ],
  "template_id": "initial_br",
  "schedule_time": "2024-12-25T10:00:00"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "total_messages": 1,
    "successful": 1,
    "failed": 0,
    "execution_time": 1.2
  }
}
```

#### `POST /api/billing/validate-clients`
Valida dados de clientes sem enviar mensagens.

### Endpoints de Conversação

#### `POST /api/conversation/process-message`
Processa mensagem do usuário com IA.

**Request:**
```json
{
  "phone": "+5511999999999",
  "message": "Oi, recebi uma cobrança",
  "user_name": "João Silva",
  "auto_reply": true
}
```

**Response:**
```json
{
  "success": true,
  "response": {
    "text": "Olá João! Como posso ajudá-lo?",
    "type": "informative",
    "confidence": 0.95,
    "should_escalate": false
  }
}
```

### Webhooks

#### `POST /api/webhook/whatsapp`
Recebe webhooks do Waha para processar mensagens.

## 🤖 Bot de Conversação

### Intenções Suportadas
- **Cumprimento**: Detecta saudações e inicia conversa
- **Confirmação de Pagamento**: Identifica quando cliente confirma pagamento
- **Perguntas sobre Pagamento**: Responde dúvidas sobre como pagar
- **Negociação**: Oferece alternativas de pagamento
- **Reclamações**: Escalona para atendimento humano
- **Despedida**: Finaliza conversas educadamente

### Análise de Sentimento
- **Positivo**: Respostas calorosas e agradecimentos
- **Neutro**: Informações diretas e objetivas
- **Negativo**: Abordagem empática
- **Raiva**: Escalação imediata para humano

## 📊 Sistema de Logs

### Categorias de Log
- **SYSTEM**: Eventos do sistema
- **BILLING**: Eventos de cobrança
- **CONVERSATION**: Interações com clientes
- **WHATSAPP**: Integração WhatsApp
- **VALIDATION**: Validação de dados
- **SECURITY**: Eventos de segurança

### Formatos de Saída
- **JSON estruturado**: Para análise automatizada
- **Texto legível**: Para desenvolvimento
- **Console colorido**: Para debugging

## 🔒 Segurança

### Medidas Implementadas
- **Validação rigorosa** de entrada
- **Sanitização** de dados
- **Rate limiting** de APIs
- **Verificação de assinatura** em webhooks
- **Logs de segurança** detalhados
- **Escape** de caracteres especiais

### Configurações Recomendadas
```env
# Use senhas fortes
SECRET_KEY=chave_com_pelo_menos_32_caracteres_aleatorios
API_KEY=api_key_complexa_e_unica
WEBHOOK_SECRET=secret_para_validacao_webhooks

# Limite logs em produção
LOG_LEVEL=INFO
DEBUG=False
```

## 🌐 Deploy na Railway

### 1. Preparação
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login
```

### 2. Deploy
```bash
# Criar projeto
railway init

# Configurar variáveis
railway variables:set SECRET_KEY=sua_chave_aqui
railway variables:set WAHA_BASE_URL=https://sua-waha.com

# Deploy
railway up
```

### 3. Configuração de Domínio
1. Acesse o dashboard Railway
2. Configure domínio personalizado
3. Atualize `WAHA_WEBHOOK_URL` com o novo domínio

## 📋 Uso do Sistema

### 1. Upload de Dados
- Prepare arquivo JSON com dados dos clientes
- Use o formato especificado na documentação
- Faça upload pela interface web

### 2. Validação
- Clique em "Validar Dados" para verificar
- Corrija erros se necessário
- Sistema mostra preview dos dados

### 3. Envio de Mensagens
- Selecione template apropriado
- Configure agendamento se necessário
- Clique em "Enviar Cobranças"

### 4. Monitoramento
- Acompanhe conversas em tempo real
- Verifique logs e estatísticas
- Gerencie escalações quando necessário

## 🧪 Testes

### Estrutura de Testes
- **Unitários**: Testam componentes isolados
- **Integração**: Testam fluxos completos
- **API**: Testam endpoints REST
- **Cobertura**: Análise de cobertura de código

### Executar Testes
```bash
# Todos os testes
python run_tests.py --all

# Testes específicos
python run_tests.py --unit
python run_tests.py --api --coverage

# Módulo específico
python run_tests.py --module validation_engine
```

## 📈 Monitoramento

### Métricas Disponíveis
- **Mensagens enviadas**: Total e taxa de sucesso
- **Conversas ativas**: Número e duração
- **Performance**: Tempo de resposta e throughput
- **Erros**: Taxa e categorização

### Logs Estruturados
```json
{
  "timestamp": "2024-01-01T10:00:00Z",
  "level": "INFO",
  "category": "billing",
  "message": "Mensagem enviada com sucesso",
  "details": {
    "phone": "+5511999999999",
    "template": "initial_br"
  }
}
```

## 🔧 Personalização

### Templates de Mensagem
Edite em `backend/modules/billing_dispatcher.py`:

```python
self.templates['custom_br'] = MessageTemplate(
    type=MessageType.CUSTOM,
    subject="Seu Assunto",
    content="Sua mensagem personalizada com {client_name}",
    variables=['client_name', 'amount'],
    priority=1
)
```

### Intenções da IA
Adicione em `backend/modules/conversation_bot.py`:

```python
IntentType.CUSTOM_INTENT = "custom_intent"

# No método _load_intent_patterns:
IntentType.CUSTOM_INTENT: [
    r'\b(palavra-chave|padrão)\b',
    r'outro padrão de reconhecimento'
]
```

## 🤝 Contribuição

### Processo de Desenvolvimento
1. Fork o repositório
2. Crie branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Add: nova funcionalidade'`)
4. Push para branch (`git push origin feature/nova-funcionalidade`)
5. Abra Pull Request

### Padrões de Código
- **PEP 8** para Python
- **ESLint** para JavaScript
- **Type hints** obrigatórios
- **Docstrings** em todas as funções
- **Testes** para novas funcionalidades

## 📞 Suporte

### Problemas Comuns

**1. Erro de conexão com Waha**
```bash
# Verificar URL e credenciais
curl -X GET $WAHA_BASE_URL/api/health
```

**2. Mensagens não enviando**
```bash
# Verificar logs
tail -f logs/billing.log
```

**3. IA não respondendo corretamente**
```bash
# Testar análise NLP
python run_tests.py --module conversation_bot
```

### Logs de Debug
```bash
# Habilitar debug
export DEBUG=True
export LOG_LEVEL=DEBUG

# Restart da aplicação
python start.py
```

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏆 Créditos

Desenvolvido com ❤️ para automação inteligente de cobrança.

---

**Sistema de Cobrança Inteligente** - Transformando a gestão de cobranças com IA e automação! 🚀
# Force deploy
# Force new deploy - ter 02 set 2025 10:25:59 -03
# Force restart - ter 02 set 2025 10:41:31 -03
# CRÍTICO: Blueprint webhook não carregando - ter 02 set 2025 10:45:44 -03
#   D e p l o y   0 9 / 0 3 / 2 0 2 5   2 1 : 5 5 : 4 0  
 