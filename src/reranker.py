from typing import List, Dict, Any
from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3"):
        print(f"Loading reranker model: {model_name}...")
        self.model = CrossEncoder(
            model_name,
            max_length=512,
            cache_folder='./model_cache'
        )

    def rerank(self, query: str, results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        if not results:
            return []

        pairs = [[query, r["text"]] for r in results]
        scores = self.model.predict(pairs)

        scored_results = []
        for result, score in zip(results, scores):
            result["score"] = float(score)
            scored_results.append(result)

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]