import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.embeddings import Embedder
from src.indexer import FAISSIndexer
from src.search import SemanticSearch


def main():
    base_path = Path(__file__).parent.parent
    chunks_dir = base_path / "data" / "chunks"
    results_base = base_path / "data" / "results"

    index_path = base_path / "data" / "index" / "faiss.index"
    db_path = base_path / "data" / "metadata" / "chunks.db"

    print("Loading index...")
    embedder = Embedder("BAAI/bge-m3")
    indexer = FAISSIndexer(
        dimension=embedder.dimension,
        index_path=str(index_path),
        db_path=str(db_path)
    )
    indexer.load()

    files = {
        "chatgpt": "ChatGPT_Direito_e_Tecnologia_Regulação_e_IA_references.json",
        "gemini": "Gemini_Direito_e_Tecnologia_Regulação_e_IA_references.json"
    }

    for folder, filename in files.items():
        chunks_file = chunks_dir / filename
        output_dir = results_base / folder
        output_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nProcessing {filename}...")

        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        search = SemanticSearch(indexer, embedder, top_k=20)

        for i, chunk in enumerate(chunks):
            query_text = chunk["text"]
            results = search.search(query_text)

            output_file = output_dir / f"result_{i:03d}.json"

            output_data = {
                "query": query_text,
                "original_references": chunk.get("references", []),
                "results": results
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(chunks)} chunks")

        print(f"  Completed: {len(chunks)} files saved to {output_dir}")


if __name__ == "__main__":
    main()