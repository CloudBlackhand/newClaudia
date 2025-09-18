# Teste do Modelo Qwen2.5-1.5B no Railway

Este projeto testa o modelo de IA Qwen2.5-1.5B quantizado no Railway.

## 🚀 Deploy no Railway

1. Instale o Railway CLI:
```bash
curl -fsSL https://railway.com/install.sh | sh
```

2. Faça login:
```bash
railway login
```

3. Conecte ao projeto:
```bash
railway link -p 7e3ed4cd-ecd1-4142-9bf4-e0c13a4fe487
```

4. Faça o deploy:
```bash
railway up
```

## 📊 Endpoints

- `GET /` - Status do modelo
- `GET /health` - Health check
- `POST /generate` - Gerar resposta
- `GET /test` - Teste simples

## 🔧 Configurações

- **Modelo**: Qwen2.5-1.5B-unsloth-bnb-4bit
- **Quantização**: 4-bit
- **RAM necessária**: ~4-6GB
- **CPU**: 8 vCPU (Railway Hobby Plan)

## 📝 Exemplo de Uso

```bash
curl -X POST https://seu-app.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Olá, como você está?"}'
```
