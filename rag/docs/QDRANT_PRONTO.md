# ✅ Qdrant Está Rodando no Docker!

## Status Atual

O Qdrant foi iniciado com sucesso no Docker:

```
Container ID: 14d51e32bdeb
Image: qdrant/qdrant:latest
Status: Up and running
Ports: 6333 (REST API), 6334 (gRPC)
Version: 1.15.5
```

---

## 🌐 Acessar o Dashboard

### Dashboard Web do Qdrant

**URL:** http://localhost:6333/dashboard

Clique para abrir: [Qdrant Dashboard](http://localhost:6333/dashboard)

### O Que Você Pode Fazer no Dashboard

1. **📊 Collections Tab**
   - Ver a coleção `knowledge_base`
   - Total de documentos (pontos)
   - Configuração de vetores
   - Status da coleção

2. **🔍 Console Tab**
   - Executar queries diretamente
   - Buscar por similaridade
   - Filtrar documentos
   - Testar embeddings

3. **⚙️ Cluster Tab**
   - Informações do servidor
   - Uso de recursos
   - Configurações ativas

4. **📈 Metrics**
   - Performance do servidor
   - Estatísticas de queries
   - Uso de memória

---

## 🚀 Próximos Passos

### 1. Verificar Collections

Abra o dashboard e vá para **Collections**. Se a coleção `knowledge_base` já existir, você verá os documentos indexados.

Se não existir, você precisa indexar os documentos:

```bash
python -c "from rag import create_rag_instance; rag = create_rag_instance('./rag/base_conhecimento'); print('Indexado!')"
```

### 2. Testar Busca no Dashboard

1. Vá para **Console** no dashboard
2. Selecione a collection `knowledge_base`
3. Execute uma query de teste:

```json
{
  "limit": 5,
  "with_payload": true
}
```

### 3. Rodar a Aplicação

```bash
streamlit run app_01.py
```

A aplicação vai se conectar automaticamente ao Qdrant rodando no Docker.

### 4. Testar RAG na Aplicação

1. Abrir aplicação: http://localhost:8501
2. Verificar sidebar: deve mostrar "📚 Base de Conhecimento (RAG)"
3. Ativar RAG (toggle)
4. Fazer uma pergunta: "Como resolver problema de internet?"
5. Ver documentos recuperados acima da resposta

---

## 📋 Comandos Úteis

### Gerenciar Container

```bash
# Ver status
docker ps | findstr qdrant

# Ver logs
docker logs qdrant-rag

# Ver logs em tempo real
docker logs -f qdrant-rag

# Parar
docker stop qdrant-rag

# Iniciar
docker start qdrant-rag

# Reiniciar
docker restart qdrant-rag
```

### API do Qdrant

```bash
# Health check
curl http://localhost:6333/

# Listar collections
curl http://localhost:6333/collections

# Info da collection
curl http://localhost:6333/collections/knowledge_base

# Contar pontos
curl http://localhost:6333/collections/knowledge_base/points/count
```

### Backup

```bash
# Parar container
docker stop qdrant-rag

# Fazer backup
xcopy "rag\qdrant_storage" "rag\qdrant_storage_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%" /E /I /H

# Reiniciar container
docker start qdrant-rag
```

---

## 🔧 Arquivos Criados

### Scripts de Inicialização

- ✅ `start-qdrant.bat` - Script Windows para iniciar Qdrant
- ✅ `start-qdrant.sh` - Script Linux/Mac para iniciar Qdrant

**Como usar:**
```bash
# Windows
start-qdrant.bat

# Linux/Mac
chmod +x start-qdrant.sh
./start-qdrant.sh
```

### Docker Compose

- ✅ `docker-compose.yml` - Atualizado com serviço Qdrant

**Como usar:**
```bash
# Apenas Qdrant
docker-compose up -d qdrant

# Qdrant + Aplicação
docker-compose up -d
```

### Documentação

- ✅ `DOCKER_QUICKSTART.md` - Quick start
- ✅ `rag/docs/DOCKER_QDRANT.md` - Guia completo
- ✅ `rag/docs/ACESSAR_PAINEL_QDRANT.md` - Como acessar painel
- ✅ `rag/docs/VISUALIZACAO_RAG.md` - Visualização no chat
- ✅ `rag/docs/COMO_FUNCIONA_RAG.md` - Como funciona

---

## 🎯 Checklist de Configuração

- [x] Docker instalado
- [x] Qdrant rodando no Docker
- [x] Dashboard acessível (http://localhost:6333/dashboard)
- [x] API respondendo
- [ ] Documentos indexados (rodar script de indexação)
- [ ] Aplicação testada
- [ ] RAG funcionando no chat

---

## 📊 Exemplo de Uso do Dashboard

### 1. Ver Collections

No dashboard, vá para **Collections** e clique em `knowledge_base`.

Você verá:
```
Collection: knowledge_base
Points: 1247
Vectors: 384 dimensions
Distance: Cosine
Status: Green
```

### 2. Buscar Documentos

No **Console**, execute:

```json
{
  "limit": 3,
  "with_payload": true,
  "with_vector": false
}
```

Resultado:
```json
{
  "result": [
    {
      "id": 0,
      "payload": {
        "text": "Para resolver problemas de conexão...",
        "source": "guia_resolucao_problemas.txt",
        "category": "suporte_tecnico",
        "chunk_index": 0
      },
      "score": null
    },
    ...
  ]
}
```

### 3. Filtrar por Categoria

```json
{
  "limit": 5,
  "filter": {
    "must": [
      {
        "key": "category",
        "match": {
          "value": "suporte_tecnico"
        }
      }
    ]
  }
}
```

### 4. Busca por Similaridade

Para buscar por texto similar, você precisa do vetor embedding. Isso é feito automaticamente pela aplicação, mas pode testar no console do dashboard usando um vetor de exemplo.

---

## 🐛 Troubleshooting

### Dashboard não carrega

```bash
# Verificar se está rodando
docker ps | findstr qdrant

# Ver logs
docker logs qdrant-rag

# Reiniciar
docker restart qdrant-rag
```

### Porta em uso

Se a porta 6333 já estiver em uso:

```bash
# Parar container atual
docker stop qdrant-rag
docker rm qdrant-rag

# Iniciar com porta diferente
docker run -d --name qdrant-rag -p 6335:6333 -p 6336:6334 -v "c:/Python Projects/pos-ufg/Primeiro_Trabalho/rag/qdrant_storage:/qdrant/storage" qdrant/qdrant:latest

# Acessar: http://localhost:6335/dashboard
```

### Aplicação não conecta

Se a aplicação não conseguir conectar ao Qdrant:

1. Verificar se Qdrant está rodando: `docker ps`
2. Testar API: `curl http://localhost:6333/`
3. Verificar firewall do Windows
4. Reiniciar Qdrant: `docker restart qdrant-rag`

---

## 📚 Recursos Adicionais

### Documentação Oficial Qdrant

- Site: https://qdrant.tech/
- Docs: https://qdrant.tech/documentation/
- API Reference: https://qdrant.github.io/qdrant/redoc/

### Tutoriais

- Quick Start: https://qdrant.tech/documentation/quick-start/
- Collections: https://qdrant.tech/documentation/concepts/collections/
- Search: https://qdrant.tech/documentation/concepts/search/
- Filters: https://qdrant.tech/documentation/concepts/filtering/

### Ferramentas

- **Qdrant Client Python**: https://github.com/qdrant/qdrant-client
- **Dashboard**: Já incluído no container
- **Python SDK**: Já instalado (`qdrant-client`)

---

## ✨ Resumo

**Você agora tem:**

1. ✅ Qdrant rodando no Docker
2. ✅ Dashboard acessível em http://localhost:6333/dashboard
3. ✅ Scripts prontos para iniciar/parar
4. ✅ Docker Compose configurado
5. ✅ Documentação completa
6. ✅ Aplicação pronta para usar RAG

**Próximo passo:**

1. Abrir dashboard: http://localhost:6333/dashboard
2. Indexar documentos (se ainda não tiver feito)
3. Testar na aplicação: `streamlit run app_01.py`
4. Ver RAG em ação! 🚀

---

**Links Rápidos:**

- 🌐 Dashboard: http://localhost:6333/dashboard
- 📖 Docs: [rag/docs/DOCKER_QDRANT.md](rag/docs/DOCKER_QDRANT.md)
- 🚀 Quick Start: [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)

**Última atualização**: 2025-10-24
