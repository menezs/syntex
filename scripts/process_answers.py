import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.file_loader import FileLoader
from src.reference_extractor import ReferenceExtractor


def process_answers(answers_dir: str, output_dir: str = None):
    base_path = Path(__file__).parent.parent
    answers_dir = Path(answers_dir)

    if output_dir is None:
        output_dir = base_path / "data" / "chunks"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading files from {answers_dir}...")
    loader = FileLoader(str(answers_dir))
    documents = loader.load()
    print(f"Loaded {len(documents)} files")

    extractor = ReferenceExtractor()

    total_chunks = 0

    for doc in documents:
        print(f"\nProcessing: {doc.filename}")

        chunks = extractor.extract_chunks_with_references(doc.content)

        if not chunks:
            print(f"  No content extracted, skipping")
            continue

        output_file = output_dir / f"{doc.filename.rsplit('.', 1)[0]}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        refs_count = sum(len(c["references"]) for c in chunks)
        print(f"  Chunks: {len(chunks)} | References found: {refs_count}")
        print(f"  Saved: {output_file.name}")

        total_chunks += len(chunks)

    print(f"\nDone! Total: {total_chunks} chunks saved to {output_dir}")


def main():
    base_path = Path(__file__).parent.parent
    answers_dir = str(base_path / "data" / "answers")
    process_answers(answers_dir)


if __name__ == "__main__":
    main()
