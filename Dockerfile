# Dockerfile otimizado para EasyPanel / builds que precisam compilar extensões nativas
FROM python:3.12-slim

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

# Instalar ferramentas de build e dependências do sistema necessárias para compilar wheels
# Usamos um grupo "build-deps" para remover depois e minimizar imagem final.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    git \
    curl \
    ca-certificates \
    dos2unix \
    # libs para Pillow, wordcloud, e similares:
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    libtiff5-dev \
    # libs que podem ser necessárias por bindings nativos (opcional mas útil):
    libglib2.0-0 \
    libgl1 \
    # OpenSSL headers (p/ cryptography, etc.)
    libssl-dev \
    # Rust toolchain (algumas libs usam rust/cargo, ex: tokenizers)
    cargo \
  && rm -rf /var/lib/apt/lists/*

# Copiar requirements (se existir)
COPY requirements.txt /tmp/requirements.txt

# Atualizar pip/setuptools/wheel, instalar dependências python
RUN python -m pip install --upgrade pip setuptools wheel \
 && cp /tmp/requirements.txt /tmp/requirements.fixed \
 && dos2unix /tmp/requirements.fixed 2>/dev/null || true \
 && sed -i '1s/^\xEF\xBB\xBF//' /tmp/requirements.fixed \
 && pip install --no-cache-dir -r /tmp/requirements.fixed

# LIMPEZA: remover caches e arquivos temporários de pip
RUN rm -rf /tmp/requirements* \
 && pip cache purge || true

# (Opcional) Se quiser reduzir mais a imagem, remover toolchain de build
# *Cuidado*: se houver necessidade posterior de compilar algo em tempo de execução, não remova.
RUN apt-get purge -y --auto-remove gcc g++ build-essential make pkg-config cargo \
 && rm -rf /var/lib/apt/lists/* || true

# Copiar código da aplicação
COPY . /app

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

# Healthcheck simples (streamlit)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501 || exit 1

CMD ["streamlit", "run", "app_01.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
