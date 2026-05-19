from typing import List, Dict, Any, Optional
from src.models import Chunk
from src.embeddings import Embedder
from src.indexer import FAISSIndexer
from src.reranker import Reranker


class SemanticSearch:
    def __init__(
        self,
        indexer: FAISSIndexer,
        embedder: Embedder,
        reranker: Optional[Reranker] = None,
        top_k: int = 10,
        rerank_top_k: int = 5
    ):
        self.indexer = indexer
        self.embedder = embedder
        self.reranker = reranker
        self.top_k = top_k
        self.rerank_top_k = rerank_top_k

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_embedding = self.embedder.encode([query])[0]

        indices = self.indexer.search(query_embedding, top_k=self.top_k)

        results = []
        for idx in indices:
            if idx == -1:
                continue
            chunk = self.indexer.get_chunk_by_id(idx)
            if chunk:
                results.append({
                    "id": chunk.id,
                    "document": chunk.document,
                    "section": chunk.section,
                    "text": chunk.text,
                    "tokens": chunk.tokens
                })

        if self.reranker and len(results) > self.rerank_top_k:
            results = self.reranker.rerank(query, results, self.rerank_top_k)

        return results