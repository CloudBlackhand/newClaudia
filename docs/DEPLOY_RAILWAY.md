# Guia de Deploy na Railway 🚀

Este guia detalha como fazer o deploy do Sistema de Cobrança Avançado na Railway.

## Pré-requisitos

- Conta na [Railway](https://railway.app)
- Código do projeto no GitHub
- Instância do Waha configurada (opcional para testes)

## Método 1: Deploy Automático via GitHub

### 1. Preparar o Repositório

1. **Commit e Push do código**:
   ```bash
   git add .
   git commit -m "Sistema de Cobrança Avançado completo"
   git push origin main
   ```

### 2. Conectar com Railway

1. Acesse [railway.app](https://railway.app) e faça login
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte sua conta GitHub se necessário
5. Escolha o repositório do projeto
6. A Railway detectará automaticamente o `Dockerfile` e iniciará o build

### 3. Configurar Variáveis de Ambiente

No painel da Railway, vá para a aba "Variables" e configure:

**Variáveis Obrigatórias:**
```
SECRET_KEY=sua-chave-super-secreta-aqui
PORT=8000
ENVIRONMENT=production
```

**Variáveis do Waha (se disponível):**
```
WAHA_BASE_URL=https://sua-instancia-waha.com
WAHA_API_KEY=sua-api-key-aqui
WAHA_SESSION=default
WEBHOOK_SECRET=seu-webhook-secret
```

**Variáveis Opcionais:**
```
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=100
BATCH_SIZE=50
REQUEST_TIMEOUT=30
```

### 4. Deploy Automático

O Railway iniciará automaticamente o deploy. Você pode acompanhar:
- Logs de build na aba "Deployments"
- Status na aba "Metrics"

## Método 2: Deploy Manual via CLI

### 1. Instalar Railway CLI

```bash
# Via npm
npm install -g @railway/cli

# Via curl (Linux/macOS)
curl -fsSL https://railway.app/install.sh | sh
```

### 2. Login e Configuração

```bash
# Login
railway login

# Criar novo projeto
railway new

# Ou conectar projeto existente
railway link
```

### 3. Configurar Variáveis

```bash
# Configurar variáveis uma por uma
railway variables set SECRET_KEY=sua-chave-super-secreta
railway variables set PORT=8000
railway variables set ENVIRONMENT=production

# Ou via arquivo
railway variables set --from-file environment.example
```

### 4. Deploy

```bash
# Deploy direto
railway up

# Deploy com logs
railway up --detach
railway logs
```

## Configuração Avançada

### 1. Domínio Personalizado

1. No painel Railway, vá para "Settings" > "Domains"
2. Adicione seu domínio personalizado
3. Configure DNS conforme instruções

### 2. Banco de Dados (futuro)

Se precisar de persistência:

```bash
# Adicionar PostgreSQL
railway add postgresql

# A Railway criará automaticamente as variáveis:
# DATABASE_URL, PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE
```

### 3. Redis para Cache (futuro)

```bash
# Adicionar Redis
railway add redis

# Variável automática:
# REDIS_URL
```

## Monitoramento

### 1. Logs em Tempo Real

```bash
# Via CLI
railway logs

# No painel web
# Aba "Deployments" > "View Logs"
```

### 2. Métricas

No painel Railway:
- **CPU/Memory**: Aba "Metrics"
- **Network**: Requests e bandwidth
- **Deployments**: Histórico de deploys

### 3. Health Checks

O sistema inclui endpoint de saúde:
```
GET https://seu-app.railway.app/health
```

## Configuração de Webhooks Waha

### 1. URL do Webhook

Configure no Waha:
```
https://seu-app.railway.app/api/webhooks/waha
```

### 2. Eventos Suportados

- `message.text`
- `session.status` 
- `state.change`
- `qr`
- `ready`
- `auth_failure`

### 3. Autenticação (opcional)

Se configurar `WEBHOOK_SECRET`:
```bash
railway variables set WEBHOOK_SECRET=seu-secret-aqui
```

O Waha deve incluir header:
```
X-Signature: sha256=hash-assinatura
```

## Troubleshooting

### Problemas Comuns

**1. Build falha:**
```bash
# Verificar logs
railway logs --deployment [id]

# Problemas comuns:
# - Dockerfile incorreto
# - Dependências faltando
# - Variáveis não configuradas
```

**2. App não inicia:**
```bash
# Verificar saúde
curl https://seu-app.railway.app/health

# Verificar logs
railway logs

# Variáveis obrigatórias:
railway variables set SECRET_KEY=nova-chave
railway variables set PORT=8000
```

**3. Webhook não funciona:**
```bash
# Testar endpoint
curl -X POST https://seu-app.railway.app/api/webhooks/waha \
  -H "Content-Type: application/json" \
  -d '{"event":"test","payload":{}}'

# Verificar configuração Waha
# Verificar variável WEBHOOK_SECRET
```

**4. Bot não responde:**
```bash
# Testar bot diretamente
curl -X POST https://seu-app.railway.app/api/conversation/send-message \
  -H "Content-Type: application/json" \
  -d '{"user_phone":"+5511999999999","message":"teste"}'

# Verificar logs de conversa
curl https://seu-app.railway.app/api/conversation/conversation-logs
```

### Performance

**1. Otimizações Railway:**
- Use `railway.json` para configurações específicas
- Configure restart policy para falhas
- Monitor uso de recursos

**2. Configurações de Produção:**
```bash
railway variables set MAX_CONCURRENT_REQUESTS=200
railway variables set BATCH_SIZE=25
railway variables set REQUEST_TIMEOUT=60
```

**3. Scaling:**
- Railway escala automaticamente
- Monitore métricas de CPU/Memory
- Ajuste `MAX_CONCURRENT_REQUESTS` conforme necessário

## Backup e Segurança

### 1. Variáveis Sensíveis

```bash
# Backup das variáveis
railway variables > backup-vars.txt

# NUNCA commite arquivo com secrets
echo "backup-vars.txt" >> .gitignore
```

### 2. Rollback

```bash
# Ver deploys anteriores
railway status

# Rollback para deploy específico
railway rollback [deployment-id]
```

### 3. Segurança

- Use `SECRET_KEY` forte e única
- Configure `WEBHOOK_SECRET` se usar webhooks
- Monitore logs de acesso
- Use HTTPS sempre (Railway fornece automaticamente)

## Checklist de Deploy

- [ ] Código commitado e pushed
- [ ] `Dockerfile` configurado
- [ ] `railway.json` presente
- [ ] Variáveis de ambiente configuradas
- [ ] Build realizado com sucesso
- [ ] Health check respondendo
- [ ] Frontend acessível
- [ ] API funcionando (`/docs`)
- [ ] Webhooks configurados (se aplicável)
- [ ] Logs sem erros críticos
- [ ] Performance adequada

## URLs Importantes

Após deploy bem-sucedido:

- **Frontend**: `https://seu-app.railway.app/`
- **API Docs**: `https://seu-app.railway.app/docs`
- **Health Check**: `https://seu-app.railway.app/health`
- **Webhook**: `https://seu-app.railway.app/api/webhooks/waha`

## Suporte

- **Railway Docs**: https://docs.railway.app
- **Discord Railway**: https://discord.gg/railway
- **Logs do Sistema**: `railway logs`
- **Status Railway**: https://status.railway.app
