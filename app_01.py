# app.py
import os
import streamlit as st
from dotenv import load_dotenv
from streamlit.components.v1 import html as st_html
from openai import OpenAI
import json
from pathlib import Path
import re
from io import BytesIO
from collections import Counter
import base64

# cleaned imports: SequenceMatcher and base64 are stdlib, network/pyvis/wordcloud optional
try:
    from difflib import SequenceMatcher

    _SEQUENCEMATCHER_AVAILABLE = True
except Exception:
    SequenceMatcher = None
    _SEQUENCEMATCHER_AVAILABLE = False


# optional graph libs
_WORDCLOUD_AVAILABLE = True
try:
    from wordcloud import WordCloud
except Exception:
    _WORDCLOUD_AVAILABLE = False

try:
    import networkx as nx  # type: ignore
    from pyvis.network import Network  # type: ignore

    _GRAPH_AVAILABLE = True
except Exception:
    
    nx = None
    Network = None
    _GRAPH_AVAILABLE = False

# Carrega variáveis do .env
load_dotenv()

# Para rodar o sistema: streamlit run bot.py

# ╔════════════════════════════════════════════════════════════════╗
# ║ MÓDULO RAG (OPCIONAL - PLUG AND PLAY)                          ║
# ╚════════════════════════════════════════════════════════════════╝

from qdrant_client import QdrantClient

client = QdrantClient(host="qdrant", port=6333)

print(client.get_collections())


# from qdrant_client import QdrantClient
# from qdrant_client.models import VectorParams, Distance

# qdrant = QdrantClient(
#     host=os.getenv("QDRANT_HOST", "qdrant"),
#     port=int(os.getenv("QDRANT_PORT", 6333))
# )

# if not qdrant.collection_exists("minha_collection"):
#     qdrant.create_collection(
#         collection_name="minha_collection",
#         vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
#     )

#_RAG_AVAILABLE = False
#rag_instance = None

#try:
   # from rag.rag_module import create_rag_instance
   # from rag.rag_config import RAG_CONFIG, get_active_use_cases, format_rag_context
   # _RAG_AVAILABLE = True
#except ImportError:
   # RAG_CONFIG = {"enabled": False}


# ╔════════════════════════════════════════════════════════════════╗
# ║ ASSISTENTE DEFINIDO 100% NO CÓDIGO (sem RAG / sem arquivos)    ║
# ╚════════════════════════════════════════════════════════════════╝

# Prompt de sistema (Atendimento e Conciliação)
SYSTEM_PROMPT = """
Você é o Assistente de Atendimento e Conciliação da empresa.
Missão: resolver solicitações de clientes com rapidez, cordialidade e foco em acordos justos.
Você é um assistente que responde apenas após a primeira mensagem do usuário.
Não peça nome nem dados pessoais por padrão.
Se a conversa estiver vazia, não diga nada.

Princípios:
1) Clareza, objetividade e empatia; trate o cliente pelo nome se fornecido.
2) Confirme entendimento do caso em 1 frase antes de propor solução.
3) Traga opções de conciliação: reenvio, abatimento, reembolso (parcial/total), crédito em conta, cupom.
4) Explique prazos, documentos necessários e próximos passos com bullets curtos.
5) Se faltar informação, faça no máximo 2 perguntas diretas e relevantes.
6) Evite jargões; linguagem simples e educada.
7) Respeite políticas: não prometa o que não pode cumprir; se necessário, escale ao time responsável.
8) Proteção de dados: não invente dados do cliente; confirme somente o que foi informado.

Formato da resposta:
- Resumo do caso:
- Solução proposta:
- Próximos passos:
- Observações:

Exemplo de tom:
“Entendi o ocorrido e quero resolver isso da forma mais rápida e justa para você.”
"""

# Configuração do assistente (inline)
CONFIG = {
    "modelo_padrao": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    "temperatura_padrao": 0.2,
    "max_contexto_rag": 3,  # Mantido para compatibilidade futura,
}

modelo = CONFIG.get("modelo_padrao", "gpt-4.1-mini")
temperatura = CONFIG.get("temperatura_padrao", 0.2)
max_tokens = CONFIG.get("max_tokens_padrao", 400)

# ╔════════════════════════════════════════════════════════════════╗
# ║ VALIDAÇÃO E CLIENTE OPENAI  Com resgate se for modelo nano
# ╚════════════════════════════════════════════════════════════════╝

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("OPENAI_API_KEY não encontrada. Defina no ambiente (ex.: arquivo .env).")
    st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# def _is_nano(model_name: str) -> bool:
#     return "nano" in (model_name or "").lower()


