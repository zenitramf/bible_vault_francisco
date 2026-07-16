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

2. Prefer merged **local** wiki search and/or hosted **Qdrant wiki BM25**:

```bash
.qmd/bin/search-wiki-safe "natural-language or keyword question" --json
.qmd/bin/qdrant-search "prayer and the Father" --channel wiki --json
```

Or run channels separately when debugging:

```bash
qmd search "query terms" -c bible-wiki --json -n 10
.qmd/bin/semantic-wiki-safe "natural-language question" --json -n 10
.qmd/bin/qdrant-wiki-search "intercession" --json
```

3. Open the most relevant wiki notes only.
4. Open `sources/` only when:
   - the wiki is incomplete,
   - a claim needs verification,
   - interpretations disagree,
   - the user asks for source-level evidence.

Preferred **semantic** source path (Qdrant `sources_e5`, vault-scoped; pilot corpus mhenry-concise):

```bash
.qmd/bin/qdrant-sources-search "how to pray without hypocrisy" --corpus mhenry-concise --json
.qmd/bin/qdrant-search "Spirit helps in prayer" --channel both --json
.qmd/bin/qdrant-sources-search "creation of light" --book-key 1 --limit 5
```

Lexical source fallback (local qmd BM25 — good for exact phrases / not-yet-embedded corpora):

```bash
qmd search "precise source terms" -c bible-sources --json -n 15
```

Optional personal-notes vector pilot (only if embedded via `embed-notes-safe`):

```bash
.qmd/bin/semantic-notes-safe "pregunta sobre el pastor y las ovejas" --format json -n 5
```

5. Cite wiki pages and source paths used in the answer. Prefer `vault_rel_path` / `wikilink` from Qdrant JSON. Map qmd URIs back to disk paths when needed (`commentaries-english` → `commentaries_english`).
6. File a durable answer under `wiki/questions/` only if the user requests or approves it.

## Server constraints

- Do not run full `qmd query` by default (no expansion/rerank models).
- Do not start a persistent qmd MCP/HTTP daemon.
- Do not use bare `qmd vsearch` (use `semantic-wiki-safe` / `search-wiki-safe`).
- Do not embed full `bible-sources` into local qmd without explicit approval.
- Hosted source vectors: approved pilot is **mhenry-concise** in Qdrant; expand corpora only when asked.
- Qdrant needs `QCLOUD_BIBLE_CLUSTER_API_KEY`. See `.qmd/qdrant-cloud.md`.
- Prefer `search-wiki-safe` for local wiki merge; `qdrant-search` for hosted wiki + sources E5.
- Wiki BM25 scores and sources E5 cosine scores are **not** comparable — do not merge-rank them.
