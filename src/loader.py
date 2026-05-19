import os
from pathlib import Path
from typing import List
from src.models import Document


class MarkdownLoader:
    def __init__(self, documents_dir: str):
        self.documents_dir = Path(documents_dir)

    def load(self) -> List[Document]:
        documents = []

        if not self.documents_dir.exists():
            raise FileNotFoundError(f"Directory not found: {self.documents_dir}")

        for filepath in self.documents_dir.glob("*.md"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            doc = Document(
                path=str(filepath),
                filename=filepath.name,
                content=content,
                metadata={"path": str(filepath)}
            )
            documents.append(doc)

        return documents