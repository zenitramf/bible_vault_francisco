---
type: Metadata Convention
title: Bible Vault Metadata Conventions
description: Rules for OKF metadata, tags, Bible references, and navigation in this vault.
tags: [scripture, bible-study]
---

# Bible Vault Metadata Conventions

This vault is an OKF knowledge bundle (Open Knowledge Format v0.1). Every concept document has YAML frontmatter with a non-empty `type`, `title`, `description`, and `tags` list. Reserved `index.md` files do not have frontmatter.

OKF requires only a non-empty `type` on concept documents. This producer additionally requires `title`, `description`, and thematic `tags` for wiki quality. Producers MAY add extension fields; consumers MUST tolerate unknown types and unknown keys. See `schema/frontmatter-schema.md`.

## Tags

`tags` is a YAML list of short, lowercase, hyphenated strings for cross-cutting **Biblical concepts and themes**. Use tags such as `covenant`, `creation`, `redemption`, `faith`, `prayer`, `holiness`, `worship`, `discipleship`, `justice`, `prophecy`, `church`, `pastoral-ministry`, `salvation`, `christ`, `holy-spirit`, and `christian-life`.

Do not use generic document/source labels as tags, including `commentary`, `sermon`, `devotional`, `english`, `spanish`, author names, collection names, or publication formats. Do not use Bible books, chapters, verses, or reference abbreviations as tags. A fallback tag such as `christian-life` is acceptable when the document's specific theme cannot be determined reliably.

## Bible reference fields

When a document has a clear primary biblical passage, add these custom frontmatter fields:

```yaml
bible_reference: "<abbrev> <chapter>:<verse>[-<last-verse>]"
bible_book_key: <book_key>
bible_book_name: "<name>"
```

`bible_reference` must use the abbreviation table below and the format `<ref> <chapter>:<verse>[-<last-verse>]`; do not place Bible references in `tags`. If a document's primary scope is an entire chapter but no specific verse range is known, omit `bible_reference` rather than inventing a verse range; still add `bible_book_key` and `bible_book_name` when the book is known.

| book_key | name | abbrev |
|---:|---|---|
| 1 | Genesis | ge |
| 2 | Exodus | ex |
| 3 | Leviticus | le |
| 4 | Numbers | nu |
| 5 | Deuteronomy | de |
| 6 | Joshua | jos |
| 7 | Judges | jud |
| 8 | Ruth | ru |
| 9 | 1 Samuel | 1sa |
| 10 | 2 Samuel | 2sa |
| 11 | 1 Kings | 1ki |
| 12 | 2 Kings | 2ki |
| 13 | 1 Chronicles | 1ch |
| 14 | 2 Chronicles | 2ch |
| 15 | Ezra | ezr |
| 16 | Nehemiah | ne |
| 17 | Esther | es |
| 18 | Job | job |
| 19 | Psalms | ps |
| 20 | Proverbs | pr |
| 21 | Ecclesiates | ec |
| 22 | Song of Solomon | so |
| 23 | Isaiah | isa |
| 24 | Jeremiah | jer |
| 25 | Lamentations | la |
| 26 | Ezekiel | eze |
| 27 | Daniel | da |
| 28 | Hosea | ho |
| 29 | Joel | joe |
| 30 | Amos | am |
| 31 | Obadiah | ob |
| 32 | Jonah | jon |
| 33 | Micah | mic |
| 34 | Nahum | na |
| 35 | Habakkuk | hab |
| 36 | Zephaniah | zep |
| 37 | Haggi | hag |
| 38 | Zechariah | zec |
| 39 | Malachi | mal |
| 40 | Matthew | mt |
| 41 | Mark | mr |
| 42 | Luke | lu |
| 43 | John | joh |
| 44 | Acts | ac |
| 45 | Romans | ro |
| 46 | 1 Corinthians | 1co |
| 47 | 2 Corinthians | 2co |
| 48 | Galatians | ga |
| 49 | Ephesians | eph |
| 50 | Philippians | php |
| 51 | Colossians | col |
| 52 | 1 Thessalonians | 1th |
| 53 | 2 Thessalonians | 2th |
| 54 | 1 Timothy | 1ti |
| 55 | 2 Timothy | 2ti |
| 56 | Titus | tit |
| 57 | Philemon | phm |
| 58 | Hebrews | heb |
| 59 | James | jas |
| 60 | 1 Peter | 1pe |
| 61 | 2 Peter | 2pe |
| 62 | 1 John | 1jo |
| 63 | 2 John | 2jo |
| 64 | 3 John | 3jo |
| 65 | Jude | jude |
| 66 | Revelation | re |

