#!/bin/bash
# Script para iniciar Qdrant no Docker (Linux/Mac)

set -e

echo "====================================="
echo "   Iniciando Qdrant no Docker"
echo "====================================="
echo ""

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "[ERRO] Docker não está instalado!"
    echo ""
    echo "Instale o Docker:"
    echo "https://docs.docker.com/engine/install/"
    echo ""
    exit 1
fi

echo "[OK] Docker encontrado"
echo ""

# Verificar se container já existe
if docker ps -a | grep -q qdrant-rag; then
    echo "Container 'qdrant-rag' já existe."
    echo ""

    # Verificar se está rodando
    if docker ps | grep -q qdrant-rag; then
        echo "[INFO] Qdrant já está rodando!"
        echo ""
    else
        echo "[INFO] Iniciando container existente..."
        docker start qdrant-rag
        echo "[OK] Qdrant iniciado com sucesso!"
        echo ""
    fi
else
    echo "[INFO] Criando novo container Qdrant..."
    echo ""

    # Criar diretório de storage se não existir
    if [ ! -d "rag/qdrant_storage" ]; then
        echo "[INFO] Criando diretório rag/qdrant_storage..."
        mkdir -p rag/qdrant_storage
    fi

    # Rodar container
    docker run -d \
      --name qdrant-rag \
      -p 6333:6333 \
      -p 6334:6334 \
      -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" \
      --restart unless-stopped \
      qdrant/qdrant:latest

    echo "[OK] Qdrant criado e iniciado com sucesso!"
    echo ""
fi

# Aguardar Qdrant iniciar (max 30 segundos)
echo "[INFO] Aguardando Qdrant inicializar..."
contador=0
while [ $contador -lt 30 ]; do
    if curl -s http://localhost:6333/ > /dev/null 2>&1; then
        echo "[OK] Qdrant está pronto!"
        echo ""
        break
    fi
    sleep 1
    contador=$((contador + 1))
done

if [ $contador -eq 30 ]; then
    echo "[AVISO] Timeout aguardando Qdrant. Verifique os logs."
    echo ""
fi

echo "====================================="
echo "   Qdrant Rodando!"
echo "====================================="
echo ""
echo "  Dashboard:  http://localhost:6333/dashboard"
echo "  API:        http://localhost:6333"
echo ""
echo "Comandos úteis:"
echo "  Ver logs:       docker logs -f qdrant-rag"
echo "  Parar:          docker stop qdrant-rag"
echo "  Reiniciar:      docker restart qdrant-rag"
echo "  Remover:        docker rm -f qdrant-rag"
echo ""
echo "Para iniciar a aplicação:"
echo "  streamlit run app_01.py"
echo ""
echo "====================================="
echo ""

# Perguntar se deseja abrir o dashboard
read -p "Abrir dashboard no navegador? (s/N): " ABRIR
if [ "$ABRIR" = "s" ] || [ "$ABRIR" = "S" ]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:6333/dashboard
    elif command -v open &> /dev/null; then
        open http://localhost:6333/dashboard
    else
        echo "Abra manualmente: http://localhost:6333/dashboard"
    fi
fi
