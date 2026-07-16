---
type: Operations Reference
title: Qdrant Cloud (Bible Vault)
description: Hosted vector layer — sparse wiki BM25 and dense sources E5; local embeddings, vault-linked metadata.
tags: [okf, tooling, retrieval]
updated: 2026-07-16
status: developing
---

# Qdrant Cloud (Bible Vault)

Hosted ANN / sparse retrieval for this vault. Embeddings are produced by
**Qdrant Cloud Inference** (free `intfloat/multilingual-e5-small` + `Qdrant/bm25`);
hermes only chunks text, upserts `Document(...)`, and queries.

## Cluster

| Field | Value |
|---|---|
| Name | `bible_vault` |
| Endpoint | `https://af215873-0bcb-46d3-8a94-829541781b37.us-west-1-0.aws.cloud.qdrant.io:6333` |
| Version | 1.18.x |
| Auth env | `QCLOUD_BIBLE_CLUSTER_API_KEY` (database key) or `QDRANT_API_KEY` |
| Optional URL env | `QDRANT_URL` |
| Vault id | `bible_vault_francisco` |

Management (`qcloud` CLI) is separate from the database API key.

## Collections (v1)

| Collection | Vector type | Model / method | Layer |
|---|---|---|---|
| `wiki_bm25` | Sparse named `bm25` (IDF) | BM25 (e.g. FastEmbed `Qdrant/bm25`) | `wiki/` |
| `sources_e5` | Dense 384-d cosine | `intfloat/multilingual-e5-small` | `sources/` |

### E5 prefix policy

- Upsert: `passage: {chunk}`
- Query: `query: {question}`

### Required payload (both)

- `vault_id` — always filter; value `bible_vault_francisco` for this repo
- `vault_rel_path` — disk path from vault root (e.g. `wiki/concepts/Prayer.md`)
- `layer` — `wiki` \| `sources` \| `personal-notes`
- `embed_model`, `content_hash` / `doc_hash`, `git_commit` (when known)

### Wiki-only payload

- `page_type`, `status`, `title`, `tags`, optional `bible_*`

### Sources-only payload

- `source_corpus`, `content_kind`, `language`, optional `bible_*`, `chunk_index`

## Bootstrap + local venv

```bash
export QCLOUD_BIBLE_CLUSTER_API_KEY=...   # already set on hermes if configured

# One-time tooling env (gitignored)
python3 -m venv .tools/venv-qdrant
.tools/venv-qdrant/bin/pip install -r .tools/requirements-qdrant.txt

python3 .tools/scripts/qdrant_bootstrap.py
# or: .tools/venv-qdrant/bin/python .tools/scripts/qdrant_bootstrap.py
```

## Wiki sparse (live)

```bash
.qmd/bin/qdrant-wiki-upsert              # BM25 upsert all wiki pages
.qmd/bin/qdrant-wiki-search "prayer"     # sparse search → vault_rel_path
.qmd/bin/qdrant-wiki-search "intercession" --limit 5 --json
```

## Embedding backend: Qdrant Cloud Inference

| Collection | Model | Where it runs |
|---|---|---|
| `wiki_bm25` | `Qdrant/bm25` (sparse, IDF) | Qdrant Cloud |
| `sources_e5` | `intfloat/multilingual-e5-small` (384-d) | Qdrant Cloud |

Client must use `cloud_inference=True` (set in `make_client()`). For E5 family,
Qdrant applies `passage:` / query-side prefixes server-side.

Optional offline helper (not used by upsert/search): `.qmd/bin/e5-encode` (local ONNX).

## Sources dense pilot (phase 4+)

Default corpus: **mhenry-concise** (~4.8k chunks after heading-aware split).

```bash
.qmd/bin/qdrant-sources-upsert --corpus mhenry-concise
.qmd/bin/qdrant-sources-upsert --dry-run
.qmd/bin/qdrant-sources-upsert --limit-files 20   # smoke
.qmd/bin/qdrant-sources-search "how to pray without hypocrisy" --corpus mhenry-concise
.qmd/bin/qdrant-sources-search "creation of light" --book-key 1 --limit 5
```

Re-upsert after switching to Cloud Inference so stored vectors match the
cloud model (do not mix local ONNX vectors with cloud-inferred queries).

## Agent search (phase 5)

```bash
# Multi-channel (wiki BM25 then sources E5; scores not cross-comparable)
.qmd/bin/qdrant-search "prayer without hypocrisy" --channel both --json
.qmd/bin/qdrant-search "Spirit intercession" --channel wiki --json
.qmd/bin/qdrant-search "creation of light" --channel sources --corpus mhenry-concise --book-key 1

# Single-channel
.qmd/bin/qdrant-sources-search "how to pray" --corpus mhenry-concise --min-score 0.82 --json
.qmd/bin/qdrant-wiki-search "intercession" --page-type passage --json
```

JSON hits include `channel`, `vault_rel_path`, `wikilink`, and `text_preview`. Always open the vault path for citations.

## Agent retrieval order (target)

1. `wiki_tool.py search-catalog`
2. Local `search-wiki-safe` and/or Qdrant `wiki_bm25` — **implemented**
3. Qdrant `sources_e5` (dense, E5 query prefix) — **pilot (mhenry-concise) implemented**
4. Open `vault_rel_path` on disk for citations

Local `qmd` BM25 may remain as a transitional lexical channel for sources not yet in Qdrant.

## Security

- Do not commit API keys or connection strings.
- Do not log full keys.
- Prefer env vars only; never write secrets into wiki or git.
