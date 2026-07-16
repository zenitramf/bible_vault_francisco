---
type: Schema Reference
title: Command Reference
description: Commands for wiki_tool.py, lint_wiki.py, and audit_public.py.
tags: [okf, schema, tooling]
updated: 2026-07-16
---

# Command Reference

All wiki maintenance and search tools live under `.tools/scripts/`. This vault does not use qmd, Chroma, Qdrant, or other RAG/embedding stacks.

## `wiki_tool.py`

```bash
python3 .tools/scripts/wiki_tool.py <command> [options]
```

| Command | Purpose |
|---|---|
| `doctor` | Non-mutating health check (folders, Python, catalog, reverse indexes, manifest, note counts) |
| `build` | Write `wiki/catalog.jsonl`, `wiki/indexes/*.jsonl`, regenerate wiki `index.md` files, and regenerate side-by-side `index.base` files plus root `bases.base` |
| `lint` | Validate wiki frontmatter, tags shape, source_count, claims, wikilinks |
| `source-scan` | List or update `schema/source-manifest.jsonl` from `sources/` |
| `source-scan --update` | Rewrite manifest inventory from disk |
| `source-scan --update --accept-covered` | Also mark coverage from wiki backlinks |
| `source-lint` | Manifest consistency and covered-without-links failures |
| `source-delta` | Sources on disk missing from the manifest |
| `source-coverage` | Covered vs uncovered summary (full vault or path-scoped) |
| `source-coverage --path PREFIX` | Filter by source path substring (corpus/volume gates) |
| `source-coverage --path PREFIX --require-zero` | Exit 1 if any uncovered remain in scope |
| `source-coverage --path PREFIX --uncovered-only` | List only uncovered paths in scope |
| `search-catalog --query "text"` | Ranked search over the enriched catalog (title, tags, refs, sources) |
| `search-catalog --tag TAG` | Filter to pages with a thematic tag |
| `search-catalog --ref "mt 6"` | Filter/boost by Bible reference or book |
| `search-catalog --source PATH` | Filter by source path substring |
| `search-catalog --type "Passage"` | Filter by page type substring |
| `tsk --ref "mt 6:9"` | Treasury of Scripture Knowledge cross-refs for a verse or range |
| `tsk --chapter "ge 1"` | TSK entries for every verse in a chapter |
| `log --title "..." --details "..."` | Append an entry to `wiki/log.md` |

### `search-catalog` examples

```bash
python3 .tools/scripts/wiki_tool.py search-catalog --query "prayer"
python3 .tools/scripts/wiki_tool.py search-catalog --query "matthew 6"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "ro 8" --limit 5
python3 .tools/scripts/wiki_tool.py search-catalog --source "sermon_1532"
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer --type "Biblical Concept"
```

Hits print a score, match reasons, and derived refs when present. This is the primary agent retrieval path for the compiled wiki.

### `tsk` (Treasury of Scripture Knowledge)

Immutable data: `sources/reference/tsk/tskxref.txt` (see provenance note beside it). Do not hand-scan the TSV; use this command when a study question needs traditional cross-reference chains. Output is **not** wiki synthesis—pair with `search-catalog` / passage hubs.

```bash
python3 .tools/scripts/wiki_tool.py tsk --ref "mt 6:9"
python3 .tools/scripts/wiki_tool.py tsk --ref "Matthew 6:9-13"
python3 .tools/scripts/wiki_tool.py tsk --chapter "ge 1"
python3 .tools/scripts/wiki_tool.py tsk --ref "joh 1:1" --format json
python3 .tools/scripts/wiki_tool.py tsk --chapter "ps 23" --format plain --max-refs 12
```

| Option | Purpose |
|---|---|
| `--ref` | Verse or verse range (`mt 6:9`, `mt 6:1-15`, English book names ok) |
| `--chapter` | All TSK rows for a chapter (`mt 6`, `Genesis 1`) |
| `--format` | `markdown` (default), `plain`, or `json` |
| `--max-refs` | Cap how many refs print per keyword entry (`0` = unlimited) |

Markdown output links the matching `wiki/passages/` chapter hub when present.

### Coverage gates (`source-coverage`)

After linking sources into the wiki for a volume or month, refresh coverage then assert zero uncovered in that path scope when required:

```bash
# Refresh covered_by from wiki source links
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered

# Per-corpus / volume / month checks (exit 0 only when uncovered = 0)
python3 .tools/scripts/wiki_tool.py source-coverage --path mhenry-complete/volume-1 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-tod/volume-1 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-sermons/volume-1 --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-fcb/january --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-mae/january --require-zero

# Full corpus gates
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-sermons --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path mhenry-complete --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-fcb --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-mae --require-zero
python3 .tools/scripts/wiki_tool.py source-coverage --path chspurgeon-tod --require-zero

# Debug remaining gaps
python3 .tools/scripts/wiki_tool.py source-coverage --path mhenry-complete/volume-1 --uncovered-only --limit 20
```

`--path` is a substring match on the vault-relative source path.

## `lint_wiki.py`

```bash
python3 .tools/scripts/lint_wiki.py
```

Complementary structural lint: index.md presence/shape under wiki and sources trees, required frontmatter fields, `bible_reference` shape, uncited core claims, and broken/ambiguous wikilinks. Pairing of `index.base` with each non-root `index.md` (and root `bases.base` only) is enforced by `wiki_tool.py lint`.

## `audit_public.py`

```bash
python3 .tools/scripts/audit_public.py
```

Fails on obvious secrets, private key blocks, and machine-local absolute home paths in committed text. Ignores `.git/` and ignored Obsidian cache paths.

## Optional git hooks

```bash
bash .tools/scripts/install_hooks.sh
```

Installs a pre-commit hook that runs `build`, `lint`, `source-lint`, and `lint_wiki`.

## Maintenance gate

```bash
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```
