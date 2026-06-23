import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scripts.build_index import build_index
from scripts.batch_search import batch_search
from scripts.query import query_search
from scripts.process_answers import process_answers
from scripts.json_to_markdown import convert_to_markdown


def cmd_build(args):
    build_index(
        documents_dir=args.docs,
        index_path=args.index,
        db_path=args.db
    )


def cmd_search(args):
    batch_search(
        chunks_file=args.chunks,
        output_dir=args.output,
        index_path=args.index,
        db_path=args.db
    )


def cmd_query(args):
    query_search(
        query=args.query_text,
        index_path=args.index,
        db_path=args.db
    )


def cmd_process(args):
    process_answers(
        answers_dir=args.answers,
        output_dir=args.output
    )


def cmd_convert(args):
    convert_to_markdown(results_dir=args.results)


def cmd_clean(args):
    base_path = Path(__file__).parent

    if args.index:
        index_path = Path(args.index)
    else:
        index_path = base_path / "data" / "index" / "faiss.index"

    if args.db:
        db_path = Path(args.db)
    else:
        db_path = base_path / "data" / "metadata" / "chunks.db"

    files_to_remove = []

    if index_path.exists():
        files_to_remove.append(index_path)

    if db_path.exists():
        files_to_remove.append(db_path)

    if not files_to_remove:
        print("No index files found to clean.")
        return

    if not args.force:
        print("Files to be removed:")
        for f in files_to_remove:
            print(f"  - {f}")
        confirm = input("\nConfirm? (y/N): ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    for f in files_to_remove:
        f.unlink()
        print(f"Removed: {f}")

    print("\nIndex cleaned successfully.")


def main():
    parser = argparse.ArgumentParser(
        prog="syntex",
        description="Sistema de busca semântica para documentos jurídicos"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = subparsers.add_parser("build", help="Construir índice FAISS a partir de documentos")
    p_build.add_argument("--docs", required=True, help="Pasta com documentos .md para indexar")
    p_build.add_argument("--index", help="Caminho do índice FAISS (default: data/index/faiss.index)")
    p_build.add_argument("--db", help="Caminho do banco SQLite (default: data/metadata/chunks.db)")
    p_build.set_defaults(func=cmd_build)

    # search
    p_search = subparsers.add_parser("search", help="Busca em lote usando chunks de referência")
    p_search.add_argument("--chunks", required=True, help="Arquivo JSON com chunks de referência")
    p_search.add_argument("--output", help="Pasta de saída para resultados")
    p_search.add_argument("--index", help="Caminho do índice FAISS")
    p_search.add_argument("--db", help="Caminho do banco SQLite")
    p_search.set_defaults(func=cmd_search)

    # query
    p_query = subparsers.add_parser("query", help="Busca interativa por query")
    p_query.add_argument("query_text", help="Texto da consulta")
    p_query.add_argument("--index", help="Caminho do índice FAISS")
    p_query.add_argument("--db", help="Caminho do banco SQLite")
    p_query.set_defaults(func=cmd_query)

    # process
    p_process = subparsers.add_parser("process", help="Processar respostas (PDF/DOCX/MD) em chunks")
    p_process.add_argument("--answers", required=True, help="Pasta com arquivos PDF, DOCX ou MD")
    p_process.add_argument("--output", help="Pasta de saída para chunks JSON")
    p_process.set_defaults(func=cmd_process)

    # convert
    p_convert = subparsers.add_parser("convert", help="Converter resultados JSON para Markdown")
    p_convert.add_argument("--results", required=True, help="Pasta com resultados JSON")
    p_convert.set_defaults(func=cmd_convert)

    # clean
    p_clean = subparsers.add_parser("clean", help="Limpar índice FAISS e banco SQLite")
    p_clean.add_argument("--index", help="Caminho do índice FAISS")
    p_clean.add_argument("--db", help="Caminho do banco SQLite")
    p_clean.add_argument("-f", "--force", action="store_true", help="Confirmar sem pedir")
    p_clean.set_defaults(func=cmd_clean)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