# SUGESTÃO DE CÓDIGO PARA CRIAR O CACHE:
# CASO NÃO FUNCIONE, REMOVER ESSE TRECHO!!!
# @st.cache_resource
# def get_rag_instance():
#     """
#     Carrega a instância RAG uma única vez e a armazena em cache.
#     """
#     if not _RAG_AVAILABLE or not RAG_CONFIG.get("enabled", False):
#         return None
#     try:
#         # Este spinner só aparecerá na *primeira* carga do app
#         with st.spinner("🔧 Inicializando sistema RAG (cache)..."):
#             rag_instance = create_rag_instance(
#                 knowledge_base_dir=RAG_CONFIG.get("knowledge_base_dir", "./base_conhecimento"),
#                 verbose=False
#             )
#             return rag_instance
#     except Exception as e:
#         # Se falhar, mostrará o erro na sidebar
#         st.sidebar.error(f"Falha ao inicializar RAG: {e}")
#         return None

# # Inicializa e obtém a instância RAG do cache
# rag_instance = get_rag_instance()

## teste para carregar o qdrant 
import qdrant_client
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def get_qdrant_client():
    return QdrantClient(host="qdrant", port=6333)

def ensure_qdrant_collection(client, collection_name="rag_collection", vector_size=768):
    collections = client.get_collections()
    if collection_name not in [c.name for c in collections.collections]:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

# Inicialização direta no Streamlit
try:
    client = get_qdrant_client()
    ensure_qdrant_collection(client)
except Exception as e:
    st.sidebar.error(f"Erro ao inicializar Qdrant: {e}")
    st.stop()

# E depois para consultar/exibir:
docs = client.search(collection_name="rag_collection", query_vector=seu_vector)
st.markdown("### Resultados RAG")
for i, doc in enumerate(docs, 1):
    st.markdown(f"**{i}.** {doc['payload']['text']}")

# ********####

