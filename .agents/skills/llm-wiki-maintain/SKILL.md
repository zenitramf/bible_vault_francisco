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

`build` regenerates `wiki/catalog.jsonl`, `wiki/indexes/*.jsonl` (by-tag, by-passage, by-source, by-type), and folder `index.md` files. Run it after any material wiki edit.

Optional catalog unit checks:

```bash
python3 .tools/scripts/test_wiki_tool_catalog.py
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

- Lexical refresh after source moves or wiki page adds: `.qmd/bin/update-safe`
- Wiki embeddings when synthesis changed: `.qmd/bin/embed-wiki-safe`
- Optional personal-notes vector pilot only: `.qmd/bin/embed-notes-safe`
- Retrieval smoke: `.qmd/bin/benchmark-lexical` and `.qmd/bin/benchmark-multilingual`
- Merged wiki search check: `.qmd/bin/search-wiki-safe "prayer" --no-semantic`
- Never embed full `bible-sources` without explicit approval
- Never index `raw/`
- See `.qmd/README.md` for models policy and path normalization

## Templates and schema

- Templates: `_templates/`
- Schema docs: `schema/`
- Agent rules: `AGENTS.md`
