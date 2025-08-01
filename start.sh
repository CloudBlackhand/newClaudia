#!/bin/bash

echo "🚀 Iniciando Blacktemplar Bolter no Render..."

# Instalar dependências do Playwright se necessário
if [ ! -d "/opt/render/.cache/ms-playwright" ]; then
    echo "📦 Instalando navegadores Playwright..."
    playwright install --with-deps chromium
fi

# Criar diretórios necessários
mkdir -p uploads sessions faturas logs

# Definir variáveis de ambiente específicas do Render
export RENDER_CLOUD=true
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/.cache/ms-playwright

# Verificar memória disponível
echo "💾 Memória disponível: $(free -h | grep Mem | awk '{print $7}')"

# Iniciar aplicação
echo "✅ Iniciando servidor FastAPI..."
python app.py