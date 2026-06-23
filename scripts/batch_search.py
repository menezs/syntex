import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings import Embedder
from src.indexer import FAISSIndexer
from src.reranker import Reranker
from src.search import SemanticSearch


def batch_search(chunks_file: str, output_dir: str = None, index_path: str = None, db_path: str = None):
    base_path = Path(__file__).parent.parent
    chunks_file = Path(chunks_file)

    if index_path is None:
        index_path = base_path / "data" / "index" / "faiss.index"
    else:
        index_path = Path(index_path)

    if db_path is None:
        db_path = base_path / "data" / "metadata" / "chunks.db"
    else:
        db_path = Path(db_path)

    if output_dir is None:
        output_dir = base_path / "data" / "results" / chunks_file.stem
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

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

    print(f"\nProcessing {chunks_file.name}...")

    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    search = SemanticSearch(indexer, embedder, reranker, top_k=50, rerank_top_k=20)

    for i, chunk in enumerate(chunks):
        query_text = chunk["text"]
        results = search.search(query_text)

        result_file = output_dir / f"result_{i:03d}.json"

        output_data = {
            "query": query_text,
            "original_references": chunk.get("references", []),
            "results": results
        }

        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(chunks)} chunks")

    print(f"  Completed: {len(chunks)} files saved to {output_dir}")


def main():
    base_path = Path(__file__).parent.parent
    chunks_dir = base_path / "data" / "chunks"

    files = {
        "chatgpt": "ChatGPT_Direito_e_Tecnologia_Regulação_e_IA_references.json",
        "gemini": "Gemini_Direito_e_Tecnologia_Regulação_e_IA_references.json"
    }

    for folder, filename in files.items():
        chunks_file = chunks_dir / filename
        if chunks_file.exists():
            batch_search(str(chunks_file))


if __name__ == "__main__":
    main()
