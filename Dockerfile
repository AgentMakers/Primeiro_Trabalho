# Dockerfile final otimizado para EasyPanel (Python 3.12)
FROM python:3.12-slim

# --------- Variáveis de ambiente ----------
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
    # Definimos HOME antes de trocar de usuário
    HOME=/home/appuser \
    # Diretórios de cache (garantem que HF/transformers/matplotlib escrevam em local gravável)
    HF_HOME=/home/appuser/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers \
    TORCH_HOME=/home/appuser/.cache/torch \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib

WORKDIR /app

# --------- Instala dependências do sistema (inclui curl para healthcheck) ----------
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

# Normaliza requirements (remove BOM, converte CRLF -> LF) com script Python em bloco separado
RUN python -m pip install --upgrade pip setuptools wheel && \
    python - <<'PY'
from pathlib import Path
p = Path('/tmp/requirements.txt')
if not p.exists():
    raise SystemExit("requirements.txt not found in /tmp")
b = p.read_bytes()
# remove BOM se existir
if b.startswith(b'\xef\xbb\xbf'):
    b = b[3:]
# normaliza CRLF -> LF
b = b.replace(b'\r\n', b'\n')
Path('/tmp/requirements.fixed').write_bytes(b)
PY

# Instala dependências Python (rodando como root), depois limpa caches e remove pacotes de build
RUN set -eux; \
    python -m pip install --no-cache-dir -r /tmp/requirements.fixed; \
    rm -rf /tmp/requirements* /root/.cache/pip; \
    # remover toolchain de build que não é necessário em runtime
    apt-get purge -y --auto-remove build-essential gcc || true; \
    rm -rf /var/lib/apt/lists/*; \
    apt-get clean || true

# Copia a aplicação
COPY . /app

# Cria usuário não-root COM diretório HOME e diretórios de cache necessários, ajusta permissões
RUN set -eux; \
    # cria usuário com home
    useradd -m -d /home/appuser -s /bin/bash appuser || true; \
    # cria diretórios de cache e config para bibliotecas que precisam gravar
    mkdir -p /home/appuser/.cache/huggingface /home/appuser/.cache/torch /home/appuser/.config/matplotlib; \
    chown -R appuser:appuser /home/appuser /app; \
    chmod -R 700 /home/appuser/.cache /home/appuser/.config || true

# Definir variáveis de ambiente novamente para o shell do container (garante HOME ativo antes do USER)
ENV HOME=/home/appuser \
    HF_HOME=/home/appuser/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface/transformers \
    TORCH_HOME=/home/appuser/.cache/torch \
    MPLCONFIGDIR=/home/appuser/.config/matplotlib

USER appuser

# Porta usada pelo Streamlit
EXPOSE 8501

# HEALTHCHECK (mantém curl instalado antes do purge)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicialização (substitua app_01.py pelo entrypoint correto se necessário)
CMD ["streamlit", "run", "app_01.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
