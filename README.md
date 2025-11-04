# VOXMAP


## 📋 Sobre o Projeto

VOXMAP é uma aplicação inteligente de Assistente de Atendimento e Conciliação que utiliza:
- **Interface:** Streamlit para interface web interativa
- **IA:** OpenAI para análise e geração de respostas
- **RAG:** Sistema de busca semântica com Qdrant (banco vetorial)
- **Análises:** Sentimento, nuvem de palavras e grafos de relacionamento

---

## 🔧 Pré-requisitos

- **Python 3.13.5 ou superior**
- **Docker** (para visualização da interface do qdrant)
- **Docker Compose** (opcional, recomendado para produção)

---

## ⚙️ Configuração Inicial

### 1. Arquivo de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# API OpenAI
OPENAI_API_KEY=sua_chave_api_aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
OPENAI_MAX_TOKENS=400
```

> ⚠️ **IMPORTANTE:** Nunca commite o arquivo `.env` no Git!

---

## 🚀 Instalação e Execução
##############################################################
### Opção 1: Ambiente Local (Linux/Mac)

```bash
# 1. Clone o repositório (se necessário)
git clone <seu-repositorio>
cd Primeiro_Trabalho

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Rodar Qdrant (interface visual) usando Docker, para acesso ao dashboard web. 
# Para execução local, será necessário instalar o docker Desktop.
# Após instalado e com o docker Descktop aberto, executar o seguinte comando para inicializar o container do qdrant:
### No terminal:
docker run -d --name qdrant-rag -p 6333:6333 -p 6334:6334 -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" qdrant/qdrant:latest

# 5. Execute a aplicação Streamlit
streamlit run app_01.py 
```

###############################################################
### Opção 2: Ambiente Local (Windows PowerShell)

```powershell
# 1. Navegue até o diretório do projeto
cd "C:\Python Projects\pos-ufg\Primeiro_Trabalho"

# 2. Crie e ative o ambiente virtual
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
.\.venv\Scripts\Activate.ps1

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Rodar Qdrant (interface visual) usando Docker, para acesso ao dashboard web. 
# Para execução local, será necessário instalar o docker Desktop.
# Após instalado e com o docker Descktop aberto, executar o seguinte comando para inicializar o container do qdrant:
### No terminal:
docker run -d --name qdrant-rag -p 6333:6333 -p 6334:6334 -v "$(pwd)/rag/qdrant_storage:/qdrant/storage" qdrant/qdrant:latest

# 5. Execute a aplicação Streamlit
streamlit run app_01.py --server.port 8501 --server.address 0.0.0.0
```

#################################################################
### Opção 3: Docker (Recomendado para Produção)

```bash
# Executar com Docker Compose
docker compose up --build -d

# Verificar logs
docker compose logs -f

# Parar a aplicação
docker compose down
```

---

## 🌐 Acesso à Aplicação

Após iniciar, acesse no navegador:
- **Local:** http://localhost:8501
- **Rede:** http://seu-ip:8501

---

## 📦 Estrutura do Projeto

```
Primeiro_Trabalho/
├── app/
│   └── app_01.py          # Aplicação principal Streamlit
├── rag/                    # Módulo RAG (busca semântica)
│   └── rag_module.py
├── .env                    # Variáveis de ambiente (NÃO commitar)
├── requirements.txt        # Dependências Python
├── Dockerfile             # Configuração Docker
└── docker-compose.yml     # Orquestração Docker
```

---

## 🔍 Comandos Úteis

### Aplicação Streamlit
```bash
# Modo desenvolvimento
streamlit run app_01.py

# Modo produção (aceita conexões externas)
streamlit run app_01.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
```

### API (se disponível)
```bash
# Entrar na pasta app e executar
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🛠️ Troubleshooting

### Problema: Streamlit não inicia
```bash
# Verifique se as dependências estão instaladas
pip list

# Reinstale as dependências
pip install -r requirements.txt --force-reinstall
```

### Problema: Erro de encoding no requirements.txt
```bash
# Certifique-se que o arquivo está em UTF-8
# No Windows, abra no VS Code e salve como UTF-8
```

### Problema: Docker não conecta
```bash
# Verifique os logs
docker compose logs -f

# Reinicie os containers
docker compose restart

# Reconstrua a imagem
docker compose up --build --force-recreate
```

### Problema: Porta 8501 em uso
```bash
# Linux/Mac - Encontre o processo
lsof -i :8501

# Windows - Encontre o processo
netstat -ano | findstr :8501

# Mate o processo ou use outra porta
streamlit run app_01.py --server.port 8502
```

---

## 📚 Dependências Principais

| Biblioteca | Versão | Propósito |
|-----------|--------|-----------|
| streamlit | 1.50.0 | Interface web |
| openai | 2.6.1 | API de IA |
| qdrant-client | 1.15.1 | Banco vetorial |
| sentence-transformers | 5.1.2 | Embeddings |
| pandas | 2.3.3 | Análise de dados |
| wordcloud | 1.9.4 | Visualizações |

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos na UFG.

---

Pós-graduação UFG

---

## 🆘 Suporte

Para questões ou problemas:
1. Verifique a seção de Troubleshooting
2. Consulte a documentação das bibliotecas utilizadas
3. Entre em contato com a equipe do projeto
