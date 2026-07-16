---
type: Schema Reference
title: Naming Conventions
description: Paths, concept IDs, types, tags, and file naming for the Bible Vault OKF bundle.
tags: [okf, schema, naming]
updated: 2026-07-16
---

# Naming Conventions

## Bundle layers

| Path | Role |
|---|---|
| `raw/` | Unindexed staging; do not rewrite contents |
| `sources/` | Immutable evidence |
| `wiki/` | LLM-maintained synthesis (OKF concepts) |
| `schema/` | Producer rules, manifests, command docs |
| `_templates/` | Note templates for agents and humans |
| `.tools/scripts/` | Deterministic maintenance tooling |
| `.agents/skills/` | Agent skill playbooks |
| `.qmd/` | Guarded lexical/semantic retrieval config and scripts |

## Concept ID (OKF §2)

The concept ID is the file path within the bundle with the `.md` suffix removed.

Examples:

- `wiki/concepts/Prayer` ← `wiki/concepts/Prayer.md`
- `sources/personal-notes/Devotional on 1 Timothy 1_12`

## File names

- Prefer readable titles with spaces for wiki concept files (Obsidian-friendly): `Pastoral Ministry.md`.
- Avoid leading/trailing spaces and characters that break shell or markdown: `* ? : " < > |`.
- Reserved: never name a concept document `index.md` or `log.md`.
- Do not introduce `_index.md` or `README.md` as navigation substitutes.

## Wiki type values (producer set)

| `type` | Directory |
|---|---|
| `Biblical Concept` | `wiki/concepts/` |
| `Biblical Person` | `wiki/people/` |
| `Passage Study` | `wiki/passages/` |
| `Biblical Question` | `wiki/questions/` |
| `Source Note` | `wiki/source-notes/` |
| `Wiki Log` | `wiki/log.md` only |
| `Metadata Convention` | `AGENTS.md` |
| `Schema Reference` | `schema/*.md` |

OKF consumers must tolerate unknown types. Do not invent a parallel generic taxonomy (`topic`/`entity`/`project` tags as the primary type system).

## Tags

Tags are thematic, lowercase, hyphenated biblical concepts (see AGENTS.md). Examples: `covenant`, `prayer`, `pastoral-ministry`.

Not tags: source genres, languages, author names, Bible book abbreviations, chapter/verse references.

## Links

Prefer full-path Obsidian wikilinks for vault-internal evidence because short filenames collide:

```markdown
[[sources/commentaries_english/mhenry-concise/matthew/chapter-6|Matthew Henry Concise, Matthew 6]]
[[wiki/concepts/Prayer|Prayer]]
```

OKF also allows standard markdown links (`[title](/path.md)`). When writing new markdown links, prefer bundle-root-relative paths. Do not invent citations.
