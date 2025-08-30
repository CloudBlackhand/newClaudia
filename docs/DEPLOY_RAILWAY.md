# Guia de Deploy na Railway 🚂

Este guia detalha o processo completo de deploy do Sistema de Cobrança Inteligente na Railway.

## 📋 Pré-requisitos

### 1. Contas Necessárias
- ✅ Conta na [Railway](https://railway.app)
- ✅ Conta no GitHub (para versionamento)
- ✅ Instância Waha configurada (deploy separado)

### 2. Ferramentas Locais
```bash
# Railway CLI
npm install -g @railway/cli

# Git (se não tiver)
git --version

# Python 3.11+
python --version
```

## 🚀 Preparação do Projeto

### 1. Clone e Configuração
```bash
# Clone do repositório
git clone <seu-repositorio>
cd sistema-cobranca-inteligente

# Verificar estrutura
ls -la
# Deve conter: requirements.txt, railway.json, start.py
```

### 2. Teste Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente local
cp environment.example .env
nano .env

# Testar aplicação
python start.py
```

### 3. Validar Configurações Railway
Verifique se `railway.json` está correto:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python start.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## 🌐 Deploy na Railway

### Método 1: Deploy via CLI (Recomendado)

#### 1. Login na Railway
```bash
railway login
```
- Será aberto o browser para autenticação
- Confirme o login no terminal

#### 2. Inicializar Projeto
```bash
# Na pasta do projeto
railway init

# Escolher opções:
# - Create new project: Yes
# - Project name: sistema-cobranca-inteligente
# - Environment: production
```

#### 3. Configurar Variáveis de Ambiente
```bash
# Variáveis obrigatórias
railway variables:set SECRET_KEY="sua_chave_secreta_super_forte_de_32_chars"
railway variables:set DEBUG="False"
railway variables:set APP_NAME="Sistema de Cobrança Inteligente"

# Configurações do WhatsApp
railway variables:set WAHA_BASE_URL="https://sua-instancia-waha.com"
railway variables:set WAHA_SESSION_NAME="default"

# Será configurado após deploy
railway variables:set WAHA_WEBHOOK_URL="https://seu-dominio.railway.app/api/webhook/whatsapp"

# Configurações de segurança
railway variables:set API_KEY="sua_api_key_complexa_aqui"
railway variables:set WEBHOOK_SECRET="seu_webhook_secret_aqui"

# Configurações de logs
railway variables:set LOG_LEVEL="INFO"
railway variables:set LOG_FILE="logs/app.log"

# Configurações da IA
railway variables:set AI_CONFIDENCE_THRESHOLD="0.8"
railway variables:set AI_MODEL_VERSION="1.0"
railway variables:set AI_LEARNING_ENABLED="True"

# Configurações de cobrança
railway variables:set MAX_RETRY_ATTEMPTS="3"
railway variables:set RETRY_DELAY_SECONDS="5"
railway variables:set MESSAGE_RATE_LIMIT="10"
```

#### 4. Deploy da Aplicação
```bash
# Deploy inicial
railway up

# Acompanhar deploy
railway logs --follow
```

### Método 2: Deploy via GitHub

#### 1. Conectar Repositório
```bash
# Push para GitHub
git add .
git commit -m "feat: Sistema de Cobrança Inteligente completo"
git push origin main
```

#### 2. Configurar na Railway
1. Acesse [Railway Dashboard](https://railway.app/dashboard)
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Escolha seu repositório
5. Configure as variáveis de ambiente no dashboard

## 🔧 Configuração Pós-Deploy

### 1. Verificar Deploy
```bash
# Verificar status
railway status

# Verificar logs
railway logs

# Testar health check
curl https://seu-dominio.railway.app/health
```

### 2. Configurar Domínio Personalizado

#### Via Dashboard:
1. Acesse seu projeto na Railway
2. Clique em "Settings" → "Domains"
3. Clique em "Custom Domain"
4. Adicione seu domínio
5. Configure DNS conforme instruções

#### Via CLI:
```bash
# Adicionar domínio personalizado
railway domain add seu-dominio.com
```

### 3. Atualizar Webhook URL
```bash
# Após configurar domínio
railway variables:set WAHA_WEBHOOK_URL="https://seu-dominio.com/api/webhook/whatsapp"

# Forçar redeploy
railway redeploy
```

### 4. Configurar SSL/TLS
A Railway configura SSL automaticamente. Verifique:
```bash
curl -I https://seu-dominio.railway.app
# Deve retornar: HTTP/2 200
```

## 🔗 Integração com Waha

### 1. Configurar Webhook no Waha
```bash
# Configurar sessão com webhook
curl -X POST https://sua-waha.com/api/sessions/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default",
    "config": {
      "webhooks": [
        {
          "url": "https://seu-dominio.railway.app/api/webhook/whatsapp",
          "events": ["message", "session.status", "message.ack"]
        }
      ]
    }
  }'
