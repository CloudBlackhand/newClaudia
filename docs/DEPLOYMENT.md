# Guia de Deploy - Sistema de Cobrança Inteligente

## Visão Geral

Este documento fornece instruções completas para deploy do Sistema de Cobrança Inteligente na Railway e outras plataformas de hospedagem.

## Pré-requisitos

### Contas e Serviços Necessários
- [ ] Conta na Railway (railway.app)
- [ ] Servidor Waha configurado
- [ ] Repositório Git (GitHub, GitLab, etc.)
- [ ] WhatsApp Business (para integração)

### Ferramentas Locais
- [ ] Git
- [ ] Python 3.11+
- [ ] Node.js 18+ (opcional, para desenvolvimento)

## Deploy na Railway

### 1. Preparação do Repositório

```bash
# Clone o repositório
git clone <seu-repositorio>
cd cobrança

# Verifique se todos os arquivos estão presentes
ls -la

# Estrutura necessária:
# ├── backend/
# ├── frontend/
# ├── requirements.txt
# ├── Dockerfile
# ├── railway.toml
# └── README.md
```

### 2. Configuração na Railway

#### 2.1 Criação do Projeto
1. Acesse [railway.app](https://railway.app)
2. Faça login ou crie uma conta
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Conecte seu repositório

#### 2.2 Configuração das Variáveis de Ambiente

No painel da Railway, vá em "Variables" e configure:

```env
# Aplicação
FLASK_ENV=production
SECRET_KEY=seu_secret_key_super_seguro_aqui
PORT=8000
DEBUG=False

# Waha Integration
WAHA_BASE_URL=https://seu-waha-server.com
WAHA_API_KEY=sua_api_key_waha
WAHA_SESSION_NAME=cobranca_session
WAHA_WEBHOOK_URL=https://seu-app.railway.app/webhook/waha

# Segurança
JWT_SECRET_KEY=jwt_secret_key_super_seguro
ENCRYPTION_KEY=encryption_key_32_caracteres
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Modelo
MODEL_PATH=models/chatbot_model.pth
MODEL_CACHE_SIZE=100
MODEL_MAX_LENGTH=512
MODEL_TEMPERATURE=0.7
USE_GPU=False

# Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=data/uploads
ALLOWED_EXTENSIONS=json,txt,csv

# Monitoramento
ENABLE_METRICS=True
METRICS_PORT=9090
```

#### 2.3 Configuração do Domínio

1. Na Railway, vá em "Settings" > "Domains"
2. Clique em "Generate Domain" para obter um domínio .railway.app
3. Ou configure um domínio customizado

### 3. Deploy Automático

#### 3.1 Configuração do railway.toml

O arquivo `railway.toml` já está configurado:

```toml
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
PYTHON_VERSION = "3.11"
PORT = "8000"
FLASK_ENV = "production"
LOG_LEVEL = "INFO"

[services.web]
startCommand = "gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 300 backend.app:app"
healthcheckPath = "/health"

[services.web.env]
WEB_CONCURRENCY = "4"
MAX_WORKERS = "4"
```

#### 3.2 Processo de Deploy

1. Faça commit das alterações:
```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

2. A Railway detectará automaticamente as mudanças e iniciará o deploy

3. Monitore o progresso na aba "Deployments"

### 4. Verificação do Deploy

#### 4.1 Health Check
```bash
curl https://seu-app.railway.app/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

#### 4.2 Teste da API
```bash
# Login
curl -X POST https://seu-app.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Status Waha
curl -X GET https://seu-app.railway.app/api/waha/status \
  -H "Authorization: Bearer SEU_TOKEN"
```

## Configuração do Waha

### 1. Setup do Servidor Waha

#### Opção 1: Docker (Recomendado)
```bash
# Crie um docker-compose.yml
version: '3.8'
services:
  waha:
    image: devlikeapro/waha:latest
    ports:
      - "3000:3000"
    environment:
      - WHATSAPP_HOOK_URL=https://seu-app.railway.app/webhook/waha
      - WHATSAPP_HOOK_EVENTS=message,message.any,state.change
    volumes:
      - ./waha-data:/app/session
    restart: unless-stopped

# Execute
docker-compose up -d
```

#### Opção 2: Railway Service
1. Crie um novo service na Railway
2. Use a imagem `devlikeapro/waha:latest`
3. Configure as variáveis de ambiente necessárias

### 2. Configuração da Integração

1. **Inicie a sessão Waha**:
```bash
curl -X POST http://seu-waha-server:3000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cobranca_session",
    "config": {
      "webhooks": [{
        "url": "https://seu-app.railway.app/webhook/waha",
        "events": ["message", "message.any", "state.change"]
      }]
    }
  }'
```

2. **Obtenha o QR Code**:
```bash
curl http://seu-waha-server:3000/api/sessions/cobranca_session/auth/qr
```

3. **Escaneie com WhatsApp** para autenticar

## Deploy em Outras Plataformas

### Heroku

1. **Procfile**:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 backend.app:app
```

2. **Deploy**:
```bash
heroku create seu-app-cobranca
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=seu_secret_key
# ... outras variáveis
git push heroku main
```

### DigitalOcean App Platform

1. **app.yaml**:
```yaml
name: cobranca-inteligente
services:
- name: web
  source_dir: /
  github:
    repo: seu-usuario/seu-repo
    branch: main
  run_command: gunicorn --bind 0.0.0.0:$PORT --workers 4 backend.app:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
  - key: SECRET_KEY
    value: seu_secret_key
```

### AWS Elastic Beanstalk

1. **requirements.txt** na raiz do projeto
2. **application.py**:
```python
from backend.app import app as application

if __name__ == "__main__":
    application.run()
```

3. **Deploy**:
```bash
eb init
eb create cobranca-production
eb deploy
```

### Google Cloud Run

1. **cloudbuild.yaml**:
```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/cobranca:$COMMIT_SHA', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/cobranca:$COMMIT_SHA']
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'cobranca', '--image', 'gcr.io/$PROJECT_ID/cobranca:$COMMIT_SHA', '--region', 'us-central1', '--platform', 'managed']
```

## Monitoramento e Logs

### 1. Railway Logs

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs
railway logs

# Logs em tempo real
railway logs --follow
```

