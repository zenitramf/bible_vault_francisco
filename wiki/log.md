---
type: Wiki Log
title: Bible Wiki Log
description: Append-only chronological record of Bible Wiki ingests, filed queries, lint passes, and maintenance.
tags: [bible-study]
append_only: true
---

# Bible Wiki Log

## [2026-07-16] maintenance | Initialize persistent Bible Wiki

- Created the source and wiki layers.
- Moved the English commentary corpus to `sources/commentaries_english/` without changing source contents.
- Deprecated and removed the Chroma indexing subsystem.
- Added project-local qmd configuration with resource-constrained operations.
- Indexed all sources for BM25 retrieval and embedded only four seed wiki pages.
- Confirmed the embedding pilot stayed near 576 MiB RSS and 50% of one CPU.
- Disabled bare `qmd vsearch` after qmd 2.5.3 attempted to initialize its large query-expansion model; semantic wiki search now uses an explicit vector-only, no-rerank query.

## [2026-07-16] ingest | Devotional on 1 Timothy 1:12

- Created a source note for the existing personal devotional.
- Seeded pages for Christ-centered ministry, 1 Timothy 1:12, and the question of what sustains Christian ministry.
- Connected each synthesis page to the immutable source note.

## [2026-07-16] maintenance | Consolidate sources and add raw staging

- Moved the five root personal notes to `sources/personal-notes/` without changing their contents.
- Updated wiki citations and qmd context to the new source paths.
- Added `raw/` as an unindexed staging ground for files that have not yet been processed.

## [2026-07-16] maintenance | Bootstrap concept pages: Covenant, Creation, Redemption, Salvation, Faith

- Created five source-backed seed concept pages under `wiki/concepts/`.
- Principal evidence drawn from Matthew Henry (complete and concise) and Spurgeon sermons via BM25 search of `bible-sources` only; sources were not embedded.
- Covenant and Creation are currently Henry-heavy; Redemption, Salvation, and Faith include both Henry and Spurgeon.
- Updated `wiki/concepts/index.md`.
- Recorded interpretive tensions rather than manufacturing consensus, especially on particular redemption language and covenant administrations.
- Deferred bible_reference frontmatter where no single primary verse range was clear.

## [2026-07-16] maintenance | Bootstrap concept pages batch 2: Prayer, Holiness, Worship, Discipleship, Church

- Created five more source-backed seed concept pages from BM25 evidence in `bible-sources`.
- Principal sources: Matthew Henry (Matthew 6, John 4/17, Ephesians 4, Matthew 16) and Spurgeon (sermons 1532, 1890, 2650, 1159, 1761; Treasury Psalm 134).
- Updated concepts index.

## [2026-07-16] maintenance | Bootstrap concept pages batch 3: Pastoral Ministry, Prophecy, Justice, Christ, Holy Spirit

- Completed the planned fifteen-concept seed set (plus existing Christ-Centered Ministry).
- Pastoral Ministry integrates Henry, Spurgeon, and the Spanish personal note by Pastor Andrés Gómez.
- Prophecy seed is Henry-dominant; Spurgeon definitional hits were weak and not forced.
- Christ and Holy Spirit pages anchor deity/incarnation and Comforter/Pentecost themes with Henry and Spurgeon.
- Updated concepts index and recorded open questions for later deepening.

## [2026-07-16] maintenance | Mesh related-page links across concept seeds

- Added reciprocal concept links among the fifteen seed pages and Christ-Centered Ministry after the full concept set was created.

## [2026-07-16] maintenance | LLM Wiki core tooling and OKF schema

- Added schema/ OKF frontmatter rules, _templates/ for wiki page types, .tools/scripts/wiki_tool.py and audit_public.py, agent skills, catalog.jsonl, and source-manifest.jsonl.
- Preserved raw/sources/wiki/.qmd layers and AGENTS.md Bible conventions.
- Built catalog (19 wiki notes); manifest covers 6836 sources with 53 wiki-linked.
- Maintenance gate: doctor, build, lint, source-lint, audit_public, .qmd/bin/lint-wiki all passed.

## [2026-07-16] maintenance | Enrich catalog and reverse indexes

- Enriched wiki/catalog.jsonl with derived bible_references, source_paths, related_paths, and headings.
- Generated wiki/indexes reverse maps (by-tag, by-passage, by-source, by-type).
- Improved search-catalog ranking with --tag/--ref/--source/--type filters and match reasons.
- Rewrote wiki descriptions to drop ranking-killing boilerplate.
- Added passage seeds for Matthew 6:5–15 and Romans 8:26–27 linked from Prayer.

## [2026-07-16] maintenance | Add Spiritual Warfare concept page and mesh backlinks

- New wiki/concepts/Spiritual Warfare.md (status: seed, source_count: 12) synthesizing Matthew Henry on Ephesians 6, 1 Peter 5, James 4, and Matthew 4; six Spurgeon sermons (416, 419, 2201, 2707, 3143, 3466) and Faith's Checkbook June 17; plus the Spanish personal note on the pastor's interior war by Pastor Andrés Gómez. Backlinks added to Discipleship, Holy Spirit, Prayer, Faith, Holiness, Christ, Christ-Centered Ministry, and Pastoral Ministry. Catalog 21 -> 22; reverse indexes refreshed; doctor, build, lint, source-scan --accept-covered, source-lint, audit_public, lint-wiki all passed.
