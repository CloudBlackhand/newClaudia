# 🤖 Claudia Cobranças - Bot de Conversação Inteligente

Bot inteligente de conversação da Desktop, focado em entender e responder às pessoas de forma natural e eficiente.

## 🚀 **CARACTERÍSTICAS PRINCIPAIS**

### 🧠 **BOT DE CONVERSAÇÃO INTELIGENTE**
- **Detecção de Intenções:** Identifica pedidos, dúvidas, solicitações
- **Respostas Contextuais:** Mantém contexto da conversa
- **Processamento Natural:** Entende linguagem coloquial
- **Múltiplas Intenções:** Detecta intenções combinadas

### 🔐 **SISTEMA DE AUTENTICAÇÃO**
- **Login Seguro:** Sistema de autenticação manual
- **Sessões Ativas:** Controle de acesso por token
- **Timeout Configurável:** Sessões com expiração automática

### 🌐 **INTERFACE WEB**
- **Dashboard Moderno:** Interface responsiva e intuitiva
- **Teste de Conversação:** Teste direto do bot
- **Logs em Tempo Real:** Monitoramento de atividades
- **Status do Sistema:** Informações em tempo real

## 📁 **ESTRUTURA DO PROJETO**

```
claudia-cobrancas/
├── app.py                 # Aplicação principal FastAPI
├── config.py              # Configurações do sistema
├── railway_startup.py     # Script de inicialização Railway
├── install_railway.py     # Instalação de dependências
├── requirements.txt       # Dependências completas
├── requirements_minimal.txt # Dependências essenciais
├── Dockerfile            # Container Docker
├── Procfile              # Configuração Railway
├── railway.toml          # Configuração Railway
├── core/
│   ├── __init__.py       # Inicialização dos módulos
│   └── conversation.py   # Engine de conversação
└── web/
    └── static/
        ├── app.js        # Interface JavaScript
        ├── style.css     # Estilos CSS
        └── icon.png      # Ícone do sistema
```

## 🚂 **DEPLOY NO RAILWAY**

### **1. Preparação**
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/claudia-cobrancas.git
cd claudia-cobrancas

# Verifique se está tudo pronto
python railway_startup.py
```

### **2. Deploy no Railway**
1. **Conecte ao Railway:**
   ```bash
   railway login
   railway init
   ```

2. **Configure as variáveis de ambiente:**
   ```bash
   railway variables set RAILWAY_DEPLOY=True
   railway variables set DEBUG=False
   ```

3. **Faça o deploy:**
   ```bash
   railway up
   ```

### **3. Configuração Pós-Deploy**
1. **Acesse o dashboard:** `https://seu-app.railway.app`
2. **Teste o bot:** Use a seção de conversação
3. **Monitore logs:** Verifique a seção de logs

## 🔧 **DESENVOLVIMENTO LOCAL**

### **Instalação**
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar
python app.py
```

### **Testes**
```bash
# Testar conversação
curl -X POST http://localhost:8000/api/conversation/test \
  -H "Content-Type: application/json" \
  -d '{"message": "quanto eu devo?"}'

# Verificar status
curl http://localhost:8000/health
```

## 📊 **API ENDPOINTS**

### **Conversação**
- `POST /api/conversation/test` - Testar conversação

### **Sistema**
- `GET /health` - Healthcheck
- `GET /api/stats` - Estatísticas
- `GET /api/logs` - Logs do sistema

### **Autenticação**
- `POST /api/auth/request` - Solicitar login
- `GET /api/auth/status/{id}` - Status da solicitação
- `GET /api/auth/approve/{id}` - Aprovar acesso
- `GET /api/auth/reject/{id}` - Rejeitar acesso

## 🎯 **CONFIGURAÇÕES**

### **Variáveis de Ambiente**
```bash
RAILWAY_DEPLOY=True      # Modo Railway
DEBUG=False             # Modo debug
PORT=8000              # Porta do servidor
SECRET_KEY=chave-secreta # Chave de segurança
```

### **Configurações de Performance**
- **Workers:** 1 (Railway) / 4 (Desenvolvimento)
- **Timeout:** 30s (Railway) / 60s (Desenvolvimento)
- **Cache:** Habilitado no Railway
- **Compressão:** Ativa no Railway

## 🔍 **MONITORAMENTO**

### **Logs**
- Logs em tempo real via interface web
- Níveis: INFO, WARNING, ERROR
- Rotação automática

### **Métricas**
- Mensagens processadas
- Conversações ativas
- Status do bot
- Performance do sistema

## 🛠️ **TECNOLOGIAS**

- **Backend:** FastAPI + Python 3.11
- **Frontend:** JavaScript + Bootstrap 5
- **Deploy:** Railway
- **Container:** Docker
- **Processamento:** Engine de conversação customizada

## 📈 **ROADMAP**

- [ ] Integração com WhatsApp (WAHA)
- [ ] Machine Learning para melhorar respostas
- [ ] Sistema de notificações
- [ ] Analytics avançado
- [ ] Multi-idioma

## 🤝 **CONTRIBUIÇÃO**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 **LICENÇA**

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 **SUPORTE**

- **Email:** cobranca@desktop.com.br
- **Website:** https://sac.desktop.com.br
- **Documentação:** Este README

---

**Desenvolvido com ❤️ pela Desktop**
 