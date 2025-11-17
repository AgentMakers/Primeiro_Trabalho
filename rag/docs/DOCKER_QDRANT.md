# Rodando Qdrant com Docker

Este guia explica como rodar o Qdrant usando Docker, com acesso ao dashboard web.

## Opções Disponíveis

### Opção 1: Apenas Qdrant (Mais Simples) ⭐ RECOMENDADO

Rodar apenas o Qdrant em Docker, mantendo a aplicação Streamlit local.

### Opção 2: Qdrant + Aplicação (Docker Compose Completo)

Rodar tanto o Qdrant quanto a aplicação Streamlit em containers.

---

## Opção 1: Apenas Qdrant (Recomendado)

### Passo 1: Verificar Docker Instalado

```bash
docker --version
```

Se não tiver Docker instalado:
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Linux: https://docs.docker.com/engine/install/
- Mac: https://docs.docker.com/desktop/install/mac-install/

### Passo 2: Rodar Qdrant

**Comando único:**

### No terminal:
```bash 
docker run -d --name qdrant-rag -p 6333:6333 -p 6334:6334 -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" qdrant/qdrant:latest
```

## outra forma:
**comando no terminal - substitua o endereço absoluto "C:\Python Projects\pos-ufg\" pelo o da sua máquina**
```bash 
docker run -d --name qdrant-rag -p 6333:6333 -p 6334:6334 -v "C:\Python Projects\pos-ufg\Primeiro_Trabalho\rag\qdrant_storage:/qdrant/storage" qdrant/qdrant:latest
```

**No Windows PowerShell:**

```powershell
docker run -d `
  --name qdrant-rag `
  -p 6333:6333 `
  -p 6334:6334 `
  -v "${PWD}/rag/qdrant_storage:/qdrant/storage" `
  qdrant/qdrant:latest
```

**No Linux/Mac:**

```bash
docker run -d \
  --name qdrant-rag \
  -p 6333:6333 \
  -p 6334:6334 \
  -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" \
  qdrant/qdrant:latest
```

### Passo 3: Verificar se Está Rodando

```bash
# Ver logs
docker logs qdrant-rag

# Ver status
docker ps | grep qdrant
```

**Saída esperada:**
```
CONTAINER ID   IMAGE                  STATUS         PORTS
abc123def456   qdrant/qdrant:latest   Up 10 seconds  0.0.0.0:6333->6333/tcp, 0.0.0.0:6334->6334/tcp
```

### Passo 4: Acessar o Dashboard

Abra no navegador: **http://localhost:6333/dashboard**

Você verá:
- 📊 Collections (suas coleções)
- 🔍 Console (executar queries)
- ⚙️ Cluster (informações do servidor)

### Passo 5: Rodar a Aplicação Localmente

```bash
# Em outro terminal
streamlit run app_01.py
```

A aplicação vai se conectar automaticamente ao Qdrant rodando no Docker.

### Comandos Úteis

```bash
# Parar Qdrant
docker stop qdrant-rag

# Iniciar Qdrant
docker start qdrant-rag

# Reiniciar Qdrant
docker restart qdrant-rag

# Ver logs em tempo real
docker logs -f qdrant-rag

# Remover container (mantém dados)
docker rm qdrant-rag

# Remover tudo (CUIDADO: apaga dados!)
docker rm -f qdrant-rag
rm -rf rag/qdrant_storage
```

---

## Opção 2: Qdrant + Aplicação (Docker Compose)

### Passo 1: Verificar Arquivos

Certifique-se de que existe:
- `docker-compose.yml` (já atualizado)
- `.env` com sua `OPENAI_API_KEY`

### Passo 2: Subir os Serviços

```bash
# Subir tudo em background
docker-compose up -d

# Subir e ver logs
docker-compose up
```

**O que vai acontecer:**
1. Baixa imagens do Docker (primeira vez)
2. Sobe container Qdrant
3. Espera Qdrant ficar saudável (healthcheck)
4. Sobe container Streamlit
5. Instala dependências
6. Inicia aplicação

### Passo 3: Verificar Serviços

```bash
# Ver status
docker-compose ps

# Ver logs
docker-compose logs -f

# Ver logs apenas do Qdrant
docker-compose logs -f qdrant

# Ver logs apenas do app
docker-compose logs -f app
```

### Passo 4: Acessar os Serviços

- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Streamlit App**: http://localhost:8501

### Comandos Docker Compose

```bash
# Parar tudo
docker-compose down

# Parar e remover volumes (CUIDADO: apaga dados!)
docker-compose down -v

