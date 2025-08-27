# Dockerfile para a aplicação RAG
FROM python:3.13-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para logs
RUN mkdir -p logs

# Expor porta
EXPOSE 5000

# Variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_APP=src/app.py
ENV FLASK_ENV=production

# Comando para executar a aplicação
CMD ["gunicorn", "--config", "gunicorn.conf.py", "src.app:app"]
