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
python3 .tools/scripts/audit_public.py
```

## Coverage reports

```bash
python3 .tools/scripts/wiki_tool.py source-coverage
python3 .tools/scripts/wiki_tool.py source-delta
```

Sparse coverage of the commentary corpus is expected. Do not mass-ingest sources just to raise coverage percentages.

## Optional hooks

```bash
bash .tools/scripts/install_hooks.sh
```

Hooks run build/lint/source-lint only — never embedding.

## Indexing / embeddings

- Lexical refresh after source moves: `.qmd/bin/update-safe`
- Wiki embeddings only when needed: `.qmd/bin/embed-wiki-safe`
- Never embed `bible-sources` without explicit approval
- Never index `raw/`

## Templates and schema

- Templates: `_templates/`
- Schema docs: `schema/`
- Agent rules: `AGENTS.md`
