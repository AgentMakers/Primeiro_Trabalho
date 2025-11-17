"""
Módulo RAG (Retrieval Augmented Generation) para VOXMAP
Versão: 1.0

Sistema modular de busca semântica usando Qdrant + Sentence Transformers
Suporta documentos TXT e PDF com processamento automático
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, MatchText
from sentence_transformers import SentenceTransformer
from pathlib import Path
from typing import List, Dict, Optional
import hashlib
import json
import re


class QdrantRAG:
    """
    Sistema RAG completo com Qdrant

    Funcionalidades:
    - Carregamento automático de TXT e PDF
    - Embeddings multilíngue (PT-BR)
    - Busca por similaridade semântica
    - Persistência em disco
    - Filtros por fonte/categoria
    """

    def __init__(
        self,
        knowledge_base_dir: str = "./base_conhecimento",
        collection_name: str = "voxmap_kb",
        persist_path: str = "./qdrant_storage",
        embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2",
        auto_load: bool = True,
        verbose: bool = True
    ):
        """
        Inicializa o sistema RAG

        Args:
            knowledge_base_dir: Pasta com documentos (TXT/PDF)
            collection_name: Nome da coleção no Qdrant
            persist_path: Onde salvar o banco vetorial
            embedding_model: Modelo de embeddings (multilíngue por padrão)
            auto_load: Se True, carrega documentos automaticamente
            verbose: Se True, mostra logs detalhados
        """
        self.knowledge_base_dir = knowledge_base_dir
        self.collection_name = collection_name
        self.verbose = verbose

        # Inicializa cliente Qdrant (persistente em disco)
        if self.verbose:
            print("🔧 Inicializando Qdrant...")
        # self.client = QdrantClient(path=persist_path) - modo arquivo local
        self.client = QdrantClient(host="localhost", port=6333) # - modo servidor Docker

        # Carrega modelo de embeddings
        if self.verbose:
            print(f"🧠 Carregando modelo de embeddings: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()

        # Cria coleção se não existir
        self._initialize_collection()

        # Carrega documentos automaticamente se solicitado
        if auto_load:
            if self.is_empty():
                if self.verbose:
                    print("📚 Base de conhecimento vazia. Carregando documentos...")
                self.load_documents(self.knowledge_base_dir)
            else:
                if self.verbose:
                    print(f"✅ Base de conhecimento carregada: {self.count()} documentos")

    def __del__(self):
        """Cleanup do cliente Qdrant"""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
        except Exception:
            # Ignora erros de cleanup (comum com Qdrant local)
            pass

    def _initialize_collection(self):
        """Cria a coleção no Qdrant se não existir"""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)

            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                if self.verbose:
                    print(f"✅ Coleção '{self.collection_name}' criada")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Erro ao inicializar coleção: {e}")
            raise

    def _split_text(
        self,
        text: str,
        chunk_size: int = 50,
        overlap: int = 10
    ) -> List[str]:
        """
        Divide texto em chunks com overlap

        Args:
            text: Texto para dividir
            chunk_size: Tamanho aproximado (em palavras)
            overlap: Overlap entre chunks (em palavras)

        Returns:
            Lista de chunks
        """
        words = text.split()
        chunks = []

        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk = ' '.join(chunk_words)

            if len(chunk.strip()) > 0:
                chunks.append(chunk.strip())

            i += chunk_size - overlap

        return chunks if chunks else [text.strip()]

    def _load_txt(self, file_path: Path) -> str:
        """Carrega arquivo TXT"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _load_pdf(self, file_path: Path) -> str:
        """
        Carrega arquivo PDF usando PyPDF2
        Fallback para leitura básica se PyPDF2 não estiver disponível
        """
        try:
            import PyPDF2

            text = []
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

            return '\n\n'.join(text)

        except ImportError:
            if self.verbose:
                print(f"⚠️  PyPDF2 não instalado. Instale: pip install PyPDF2")
            return ""
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Erro ao ler PDF {file_path.name}: {e}")
            return ""

    def load_documents(
        self,
        dir_path: str,
        chunk_size: int = 500,  # <-- Usado apenas para PDFs
        file_types: List[str] = None
    ):
        """
        Carrega documentos de uma pasta

        Args:
            dir_path: Caminho da pasta
            chunk_size: Tamanho dos chunks (usado para PDFs)
            file_types: Lista de extensões (ex: ['.txt', '.pdf'])
        """
        if file_types is None:
            file_types = ['.txt', '.pdf']

        path = Path(dir_path)
        if not path.exists():
            if self.verbose:
                print(f"⚠️  Pasta '{dir_path}' não encontrada. Criando...")
            path.mkdir(parents=True, exist_ok=True)
            return

        points = []
        doc_count = self.count()  # ID inicial
        files_processed = 0

        # Processa cada tipo de arquivo
        for file_type in file_types:
            for file in path.glob(f"**/*{file_type}"):
                try:
                    chunks = []
                    content = ""

                    # Determina categoria pela estrutura de pastas
                    category = file.parent.name if file.parent.name != path.name else "geral"

