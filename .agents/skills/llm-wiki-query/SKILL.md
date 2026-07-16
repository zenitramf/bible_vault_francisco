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
python3 .tools/scripts/wiki_tool.py search-catalog --type "Biblical Concept" --query "prayer"
```

Catalog rows and reverse indexes (`wiki/indexes/`) include derived `bible_references`, `source_paths`, and `related_paths`. Use match reasons in the CLI output to choose pages.

2. Open the most relevant wiki notes only.
3. Open `sources/` only when:
   - the wiki is incomplete,
   - a claim needs verification,
   - interpretations disagree,
   - the user asks for source-level evidence.

Prefer paths already listed on wiki pages or in catalog `source_paths`. Do not run embedding, vector, or full-corpus BM25 search—this vault has no qmd, Chroma, or Qdrant layer.

4. Cite wiki pages and source paths used in the answer.
5. File a durable answer under `wiki/questions/` only if the user requests or approves it.

## Retrieval model

- **Primary:** `wiki_tool.py search-catalog` over `wiki/catalog.jsonl`.
- **Structure:** reverse indexes under `wiki/indexes/` (by-tag, by-passage, by-source, by-type).
- **Evidence:** open specific `sources/` files via wikilinks when needed.
- **Out of scope:** vector databases, embedding pipelines, hosted sparse/dense RAG.
