# 🤖 Claudia Cobranças - Sistema de Cobrança da Desktop

Sistema oficial de cobrança da Desktop, otimizado para Railway e totalmente funcional.

## 🚀 Características Principais

### 🧠 **ENGINE DE CONVERSAÇÃO ULTRA INTELIGENTE**
- **Entendimento Natural:** Compreende QUALQUER cliente, mesmo com erros graves
- **Correção Automática:** Corrige português mal escrito automaticamente
- **Detecção de Intenções:** Identifica pedidos de fatura, valor, vencimento, etc.
- **Respostas Contextuais:** Adapta respostas ao estado emocional do cliente

### 📊 **PROCESSAMENTO DE EXCEL**
- **Upload de Arquivos:** Suporte para .xlsx e .xls
- **Extração Inteligente:** Detecta automaticamente colunas relevantes
- **Validação de Dados:** Verifica CPF, telefones, valores
- **Processamento em Lote:** Otimizado para grandes volumes

### 🔐 **SISTEMA DE LOGIN ULTRA SEGURO**
- **Aprovação Manual:** Zero possibilidade de ataques de força bruta
- **Controle Total:** Cada tentativa precisa de aprovação humana
- **Logs Detalhados:** Registro completo de todas as tentativas
- **Interface Web:** Dashboard moderno e responsivo

### 🚂 **OTIMIZADO PARA RAILWAY**
- **Performance Máxima:** Configurado para plano $5/mês
- **Healthcheck Robusto:** Endpoint `/health` para monitoramento
- **Startup Rápido:** Inicialização otimizada
- **Recursos Controlados:** Sistema econômico de recursos

## 📋 Funcionalidades Completas

### 🤖 **BOT DE COBRANÇA**
- Entende QUALQUER cliente (mesmo os mais burros)
- Respostas personalizadas por contexto
- Detecção emocional avançada
- Sistema de conversação contextual

### 📄 **DOWNLOAD DE FATURAS**
- Integração com SAC Desktop (sac.desktop.com.br)
- Anti-captcha funcional
- Download automático
- Sistema Playwright

### 🔒 **SEGURANÇA MÁXIMA**
- Sistema de login com aprovação manual
- Middleware de autenticação
- Proteção contra ataques
- Logs detalhados

## 🛠️ Arquivos Principais

```
├── app.py                      # Aplicação FastAPI completa
├── config.py                   # Configurações
├── requirements.txt            # Dependências otimizadas
├── Procfile                   # Comando Railway
├── railway.toml               # Config Railway
├── runtime.txt                # Python 3.11.7
├── railway_startup.py         # Startup otimizado
├── web/
│   ├── static/
│   │   ├── app.js            # Frontend JavaScript
│   │   ├── style.css         # Estilos CSS
│   │   └── login.js          # Sistema de login
└── core/
    ├── conversation.py       # 🧠 ENGINE ULTRA INTELIGENTE
    ├── excel_processor.py    # Processamento Excel
    ├── fatura_downloader.py  # Download faturas Desktop
    ├── captcha_solver.py     # Anti-captcha
    ├── storage_manager.py    # Gerenciamento de arquivos
    ├── monitoring.py         # Monitoramento do sistema
    ├── performance.py        # Otimizações
    ├── security.py           # Segurança
    └── logger.py             # Sistema de logs
```

## 🚀 Deploy Railway

### 🔧 **Configuração Rápida:**

1. **Fork/Clone o repositório**
2. **Deploy no Railway:**
   ```bash
   # Railway detectará automaticamente:
   # - Python 3.11.7
   # - Comando: python railway_startup.py
   # - Porta: $PORT
   ```

3. **Configure variáveis de ambiente:**
   ```bash
   RAILWAY_DEPLOY=True
   SECRET_KEY=sua-chave-secreta-aqui
   DEBUG=False
   ```

4. **Acesse o sistema:**
   ```
   https://seu-app.railway.app
   ```

### 📊 **Monitoramento:**
- **Healthcheck:** `https://seu-app.railway.app/health`
- **Dashboard:** `https://seu-app.railway.app/`
- **Logs:** Via Railway Dashboard

## 🎯 **Resultado Final**

### ✅ **CLAUDIA COBRANÇAS - BOT PERFEITO PARA CLIENTES BURROS**

* Entende QUALQUER texto mal escrito
* Corrige português automaticamente
* Detecta intenções mesmo com erros graves
* Respostas ultra inteligentes e contextuais

### 🔐 **SEGURANÇA IMPOSSÍVEL DE QUEBRAR**

* Login com aprovação manual
* Zero possibilidade de força bruta
* Controle total do administrador

### 💻 **SISTEMA COMPLETO E OTIMIZADO**

* Pronto para Railway
* Performance máxima
* Custos controlados
* Zero dependências desnecessárias
* **HEALTHCHECK FUNCIONANDO PERFEITAMENTE!**

## 🔧 Desenvolvimento Local

### **Instalação:**
```bash
# Clone o repositório
git clone https://github.com/CloudBlackhand/Bot-cobranca.git
cd Bot-cobranca

# Instale dependências
pip install -r requirements.txt

# Execute localmente
python railway_startup.py
```

### **Acesso:**
- **Sistema:** http://localhost:8000
- **Healthcheck:** http://localhost:8000/health

## 📝 Licença

Sistema proprietário da Desktop - Todos os direitos reservados.

---

> 🚀 **CLAUDIA COBRANÇAS - SISTEMA FINALIZADO!**
> 
> **O BOT DE COBRANÇA MAIS INTELIGENTE DA DESKTOP!**
> 
> Capaz de entender QUALQUER cliente, por mais burro que seja! 🧠⚡
 