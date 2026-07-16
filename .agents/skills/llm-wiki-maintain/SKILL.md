---
name: llm-wiki-maintain
description: Rebuild catalog and indexes, refresh coverage, and keep the Bible Wiki healthy.
---

# LLM Wiki Maintain

## Routine rebuild

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

`build` regenerates `wiki/catalog.jsonl`, `wiki/indexes/*.jsonl` (by-tag, by-passage, by-source, by-type), wiki folder `index.md` files, every side-by-side `index.base` (paired with each non-root `index.md`), and root `bases.base` (base of bases). Run it after any material wiki edit or when new content directories gain an `index.md`.

Optional catalog unit checks:

```bash
python3 .tools/scripts/test_wiki_tool_catalog.py
```

## Coverage reports

```bash
python3 .tools/scripts/wiki_tool.py source-coverage
python3 .tools/scripts/wiki_tool.py source-delta
```

Sparse coverage of the commentary corpus is expected outside deliberate full-coverage campaigns. Do not mass-ingest sources just to raise coverage percentages.

## Optional hooks

```bash
bash .tools/scripts/install_hooks.sh
```

Hooks run build/lint/source-lint/lint_wiki only.

## Retrieval

- Wiki search for agents: `wiki_tool.py search-catalog` (and reverse indexes under `wiki/indexes/`).
- No embedding, vector database, qmd, Chroma, or Qdrant stack is part of this vault.

## Templates and schema

- Templates: `_templates/`
- Schema docs: `schema/`
- Agent rules: `AGENTS.md`
