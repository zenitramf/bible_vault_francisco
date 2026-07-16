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
| `source-coverage` | Covered vs uncovered summary |
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

| Script | Purpose |
|---|---|
| `.qmd/bin/update-safe` | BM25 index refresh under memory/CPU limits |
| `.qmd/bin/embed-wiki-safe` | Embed `bible-wiki` only under limits |
| `.qmd/bin/semantic-wiki-safe` | Vector-only wiki query, no rerank |
| `.qmd/bin/lint-wiki` | Complementary structural lint |
| `.qmd/bin/benchmark-lexical` | Lexical retrieval baseline |

Never run bare `qmd vsearch` or `qmd bench` on this server by default.