### 2. Configuração de Alertas

#### Uptime Monitoring
Configure monitores em:
- UptimeRobot
- Pingdom
- StatusCake

URL para monitorar: `https://seu-app.railway.app/health`

#### Log Monitoring
Para aplicações em produção, considere:
- Sentry (para erros)
- LogRocket (para monitoramento)
- DataDog (para métricas)

### 3. Backup e Disaster Recovery

#### Backup de Configurações
```bash
# Export das variáveis de ambiente
railway variables > backup-env.txt

# Backup dos templates
curl -H "Authorization: Bearer TOKEN" \
  https://seu-app.railway.app/api/billing/templates > templates-backup.json
```

#### Disaster Recovery Plan
1. **Repositório Git**: Sempre up-to-date
2. **Variáveis de Ambiente**: Documentadas e backup
3. **Dados de Configuração**: Export regular
4. **Waha Session**: Backup da pasta de sessão

## Configurações de Produção

### 1. Segurança

#### SSL/TLS
- Railway fornece SSL automático
- Verifique se `HTTPS` está funcionando

#### Environment Variables
```env
# Nunca commitar no Git
SECRET_KEY=use_gerador_de_senha_forte
JWT_SECRET_KEY=outro_secret_forte  
ENCRYPTION_KEY=chave_de_32_caracteres_exatos

# API Keys
WAHA_API_KEY=sua_api_key_waha_real
```

#### Headers de Segurança
O sistema já inclui headers de segurança automáticos:
- HSTS
- X-Frame-Options
- X-Content-Type-Options
- CSP

### 2. Performance

#### Configuração do Gunicorn
```bash
# Para aplicações pequenas (Railway basic)
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 backend.app:app

# Para aplicações médias
gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 300 backend.app:app

# Para aplicações grandes
gunicorn --bind 0.0.0.0:$PORT --workers 8 --timeout 300 \
  --worker-class gevent --worker-connections 1000 backend.app:app
```

#### Cache e Otimização
- CDN para assets estáticos
- Compressão gzip (automática na Railway)
- Cache de modelos ML em memória

### 3. Escalabilidade

#### Scaling Horizontal (Railway)
1. Vá em "Settings" > "Scale"
2. Ajuste RAM e CPU conforme necessário
3. Para múltiplas instâncias, considere load balancer

#### Database (se necessário)
Para persistência de dados:
```bash
# PostgreSQL na Railway
railway add postgresql

# Configure no código
DATABASE_URL=postgresql://...
```

## Troubleshooting

### Problemas Comuns

#### 1. Build Failure
```bash
# Verifique requirements.txt
pip install -r requirements.txt

# Verifique Python version
python --version  # Deve ser 3.11+
```

#### 2. Application Crash
```bash
# Verifique logs
railway logs

# Verifique health endpoint
curl https://seu-app.railway.app/health
```

#### 3. Waha Integration Issues
```bash
# Teste conectividade
curl http://seu-waha-server:3000/api/sessions

# Verifique webhook
curl -X POST https://seu-app.railway.app/webhook/waha \
  -H "Content-Type: application/json" \
  -d '{"event": "test"}'
```

#### 4. Memory Issues
- Aumente RAM na Railway
- Otimize modelos ML
- Implemente cache cleanup

#### 5. Timeout Issues
- Aumente timeout do Gunicorn
- Configure timeout na Railway
- Otimize operações assíncronas

### Debugging

#### Local Testing
```bash
# Teste localmente com variáveis de produção
export FLASK_ENV=production
export SECRET_KEY=your_secret
python backend/app.py
```

#### Production Debugging
```bash
# Enable debug mode temporariamente
railway variables set DEBUG=True

# Não esqueça de desabilitar
railway variables set DEBUG=False
```

## Checklist Final

### Pré-Deploy
- [ ] Todas as variáveis de ambiente configuradas
- [ ] Secrets seguros (não commitados)
- [ ] Testes passando
- [ ] Dockerfile otimizado
- [ ] railway.toml configurado

### Pós-Deploy
- [ ] Health check funcionando
- [ ] API endpoints respondendo
- [ ] Integração Waha ativa
- [ ] Logs sendo gerados
- [ ] Monitoring configurado
- [ ] Backup strategy definida

### Produção
- [ ] SSL ativo
- [ ] Domain configurado
- [ ] Performance aceitável
- [ ] Escalabilidade testada
- [ ] Security headers ativos
- [ ] Error tracking ativo

## Suporte e Manutenção

### Updates
```bash
# Update do código
git pull origin main
git push origin main  # Deploy automático

# Update de dependências
pip install -r requirements.txt --upgrade
```

### Monitoring Scripts
```bash
#!/bin/bash
# health-check.sh
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://seu-app.railway.app/health)
if [ $RESPONSE != "200" ]; then
    echo "Application is down! Status: $RESPONSE"
    # Send alert
fi
```

### Maintenance Windows
- Updates de segurança: Imediatos
- Updates de features: Janelas programadas
- Database migrations: Backup + maintenance mode

---

**Importante**: Mantenha este documento atualizado conforme o sistema evolui e sempre teste em ambiente de staging antes de aplicar mudanças em produção.