## Indexes

Every content directory has a frontmatter-free `index.md` with a title and `# Contents` list. Do not create `_index.md` or `README.md` navigation documents. This matches OKF reserved `index.md` progressive-disclosure listings.

Regenerate wiki indexes with `python3 .tools/scripts/wiki_tool.py build` after adding or renaming wiki pages. Source-tree indexes remain hand-maintained when sources move (never rewrite source document bodies).

## Knowledge layers and ownership

This vault has four distinct content/retrieval layers:

- `raw/` is an unindexed staging ground for unprocessed files. Agents may inspect staged files during an ingest but must not rewrite their contents. After classification, move each processed file unchanged into the appropriate `sources/` directory and update both navigation indexes.
- `sources/` contains immutable evidence. Agents may read source documents but must not rewrite, normalize, retag, or otherwise edit them during wiki work. Navigation-only `index.md` files are the exception and may be maintained.
- `wiki/` contains LLM-maintained synthesis. Agents create and revise these pages as new evidence and durable investigations are integrated.
- `.qmd/` contains committed qmd configuration, benchmarks, and guarded operational scripts. Generated SQLite files are local artifacts and must not be committed.

Supporting producer layers (not evidence, not synthesis):

- `schema/` — OKF-aligned frontmatter rules, lint checklist, workflows, command reference, and `source-manifest.jsonl`.
- `_templates/` — note templates matching this vault's frontmatter and body sections.
- `.tools/scripts/` — deterministic `wiki_tool.py` and `audit_public.py` maintenance tooling.
- `.agents/skills/` — ingest, query, lint, and maintain skill playbooks for agents.

The vault root contains navigation and agent instructions, not content documents. Personal notes belong in `sources/personal-notes/`.

**Agent rules (summary):**

- Treat `raw/` and `sources/` as source material, not as compiled notes.
- Write reusable knowledge only under `wiki/`.
- Keep every compiled note linked to one or more sources (or a wiki source-note that does).
- Search `wiki/catalog.jsonl` (via `wiki_tool.py search-catalog`) before opening broad source context.
- Run `build`, `lint`, source checks, and `audit_public` before meaningful commits.
- Do not invent citations or create unsupported claims.

## Wiki page conventions

Wiki pages follow the vault-wide metadata rules and may add operational properties. A typical concept page begins with:

```yaml
---
type: Biblical Concept
title: Prayer in Christian Life
description: A source-backed synthesis of prayer's purpose, practice, and theology.
tags: [prayer, christian-life]
status: developing
updated: 2026-07-16
source_count: 4
---
```

Use `status: seed`, `status: developing`, or `status: reviewed`. Update `updated` and `source_count` whenever the synthesis changes materially.

Concept, person, passage, source-note, and question pages should use the relevant portions of this structure:

```markdown
# Page Title

## Summary

## Core claims

## Agreements and tensions

## Biblical passages

## Related pages

## Sources

## Open questions
```

Templates for these pages live in `_templates/`.

Every material interpretive claim must be traceable to at least one source link. Use full-path Obsidian wikilinks for internal evidence because source filenames such as `chapter-1.md` are not unique:

```markdown
[[sources/commentaries_english/mhenry-complete/volume-4/joel/chapter-1#Threatenings of Judgment (720 BC)|Matthew Henry on Joel 1]]
```

Record meaningful disagreements in `## Agreements and tensions`; do not flatten distinct interpretations into a false consensus. Clearly distinguish source claims, synthesis, and unresolved questions.

