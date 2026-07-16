---
type: Schema Reference
title: Command Reference
description: Commands for wiki_tool.py, audit_public.py, and guarded qmd helpers.
tags: [okf, schema, tooling]
updated: 2026-07-16
---

# Command Reference

All wiki maintenance tools live under `.tools/scripts/`. Resource-safe qmd helpers remain under `.qmd/bin/`.

## `wiki_tool.py`

```bash
python3 .tools/scripts/wiki_tool.py <command> [options]
```

| Command | Purpose |
|---|---|
| `doctor` | Non-mutating health check (folders, Python, catalog, reverse indexes, manifest, note counts) |
| `build` | Write `wiki/catalog.jsonl`, `wiki/indexes/*.jsonl`, and regenerate wiki `index.md` files |
| `lint` | Validate wiki frontmatter, tags shape, source_count, claims, wikilinks |
| `source-scan` | List or update `schema/source-manifest.jsonl` from `sources/` |
| `source-scan --update` | Rewrite manifest inventory from disk |
| `source-scan --update --accept-covered` | Also mark coverage from wiki backlinks |
| `source-lint` | Manifest consistency and covered-without-links failures |
| `source-delta` | Sources on disk missing from the manifest |
| `source-coverage` | Covered vs uncovered summary (full vault or path-scoped) |
| `source-coverage --path PREFIX` | Filter by source path substring (Phase 4 corpus/volume gates) |
| `source-coverage --path PREFIX --require-zero` | Exit 1 if any uncovered remain in scope |
| `source-coverage --path PREFIX --uncovered-only` | List only uncovered paths in scope |
| `search-catalog --query "text"` | Ranked search over the enriched catalog (title, tags, refs, sources) |
| `search-catalog --tag TAG` | Filter to pages with a thematic tag |
| `search-catalog --ref "mt 6"` | Filter/boost by Bible reference or book |
| `search-catalog --source PATH` | Filter by source path substring |
| `search-catalog --type "Passage"` | Filter by page type substring |
| `log --title "..." --details "..."` | Append an entry to `wiki/log.md` |

### `search-catalog` examples

```bash
python3 .tools/scripts/wiki_tool.py search-catalog --query "prayer"
python3 .tools/scripts/wiki_tool.py search-catalog --query "matthew 6"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "ro 8" --limit 5
python3 .tools/scripts/wiki_tool.py search-catalog --source "sermon_1532"
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer --type "Biblical Concept"
```

Hits print a score, match reasons, and derived refs when present.

### Phase 4 coverage gates (`source-coverage`)

After each Phase 4 sub-row (volume, volume-band, or calendar month), refresh coverage then assert zero uncovered in that path scope:

```bash
# Refresh covered_by from wiki source links
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered

# Per-corpus / volume / month checks (exit 0 only when uncovered = 0)
python3 .tools/scripts/wiki_tool.py source-coverage --path mhenry-complete/volume-1 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-tod/volume-1 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-sermons/volume-1 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-fcb/january --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-mae/january --require-zero

# Full Phase 4 corpus gates
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-sermons --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path mhenry-complete --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-fcb --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-mae --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-tod --require-zero

# Debug remaining gaps
python3 .tools/scripts/wiki_tool.py source-coverage --path mhenry-complete/volume-1 --uncovered-only --limit 20
```

`--path` is a substring match on the vault-relative source path. Mark a tracker row `reviewed` only when the matching `--require-zero` check passes. Commit once per completed sub-row (or volume-band).

## `audit_public.py`

```bash
python3 .tools/scripts/audit_public.py
```

Fails on obvious secrets, private key blocks, and machine-local absolute home paths in committed text. Ignores `.git/`, `.qmd` sqlite, and ignored Obsidian cache paths.

## Optional git hooks

```bash
bash .tools/scripts/install_hooks.sh
```

Installs a pre-commit hook that runs `build`, `lint`, and `source-lint` (no embedding, no heavy qmd models).

## Guarded qmd (do not replace)

See also `.qmd/README.md` for collections, path normalization, and models policy.

| Script | Purpose |
|---|---|
| `.qmd/bin/update-safe` | BM25 index refresh under memory/CPU limits |
| `.qmd/bin/embed-wiki-safe` | Embed `bible-wiki` only under limits |
| `.qmd/bin/embed-notes-safe` | Optional embed of `bible-personal-notes` pilot only |
| `.qmd/bin/semantic-wiki-safe` | Vector-only wiki query (`vec:`, no rerank) |
| `.qmd/bin/semantic-notes-safe` | Vector-only personal-notes pilot query |
| `.qmd/bin/search-wiki-safe` | Merge catalog + BM25 wiki + vector wiki hits |
| `.qmd/bin/lint-wiki` | Complementary structural lint |
| `.qmd/bin/benchmark-lexical` | Source BM25 fixture |
| `.qmd/bin/benchmark-multilingual` | EN/ES lexical + wiki semantic fixture |

### Qdrant Cloud (hosted vectors)

Requires `uv` on PATH and `QCLOUD_BIBLE_CLUSTER_API_KEY`. Details: `.qmd/qdrant-cloud.md`.

| Script | Purpose |
|---|---|
| `.qmd/bin/qdrant-setup` | `uv sync` → `.tools/venv-qdrant` from `.tools/pyproject.toml` |
| `.tools/scripts/qdrant_bootstrap.py` | Ensure empty `wiki_bm25` + `sources_e5` + payload indexes |
| `.qmd/bin/qdrant-wiki-upsert` | Sparse BM25 upsert of wiki pages |
| `.qmd/bin/qdrant-wiki-search` | Sparse wiki search |
| `.qmd/bin/e5-encode` | Optional local E5 ONNX (needs `uv sync --extra e5-local`) |
| `.qmd/bin/qdrant-sources-upsert` | Dense E5 upsert (default corpus: mhenry-concise) |
| `.qmd/bin/qdrant-sources-search` | Dense sources search (vault-scoped) |
| `.qmd/bin/qdrant-search` | Multi-channel agent search (wiki and/or sources) |

```bash
.qmd/bin/qdrant-setup
# or: UV_PROJECT_ENVIRONMENT=.tools/venv-qdrant uv sync --directory .tools
```


```bash
.qmd/bin/update-safe
.qmd/bin/embed-wiki-safe
.qmd/bin/search-wiki-safe "prayer and the Spirit" --json
.qmd/bin/qdrant-search "prayer without hypocrisy" --channel both --json
.qmd/bin/qdrant-sources-search "creation of light" --book-key 1 --json
.qmd/bin/benchmark-lexical
.qmd/bin/benchmark-multilingual
```

Never run bare `qmd vsearch` or `qmd bench` on this server by default. Do not embed full `bible-sources` into local qmd without explicit approval. Query-expansion and rerank models are intentionally not used in routine ops.
