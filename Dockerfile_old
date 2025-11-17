# Dockerfile otimizado para ambiente cloud/EasyPanel
FROM python:3.12-slim

# Variáveis de ambiente para produção
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXSRF_PROTECTION=false \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false \
    QDRANT_HOST=qdrant \
    QDRANT_PORT=6333

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    libfreetype6-dev \
    libpng-dev \
    libgl1 \
    dos2unix \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar e instalar dependências Python
COPY requirements.txt /tmp/requirements.txt

# Instalar dependências Python com limpeza de arquivos
RUN python -m pip install --upgrade pip \
    && cp /tmp/requirements.txt /tmp/requirements.fixed \
    && dos2unix /tmp/requirements.fixed 2>/dev/null || true \
    && sed -i '1s/^\xEF\xBB\xBF//' /tmp/requirements.fixed \
    && pip install --no-cache-dir -r /tmp/requirements.fixed \
    && rm -rf /tmp/requirements* \
    && pip cache purge

# Copiar código da aplicação
COPY . /app

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

# Expor porta
EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicialização
CMD ["streamlit", "run", "app_01.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
