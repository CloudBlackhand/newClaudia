# 🚀 DEPLOY WAHA NO RAILWAY - CLAUDIA COBRANÇAS

## 📋 **PASSO A PASSO PARA DEPLOY**

### 1. **Criar Projeto WAHA no Railway**

```bash
# 1. Acesse railway.app
# 2. Clique em "New Project"
# 3. Selecione "Deploy from GitHub repo"
# 4. Use o repositório: whatsapp/whatsapp-http-api
```

### 2. **Configurar Variáveis de Ambiente**

```env
# Configurações básicas
NODE_ENV=production
PORT=3000

# Configurações do WAHA
WAHA_INSTANCE_NAME=claudia-cobrancas
WAHA_WEBHOOK_URL=https://seu-claudia-app.railway.app/webhook
WAHA_WEBHOOK_BY_EVENTS=false
WAHA_WEBHOOK_BASE64=false

# Configurações de segurança
WAHA_AUTH_TOKEN=seu-token-secreto-aqui
```

### 3. **Configurar Build**

```json
// nixpacks.toml
[phases.setup]
nixPkgs = ["nodejs", "npm"]

[phases.install]
cmds = ["npm install"]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "npm start"
```

### 4. **Conectar Claudia ao WAHA**

1. **No projeto Claudia, configure:**
   ```env
   WAHA_URL=https://seu-waha-app.railway.app
   WEBHOOK_URL=https://seu-claudia-app.railway.app/webhook
   ```

2. **Teste a conexão:**
   ```bash
   python test_waha.py
   ```

### 5. **Verificar Funcionamento**

1. **Acesse o WAHA:**
   ```
   https://seu-waha-app.railway.app
   ```

2. **Crie instância:**
   ```bash
   curl -X POST https://seu-waha-app.railway.app/api/instances/create \
     -H "Content-Type: application/json" \
     -d '{"instanceName": "claudia-cobrancas"}'
   ```

3. **Inicie instância:**
   ```bash
   curl -X POST https://seu-waha-app.railway.app/api/instances/claudia-cobrancas/start
   ```

4. **Obtenha QR Code:**
   ```bash
   curl https://seu-waha-app.railway.app/api/instances/claudia-cobrancas/qr
   ```

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **Webhook Configuration**

```json
{
  "webhook": "https://seu-claudia-app.railway.app/webhook",
  "webhookByEvents": false,
  "webhookBase64": false,
  "events": ["messages.upsert", "connection.update"]
}
```

### **Instance Management**

```bash
# Listar instâncias
curl https://seu-waha-app.railway.app/api/instances

# Status da instância
curl https://seu-waha-app.railway.app/api/instances/claudia-cobrancas/info

# Deletar instância
curl -X DELETE https://seu-waha-app.railway.app/api/instances/claudia-cobrancas
```

## 🧪 **TESTES**

### **Teste de Conexão**
```bash
python test_waha.py
```

### **Teste de Webhook**
```bash
curl -X POST https://seu-claudia-app.railway.app/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": {"test": true}}'
```

## 📊 **MONITORAMENTO**

### **Logs do WAHA**
```bash
# No Railway Dashboard
# Vá em "Deployments" > "View Logs"
```

### **Status da Instância**
```bash
curl https://seu-waha-app.railway.app/api/instances/claudia-cobrancas/info
```

## 🚨 **TROUBLESHOOTING**

### **Problema: WAHA não responde**
- Verifique se o projeto está rodando no Railway
- Confirme as variáveis de ambiente
- Verifique os logs de deploy

### **Problema: QR Code não aparece**
- Aguarde alguns segundos após iniciar a instância
- Verifique se a instância está ativa
- Tente deletar e recriar a instância

### **Problema: Webhook não recebe mensagens**
- Verifique se a URL do webhook está correta
- Confirme se o endpoint `/webhook` está funcionando
- Teste com curl para verificar conectividade

## ✅ **CHECKLIST FINAL**

- [ ] WAHA deployado no Railway
- [ ] Variáveis de ambiente configuradas
- [ ] Instância criada e iniciada
- [ ] QR Code escaneado
- [ ] Webhook configurado
- [ ] Claudia conectada ao WAHA
- [ ] Testes passando
- [ ] Mensagens sendo enviadas/recebidas

---

**🎯 RESULTADO: Claudia Cobranças funcionando com WAHA no Railway!**
