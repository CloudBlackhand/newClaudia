# 🤖 Blacktemplar Bolter - SuperBot de Cobrança

Sistema de cobrança automatizada 100% gratuito com interface web e recursos avançados.

## ⚡ Principais Funcionalidades

- 🌐 **Interface Web** - Upload de planilhas via browser
- 📱 **WhatsApp Web.js** - Login via QR Code, sem dependências Node.js
- 🔓 **Anti-Captcha** - Integração com GoogleRecaptchaBypass local
- 🥷 **Sistema Stealth** - Comportamento humano, simulação de digitação
- 💬 **Conversação Inteligente** - Engine baseada em regras (sem IA paga)
- 📊 **Processamento Excel** - FPD + VENDAS/contratos automático
- ☁️ **Cloud Ready** - Deploy otimizado para Oracle Cloud e outros provedores
- 🚀 **100% Gratuito** - Sem APIs pagas

## 🏗️ Arquitetura

```
Blacktemplar Bolter/
├── app.py                  # FastAPI principal
├── config.py              # Configurações
├── requirements.txt       # Dependências mínimas
├── Dockerfile             # Container otimizado
├── core/
│   ├── __init__.py
│   ├── excel_processor.py # Processa FPD + VENDAS
│   ├── whatsapp_client.py # WhatsApp Web.js integration
│   ├── captcha_solver.py  # Anti-captcha local
│   ├── conversation.py    # Engine de conversação
│   ├── fatura_downloader.py # Download sem Selenium
│   └── stealth_sender.py  # Envios stealth
├── web/
│   ├── static/           # CSS, JS
│   └── templates/        # HTML templates
├── uploads/              # Planilhas temporárias
└── faturas/             # Faturas baixadas
```

## 🎯 Workflow Automático

1. **Login WhatsApp** - QR Code via interface web
2. **Upload Planilhas** - FPD + VENDAS via drag & drop
3. **Processamento** - Localiza protocolos automaticamente
4. **Cobrança Stealth** - Envios rápidos com simulação humana
5. **Atendimento 24/7** - Responde solicitações de fatura
6. **Anti-Detecção** - Resolve captchas, varia comportamento

## 🚀 Deploy

### Oracle Cloud (Recomendado)

Para implantar no Oracle Cloud, use o script de deploy especializado:

```bash
# Tornar executável
chmod +x oracle_deploy.sh

# Executar script de configuração automática
sudo ./oracle_deploy.sh
```

Detalhes de configuração avançada estão disponíveis em:
- `README_ORACLE_CLOUD.md` - Guia completo de implantação
- `oracle_cloud_setup.md` - Instruções detalhadas de configuração

### Outros Provedores Gratuitos

- **Railway**
- **Render**
- **Fly.io**
- **Heroku** (com limitações)

Para deploy automático em provedores com CI/CD:
```bash
git push origin main
``` 