# Syntex

Sistema de busca semântica para documentos jurídicos sobre Direito e Tecnologia, Regulação e IA.

## Arquitetura

O projeto implementa um pipeline de Retrieval-Augmented Generation (RAG) com os seguintes componentes:

### Módulos Principais

| Módulo | Descrição |
|--------|-----------|
| `src/loader.py` | Carrega documentos Markdown do diretório `data/documents` |
| `src/chunker.py` | Segmenta documentos em chunks semânticos baseados em tokens e estrutura Markdown |
| `src/embeddings.py` | Gera embeddings usando o modelo `BAAI/bge-m3` (dimensão: 1024) |
| `src/indexer.py` | Indexa vetores no FAISS (IndexFlatIP) e metadados no SQLite |
| `src/search.py` | Executa busca semântica com suporte a reranking |
| `src/reranker.py` | Reordena resultados usando `BAAI/bge-reranker-v2-m3` |

### Estrutura de Dados

```
data/
├── documents/      # 62 documentos Markdown (referências jurídicas)
├── chunks/        # Arquivos JSON com chunks de referências
├── index/         # Índice FAISS (faiss.index)
├── metadata/      # Banco SQLite (chunks.db)
└── results/       # Resultados de buscas em lote
    ├── chatgpt/
    └── gemini/
```

## Instalação

```bash
pip install -r requirements.txt
```

Dependências:
- `sentence-transformers` - Modelos de embeddings e reranker
- `faiss-cpu` - Índice de busca vetorial
- `tiktoken` - Tokenizador para chunking
- `semantic-text-splitter` - Divisor semântico de texto
- `mistune` - Parser Markdown

## Uso

### 1. Construir Índice

```bash
python scripts/build_index.py
```

Executa:
1. Carrega 62 documentos de `data/documents/`
2. Cria ~512 chunks semânticos (max_tokens=512, overlap=50)
3. Gera embeddings com BAAI/bge-m3
4. Indexa no FAISS + SQLite

### 2. Busca Interativa

```bash
python scripts/query.py "sua consulta aqui"
```

### 3. Busca em Lote

```bash
python scripts/batch_search.py
```

Processa chunks de referência de ChatGPT e Gemini, salvando resultados em `data/results/`.

### Conversão JSON → Markdown

```bash
python scripts/json_to_markdown.py
```

Converte resultados JSON para formato Markdown legível.

## Modelos Utilizados

| Modelo | Tamanho | Uso |
|--------|---------|-----|
| `BAAI/bge-m3` | ~1GB | Embeddings multilingue |
| `BAAI/bge-reranker-v2-m3` | ~1GB | Reranking de resultados |

Modelos cacheados em `./model_cache/`.

## Status Atual

- **Documentos indexados**: 62
- **Chunks gerados**: ~512 (varia conforme conteúdo)
- **Resultados em lote**: 56 arquivos JSON em `data/results/chatgpt/`
- **Index FAISS**: Pronto em `data/index/faiss.index`
- **Banco de metadados**: SQLite em `data/metadata/chunks.db`

## Estrutura do Código

```
syntex/
├── src/
│   ├── models.py       # Dataclasses: Chunk, Document
│   ├── loader.py      # MarkdownLoader
│   ├── chunker.py     # SemanticChunker
│   ├── embeddings.py  # Embedder (BGE-M3)
│   ├── indexer.py     # FAISSIndexer + SQLite
│   ├── search.py      # SemanticSearch
│   └── reranker.py    # Reranker (BGE-Reranker)
├── scripts/
│   ├── build_index.py   # Constrói índice
│   ├── query.py         # Busca interativa
│   ├── batch_search.py  # Busca em lote
│   └── json_to_markdown.py
├── data/
│   ├── documents/       # Markdown fontes
│   ├── chunks/          # Chunks JSON de referências
│   ├── index/           # Índice FAISS
│   ├── metadata/        # SQLite
│   └── results/         # Resultados
└── requirements.txt
```