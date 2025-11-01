# Guia de Instalação - Sistema RAG VOXMAP

## 📋 Pré-requisitos

- Python 3.10 ou superior
- pip atualizado
- Conexão com internet (para download de modelos)
- ~2GB de espaço em disco (modelos + dados)

## 🚀 Instalação Rápida (5 minutos)

### 1. Navegar para a pasta do projeto
```bash
cd "C:\Python Projects\pos-ufg\Primeiro_Trabalho"
```

### 2. Criar ambiente virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

**Tempo estimado:** 2-3 minutos (depende da internet)

### 4. Configurar variável de ambiente
Crie/edite arquivo `.env`:
```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4.1-mini
```

### 5. Verificar instalação
```bash
python rag/utils/check_rag_setup.py
```

**Esperado:** Todas verificações com ✅ (exceto qdrant_storage que será criado depois)

### 6. Primeira execução
```bash
streamlit run app_01.py
```

**Na primeira vez:**
- Sistema baixará modelo de embeddings (~400MB) - Aguarde!
- Indexará documentos (~2 minutos)
- Criará pasta `rag/qdrant_storage/`

**Próximas execuções:** Instantâneas! ⚡

---

## 📦 Dependências Explicadas

### Core (Obrigatórias)
```bash
pip install streamlit python-dotenv openai
```
- `streamlit`: Interface web
- `python-dotenv`: Variáveis de ambiente
- `openai`: API OpenAI (GPT)

### RAG (Sistema de Busca)
```bash
pip install qdrant-client sentence-transformers PyPDF2
```
- `qdrant-client`: Banco vetorial (busca rápida)
- `sentence-transformers`: Embeddings (conversão texto→vetor)
- `PyPDF2`: Leitura de arquivos PDF

### Análises (Opcionais)
```bash
pip install wordcloud networkx pyvis pillow
```
- `wordcloud`: Nuvem de palavras
- `networkx`: Grafos
- `pyvis`: Visualização interativa
- `pillow`: Processamento de imagens

### Utilitários (Opcionais)
```bash
pip install reportlab
```
- `reportlab`: Geração de PDFs profissionais

---

## 🔍 Verificação Detalhada

### Checklist Pós-Instalação:

#### ✅ Dependências
```bash
python -c "import qdrant_client; print('Qdrant OK')"
python -c "import sentence_transformers; print('Transformers OK')"
python -c "from openai import OpenAI; print('OpenAI OK')"
```

#### ✅ Estrutura de Arquivos
```bash
ls rag/rag_module.py          # Deve existir
ls rag/rag_config.py           # Deve existir
ls rag/base_conhecimento/      # Deve existir
```

#### ✅ Imports Python
```bash
python -c "from rag import create_rag_instance; print('Import OK')"
```

#### ✅ Documentos
```bash
ls rag/base_conhecimento/suporte_tecnico/*.txt
ls rag/base_conhecimento/relacionamento/*.txt
```
**Esperado:** 4 arquivos .txt

---

## 🐛 Problemas Comuns

### Problema 1: "ModuleNotFoundError: No module named 'qdrant_client'"

**Causa:** Dependências RAG não instaladas

**Solução:**
```bash
pip install qdrant-client sentence-transformers PyPDF2
```

---

### Problema 2: "No module named 'rag'"

**Causa:** Executando do diretório errado

**Solução:**
```bash
cd "C:\Python Projects\pos-ufg\Primeiro_Trabalho"
python rag/utils/check_rag_setup.py
```

---

### Problema 3: Download do modelo muito lento

**Causa:** Internet lenta ou proxy

**Soluções:**
1. Aguardar (só acontece 1x, ~400MB)
2. Ou baixar modelo manualmente:
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

---

### Problema 4: "OPENAI_API_KEY não encontrada"

**Causa:** Arquivo .env não configurado

**Solução:**
1. Criar arquivo `.env` na raiz
2. Adicionar: `OPENAI_API_KEY=sua_chave`
3. Obter chave em: https://platform.openai.com/api-keys

---

### Problema 5: Windows - Erro de encoding

**Causa:** Terminal Windows com encoding errado

**Solução:**
```bash
chcp 65001
python rag/utils/check_rag_setup.py
```

---

## 🌐 Instalação em Ambiente Corporativo

### Com Proxy:
```bash
set HTTP_PROXY=http://proxy.empresa.com:8080
set HTTPS_PROXY=http://proxy.empresa.com:8080
pip install -r requirements.txt
```

