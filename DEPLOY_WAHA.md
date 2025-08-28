# 🚀 DEPLOY WAHA NO RAILWAY - INSTRUÇÕES DETALHADAS

## 📋 **PASSO A PASSO COMPLETO**

### 1. **Criar Projeto WAHA no Railway**

1. Acesse [railway.app](https://railway.app)
2. Clique em **"New Project"**
3. Selecione **"Deploy from GitHub repo"**
4. Use o repositório: `whatsapp/whatsapp-http-api`
5. Clique em **"Deploy"**

### 2. **Configurar Variáveis de Ambiente**

No projeto WAHA criado, vá em **"Variables"** e configure:

```env
# Configurações básicas
NODE_ENV=production
PORT=3000

# Configurações do WAHA
WAHA_INSTANCE_NAME=claudia-cobrancas
WAHA_WEBHOOK_URL=https://bot-cobranca-production.up.railway.app/webhook
WAHA_WEBHOOK_BY_EVENTS=false
WAHA_WEBHOOK_BASE64=false

# Configurações de segurança
WAHA_AUTH_TOKEN=claudia-secret-token-2024
```

### 3. **Obter URL do WAHA**

1. No projeto WAHA, vá em **"Settings"**
2. Copie a **"Custom Domain"** ou use a URL gerada
3. A URL será algo como: `https://waha-claudia.up.railway.app`

### 4. **Configurar Claudia com a URL do WAHA**

No projeto **Bot-cobranca**, configure a variável:

```env
WAHA_URL=https://waha-claudia.up.railway.app
```

### 5. **Testar Conexão**

Execute o script de teste:

```bash
python3 check_waha.py
```

## 🔧 **CONFIGURAÇÃO ALTERNATIVA - DOCKER**

Se preferir usar Docker, crie um `Dockerfile` para o WAHA:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# Instalar WAHA
RUN npm install -g @open-wa/wa-automate

# Expor porta
EXPOSE 3000

# Comando de inicialização
CMD ["wa-automate", "start", "--port", "3000"]
```

## 🧪 **TESTE MANUAL**

### Testar WAHA diretamente:

```bash
# Verificar se está rodando
curl https://waha-claudia.up.railway.app/api/instances

# Criar instância
curl -X POST https://waha-claudia.up.railway.app/api/instances/create \
  -H "Content-Type: application/json" \
  -d '{"instanceName": "test"}'

# Verificar status
curl https://waha-claudia.up.railway.app/api/instances/test/info
```

## 🚨 **TROUBLESHOOTING**

### Problema: "Application not found"
- ✅ Verifique se o projeto WAHA foi criado
- ✅ Confirme se o deploy foi concluído
- ✅ Aguarde alguns minutos após o deploy

### Problema: "Connection refused"
- ✅ Verifique se a URL está correta
- ✅ Confirme se o WAHA está rodando
- ✅ Teste a URL no navegador

### Problema: "Timeout"
- ✅ Verifique se o WAHA não está sobrecarregado
- ✅ Aguarde alguns segundos e tente novamente

## 📊 **MONITORAMENTO**

### Logs do WAHA:
1. No Railway Dashboard
2. Vá em **"Deployments"**
3. Clique em **"View Logs"**

### Status da Instância:
```bash
curl https://waha-claudia.up.railway.app/api/instances/claudia-cobrancas/info
```

## ✅ **CHECKLIST FINAL**

- [ ] Projeto WAHA criado no Railway
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy concluído com sucesso
- [ ] URL do WAHA obtida
- [ ] Variável WAHA_URL configurada no Bot-cobranca
- [ ] Teste de conexão passando
- [ ] Claudia conectada ao WAHA

---

**🎯 RESULTADO: WAHA funcionando + Claudia conectada!**
