FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema + Chrome (método moderno)
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    ca-certificates \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Criar diretórios necessários
RUN mkdir -p logs data temp

# Copiar código da aplicação (estrutura completa)
COPY . .

# Verificar estrutura dos arquivos
RUN ls -la && echo "=== ESTRUTURA BACKEND ===" && ls -la backend/ || echo "BACKEND NÃO ENCONTRADO"

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "backend/app.py"]
