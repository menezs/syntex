import json
from pathlib import Path


def main():
    base_path = Path(__file__).parent.parent
    results_dirs = [
        base_path / "data" / "results" / "chatgpt",
        base_path / "data" / "results" / "gemini"
    ]

    total = 0

    for results_dir in results_dirs:
        if not results_dir.exists():
            print(f"Directory not found: {results_dir}")
            continue

        json_files = sorted(results_dir.glob("*.json"))
        print(f"Processing {results_dir.name}: {len(json_files)} files")

        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            md_content = ""
            for result in data["results"]:
                section = result.get("section", "")
                text = result.get("text", "")
                md_content += f"## {section}\n{text}\n\n"

            md_file = json_file.with_suffix(".md")
            with open(md_file, "w", encoding="utf-8") as f:
                f.write(md_content)

            total += 1

        print(f"  Completed {len(json_files)} .md files")

    print(f"\nTotal: {total} markdown files generated")


if __name__ == "__main__":
    main()