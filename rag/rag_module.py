import os
import glob
from pathlib import Path
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer


class QdrantRAG:
    """
    RAG integrado com Qdrant.

    Funcionalidades principais usadas pelo app_01.py:
    - carregar documentos da pasta ./rag/base_conhecimento
    - indexar no Qdrant (coleção rag_collection)
    - buscar documentos relevantes (retrieve)
    - limpar/recarregar base (clear + load_documents)
    - expor estatísticas (get_stats)
    """

    def __init__(
        self,
        knowledge_base_dir: str = "./rag/base_conhecimento",
        collection_name: str = "rag_collection",
        verbose: bool = True,
    ):
        self.knowledge_base_dir = knowledge_base_dir
        self.collection_name = collection_name
        self.verbose = verbose

        # -------------------------------
        # 🔌 Conexão com Qdrant
        # -------------------------------
        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", 6333))

        if self.verbose:
            print(f"📡 Conectando ao Qdrant em {host}:{port} ...")

        self.client = QdrantClient(host=host, port=port)

        # -------------------------------
        # 🧠 Modelo de embeddings
        # -------------------------------
        model_name = os.getenv(
            "RAG_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
        if self.verbose:
            print(f"🧠 Carregando modelo de embeddings: {model_name}")

        self.embedding_model = SentenceTransformer(model_name, device="cpu")
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # -------------------------------
        # 📚 Carrega e indexa documentos
        # -------------------------------
        self._ensure_collection()
        self.documents = self._load_documents()

        if self.verbose:
            print(f"📁 {len(self.documents)} documentos encontrados.")

        if self.documents:
            self._index_documents()

    # ----------------------------------------------------
    # LEITURA DOS ARQUIVOS DA BASE
    # ----------------------------------------------------
    def _load_documents(self, base_dir: Optional[str] = None) -> List[Dict]:
        """
        Lê todos os .txt da pasta base e retorna lista de dicts:
        [{id, text, source}]
        """
        docs: List[Dict] = []
        base_path = Path(base_dir or self.knowledge_base_dir)

        if not base_path.exists():
            if self.verbose:
                print(f"⚠️ Diretório '{base_path}' não existe. Criando.")
            base_path.mkdir(parents=True, exist_ok=True)
            return []

        for file in glob.glob(str(base_path / "**/*.txt"), recursive=True):
            path = Path(file)
            try:
                with path.open("r", encoding="utf-8") as f:
                    content = f.read().strip()
                if not content:
                    continue

                docs.append(
                    {
                        "id": path.name,
                        "text": content,
                        "source": str(path.relative_to(base_path)),
                    }
                )
            except Exception as e:
                print(f"⚠️ Erro lendo {path}: {e}")

        return docs

    # ----------------------------------------------------
    # COLLECTION NO QDRANT
    # ----------------------------------------------------
    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        names = [c.name for c in collections]

        if self.collection_name not in names:
            if self.verbose:
                print(
                    f"🛠 Criando coleção '{self.collection_name}' "
                    f"(dim={self.embedding_dim}) ..."
                )
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_dim,
                    distance=models.Distance.COSINE,
                ),
            )
        else:
            if self.verbose:
                print(f"✔ Coleção '{self.collection_name}' já existe.")

    # ----------------------------------------------------
    # INDEXAÇÃO
    # ----------------------------------------------------
    def _index_documents(self):
        if not self.documents:
            if self.verbose:
                print("⚠️ Nenhum documento para indexar.")
            return

        if self.verbose:
            print("⚙️ Indexando documentos no Qdrant...")

        vectors = []
        payloads = []
        ids = []

        start_id = self.count() + 1

        for i, doc in enumerate(self.documents):
            emb = self.embedding_model.encode(doc["text"]).tolist()
            vectors.append(emb)
            payloads.append(
                {
                    "id": doc["id"],
                    "text": doc["text"],
                    "source": doc.get("source", doc["id"]),
                    "category": "geral",
                    "file_type": "txt",
                    "chunk_index": 0,
                }
            )
            ids.append(start_id + i)

        self.client.upsert(
            collection_name=self.collection_name,
            points=models.Batch(ids=ids, vectors=vectors, payloads=payloads),
        )

        if self.verbose:
            print(f"✅ {len(vectors)} documentos indexados com sucesso.")

    # ----------------------------------------------------
    # API USADA PELO app_01.py
    # ----------------------------------------------------
    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.5,
        category_filter: Optional[str] = None,  # mantido para compat
    ) -> List[Dict]:
        """
        Método chamado em app_01.py → rag_instance.retrieve(...)
        Retorna lista de documentos com: text, source, category, score.
        """
        query_emb = self.embedding_model.encode(query).tolist()

        # (category_filter não está sendo usado de fato, mas mantemos a assinatura)
        q_filter = None
        if category_filter:
            # só para compat futura; por enquanto ignorado
            pass

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_emb,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=q_filter,
        )

        docs: List[Dict] = []
        for r in results:
            payload = r.payload or {}
            docs.append(
                {
                    "text": payload.get("text", ""),
                    "source": payload.get("source", payload.get("id", "Desconhecido")),
                    "category": payload.get("category", "geral"),
                    "file_type": payload.get("file_type", "txt"),
                    "score": float(r.score),
                    "chunk_index": payload.get("chunk_index", 0),
                }
            )
        return docs

    def count(self) -> int:
        """Usado no app_01.py para mostrar quantidade de documentos."""
        try:
            info = self.client.get_collection(self.collection_name)
            return int(info.points_count or 0)
        except Exception:
            return 0

    def clear(self):
        """Usado no botão '🔄 Recarregar' da sidebar."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._ensure_collection()

    def load_documents(self, dir_path: Optional[str] = None):
        """
        Usado no botão 'Recarregar' da sidebar:
        rag_instance.clear()
        rag_instance.load_documents(RAG_CONFIG.get("knowledge_base_dir"))
        """
        if dir_path:
            self.knowledge_base_dir = dir_path

        self.documents = self._load_documents()
        if self.verbose:
            print(f"📁 Recarregados {len(self.documents)} documentos.")
        if self.documents:
            self._index_documents()

    def get_stats(self) -> Dict:
        """
        Usado em:
            stats = rag_instance.get_stats()
        para mostrar no popover "📊 Stats".
        """
        total = self.count()
        return {
            "collection_name": self.collection_name,
            "total_documents": total,
            "categories": ["geral"],
            "category_counts": {"geral": total},
            "embedding_model": self.embedding_model.__class__.__name__,
            "embedding_dim": self.embedding_dim,
        }

    # ----------------------------------------------------
    # Helpers opcionais
    # ----------------------------------------------------
    def is_empty(self) -> bool:
        return self.count() == 0

    def close(self):
        try:
            if hasattr(self, "client") and self.client:
                self.client.close()
        except Exception:
            pass


# =========================================================
# Factory function usada pelo app_01.py
# =========================================================
def create_rag_instance(
    knowledge_base_dir: str = "./rag/base_conhecimento",
    verbose: bool = True,
) -> Optional[QdrantRAG]:
    try:
        rag = QdrantRAG(
            knowledge_base_dir=knowledge_base_dir,
            collection_name="rag_collection",
            verbose=verbose,
        )
        return rag
    except Exception as e:
        print(f"❌ Erro ao inicializar RAG: {e}")
        return None
