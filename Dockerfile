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

# Instalar dependências do SO
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    ca-certificates \
    libfreetype6-dev \
    libpng-dev \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt /tmp/requirements.txt

# Normalizar e instalar requirements sem HEREDOC problemático
RUN python -m pip install --upgrade pip setuptools wheel && \
    python - <<EOF
from pathlib import Path
p = Path('/tmp/requirements.txt')
b = p.read_bytes()
# remove BOM
if b.startswith(b'\xef\xbb\xbf'):
    b = b[3:]
# normaliza CRLF
b = b.replace(b'\r\n', b'\n')
Path('/tmp/requirements.fixed').write_bytes(b)
EOF

RUN pip install --no-cache-dir -r /tmp/requirements.fixed && \
    rm -rf /tmp/requirements* /root/.cache/pip && \
    apt-get purge -y --auto-remove build-essential gcc || true && \
    apt-get clean

# Copiar aplicação
COPY . /app

# Criar usuário não-root
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8501

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando principal
CMD ["streamlit", "run", "app_01.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
