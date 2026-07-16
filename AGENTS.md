---
type: Metadata Convention
title: Bible Vault Metadata Conventions
description: Agent operating rules for this LLM wiki vault—OKF metadata, catalog-first search, tags, Bible references, and maintenance without RAG.
tags: [scripture, bible-study]
---

# Bible Vault — Agent Conventions

This vault is an **LLM wiki** (compiled synthesis over immutable sources), not a vector RAG system. Agents answer from maintained `wiki/` pages, discover them via the **catalog**, and open `sources/` only when synthesis is thin or a claim needs verification.

There is **no** qmd, Chroma, Qdrant, embedding pipeline, or full-corpus BM25 index. Do not reintroduce them. Retrieval is deterministic tooling plus reading markdown.

This bundle is OKF (Open Knowledge Format v0.1). Every concept document has YAML frontmatter with a non-empty `type`, `title`, `description`, and `tags` list. Reserved `index.md` files do not have frontmatter. OKF requires only a non-empty `type` on concept documents; this producer also requires `title`, `description`, and thematic `tags`. Producers MAY add extension fields; consumers MUST tolerate unknown types and unknown keys. See `schema/frontmatter-schema.md`.

## How agents find knowledge (retrieval model)

**Order of operations for questions:**

1. **Catalog first** — ranked search over `wiki/catalog.jsonl` (metadata map of every compiled note).
2. **Open ranked wiki pages** — concepts, passages, source-notes, questions, people.
3. **Follow wikilinks and reverse indexes** — `wiki/indexes/` for browse-by-tag, passage, source, or type.
4. **Open specific sources only when needed** — use catalog `source_paths` / page `## Sources` links; never scan the whole commentary tree by default.

```bash
# Primary retrieval (always available; no models)
python3 .tools/scripts/wiki_tool.py search-catalog --query "prayer spirit intercession"
python3 .tools/scripts/wiki_tool.py search-catalog --ref "mt 6"
python3 .tools/scripts/wiki_tool.py search-catalog --tag prayer
python3 .tools/scripts/wiki_tool.py search-catalog --source "sermon_1532"
python3 .tools/scripts/wiki_tool.py search-catalog --type "Biblical Concept" --query "holiness"
python3 .tools/scripts/wiki_tool.py search-catalog --query "matthew 6" --limit 10
```

**What the catalog scores:** title, path, tags, aliases, description, type, Bible references (including book/chapter hints), linked source paths, and soft boosts for `status` / `source_count`. CLI hits include **match reasons** and derived refs—use them to pick pages.

**Catalog row fields (retrieval-facing):** `path`, `title`, `type`, `tags`, `description`, `status`, `source_count`, `updated`, `bible_reference` / `bible_references` / `bible_book_key(s)`, `source_paths`, `primary_source_path`, `related_paths`, `headings`, optional `aliases`.

**Reverse indexes** (rebuild with `build`; do not hand-edit):

| File | Use when |
|---|---|
| `wiki/indexes/by-tag.jsonl` | User names a theme (`prayer`, `salvation`, …) |
| `wiki/indexes/by-passage.jsonl` | User names a book/chapter/verse |
| `wiki/indexes/by-source.jsonl` | Trace which wiki pages cover a source file |
| `wiki/indexes/by-type.jsonl` | Restrict to Concept / Passage / Source Note / … |

**Out of scope (do not use or rebuild):**

- Vector stores, embeddings, hybrid/semantic rankers
- Hosted sparse/dense RAG (Qdrant or otherwise)
- Local qmd / Chroma / SQLite full-text indexes of `sources/` or `wiki/`
- Query-expansion or rerank models
- Scanning thousands of commentary files before searching the wiki

If the catalog looks wrong or empty after wiki edits, run `python3 .tools/scripts/wiki_tool.py build` and search again.

## Knowledge layers and ownership

Three content layers:

| Path | Role | Agent may |
|---|---|---|
| `raw/` | Unindexed staging | Inspect; move out unchanged; never rewrite bodies |
| `sources/` | Immutable evidence | Read; never rewrite, retag, or “normalize” bodies during wiki work (navigation `index.md` only is editable) |
| `wiki/` | LLM-maintained synthesis | Create, revise, link, rebuild catalog |

