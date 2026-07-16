---
type: Schema Reference
title: Workflow Examples
description: Example ingest, query, and maintenance workflows for the Bible Vault LLM Wiki.
tags: [okf, schema, workflow]
updated: 2026-07-16
---

# Workflow Examples

## Query (compiled wiki first)

```bash
# 1. Catalog (lightweight, no models)
python3 .tools/scripts/wiki_tool.py search-catalog --query "prayer spirit intercession"

# 2. Lexical wiki search (guarded qmd)
qmd search "prayer intercession" -c bible-wiki --json -n 10

# 3. Semantic wiki only when needed (memory-safe wrapper)
.qmd/bin/semantic-wiki-safe "How does the Spirit help in prayer?" --json -n 10
```

Open the best `wiki/` hits. Open `sources/` only for verification, disagreement, or missing detail:

```bash
qmd search "Romans 8 intercession" -c bible-sources --json -n 15
```

## Ingest a new source

1. Place cleaned markdown in `raw/` (or confirm it already lives under `sources/`).
2. Classify and move unchanged into `sources/...`; update `raw/index.md` and the target source `index.md`.
3. Refresh lexical index: `.qmd/bin/update-safe`
4. Search catalog + wiki for related pages.
5. Create/update `wiki/source-notes/` and affected concept/passage/question pages.
6. Keep every material claim linked; set accurate `source_count`.
7. Rebuild and lint:

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/audit_public.py
.qmd/bin/lint-wiki
```

8. Log: `python3 .tools/scripts/wiki_tool.py log --title "ingest | My Source" --details "Summary of what changed."`
9. Optionally embed wiki: `.qmd/bin/embed-wiki-safe` (never embed sources without approval).

## Maintenance gate

```bash
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/audit_public.py
.qmd/bin/lint-wiki
```

## Source coverage report

```bash
python3 .tools/scripts/wiki_tool.py source-coverage
python3 .tools/scripts/wiki_tool.py source-delta
```

Most of the commentary corpus will remain uncovered by design. Coverage tracks intentional synthesis, not bulk ingestion.
