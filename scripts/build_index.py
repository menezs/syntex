import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import tiktoken
from src.loader import MarkdownLoader
from src.chunker import SemanticChunker
from src.embeddings import Embedder
from src.indexer import FAISSIndexer


def build_index(documents_dir: str, index_path: str = None, db_path: str = None):
    base_path = Path(__file__).parent.parent

    if index_path is None:
        index_path = base_path / "data" / "index" / "faiss.index"
    else:
        index_path = Path(index_path)

    if db_path is None:
        db_path = base_path / "data" / "metadata" / "chunks.db"
    else:
        db_path = Path(db_path)

    print("Cleaning existing index...")
    if index_path.exists():
        index_path.unlink()
    if db_path.exists():
        db_path.unlink()

    print("Loading documents...")
    loader = MarkdownLoader(documents_dir)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents")

    print("\nInitializing tokenizer...")
    tokenizer = tiktoken.get_encoding("cl100k_base")

    print("\nChunking documents...")
    chunker = SemanticChunker(tokenizer, max_tokens=512, overlap=50)
    all_chunks = []
    chunk_id = 0

    for doc in documents:
        chunks = chunker.chunk_document(doc, start_id=chunk_id)
        all_chunks.extend(chunks)
        chunk_id = len(all_chunks)

    print(f"Created {len(all_chunks)} chunks")

    print("\nGenerating embeddings...")
    embedder = Embedder("BAAI/bge-m3")

    print("\nEmbedding chunks (this may take a while)...")
    all_chunks = embedder.embed_chunks(all_chunks)

    print("\nBuilding FAISS index...")
    indexer = FAISSIndexer(
        dimension=embedder.dimension,
        index_path=str(index_path),
        db_path=str(db_path)
    )

    indexer.add_chunks(all_chunks)
    indexer.save()

    print("\nDone! Index built successfully.")


def main():
    base_path = Path(__file__).parent.parent
    documents_dir = str(base_path / "data" / "documents")
    build_index(documents_dir)


if __name__ == "__main__":
    main()
