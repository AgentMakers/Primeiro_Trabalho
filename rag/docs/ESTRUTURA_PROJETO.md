# Estrutura do Projeto VOXMAP com RAG

## Visão Geral dos Arquivos

```
Primeiro_Trabalho/
│
├── 📱 APLICAÇÃO PRINCIPAL
│   ├── app_01.py                      # Aplicação Streamlit (integrada com RAG)
│   ├── app_02.py                      # Versão alternativa
│   └── app/
│       └── app_01.py                  # Versão para Docker
│
├── 🤖 SISTEMA RAG (NOVO!)
│   ├── rag_module.py                  # ⭐ Motor RAG completo (450 linhas)
│   ├── rag_config.py                  # ⭐ Configurações e casos de uso (200 linhas)
│   └── generate_pdfs.py               # ⭐ Conversor TXT → PDF (opcional)
│
├── 📚 BASE DE CONHECIMENTO (NOVO!)
│   └── base_conhecimento/
│       ├── suporte_tecnico/           # ⭐ Caso de Uso 1
│       │   ├── guia_resolucao_problemas.txt      (8.5KB)
│       │   └── procedimentos_seguranca.txt        (11.2KB)
│       └── relacionamento/            # ⭐ Caso de Uso 2
│           ├── politicas_atendimento.txt          (16.8KB)
│           └── gestao_conflitos.txt               (14.5KB)
│
├── 💾 BANCO VETORIAL (gerado automaticamente)
│   └── qdrant_storage/                # Criado na primeira execução
│       ├── collection/
│       └── meta.json
│
├── 📖 DOCUMENTAÇÃO (NOVO!)
│   ├── RAG_README.md                  # ⭐ Documentação técnica completa
│   ├── QUICK_START.md                 # ⭐ Guia rápido (5 minutos)
│   ├── RESUMO_IMPLEMENTACAO.md        # ⭐ Este resumo
│   ├── ESTRUTURA_PROJETO.md           # ⭐ Estrutura de arquivos
│   └── README.md                      # Documentação geral do projeto
│
├── ⚙️ CONFIGURAÇÃO
│   ├── .env                           # Variáveis de ambiente (OPENAI_API_KEY)
│   ├── requirements.txt               # ⭐ Atualizado com dependências RAG
│   ├── Dockerfile                     # Container Docker
│   └── .gitignore                     # Arquivos ignorados no Git
│
└── 📁 OUTROS
    ├── Prompts/                       # Prompts alternativos
    │   ├── Operadora_tv.txt
    │   └── assistencia_tecnica.txt
    └── source/                        # Ambiente virtual Python
```

## Legenda

- ⭐ = **Arquivo NOVO** criado na implementação RAG
- 📱 = Aplicação Streamlit
- 🤖 = Sistema RAG (Inteligência Artificial)
- 📚 = Documentos para o RAG
- 💾 = Armazenamento (banco vetorial)
- 📖 = Documentação
- ⚙️ = Configuração
- 📁 = Outros arquivos

---

## Arquivos Principais Explicados

### APLICAÇÃO

#### `app_01.py` (MODIFICADO)
**O que faz:** Interface Streamlit com chat, análise de sentimento, wordcloud, grafo
**Modificações RAG:**
- Importa `rag_module` e `rag_config`
- Busca contexto automaticamente em `obter_mensagens_completas()`
- Adiciona controles RAG na sidebar
- Mostra contexto usado

**Linhas modificadas:** ~50 (adicionadas, não quebram código existente)
**Compatibilidade:** 100% - funciona com ou sem RAG

---

### SISTEMA RAG

#### `rag_module.py` ⭐ NOVO
**O que faz:** Motor completo do sistema RAG
**Funcionalidades:**
- Carrega documentos TXT e PDF
- Divide em chunks (pedaços)
- Gera embeddings (vetores numéricos)
- Armazena no Qdrant
- Busca por similaridade semântica
- Filtra por categoria

**Classes principais:**
- `QdrantRAG`: Classe principal
- `create_rag_instance()`: Factory function

**Métodos importantes:**
- `load_documents()`: Carrega e indexa docs
- `retrieve()`: Busca documentos relevantes
- `get_categories()`: Lista categorias
- `get_stats()`: Estatísticas da base

**Dependências:**
- qdrant-client (banco vetorial)
- sentence-transformers (embeddings)
- PyPDF2 (leitura de PDFs)

#### `rag_config.py` ⭐ NOVO
**O que faz:** Configurações centralizadas
**Seções:**
- `RAG_CONFIG`: Parâmetros gerais
- `USE_CASES`: Casos de uso (suporte, relacionamento)
- `INTEGRATION_CONFIG`: Como integrar com app
- Funções auxiliares de formatação

