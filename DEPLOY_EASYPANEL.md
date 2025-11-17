# Configuração para EasyPanel
# Este arquivo contém instruções específicas para deploy no EasyPanel

## 📋 Pré-requisitos

1. **Conta EasyPanel** configurada
2. **API Key OpenAI** válida
3. **Docker** habilitado no projeto

## 🚀 Deploy no EasyPanel

### 1. Configuração das Variáveis de Ambiente

No painel do EasyPanel, configure as seguintes variáveis:

```
OPENAI_API_KEY=sua-chave-openai-aqui
QDRANT_HOST=qdrant
QDRANT_PORT=6333
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### 2. Portas a Expor

- **8501** - Interface Streamlit (aplicação principal)
- **6333** - Qdrant REST API (interno)
- **6334** - Qdrant gRPC API (interno)

### 3. Volumes Necessários

- **qdrant_storage** - Persistência do banco vetorial Qdrant

### 4. Comandos de Deploy

#### Opção A: Docker Compose (Recomendado)
```bash
docker-compose up -d
```

#### Opção B: Build Manual
```bash
# Build da imagem
docker build -t rag-app .

# Executar Qdrant
docker run -d --name qdrant-rag \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Executar aplicação
docker run -d --name streamlit-rag-app \
  -p 8501:8501 \
  --link qdrant-rag:qdrant \
  -e OPENAI_API_KEY=sua-chave \
  -e QDRANT_HOST=qdrant \
  rag-app
```

### 5. Health Checks

O sistema possui health checks configurados:
- **Qdrant**: `curl -f http://localhost:6333/`
- **Streamlit**: `curl -f http://localhost:8501/_stcore/health`

### 6. Recursos Recomendados

- **CPU**: 1-2 cores
- **RAM**: 2-4GB (mínimo 1GB)
- **Storage**: 5-10GB para volumes

### 7. Monitoramento

Verifique os logs com:
```bash
docker-compose logs -f app
docker-compose logs -f qdrant
```

### 8. Domínio Customizado

Configure o domínio no EasyPanel apontando para a porta **8501**.

## 🔧 Troubleshooting

### Problema: RAG não funciona
- Verificar se Qdrant está rodando: `curl http://qdrant:6333/`
- Verificar logs: `docker logs qdrant-rag`

### Problema: OpenAI não responde
- Verificar se OPENAI_API_KEY está configurada
- Testar a chave manualmente

### Problema: Aplicação não carrega
- Verificar se todas as dependências foram instaladas
- Verificar logs: `docker logs streamlit-rag-app`

## 📚 Estrutura dos Serviços

```
┌─────────────────┐    ┌─────────────────┐
│   EasyPanel     │    │   Usuários      │
│   (Proxy)       │◄───┤   (Browser)     │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Streamlit     │
│   (Port 8501)   │
└─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│   Qdrant DB     │    │   OpenAI API    │
│   (Port 6333)   │    │   (External)    │
└─────────────────┘    └─────────────────┘
```