## Catalog and source manifest

- `wiki/catalog.jsonl` — one JSON object per compiled wiki note (path, title, type, tags, description, status, source_count, updated) plus derived retrieval fields (`bible_references`, `source_paths`, `related_paths`, `headings`, optional `aliases`). Rebuild with `wiki_tool.py build`.
- `wiki/indexes/` — generated reverse indexes (`by-tag`, `by-passage`, `by-source`, `by-type` JSONL). Rebuild with `wiki_tool.py build`; do not hand-edit.
- `schema/source-manifest.jsonl` — inventory of `sources/**/*.md` with optional `covered_by` wiki paths. Coverage is derived from wiki links and `source_path`; **never** by rewriting source files. Most of the commentary corpus is intentionally uncovered until ingested into synthesis.

## Ingest workflow

When the user asks to ingest a source:

1. Locate the unprocessed file in `raw/`, classify it, and move it unchanged into the appropriate `sources/` directory. If it is already under `sources/`, leave it in place.
2. Do not modify the source document; update the affected `raw/index.md` and source `index.md` navigation files.
3. Run `.qmd/bin/update-safe` to refresh lexical search after the file is under `sources/`.
4. Search the wiki first for affected concepts, people, passages, and prior questions (`search-catalog`, then qmd wiki search).
5. Read the source and discuss its important takeaways with the user when appropriate.
6. Create or update a page in `wiki/source-notes/`.
7. Update every materially affected wiki page, including explicit source links and tensions.
8. Update the `index.md` of each changed content directory (or run `wiki_tool.py build` for wiki indexes).
9. Append an entry to `wiki/log.md` using `## [YYYY-MM-DD] ingest | Title` (or `wiki_tool.py log`).
10. Run `.qmd/bin/update-safe`, then `.qmd/bin/embed-wiki-safe` when semantic retrieval needs refreshing.
11. Review the Git diff and run the vault lint checks before reporting completion.

