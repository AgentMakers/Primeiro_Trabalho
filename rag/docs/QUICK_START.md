# Guia Rápido - Sistema RAG VOXMAP

## Setup em 5 Minutos

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
Certifique-se que `.env` existe com:
```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4.1-mini
```

### 3. Rodar Aplicação
```bash
streamlit run app_01.py
```

A aplicação abrirá em `http://localhost:8501`

### 4. Primeira Vez
- Sistema carregará automaticamente os documentos da pasta `rag/base_conhecimento/`
- Aguarde 1-2 minutos para criar embeddings
- Pronto! RAG está ativo

---

## Testando o Sistema

### Caso 1: Suporte Técnico

**Na sidebar:**
- Caso de uso: "Suporte Técnico TI"

**Perguntas para testar:**
1. "Como resolver problema de internet lenta?"
2. "Quais são os requisitos de senha?"
3. "O que fazer se detectar malware?"
4. "Como funciona a VPN corporativa?"

### Caso 2: Relacionamento com Cliente

**Na sidebar:**
- Caso de uso: "Relacionamento com Cliente"

**Perguntas para testar:**
1. "Qual o prazo de devolução?"
2. "Como lidar com cliente furioso?"
3. "Quais são os canais de atendimento?"
4. "O que fazer em caso de atraso na entrega?"

---

## Verificando se RAG está Funcionando

✅ **Indicadores de sucesso:**
- Sidebar mostra "📚 RAG Ativo" no topo
- Seção "Base de Conhecimento (RAG)" aparece na sidebar
- Métrica mostra número de documentos (deve ser > 0)
- Após resposta, veja "Contexto usado na última resposta"

❌ **Se não estiver funcionando:**
- Verifique se bibliotecas foram instaladas: `pip list | grep qdrant`
- Veja mensagens de erro no terminal
- Consulte [RAG_README.md](RAG_README.md) seção Troubleshooting

---

## Adicionando Seus Próprios Documentos

### Estrutura de Pastas
```
rag/base_conhecimento/
├── sua_categoria/
│   ├── documento1.txt
│   └── documento2.pdf
```

### Formato TXT Recomendado
```txt
TÍTULO DO DOCUMENTO

=== SEÇÃO 1 ===

Conteúdo da seção 1...

SUBTÍTULO: Explicação
- Ponto 1
- Ponto 2

=== SEÇÃO 2 ===

Conteúdo da seção 2...
```

### Recarregar Documentos
1. Adicione/modifique arquivos em `rag/base_conhecimento/`
2. Na aplicação, clique "🔄 Recarregar"
3. Aguarde processamento
4. Pronto!

---

## Configuração Personalizada

### Criar Novo Caso de Uso

Edite `rag_config.py`:

```python
USE_CASES = {
    "meu_caso": {
        "name": "Meu Caso de Uso",
        "description": "Descrição",
        "category_filter": "nome_da_pasta",
        "system_prompt_addon": """
        Instruções específicas...
        """,
        "enabled": True
    }
}
```

Reinicie a aplicação.

---

## Dicas de Uso

### Para Melhor Performance

**Relevância Mínima (threshold):**
- Respostas muito genéricas? → Aumentar para 0.7
- Não acha documentos? → Diminuir para 0.3
- Ideal: 0.5-0.6

**Documentos Retornados (top_k):**
- Respostas superficiais? → Aumentar para 4-5
- Contexto confuso? → Diminuir para 2
- Ideal: 2-3

### Escrevendo Bons Documentos

✅ **FAÇA:**
- Seja específico e direto
- Use números e prazos concretos
- Estruture bem (use === para seções)
- Inclua exemplos práticos

❌ **EVITE:**
- Informações vagas ou genéricas
- Duplicação de conteúdo
- Textos muito curtos (<100 caracteres)
- Jargões sem explicação

---

## Comandos Úteis

### Gerar PDFs a partir de TXT
```bash
pip install reportlab
python rag/utils/generate_pdfs.py
```

### Limpar Cache e Reconstruir Base
```bash
# Windows
rmdir /s rag\qdrant_storage

# Linux/Mac
rm -rf rag/qdrant_storage

# Depois reinicie a aplicação
streamlit run app_01.py
```

### Ver Logs Detalhados
Edite `rag/rag_config.py`:
```python
RAG_CONFIG = {
    ...
    "verbose": True  # ← Ativa logs detalhados
}
```

---

## Próximos Passos

1. ✅ Teste com documentos de exemplo (já incluídos)
2. ✅ Adicione seus próprios documentos
3. ✅ Ajuste configurações conforme necessário
4. ✅ Crie casos de uso específicos
5. ✅ Monitore qualidade das respostas

---

## Recursos

- **Documentação Completa:** [RAG_README.md](RAG_README.md)
- **Código RAG:** [../rag_module.py](../rag_module.py)
- **Configurações:** [../rag_config.py](../rag_config.py)
- **Aplicação:** [../../app_01.py](../../app_01.py)

---

## FAQ Rápido

**P: Preciso pagar pela API Qdrant?**
R: Não! Qdrant roda localmente de graça.

**P: Preciso pagar pelos embeddings?**
R: Não! Sentence Transformers roda localmente de graça.

**P: Só pago pela API OpenAI?**
R: Sim, apenas para gerar as respostas finais.

**P: Posso usar sem OpenAI?**
R: Sim, mas precisará modificar `app_01.py` para usar outro LLM (ex: Ollama, LM Studio).

**P: Quantos documentos posso ter?**
R: Milhares! Qdrant é muito eficiente. Teste com 100-500 para começar.

**P: Funciona offline?**
R: RAG sim (embeddings locais), mas OpenAI não (precisa internet).

**P: Como atualizo um documento?**
R: Edite o arquivo e clique em "Recarregar" na aplicação.

---

**Dúvidas?** Consulte [RAG_README.md](RAG_README.md) para documentação completa!
