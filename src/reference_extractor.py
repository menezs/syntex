import re
from typing import List, Dict


class ReferenceExtractor:
    def __init__(self):
        self.pattern_bracket = re.compile(r'\[\s*(\d+)\s*\]')
        self.pattern_sup_html = re.compile(r'<sup>\s*(\d+)\s*</sup>')
        self.pattern_sub_html = re.compile(r'<sub>\s*(\d+)\s*</sub>')
        self.pattern_sup_unicode = re.compile(
            '[\u00B9\u00B2\u00B3\u2070\u2071\u2072\u2073\u2074\u2075'
            '\u2076\u2077\u2078\u2079\u207A\u207B]+'
        )
        self.pattern_orphan_html = re.compile(r'</?sup>|</?sub>')
        self._unicode_map = {
            '\u00B9': '1', '\u00B2': '2', '\u00B3': '3',
            '\u2070': '0', '\u2071': '1', '\u2072': '2',
            '\u2073': '3', '\u2074': '4', '\u2075': '5',
            '\u2076': '6', '\u2077': '7', '\u2078': '8',
            '\u2079': '9', '\u207A': '+', '\u207B': '-',
        }

    def _unicode_sup_to_number(self, match: re.Match) -> str:
        sup_text = match.group(0)
        result = ""
        for char in sup_text:
            result += self._unicode_map.get(char, char)
        return f"[{result}]"

    def _normalize_references(self, text: str) -> str:
        text = self.pattern_sup_html.sub(r'[\1]', text)
        text = self.pattern_sup_unicode.sub(self._unicode_sup_to_number, text)
        return text

    def _clean_chunk_text(self, text: str) -> str:
        text = self.pattern_orphan_html.sub('', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def extract_references(self, text: str) -> List[str]:
        normalized = self._normalize_references(text)
        matches = self.pattern_bracket.findall(normalized)
        seen = set()
        refs = []
        for num in matches:
            ref = f"[{num}]"
            if ref not in seen:
                seen.add(ref)
                refs.append(ref)
        return refs

    def extract_chunks_with_references(self, text: str) -> List[Dict]:
        normalized = self._normalize_references(text)
        matches = list(self.pattern_bracket.finditer(normalized))

        if not matches:
            text_stripped = text.strip()
            if text_stripped:
                return [{"text": text_stripped, "references": []}]
            return []

        chunks = []
        last_end = 0

        for match in matches:
            start = match.start()
            chunk_text = self._clean_chunk_text(normalized[last_end:start])

            if chunk_text:
                refs_at_pos = self._collect_refs_at_position(matches, start)
                chunks.append({
                    "text": chunk_text,
                    "references": refs_at_pos
                })

            last_end = match.end()

        trailing_text = self._clean_chunk_text(normalized[last_end:])
        if trailing_text:
            chunks.append({
                "text": trailing_text,
                "references": []
            })

        return chunks

    def _collect_refs_at_position(self, matches: list, position: int) -> List[str]:
        refs = []
        seen = set()
        for match in matches:
            if match.start() == position:
                ref = f"[{match.group(1)}]"
                if ref not in seen:
                    seen.add(ref)
                    refs.append(ref)
        return refs
