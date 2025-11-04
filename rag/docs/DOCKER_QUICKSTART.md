# Quick Start: Rodando Qdrant no Docker

Guia rápido para rodar o Qdrant em Docker e acessar o dashboard.

## Opção 1: Script Automático (Mais Fácil) ⭐

### Windows

```bash
start-qdrant.bat
```

### Linux/Mac

```bash
chmod +x start-qdrant.sh
./start-qdrant.sh
```

**O script faz tudo automaticamente:**
- ✅ Verifica se Docker está instalado
- ✅ Cria container Qdrant (se não existir)
- ✅ Inicia container (se já existir)
- ✅ Aguarda Qdrant ficar pronto
- ✅ Mostra URLs e comandos úteis
- ✅ Oferece abrir dashboard no navegador

---

## Opção 2: Comando Manual (Docker Run)

### No terminal (powershell):

```bash 
docker run -d `  --name qdrant-rag `  -p 6333:6333 `  -p 6334:6334 `  -v "${PWD}/rag/qdrant_storage:/qdrant/storage" `  qdrant/qdrant:latest
```

### Linux/Mac

```bash
docker run -d --name qdrant-rag -p 6333:6333 -p 6334:6334 -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" qdrant/qdrant:latest
```

---

## Opção 3: Docker Compose (Qdrant + App)

```bash
# Subir apenas Qdrant
docker-compose up -d qdrant

# Subir tudo (Qdrant + Aplicação)
docker-compose up -d
```

---

## Acessar o Dashboard

Depois de iniciar o Qdrant, abra no navegador:

### 🌐 http://localhost:6333/dashboard

**Recursos do Dashboard:**
- 📊 Visualizar collections
- 🔍 Buscar documentos
- 📈 Estatísticas em tempo real
- ⚙️ Configurações do servidor

---

## Comandos Úteis

```bash
# Ver status
docker ps | grep qdrant

# Ver logs
docker logs -f qdrant-rag

# Parar Qdrant
docker stop qdrant-rag

# Iniciar Qdrant
docker start qdrant-rag

# Reiniciar Qdrant
docker restart qdrant-rag

# Remover container (dados são mantidos)
docker rm -f qdrant-rag
```

---

## Usar com a Aplicação

### Modo 1: Aplicação Local + Qdrant Docker (Recomendado)

```bash
# 1. Iniciar Qdrant
start-qdrant.bat  # Windows
./start-qdrant.sh  # Linux/Mac

# 2. Rodar aplicação normalmente
streamlit run app_01.py
```

A aplicação vai se conectar automaticamente ao Qdrant no Docker.

### Modo 2: Tudo no Docker

```bash
# Subir tudo
docker-compose up -d

# Acessar:
# - Qdrant: http://localhost:6333/dashboard
# - App: http://localhost:8501
```

---

## Verificar se Está Funcionando

### Teste 1: API REST

```bash
curl http://localhost:6333/
```

**Esperado:**
```json
{"title":"qdrant - vector search engine","version":"1.7.0"}
```

### Teste 2: Dashboard

Abra: http://localhost:6333/dashboard

Deve mostrar a interface do Qdrant.

### Teste 3: Collections

```bash
curl http://localhost:6333/collections
```

**Esperado:**
```json
{
  "result": {
    "collections": [
      {
        "name": "knowledge_base"
      }
    ]
  }
}
```

---

## Troubleshooting

### ❌ Porta 6333 já em uso

**Solução:** Trocar porta externa

```bash
docker run -d --name qdrant-rag -p 6335:6333 ...
```

Acessar: http://localhost:6335/dashboard

### ❌ Docker não encontrado

**Erro:** `docker: command not found`

**Solução:** Instalar Docker Desktop
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Mac: https://docs.docker.com/desktop/install/mac-install/
- Linux: https://docs.docker.com/engine/install/

### ❌ Permissão negada (Linux)

**Erro:** `permission denied while trying to connect`

**Solução:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### ❌ Container não inicia

**Ver logs:**
```bash
docker logs qdrant-rag
```

**Reiniciar:**
```bash
docker restart qdrant-rag
```

---

## Próximos Passos

1. ✅ Rodar Qdrant: `start-qdrant.bat` ou `./start-qdrant.sh`
2. 🌐 Acessar dashboard: http://localhost:6333/dashboard
3. 📊 Explorar collections e dados
4. 🚀 Rodar aplicação: `streamlit run app_01.py`
5. 🔍 Testar busca RAG na aplicação

---

## Documentação Completa

- **Guia completo Docker**: [rag/docs/DOCKER_QDRANT.md](rag/docs/DOCKER_QDRANT.md)
- **Visualizar dados**: [rag/docs/ACESSAR_PAINEL_QDRANT.md](rag/docs/ACESSAR_PAINEL_QDRANT.md)
- **Como funciona RAG**: [rag/docs/COMO_FUNCIONA_RAG.md](rag/docs/COMO_FUNCIONA_RAG.md)

---

**Última atualização**: 2025-10-24
