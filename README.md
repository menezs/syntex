# Syntex

Sistema de busca semântica para documentos jurídicos sobre Direito e Tecnologia, Regulação e IA.

## Arquitetura

O projeto implementa um pipeline de **Retrieval-Augmented Generation (RAG)** com busca semântica em duas etapas:

1. **Retrieval** — Busca vetorial amplo (top_k=50) via FAISS para alto recall
2. **Reranking** — Reordenação com CrossEncoder (top 20) para alta precisão

### Módulos Principais

| Módulo | Descrição |
|--------|-----------|
| `src/models.py` | Dataclasses: `Chunk`, `Document` |
| `src/loader.py` | Carrega documentos Markdown do diretório `data/documents` |
| `src/file_loader.py` | Carrega arquivos PDF, DOCX e MD do diretório `data/answers` |
| `src/chunker.py` | Segmenta documentos em chunks semânticos (max_tokens=512, overlap=50) |
| `src/reference_extractor.py` | Extrai citações e cria chunks por marcação de referência |
| `src/embeddings.py` | Gera embeddings usando `BAAI/bge-m3` (dimensão: 1024) |
| `src/indexer.py` | Indexa vetores no FAISS (IndexFlatIP) e metadados no SQLite |
| `src/search.py` | Busca semântica com dois estágios: retrieval + reranking |
| `src/reranker.py` | Reordena resultados usando `BAAI/bge-reranker-v2-m3` |

### Fluxo de Busca

```
Query → Embedding (BGE-M3) → FAISS top-50 → Reranker (BGE-Reranker) → Top-20
```

## Estrutura de Dados

```
data/
├── answers/         # Arquivos de entrada (PDF, DOCX, MD)
├── documents/       # Documentos Markdown (fonte para índice)
├── chunks/          # JSONs com chunks extraídos dos arquivos
├── index/           # Índice FAISS (faiss.index)
├── metadata/        # Banco SQLite (chunks.db)
└── results/         # Resultados de buscas em lote
    ├── chatgpt/
    └── gemini/
```

## Instalação

```bash
pip install -r requirements.txt
```

Dependências:
- `sentence-transformers` — Modelos de embeddings e reranker
- `faiss-cpu` — Índice de busca vetorial
- `tiktoken` — Tokenizador para chunking
- `semantic-text-splitter` — Divisor semântico de texto
- `mistune` — Parser Markdown
- `pymupdf4llm` — Extração de texto de PDFs
- `python-docx` — Leitura de arquivos DOCX

## CLI

O projeto utiliza uma interface de linha de comando unificada via `syntex.py`.

### Visão Geral

```bash
python syntex.py <comando> [opções]
```

### Comandos Disponíveis

#### `build` — Construir Índice

```bash
python syntex.py build --docs data/documents
```

| Flag | Obrigatório | Descrição |
|------|-------------|-----------|
| `--docs` | Sim | Pasta com documentos `.md` para indexar |
| `--index` | Não | Caminho do índice FAISS (default: `data/index/faiss.index`) |
| `--db` | Não | Caminho do banco SQLite (default: `data/metadata/chunks.db`) |

#### `search` — Busca em Lote

```bash
python syntex.py search --chunks data/chunks/ChatGPT-Desafios_e_avanços_em_LLMs_multilíngues.json
```

| Flag | Obrigatório | Descrição |
|------|-------------|-----------|
| `--chunks` | Sim | Arquivo JSON com chunks de referência |
| `--output` | Não | Pasta de saída para resultados |
| `--index` | Não | Caminho do índice FAISS |
| `--db` | Não | Caminho do banco SQLite |

#### `query` — Busca Interativa

```bash
python syntex.py query "regulação de IA no Brasil"
```

| Argumento/Flag | Obrigatório | Descrição |
|----------------|-------------|-----------|
| `query_text` | Sim | Texto da consulta (posicional) |
| `--index` | Não | Caminho do índice FAISS |
| `--db` | Não | Caminho do banco SQLite |

#### `process` — Processar Respostas

```bash
python syntex.py process --answers data/answers
```

| Flag | Obrigatório | Descrição |
|------|-------------|-----------|
| `--answers` | Sim | Pasta com arquivos PDF, DOCX ou MD |
| `--output` | Não | Pasta de saída para chunks JSON (default: `data/chunks/`) |

**Formatos suportados:**
- **PDF** — Extração via pymupdf4llm
- **DOCX** — Extração via python-docx (detecta superscripts e hyperlinks)
- **MD** — Leitura direta

**Padrões de citação detectados:**
- Números entre colchetes: `[1]`, `[12]`, `[1][2][3]`
- Com espaços opcionais: `[ 1]`, `[1 ]`, `[ 12 ]`
- Superscripts HTML: `<sup>1</sup>` (vindos de DOCX)
- Superscripts Unicode: `¹`, `²`, `³`, `⁰`-`⁹` (vindos de PDFs)

#### `convert` — Converter para Markdown

```bash
python syntex.py convert --results data/results/chatgpt
```

| Flag | Obrigatório | Descrição |
|------|-------------|-----------|
| `--results` | Sim | Pasta com resultados JSON |

#### `clean` — Limpar Índice

```bash
python syntex.py clean
python syntex.py clean -f  # sem confirmação
```

| Flag | Obrigatório | Descrição |
|------|-------------|-----------|
| `--index` | Não | Caminho do índice FAISS |
| `--db` | Não | Caminho do banco SQLite |
| `-f`, `--force` | Não | Confirmar limpeza sem pedir |

Remove o índice FAISS (`data/index/faiss.index`) e o banco SQLite (`data/metadata/chunks.db`). Por padrão, solicita confirmação antes de remover.

### Scripts Standalone

Os scripts em `scripts/` continuam funcionando de forma independente:

```bash
python scripts/build_index.py
python scripts/batch_search.py
python scripts/query.py "sua consulta"
python scripts/process_answers.py
python scripts/json_to_markdown.py
```

## Modelos Utilizados

| Modelo | Tamanho | Uso |
|--------|---------|-----|
| `BAAI/bge-m3` | ~1GB | Embeddings multilingue |
| `BAAI/bge-reranker-v2-m3` | ~1GB | Reranking de resultados |

Modelos cacheados em `./model_cache/`.

## Estrutura do Código

```
syntex/
├── syntex.py                  # Entry point CLI
├── src/
│   ├── models.py               # Dataclasses: Chunk, Document
│   ├── loader.py               # MarkdownLoader
│   ├── file_loader.py          # FileLoader (PDF, DOCX, MD)
│   ├── chunker.py              # SemanticChunker
│   ├── reference_extractor.py  # ReferenceExtractor
│   ├── embeddings.py           # Embedder (BGE-M3)
│   ├── indexer.py              # FAISSIndexer + SQLite
│   ├── search.py               # SemanticSearch (retrieval + reranking)
│   └── reranker.py             # Reranker (BGE-Reranker)
├── scripts/
│   ├── process_answers.py      # Processa respostas em lote
│   ├── build_index.py          # Constrói índice
│   ├── query.py                # Busca interativa
│   ├── batch_search.py         # Busca em lote
│   └── json_to_markdown.py
├── data/
│   ├── answers/                # Arquivos de entrada (PDF, DOCX, MD)
│   ├── documents/              # Markdown fontes
│   ├── chunks/                 # Chunks JSON extraídos
│   ├── index/                  # Índice FAISS
│   ├── metadata/               # SQLite
│   └── results/                # Resultados
└── requirements.txt
```
