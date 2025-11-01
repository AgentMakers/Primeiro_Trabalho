# Sistema RAG - VOXMAP

Sistema modular de **RAG (Retrieval Augmented Generation)** para melhorar respostas do assistente com informações da base de conhecimento da empresa.

## 📁 Estrutura da Pasta

```
rag/
├── __init__.py                 # Torna a pasta um pacote Python
├── rag_module.py              # Motor principal do RAG
├── rag_config.py              # Configurações e casos de uso
├── README.md                  # Este arquivo
│
├── base_conhecimento/         # Seus documentos (TXT/PDF)
│   ├── suporte_tecnico/
│   │   ├── guia_resolucao_problemas.txt
│   │   └── procedimentos_seguranca.txt
│   └── relacionamento/
│       ├── politicas_atendimento.txt
│       └── gestao_conflitos.txt
│
├── qdrant_storage/            # Banco vetorial (criado automaticamente)
│   └── (arquivos do Qdrant)
│
├── docs/                      # Documentação completa
│   ├── RAG_README.md         # Documentação técnica
│   ├── QUICK_START.md        # Início rápido
│   ├── RESUMO_IMPLEMENTACAO.md
│   ├── ESTRUTURA_PROJETO.md
│   └── TESTES_RAG.md
│
└── utils/                     # Ferramentas auxiliares
    ├── generate_pdfs.py      # Converte TXT → PDF
    └── check_rag_setup.py    # Verifica instalação
```

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
# Na raiz do projeto
pip install qdrant-client sentence-transformers PyPDF2
```

### 2. Verificar Instalação
```bash
# Na raiz do projeto
python rag/utils/check_rag_setup.py
```

### 3. Usar no App
```python
# O app_01.py já está configurado!
# Basta rodar:
streamlit run app_01.py
```

## 📖 Documentação

- **[Início Rápido](docs/QUICK_START.md)** - Setup em 5 minutos
- **[Documentação Técnica](docs/RAG_README.md)** - Guia completo
- **[Resumo](docs/RESUMO_IMPLEMENTACAO.md)** - Visão executiva
- **[Testes](docs/TESTES_RAG.md)** - Como testar o sistema
- **[Estrutura](docs/ESTRUTURA_PROJETO.md)** - Organização do projeto

## 🔧 Uso

### Importar Módulos

```python
# Forma recomendada
from rag import create_rag_instance, RAG_CONFIG

# Ou específico
from rag.rag_module import QdrantRAG
from rag.rag_config import get_active_use_cases
```

### Criar Instância RAG

```python
rag = create_rag_instance(
    knowledge_base_dir="./rag/base_conhecimento",
    verbose=True
)
```

### Buscar Documentos

```python
docs = rag.retrieve(
    query="Como resolver problema de internet?",
    top_k=5,
    score_threshold=0.5
)

for doc in docs:
    print(f"{doc['source']}: {doc['score']:.2%}")
    print(doc['text'][:200])
```

## 📚 Adicionar Documentos

1. Coloque arquivos `.txt` ou `.pdf` em `base_conhecimento/sua_categoria/`
2. No app, clique em "🔄 Recarregar"
3. Pronto! Documentos indexados

## ⚙️ Configuração

Edite `rag_config.py` para personalizar:

- **Casos de uso** (suporte, vendas, etc.)
- **Parâmetros de busca** (top_k, threshold)
- **Modelo de embeddings**
- **Tamanho dos chunks**

## 🛠️ Ferramentas

### Gerar PDFs
```bash
python rag/utils/generate_pdfs.py
```

### Verificar Setup
```bash
python rag/utils/check_rag_setup.py
```

## 🎯 Casos de Uso Incluídos

### 1. Suporte Técnico TI
- Resolução de problemas
- Procedimentos de segurança
- ~450 chunks indexados

### 2. Relacionamento com Cliente
- Políticas de atendimento
- Gestão de conflitos
- ~750 chunks indexados

## 📊 Performance

- **Primeira carga:** 1-2 minutos (download modelo)
- **Cargas seguintes:** Instantâneo
- **Busca:** 50-200ms
- **Modelo:** ~400MB RAM
- **Storage:** ~1MB por 1000 chunks

## 🔗 Integração com App

O `app_01.py` já importa automaticamente:

```python
# Em app_01.py
from rag.rag_module import create_rag_instance
from rag.rag_config import RAG_CONFIG, format_rag_context

# RAG funciona automaticamente quando habilitado
```

## 🆘 Troubleshooting

### RAG não aparece
```bash
# Verificar dependências
pip list | grep qdrant
pip list | grep sentence-transformers
```

### Documentos não são encontrados
- Verificar se `rag_enabled = True` na sidebar
- Diminuir threshold (0.3)
- Aumentar top_k (5)

### Imports não funcionam
```bash
# Verificar se __init__.py existe
ls rag/__init__.py

# Tentar import
python -c "from rag import create_rag_instance"
```

## 📝 Logs e Debug

Ativar logs detalhados:

```python
rag = create_rag_instance(
    knowledge_base_dir="./rag/base_conhecimento",
    verbose=True  # ← Ativa logs
)
```

## 🔄 Atualizar Base

Quando adicionar/modificar documentos:

1. **Via Interface:** Clique "🔄 Recarregar" na sidebar
2. **Via Código:**
   ```python
   rag.clear()
   rag.load_documents("./rag/base_conhecimento")
   ```

## 📈 Próximos Passos

1. ✅ Adicionar seus próprios documentos
2. ✅ Criar novos casos de uso
3. ✅ Ajustar parâmetros conforme necessidade
4. ✅ Monitorar métricas de satisfação

## 🤝 Suporte

- **Documentação:** Veja `docs/`
- **Problemas:** Consulte `docs/TESTES_RAG.md`
- **Código:** Comentários em `rag_module.py`

## 📄 Licença

Parte do projeto VOXMAP
© 2025 Marcus Loreto

---

**Versão:** 1.0.0
**Última atualização:** Janeiro 2025
