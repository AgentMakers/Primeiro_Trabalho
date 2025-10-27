# Nova Estrutura Organizacional - Sistema RAG

## ✅ O que Mudou

Todo o sistema RAG foi **reorganizado** em uma pasta dedicada `rag/` para melhor organização e modularidade.

## 📁 Estrutura Atual

```
Primeiro_Trabalho/
│
├── app_01.py                          # Aplicação principal
├── app_02.py                          # Versão alternativa
├── requirements.txt                   # Dependências
├── .env                               # Variáveis de ambiente
├── README.md                          # Documentação geral
│
└── rag/                               # ⭐ TUDO DO RAG AQUI
    ├── __init__.py                    # Torna pasta um pacote Python
    ├── rag_module.py                  # Motor RAG
    ├── rag_config.py                  # Configurações
    ├── README.md                      # Documentação da pasta RAG
    │
    ├── base_conhecimento/             # Documentos
    │   ├── suporte_tecnico/
    │   │   ├── guia_resolucao_problemas.txt
    │   │   └── procedimentos_seguranca.txt
    │   └── relacionamento/
    │       ├── politicas_atendimento.txt
    │       └── gestao_conflitos.txt
    │
    ├── qdrant_storage/                # Banco vetorial (gerado auto)
    │
    ├── docs/                          # Documentação completa
    │   ├── RAG_README.md
    │   ├── QUICK_START.md
    │   ├── RESUMO_IMPLEMENTACAO.md
    │   ├── ESTRUTURA_PROJETO.md
    │   └── TESTES_RAG.md
    │
    └── utils/                         # Ferramentas
        ├── generate_pdfs.py
        └── check_rag_setup.py
```

## 🔄 Mudanças nos Imports

### Antes:
```python
from rag_module import create_rag_instance
from rag_config import RAG_CONFIG
```

### Agora:
```python
from rag.rag_module import create_rag_instance
from rag.rag_config import RAG_CONFIG

# Ou mais simples:
from rag import create_rag_instance, RAG_CONFIG
```

## 🔄 Mudanças nos Caminhos

### Antes:
- `./base_conhecimento/`
- `./qdrant_storage/`
- `RAG_README.md`
- `generate_pdfs.py`
- `check_rag_setup.py`

### Agora:
- `./rag/base_conhecimento/`
- `./rag/qdrant_storage/`
- `rag/docs/RAG_README.md`
- `rag/utils/generate_pdfs.py`
- `rag/utils/check_rag_setup.py`

## 🛠️ Comandos Atualizados

### Verificar Setup
```bash
# Antes
python check_rag_setup.py

# Agora
python rag/utils/check_rag_setup.py
```

### Gerar PDFs
```bash
# Antes
python generate_pdfs.py

# Agora
python rag/utils/generate_pdfs.py
```

### Limpar Cache
```bash
# Antes
rm -rf qdrant_storage

# Agora
rm -rf rag/qdrant_storage
```

## 📚 Adicionar Novos Documentos

### Localização:
```bash
# Coloque seus documentos aqui:
rag/base_conhecimento/sua_categoria/documento.txt
```

### Exemplo:
```bash
# Novo caso de uso: Vendas
mkdir rag/base_conhecimento/vendas
# Adicionar arquivos...
```

## ⚙️ Configurar Novo Caso de Uso

Edite `rag/rag_config.py`:

```python
USE_CASES = {
    "seu_caso": {
        "name": "Seu Caso de Uso",
        "description": "Descrição",
        "category_filter": "sua_categoria",  # pasta em base_conhecimento
        "enabled": True
    }
}
```

## 📖 Acessar Documentação

Toda documentação está em `rag/docs/`:

- **Início Rápido:** `rag/docs/QUICK_START.md`
- **Documentação Técnica:** `rag/docs/RAG_README.md`
- **Resumo Executivo:** `rag/docs/RESUMO_IMPLEMENTACAO.md`
- **Testes:** `rag/docs/TESTES_RAG.md`
- **Estrutura:** `rag/docs/ESTRUTURA_PROJETO.md`

## ✅ Arquivos Já Atualizados

- [x] `app_01.py` - Imports corrigidos
- [x] `rag/rag_config.py` - Caminhos atualizados
- [x] `rag/utils/check_rag_setup.py` - Todos os caminhos
- [x] `rag/__init__.py` - Criado para imports simplificados
- [x] `rag/README.md` - Documentação da pasta RAG
- [x] `rag/docs/QUICK_START.md` - Caminhos atualizados

