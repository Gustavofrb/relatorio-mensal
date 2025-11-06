# Dockerfile para Fechamento Mensal Seazone
FROM python:3.11-slim

# Metadados
LABEL maintainer="Seazone Tech Team"
LABEL description="Automação de Fechamento Mensal - Pipeline de Dados e IA"

# Diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache do Docker)
COPY src/requirements.txt /app/requirements.txt


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY src/ /app/


RUN mkdir -p /app/data /app/output

# Copiar entrypoint 
COPY docker/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando padrão (mantém container rodando para n8n executar)
CMD ["tail", "-f", "/dev/null"]
