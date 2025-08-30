FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo o código
COPY . .

# Configurar ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]