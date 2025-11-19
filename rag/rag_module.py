import os
import glob
import json
from pathlib import Path
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer


class QdrantRAG:
    """
    RAG integrado com Qdrant — versão corrigida.
    """

    def __init__(
        self,
        knowledge_base_dir: str = "./rag/base_conhecimento",
        collection_name: str = "rag_collection",
        verbose: bool = True
    ):
        self.knowledge_base_dir = knowledge_base_dir
        self.collection_name = collection_name
        self.verbose = verbose

        # -------------------------------
        # 🔌 Conexão dinâmica com Qdrant
        # -------------------------------

        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", 6333))

        if self.verbose:
            print(f"📡 Conectando ao Qdrant em {host}:{port} ...")

        self.client = QdrantClient(host=host, port=port)

        # -------------------------------
        # 🧠 Carregar modelo de embeddings
        # -------------------------------
        if self.verbose:
            print("🧠 Carregando modelo de embeddings...")

        model_name = os.getenv("RAG_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(model_name, device="cpu")

        # -------------------------------
        # 📚 Carrega documentos e indexa
        # -------------------------------
        if self.verbose:
            print("📚 Lendo documentos da base...")

        self.documents = self._load_documents()

        if self.verbose:
            print(f"📁 {len(self.documents)} documentos encontrados.")

        if len(self.documents) > 0:
            self._ensure_collection()
            self._index_documents()

    # ----------------------------------------------------
    # LEITURA DOS ARQUIVOS DA BASE DE CONHECIMENTO
    # ----------------------------------------------------
    def _load_documents(self) -> List[Dict]:
        docs = []
        base = Path(self.knowledge_base_dir)

        if not base.exists():
            print(f"⚠️ Diretório '{self.knowledge_base_dir}' não existe.")
            return []

        for file in glob.glob(str(base / "**/*.txt"), recursive=True):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        docs.append({"id": Path(file).name, "text": content})
            except Exception as e:
                print(f"Erro lendo {file}: {e}")

        return docs

    # ----------------------------------------------------
    # VERIFICA / CRIA COLLECTION NO QDRANT
    # ----------------------------------------------------
    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        existing = [c.name for c in collections]

        if self.collection_name not in existing:
            if self.verbose:
                print(f"🛠 Criando coleção '{self.collection_name}' ...")

            vector_size = self.embedding_model.get_sentence_embedding_dimension()

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
        else:
            if self.verbose:
                print(f"✔ Coleção '{self.collection_name}' já existe.")

    # ----------------------------------------------------
    # INDEXAÇÃO DOS DOCUMENTOS
    # ----------------------------------------------------
    def _index_documents(self):
        if self.verbose:
            print("⚙️ Indexando documentos no Qdrant...")

        payloads = []
        vectors = []

        for doc in self.documents:
            emb = self.embedding_model.encode(doc["text"]).tolist()
            vectors.append(emb)
            payloads.append({"id": doc["id"], "text": doc["text"]})

        ids = list(range(1, len(vectors) + 1))

        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads
            )
        )

        if self.verbose:
            print(f"✅ {len(vectors)} documentos indexados com sucesso.")

    # ----------------------------------------------------
    # CONSULTA RAG
    # ----------------------------------------------------
    def query(self, query_text: str, limit: int = 3):
        emb = self.embedding_model.encode(query_text).tolist()

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=emb,
            limit=limit
        )

        return [
            {
                "score": r.score,
                "text": r.payload.get("text", "")
            }
            for r in results
        ]

    # ----------------------------------------------------
    # CONTAGEM DE DOCUMENTOS
    # ----------------------------------------------------
    def count(self) -> int:
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count or 0
        except Exception:
            return 0


# =========================================================
# 🔥 FACTORY FUNCTION — ESSENCIAL PARA O app_01.py
# =========================================================
def create_rag_instance(
    knowledge_base_dir: str = "./rag/base_conhecimento",
    verbose: bool = True
):
    """
    Função utilizada pelo app_01.py
    Retorna uma instância funcional de QdrantRAG
    ou None se falhar.
    """
    try:
        rag = QdrantRAG(
            knowledge_base_dir=knowledge_base_dir,
            verbose=verbose
        )
        return rag
    except Exception as e:
        print(f"❌ Erro ao inicializar RAG: {e}")
        return None