```

### 2. Testar Integração
```bash
# Verificar status da sessão Waha
curl https://sua-waha.com/api/sessions/default

# Testar webhook
curl -X POST https://seu-dominio.railway.app/api/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": "railway deploy"}'
```

## 📊 Monitoramento

### 1. Logs da Railway
```bash
# Logs em tempo real
railway logs --follow

# Logs específicos
railway logs --lines 100

# Filtrar logs por nível
railway logs | grep ERROR
```

### 2. Métricas de Performance
Acesse o dashboard Railway para ver:
- CPU Usage
- Memory Usage
- Network Traffic
- Response Times

### 3. Alertas Personalizados
Configure alertas no dashboard:
1. Settings → Notifications
2. Adicione webhook para alertas
3. Configure limites de CPU/Memory

## 🔧 Comandos Úteis

### Gerenciamento do Deploy
```bash
# Status do projeto
railway status

# Informações do projeto
railway show

# Redeploy forçado
railway redeploy

# Reverter para deploy anterior
railway rollback

# Abrir aplicação
railway open

# Conectar ao banco (se usar)
railway connect
```

### Debug e Troubleshooting
```bash
# Logs detalhados
railway logs --level debug

# Variáveis de ambiente
railway variables

# Shell no container
railway shell

# Executar comando no container
railway run python --version
```

## 🛠️ Troubleshooting

### Problema: Deploy Falha

#### Verificar logs:
```bash
railway logs --lines 50
```

#### Causas comuns:
1. **Dependências ausentes**
   ```bash
   # Verificar requirements.txt
   cat requirements.txt
   
   # Adicionar dependência faltante
   echo "nova-dependencia==1.0.0" >> requirements.txt
   git add . && git commit -m "fix: adicionar dependência" && git push
   ```

2. **Variáveis de ambiente**
   ```bash
   # Verificar variáveis
   railway variables
   
   # Adicionar variável faltante
   railway variables:set NOVA_VAR="valor"
   ```

3. **Porta incorreta**
   ```python
   # Em start.py, usar PORT do ambiente
   port = int(os.getenv('PORT', 8000))
   ```

### Problema: Aplicação Não Responde

#### 1. Verificar Health Check
```bash
curl -f https://seu-dominio.railway.app/health || echo "Health check falhou"
```

#### 2. Verificar Logs de Erro
```bash
railway logs | grep -i error
```

#### 3. Verificar Configurações
```bash
# Verificar se variáveis estão corretas
railway variables | grep SECRET_KEY
```

### Problema: Webhook Não Funciona

#### 1. Testar Endpoint
```bash
curl -X POST https://seu-dominio.railway.app/api/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'
```

#### 2. Verificar Configuração Waha
```bash
# Verificar se webhook está configurado
curl https://sua-waha.com/api/sessions/default
```

#### 3. Verificar Logs de Webhook
```bash
railway logs | grep webhook
```

## 🔄 CI/CD Automatizado

### 1. Configurar GitHub Actions
Crie `.github/workflows/railway-deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run tests
      run: python run_tests.py --unit
    
    - name: Deploy to Railway
      uses: railway-app/railway-action@v1
      with:
        api_token: ${{ secrets.RAILWAY_TOKEN }}
        project_id: ${{ secrets.RAILWAY_PROJECT_ID }}
