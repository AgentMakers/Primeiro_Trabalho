# Visualização do RAG no Chat

Este documento explica as melhorias adicionadas para visualizar o funcionamento do RAG na aplicação.

## O Que Foi Implementado

### 1. Visualização dos Documentos Recuperados no Chat

Agora, quando o RAG está ativo e recupera documentos relevantes, eles são exibidos **diretamente no chat**, logo acima da resposta do assistente.

#### Como Funciona

- **Expander Interativo**: Os documentos aparecem em um expander (pode expandir/colapsar)
- **Título Informativo**: Mostra quantos documentos foram consultados
  - Exemplo: "📚 2 documento(s) consultado(s) na base de conhecimento"
- **Detalhes de Cada Documento**:
  - Nome do arquivo fonte
  - Score de relevância (0-100%)
  - Trecho do texto recuperado (primeiros 300 caracteres)

#### Localização no Código

**Arquivo**: [app_01.py:864-872](app_01.py#L864-L872)

```python
# Mostra documentos RAG ANTES da resposta (se disponíveis)
docs_rag = st.session_state.get("ultimo_contexto_rag", [])
if docs_rag and st.session_state.get("rag_enabled", False):
    with st.expander(f"📚 {len(docs_rag)} documento(s) consultado(s) na base de conhecimento", expanded=False):
        for i, doc in enumerate(docs_rag, 1):
            st.markdown(f"**{i}. {doc['source']}** - Relevância: `{doc['score']:.1%}`")
            st.info(doc['text'][:300] + ("..." if len(doc['text']) > 300 else ""))
            if i < len(docs_rag):
                st.divider()
```

### 2. Histórico Persistente do Contexto RAG

Os documentos recuperados agora são salvos no histórico da conversa, para que você possa ver **quais documentos foram usados** em cada resposta anterior.

#### Como Funciona

- Ao gerar uma resposta com RAG, o contexto é salvo em `lista_mensagens`
- Ao recarregar a página ou rolar o histórico, os documentos aparecem novamente
- Cada resposta mostra seu próprio conjunto de documentos consultados

#### Localização no Código

**Salvamento do contexto** - [app_01.py:889-893](app_01.py#L889-L893):

```python
# Salva contexto RAG junto com a mensagem para histórico
if docs_rag:
    st.session_state["lista_mensagens"].append(
        {"role": "rag_context", "docs": docs_rag}
    )
```

**Renderização no histórico** - [app_01.py:810-820](app_01.py#L810-L820):

```python
elif msg["role"] == "rag_context":
    # Mostra documentos RAG que foram usados nesta resposta
    with st.chat_message("assistant"):
        docs = msg.get("docs", [])
        if docs:
            with st.expander(f"📚 {len(docs)} documento(s) consultado(s) na base de conhecimento", expanded=False):
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**{i}. {doc['source']}** - Relevância: `{doc['score']:.1%}`")
                    st.info(doc['text'][:300] + ("..." if len(doc['text']) > 300 else ""))
```

### 3. Visualização na Sidebar (Já Existente)

A sidebar já tinha uma visualização do último contexto usado, que foi **mantida** para referência rápida.

#### Localização

**Sidebar** - [app_01.py:684-689](app_01.py#L684-L689):

```python
# Mostra último contexto usado
if st.session_state.get("ultimo_contexto_rag"):
    with st.sidebar.expander("🔍 Contexto usado na última resposta"):
        for doc in st.session_state["ultimo_contexto_rag"]:
            st.caption(f"**{doc['source']}** ({doc['score']:.1%})")
            st.text(doc['text'][:150] + "...")
```

---

## Como Testar a Visualização

### Pré-requisitos

1. **Instalar dependências do RAG**:
   ```bash
   pip install qdrant-client sentence-transformers PyPDF2
   ```

2. **Verificar base de conhecimento**:
   ```bash
   python rag/utils/check_rag_setup.py
   ```

### Teste 1: Visualização Básica

1. **Iniciar a aplicação**:
   ```bash
   streamlit run app_01.py
   ```

2. **Verificar RAG ativo na sidebar**:
   - Deve aparecer "📚 Base de Conhecimento (RAG)"
   - Métrica mostrando número de documentos
   - Toggle "Ativar RAG" deve estar ligado

3. **Fazer uma pergunta relevante**:
   - Caso de uso: "Suporte Técnico"
   - Pergunta: "Como resolver problema de internet?"

4. **Observar a resposta**:
   - Logo acima da resposta do assistente, deve aparecer:
     ```
     📚 2 documento(s) consultado(s) na base de conhecimento
     ```
   - Clicar no expander para ver os documentos
   - Verificar:
     - Nome do arquivo (ex: guia_resolucao_problemas.txt)
     - Score de relevância (ex: 87.3%)
     - Trecho do texto

### Teste 2: Diferentes Casos de Uso

1. **Mudar para "Relacionamento com Cliente"** na sidebar

2. **Fazer pergunta sobre políticas**:
   - Pergunta: "Qual o prazo para devolução de produto?"

3. **Verificar documentos diferentes**:
   - Deve buscar em `politicas_atendimento.txt` ou `gestao_conflitos.txt`
   - Score deve refletir a relevância

### Teste 3: Ajustar Parâmetros RAG

1. **Expandir "⚙️ Configurações RAG"** na sidebar

2. **Testar diferentes valores**:
   - **Documentos retornados**: 1, 3, 5
   - **Relevância mínima**: 0.3, 0.5, 0.7

3. **Observar mudanças**:
   - Com top_k=1: Apenas 1 documento
   - Com threshold=0.7: Apenas documentos muito relevantes
   - Com threshold=0.3: Mais documentos, mas menos relevantes

### Teste 4: Histórico Persistente

1. **Fazer 3 perguntas diferentes**:
   - "Como resolver problema de internet?"
   - "Procedimentos de segurança"
   - "Política de devolução"

2. **Rolar para cima** no chat

3. **Verificar cada resposta**:
   - Cada uma deve ter seu próprio expander com documentos
   - Documentos devem ser diferentes para cada pergunta

### Teste 5: RAG Desligado

1. **Desligar o toggle "Ativar RAG"** na sidebar

2. **Fazer uma pergunta**:
   - Pergunta: "Como resolver problema de internet?"

3. **Verificar comportamento**:
   - NÃO deve aparecer o expander de documentos
   - Resposta baseada apenas no conhecimento do GPT

---

## Exemplo Visual

### Com RAG Ativo

```
┌─────────────────────────────────────────────────────┐
│ 👤 Usuário                                          │
│ Como resolver problema de internet?                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🤖 Assistente                                       │
│                                                     │
│ ▼ 📚 2 documento(s) consultado(s) na base de...   │
│   ├─ 1. guia_resolucao_problemas.txt - 87.3%      │
│   │   Para resolver problemas de conexão com...   │
│   └─ 2. procedimentos_seguranca.txt - 65.2%       │
│       Verifique se todos os cabos estão...        │
│                                                     │
│ Para resolver problemas de internet, siga...       │
└─────────────────────────────────────────────────────┘
```

### Com RAG Desligado

```
┌─────────────────────────────────────────────────────┐
│ 👤 Usuário                                          │
│ Como resolver problema de internet?                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 🤖 Assistente                                       │
│                                                     │
│ Para resolver problemas de internet, você pode...  │
│ (resposta genérica do GPT)                         │
└─────────────────────────────────────────────────────┘
```

---

## Informações Exibidas em Cada Documento

Para cada documento recuperado, são exibidos:

1. **Número do documento**: 1, 2, 3...
2. **Nome do arquivo fonte**: `guia_resolucao_problemas.txt`
3. **Score de relevância**: Formato percentual (87.3%)
4. **Trecho do texto**: Primeiros 300 caracteres
5. **Indicador visual**: Caixa azul (st.info) para fácil leitura

### Formato do Score

- **Score alto** (70-100%): Documento muito relevante
- **Score médio** (50-70%): Documento relevante
- **Score baixo** (30-50%): Documento pouco relevante
- **Abaixo do threshold**: Não é mostrado

---

## Controles na Sidebar

### Painel RAG

1. **Métrica de Documentos**: Total de chunks na base
2. **Toggle "Ativar RAG"**: Liga/desliga o sistema
3. **Caso de uso**: Filtra documentos por contexto
4. **Configurações avançadas**:
   - Documentos retornados (top_k)
   - Relevância mínima (threshold)
   - Mostrar erros

### Última Resposta

- Expander mostrando documentos da última pergunta
- Versão resumida (150 caracteres por documento)
- Útil para referência rápida

### Estatísticas

- Botão "📊 Stats" mostra JSON completo:
  ```json
  {
    "total_documents": 1247,
    "categories": {
      "suporte_tecnico": 623,
      "relacionamento": 624
    },
    "sources": {...}
  }
  ```

---

## Troubleshooting

### Problema: Expander não aparece

**Possíveis causas**:
1. RAG desligado (verificar toggle na sidebar)
2. Nenhum documento relevante encontrado (score < threshold)
3. Pergunta muito genérica ou fora do escopo da base

**Solução**:
- Verificar que RAG está ativo
- Reduzir threshold para 0.3
- Aumentar top_k para 5
- Fazer perguntas mais específicas relacionadas aos documentos

### Problema: Scores muito baixos

**Possíveis causas**:
1. Pergunta em idioma diferente dos documentos
2. Vocabulário muito diferente
3. Base de conhecimento não cobre o assunto

**Solução**:
- Reformular a pergunta usando termos dos documentos
- Verificar se o caso de uso está correto
- Adicionar mais documentos relevantes à base

### Problema: Muitos documentos irrelevantes

**Solução**:
- Aumentar threshold para 0.6 ou 0.7
- Reduzir top_k para 1 ou 2
- Usar caso de uso específico (não "Todos")

---

## Próximos Passos

### Melhorias Futuras

1. **Destacar texto relevante**: Marcar palavras-chave no trecho
2. **Link para documento completo**: Botão para ver documento inteiro
3. **Feedback do usuário**: Marcar documento como útil/não útil
4. **Visualização de embeddings**: Mostrar proximidade semântica em gráfico
5. **Cache de buscas**: Evitar buscas duplicadas
6. **Modo debug**: Mostrar query processada e embeddings

### Personalização

Você pode personalizar a visualização editando [app_01.py:867-872](app_01.py#L867-L872):

```python
# Mudar para expanded=True para abrir automaticamente
with st.expander(f"📚 ...", expanded=True):

# Mudar quantidade de texto exibido
st.info(doc['text'][:500] + ...)  # 500 caracteres em vez de 300

# Mudar formato do score
st.markdown(f"Relevância: {doc['score']*100:.1f}%")  # 87.3% em vez de 87%
```

---

## Resumo

As mudanças implementadas permitem **visualizar claramente** quais documentos da base de conhecimento foram consultados para gerar cada resposta do assistente.

**Benefícios**:
- ✅ Transparência: Você sabe exatamente de onde vem a informação
- ✅ Confiabilidade: Pode verificar a fonte e relevância
- ✅ Debugging: Identifica quando RAG não está funcionando bem
- ✅ Aprendizado: Entende como o sistema busca informações
- ✅ Histórico: Mantém registro de todos os documentos consultados

**Localizações principais**:
- Visualização no chat: [app_01.py:864-872](app_01.py#L864-L872)
- Histórico persistente: [app_01.py:810-820](app_01.py#L810-L820)
- Sidebar (resumo): [app_01.py:684-689](app_01.py#L684-L689)

---

**Documentação relacionada**:
- [Como Funciona RAG](COMO_FUNCIONA_RAG.md) - Explicação de chunks e embeddings
- [Instalação RAG](../../INSTALACAO_RAG.md) - Como configurar o sistema
- [RAG README](RAG_README.md) - Documentação completa

**Última atualização**: 2025-10-24
