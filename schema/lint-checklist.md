---
type: Schema Reference
title: Lint Checklist
description: Structural and content checks for the Bible Vault wiki and supporting artifacts.
tags: [okf, schema, lint]
updated: 2026-07-16
---

# Lint Checklist

Run before meaningful commits:

```bash
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/audit_public.py
.qmd/bin/lint-wiki
```

After source ingestion, also:

```bash
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
```

## OKF structural checks

- [ ] Non-reserved `.md` under `wiki/` has YAML frontmatter
- [ ] Every wiki concept frontmatter has non-empty `type`
- [ ] `index.md` files have **no** frontmatter and include a `# Contents` section
- [ ] `log.md` remains append-only operational history

## Wiki producer checks

- [ ] `title`, `description`, and non-empty `tags` present on wiki concepts
- [ ] Thematic tags only (no genre/author/book tags)
- [ ] `status` is `seed`, `developing`, or `reviewed` when present
- [ ] `source_count` matches listed evidence sources when present
- [ ] `bible_reference` matches `^[1-3]?[a-z]+ \d+:\d+(-\d+)?$` when present
- [ ] Each `## Core claims` bullet includes a wikilink
- [ ] Wikilinks resolve; full paths preferred for non-unique names
- [ ] Material claims trace to `sources/` or a source-note

## Source layer checks

- [ ] Do **not** rewrite files under `sources/` during wiki work
- [ ] Manifest coverage is derived from wiki links / `source_path`
- [ ] Uncovered commentary files are expected; sparse coverage is not a lint failure
- [ ] A source marked covered in the manifest must have at least one wiki backlink

## Catalog and indexes

- [ ] `wiki/catalog.jsonl` regenerated via `build`
- [ ] Wiki folder `index.md` files regenerated or consistent with disk
- [ ] `schema/source-manifest.jsonl` updated after intentional coverage changes

## Public audit

- [ ] No private keys, obvious secrets, or machine-local absolute home paths in committed text
- [ ] No Obsidian plugin/cache state committed

## Log

- [ ] Record lint/maintenance/ingest in `wiki/log.md`:
  `## [YYYY-MM-DD] lint | Scope`