**Fácil personalizar:** Sim! Apenas edite este arquivo

#### `generate_pdfs.py` ⭐ NOVO
**O que faz:** Converte TXT em PDF profissional
**Uso:** `python generate_pdfs.py`
**Dependência:** reportlab
**Opcional:** Sim (TXT funcionam perfeitamente)

---

### BASE DE CONHECIMENTO

#### `base_conhecimento/` ⭐ NOVA PASTA
**Estrutura:**
```
base_conhecimento/
├── suporte_tecnico/      ← Categoria 1
│   ├── doc1.txt
│   └── doc2.txt
└── relacionamento/       ← Categoria 2
    ├── doc3.txt
    └── doc4.txt
```

**Nome da pasta = Categoria no sistema**

#### Documentos Criados:

**Suporte Técnico (2 arquivos):**
1. `guia_resolucao_problemas.txt`
   - Problemas de rede, software, hardware
   - Email, impressoras, senhas, backup
   - ~200 linhas, 8.5KB

2. `procedimentos_seguranca.txt`
   - Políticas de senha, 2FA
   - Phishing, malware, VPN
   - Gestão de dados e dispositivos
   - ~250 linhas, 11.2KB

**Relacionamento com Cliente (2 arquivos):**
1. `politicas_atendimento.txt`
   - Canais, SLA, scripts
   - Trocas, devoluções, reembolsos
   - Garantias, privacidade, fidelidade
   - ~400 linhas, 16.8KB

2. `gestao_conflitos.txt`
   - Tipos de clientes difíceis
   - Técnicas de comunicação
   - Recovery, situações especiais
   - ~350 linhas, 14.5KB

**Total:** ~1.200 linhas, 50KB de conteúdo

---

### BANCO VETORIAL

#### `qdrant_storage/` (gerado automaticamente)
**O que é:** Banco de dados que armazena embeddings
**Criado quando:** Primeira execução do app
**Pode deletar?** Sim, será recriado (mas demora ~2min)
**Tamanho:** ~1-5MB (dependendo de quantos documentos)
**Backup necessário?** Não obrigatório (pode ser recriado)

---

### DOCUMENTAÇÃO

#### `RAG_README.md` ⭐ NOVO
**Tipo:** Documentação técnica completa
**Tamanho:** ~500 linhas
**Público:** Desenvolvedores e usuários técnicos
**Conteúdo:**
- O que é RAG
- Arquitetura detalhada
- Instalação passo a passo
- Personalização avançada
- Troubleshooting completo

#### `QUICK_START.md` ⭐ NOVO
**Tipo:** Guia de início rápido
**Tamanho:** ~200 linhas
**Público:** Qualquer pessoa
**Conteúdo:**
- Setup em 5 minutos
- Testes rápidos
- FAQ essencial
- Comandos úteis

#### `RESUMO_IMPLEMENTACAO.md` ⭐ NOVO
**Tipo:** Visão executiva
**Tamanho:** ~400 linhas
**Público:** Gestores e decisores
**Conteúdo:**
- O que foi feito
- Como funciona
- Métricas e performance
- Próximos passos

#### `ESTRUTURA_PROJETO.md` ⭐ ESTE ARQUIVO
**Tipo:** Mapa de navegação
**Público:** Qualquer pessoa
**Objetivo:** Entender organização do projeto

---

## Fluxo de Arquivos

### Quando Usuário Faz Pergunta:

```
1. app_01.py recebe mensagem
   ↓
2. Chama obter_mensagens_completas()
   ↓
3. Importa rag_module.py
   ↓
4. rag_module.py busca em qdrant_storage/
   ↓
5. Encontra documentos em base_conhecimento/
   ↓
6. Formata contexto usando rag_config.py
   ↓
7. Retorna para app_01.py
   ↓
8. app_01.py envia para OpenAI (com contexto)
   ↓
9. Resposta exibida ao usuário
```

### Quando Adiciona Documentos:

```
1. Usuário coloca arquivo em base_conhecimento/categoria/
   ↓
2. Clica "Recarregar" no app_01.py
   ↓
3. app_01.py chama rag_instance.load_documents()
   ↓
4. rag_module.py lê arquivo
   ↓
5. Divide em chunks
   ↓
6. Gera embeddings (sentence-transformers)
   ↓
7. Salva em qdrant_storage/
   ↓
8. Pronto! Documento indexado
```

---

## Dependências por Arquivo

### `app_01.py`
```python
streamlit
python-dotenv
openai
wordcloud
networkx
pyvis
pillow
# + rag_module (se disponível)
```

