import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings import Embedder
from src.indexer import FAISSIndexer
from src.search import SemanticSearch


def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py \"your search query\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    index_path = Path(__file__).parent.parent / "data" / "index" / "faiss.index"
    db_path = Path(__file__).parent.parent / "data" / "metadata" / "chunks.db"

    print("Loading index...")
    embedder = Embedder("BAAI/bge-m3")
    indexer = FAISSIndexer(
        dimension=embedder.dimension,
        index_path=str(index_path),
        db_path=str(db_path)
    )
    indexer.load()

    print(f"\nSearching for: \"{query}\"\n")

    search = SemanticSearch(indexer, embedder, top_k=5)
    results = search.search(query)

    print("=" * 80)
    for i, result in enumerate(results, 1):
        print(f"\n[Result {i}]")
        print(f"Document: {result['document']}")
        print(f"Section: {result['section']}")
        print(f"Tokens: {result['tokens']}")
        print("-" * 40)
        print(result['text'][:500] + ("..." if len(result['text']) > 500 else ""))
        print("=" * 80)


if __name__ == "__main__":
    main()