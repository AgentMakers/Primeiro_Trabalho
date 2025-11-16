FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_ENABLECORS=false \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl libfreetype6-dev libpng-dev libgl1 dos2unix ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    dos2unix /tmp/requirements.txt || true && \
    sed -i '1s/^\xEF\xBB\xBF//' /tmp/requirements.txt && \
    pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /app

EXPOSE 8501

CMD ["sh","-lc","test -f \"$STREAMLIT_ENTRY\" || { echo \"[ERRO] $STREAMLIT_ENTRY não encontrado em /app\"; ls -la /app; ls -la /app/app || true; exit 1; }; exec streamlit run \"$STREAMLIT_ENTRY\" --server.port ${STREAMLIT_SERVER_PORT:-8501} --server.address 0.0.0.0 --server.headless true"]
