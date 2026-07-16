---
type: Operations Reference
title: qmd Operations (Bible Vault)
description: Resource-safe qmd configuration, collections, models policy, and retrieval workflow.
tags: [okf, tooling, retrieval]
updated: 2026-07-16
---

# qmd Operations (Bible Vault)

Project-local index lives in `.qmd/`. The SQLite DB (`index.sqlite`) is a **local artifact** and must not be committed.

## Collections

| Name | Path | Default | Lexical | Vectors (this host) |
|---|---|---|---|---|
| `bible-wiki` | `wiki/` | yes | yes | yes (via `embed-wiki-safe`) |
| `bible-sources` | `sources/` | no | yes | **no** (policy) |
| `bible-personal-notes` | `sources/personal-notes/` | no | yes | optional pilot only |

`raw/` is never indexed.

### Path normalization

- Disk paths use underscores and spaces as in the vault (e.g. `sources/commentaries_english/...`).
- qmd URIs often hyphenate path segments (`qmd://bible-sources/commentaries-english/...`).
- Wiki wikilinks and `source-manifest` always use **disk** paths under `sources/`.
- When copying a path from `qmd search` into a wikilink, map back to the real filesystem path.

## Models policy (this server)

| Model | Role | Routine use |
|---|---|---|
| EmbeddingGemma 300M | embeddings | wiki (+ optional personal-notes pilot) |
| query-expansion 1.7B | hybrid `qmd query` expand | **do not load** |
| Qwen3 reranker 0.6B | rerank | **do not load** |

Reasons: ~4 GiB RAM, CPU-only inference, multi-tenant safety. Missing generate/rerank caches in `qmd doctor` are **expected**, not a defect.

Do **not**:

- run bare `qmd query` without `vec:` / `--no-rerank` guards
- run bare `qmd vsearch` (qmd 2.5.3 may still init expansion)
- run `qmd bench` (full hybrid backends)
- start a persistent qmd MCP/HTTP daemon by default
- embed full `bible-sources` without explicit approval

## Safe scripts (use these)

| Script | Purpose |
|---|---|
| `.qmd/bin/update-safe` | BM25 reindex (all collections) under mem/CPU caps |
| `.qmd/bin/embed-wiki-safe` | Embed `bible-wiki` only |
| `.qmd/bin/embed-notes-safe` | Optional embed of `bible-personal-notes` pilot only |
| `.qmd/bin/semantic-wiki-safe` | Vector-only wiki query (`vec:`, no rerank) |
| `.qmd/bin/search-wiki-safe` | Merge catalog + BM25 wiki + vector wiki hits |
| `.qmd/bin/benchmark-lexical` | Source BM25 fixture |
| `.qmd/bin/benchmark-multilingual` | EN/ES lex + wiki semantic fixture |
| `.qmd/bin/lint-wiki` | Structural wiki lint (complement to `wiki_tool lint`) |

## Hosted vectors (Qdrant Cloud)

Local QMD vectors are constrained on this host. Hosted collections live on Qdrant Cloud; see **[qdrant-cloud.md](qdrant-cloud.md)**.

| Collection | Kind | Purpose |
|---|---|---|
| `wiki_bm25` | Sparse BM25 (IDF) | Wiki free-text |
| `sources_e5` | Dense 384-d (`multilingual-e5-small`) | Source semantic search |

```bash
# venv once: python3 -m venv .tools/venv-qdrant && .tools/venv-qdrant/bin/pip install -r .tools/requirements-qdrant.txt
python3 .tools/scripts/qdrant_bootstrap.py   # empty collections + indexes
.qmd/bin/qdrant-wiki-upsert                  # sparse BM25 → wiki_bm25
.qmd/bin/qdrant-wiki-search "prayer"         # search wiki
.qmd/bin/e5-encode self-test                 # local multilingual-e5-small (ONNX)
.qmd/bin/qdrant-sources-upsert               # dense E5 → sources_e5 (mhenry-concise pilot)
.qmd/bin/qdrant-sources-search "how to pray" # dense source search
```

Requires `QCLOUD_BIBLE_CLUSTER_API_KEY`. Embeddings stay local; Qdrant stores vectors + vault-linked payload only.

## Recommended agent retrieval order

1. `wiki_tool.py search-catalog` — tags, refs, structured map  
2. `.qmd/bin/search-wiki-safe "question"` — merged wiki BM25 + vectors (+ catalog)  
3. `qmd search … -c bible-sources` — evidence when wiki is thin  
4. Optional: personal-notes pilot vectors only if that pilot is embedded and the question is personal-note shaped  

## After wiki or source changes

```bash
.qmd/bin/update-safe
.qmd/bin/embed-wiki-safe          # when wiki synthesis changed
# .qmd/bin/embed-notes-safe       # only if personal-notes pilot is active
.qmd/bin/benchmark-lexical
.qmd/bin/benchmark-multilingual   # needs free memory for semantic cases
```
