# Dockerfile final — instala TORCH CPU primeiro para evitar downloads CUDA enormes
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
    QDRANT_PORT=6333 \
    HOME=/home/appuser \
    HF_HOME=/home/appuser/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers \
    TORCH_HOME=/home/appuser/.cache/torch \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib

WORKDIR /app

# Instala dependências do SO (mantemos curl)
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

# Copia requirements (para cache)
COPY requirements.txt /tmp/requirements.txt

# Atualiza pip e instala um TORCH CPU-only primeiro (evita que pip escolha dependências CUDA gigantes)
# usamos o index oficial de wheels CPU da PyTorch
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch || true

# Normaliza requirements (remove BOM, CRLF -> LF)
RUN python - <<'PY'
from pathlib import Path
p = Path('/tmp/requirements.txt')
if not p.exists():
    raise SystemExit("requirements.txt not found in /tmp")
b = p.read_bytes()
if b.startswith(b'\xef\xbb\xbf'):
    b = b[3:]
b = b.replace(b'\r\n', b'\n')
Path('/tmp/requirements.fixed').write_bytes(b)
PY

# Instala o resto das dependências usando o torch já instalado
RUN set -eux; \
    python -m pip install --no-cache-dir -r /tmp/requirements.fixed; \
    rm -rf /tmp/requirements* /root/.cache/pip; \
    # opcional: remover toolchain (mantive o purge, caso precise remover para reduzir imagem)
    apt-get purge -y --auto-remove build-essential gcc || true; \
    rm -rf /var/lib/apt/lists/*; apt-get clean || true

# Copia aplicação
COPY . /app

# Cria usuário não-root com HOME e diretórios de cache para HF/matplotlib
RUN set -eux; \
    useradd -m -d /home/appuser -s /bin/bash appuser || true; \
    mkdir -p /home/appuser/.cache/huggingface /home/appuser/.cache/torch /home/appuser/.config/matplotlib; \
    chown -R appuser:appuser /home/appuser /app; \
    chmod -R 700 /home/appuser/.cache /home/appuser/.config || true

ENV HOME=/home/appuser \
    HF_HOME=/home/appuser/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers \
    TORCH_HOME=/home/appuser/.cache/torch \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app_01.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