Supporting producer layers (not evidence, not synthesis):

- `schema/` — frontmatter rules, lint checklist, workflows, command reference, `source-manifest.jsonl`
- `_templates/` — note templates
- `.tools/scripts/` — `wiki_tool.py`, `lint_wiki.py`, `audit_public.py`
- `.agents/skills/` — ingest, query, lint, maintain playbooks

Vault root holds navigation and these agent instructions, not content notes. Personal notes live under `sources/personal-notes/`.

### Wiki layout

| Directory | Typical `type` | Contents |
|---|---|---|
| `wiki/concepts/` | `Biblical Concept` | Cross-cutting doctrine and practice hubs |
| `wiki/passages/` | `Passage Study` | Chapter/verse-range atlases |
| `wiki/source-notes/` | `Source Note` | One-source or batch synthesis notes |
| `wiki/people/` | `Biblical Person` | Persons (when present) |
| `wiki/questions/` | `Biblical Question` | Durable investigations (only when user wants them kept) |
| `wiki/campaigns/` | Campaign docs | Tracker / plans for large ingest campaigns |
| `wiki/indexes/` | Generated | Reverse indexes from `build` |
| `wiki/catalog.jsonl` | Generated | One JSON object per wiki concept page |
| `wiki/log.md` | Operational | Append-only work log |

### Agent rules (summary)

- Treat `raw/` and `sources/` as source material, not compiled notes.
- Write reusable knowledge only under `wiki/`.
- Keep every material claim linked to evidence (`sources/` or a wiki source-note that does).
- **Search the catalog before opening broad source context.**
- Run `build`, `lint`, `lint_wiki`, source checks, and `audit_public` before meaningful commits.
- Do not invent citations or create unsupported claims.
- Do not add embedding, vector-database, or external RAG subsystems.

## Tags

`tags` is a YAML list of short, lowercase, hyphenated strings for cross-cutting **Biblical concepts and themes**. Use tags such as `covenant`, `creation`, `redemption`, `faith`, `prayer`, `holiness`, `worship`, `discipleship`, `justice`, `prophecy`, `church`, `pastoral-ministry`, `salvation`, `christ`, `holy-spirit`, and `christian-life`.

Do not use generic document/source labels as tags, including `commentary`, `sermon`, `devotional`, `english`, `spanish`, author names, collection names, or publication formats. Do not use Bible books, chapters, verses, or reference abbreviations as tags. A fallback tag such as `christian-life` is acceptable when the document's specific theme cannot be determined reliably.

Tags power `--tag` catalog search and `wiki/indexes/by-tag.jsonl`. Keep them thematic and stable.

## Bible reference fields

When a document has a clear primary biblical passage, add these custom frontmatter fields:

```yaml
bible_reference: "<abbrev> <chapter>:<verse>[-<last-verse>]"
bible_book_key: <book_key>
bible_book_name: "<name>"
```

`bible_reference` must use the abbreviation table below and the format `<ref> <chapter>:<verse>[-<last-verse>]`; do not place Bible references in `tags`. If a document's primary scope is an entire chapter but no specific verse range is known, omit `bible_reference` rather than inventing a verse range; still add `bible_book_key` and `bible_book_name` when the book is known.

These fields (and derived `bible_references` on catalog rows) power `--ref` search and `wiki/indexes/by-passage.jsonl`.

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

## Indexes (navigation)

Every content directory has a frontmatter-free `index.md` with a title and `# Contents` list. Do not create `_index.md` or `README.md` navigation documents. This matches OKF reserved `index.md` progressive-disclosure listings.

Regenerate **wiki** folder indexes and the catalog with:

```bash
python3 .tools/scripts/wiki_tool.py build
```

Source-tree `index.md` files remain hand-maintained when sources move (never rewrite source document bodies).

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

Use `status: seed`, `status: developing`, or `status: reviewed`. Update `updated` and `source_count` whenever the synthesis changes materially. Accurate metadata improves catalog ranking and agent routing.

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

Templates live in `_templates/`.

Every material interpretive claim must be traceable to at least one source link. Use full-path Obsidian wikilinks for internal evidence because source filenames such as `chapter-1.md` are not unique:

