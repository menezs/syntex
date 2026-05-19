import re
from typing import List, Tuple
from src.models import Document, Chunk
from semantic_text_splitter import TextSplitter


class SemanticChunker:
    def __init__(self, tokenizer, max_tokens: int = 512, overlap: int = 50):
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.splitter = TextSplitter(capacity=max_tokens)

    def parse_markdown_sections(self, content: str) -> List[Tuple[str, str]]:
        lines = content.split("\n")
        sections = []
        current_section = "Root"
        current_content = []

        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

        for line in lines:
            match = heading_pattern.match(line)
            if match:
                if current_content:
                    sections.append((current_section, "\n".join(current_content)))
                current_section = match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append((current_section, "\n".join(current_content)))

        return sections

    def chunk_document(self, doc: Document, start_id: int = 0) -> List[Chunk]:
        chunks = []
        chunk_id = start_id

        sections = self.parse_markdown_sections(doc.content)

        for section_title, section_content in sections:
            section_content = section_content.strip()
            if not section_content:
                continue

            texts = self.splitter.chunks(section_content)

            for idx, text in enumerate(texts):
                tokens = len(self.tokenizer.encode(text))

                chunk = Chunk(
                    id=chunk_id,
                    document=doc.filename,
                    section=section_title,
                    chunk_index=idx,
                    text=text.strip(),
                    tokens=tokens
                )
                chunks.append(chunk)
                chunk_id += 1

        return chunks