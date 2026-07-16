---
type: Schema Reference
title: Frontmatter Schema (OKF)
description: OKF v0.1 frontmatter rules and Bible Vault producer extensions.
tags: [okf, schema, metadata]
updated: 2026-07-16
---

# Frontmatter Schema (OKF)

This vault is an **OKF knowledge bundle** (Open Knowledge Format v0.1). OKF is a directory of UTF-8 markdown files with YAML frontmatter. There is no schema registry and no required proprietary tooling.

## Conformance (OKF §9)

A document is OKF-conformant when:

1. Every non-reserved `.md` file has a parseable YAML frontmatter block delimited by `---` lines.
2. Every frontmatter block contains a non-empty `type` field.
3. Reserved filenames `index.md` and `log.md` follow their reserved roles (see Indexes and Logs).

Consumers MUST tolerate unknown `type` values, unknown extra keys, missing optional fields, and broken cross-links. Producers in this vault additionally require stronger fields for wiki quality (below).

## Required fields (OKF)

| Field | Required by | Notes |
|---|---|---|
| `type` | OKF | Short string identifying the kind of concept. Not centrally registered. |

## Recommended fields (OKF)

| Field | Purpose |
|---|---|
| `title` | Human-readable display name |
| `description` | One-sentence summary for indexes and search |
| `resource` | Canonical URI for an underlying asset (omit for abstract ideas) |
| `tags` | YAML list of short strings for cross-cutting categorization |
| `timestamp` | ISO 8601 datetime of last meaningful change |

## Bible Vault producer requirements

For **wiki concept documents** (all non-reserved `.md` under `wiki/` except navigation-only pages), this producer requires:

| Field | Rule |
|---|---|
| `type` | Non-empty (OKF required) |
| `title` | Non-empty |
| `description` | Non-empty one-line summary |
| `tags` | Non-empty YAML list of thematic tags (see AGENTS.md) |

These are producer conventions that tighten OKF's recommended fields. Lint tools enforce them for `wiki/`; they do not rewrite immutable `sources/`.

## Producer-defined extensions (allowed by OKF §4.1)

Consumers MUST preserve unknown keys. This vault commonly uses:

| Field | Where | Purpose |
|---|---|---|
| `status` | wiki | `seed`, `developing`, or `reviewed` |
| `updated` | wiki | ISO date `YYYY-MM-DD` of last material change (date-only form of last-modified) |
| `source_count` | wiki | Integer count of evidence sources backing the page |
| `source_path` | wiki source-notes | Primary immutable source path under `sources/` |
| `bible_reference` | any | Primary passage: `"<abbrev> <chapter>:<verse>[-last]"` |
| `bible_book_key` | any | Integer book key (1–66) |
| `bible_book_name` | any | Canonical book display name |
| `append_only` | `wiki/log.md` | Operational marker for the vault log |
| `linkTitle`, `weight` | some sources | Legacy source navigation metadata; do not invent in wiki |

Prefer `updated` (date) for wiki operational tracking. Optional OKF `timestamp` (full datetime) MAY be added; do not remove `updated` when present.

## Example wiki concept

```yaml
---
type: Biblical Concept
title: Prayer
description: A source-backed synthesis of prayer as humble approach to the Father.
tags: [prayer, christ, holy-spirit, discipleship]
status: seed
updated: 2026-07-16
source_count: 4
---
```

## Example passage-scoped page

```yaml
---
type: Passage Study
title: 1 Timothy 1:12
description: Synthesis of Christ's call, enablement, and expectation of faithfulness.
tags: [christ, pastoral-ministry, discipleship]
status: seed
updated: 2026-07-16
source_count: 1
bible_reference: "1ti 1:12"
bible_book_key: 54
bible_book_name: "1 Timothy"
---
```

## Reserved filenames (OKF §3.1)

| Filename | Role |
|---|---|
| `index.md` | Directory listing for progressive disclosure. **No frontmatter** in this vault. |
| `log.md` | Update history for a scope. |

Do not use `index.md` or `log.md` as ordinary concept documents.

## Body conventions (vault)

OKF does not require body sections. This vault uses conventional headings for synthesis pages:

- `## Summary`
- `## Core claims`
- `## Agreements and tensions`
- `## Biblical passages`
- `## Related pages`
- `## Sources`
- `## Open questions`

Material claims in `## Core claims` MUST include a full-path wikilink to evidence under `sources/` or a wiki source-note. See AGENTS.md.

## Citations (OKF §8)

OKF recommends a `# Citations` section for external sources. This vault's primary evidence is local and immutable under `sources/`. Use:

1. Inline full-path wikilinks on claims, and
2. A `## Sources` section listing those paths.

External URLs MAY appear when a claim depends on them; prefer local sources when available.
