from sentence_transformers import SentenceTransformer
from typing import List
from src.models import Chunk


class Embedder:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name, cache_folder='./model_cache')
        self.dimension = self.model.get_embedding_dimension()

    def encode(self, texts: List[str], normalize: bool = True) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=normalize,
            show_progress_bar=True
        )
        return embeddings.tolist()

    def embed_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        texts = [chunk.text for chunk in chunks]
        embeddings = self.encode(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        return chunks