def call_llm(
    user_message: str,
    *,
    model: str | None = None,
    # temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Chamada robusta que trata modelos 'nano' (sem temperature e com max_completion_tokens),
    e usa parâmetros padrão do CONFIG quando não informados.
    """
    model = model or CONFIG["modelo_padrao"]
    max_tokens = max_tokens or CONFIG["max_tokens_padrao"]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        # NÃO enviar temperature para nano
        max_completion_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()


def obter_mensagens_completas():
    """Inclui o system message + contexto RAG no início da lista de mensagens"""
    system_msg = {"role": "system", "content": prompt_sistema.strip()}

    # ═══════════════════════════════════════════════════════
    # INTEGRAÇÃO RAG - Busca contexto relevante automaticamente
    # ═══════════════════════════════════════════════════════
    if _RAG_AVAILABLE and rag_instance and st.session_state.get("rag_enabled", True):
        try:
            # Pega últimas mensagens do usuário para contexto
            user_messages = [
                m["content"] for m in st.session_state["lista_mensagens"][-6:]
                if m["role"] == "user"
            ]

            if user_messages:
                # Combina últimas mensagens como query
                query = " ".join(user_messages[-1:])  # Últimas 2 mensagens

                # Busca documentos relevantes
                # category_filter = st.session_state.get("rag_category_filter")
                docs = rag_instance.retrieve(
                    query=query,
                    top_k=st.session_state.get("rag_top_k", 3),
                    score_threshold=st.session_state.get("rag_threshold", 0.5),
                    # category_filter=category_filter
                )

                if docs:
                    # Formata contexto usando a função do config
                    contexto_rag = format_rag_context(docs)
                    system_msg["content"] += contexto_rag

                    # Salva para exibir na UI
                    st.session_state["ultimo_contexto_rag"] = docs
                else:
                    st.session_state["ultimo_contexto_rag"] = []
        except Exception as e:
            if st.session_state.get("rag_show_errors", False):
                st.sidebar.error(f"Erro no RAG: {e}")

    # codigo original (removido para evitar o erro junto a OpenAI - substituido pelo codigo abaixo)
    # return [system_msg] + st.session_state["lista_mensagens"]
    
    # Filtra o histórico de mensagens para enviar à API
    # Isso remove as mensagens internas, como "rag_context"
    api_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state["lista_mensagens"]
        if msg["role"] in ("user", "assistant")
    ]

    return [system_msg] + api_messages


# ═══════════════════════════════════════════════════════
# CONFIGURAÇÃO INICIAL
# ═══════════════════════════════════════════════════════

config = CONFIG
prompt_sistema = SYSTEM_PROMPT


# Inicializa RAG se disponível
#if _RAG_AVAILABLE and RAG_CONFIG.get("enabled", False):
#    if rag_instance is None:
#        with st.spinner("🔧 Inicializando sistema RAG..."):
#            rag_instance = create_rag_instance(
#                knowledge_base_dir=RAG_CONFIG.get("knowledge_base_dir", "./base_conhecimento"),
#                verbose=False  # Logs no console, não no Streamlit
#            )
#

# O código a seguir inicializa a instância RAG no session_state porém como o
# cache já está funcionando, não é necessário.
#if _RAG_AVAILABLE and RAG_CONFIG.get("enabled", False):
#    # Verifica se a instância já existe no st.session_state
#    if "rag_instance" not in st.session_state:
#        with st.spinner("🔧 Inicializando sistema RAG..."):
#            # Armazena a instância no session_state
#            st.session_state["rag_instance"] = create_rag_instance(
#                knowledge_base_dir=RAG_CONFIG.get("knowledge_base_dir", "./base_conhecimento"),
#                verbose=False  # Logs no console, não no Streamlit
#            )
#    # Atribui a instância do cache à variável local para o restante do script usar
#    rag_instance = st.session_state.get("rag_instance")            

st.title("🧑‍💬 Analisador de Conversas ")
st.write("---")
caption_parts = [" • 🧠 Sentimento   • ☁️ WordCloud   • 🔗 Grafo de Palavras "]
if rag_instance:
    caption_parts.append("  • 📚 RAG Ativo")
st.caption("".join(caption_parts))


# ──────────────────────────────────────────────────────────────
# Funções de Sentimento
# ──────────────────────────────────────────────────────────────


def _formatar_prompt_sentimento(texto: str) -> str:
    return (
        "Você é um classificador de sentimento. Classifique a mensagem a seguir.\n"
        "Responda APENAS com JSON válido com as chaves exatamente assim:\n"
        '{"label":"positivo|neutro|negativo","confidence":0.0-1.0,"emotions":["..."],"reason":"..."}\n'
        "Mensagem:\n"
        f"{texto.strip()}"
    )


def analisar_sentimento(texto: str, modelo_sentimento: str):
    # Por que: mantemos consistência de qualidade centralizando no modelo.
    try:
        resp = client.chat.completions.create(
            model=modelo_sentimento,
            messages=[
                {"role": "system", "content": "Retorne JSON estrito."},
                {"role": "user", "content": _formatar_prompt_sentimento(texto)},
            ],
            temperature=0.0,
            max_tokens=150,
            top_p=0.0,
        )
        raw = resp.choices[0].message.content.strip()
        data = json.loads(raw)
        label = str(data.get("label", "neutro")).lower()
        if label not in {"positivo", "neutro", "negativo"}:
            label = "neutro"
        conf = float(data.get("confidence", 0.5))
        conf = max(0.0, min(1.0, conf))
        emotions = data.get("emotions", [])
        if not isinstance(emotions, list):
            emotions = [str(emotions)]
        reason = str(data.get("reason", "")).strip()
        return {
            "label": label,
            "confidence": conf,
            "emotions": [str(e) for e in emotions if str(e).strip()],
            "reason": reason,
        }
    except Exception as e:
        return {
            "label": "neutro",
            "confidence": 0.0,
            "emotions": [],
            "reason": f"Falha na análise: {e}",
        }


def _score_from_label(label: str, confidence: float) -> float:
    """
    Converte rótulo + confiança em um score ∈ [-1, 1].
    positivo = +conf; neutro = 0; negativo = -conf
    """
    sgn = 1 if label == "positivo" else (-1 if label == "negativo" else 0)
    try:
        c = float(confidence)
    except Exception:
        c = 0.0
    c = max(0.0, min(1.0, c))
    return round(sgn * c, 3)


# ──────────────────────────────────────────────────────────────
# Tokenização PT-BR (WordCloud + Grafo)
# ──────────────────────────────────────────────────────────────

_PT_STOPWORDS = {
    "a",
    "à",
    "às",
    "ao",
    "aos",
    "as",
    "o",
    "os",
    "um",
    "uma",
    "uns",
    "umas",
    "de",
    "da",
    "do",
    "das",
    "dos",
    "dá",
    "dão",
    "em",
    "no",
    "na",
    "nos",
    "nas",
    "por",
    "para",
    "pra",
    "com",
    "sem",
    "entre",
    "sobre",
    "sob",
    "até",
    "após",
    "que",
    "se",
    "é",
    "ser",
    "são",
    "era",
    "eram",
    "foi",
    "fui",
    "vai",
    "vou",
    "e",
    "ou",
    "mas",
    "como",
    "quando",
    "onde",
    "qual",
    "quais",
    "porque",
    "porquê",
    "já",
    "não",
    "sim",
    "também",
    "mais",
    "menos",
    "muito",
    "muita",
    "muitos",
    "muitas",
    "meu",
    "minha",
    "meus",
    "minhas",
    "seu",
    "sua",
    "seus",
    "suas",
    "depois",
    "antes",
    "este",
    "esta",
    "estes",
    "estas",
    "isso",
    "isto",
    "aquele",
    "aquela",
    "aqueles",
    "aquelas",
    "lhe",
    "lhes",
    "ele",
    "ela",
    "eles",
    "elas",
    "você",
    "vocês",
    "nós",
    "nosso",
    "nossa",
    "nossos",
    "nossas",
}


def tokenize_pt(texto: str):
    # Por que: reduzir ruído, focar termos relevantes para WordCloud/Grafo.
    texto = texto.lower()
    tokens = re.findall(r"[a-zA-ZÀ-ÿ]+", texto)
    tokens = [t for t in tokens if len(t) >= 3 and t not in _PT_STOPWORDS]
    return tokens


def gerar_wordcloud(corpus_text: str, width: int = 450, height: int = 280):
    # Por que: visão rápida dos temas recorrentes.
    if not corpus_text.strip():
        return None, "Digite algo para iniciar a nuvem de palavras."
    if not _WORDCLOUD_AVAILABLE:
        return None, "Pacote 'wordcloud' não encontrado. Instale: pip install wordcloud"
    wc = WordCloud(
        width=width, height=height, background_color="white", collocations=False
    )
    wc.generate(corpus_text)
    img = wc.to_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf, None


# ═══════════════════════════════════════════════════════
# Grafo de Palavras (coocorrências por bigram em cada mensagem)
# ═══════════════════════════════════════════════════════
import networkx as nx
from itertools import combinations


def build_cooc_graph(
    token_sequences, *, window_k: int = -1, min_edge_weight: int = 1
) -> nx.Graph:
    """
    Constrói grafo de coocorrência:
      - window_k = -1  => todos os pares dentro da mesma mensagem (mais denso)
      - window_k = 2..10 => pares dentro de uma janela deslizante de k tokens (mais conservador)
    Filtra arestas com peso < min_edge_weight.
    """
    G = nx.Graph()

    for tokens in token_sequences:
        if not tokens or len(tokens) < 2:
            # ainda conta frequência do nó (para dimensionar)
            for t in tokens:
                G.nodes[t]["count"] = G.nodes.get(t, {}).get("count", 0) + 1
            continue

        # conta nós
        for t in tokens:
            G.nodes[t]["count"] = G.nodes.get(t, {}).get("count", 0) + 1

        # escolhe pares
        if window_k == -1:
            pairs = combinations(tokens, 2)  # todos os pares na msg
        else:
            pairs = (
                (tokens[i], tokens[j])
                for i in range(len(tokens))
                for j in range(i + 1, min(i + window_k, len(tokens)))
            )

        # acumula pesos
        for a, b in pairs:
            if a == b:
                continue
            if G.has_edge(a, b):
                G[a][b]["weight"] = G[a][b].get("weight", 0) + 1
            else:
                G.add_edge(a, b, weight=1)

    # filtra arestas fracas
    to_drop = [
        (u, v)
        for u, v, d in G.edges(data=True)
        if d.get("weight", 0) < int(min_edge_weight)
    ]
    G.remove_edges_from(to_drop)

    return G


def build_word_graph(token_sequences, min_edge_weight: int = 1):
    """
    Constrói um grafo não-direcionado de coocorrências por bigram.
    - Nós: palavras, com atributo 'count' (frequência total).
    - Arestas: pares adjacentes em cada mensagem, com 'weight' (coocorrência).
    """
    if not _GRAPH_AVAILABLE:
        return None

    G = nx.Graph()
    node_counts = Counter()
    edge_counts = Counter()

    for seq in token_sequences:
        node_counts.update(seq)  # conta ocorrências por palavra
        for i in range(len(seq) - 1):
            a, b = seq[i], seq[i + 1]
            if a == b:
                continue
            edge = tuple(sorted((a, b)))
            edge_counts[edge] += 1

    # adiciona nós com atributo de frequência
    for w, c in node_counts.items():
        G.add_node(w, count=int(c))

    # adiciona arestas com peso mínimo
    for (a, b), w in edge_counts.items():
        if w >= max(1, int(min_edge_weight)):
            G.add_edge(a, b, weight=int(w))

    return G


def subgraph_paths_to_target(G, target: str, max_depth: int = 4):
    """
    Extrai subgrafo contendo:
    - o alvo;
    - nós que possuem caminho até o alvo com comprimento <= max_depth.
    """
    if G is None or target not in G:
        return None

    # BFS limitado para coletar nós que alcançam o alvo até max_depth
    visited = {target}
    frontier = {target}
    depth = 0
    while frontier and depth < max_depth:
        next_frontier = set()
        for u in frontier:
            for v in G.neighbors(u):
                if v not in visited:
                    visited.add(v)
                    next_frontier.add(v)
        frontier = next_frontier
        depth += 1

    # cria subgrafo induzido
    return G.subgraph(visited).copy()


def render_graph_pyvis(
    G, highlight_target: str = None, height_px: int = 600, dark_mode: bool = False
):
    """
    Renderiza com PyVis (interativo). Dimensiona nós por frequência (log-scale) e arestas por peso.
    - `highlight_target` recebe cor especial para facilitar leitura.
    """
    if not _GRAPH_AVAILABLE or G is None or len(G) == 0:
        return (
            None,
            "Grafo indisponível (instale: pip install networkx pyvis) ou sem dados.",
        )

    bg = "#0f172a" if dark_mode else "#ffffff"
    fg = "#e5e7eb" if dark_mode else "#333333"
    net = Network(
        height=f"{height_px}px",
        width="100%",
        bgcolor=bg,
        font_color=fg,
        notebook=False,
        directed=False,
    )
    net.barnes_hut(
        gravity=-2000,
        central_gravity=0.3,
        spring_length=160,
        spring_strength=0.01,
        damping=0.9,
    )

    # normalizações de tamanho
    node_counts = nx.get_node_attributes(G, "count")
    if node_counts:
        max_count = max(node_counts.values())
    else:
        max_count = 1

    for node, data in G.nodes(data=True):
        count = int(data.get("count", 1))
        size = 10 + (30 * (count / max_count))
        color_high = "#34d399" if dark_mode else "#10b981"
        color_norm = "#93c5fd" if dark_mode else "#60a5fa"
        color = color_high if node == highlight_target else color_norm
        title = f"{node}<br/>freq: {count}"
        net.add_node(node, label=node, size=size, color=color, title=title)

    for u, v, data in G.edges(data=True):
        w = int(data.get("weight", 1))
        width = 1 + min(10, w)
        title = f"{u} — {v}<br/>coocorrências: {w}"
        net.add_edge(u, v, value=w, width=width, title=title)

    return net.generate_html(), None


def show_grafo_modal():
    """Abre o grafo em tela cheia sem ocupar a área de diálogo.
    Usa st.dialog (ou experimental_dialog). Fallback: abrir em nova aba."""
    html = st.session_state.get("grafo_html", "")
    if not html:
        return

    # ✅ Modal (Streamlit mais novo)
    if hasattr(st, "dialog"):

        @st.dialog("Grafo de Palavras — Tela Cheia")
        def _dlg():
            st_html(html, height=820, scrolling=True)

        _dlg()
        return

    # ✅ Experimental dialog (algumas versões)
    if hasattr(st, "experimental_dialog"):

        @st.experimental_dialog("Grafo de Palavras — Tela Cheia")
        def _dlg():
            st_html(html, height=820, scrolling=True)

        _dlg()
        return

    # ⚠️ Fallback (sem modal): abrir em nova aba (link na sidebar)
    import base64

    data_url = (
        "data:text/html;base64," + base64.b64encode(html.encode("utf-8")).decode()
    )
    st.sidebar.warning("Sua versão do Streamlit não suporta modal. Abra em nova aba:")
    st.sidebar.markdown(
        f'<a href="{data_url}" target="_blank">🧭 Abrir grafo em nova aba</a>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════
# Sidebar (sem controles de modelo/temperatura p/ ganhar espaço)
# ═══════════════════════════════════════════════════════

st.sidebar.title("⚙️ PAINEL DE CONTROLE")

# ═══════════════════════════════════════════════════════
# ─ RAG (Base de Conhecimento) – controles
# ═══════════════════════════════════════════════════════
# if rag_instance:
if rag_instance:
    st.sidebar.write("### 📚 Base de Conhecimento (RAG)")

    col_rag1, col_rag2 = st.sidebar.columns(2)
    with col_rag1:
        st.metric("Documentos", rag_instance.count())
    with col_rag2:
        if "rag_enabled" not in st.session_state:
            st.session_state["rag_enabled"] = True
        st.session_state["rag_enabled"] = st.toggle(
            "Ativar RAG",
            value=st.session_state.get("rag_enabled", True),
            key="rag_toggle"
        )

    # Seletor de caso de uso
    if _RAG_AVAILABLE:
        use_cases = get_active_use_cases()
        use_case_options = {uc["name"]: uc["key"] for uc in use_cases}

        selected_use_case_name = st.sidebar.selectbox(
            "Caso de uso:",
            options=list(use_case_options.keys()),
            help="Filtra a base de conhecimento por contexto"
        )
        selected_use_case_key = use_case_options[selected_use_case_name]

        # Armazena filtro de categoria
        use_case_config = next((uc for uc in use_cases if uc["key"] == selected_use_case_key), None)
        if use_case_config:
            st.session_state["rag_category_filter"] = use_case_config.get("category_filter")

    # Configurações avançadas (expander)
    with st.sidebar.expander("⚙️ Configurações RAG"):
        st.session_state["rag_top_k"] = st.slider(
            "Documentos retornados", 1, 5, 2,
            help="Quantos documentos usar como contexto"
        )
        st.session_state["rag_threshold"] = st.slider(
            "Relevância mínima", 0.0, 1.0, 0.5, 0.1,
            help="Score mínimo para considerar documento relevante"
        )
        st.session_state["rag_show_errors"] = st.checkbox("Mostrar erros", value=False)

    # Mostra último contexto usado
    if st.session_state.get("ultimo_contexto_rag"):
        with st.sidebar.expander("🔍 Contexto usado na última resposta"):
            for doc in st.session_state["ultimo_contexto_rag"]:
                st.caption(f"**{doc['source']}** ({doc['score']:.1%})")
                st.text(doc['text'][:150] + "...")

    # Botão para recarregar base
    col_r1, col_r2 = st.sidebar.columns(2)
    with col_r1:
        if st.button("🔄 Recarregar", width='stretch', key="rag_reload"):
            rag_instance.clear()
            rag_instance.load_documents(RAG_CONFIG.get("knowledge_base_dir"))
            st.success("Base recarregada!")
            st.rerun()
    with col_r2:
        stats = rag_instance.get_stats()
        with st.popover("📊 Stats"):
            st.json(stats)

    st.sidebar.write("---")

# ─ Sentimento – controles mínimos
st.sidebar.write("### 🧠 Análise de Sentimento")
sentimento_habilitado = st.sidebar.toggle(
    "Ativar análise de sentimento",
    value=bool(config.get("sentimento_habilitado", True)),
)
modelo_sentimento = str(config.get("modelo_sentimento", "gpt-4.1-mini"))

# Área dinâmica de exibição do sentimento
sent_container = st.sidebar.container()
sent_container.caption("Última mensagem do usuário")


# — Evolução do Sentimento (linha em tempo real)
st.sidebar.write("### 📈 Evolução do Sentimento")
with st.sidebar.container():
    _hist = st.session_state.get("sentiment_history", [])
    if _hist:
        _scores = [h.get("score", 0.0) for h in _hist]
        st.line_chart(_scores, height=150, width='stretch')
        _last = _hist[-1]
        st.caption(
            f"Mensagens analisadas: {len(_scores)} | Último: {_last.get('label', '?')} ({int(float(_last.get('confidence', 0.0)) * 100)}%)"
        )
    else:
        st.info("Sem dados ainda. Envie uma mensagem para iniciar a série.")


# ─ Nuvem de Palavras
st.sidebar.write("### ☁️ Nuvem de Palavras")
wc_container = st.sidebar.container()

col_wc1, col_wc2 = st.sidebar.columns(2)
with col_wc1:
    if st.button("🗑️ Limpar nuvem", width='stretch'):
        st.session_state["user_corpus_text"] = ""
        st.session_state["user_token_sequences"] = []
        st.rerun()
with col_wc2:
    st.caption("Atualiza ao enviar nova mensagem")

# ─ Grafo de Palavras
st.sidebar.write("### 🔗 Grafo de Palavras")
graph_container = st.sidebar.container()

# Controles do grafo (na lateral) — comentamos "o que faz" conforme pedido:
with graph_container:
    # Seleciona o mínimo de coocorrências exigido por aresta (filtra ruído)
    min_edge_weight = st.slider(
        "Mín. coocorrências (aresta)", 1, 5, 1, help="Filtra arestas fracas"
    )
    # Define a profundidade máxima para caminhos até o alvo (limita subgrafo)
    max_path_depth = st.slider(
        "Profundidade máx. caminho", 1, 8, 4, help="Caminhos até a palavra alvo"
    )
    # Alterna entre ver o grafo completo ou apenas caminhos que chegam ao alvo
    show_paths_only = st.toggle(
        "Mostrar apenas caminhos até a palavra alvo", value=True
    )
    # Modo escuro apenas para o grafo (melhor contraste)
    graph_dark_mode = st.toggle(
        "Modo escuro (grafo)", value=True, help="Apenas afeta o grafo interativo."
    )
    # Espaço para desenhar o grafo após calcularmos dados (abaixo, no pós-input)

st.sidebar.write("---")
st.sidebar.write("### 🛠️ Ações")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Limpar chat", width='stretch'):
        st.session_state["lista_mensagens"] = []
        st.session_state["sentimento_atual"] = None
        st.session_state["user_corpus_text"] = ""
        st.session_state["user_token_sequences"] = []
        st.session_state["sentiment_history"] = []
        st.rerun()
with col2:
    if st.button("Recarregar", width='stretch'):
        st.cache_data.clear()
        st.rerun()

# ═══════════════════════════════════════════════════════
# Estado principal
# ═══════════════════════════════════════════════════════

if "lista_mensagens" not in st.session_state:
    st.session_state["lista_mensagens"] = []
if "sentimento_atual" not in st.session_state:
    st.session_state["sentimento_atual"] = None
if "user_corpus_text" not in st.session_state:
    st.session_state["user_corpus_text"] = ""
if "user_token_sequences" not in st.session_state:
    st.session_state["user_token_sequences"] = []
if "sentiment_history" not in st.session_state:
    st.session_state[
        "sentiment_history"
    ] = []  # histórico de scores por mensagem do usuário# <- sequências de tokens por mensagem (para grafo)

# Render histórico
for msg in st.session_state["lista_mensagens"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])
    elif msg["role"] == "rag_context":
        # Mostra documentos RAG que foram usados nesta resposta
        docs = msg.get("docs", [])
        if docs:
            with st.expander(f"📚 {len(docs)} documento(s) consultado(s) na base de conhecimento", expanded=False):
                for i, doc in enumerate(docs, 1):
                    st.markdown(f"**{i}. {doc['source']}** - Relevância: `{doc['score']:.1%}`")
                    st.info(doc['text'][:300] + ("..." if len(doc['text']) > 300 else ""))
                    if i < len(docs):
                        st.divider()
    elif msg["role"] == "context":
        with st.expander("🔍 Contexto RAG utilizado"):
            st.text(msg["content"])

# Entrada
mensagem_usuario = st.chat_input("💭 Digite sua mensagem aqui...")

# ═══════════════════════════════════════════════════════
# Ao receber mensagem: RAG + Sentimento + WordCloud + Grafo
# ═══════════════════════════════════════════════════════
if mensagem_usuario:
    st.chat_message("user").write(mensagem_usuario)
    st.session_state["lista_mensagens"].append(
        {"role": "user", "content": mensagem_usuario}
    )

    # Atualiza corpus (WordCloud): agrega tokens ao texto global
    tokens = tokenize_pt(mensagem_usuario)
    if tokens:
        st.session_state["user_corpus_text"] += " " + " ".join(tokens)
        # Atualiza sequência de tokens desta mensagem (para grafo)
        st.session_state["user_token_sequences"].append(tokens)

    # Análise de sentimento
    if sentimento_habilitado:
        with st.spinner("🧠 Analisando sentimento..."):
            st.session_state["sentimento_atual"] = analisar_sentimento(
                mensagem_usuario, modelo_sentimento=modelo_sentimento
            )
    # --- acumula score por mensagem do usuário (após obter sentimento) ---
    _data = st.session_state.get("sentimento_atual")
    try:
        idx_user = sum(
            1
            for m in st.session_state.get("lista_mensagens", [])
            if m.get("role") == "user"
        )
    except Exception:
        idx_user = len(st.session_state.get("sentiment_history", [])) + 1
    if _data:
        st.session_state["sentiment_history"].append(
            {
                "idx": idx_user,
                "label": _data.get("label", "neutro"),
                "confidence": float(_data.get("confidence", 0.0)),
                "score": _score_from_label(
                    _data.get("label", "neutro"), float(_data.get("confidence", 0.0))
                ),
            }
        )

    with st.chat_message("assistant"):  # , avatar="🤖"):
        with st.spinner("🤔 Pensando na resposta..."):
            try:
                # Obtém mensagens completas (inclui busca RAG)
                messages = obter_mensagens_completas()
                
                resposta = client.chat.completions.create(
                    model=modelo,
                    messages=messages,
                    temperature=temperatura,
                    max_tokens=max_tokens,
                    top_p=0.9,
                    frequency_penalty=0.1,
                )
                resposta_ia = resposta.choices[0].message.content or ""
                st.write(resposta_ia)

                st.session_state["lista_mensagens"].append(
                    {"role": "assistant", "content": resposta_ia}
                )

                # Salva contexto RAG junto com a mensagem para histórico (se disponível)
                docs_rag = st.session_state.get("ultimo_contexto_rag", [])
                if docs_rag and st.session_state.get("rag_enabled", True):
                    st.session_state["lista_mensagens"].append(
                        {"role": "rag_context", "docs": docs_rag}
                    )

                # opcional: evita efeitos visuais residuais
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro na API: {str(e)}")


# ─ Mostrar grafo na TELA PRINCIPAL quando o toggle estiver ligado
if st.session_state.get("grafo_expand_main") and st.session_state.get("grafo_html"):
    st.markdown("### 🔗 Grafo de Palavras (expandido)")
    st_html(st.session_state["grafo_html"], height=820, scrolling=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("↩️ Recolher para a sidebar", key="grafo_collapse_main"):
            st.session_state["grafo_expand_main"] = False
            st.rerun()
    with c2:
        if st.button("🔎 Tela cheia (modal)", key="grafo_open_full_from_main"):
            st.session_state["grafo_fullscreen"] = True

# ═══════════════════════════════════════════════════════
# Sidebar: Sentimento + WordCloud + Grafo
# ═══════════════════════════════════════════════════════


def _badge(label: str) -> str:
    colors = {"positivo": "#16a34a", "neutro": "#6b7280", "negativo": "#dc2626"}
    color = colors.get(label, "#6b7280")
    return (
        f"<span style='background:{color};color:white;padding:4px 10px;border-radius:999px;"
        f"font-weight:600;font-size:12px;'>{label.upper()}</span>"
    )


with sent_container:
    data = st.session_state.get("sentimento_atual")
    if sentimento_habilitado and data:
        st.markdown(_badge(data["label"]), unsafe_allow_html=True)
        st.metric("Confiança", f"{round(data['confidence'] * 100):d}%")
        if data["emotions"]:
            emotes = " ".join([f"`{e}`" for e in data["emotions"][:6]])
            st.write(f"**Emoções:** {emotes}")
        if data.get("reason"):
            with st.expander("Por que o modelo decidiu isso?"):
                st.write(data["reason"])
    elif sentimento_habilitado:
        st.info("Envie uma mensagem para ver o sentimento aqui.")

with wc_container:
    buf, err = gerar_wordcloud(st.session_state.get("user_corpus_text", ""))
    if err:
        st.info(err)
    elif buf:
        st.image(buf, caption="Nuvem de Palavras do Usuário", width='stretch')
        st.download_button(
            "📥 Baixar PNG",
            data=buf,
            file_name="wordcloud.png",
            mime="image/png",
            width='stretch',
        )

with graph_container:
    # Calcula grafo a partir das sequências do usuário (aplica filtro de aresta)
    G_full = build_word_graph(
        st.session_state.get("user_token_sequences", []),
        min_edge_weight=min_edge_weight,
    )

    if not _GRAPH_AVAILABLE:
        st.info("Para ver o grafo, instale: pip install networkx pyvis")
    elif G_full is None or len(G_full) == 0:
        st.info("Sem dados suficientes para montar o grafo.")
    else:
        # Gera lista de palavras ordenadas por frequência (para o seletor de alvo)
        counts = nx.get_node_attributes(G_full, "count")
        words_sorted = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
        top_words = [w for w, c in words_sorted]
        target = st.selectbox(
            "Palavra alvo (destacar/filtrar caminhos):",
            options=top_words[:200] if top_words else ["(vazio)"],
        )

        # Se mostrar apenas caminhos até o alvo, extrai subgrafo limitado por profundidade
        G_view = G_full
        if show_paths_only and target:
            G_tmp = subgraph_paths_to_target(G_full, target, max_depth=max_path_depth)
            if G_tmp is not None and len(G_tmp) > 0:
                G_view = G_tmp
            else:
                st.info("Não há caminhos dentro da profundidade escolhida.")
                G_view = None

        if G_view is not None and len(G_view) > 0:
            html, gerr = render_graph_pyvis(
                G_view,
                highlight_target=target,
                height_px=520,
                dark_mode=graph_dark_mode,
            )
            st.session_state["grafo_html"] = html
            if gerr:
                st.info(gerr)
            else:
                # Exibe grafo interativo (PyVis) na sidebar
                # Exibe grafo na sidebar (preview)
                # preview do grafo na sidebar
                st.components.v1.html(html, height=540, scrolling=True)

                # botões na sidebar
                col_sb1, col_sb2 = st.sidebar.columns(2)
                with col_sb1:
                    if st.button("🔎 Tela cheia (modal)", key="grafo_open_modal"):
                        show_grafo_modal()  # <-- abre o modal sem usar a área de diálogo
