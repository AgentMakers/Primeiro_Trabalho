"""
Script de Verificação - Sistema RAG VOXMAP
Execute este script para verificar se tudo está configurado corretamente

Uso: python check_rag_setup.py
"""

import sys
import os
from pathlib import Path

# Configurar encoding para UTF-8 no Windows
if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def check_color(text, status):
    """Adiciona cor ao output"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "end": "\033[0m"
    }

    if status == "ok":
        return f"{colors['green']}✅ {text}{colors['end']}"
    elif status == "error":
        return f"{colors['red']}❌ {text}{colors['end']}"
    elif status == "warning":
        return f"{colors['yellow']}⚠️  {text}{colors['end']}"
    elif status == "info":
        return f"{colors['blue']}ℹ️  {text}{colors['end']}"
    return text


def check_dependencies():
    """Verifica se dependências estão instaladas"""
    print("\n" + "="*60)
    print("📦 VERIFICANDO DEPENDÊNCIAS")
    print("="*60 + "\n")

    dependencies = {
        "streamlit": "Core - Interface web",
        "openai": "Core - API OpenAI",
        "qdrant_client": "RAG - Banco vetorial",
        "sentence_transformers": "RAG - Embeddings",
        "PyPDF2": "RAG - Leitura de PDFs",
        "wordcloud": "Opcional - Nuvem de palavras",
        "networkx": "Opcional - Grafos",
        "pyvis": "Opcional - Visualização de grafos"
    }

    all_ok = True

    for package, description in dependencies.items():
        try:
            __import__(package)
            print(check_color(f"{package:30} - {description}", "ok"))
        except ImportError:
            print(check_color(f"{package:30} - {description}", "error"))
            all_ok = False

    return all_ok


def check_files():
    """Verifica se arquivos necessários existem"""
    print("\n" + "="*60)
    print("📁 VERIFICANDO ARQUIVOS")
    print("="*60 + "\n")

    required_files = {
        "rag/rag_module.py": "Motor RAG",
        "rag/rag_config.py": "Configurações RAG",
        "app_01.py": "Aplicação principal",
        "requirements.txt": "Lista de dependências",
        ".env": "Variáveis de ambiente"
    }

    all_ok = True

    for file, description in required_files.items():
        path = Path(file)
        if path.exists():
            size = path.stat().st_size
            print(check_color(f"{file:30} - {description} ({size} bytes)", "ok"))
        else:
            print(check_color(f"{file:30} - {description}", "error"))
            all_ok = False

    return all_ok


def check_base_conhecimento():
    """Verifica base de conhecimento"""
    print("\n" + "="*60)
    print("📚 VERIFICANDO BASE DE CONHECIMENTO")
    print("="*60 + "\n")

    base_dir = Path("./rag/base_conhecimento")

    if not base_dir.exists():
        print(check_color("Pasta rag/base_conhecimento não existe!", "error"))
        return False

    print(check_color(f"Pasta rag/base_conhecimento existe", "ok"))

    # Conta documentos
    txt_files = list(base_dir.glob("**/*.txt"))
    pdf_files = list(base_dir.glob("**/*.pdf"))

    total_files = len(txt_files) + len(pdf_files)

    print(check_color(f"Arquivos TXT encontrados: {len(txt_files)}", "info"))
    print(check_color(f"Arquivos PDF encontrados: {len(pdf_files)}", "info"))
    print(check_color(f"Total de documentos: {total_files}", "info"))

    if total_files == 0:
        print(check_color("Nenhum documento encontrado!", "warning"))
        return False

    # Lista categorias (pastas)
    categories = set()
    for file in txt_files + pdf_files:
        if file.parent != base_dir:
            categories.add(file.parent.name)

    print(check_color(f"\nCategorias encontradas: {', '.join(categories) if categories else 'nenhuma'}", "info"))

    # Lista arquivos por categoria
    print("\nDetalhamento por categoria:")
    for category in sorted(categories):
        category_path = base_dir / category
        cat_txt = list(category_path.glob("*.txt"))
        cat_pdf = list(category_path.glob("*.pdf"))
        print(f"\n  📁 {category}:")
        for file in cat_txt + cat_pdf:
            size_kb = file.stat().st_size / 1024
            print(f"     └─ {file.name} ({size_kb:.1f} KB)")

    return total_files > 0


def check_env_file():
    """Verifica arquivo .env"""
    print("\n" + "="*60)
    print("🔑 VERIFICANDO VARIÁVEIS DE AMBIENTE")
    print("="*60 + "\n")

    env_path = Path(".env")

    if not env_path.exists():
        print(check_color(".env não encontrado!", "error"))
        print(check_color("Crie um arquivo .env com:", "info"))
        print("""
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4.1-mini
        """)
        return False

    print(check_color(".env encontrado", "ok"))

    # Tenta ler variáveis
    try:
        with open(env_path, 'r') as f:
            content = f.read()

        has_api_key = "OPENAI_API_KEY" in content
        has_model = "OPENAI_MODEL" in content

        if has_api_key:
            print(check_color("OPENAI_API_KEY configurada", "ok"))
        else:
            print(check_color("OPENAI_API_KEY não encontrada no .env", "error"))
            return False

        if has_model:
            print(check_color("OPENAI_MODEL configurada", "ok"))
        else:
            print(check_color("OPENAI_MODEL não encontrada (usará padrão)", "warning"))

        return has_api_key

    except Exception as e:
        print(check_color(f"Erro ao ler .env: {e}", "error"))
        return False


def check_qdrant_storage():
    """Verifica se Qdrant já foi inicializado"""
    print("\n" + "="*60)
    print("💾 VERIFICANDO ARMAZENAMENTO QDRANT")
    print("="*60 + "\n")

    qdrant_path = Path("./rag/qdrant_storage")

    if qdrant_path.exists():
        size = sum(f.stat().st_size for f in qdrant_path.rglob('*') if f.is_file())
        size_mb = size / (1024 * 1024)
        print(check_color(f"rag/qdrant_storage existe ({size_mb:.2f} MB)", "ok"))
        print(check_color("Base de conhecimento já foi indexada", "info"))
        return True
    else:
        print(check_color("qdrant_storage não existe", "warning"))
        print(check_color("Será criado na primeira execução do app (~1-2 minutos)", "info"))
        return True  # Não é erro, apenas aviso


def check_documentation():
    """Verifica documentação"""
    print("\n" + "="*60)
    print("📖 VERIFICANDO DOCUMENTAÇÃO")
    print("="*60 + "\n")

    docs = {
        "rag/docs/RAG_README.md": "Documentação técnica completa",
        "rag/docs/QUICK_START.md": "Guia de início rápido",
        "rag/docs/RESUMO_IMPLEMENTACAO.md": "Resumo da implementação",
        "rag/docs/ESTRUTURA_PROJETO.md": "Estrutura do projeto",
        "rag/docs/TESTES_RAG.md": "Guia de testes"
    }

    for doc, description in docs.items():
        path = Path(doc)
        if path.exists():
            print(check_color(f"{doc:30} - {description}", "ok"))
        else:
            print(check_color(f"{doc:30} - {description}", "warning"))


def test_import_rag():
    """Tenta importar módulos RAG"""
    print("\n" + "="*60)
    print("🧪 TESTANDO IMPORTAÇÃO DOS MÓDULOS RAG")
    print("="*60 + "\n")

    try:
        print("Importando rag.rag_module...")
        from rag import rag_module
        print(check_color("rag.rag_module importado com sucesso", "ok"))

        print("Importando rag.rag_config...")
        from rag import rag_config
        print(check_color("rag.rag_config importado com sucesso", "ok"))

        print("Verificando função create_rag_instance...")
        from rag.rag_module import create_rag_instance
        print(check_color("create_rag_instance disponível", "ok"))

        return True

    except Exception as e:
        print(check_color(f"Erro ao importar módulos: {e}", "error"))
        return False


def print_summary(results):
    """Imprime resumo dos testes"""
    print("\n" + "="*60)
    print("📊 RESUMO DA VERIFICAÇÃO")
    print("="*60 + "\n")

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    print(f"Total de verificações: {total}")
    print(check_color(f"Passaram: {passed}", "ok" if passed == total else "info"))

    if failed > 0:
        print(check_color(f"Falharam: {failed}", "error"))

    print("\nDetalhamento:")
    for check, status in results.items():
        status_str = "✅ OK" if status else "❌ FALHOU"
        print(f"  {check:30} {status_str}")

    print("\n" + "="*60)

    if passed == total:
        print(check_color("🎉 TUDO OK! Sistema pronto para uso!", "ok"))
        print("\nPróximos passos:")
        print("1. Execute: streamlit run app_01.py")
        print("2. Aguarde 1-2 minutos na primeira vez (download do modelo)")
        print("3. Teste com perguntas relacionadas aos documentos")
        print("4. Consulte QUICK_START.md para mais informações")
    else:
        print(check_color("⚠️  ATENÇÃO: Alguns problemas foram encontrados", "warning"))
        print("\nResolva os problemas acima antes de prosseguir.")
        print("Consulte RAG_README.md → Troubleshooting para ajuda.")

    print("="*60 + "\n")


def main():
    """Função principal"""
    print("\n" + "🔍 VERIFICADOR DE SETUP - SISTEMA RAG VOXMAP".center(60))

    results = {}

    # Executa todas as verificações
    results["Dependências"] = check_dependencies()
    results["Arquivos essenciais"] = check_files()
    results["Base de conhecimento"] = check_base_conhecimento()
    results["Variáveis de ambiente"] = check_env_file()
    results["Armazenamento Qdrant"] = check_qdrant_storage()
    results["Documentação"] = check_documentation()
    results["Importação dos módulos"] = test_import_rag()

    # Imprime resumo
    print_summary(results)

    # Código de saída
    if all(results.values()):
        sys.exit(0)  # Sucesso
    else:
        sys.exit(1)  # Falha


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificação interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)