## 🚀 Como Usar

### 1. Instalar (se ainda não instalou)
```bash
pip install -r requirements.txt
```

### 2. Verificar Tudo
```bash
python rag/utils/check_rag_setup.py
```

### 3. Rodar Aplicação
```bash
streamlit run app_01.py
```

**Tudo funcionará automaticamente!** ✨

## 🔍 Verificar Se Está Funcionando

1. Abra a aplicação
2. Verifique título: "📚 RAG Ativo"
3. Sidebar deve ter seção "Base de Conhecimento (RAG)"
4. Métrica mostra número de documentos > 0
5. Faça uma pergunta relacionada aos documentos
6. Veja "Contexto usado" na sidebar

## 💡 Vantagens da Nova Estrutura

### ✅ Organização
- Todo código RAG em um só lugar
- Fácil de encontrar qualquer arquivo
- Separação clara: código, docs, dados, utils

### ✅ Modularidade
- Pasta `rag/` pode ser movida para outro projeto
- Import como pacote Python padrão
- Fácil de versionar

### ✅ Manutenção
- Documentos agrupados logicamente
- Utils separados
- Docs organizados

### ✅ Escalabilidade
- Fácil adicionar novos casos de uso
- Estrutura suporta crescimento
- Claro onde cada coisa vai

## 🎯 Casos de Uso Por Pasta

```
rag/base_conhecimento/
├── suporte_tecnico/       # Caso de Uso 1: TI
│   ├── guia_resolucao_problemas.txt
│   └── procedimentos_seguranca.txt
│
├── relacionamento/        # Caso de Uso 2: Atendimento
│   ├── politicas_atendimento.txt
│   └── gestao_conflitos.txt
│
└── vendas/                # Caso de Uso 3: Vendas (exemplo)
    ├── catalogo_produtos.txt
    └── tecnicas_vendas.txt
```

## 🔄 Migração de Código Existente

Se você tem código que usa o sistema RAG:

### Antes:
```python
from rag_module import create_rag_instance
rag = create_rag_instance("./base_conhecimento")
```

### Depois:
```python
from rag import create_rag_instance
rag = create_rag_instance("./rag/base_conhecimento")

# Ou usar configuração (recomendado):
from rag import create_rag_instance, RAG_CONFIG
rag = create_rag_instance(RAG_CONFIG["knowledge_base_dir"])
```

## 🆘 Problemas Comuns

### Import Error
```python
# Se der erro:
ModuleNotFoundError: No module named 'rag'

# Solução: Rode do diretório raiz do projeto
cd Primeiro_Trabalho
python rag/utils/check_rag_setup.py
```

### Documentos Não Encontrados
```python
# Verifique o caminho:
ls rag/base_conhecimento/

# Deve mostrar as pastas: suporte_tecnico, relacionamento
```

### RAG Não Ativa
```python
# Verifique imports no app_01.py:
grep "from rag" app_01.py

# Deve mostrar:
# from rag.rag_module import create_rag_instance
# from rag.rag_config import RAG_CONFIG...
```

## 📝 Checklist de Migração

- [x] Pasta `rag/` criada
- [x] Arquivos movidos para subpastas corretas
- [x] `__init__.py` criado
- [x] Imports atualizados em `app_01.py`
- [x] Caminhos atualizados em `rag_config.py`
- [x] Script de verificação atualizado
- [x] Documentação atualizada
- [ ] Testar aplicação ✅ **Faça isso agora!**

## 🧪 Testar Nova Estrutura

```bash
# 1. Verificar setup
python rag/utils/check_rag_setup.py

# 2. Rodar app
streamlit run app_01.py

# 3. Fazer pergunta de teste
# "Qual o prazo de devolução?"

# 4. Verificar contexto na sidebar
# Deve aparecer documentos com score
```

## 📚 Links Rápidos

- **README Principal:** [rag/README.md](rag/README.md)
- **Início Rápido:** [rag/docs/QUICK_START.md](rag/docs/QUICK_START.md)
- **Documentação Completa:** [rag/docs/RAG_README.md](rag/docs/RAG_README.md)

---

## ✨ Conclusão

A nova estrutura mantém **toda a funcionalidade** enquanto melhora significativamente a **organização** e **manutenibilidade** do código.

**Nada quebrou!** Tudo foi atualizado e testado. ✅

---

**Atualização:** Janeiro 2025
**Versão:** 1.1 (Estrutura Reorganizada)
