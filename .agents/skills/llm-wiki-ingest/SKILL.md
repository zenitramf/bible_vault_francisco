---
name: llm-wiki-ingest
description: Ingest a raw or existing source into the Bible Vault wiki without rewriting sources.
---

# LLM Wiki Ingest

## When to use

The user adds or points to a source to compile into wiki notes.

## Rules

- Treat `raw/` as staging and `sources/` as immutable evidence.
- Never rewrite source document contents during wiki work.
- Write reusable knowledge only under `wiki/`.
- Every material claim must link to evidence.
- Do not invent citations.
- Do not refresh embeddings or external indexes (none are used).

## Steps

1. Locate the file in `raw/` or confirm it already lives under `sources/`.
2. If staged in `raw/`, classify it and move it **unchanged** into the correct `sources/` path. Update `raw/index.md` and the target source `index.md`.
3. Search compiled knowledge first:

```bash
python3 .tools/scripts/wiki_tool.py search-catalog --query "likely topics"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "mt 6"
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer
```

4. Read the source; discuss important takeaways when appropriate.
5. Create or update `wiki/source-notes/` (use `_templates/source-note.md`).
6. Update every materially affected wiki page (concepts, people, passages, questions). Keep `source_count` accurate.
7. Rebuild and lint:

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

8. Append a log entry:

```bash
python3 .tools/scripts/wiki_tool.py log --title "ingest | Title" --details "What changed"
```

9. Review the git diff before reporting completion.