```

### 2. Configurar Secrets
No GitHub:
1. Settings → Secrets and variables → Actions
2. Adicionar:
   - `RAILWAY_TOKEN`: Token da Railway CLI
   - `RAILWAY_PROJECT_ID`: ID do projeto Railway

### 3. Obter Tokens Railway
```bash
# Gerar token
railway login
railway tokens:create

# Obter project ID
railway status
```

## 📈 Otimizações de Performance

### 1. Configurações de Produção
```bash
# Otimizações para produção
railway variables:set PYTHONUNBUFFERED="1"
railway variables:set PYTHONDONTWRITEBYTECODE="1"
railway variables:set FLASK_ENV="production"
```

### 2. Configurar Gunicorn
Em `requirements.txt`, já incluído:
```txt
gunicorn==21.2.0
```

O `start.py` já detecta ambiente Railway e usa Gunicorn automaticamente.

### 3. Configurar Logs Estruturados
```bash
railway variables:set LOG_FORMAT="json"
railway variables:set LOG_LEVEL="INFO"
```

## 💰 Custos e Limites

### Plano Gratuito Railway
- ✅ $5 de crédito mensal
- ✅ 512MB RAM
- ✅ 1GB disco
- ✅ Domínio personalizado
- ⚠️ Sleep após inatividade

### Otimizar Custos
```bash
# Configurar sleep automático
railway variables:set RAILWAY_SLEEP_AFTER="1h"

# Monitorar uso
railway usage
```

### Plano Pro (Recomendado para Produção)
- 💰 $20/mês
- 🚀 8GB RAM
- 💾 100GB disco  
- ⚡ Sem sleep
- 📊 Métricas avançadas

## 🔐 Segurança em Produção

### 1. Configurações Obrigatórias
```bash
# Chave secreta forte
railway variables:set SECRET_KEY="$(openssl rand -hex 32)"

# Desabilitar debug
railway variables:set DEBUG="False"

# API Key forte
railway variables:set API_KEY="$(openssl rand -hex 16)"

# Webhook secret
railway variables:set WEBHOOK_SECRET="$(openssl rand -hex 20)"
```

### 2. Headers de Segurança
Já configurado no código, mas verifique:
- CORS restrito
- Rate limiting ativo
- Validação de entrada
- Sanitização de dados

### 3. Monitoramento de Segurança
```bash
# Logs de segurança
railway logs | grep -i security

# Verificar tentativas de acesso não autorizado
railway logs | grep -i "401\|403"
```

## 📋 Checklist de Deploy

### Pré-Deploy
- [ ] Testes locais passando
- [ ] Variáveis de ambiente configuradas
- [ ] Instância Waha funcionando
- [ ] Dependências atualizadas
- [ ] Logs configurados

### Deploy
- [ ] Deploy executado com sucesso
- [ ] Health check respondendo
- [ ] Logs sem erros críticos
- [ ] Domínio configurado
- [ ] SSL funcionando

### Pós-Deploy
- [ ] Webhook configurado no Waha
- [ ] Teste de envio de mensagem
- [ ] Teste de conversação
- [ ] Monitoramento ativo
- [ ] Backups configurados

### Produção
- [ ] Domínio personalizado
- [ ] Plano adequado
- [ ] Alertas configurados
- [ ] CI/CD funcionando
- [ ] Documentação atualizada

---

🎉 **Parabéns!** Seu Sistema de Cobrança Inteligente está agora rodando na Railway!

Para dúvidas ou problemas, consulte os logs e a [documentação da API](API.md).