```markdown
[[sources/commentaries_english/mhenry-complete/volume-4/joel/chapter-1#Threatenings of Judgment (720 BC)|Matthew Henry on Joel 1]]
```

Record meaningful disagreements in `## Agreements and tensions`; do not flatten distinct interpretations into a false consensus. Clearly distinguish source claims, synthesis, and unresolved questions.

## Catalog and source manifest

- `wiki/catalog.jsonl` — one JSON object per compiled wiki note. Rebuild with `wiki_tool.py build` after adding, renaming, or materially editing wiki pages.
- `wiki/indexes/` — generated reverse indexes (`by-tag`, `by-passage`, `by-source`, `by-type`). Rebuild with `build`; do not hand-edit.
- `schema/source-manifest.jsonl` — inventory of `sources/**/*.md` with optional `covered_by` wiki paths. Coverage is derived from wiki links and `source_path`; **never** by rewriting source files.

Coverage tracks intentional synthesis links, not automatic ingestion. Refresh coverage after linking sources:

```bash
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-coverage
```

## Query workflow

When the user asks a biblical, theological, or vault-knowledge question:

1. Run `search-catalog` with the best available signal (`--query`, and when known `--ref`, `--tag`, `--source`, `--type`).
2. Open the top wiki hits (prefer hubs with multiple sources and non-seed status when scores are close).
3. Answer from wiki synthesis; cite wiki paths and, when quoting evidence, the underlying source wikilinks.
4. Open `sources/` only if the wiki is incomplete, claims disagree, verification is required, or the user asks for source-level detail—then open **specific** paths from the catalog or page, not the whole corpus.
5. File under `wiki/questions/` only if the user requests or approves a durable investigation.

See also `.agents/skills/llm-wiki-query/SKILL.md`.

## Ingest workflow

When the user asks to ingest a source:

1. Locate the unprocessed file in `raw/`, classify it, and move it unchanged into the appropriate `sources/` directory. If it is already under `sources/`, leave it in place.
2. Do not modify the source document body; update the affected `raw/index.md` and source `index.md` navigation files.
3. Search the wiki first (`search-catalog`) for affected concepts, people, passages, and prior questions.
4. Read the source and discuss important takeaways with the user when appropriate.
5. Create or update a page in `wiki/source-notes/`.
6. Update every materially affected wiki page, including explicit source links and tensions; keep `source_count` accurate.
7. Run `wiki_tool.py build` so catalog and indexes include the new pages.
8. Append a log entry: `## [YYYY-MM-DD] ingest | Title` (or `wiki_tool.py log`).
9. Run the maintenance gate below and review the Git diff before reporting completion.

After synthesis changes:

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

See also `.agents/skills/llm-wiki-ingest/SKILL.md`.

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
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

- `wiki_tool.py lint` — producer checks on wiki concept pages (frontmatter, tags shape, claims, wikilinks, source_count).
- `lint_wiki.py` — complementary structural pass (indexes under wiki/sources trees, required fields, uncited claims, link resolution).
- `audit_public.py` — secrets / private keys / machine-local home paths.

See `schema/lint-checklist.md` and `.agents/skills/llm-wiki-lint/SKILL.md`.

## Agent skills

| Skill | Path | When |
|---|---|---|
| Query | `.agents/skills/llm-wiki-query/SKILL.md` | Answer questions from the wiki |
| Ingest | `.agents/skills/llm-wiki-ingest/SKILL.md` | Compile a source into wiki notes |
| Lint | `.agents/skills/llm-wiki-lint/SKILL.md` | Pre-commit / hygiene checks |
| Maintain | `.agents/skills/llm-wiki-maintain/SKILL.md` | Rebuild catalog, coverage, health |

## Tooling reference

Full command list: `schema/command-reference.md`. Workflows: `schema/workflow-examples.md`. Primary entry points:

```bash
python3 .tools/scripts/wiki_tool.py doctor|build|lint|source-scan|source-lint|source-delta|source-coverage|search-catalog|log
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
```

Optional pre-commit hooks (build + lint + source-lint + lint_wiki only):

```bash
bash .tools/scripts/install_hooks.sh
```
