# Como Acessar o Painel do Qdrant

Este guia explica como visualizar e consultar os dados do Qdrant.

## Opções Disponíveis

### Opção 1: Dashboard Web (Qdrant Server) - Recomendado

O Qdrant tem um dashboard web interativo, mas ele **só funciona quando você roda o Qdrant Server**.

Atualmente você está usando **Qdrant em modo arquivo** (`./rag/qdrant_storage/`), que não tem interface web.

#### Como habilitar o Dashboard Web

**Usando Docker (mais fácil):**

```bash
# Rodar Qdrant Server com seus dados
docker run -p 6333:6333 -p 6334:6334 \
    -v "c:/Python Projects/pos-ufg/Primeiro_Trabalho/rag/qdrant_storage:/qdrant/storage" \
    qdrant/qdrant
```

**Sem Docker:**

1. Baixar Qdrant: https://github.com/qdrant/qdrant/releases
2. Executar:
   ```bash
   ./qdrant --storage-path="./rag/qdrant_storage"
   ```

**Acessar o Dashboard:**

Abra no navegador: **http://localhost:6333/dashboard**

#### Recursos do Dashboard Web

- 📊 Visualização de coleções
- 🔍 Busca vetorial interativa
- 📈 Estatísticas em tempo real
- 🗺️ Visualização de clusters (se habilitado)
- ⚙️ Configurações da coleção

---

### Opção 2: Script Python (Modo Arquivo) - Mais Simples

Criei um script para visualizar os dados diretamente do arquivo, **sem precisar rodar servidor**.

#### Como Usar

```bash
# Executar o visualizador
python rag/utils/visualizar_qdrant.py
```

#### O Que o Script Faz

1. **Mostra informações básicas**:
   - Número de documentos
   - Coleções disponíveis
   - Configuração dos vetores

2. **Lista primeiros 10 documentos**:
   - ID
   - Fonte (arquivo)
   - Categoria
   - Preview do texto
   - Índice do chunk

3. **Estatísticas iniciais**:
   - Documentos por fonte
   - Documentos por categoria

4. **Menu interativo** com opções:

#### Opção 1: Buscar por Texto

Busca semântica usando embeddings (igual ao RAG):

```
🔍 Digite o texto para buscar: problema de internet

📄 5 resultados encontrados:

1. Score: 87.3%
   📁 Fonte: guia_resolucao_problemas.txt
   🏷️  Categoria: suporte_tecnico
   📝 Texto: Para resolver problemas de conexão...

2. Score: 72.1%
   ...
```

#### Opção 2: Estatísticas Completas

Mostra estatísticas detalhadas de **todos** os documentos:

```
📊 ESTATÍSTICAS COMPLETAS

✅ 1247 documentos carregados

📁 Documentos por fonte:
   guia_resolucao_problemas.txt: 312 (25.0%)
   procedimentos_seguranca.txt: 311 (24.9%)
   politicas_atendimento.txt: 312 (25.0%)
   gestao_conflitos.txt: 312 (25.0%)

🏷️  Documentos por categoria:
   suporte_tecnico: 623 (49.9%)
   relacionamento: 624 (50.1%)

📏 Tamanho dos textos:
   Média: 450 caracteres
   Mínimo: 120 caracteres
   Máximo: 2100 caracteres
```

#### Opção 3: Exportar para JSON

Exporta todos os dados para um arquivo JSON:

```
📁 Nome do arquivo de saída: meus_dados.json

✅ 1247 documentos exportados para: meus_dados.json
📊 Tamanho do arquivo: 2.3 MB
```

**Formato do JSON:**

```json
[
  {
    "id": 0,
    "payload": {
      "text": "Para resolver problemas de conexão...",
      "source": "guia_resolucao_problemas.txt",
      "category": "suporte_tecnico",
      "chunk_index": 0
    }
  },
  ...
]
```

---

### Opção 3: Script Python Personalizado

Você pode criar scripts customizados para consultas específicas:

```python
from qdrant_client import QdrantClient

# Conectar
client = QdrantClient(path="./rag/qdrant_storage")

# Contar documentos
collection = client.get_collection("knowledge_base")
print(f"Total: {collection.points_count} documentos")

# Buscar documentos de uma fonte específica
from qdrant_client.models import Filter, FieldCondition, MatchValue

results = client.scroll(
    collection_name="knowledge_base",
    scroll_filter=Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value="guia_resolucao_problemas.txt")
            )
        ]
    ),
    limit=100
)

print(f"Encontrados: {len(results[0])} chunks deste arquivo")
```

---

## Comparação das Opções

