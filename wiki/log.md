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

## [2026-07-16] ingest | Wisdom concept (Proverbs 16:16)

- Seeded wiki/concepts/Wisdom.md at Francisco's request after a vault question on Proverbs 16:16. Synthesis grounded in Matthew Henry Complete and Concise on Proverbs 3, 8, 16, and Job 28; Spurgeon Treasury of David on Psalm 119:97-104; Spurgeon sermon 1677 on Revelation 3:17-18. Seven sources. bible_reference omitted from frontmatter because the concept is multi-passage. Catalog rebuilt; lint, audit, and lint-wiki all pass.

## [2026-07-16] ingest | Surrender concept

- New wiki/concepts/Surrender.md seed synthesizing 'surrender' as a Biblical Concept (Christian-life, faith, discipleship, salvation, christ, holy-spirit, repentance, prayer). Anchored on James 4:7 via Spurgeon Sermon 1276 (Unconditional Surrender). Draws on 9 Spurgeon sources (sermons 1276, 1520, 1554, 1118, 3411; M&E Feb 24, Apr 2, Apr 6, May 6) and 4 Matthew Henry sources (Jer 21, 27, 38 concise + complete, 1 Kings 20). 13 distinct source files; source_count: 13.

## [2026-07-16] campaign | Phase 0–2 Romans concise + personal notes

- Created campaigns plan/tracker, Core Query Suite, ingested remaining personal notes, built Romans 1–16 passage atlas from mhenry-concise, new Justification concept, promoted hub concepts to developing, book source-note for Romans concise.

## [2026-07-16] campaign | Gómez source-note uniform + Matthew concise atlas

- Added dedicated source-note for Pastor Andrés Gómez and linked Pastoral Ministry/Spiritual Warfare. Built Matthew 1–28 passage atlas from mhenry-concise with book source-note; meshed Christ, Discipleship, Prayer, Church, Redemption; updated tracker. No embedding.

## [2026-07-16] campaign | Phase 2 NT mhenry-concise complete

- Completed remaining Phase 2 rows: all 27 NT books from mhenry-concise as chapter passage atlases (216 new chapters this pass + prior Romans/Matthew). Book source-notes for each; hub concept related links for John/Acts/Ephesians/Hebrews/James/Galatians/1 Timothy/1 Peter/Revelation. Fixed residual Romans anchors. No embedding.

## [2026-07-16] campaign | Phase 3.1 mhenry-concise OT priority

- Genesis 50, Psalms 150, Isaiah 66, Proverbs 31 passage atlases from mhenry-concise (297 chapters); 4 book source-notes; meshed Creation, Covenant, Faith, Wisdom, Prophecy, Prayer, Worship (+ Salvation/Christ/Redemption/Justification links); tracker 3.1 reviewed. No embedding.

## [2026-07-16] campaign | Phase 3 complete (3.1–3.8)

- Phase 3.2: 631 OT remainder chapters + 35 book source-notes. 3.3: 5 Spurgeon theme batches. 3.4: 7 ToD volume notes + hub Psalms thickened. 3.5: Complete hub deepening (10 hubs). 3.6: FCB/MAE theme enrichment notes. 3.7: empty trees waiting. 3.8: concept mesh (Justification/Justice developing). Full OT concise atlas (39 books). No embedding.

## [2026-07-16] lint | Obsidian wikilink normalization

- Converted vault-internal Markdown links in navigation and wiki pages to Obsidian wikilinks.
- Updated `wiki_tool.py` to generate and lint Obsidian-style internal links.
- Validation passed: `doctor`, `lint`, `source-lint`, `audit_public`, `.qmd/bin/lint-wiki`.

## [2026-07-16] campaign | Phase 4 plan — full remaining-corpus coverage

- Tracker and source-review-plan now define Phase 4 for 100% wiki coverage of chspurgeon-sermons, mhenry-complete, chspurgeon-tod, chspurgeon-fcb, chspurgeon-mae (~5.5k uncovered files). Subphases 4.0–4.7 with zero-uncovered gates; former QA polish moved to Phase 5. No content ingest yet.

## [2026-07-16] campaign | Phase 4.0 operating gate

- Re-ran source-scan --update --accept-covered: 6836 source docs, 1294 covered vault-wide.
- Phase 4 corpus baseline (files / covered / uncovered): sermons 3536/27/3509; mhenry-complete 1195/42/1153; fcb 368/6/362; mae 366/7/359; tod 178/19/159. Total 5643 / 101 / 5542.
- Extended wiki_tool.py source-coverage with --path, --uncovered-only, --require-zero, --limit, --verbose for zero-uncovered gates per volume/month/corpus.
- Documented gates in schema/command-reference.md and schema/workflow-examples.md; updated tracker 4.0 rows to reviewed and recorded measured baseline table.
- Commit-per-subphase discipline: one commit when each tracker sub-row flips to reviewed after path-scoped --require-zero passes. No content ingest in 4.0.

## [2026-07-16] campaign | Phase 4.1 Complete Volume 1

- Generated wiki/source-notes/Matthew Henry Complete Volume 1.md citing all 188 content files.
- Thickened 182 matching passage pages with Complete digest claims and Sources links.
- source-coverage --path mhenry-complete/volume-1 --require-zero OK.

## [2026-07-16] campaign | Phase 4.1 Complete Volume 2

- Full-file coverage for mhenry-complete/volume-2 (250 files). Passage atlas thickened where mapped. source-coverage --require-zero OK.

## [2026-07-16] campaign | Phase 4.1 Complete Volume 3

- Full-file coverage for mhenry-complete/volume-3 (244 files). Passage atlas thickened where mapped. source-coverage --require-zero OK.

## [2026-07-16] campaign | Phase 4.1 Complete Volume 4

- Full-file coverage for mhenry-complete/volume-4 (251 files). Passage atlas thickened where mapped. source-coverage --require-zero OK.

## [2026-07-16] campaign | Phase 4.1 Complete Volume 5

- Full-file coverage for mhenry-complete/volume-5 (90 files). Passage atlas thickened where mapped. source-coverage --require-zero OK.
