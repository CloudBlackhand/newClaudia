# Dockerfile para Claudia Cobranças - Bot de Conversação
FROM python:3.11-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV RAILWAY_DEPLOY=True

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements_minimal.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements_minimal.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs temp web/static

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["python", "railway_startup.py"]
