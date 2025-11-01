"""
Sistema RAG (Retrieval Augmented Generation) para VOXMAP
Autor: Marcus Loreto
Versão: 1.0

Módulo que fornece capacidades de busca semântica em documentos
para melhorar as respostas do assistente com informações específicas da empresa.
"""

__version__ = "1.0.0"
__author__ = "Marcus Loreto"

# Imports principais para facilitar uso
from .rag_module import QdrantRAG, create_rag_instance
from .rag_config import RAG_CONFIG, USE_CASES, get_active_use_cases, format_rag_context

__all__ = [
    "QdrantRAG",
    "create_rag_instance",
    "RAG_CONFIG",
    "USE_CASES",
    "get_active_use_cases",
    "format_rag_context",
]