# Reiniciar apenas um serviço
docker-compose restart qdrant
docker-compose restart app

# Ver logs de um serviço
docker-compose logs -f qdrant

# Reconstruir imagens
docker-compose up --build

# Executar comando dentro do container
docker-compose exec app bash
docker-compose exec qdrant sh
```

---

## Configuração do Qdrant

### Estrutura do Docker Compose

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant-rag
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API
    volumes:
      - ./rag/qdrant_storage:/qdrant/storage:rw
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Portas

- **6333**: REST API (usado pela aplicação)
- **6334**: gRPC API (opcional, melhor performance)

### Volumes

- `./rag/qdrant_storage`: Dados persistentes
- Se apagar este diretório, perde todos os embeddings

### Variáveis de Ambiente

```yaml
environment:
  - QDRANT__SERVICE__HTTP_PORT=6333
  - QDRANT__SERVICE__GRPC_PORT=6334
  # Opcionais:
  - QDRANT__LOG_LEVEL=INFO
  - QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS=4
```

---

## Conectar a Aplicação ao Qdrant Docker

### Modo Arquivo (Local) vs Servidor (Docker)

**Antes (modo arquivo):**

```python
from qdrant_client import QdrantClient

client = QdrantClient(path="./rag/qdrant_storage")  # Arquivo local
```

**Depois (servidor Docker):**

```python
from qdrant_client import QdrantClient

client = QdrantClient(
    host="localhost",  # ou "qdrant" se rodar app no Docker também
    port=6333
)
```

### Atualizar rag_module.py (se necessário)

Se quiser usar o Qdrant em Docker, modifique [rag/rag_module.py:97-104](rag/rag_module.py#L97-L104):

```python
# Detectar se deve usar servidor ou arquivo
import os

if os.getenv("QDRANT_HOST"):
    # Usando Docker/servidor
    self.qdrant_client = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )
else:
    # Usando arquivo local (padrão)
    self.qdrant_client = QdrantClient(path=persist_path)
```

Ou simplesmente definir no `.env`:

```bash
# Usar Qdrant local (arquivo)
# QDRANT_HOST=

# Usar Qdrant Docker
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

---

## Dashboard do Qdrant

### Acessar Dashboard

http://localhost:6333/dashboard

### Recursos do Dashboard

#### 1. Collections

- Ver todas as coleções
- Número de pontos (documentos)
- Configuração de vetores
- Status da coleção

**Exemplo:**
```
knowledge_base
├─ Points: 1247
├─ Vector size: 384
├─ Distance: Cosine
└─ Status: Green
```

#### 2. Console (Queries)

Execute queries diretamente:

**Buscar pontos:**
```json
{
  "vector": [0.1, 0.2, ...],  // 384 dimensões
  "limit": 5,
  "with_payload": true
}
```

**Filtrar por categoria:**
```json
{
  "vector": [...],
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

#### 3. Cluster

- Informações do servidor
- Uso de memória
- Configurações ativas

---

## Troubleshooting

### Problema: Porta 6333 já em uso

**Erro:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:6333: bind: address already in use
```

**Solução 1 - Trocar porta:**
```yaml
ports:
  - "6335:6333"  # Usar 6335 externa
```

Acesse: http://localhost:6335/dashboard

**Solução 2 - Parar processo:**
```bash
# Windows
netstat -ano | findstr :6333
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:6333 | xargs kill -9
```

### Problema: Container não inicia

**Ver logs:**
```bash
docker logs qdrant-rag
```

**Verificar permissões (Linux):**
```bash
sudo chown -R $USER:$USER rag/qdrant_storage
```

### Problema: Dashboard não carrega

**Verificar se está rodando:**
```bash
curl http://localhost:6333/
```

**Esperado:**
```json
{"title":"qdrant - vector search engine","version":"1.7.0"}
```

**Se não responder:**
```bash
docker restart qdrant-rag
```

### Problema: Aplicação não conecta ao Qdrant

**Erro:**
```
ConnectionError: [Errno 111] Connection refused
```

**Solução:**
1. Verificar se Qdrant está rodando: `docker ps`
2. Verificar se está escutando: `curl http://localhost:6333/`
3. Verificar firewall (Windows):
   ```bash
   # Permitir porta 6333
   netsh advfirewall firewall add rule name="Qdrant" dir=in action=allow protocol=TCP localport=6333
   ```

### Problema: Dados não persistem

**Causa:** Volume não montado corretamente

**Solução:**
```bash
# Verificar volumes
docker inspect qdrant-rag | grep Mounts -A 10

# Deve mostrar:
# "Source": "/caminho/completo/rag/qdrant_storage"
# "Destination": "/qdrant/storage"
```

