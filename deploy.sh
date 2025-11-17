#!/bin/bash
# deploy.sh - Script para deploy no EasyPanel

set -e

echo "🚀 Iniciando deploy do RAG Assistant..."

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📋 Copie .env.example para .env e configure suas variáveis:"
    echo "   cp .env.example .env"
    echo "   # Edite .env com suas configurações"
    exit 1
fi

# Verificar se OPENAI_API_KEY está configurada
source .env
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY não está configurada no arquivo .env"
    exit 1
fi

echo "✅ Configurações validadas"

# Build e deploy com docker-compose
echo "🔧 Fazendo build das imagens..."
docker-compose build --no-cache

echo "🐳 Iniciando serviços..."
docker-compose down --remove-orphans
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar health dos serviços
echo "🏥 Verificando saúde dos serviços..."

# Verificar Qdrant
for i in {1..12}; do
    if curl -s -f http://localhost:6333/ > /dev/null 2>&1; then
        echo "✅ Qdrant está funcionando"
        break
    fi
    echo "⏳ Aguardando Qdrant... (tentativa $i/12)"
    sleep 5
done

# Verificar Streamlit
for i in {1..12}; do
    if curl -s -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo "✅ Streamlit está funcionando"
        break
    fi
    echo "⏳ Aguardando Streamlit... (tentativa $i/12)"
    sleep 5
done

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo ""
echo "📱 Aplicação disponível em:"
echo "   Local: http://localhost:8501"
echo "   Qdrant Admin: http://localhost:6333/dashboard"
echo ""
echo "📊 Para ver logs:"
echo "   docker-compose logs -f app"
echo "   docker-compose logs -f qdrant"
echo ""
echo "🛑 Para parar:"
echo "   docker-compose down"