import faiss
import sqlite3
import pickle
import numpy as np
from pathlib import Path
from typing import List, Optional
from src.models import Chunk


class FAISSIndexer:
    def __init__(self, dimension: int, index_path: str, db_path: str):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.db_path = Path(db_path)
        self.index: Optional[faiss.Index] = None
        self._init_index()
        self._init_db()

    def _init_index(self):
        self.index = faiss.IndexFlatIP(self.dimension)

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY,
                document TEXT NOT NULL,
                section TEXT NOT NULL,
                text TEXT NOT NULL,
                tokens INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def add_chunks(self, chunks: List[Chunk]):
        if not chunks:
            return

        embeddings = np.array([chunk.embedding for chunk in chunks], dtype=np.float32)
        faiss.normalize_L2(embeddings)

        self.index.add(embeddings)

        conn = sqlite3.connect(self.db_path)
        for chunk in chunks:
            conn.execute(
                "INSERT INTO chunks (id, document, section, text, tokens) VALUES (?, ?, ?, ?, ?)",
                (chunk.id, chunk.document, chunk.section, chunk.text, chunk.tokens)
            )
        conn.commit()
        conn.close()

        print(f"Added {len(chunks)} chunks to index (total: {self.index.ntotal})")

    def save(self):
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        print(f"Index saved to {self.index_path}")

    def load(self):
        self.index = faiss.read_index(str(self.index_path))
        print(f"Index loaded with {self.index.ntotal} vectors")

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[int]:
        query = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query)

        distances, indices = self.index.search(query, top_k)
        return indices[0].tolist()

    def get_chunk_by_id(self, chunk_id: int) -> Optional[Chunk]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "SELECT id, document, section, text, tokens FROM chunks WHERE id = ?",
            (chunk_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return Chunk(
                id=row[0],
                document=row[1],
                section=row[2],
                text=row[3],
                tokens=row[4]
            )
        return None