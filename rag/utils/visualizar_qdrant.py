"""
Script para visualizar dados do Qdrant (modo arquivo)
Útil quando não tem acesso ao dashboard web
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    import json
    from collections import Counter
except ImportError as e:
    print(f"❌ Erro: {e}")
    print("\n📦 Instale as dependências:")
    print("pip install qdrant-client")
    sys.exit(1)


def visualizar_qdrant(persist_path="./rag/qdrant_storage", collection_name="knowledge_base"):
    """Visualiza dados do Qdrant em modo arquivo"""

    print("=" * 70)
    print("🔍 VISUALIZADOR QDRANT - Modo Arquivo")
    print("=" * 70)
    print()

    # Conectar ao Qdrant
    try:
        client = QdrantClient(path=persist_path)
        print(f"✅ Conectado ao Qdrant: {persist_path}")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return

    print()

    # Listar coleções
    try:
        collections = client.get_collections().collections
        print(f"📚 Coleções disponíveis: {len(collections)}")
        for col in collections:
            print(f"   - {col.name}")
        print()
    except Exception as e:
        print(f"❌ Erro ao listar coleções: {e}")
        return

    # Verificar se a coleção existe
    try:
        collection_info = client.get_collection(collection_name)
        print(f"📊 Informações da coleção '{collection_name}':")
        print(f"   - Vetores: {collection_info.points_count}")
        print(f"   - Dimensões: {collection_info.config.params.vectors.size}")
        print(f"   - Distância: {collection_info.config.params.vectors.distance}")
        print()
    except Exception as e:
        print(f"❌ Coleção '{collection_name}' não encontrada: {e}")
        return

    # Buscar alguns pontos
    try:
        # Scroll para pegar os primeiros pontos
        points, next_offset = client.scroll(
            collection_name=collection_name,
            limit=10,
            with_payload=True,
            with_vectors=False
        )

        print(f"📄 Primeiros {len(points)} documentos:")
        print("-" * 70)

        # Estatísticas
        sources = []
        categories = []

        for i, point in enumerate(points, 1):
            payload = point.payload
            source = payload.get('source', 'N/A')
            category = payload.get('category', 'N/A')
            text = payload.get('text', 'N/A')
            chunk_idx = payload.get('chunk_index', 'N/A')

            sources.append(source)
            categories.append(category)

            print(f"\n{i}. ID: {point.id}")
            print(f"   📁 Fonte: {source}")
            print(f"   🏷️  Categoria: {category}")
            print(f"   📑 Chunk: {chunk_idx}")
            print(f"   📝 Texto (preview): {text[:150]}...")

        print()
        print("-" * 70)

        # Estatísticas gerais
        print("\n📊 Estatísticas:")

        # Contar por fonte
        source_counts = Counter(sources)
        print(f"\n   Documentos por fonte:")
        for source, count in source_counts.most_common():
            print(f"      - {source}: {count} chunks")

        # Contar por categoria
        category_counts = Counter(categories)
        print(f"\n   Documentos por categoria:")
        for category, count in category_counts.most_common():
            print(f"      - {category}: {count} chunks")

        print()

    except Exception as e:
        print(f"❌ Erro ao buscar pontos: {e}")
        return

    # Menu interativo
    print("=" * 70)
    print("\n🔍 Opções de consulta:")
    print("   1. Buscar por texto")
    print("   2. Ver estatísticas completas")
    print("   3. Exportar para JSON")
    print("   4. Sair")
    print()

    while True:
        try:
            opcao = input("Escolha uma opção (1-4): ").strip()

            if opcao == "1":
                buscar_por_texto(client, collection_name)
            elif opcao == "2":
                estatisticas_completas(client, collection_name)
            elif opcao == "3":
                exportar_json(client, collection_name)
            elif opcao == "4":
                print("\n👋 Até logo!")
                break
            else:
                print("❌ Opção inválida. Escolha 1-4.")
        except KeyboardInterrupt:
            print("\n\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")


def buscar_por_texto(client, collection_name):
    """Busca semântica por texto"""
    from sentence_transformers import SentenceTransformer

    print("\n" + "=" * 70)
    query = input("🔍 Digite o texto para buscar: ").strip()

    if not query:
        print("❌ Texto vazio.")
        return

    try:
        # Carregar modelo de embeddings
        print("📥 Carregando modelo de embeddings...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

        # Gerar embedding da query
        query_vector = model.encode(query).tolist()

        # Buscar documentos similares
        print("🔎 Buscando documentos similares...\n")
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=5
        )

        print(f"📄 {len(results)} resultados encontrados:")
        print("-" * 70)

        for i, result in enumerate(results, 1):
            payload = result.payload
            score = result.score

            print(f"\n{i}. Score: {score:.2%}")
            print(f"   📁 Fonte: {payload.get('source', 'N/A')}")
            print(f"   🏷️  Categoria: {payload.get('category', 'N/A')}")
            print(f"   📝 Texto: {payload.get('text', 'N/A')[:200]}...")

        print("\n" + "-" * 70)

    except Exception as e:
        print(f"❌ Erro na busca: {e}")


def estatisticas_completas(client, collection_name):
    """Mostra estatísticas completas da coleção"""
    print("\n" + "=" * 70)
    print("📊 ESTATÍSTICAS COMPLETAS")
    print("=" * 70)

    try:
        # Pegar todos os pontos (com limite de segurança)
        all_points = []
        offset = None
        max_points = 10000  # Limite de segurança

        print("📥 Carregando dados...")

        while len(all_points) < max_points:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            if not points:
                break

            all_points.extend(points)
            offset = next_offset

            if next_offset is None:
                break

        print(f"✅ {len(all_points)} documentos carregados\n")

        # Estatísticas por fonte
        sources = Counter()
        categories = Counter()
        text_lengths = []

        for point in all_points:
            payload = point.payload
            sources[payload.get('source', 'N/A')] += 1
            categories[payload.get('category', 'N/A')] += 1
            text_lengths.append(len(payload.get('text', '')))

        print("📁 Documentos por fonte:")
        for source, count in sources.most_common():
            pct = (count / len(all_points)) * 100
            print(f"   {source}: {count} ({pct:.1f}%)")

        print(f"\n🏷️  Documentos por categoria:")
        for category, count in categories.most_common():
            pct = (count / len(all_points)) * 100
            print(f"   {category}: {count} ({pct:.1f}%)")

        print(f"\n📏 Tamanho dos textos:")
        print(f"   Média: {sum(text_lengths) / len(text_lengths):.0f} caracteres")
        print(f"   Mínimo: {min(text_lengths)} caracteres")
        print(f"   Máximo: {max(text_lengths)} caracteres")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"❌ Erro ao calcular estatísticas: {e}")


def exportar_json(client, collection_name):
    """Exporta dados para JSON"""
    print("\n" + "=" * 70)
    output_file = input("📁 Nome do arquivo de saída (ex: dados.json): ").strip()

    if not output_file:
        output_file = "qdrant_export.json"

    if not output_file.endswith('.json'):
        output_file += '.json'

    try:
        # Pegar todos os pontos
        all_points = []
        offset = None

        print("📥 Carregando dados...")

        while True:
            points, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            if not points:
                break

            all_points.extend(points)
            offset = next_offset

            if next_offset is None:
                break

        # Converter para formato JSON
        data = []
        for point in all_points:
            data.append({
                "id": point.id,
                "payload": point.payload
            })

        # Salvar JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ {len(data)} documentos exportados para: {output_file}")
        print(f"📊 Tamanho do arquivo: {os.path.getsize(output_file) / 1024:.1f} KB")

    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")


if __name__ == "__main__":
    # Configurar encoding UTF-8 no Windows
    if sys.platform == "win32":
        os.system("chcp 65001 > nul 2>&1")
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    # Caminho padrão
    persist_path = "./rag/qdrant_storage"

    # Aceitar caminho como argumento
    if len(sys.argv) > 1:
        persist_path = sys.argv[1]

    visualizar_qdrant(persist_path)