<<<<<<< Updated upstream
=======
#                     # Carrega conteúdo baseado na extensão
#                     if file_type == '.txt':
#                         content = self._load_txt(file)
#                         if not content or len(content.strip()) < 20: # Reduzido para 20
#                             if self.verbose:
#                                 print(f"  ⊘ {file.name}: vazio ou muito curto, ignorado")
#                             continue

#                         # --- LÓGICA DE CHUNKING SEMÂNTICO PARA TXT ---
#                         # Usamos '---' como separador, baseado na estrutura do seu documento
#                         chunks_raw = content.split('PROBLEMA:')
#                         # Limpa os chunks: remove espaços em branco no início/fim
#                         chunks = [chunk.strip() for chunk in chunks_raw if chunk.strip()]
#                         # Filtra chunks que são muito pequenos (ex: menos de 10 palavras)
#                         chunks = [chunk for chunk in chunks if len(chunk.split()) > 10]
#                         # --- FIM DA NOVA LÓGICA ---
#                     import re
# # ... (O restante do seu rag_module.py)

# ... (Dentro da função load_documents, no bloco if file_type == '.txt':)
>>>>>>> Stashed changes
                    if file_type == '.txt':
                        content = self._load_txt(file)
                        if not content or len(content.strip()) < 20:
                            if self.verbose:
                                print(f"  ⊘ {file.name}: vazio ou muito curto, ignorado")
                            continue

                        # --- LÓGICA DE CHUNKING SEMÂNTICO APRIMORADO PARA TXT ---
                        
                        # Define os padrões de separação:
                        # 1. '===' seguido de texto e '===' (ex: === PROBLEMAS DE REDE ===)
                        # 2. 'PROBLEMA:' (ex: PROBLEMA: Computador não liga)
                        # 3. '---' (linha divisória)
                        # Usamos '(?=...)' (lookahead) para *manter* o separador no início do chunk.
                        # Ex: 'PROBLEMA: ' será o início do chunk, mantendo o contexto.
                        
                        split_pattern = r'(?=^=== [^=]+ ===|^PROBLEMA:|^---)'
                        
                        # Dividir o texto usando a regex (re.split)
                        # re.MULTILINE (m) garante que o '^' capture o início de cada linha, não só do arquivo
                        chunks_raw = re.split(split_pattern, content, flags=re.MULTILINE)

                        # Adicionar o separador 'PROBLEMA:' e '===' de volta aos chunks que o perderam
                        
                        # Limpa os chunks: remove espaços em branco no início/fim e remove vazios
                        chunks = [chunk.strip() for chunk in chunks_raw if chunk.strip()]
                        
                        # Filtra chunks que são muito pequenos (ex: menos de 10 palavras)
                        chunks = [chunk for chunk in chunks if len(chunk.split()) > 10]
                        
                        # --- FIM DA NOVA LÓGICA ---

                    elif file_type == '.pdf':
                        content = self._load_pdf(file)
                        if not content or len(content.strip()) < 50:
                            if self.verbose:
                                print(f"  ⊘ {file.name}: vazio ou muito curto, ignorado")
                            continue
                        
                        # --- LÓGICA DIFERENTE PARA PDFS ---
                        # PDFs não têm '---', então usamos o split por tamanho
                        chunks = self._split_text(content, chunk_size=chunk_size)
                        # --- FIM DA LÓGICA ANTIGA ---

                    else:
                        continue
                    
                    if not chunks:
                        if self.verbose:
                            print(f"  ⊘ {file.name}: não produziu chunks, ignorado")
                        continue

                    # Gera embeddings e cria pontos
                    for i, chunk in enumerate(chunks):
                        embedding = self.embedding_model.encode(chunk).tolist()

                        point = PointStruct(
                            id=doc_count,
                            vector=embedding,
                            payload={
                                "text": chunk,
                                "source": file.name,
                                "file_path": str(file.relative_to(path)),
                                "category": category,
                                "file_type": file_type,
                                "chunk_index": i,
                                "total_chunks": len(chunks)
                            }
                        )
                        points.append(point)
                        doc_count += 1

                    files_processed += 1
                    if self.verbose:
                        print(f"  ✓ {file.name}: {len(chunks)} chunks ({category})")

                except Exception as e:
                    if self.verbose:
                        print(f"  ✗ Erro ao processar {file.name}: {e}")

        # Insere todos os pontos (batch upsert)
        if points:
            batch_size = 100
            for i in range(0, len(points), batch_size):
                batch = points[i:i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch
                )

            if self.verbose:
                print(f"✅ {files_processed} arquivos indexados ({len(points)} chunks)")
        else:
            if self.verbose:
                print("⚠️  Nenhum documento válido encontrado")

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        score_threshold: float = 0.5,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """
        Busca documentos relevantes

        Args:
            query: Texto de busca
            top_k: Número de documentos a retornar
            score_threshold: Score mínimo (0-1)
            category_filter: Filtrar por categoria específica

        Returns:
            Lista de documentos com texto, fonte, score, etc.
        """
        try:
            # Gera embedding da query
            query_embedding = self.embedding_model.encode(query).tolist()

            # Prepara filtro se necessário
            query_filter = None
            if category_filter:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key="category",
                            match=MatchValue(value=category_filter)
                        )
                    ]
                )

            # Busca no Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter
            )

            # Formata resultados
            documents = []
            for result in results:
                documents.append({
                    "text": result.payload["text"],
                    "source": result.payload["source"],
                    "category": result.payload.get("category", "geral"),
                    "file_type": result.payload.get("file_type", "txt"),
                    "score": round(result.score, 4),
                    "chunk_index": result.payload.get("chunk_index", 0)
                })

            return documents

        except Exception as e:
            if self.verbose:
                print(f"⚠️  Erro na busca: {e}")
            return []
