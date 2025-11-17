# Dockerfile otimizado para EasyPanel / cloud (Python 3.12)
FROM python:3.12-slim

# Variáveis de ambiente
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

# Instala runtime + temporariamente pacotes de build necessários
# (manter 'curl' para HEALTHCHECK; 'libfreetype6-dev' e 'libpng-dev' para bibliotecas que compilam rozs)
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        curl \
        ca-certificates \
        libfreetype6-dev \
        libpng-dev \
        libgl1 \
    ; \
    rm -rf /var/lib/apt/lists/*

# Copia apenas requirements para aproveitar cache do docker
COPY requirements.txt /tmp/requirements.txt

# Normaliza requirements (remove BOM, converte CRLF -> LF) com um script Python portátil
# e instala dependências; em seguida remove pacotes de build para uma imagem mais enxuta.
RUN set -eux; \
    python -m pip install --upgrade pip setuptools wheel; \
    python - <<'PY'
from pathlib import Path
p = Path('/tmp/requirements.txt')
if not p.exists():
    raise SystemExit("requirements.txt not found in /tmp")
b = p.read_bytes()
if b.startswith(b'\xef\xbb\xbf'):
    b = b[3:]
# Normalize CRLF to LF
b = b.replace(b'\r\n', b'\n')
Path('/tmp/requirements.fixed').write_bytes(b)
PY
    ; \
    python -m pip install --no-cache-dir -r /tmp/requirements.fixed; \
    # limpar arquivos temporários e cache do pip
    rm -rf /tmp/requirements* /root/.cache/pip; \
    # remover pacotes de build que não são necessários em runtime
    apt-get purge -y --auto-remove build-essential gcc || true; \
    rm -rf /var/lib/apt/lists/*; \
    apt-get clean || true

# Copia o restante da aplicação
COPY . /app

# Cria usuário não-root (ajusta se seu app precisar de UID/GID específicos)
RUN set -eux; \
    groupadd -r appuser && useradd -r -g appuser appuser; \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

# HEALTHCHECK (mantive o endpoint que você usava; se o caminho estiver diferente, ajuste)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando padrão: ajustei para streamlit como no seu Dockerfile original.
# Substitua "app_01.py" pelo entrypoint correto da sua aplicação, se necessário.
CMD ["streamlit", "run", "app_01.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
