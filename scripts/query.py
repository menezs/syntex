import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings import Embedder
from src.indexer import FAISSIndexer
from src.reranker import Reranker
from src.search import SemanticSearch


def query_search(query: str, index_path: str = None, db_path: str = None):
    base_path = Path(__file__).parent.parent

    if index_path is None:
        index_path = base_path / "data" / "index" / "faiss.index"
    else:
        index_path = Path(index_path)

    if db_path is None:
        db_path = base_path / "data" / "metadata" / "chunks.db"
    else:
        db_path = Path(db_path)

    print("Loading index...")
    embedder = Embedder("BAAI/bge-m3")
    indexer = FAISSIndexer(
        dimension=embedder.dimension,
        index_path=str(index_path),
        db_path=str(db_path)
    )
    indexer.load()

    print("Loading reranker...")
    reranker = Reranker()

    print(f"\nSearching for: \"{query}\"\n")

    search = SemanticSearch(indexer, embedder, reranker, top_k=50, rerank_top_k=20)
    results = search.search(query)

    print("=" * 80)
    for i, result in enumerate(results, 1):
        print(f"\n[Result {i}]")
        print(f"Document: {result['document']}")
        print(f"Section: {result['section']}")
        print(f"Tokens: {result['tokens']}")
        print(f"Score: {result.get('score', 'N/A')}")
        print("-" * 40)
        print(result['text'][:500] + ("..." if len(result['text']) > 500 else ""))
        print("=" * 80)

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py \"your search query\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    query_search(query)


if __name__ == "__main__":
    main()
