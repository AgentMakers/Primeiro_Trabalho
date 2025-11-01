# Sistema RAG (Retrieval Augmented Generation) - VOXMAP

## Índice
1. [O que é RAG?](#o-que-é-rag)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Instalação e Configuração](#instalação-e-configuração)
4. [Estrutura de Arquivos](#estrutura-de-arquivos)
5. [Como Usar](#como-usar)
6. [Casos de Uso](#casos-de-uso)
7. [Personalização](#personalização)
8. [Troubleshooting](#troubleshooting)

---

## O que é RAG?

**RAG (Retrieval Augmented Generation)** é uma técnica que melhora respostas de IA buscando informações relevantes em uma base de conhecimento antes de gerar a resposta.

### Analogia Simples:
Imagine que o GPT é um assistente muito inteligente, mas que não conhece as políticas específicas da SUA empresa. O RAG funciona assim:

1. Cliente pergunta: "Qual o prazo de devolução?"
2. RAG busca nos documentos: Encontra "30 dias corridos"
3. GPT responde usando essa informação: "Nosso prazo de devolução é de 30 dias corridos..."

### Benefícios:
- ✅ Respostas baseadas em informações reais da empresa
- ✅ Menos alucinações (invenções) da IA
- ✅ Sempre atualizado (basta atualizar os documentos)
- ✅ Transparência (mostra de onde veio a informação)
- ✅ Compliance (segue políticas da empresa)

---

## Arquitetura do Sistema

```
┌─────────────────┐
│   Usuário       │
│ faz pergunta    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│     VOXMAP (app_01.py)          │
│                                 │
│  1. Recebe pergunta             │
│  2. Chama RAG Module            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   RAG Module (rag_module.py)    │
│                                 │
│  3. Converte pergunta em        │
│     embedding (vetor numérico)  │
│  4. Busca documentos similares  │
│     no Qdrant                   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   Qdrant (banco vetorial)       │
│                                 │
│  5. Retorna documentos mais     │
│     relevantes (top 3)          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   RAG Config (rag_config.py)    │
│                                 │
│  6. Formata contexto            │
│  7. Adiciona ao prompt          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│     OpenAI GPT                  │
│                                 │
│  8. Gera resposta usando        │
│     contexto da base            │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│   Resposta      │
│  ao usuário     │
└─────────────────┘
```

### Componentes:

1. **rag_module.py**: Motor do RAG
   - Carrega documentos (TXT e PDF)
   - Cria embeddings (representação vetorial)
   - Busca documentos relevantes

2. **rag_config.py**: Configurações
   - Casos de uso (Suporte Técnico, Relacionamento)
   - Parâmetros de busca
   - Templates de formatação

3. **app_01.py**: Aplicação principal
   - Interface Streamlit
   - Integração modular com RAG
   - Controles na sidebar

4. **Qdrant**: Banco de dados vetorial
   - Armazena embeddings dos documentos
   - Busca por similaridade super rápida
   - Persistência em disco

5. **Sentence Transformers**: Modelo de embeddings
   - Converte texto em vetores
   - Multilíngue (funciona bem em PT-BR)
   - Roda localmente (sem API)

---

## Instalação e Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Ou manualmente:
```bash
pip install qdrant-client sentence-transformers PyPDF2
```

### 2. Estrutura de Pastas

O sistema criará automaticamente, mas você pode criar manualmente:

```
Primeiro_Trabalho/
├── app_01.py                    # Aplicação principal
├── rag_module.py                # Motor RAG
├── rag_config.py                # Configurações
├── generate_pdfs.py             # Gerador de PDFs (opcional)
├── base_conhecimento/           # Seus documentos (TXT ou PDF)
│   ├── suporte_tecnico/
│   │   ├── guia_resolucao_problemas.txt
│   │   └── procedimentos_seguranca.txt
│   └── relacionamento/
│       ├── politicas_atendimento.txt
│       └── gestao_conflitos.txt
└── qdrant_storage/              # Criado automaticamente
    └── (arquivos do banco)
```

### 3. Configurar .env

Certifique-se de que seu arquivo `.env` tem:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4.1-mini
```

### 4. Primeira Execução

```bash
streamlit run app_01.py
```

Na primeira vez:
- Sistema detectará que base está vazia
- Carregará automaticamente todos os documentos
- Criará embeddings (pode levar 1-2 minutos)
- Salvará no Qdrant (próximas execuções são instantâneas)

---

## Estrutura de Arquivos

### Documentos Suportados

**TXT (Recomendado para começar):**
- Simples e rápido
- Fácil de editar
- Sem formatação complexa

**PDF:**
- Mantém formatação
- Profissional
- Use o script `generate_pdfs.py` para converter TXT em PDF

### Organização por Pastas = Categorias

O sistema usa a estrutura de pastas para categorizar:

```
base_conhecimento/
├── suporte_tecnico/        ← Categoria: "suporte_tecnico"
│   ├── doc1.txt
│   └── doc2.pdf
├── relacionamento/         ← Categoria: "relacionamento"
│   ├── doc3.txt
│   └── doc4.pdf
└── vendas/                 ← Categoria: "vendas"
    └── doc5.txt
```

### Gerar PDFs (Opcional)

Se preferir usar PDFs:

```bash
# Adicionar ao requirements.txt:
# reportlab

pip install reportlab

# Gerar PDFs a partir dos TXT:
python generate_pdfs.py
```

Isso criará PDFs formatados na mesma estrutura de pastas.

---

## Como Usar

### Interface Streamlit

#### Sidebar - Controles RAG

![image](https://via.placeholder.com/300x400?text=Sidebar+RAG)

1. **Ativar RAG**: Toggle para ligar/desligar
2. **Caso de uso**: Selecione contexto (filtra documentos)
3. **Documentos retornados**: Quantos documentos usar (1-5)
4. **Relevância mínima**: Threshold de similaridade (0.0-1.0)
5. **Contexto usado**: Mostra quais documentos foram usados
6. **Stats**: Estatísticas da base de conhecimento

#### Chat Principal

Use normalmente! O RAG funciona automaticamente em segundo plano.

**Exemplo:**

```
Você: Qual o prazo para devolução?

[RAG busca automaticamente nos documentos]

Assistente: De acordo com nossa política, o prazo para
devolução é de 30 dias corridos a partir do recebimento...

[Na sidebar aparece: "Contexto usado: politicas_atendimento.txt (85%)"]
```

### Casos de Uso

#### 1. Suporte Técnico TI

**Documentos incluídos:**
- Guia de Resolução de Problemas
- Procedimentos de Segurança

**Exemplos de perguntas:**
- "Como resolver problema de internet lenta?"
- "O que fazer se o antivírus detectar malware?"
- "Quais são os requisitos de senha?"

#### 2. Relacionamento com Cliente

**Documentos incluídos:**
- Políticas de Atendimento
- Gestão de Conflitos

**Exemplos de perguntas:**
- "Qual a política de devolução?"
- "Como lidar com cliente furioso?"
- "Quais são os canais de atendimento?"

### Recarregar Base de Conhecimento

Quando adicionar ou modificar documentos:

1. Clique em "🔄 Recarregar" na sidebar
2. Aguarde processamento (barra de progresso)
3. Pronto! Novos documentos indexados

---

## Personalização

### Adicionar Novo Caso de Uso

Edite [rag_config.py](rag_config.py):

```python
USE_CASES = {
    "seu_novo_caso": {
        "name": "Nome Exibido",
        "description": "Descrição",
        "category_filter": "nome_da_pasta",  # deve corresponder à pasta
        "system_prompt_addon": """

[CONTEXTO: Seu Contexto]
Instruções específicas para este caso...
        """,
        "enabled": True
    }
}
```

Crie a pasta correspondente:
```
base_conhecimento/nome_da_pasta/
```

### Ajustar Parâmetros de Busca

Edite [rag_config.py](rag_config.py):

```python
RAG_CONFIG = {
    "chunk_size": 500,         # Tamanho de cada pedaço de texto
    "chunk_overlap": 50,       # Overlap entre pedaços
    "default_top_k": 3,        # Quantos documentos buscar
    "score_threshold": 0.5,    # Relevância mínima (0-1)
}
```

**Quando ajustar:**
- **chunk_size**: Documentos curtos → menor (300), longos → maior (800)
- **chunk_overlap**: Mais overlap = mais contexto, mas mais lento
- **top_k**: Respostas genéricas → aumentar (5), específicas → diminuir (2)
- **score_threshold**: Muitos resultados ruins → aumentar (0.7), poucos resultados → diminuir (0.3)

### Trocar Modelo de Embeddings

Modelos disponíveis:

```python
# Rápido e leve (RECOMENDADO)
"paraphrase-multilingual-MiniLM-L12-v2"

# Mais preciso, porém mais lento
"paraphrase-multilingual-mpnet-base-v2"

# Melhor para português específico
"rufimelo/bert-large-portuguese-cased-sts"
```

Edite em [rag_config.py](rag_config.py):
```python
RAG_CONFIG = {
    "embedding_model": "seu_modelo_aqui"
}
```

---

## Troubleshooting

### RAG não está aparecendo

**Problema:** Sidebar não mostra controles RAG

**Soluções:**
1. Verifique se bibliotecas estão instaladas:
```bash
pip list | grep qdrant
pip list | grep sentence-transformers
```

2. Verifique se `rag_config.py` tem:
```python
RAG_CONFIG = {
    "enabled": True,
    ...
}
```

3. Veja erros no terminal/console

---

### "Sem documentos suficientes"

**Problema:** Mensagem de base vazia

**Soluções:**
1. Verifique se pasta `base_conhecimento/` existe
2. Verifique se há arquivos .txt ou .pdf dentro
3. Arquivos devem ter pelo menos 50 caracteres
4. Clique em "Recarregar" para reprocessar

---

### Respostas não usam contexto RAG

**Problema:** IA não menciona informações dos documentos

**Causas possíveis:**
1. **Relevância muito baixa:** Documentos não são similares à pergunta
   - **Solução:** Diminuir threshold (ex: 0.3)

2. **Poucos documentos retornados:**
   - **Solução:** Aumentar `top_k` (ex: 5)

3. **RAG desativado:**
   - **Solução:** Verificar toggle "Ativar RAG"

4. **Categoria errada:**
   - **Solução:** Selecionar caso de uso correto ou usar "Geral"

**Debug:**
- Veja "Contexto usado" na sidebar
- Se estiver vazio = documentos não foram encontrados
- Se tiver documentos mas IA não usa = problema no prompt

---

### Busca muito lenta

**Problema:** Demora para responder

**Causas:**
1. **Primeira busca:** Modelo de embeddings está carregando
   - Normal na primeira execução (30-60s)
   - Próximas são rápidas

2. **Muitos documentos:**
   - Use filtro de categoria
   - Diminua `top_k`

3. **Chunks muito pequenos:**
   - Aumentar `chunk_size` (ex: 800)

---

### Erro "Collection not found"

**Problema:** Qdrant não encontra coleção

**Solução:**
```bash
# Delete pasta qdrant_storage
rm -rf qdrant_storage  # Linux/Mac
rmdir /s qdrant_storage  # Windows

# Reinicie aplicação
streamlit run app_01.py
```

Sistema recriará tudo automaticamente.

---

### PDFs não são lidos

**Problema:** PDFs aparecem vazios

**Soluções:**
1. Instale PyPDF2:
```bash
pip install PyPDF2
```

2. PDFs podem ser imagens escaneadas (não têm texto extraível)
   - Use OCR ou converta para texto primeiro

3. PDFs protegidos por senha não funcionam
   - Remova senha antes

---

## Monitoramento e Métricas

### Verificar Qualidade do RAG

**Na interface:**
- Veja "Contexto usado" após cada resposta
- Score de relevância deve ser > 60% idealmente
- Se muito baixo, documentos não são relevantes

**Perguntas de teste:**
Crie perguntas que você sabe que estão nos documentos e veja se o RAG encontra.

### Estatísticas

Clique em "📊 Stats" na sidebar:

```json
{
  "total_documents": 150,
  "categories": ["suporte_tecnico", "relacionamento"],
  "category_counts": {
    "suporte_tecnico": 80,
    "relacionamento": 70
  }
}
```

---

## Boas Práticas

### Escrevendo Documentos

**✅ BOM:**
- Linguagem clara e direta
- Seções bem definidas (===)
- Informações específicas e completas
- Exemplos práticos
- Prazos e números concretos

**❌ RUIM:**
- Linguagem vaga ("geralmente", "talvez")
- Sem estrutura
- Informações duplicadas
- Muito genérico

**Exemplo BOM:**
```
POLÍTICA DE DEVOLUÇÃO

Prazo: 30 dias corridos a partir do recebimento.

Condições:
- Produto sem uso
- Embalagem original preservada
- Nota fiscal em mãos

Reembolso: Até 10 dias úteis após receber o produto.
```

**Exemplo RUIM:**
```
Temos uma boa política de devolução.
Entre em contato que analisamos caso a caso.
Normalmente é rápido.
```

### Manutenção

**Revisão mensal:**
- Adicionar novos documentos conforme necessário
- Remover informações desatualizadas
- Testar perguntas frequentes
- Verificar métricas de satisfação

**Quando atualizar:**
- Mudança de políticas da empresa
- Novos produtos/serviços
- Feedback de clientes sobre informações incorretas
- Novas perguntas frequentes identificadas

---

## Expansão Futura

### Próximos Passos

1. **Mais casos de uso:**
   - Vendas
   - Financeiro
   - RH
   - Produto

2. **Integração com fontes externas:**
   - APIs de sistemas internos
   - Bases de dados SQL
   - Documentação online

3. **Analytics:**
   - Quais documentos são mais usados
   - Quais perguntas não encontram resposta
   - Tempo médio de resolução

4. **Multi-idioma:**
   - Documentos em inglês, espanhol
   - Detecção automática de idioma

---

## Contato e Suporte

**Dúvidas sobre RAG:**
- Consulte este README
- Veja comentários no código (`rag_module.py`)

**Problemas técnicos:**
- Verifique seção Troubleshooting
- Consulte logs no terminal

**Melhorias:**
- Documente casos de uso que funcionam bem
- Compartilhe boas práticas com equipe

---

## Changelog

### v1.0 (Atual)
- ✅ Sistema RAG modular completo
- ✅ Suporte a TXT e PDF
- ✅ 2 casos de uso (Suporte TI + Relacionamento)
- ✅ Interface Streamlit integrada
- ✅ Qdrant para busca vetorial
- ✅ Sentence Transformers para embeddings
- ✅ Documentação completa

---

**Criado por:** Marcus Loreto
**Data:** 2025
**Versão:** 1.0