########################################################

    def get_categories(self) -> List[str]:
        """Retorna todas as categorias disponíveis"""
        try:
            # Scroll por todos os pontos e coleta categorias únicas
            categories = set()
            offset = None

            while True:
                records, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                for record in records:
                    cat = record.payload.get("category", "geral")
                    categories.add(cat)

                if offset is None:
                    break

            return sorted(list(categories))

        except Exception:
            return []

    def is_empty(self) -> bool:
        """Verifica se a coleção está vazia"""
        return self.count() == 0

    def count(self) -> int:
        """Retorna número de documentos"""
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception:
            return 0

    def clear(self):
        """Limpa toda a coleção"""
        try:
            self.client.delete_collection(self.collection_name)
            self._initialize_collection()
            if self.verbose:
                print("🗑️  Base de conhecimento limpa")
        except Exception as e:
            if self.verbose:
                print(f"⚠️  Erro ao limpar: {e}")

    def add_text(
        self,
        text: str,
        source: str = "manual",
        category: str = "geral",
        chunk_size: int = 500
    ):
        """
        Adiciona texto manualmente

        Args:
            text: Conteúdo
            source: Nome da fonte
            category: Categoria do documento
            chunk_size: Tamanho dos chunks
        """
        chunks = self._split_text(text, chunk_size=chunk_size)
        points = []

        current_count = self.count()

        for i, chunk in enumerate(chunks):
            embedding = self.embedding_model.encode(chunk).tolist()

            point = PointStruct(
                id=current_count + i,
                vector=embedding,
                payload={
                    "text": chunk,
                    "source": source,
                    "category": category,
                    "file_type": "manual",
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        if self.verbose:
            print(f"✅ Texto '{source}' adicionado ({len(chunks)} chunks)")

    def get_stats(self) -> Dict:
        """Retorna estatísticas da base de conhecimento"""
        try:
            categories = self.get_categories()

            # Conta documentos por categoria
            category_counts = {}
            for cat in categories:
                results = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter={"must": [{"key": "category", "match": {"value": cat}}]},
                    limit=1,
                    with_payload=False,
                    with_vectors=False
                )
                # Estima baseado no scroll
                category_counts[cat] = len(results[0]) if results else 0

            return {
                "total_documents": self.count(),
                "categories": categories,
                "category_counts": category_counts,
                "embedding_model": self.embedding_model.get_sentence_embedding_dimension(),
                "collection_name": self.collection_name
            }
        except Exception as e:
            return {"error": str(e)}

    def close(self):
        """Fecha explicitamente o cliente Qdrant"""
        try:
            if hasattr(self, 'client') and self.client:
                self.client.close()
                if self.verbose:
                    print("🔒 Cliente Qdrant fechado")
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Erro ao fechar cliente Qdrant: {e}")


def create_rag_instance(
    knowledge_base_dir: str = "./base_conhecimento",
    verbose: bool = True
) -> Optional[QdrantRAG]:
    """
    Factory function para criar instância do RAG com tratamento de erros

    Args:
        knowledge_base_dir: Pasta com documentos
        verbose: Mostrar logs

    Returns:
        Instância do RAG ou None se falhar
    """
    try:
        rag = QdrantRAG(
            knowledge_base_dir=knowledge_base_dir,
            auto_load=True,
            verbose=verbose
        )
        return rag
    except Exception as e:
        if verbose:
            print(f"❌ Erro ao inicializar RAG: {e}")
            print("💡 Certifique-se de instalar: pip install qdrant-client sentence-transformers PyPDF2")
        return None
