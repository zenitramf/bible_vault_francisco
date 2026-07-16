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
# Catalog search (primary retrieval; no models)
python3 .tools/scripts/wiki_tool.py search-catalog --query "prayer spirit intercession"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "ro 8"
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer --limit 10

# Traditional verse cross-references (TSK; not synthesis)
python3 .tools/scripts/wiki_tool.py tsk --ref "ro 8:28"
python3 .tools/scripts/wiki_tool.py tsk --chapter "mt 6" --max-refs 12
```

Open the best `wiki/` hits. Use reverse indexes under `wiki/indexes/` when browsing by tag, passage, source, or type. Open `sources/` only for verification, disagreement, or missing detail—prefer paths already linked from wiki pages or listed in catalog `source_paths`. For cross-reference chains, use `tsk` instead of scanning `sources/reference/tsk/tskxref.txt`.

## Ingest a new source

1. Place cleaned markdown in `raw/` (or confirm it already lives under `sources/`).
2. Classify and move unchanged into `sources/...`; update `raw/index.md` and the target source `index.md`.
3. Search catalog for related pages (`search-catalog`).
4. Create/update `wiki/source-notes/` and affected concept/passage/question pages.
5. Keep every material claim linked; set accurate `source_count`.
6. Rebuild and lint:

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

7. Log: `python3 .tools/scripts/wiki_tool.py log --title "ingest | My Source" --details "Summary of what changed."`

## Maintenance gate

```bash
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

## Source coverage report

```bash
python3 .tools/scripts/wiki_tool.py source-coverage
python3 .tools/scripts/wiki_tool.py source-delta
```

Outside deliberate full-coverage campaigns, sparse coverage of the commentary corpus is expected: coverage tracks intentional synthesis, not bulk ingestion.

### Path-scoped coverage gates

After wiki links land for a volume or month:

```bash
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-sermons/volume-12 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-fcb/march --uncovered-only
```

Commit once when the tracker sub-row flips to `reviewed` and its path-scoped gate passes.