### Sem Acesso Externo (Offline):
1. Baixar pacotes em máquina com internet:
```bash
pip download -r requirements.txt -d packages/
```

2. Transferir pasta `packages/` para máquina offline

3. Instalar localmente:
```bash
pip install --no-index --find-links packages/ -r requirements.txt
```

---

## 🐳 Instalação com Docker

### Dockerfile já incluso:
```bash
docker build -t voxmap .
docker run -p 8501:8501 --env-file .env voxmap
```

Acesse: http://localhost:8501

---

## 🧪 Teste Pós-Instalação

### Teste 1: Script de Verificação
```bash
python rag/utils/check_rag_setup.py
```
**Esperado:** Maioria das verificações com ✅

### Teste 2: Executar Aplicação
```bash
streamlit run app_01.py
```
**Esperado:**
- Abre em http://localhost:8501
- Sidebar mostra "📚 RAG Ativo"
- Métrica "Documentos" > 0

### Teste 3: Buscar Documento
No chat, pergunte:
> "Qual o prazo de devolução?"

**Esperado:**
- Resposta menciona "30 dias" ou "7 dias"
- Sidebar mostra "Contexto usado"
- Score de relevância > 60%

---

## 📊 Requisitos de Sistema

### Mínimos:
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disco:** 2GB livres
- **Internet:** Para instalação e uso (OpenAI API)

### Recomendados:
- **CPU:** 4+ cores
- **RAM:** 8GB
- **Disco:** 5GB livres (para crescimento)
- **Internet:** Banda larga

### Primeira Execução:
- **RAM:** ~1.5GB (modelo de embeddings)
- **Disco:** ~500MB (modelo + índice)
- **Tempo:** 2-3 minutos

### Execuções Seguintes:
- **RAM:** ~600MB
- **Disco:** Cresce ~1MB por 1000 documentos
- **Tempo:** Instantâneo

---

## 🔄 Atualização

### Atualizar Dependências:
```bash
pip install --upgrade -r requirements.txt
```

### Atualizar Código RAG:
```bash
git pull  # Se usando git
# Ou substituir arquivos manualmente
```

### Recriar Índice:
```bash
rm -rf rag/qdrant_storage
streamlit run app_01.py
# Aguardar re-indexação
```

---

## 🗑️ Desinstalação

### Remover Ambiente Virtual:
```bash
deactivate  # Sair do venv
rm -rf venv  # Deletar venv
```

### Limpar Cache:
```bash
rm -rf rag/qdrant_storage
rm -rf rag/__pycache__
```

### Manter Apenas Documentos:
Fazer backup de `rag/base_conhecimento/` antes de deletar outras pastas

---

## 📞 Suporte

### Problemas de Instalação:
1. Consulte seção "Problemas Comuns" acima
2. Execute: `python rag/utils/check_rag_setup.py`
3. Veja logs de erro detalhados

### Problemas de Uso:
1. Consulte: `rag/docs/TESTES_RAG.md`
2. Consulte: `rag/docs/RAG_README.md` → Troubleshooting

### Documentação:
- **Rápida:** `rag/docs/QUICK_START.md`
- **Completa:** `rag/docs/RAG_README.md`
- **Estrutura:** `NOVA_ESTRUTURA_RAG.md`

---

## ✅ Checklist Final

Antes de começar a usar:

- [ ] Python 3.10+ instalado
- [ ] Todas dependências instaladas (check_rag_setup.py ✅)
- [ ] Arquivo .env configurado
- [ ] Aplicação abre corretamente
- [ ] Sidebar mostra "RAG Ativo"
- [ ] Teste de pergunta funcionou
- [ ] Contexto aparece na sidebar
- [ ] Documentação lida (pelo menos QUICK_START)

**Tudo OK?** Você está pronto para usar o sistema! 🎉

---

## 🚀 Próximos Passos

Após instalação bem-sucedida:

1. ✅ Ler: `rag/docs/QUICK_START.md`
2. ✅ Testar: Com perguntas dos documentos
3. ✅ Adicionar: Seus próprios documentos
4. ✅ Personalizar: Casos de uso em `rag/rag_config.py`
5. ✅ Monitorar: Qualidade das respostas

---

**Instalação criada:** Janeiro 2025
**Versão:** 1.1
**Sistema:** VOXMAP RAG
