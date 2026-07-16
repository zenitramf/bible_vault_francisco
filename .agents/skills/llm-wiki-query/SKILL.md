---
name: llm-wiki-query
description: Answer questions from the compiled Bible Wiki before opening broad Raw or Sources context.
---

# LLM Wiki Query

## When to use

The user asks a biblical, theological, or vault-knowledge question.

## Order of operations

1. Start with the enriched catalog (primary agent map). Prefer filters when the user names a tag, passage, or source:

```bash
python3 .tools/scripts/wiki_tool.py search-catalog --query "user topic"
python3 .tools/scripts/wiki_tool.py search-catalog --query "matthew 6"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "mt 6" --limit 5
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer
python3 .tools/scripts/wiki_tool.py search-catalog --source "sermon_1532"
```

Catalog rows and reverse indexes (`wiki/indexes/`) include derived `bible_references`, `source_paths`, and `related_paths`. Use match reasons in the CLI output to choose pages.

2. Lexical and (if needed) semantic wiki search when catalog hits are thin or you need body-level phrases:

```bash
qmd search "query terms" -c bible-wiki --json -n 10
.qmd/bin/semantic-wiki-safe "natural-language question" --json -n 10
```

3. Open the most relevant wiki notes only.
4. Open `sources/` only when:
   - the wiki is incomplete,
   - a claim needs verification,
   - interpretations disagree,
   - the user asks for source-level evidence.

```bash
qmd search "precise source terms" -c bible-sources --json -n 15
```

5. Cite wiki pages and source paths used in the answer.
6. File a durable answer under `wiki/questions/` only if the user requests or approves it.

## Server constraints

- Do not run full `qmd query` by default.
- Do not start a persistent qmd MCP/HTTP daemon.
- Do not use bare `qmd vsearch` (use `semantic-wiki-safe`).
- Combine catalog + lexical + optional vector results in the agent.