Se não estiver montado:
```bash
docker rm -f qdrant-rag
docker run -d --name qdrant-rag \
  -p 6333:6333 \
  -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" \
  qdrant/qdrant:latest
```

---

## Performance e Otimização

### Recursos Docker

Qdrant pode usar bastante RAM com grandes bases de conhecimento.

**Limitar memória:**
```yaml
services:
  qdrant:
    ...
    deploy:
      resources:
        limits:
          memory: 2G  # Máximo 2GB
        reservations:
          memory: 512M  # Mínimo 512MB
```

### Configurações de Performance

```yaml
environment:
  # Threads para busca
  - QDRANT__STORAGE__PERFORMANCE__MAX_SEARCH_THREADS=4

  # Otimizadores
  - QDRANT__STORAGE__OPTIMIZERS__DEFAULT_SEGMENT_NUMBER=2

  # Cache
  - QDRANT__STORAGE__PERFORMANCE__MAX_SEGMENT_SIZE_KB=200000
```

### Monitoramento

```bash
# Ver uso de recursos
docker stats qdrant-rag

# Resultado:
# CONTAINER     CPU %     MEM USAGE / LIMIT     MEM %
# qdrant-rag    5.23%     345.2MiB / 2GiB      16.88%
```

---

## Backup e Restore

### Backup Manual

```bash
# Parar Qdrant
docker stop qdrant-rag

# Copiar dados
cp -r rag/qdrant_storage rag/qdrant_storage_backup_$(date +%Y%m%d)

# Ou comprimir
tar -czf qdrant_backup_$(date +%Y%m%d).tar.gz rag/qdrant_storage

# Reiniciar Qdrant
docker start qdrant-rag
```

### Restore

```bash
# Parar Qdrant
docker stop qdrant-rag

# Restaurar backup
rm -rf rag/qdrant_storage
cp -r rag/qdrant_storage_backup_20251024 rag/qdrant_storage

# Ou descomprimir
tar -xzf qdrant_backup_20251024.tar.gz

# Reiniciar Qdrant
docker start qdrant-rag
```

### Backup via API

```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# Criar snapshot
snapshot = client.create_snapshot(collection_name="knowledge_base")
print(f"Snapshot criado: {snapshot.name}")

# Listar snapshots
snapshots = client.list_snapshots(collection_name="knowledge_base")
for s in snapshots:
    print(f"- {s.name}")

# Baixar snapshot
# Acessar: http://localhost:6333/collections/knowledge_base/snapshots/{snapshot_name}
```

---

## Migração de Arquivo para Docker

Se você já tem dados em modo arquivo, pode migrar para Docker:

### Opção 1: Usar mesmo diretório (Simples)

O Docker já está configurado para usar `./rag/qdrant_storage`, então **não precisa fazer nada**!

### Opção 2: Migrar manualmente

```bash
# 1. Exportar dados do arquivo
python rag/utils/visualizar_qdrant.py
# Escolher opção 3: Exportar JSON

# 2. Subir Qdrant Docker
docker-compose up -d qdrant

# 3. Reindexar documentos
python -c "
from rag import create_rag_instance
rag = create_rag_instance('./rag/base_conhecimento')
print('Reindexado!')
"
```

---

## Resumo dos Comandos

### Iniciar Qdrant (Docker simples)

```bash
docker run -d --name qdrant-rag \
  -p 6333:6333 -p 6334:6334 \
  -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" \
  qdrant/qdrant:latest
```

### Iniciar Qdrant (Docker Compose)

```bash
docker-compose up -d qdrant
```

### Acessar Dashboard

http://localhost:6333/dashboard

### Parar/Reiniciar

```bash
docker stop qdrant-rag
docker start qdrant-rag
docker restart qdrant-rag
```

### Ver Logs

```bash
docker logs -f qdrant-rag
```

---

## Próximos Passos

1. ✅ Rodar Qdrant no Docker
2. 🌐 Acessar dashboard: http://localhost:6333/dashboard
3. 🔍 Explorar collections e dados
4. 🚀 Rodar aplicação: `streamlit run app_01.py`
5. 💾 Configurar backups automáticos

---

**Documentação relacionada:**
- [Visualizar Qdrant](ACESSAR_PAINEL_QDRANT.md)
- [Como Funciona RAG](COMO_FUNCIONA_RAG.md)
- [Instalação RAG](../../INSTALACAO_RAG.md)

**Última atualização**: 2025-10-24