| Recurso | Dashboard Web | Script Python | Script Customizado |
|---------|---------------|---------------|-------------------|
| **Facilidade** | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| **Visual** | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Busca Semântica** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Estatísticas** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Exportar Dados** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Filtros Avançados** | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| **Requer Servidor** | ✅ Sim | ❌ Não | ❌ Não |
| **Requer Docker** | ⭐ Opcional | ❌ Não | ❌ Não |

---

## Exemplos de Uso

### Exemplo 1: Ver todos os documentos de suporte técnico

**Usando o script:**

```bash
python rag/utils/visualizar_qdrant.py
# Opção 2 (Estatísticas)
```

**Usando Python:**

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

client = QdrantClient(path="./rag/qdrant_storage")

results, _ = client.scroll(
    collection_name="knowledge_base",
    scroll_filter=Filter(
        must=[FieldCondition(key="category", match=MatchValue(value="suporte_tecnico"))]
    ),
    limit=1000
)

print(f"Documentos de suporte técnico: {len(results)}")
```

### Exemplo 2: Buscar documentos sobre "segurança"

**Usando o script:**

```bash
python rag/utils/visualizar_qdrant.py
# Opção 1 (Buscar por texto)
# Digite: segurança de dados
```

**Usando Python:**

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client = QdrantClient(path="./rag/qdrant_storage")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

query_vector = model.encode("segurança de dados").tolist()

results = client.search(
    collection_name="knowledge_base",
    query_vector=query_vector,
    limit=5
)

for result in results:
    print(f"Score: {result.score:.2%}")
    print(f"Texto: {result.payload['text'][:100]}...")
    print()
```

### Exemplo 3: Exportar documentos de um arquivo específico

**Usando o script:**

```bash
python rag/utils/visualizar_qdrant.py
# Opção 3 (Exportar JSON)
# Nome: politicas.json
```

Depois filtrar manualmente o JSON, ou usar Python:

```python
from qdrant_client import QdrantClient
import json

client = QdrantClient(path="./rag/qdrant_storage")

# Buscar apenas um arquivo
results, _ = client.scroll(
    collection_name="knowledge_base",
    scroll_filter=Filter(
        must=[FieldCondition(key="source", match=MatchValue(value="politicas_atendimento.txt"))]
    ),
    limit=1000
)

# Exportar
data = [{"id": p.id, "payload": p.payload} for p in results]

with open("politicas_export.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Exportado: {len(data)} chunks")
```

---

## Troubleshooting

### Problema: "No module named 'qdrant_client'"

**Solução:**
```bash
pip install qdrant-client sentence-transformers
```

### Problema: "Collection not found"

**Causa**: A base de conhecimento ainda não foi indexada.

**Solução:**
```bash
# Recarregar documentos
python -c "from rag import create_rag_instance; rag = create_rag_instance('./rag/base_conhecimento')"
```

### Problema: Docker não funciona no Windows

**Solução 1**: Usar Docker Desktop para Windows

**Solução 2**: Usar o script Python (não precisa de servidor)

```bash
python rag/utils/visualizar_qdrant.py
```

### Problema: Script muito lento

**Causa**: Muitos documentos na base.

**Solução**: Usar limite menor:

```python
# Modificar o script para usar limit menor
points, _ = client.scroll(collection_name="knowledge_base", limit=50)
```

---

## Resumo

### Para Visualização Rápida (Recomendado)

```bash
python rag/utils/visualizar_qdrant.py
```

### Para Dashboard Visual Completo

```bash
# Com Docker
docker run -p 6333:6333 -p 6334:6334 \
    -v "c:/Python Projects/pos-ufg/Primeiro_Trabalho/rag/qdrant_storage:/qdrant/storage" \
    qdrant/qdrant

# Abrir: http://localhost:6333/dashboard
```

### Para Análises Customizadas

```python
from qdrant_client import QdrantClient
client = QdrantClient(path="./rag/qdrant_storage")
# Suas consultas aqui...
```

---

## Próximos Passos

1. **Testar o visualizador**: `python rag/utils/visualizar_qdrant.py`
2. **Explorar os dados**: Usar opções de busca e estatísticas
3. **Exportar para análise**: Salvar JSON para análise offline
4. **Considerar servidor**: Se precisar de dashboard web, usar Docker

---

**Arquivos relacionados**:
- Script visualizador: [rag/utils/visualizar_qdrant.py](../utils/visualizar_qdrant.py)
- Configuração RAG: [rag/rag_config.py](../rag_config.py)
- Módulo RAG: [rag/rag_module.py](../rag_module.py)

**Última atualização**: 2025-10-24
