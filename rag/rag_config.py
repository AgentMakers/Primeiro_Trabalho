"""
Configurações do sistema RAG para VOXMAP
"""

import os

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÕES GERAIS
# ═══════════════════════════════════════════════════════

RAG_CONFIG = {
    # Habilitar/desabilitar RAG globalmente
    "enabled": True,

    # Pastas
    "knowledge_base_dir": "./rag/base_conhecimento",
    "persist_path": "./rag/qdrant_storage",

    # Coleção Qdrant
    "collection_name": "voxmap_kb",

    # Modelo de embeddings (multilíngue PT-BR)
    # Opções:
    # - "paraphrase-multilingual-MiniLM-L12-v2" (recomendado, rápido)
    # - "paraphrase-multilingual-mpnet-base-v2" (mais preciso, mais lento)
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2",

    # Processamento de texto
    "chunk_size": 500,  # Tamanho dos chunks em palavras
    "chunk_overlap": 50,  # Overlap entre chunks

    # Busca
    "default_top_k": 3,  # Número de documentos retornados
    "score_threshold": 0.5,  # Score mínimo (0-1)

    # UI
    "show_sources": True,  # Mostrar fontes na UI
    "show_scores": True,  # Mostrar scores de relevância
    "verbose": True,  # Logs detalhados no console
}

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÕES POR CASO DE USO
# ═══════════════════════════════════════════════════════

USE_CASES = {
    "suporte_tecnico": {
        "name": "Suporte Técnico TI",
        "description": "Assistente para suporte técnico de TI",
        "category_filter": "suporte_tecnico",
        "system_prompt_addon": """

[CONTEXTO: Suporte Técnico]
Você está auxiliando com questões técnicas de TI.
Use a base de conhecimento para fornecer soluções precisas.
Sempre cite os documentos usados como referência.
        """,
        "enabled": True
    },

    "relacionamento_cliente": {
        "name": "Relacionamento com Cliente",
        "description": "Assistente para atendimento e relacionamento",
        "category_filter": "relacionamento",
        "system_prompt_addon": """

[CONTEXTO: Relacionamento com Cliente]
Você está auxiliando no atendimento ao cliente.
Foque em resolver problemas com empatia e eficiência.
Siga as políticas da empresa disponíveis na base de conhecimento.
        """,
        "enabled": True
    },

    "geral": {
        "name": "Atendimento Geral",
        "description": "Assistente geral sem filtro de categoria",
        "category_filter": None,
        "system_prompt_addon": "",
        "enabled": True
    }
}

# ═══════════════════════════════════════════════════════
# CONFIGURAÇÕES DE INTEGRAÇÃO
# ═══════════════════════════════════════════════════════

INTEGRATION_CONFIG = {
    # Quantas mensagens do histórico usar para contexto
    "history_messages_for_context": 3,

    # Modo de injeção de contexto
    # "system" = adiciona ao system prompt
    # "user" = adiciona como mensagem do usuário
    # "context" = mensagem separada (role="context")
    "injection_mode": "system",

    # Template de formatação do contexto
    "context_template": """

[INFORMAÇÕES DA BASE DE CONHECIMENTO]:
{context}

Use estas informações para fundamentar sua resposta quando relevante.
""",

    # Template para cada documento
    "document_template": """
📄 Fonte: {source} | Categoria: {category} | Relevância: {score:.1%}
{text}
---
"""
}

# ═══════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═══════════════════════════════════════════════════════

def get_use_case_config(use_case: str) -> dict:
    """Retorna configuração de um caso de uso específico"""
    return USE_CASES.get(use_case, USE_CASES["geral"])

def get_active_use_cases() -> list:
    """Retorna lista de casos de uso ativos"""
    return [
        {"key": key, **config}
        for key, config in USE_CASES.items()
        if config.get("enabled", True)
    ]

def format_rag_context(documents: list) -> str:
    """Formata documentos recuperados em contexto legível"""
    if not documents:
        return ""

    context_parts = []
    for doc in documents:
        formatted_doc = INTEGRATION_CONFIG["document_template"].format(
            source=doc.get("source", "Desconhecido"),
            category=doc.get("category", "geral"),
            score=doc.get("score", 0.0),
            text=doc.get("text", "")[:500] + ("..." if len(doc.get("text", "")) > 500 else "")
        )
        context_parts.append(formatted_doc)

    context = "\n".join(context_parts)
    return INTEGRATION_CONFIG["context_template"].format(context=context)