### `rag_module.py`
```python
qdrant-client
sentence-transformers
PyPDF2
pathlib (stdlib)
typing (stdlib)
```

### `rag_config.py`
```python
os (stdlib)
# Nenhuma dependência externa!
```

### `generate_pdfs.py`
```python
reportlab
pathlib (stdlib)
```

---

## Tamanhos de Arquivos

### Código:
- `rag_module.py`: ~15KB (450 linhas)
- `rag_config.py`: ~7KB (200 linhas)
- `app_01.py` (mod): +2KB (50 linhas novas)
- `generate_pdfs.py`: ~6KB (150 linhas)

### Documentação:
- `RAG_README.md`: ~45KB (500 linhas)
- `QUICK_START.md`: ~15KB (200 linhas)
- `RESUMO_IMPLEMENTACAO.md`: ~30KB (400 linhas)
- `ESTRUTURA_PROJETO.md`: ~10KB (este arquivo)

### Base de Conhecimento:
- Suporte Técnico: ~20KB (450 linhas)
- Relacionamento: ~31KB (750 linhas)

### Total Adicionado:
- **Código:** ~30KB
- **Documentação:** ~100KB
- **Conteúdo:** ~51KB
- **TOTAL:** ~180KB de novos arquivos

---

## Como Navegar no Projeto

### Se você é...

#### Desenvolvedor
1. Leia: `RAG_README.md` (técnico)
2. Veja: `rag_module.py` (código comentado)
3. Configure: `rag_config.py`
4. Teste: `QUICK_START.md`

#### Usuário Final
1. Leia: `QUICK_START.md`
2. Execute: `streamlit run app_01.py`
3. Use a interface (intuitiva)

#### Gestor
1. Leia: `RESUMO_IMPLEMENTACAO.md`
2. Veja: Este arquivo (estrutura)
3. Decida: Casos de uso adicionais

#### Pessoa Continuando Desenvolvimento
1. Leia: `RESUMO_IMPLEMENTACAO.md` (visão geral)
2. Leia: `RAG_README.md` (detalhes técnicos)
3. Veja: Comentários no `rag_module.py`
4. Customize: `rag_config.py`

---

## Arquivos Mais Importantes

### Top 5 para Entender o Sistema:

1. **`rag_module.py`** - Coração do RAG
2. **`rag_config.py`** - Personalização fácil
3. **`RAG_README.md`** - Documentação completa
4. **`app_01.py`** (seção RAG) - Integração
5. **`base_conhecimento/`** - Conteúdo

### Top 3 para Começar:

1. **`QUICK_START.md`** - Setup rápido
2. **`requirements.txt`** - Instalar dependências
3. **`app_01.py`** - Executar

---

## Backup Essencial

### O que fazer backup?

✅ **CRÍTICO:**
- `base_conhecimento/` (seus documentos)
- `.env` (chave da API)

✅ **IMPORTANTE:**
- `rag_config.py` (se personalizou)
- `app_01.py` (se modificou além do RAG)

⚠️ **OPCIONAL:**
- `qdrant_storage/` (pode ser recriado, mas demora)

❌ **NÃO PRECISA:**
- `source/` (ambiente virtual)
- `__pycache__/` (cache Python)

---

## Onde Está Cada Coisa?

### "Quero adicionar um novo documento"
→ `base_conhecimento/categoria/seu_documento.txt`

### "Quero criar um novo caso de uso"
→ `rag_config.py` (seção USE_CASES)

### "Quero mudar quantos documentos são buscados"
→ `rag_config.py` (RAG_CONFIG["default_top_k"])

### "Quero trocar o modelo de embeddings"
→ `rag_config.py` (RAG_CONFIG["embedding_model"])

### "Quero modificar o prompt do sistema"
→ `app_01.py` (SYSTEM_PROMPT) ou `rag_config.py` (system_prompt_addon)

### "Quero desabilitar RAG temporariamente"
→ Toggle na sidebar OU `rag_config.py` (RAG_CONFIG["enabled"] = False)

### "Quero ver estatísticas da base"
→ Sidebar → "📊 Stats"

### "Quero recarregar documentos"
→ Sidebar → "🔄 Recarregar"

---

## Conclusão

Projeto bem organizado com:
- ✅ Código modular e desacoplado
- ✅ Documentação em 3 níveis (rápido, técnico, executivo)
- ✅ Base de conhecimento rica (2 casos de uso)
- ✅ Fácil manutenção e expansão
- ✅ Estrutura clara e intuitiva

**Tudo pronto para uso em produção!** 🚀

---

**Última atualização:** Janeiro 2025
**Versão:** 1.0
