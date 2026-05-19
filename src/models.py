from dataclasses import dataclass
from typing import Optional


@dataclass
class Chunk:
    id: int
    document: str
    section: str
    text: str
    tokens: int
    chunk_index: int = 0
    embedding: Optional[list] = None


@dataclass
class Document:
    path: str
    filename: str
    content: str
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}