After synthesis changes, also run:

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/audit_public.py
```

## Query workflow

Search maintained synthesis before raw evidence. Prefer the enriched catalog, then wiki, then sources:

```bash
python3 .tools/scripts/wiki_tool.py search-catalog --query "query terms"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "mt 6"
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer
.qmd/bin/search-wiki-safe "natural-language or keyword question" --json
# Hosted sparse wiki BM25 (Qdrant Cloud; always vault-scoped):
.qmd/bin/qdrant-search "prayer and the Father" --channel wiki --json
```

Channel-level wiki search (debug / fallback):

```bash
qmd search "query terms" -c bible-wiki --json -n 10
.qmd/bin/semantic-wiki-safe "natural-language question" --json -n 10
.qmd/bin/qdrant-wiki-search "intercession" --json
```

Consult sources when the wiki is incomplete, a claim requires verification, or interpretations disagree:

```bash
# Preferred semantic evidence (Qdrant sources_e5; pilot: mhenry-concise):
.qmd/bin/qdrant-sources-search "how to pray without hypocrisy" --corpus mhenry-concise --json
.qmd/bin/qdrant-search "Spirit intercession" --channel both --json
# Lexical fallback (local qmd BM25; still useful for exact phrases):
qmd search "precise source terms" -c bible-sources --json -n 15
qmd search "personal note terms" -c bible-sources --json -n 10
```

Optional personal-notes **vector pilot** (only after `.qmd/bin/embed-notes-safe`; never a substitute for full commentary embedding):

```bash
.qmd/bin/semantic-notes-safe "pregunta personal" --format json -n 5
```

Use `qmd get` or `qmd multi-get` to retrieve the selected documents, or open `vault_rel_path` / wikilink fields from Qdrant hits. Cite the local wiki and source pages used in the answer. Map qmd URI path segments back to disk paths for wikilinks when needed. File an answer in `wiki/questions/` only when the user requests it or explicitly approves preserving it as a durable investigation.

On this server, do not use the full `qmd query` pipeline by default. Do not start a persistent qmd MCP or HTTP daemon. Query expansion and reranking load additional local models that are inappropriate for the machine's available memory. Prefer `.qmd/bin/search-wiki-safe` for local wiki merge; use `.qmd/bin/qdrant-search` for hosted wiki BM25 + sources E5 (requires `QCLOUD_BIBLE_CLUSTER_API_KEY`). See `.qmd/qdrant-cloud.md`.

## qmd resource safety

This server has limited CPU and memory. All routine index changes use the guarded scripts. Operational detail: `.qmd/README.md`.

- `.qmd/bin/update-safe` refreshes the SQLite/BM25 index inside a 768 MiB memory and 50% CPU limit.
- `.qmd/bin/embed-wiki-safe` embeds only `bible-wiki`, requires at least 1.5 GiB available memory, prevents concurrent embedding, uses one CPU context, and runs inside a 1.4 GiB memory and 50% CPU limit.
- `.qmd/bin/embed-notes-safe` embeds only the tiny `bible-personal-notes` pilot collection under tighter limits.
- `.qmd/bin/semantic-wiki-safe` runs an explicit vector-only, no-rerank query against `bible-wiki`. Do not substitute bare `qmd vsearch`; qmd 2.5.3 attempted to initialize the large query-expansion model during validation.
- `.qmd/bin/search-wiki-safe` merges catalog + BM25 wiki + vector wiki without loading expansion/rerank models.
- Hosted Qdrant Cloud holds sparse `wiki_bm25` and dense `sources_e5`. **Embedding compute is Qdrant Cloud Inference** (not local ONNX/FastEmbed). Use `.qmd/bin/qdrant-search` / `qdrant-sources-search` / `qdrant-wiki-search`. Do not load expand/rerank models.

Do not embed full `bible-sources` without explicit user approval. The personal-notes pilot is the only pre-approved **local qmd** vector slice outside `bible-wiki`; the approved **hosted** source pilot is mhenry-concise in Qdrant `sources_e5`. Files in `raw/` are never indexed or embedded. Do not remove the cgroup, batch-size, CPU, concurrency, or timeout protections. A killed or failed embedding job is preferable to placing other server services under memory pressure.

Missing generate/rerank models in `qmd doctor` are expected: they are intentionally not used in routine ops.

Run `.qmd/bin/benchmark-lexical` and `.qmd/bin/benchmark-multilingual` for resource-safe retrieval baselines. Do not use `qmd bench` on this server: it exercises vector, hybrid, and full-model backends, including models intentionally excluded from routine operation.

## Lint workflow

Periodic lint passes check:

- required frontmatter and valid thematic tags;
- valid Bible reference fields;
- a frontmatter-free `index.md` in every content directory;
- missing, broken, or ambiguous internal links;
- orphan wiki pages and missing reciprocal navigation;
- material claims without source links;
- inaccurate `source_count` values;
- unrecorded contradictions or stale synthesis;
- important recurring subjects that deserve a concept page.

Record lint work in `wiki/log.md` using `## [YYYY-MM-DD] lint | Scope`. The log is append-only except to correct an error in the entry currently being written.

**Maintenance gate (before meaningful commits):**

```bash
python3 .tools/scripts/wiki_tool.py doctor
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/audit_public.py
.qmd/bin/lint-wiki
```

Run `.qmd/bin/lint-wiki` after changing generated wiki pages or navigation. See `schema/lint-checklist.md` and `.agents/skills/llm-wiki-lint/SKILL.md`.

## Agent skills

| Skill | Path |
|---|---|
| Ingest | `.agents/skills/llm-wiki-ingest/SKILL.md` |
| Query | `.agents/skills/llm-wiki-query/SKILL.md` |
| Lint | `.agents/skills/llm-wiki-lint/SKILL.md` |
| Maintain | `.agents/skills/llm-wiki-maintain/SKILL.md` |

## Tooling reference

See `schema/command-reference.md` for the full command list. Primary entry point:

```bash
python3 .tools/scripts/wiki_tool.py doctor|build|lint|source-scan|source-lint|source-delta|source-coverage|search-catalog|log
python3 .tools/scripts/audit_public.py
```
