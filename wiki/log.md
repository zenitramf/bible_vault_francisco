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

## [2026-07-16] campaign | Phase 4.1 Complete Volume 6

- Full-file coverage for mhenry-complete/volume-6 (172 files). Passage atlas thickened where mapped. source-coverage --require-zero OK.

## [2026-07-16] campaign | Phase 4.1 Complete 100%

- All six Complete volumes reviewed; source-coverage --path mhenry-complete --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 1

- Full-file coverage for chspurgeon-tod/volume-1 (27 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 2

- Full-file coverage for chspurgeon-tod/volume-2 (27 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 3

- Full-file coverage for chspurgeon-tod/volume-3 (27 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 4

- Full-file coverage for chspurgeon-tod/volume-4 (26 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 5

- Full-file coverage for chspurgeon-tod/volume-5 (16 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 6

- Full-file coverage for chspurgeon-tod/volume-6 (28 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD Volume 7

- Full-file coverage for chspurgeon-tod/volume-7 (27 files). Psalm passages thickened. --require-zero OK.

## [2026-07-16] campaign | Phase 4.2 ToD 100%

- All seven ToD volumes reviewed; source-coverage --path chspurgeon-tod --require-zero OK.

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 1–10

- Volume source-notes for sermons volumes 1–10 (576 files). Path-scoped zero-uncovered OK (trailing-slash filters).

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 11–20

- Volume source-notes for sermons volumes 11–20 (602 files). Zero-uncovered OK.

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 21–30

- Volume source-notes for sermons volumes 21–30 (616 files). Zero-uncovered OK.

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 31–40

- Volume source-notes for sermons volumes 31–40 (574 files). Zero-uncovered OK.

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 41–50

- Volume source-notes for sermons volumes 41–50 (521 files). Zero-uncovered OK.

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 51–60

- Volume source-notes for sermons volumes 51–60 (523 files). Zero-uncovered OK.

## [2026-07-16] campaign | Phase 4.3 Sermons Volumes 61–63

- Volume source-notes for sermons volumes 61–63 (124 files). Zero-uncovered OK.

## [2026-07-16] campaign | Phase 4.3 Sermons 100%

- All sermon volume bands reviewed; source-coverage --path chspurgeon-sermons --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB January + front matter

- Month source-note for FCB January (31 day files) plus root preface/verses. Zero-uncovered for month path and root files.

## [2026-07-16] campaign | Phase 4.4 FCB February

- Month source-note for FCB February (29 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB March

- Month source-note for FCB March (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB April

- Month source-note for FCB April (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB May

- Month source-note for FCB May (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB June

- Month source-note for FCB June (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB July

- Month source-note for FCB July (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB August

- Month source-note for FCB August (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB September

- Month source-note for FCB September (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB October

- Month source-note for FCB October (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB November

- Month source-note for FCB November (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB December

- Month source-note for FCB December (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.4 FCB 100%

- All FCB months + root reviewed; source-coverage --path chspurgeon-fcb --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE January

- Month source-note for MAE January (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE February

- Month source-note for MAE February (29 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE March

- Month source-note for MAE March (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE April

- Month source-note for MAE April (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE May

- Month source-note for MAE May (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE June

- Month source-note for MAE June (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE July

- Month source-note for MAE July (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE August

- Month source-note for MAE August (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE September

- Month source-note for MAE September (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE October

- Month source-note for MAE October (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE November

- Month source-note for MAE November (30 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE December

- Month source-note for MAE December (31 files). --require-zero OK.

## [2026-07-16] campaign | Phase 4.5 MAE 100%

- All MAE months reviewed; source-coverage --path chspurgeon-mae --require-zero OK.

## [2026-07-16] campaign | Phase 4.6 concept mesh during full ingest

- Related-page mesh from hub concepts to Complete/ToD/sermon/FCB/MAE Phase 4 source-notes. No doctrinal false consensus; inventory links only.

## [2026-07-16] campaign | Phase 4 complete

- Phase 4.0–4.7 complete: full wiki coverage of chspurgeon-sermons (3536), mhenry-complete (1195), chspurgeon-tod (178), chspurgeon-fcb (368), chspurgeon-mae (366).
- Vault-wide source coverage 6836/6836 (0 uncovered).
- Ingest shape: Complete/ToD volume notes + passage thickens; sermon volume notes (no per-sermon wiki pages); FCB/MAE month notes; concept Related-page mesh.
- Gates: source-scan --accept-covered, path-scoped --require-zero, wiki lint, source-lint, doctor, audit_public, update-safe all pass.
- phase4_cover.py helper retained under .tools/scripts for future re-runs.
- Phase 5 QA polish remains optional next.

## [2026-07-16] campaign | Phase 5 Core Query Suite smoke

- Wiki-only smoke on Core Query Suite after Phase 4 closeout.
- Sampled 13 questions (1,3,6,7,9,10,12,13,15,16,18,19,20): 13 Hit / 0 Thin / 0 Miss.
- Primary pages: Romans 1/4/6/8/9/11/12, Matthew 6, Justification, Holiness, Discipleship, Prayer, Holy Spirit, What Sustains Christian Ministry, Ayudas, Little Known Bible Heroes path via Discipleship/Faith, Andy Doss note, Gómez pastor note.
- Retrieval: catalog strongest for refs/titles; search-wiki-safe adequate; vault-local NL can rank concepts above exact source-notes.
- Updated wiki/questions/Core Query Suite.md results section; tracker Phase 5.1 reviewed.
- No source rewrites; no concept status promotions this pass.

## [2026-07-16] maintain | Remove RAG stack

- Removed entire .qmd/ tree (local BM25, embeddings, benchmarks, Qdrant wrappers).
- Removed Qdrant/e5 scripts, .tools/venv-qdrant, pyproject/uv.lock, requirements-qdrant.
- Preserved LLM-wiki search: wiki_tool search-catalog, catalog.jsonl, reverse indexes, lint_wiki under .tools/scripts.
- Updated AGENTS.md, agent skills, schema docs, Core Query Suite, and campaign tracker for catalog-only retrieval.
- No Chroma, qmd, or vector RAG remains.

## [2026-07-16] maintain | AGENTS.md catalog-only context

- Rewrote AGENTS.md as agent operating manual for LLM-wiki retrieval without RAG.
- Documented catalog-first search (search-catalog, reverse indexes), wiki layout, out-of-scope vector/qmd/Chroma/Qdrant tooling, and post-RAG maintenance gate.
- Aligns with removal of .qmd and Qdrant stacks; query/ingest/lint skills already catalog-only.

## [2026-07-16] campaign | Phase 5 restructure (5.1–5.3 concept graph)

- Restructured Phase 5 into three concept-graph subphases (not coverage re-ingest).
- 5.1 Initial Core Query Suite smoke — already reviewed (13/13 Hits).
- 5.2 Expand concepts from source-notes + deepen seed→developing (pending).
- 5.3 Plan developing→reviewed promotion (pending); execution follows that plan.
- Candidate expand backlog seeded on tracker (Grace, Atonement, Hope, Adoption, Repentance, Assurance, Providence, Intercession, Love, Kingdom, Word/Scripture, Sin/Fall, Resurrection, Suffering, Election, Stewardship, Unity, …).
- Existing seeds to deepen: Creation, Worship, Pastoral Ministry, Spiritual Warfare, Christ-Centered Ministry.
- Updated wiki/campaigns/tracker.md and wiki/campaigns/source-review-plan.md.

## [2026-07-16] maintenance | Side-by-side index.base in build/lint

- build regenerates every non-root index.base + root bases.base
- lint/doctor enforce pairing; root must not have index.base
- wiki folder index.md files link Live database view
- docs/skills updated (AGENTS, command-reference, lint-checklist, naming, maintain skill)

## [2026-07-16] campaign | Phase 5.2.0 baseline inventory

- Concept inventory: 20 Biblical Concept pages (15 developing, 5 seed, 0 reviewed). Harvested 13 high-signal source-notes (5 Spurgeon theme batches, 2 FCB/MAE enrichments, Complete hub deepening, 5 personal notes); skipped volume/month inventory digests for theme harvest. Gap decisions for 5.2.1: 10 create (Grace, Atonement, Hope, Intercession, Repentance, Word of God/Scripture, Sin and the Fall, Resurrection, Suffering/Affliction, Stewardship); 6 defer (Adoption, Assurance, Providence, Love, Kingdom, Election); 2 merge (Unity→Church, Sanctification→Holiness). Seed thinness: Spiritual Warfare near bar (13 sources); Christ-Centered Ministry thinnest (1). Tracker 5.2.0 marked reviewed; 5.2 overall in_progress.

## [2026-07-16] campaign | Phase 5.2.1 expand seed concepts

- Created 10 seed concept pages: Grace, Atonement, Hope, Intercession, Repentance, Word of God, Sin and the Fall, Resurrection, Suffering, Stewardship. Each has multi-claim source-linked core claims, agreements/tensions, related mesh. Linked from parent theme batches, FCB/MAE enrichments, Complete hub, personal notes, and hub concepts (Salvation, Redemption, Prayer, etc.). Concept count 20→30 (15 developing, 15 seed). Deferred/merge decisions from 5.2.0 unchanged. Next: 5.2.2 deepen seeds to developing.

## [2026-07-16] campaign | Phase 5.2.2 deepen seeds to developing

- Promoted all 15 former seed concepts to developing. Wave A: Creation, Worship (+Ps 100/150, ToD 150, MAE). Wave B: Pastoral Ministry (+Gómez duty), Spiritual Warfare (status), Christ-Centered Ministry full rewrite (Henry 1 Tim 1, 2 Cor 3/12, personal 1:12, Spurgeon Feed My Sheep). Wave C: Grace, Atonement, Hope, Intercession, Repentance, Word of God, Sin and the Fall, Resurrection, Suffering, Stewardship thickened with additional source families/claims. Result: 30 Biblical Concept pages, all developing, 0 seed. Phase 5.2 overall reviewed. Next: 5.3 plan developing→reviewed.

## [2026-07-16] campaign | Phase 5.3.0 promotion plan locked

- Wrote full developing→reviewed promotion plan on tracker 5.3: hard/soft rubric R1–R10; source-family table; priority bands P0 pilot (Salvation, Justification, Faith) → P1 gospel → P2 life/Spirit → P3 church → P4 OT/word; 8-step second-pass checklist; anti-patterns and defer rules; expected thin risks (Creation, Justice; possibly Hope/Intercession/Resurrection). Execution schedule: inside 5.3 as subphases 5.3.1–5.3.6 (no Phase 6 split). Synced source-review-plan.md. Next: 5.3.1 pilot promotions.

## [2026-07-16] campaign | Phase 5.3 complete — all concepts reviewed

- Executed 5.3.1–5.3.6: second-pass promoted all 30 Biblical Concept pages to reviewed. Thickened Creation (+Ge2, Ps104), Intercession (+Heb7), Justice (+Amos5, Mic6 Concise). Pruned Phase-4 volume-inventory Related links (~21). Rubric R1–R7 pass on all. Suite-style catalog smoke 8/8 Hits. Residual defers: none. Phase 5 concept graph maturation complete.

## [2026-07-16] ingest | Treasury of Scripture Knowledge

- Ingested immutable TSK cross-reference table under sources/reference/tsk/ (tskxref.txt + readme.txt + provenance).
- Added wiki_tool.py tsk CLI (--ref/--chapter, markdown|plain|json).
- Source note wiki/source-notes/Treasury of Scripture Knowledge.md; tool-only integration (no mass passage injection).
- Documented in AGENTS.md, command-reference, workflow-examples, llm-wiki-query skill.

## [2026-07-17] ingest | ¿De Quién Es Tu Dinero? — Ringo Ayala

- Moved raw/De Quién Es Tu Dinero - Ringo Ayala.md → sources/transcripts/ (git mv, unchanged). Created wiki/source-notes/De Quien Es Tu Dinero - Ringo Ayala.md (7 core claims, 11 Bible refs, status seed). Updated wiki/concepts/Stewardship.md (source_count 4→5; new 1 Chr 29:11–14, Col 1:16, Dt 8:18, 1 Cor 4:2, Ps 50:10–12, Rom 14:12; new 2 open questions). Updated wiki/concepts/Faith.md (10→11; +1 stewardship-faith claim). Updated wiki/concepts/Worship.md (7→8; +1 giving-as-worship claim). raw/index.md emptied; sources/transcripts/index.md seeded (first transcript). Build/lint/source-lint/lint_wiki/audit_public all pass. Manifest coverage 6837→6838.

## [2026-08-05] ingest | McGee Notes & Outlines Pastoral Epistles + Philemon

- Staged cleaned full text: raw/mcgee-thru-the-bible/1-2-timothy-titus-philemon.md (J. Vernon McGee Thru the Bible Notes & Outlines; PDF 1-2_Timothy-Titus-Philemon.pdf from Bible_LLM_Raw)
- Added raw/mcgee-thru-the-bible/index.md and sources/commentaries_english/mcgee-thru-the-bible/index.md (promotion of chapter files still open)
- Created wiki/source-notes/McGee Notes and Outlines on Pastoral Epistles and Philemon.md (status developing)
- Thickened passage hubs with McGee claims + source_count 3: 1 Timothy 1, 1 Timothy 3, 2 Timothy 3, 2 Timothy 4, Titus 1, Titus 2, Philemon 1
- Layered McGee claims onto wiki/concepts/Pastoral Ministry.md (source_count 5)
- Maintenance: build (1408 catalog rows), source-scan --update --accept-covered (6837), source-lint pass, audit-public pass, doctor pass
- Lint residual (pre-existing, not this ingest): 9 broken wikilinks to sources/personal-notes/Little Known Bible Heroes
- Caveat: cleaned corpus remains in raw/ until split into immutable chapter files under sources/commentaries_english/mcgee-thru-the-bible/

## [2026-08-07] ingest | batch batch-e30abeb6-msj2kp3b

- status: partial
- discovered: 1
- ingested: 1
- failed: 0
- skipped: 0
- maintenance: issues
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1_Corinthians.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1_Corinthians.pdf.extract.md note=wiki/source-notes/1_Corinthians.md

## [2026-08-07] ingest | batch batch-228e3149-msj2z73y

- status: partial
- discovered: 1
- ingested: 1
- failed: 0
- skipped: 0
- maintenance: issues
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1_Corinthians.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1_Corinthians.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 Corinthians.md

## [2026-08-07] maintain | Relocate McGee 1 Corinthians PDF

- Moved PDF + extract sidecar from `sources/personal-notes/ingest/` → `sources/commentaries_english/mcgee-thru-the-bible/`.
- Rewrote wiki citations on the McGee 1 Corinthians source-note, hub passages (1, 2, 3, 11–13, 15), and concepts (Church, Holiness, Holy Spirit, Resurrection, Hope).
- These Notes & Outlines are commentary corpus, not personal notes.

## [2026-08-07] ingest | batch batch-fa652486-msj5k6y4

- status: partial
- discovered: 2
- ingested: 2
- failed: 0
- skipped: 0
- maintenance: issues
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1_John.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1_John.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 John.md
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1_Peter.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1_Peter.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 Peter.md

## [2026-08-07] maintain | McGee paths, Pastoral demote, Little Known removal

- Moved 1 John and 1 Peter PDFs + extracts from sources/personal-notes/ingest/ to sources/commentaries_english/mcgee-thru-the-bible/; rewrote wiki wikilinks to *.pdf.extract.md (lint-safe).
- Demoted McGee Pastoral Epistles source-note after faulty ingest; withdrew raw/mcgee-thru-the-bible claims from Pastoral Ministry and hub passages. Staged PDF: raw/1-2_Timothy-Titus-Philemon.pdf (currently empty file — verify before re-ingest).
- Removed Little Known Bible Heroes source-note and all wiki references (Faith, Discipleship, Church, campaigns tracker).
- Dropped chapter-only bible_reference values on McGee-touched 1 Cor / 1 John / 1 Peter passage pages.

## [2026-08-07] ingest | McGee Notes and Outlines on Pastoral Epistles and Philemon

- Moved `raw/1-2_Timothy-Titus-Philemon.pdf` → `sources/commentaries_english/mcgee-thru-the-bible/` (unchanged body).
- Created pdftotext extract sidecar `1-2_Timothy-Titus-Philemon.pdf.extract.md`.
- Rebuilt source-note from extract (status developing); restored McGee claims on Pastoral Ministry, Church, Word of God, and hub passages 1 Timothy 1/3, 2 Timothy 3/4, Titus 1/2, Philemon 1.
- Evidence wikilinks target the extract (lint-safe); `source_path` remains the PDF.

## [2026-08-07] ingest | batch batch-53e1a950-msjfomfx

- status: partial
- discovered: 1
- ingested: 1
- failed: 0
- skipped: 0
- maintenance: issues
- ingested [pdf]: sources/personal-notes/ingest/1-2_Chronicles.pdf extract=sources/personal-notes/ingest/1-2_Chronicles.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 and 2 Chronicles.md

## [2026-08-07] maintenance | McGee Chronicles path fix + gate

- Promoted sources/personal-notes/ingest/1-2_Chronicles.pdf (+ extract) to sources/commentaries_english/mcgee-thru-the-bible/
- Rewrote wiki citations and source-note paths to the commentary tree; cite extract sidecars
- Cleared personal-notes/ingest index; updated McGee series index
- Removed invalid chapter-only bible_reference fields on 1 Chronicles 17/29 and 2 Chronicles 7/36
- Fixed Mastra llm-wiki-ingest classifier (assist-agent-1) to route bare McGee Notes book PDFs to mcgee-thru-the-bible
- Ran build, source-scan, doctor, lint, source-lint, lint_wiki, audit_public

## [2026-08-07] ingest | batch batch-e801a565-msjk39x7

- status: partial
- discovered: 1
- ingested: 1
- failed: 0
- skipped: 0
- maintenance: issues
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1-2_Kings.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1-2_Kings.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 and 2 Kings.md

## [2026-08-08] ingest | batch batch-fb5c56bd-msjltxvb

- status: partial
- discovered: 3
- ingested: 3
- failed: 0
- skipped: 0
- maintenance: issues
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1-2_Samuel.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1-2_Samuel.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 and 2 Samuel.md
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/1-2_Thessalonians.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/1-2_Thessalonians.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 1 and 2 Thessalonians.md
- ingested [pdf]: sources/commentaries_english/mcgee-thru-the-bible/2_Corinthians.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/2_Corinthians.pdf.extract.md note=wiki/source-notes/McGee Notes and Outlines on 2 Corinthians.md

## [2026-08-08] ingest | batch batch-0f57bd7e-msjne17a

- status: failed
- discovered: 3
- ingested: 0
- failed: 3
- skipped: 0
- maintenance: skipped
- failed [pdf]: sources/commentaries_english/mcgee-thru-the-bible/Acts.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/Acts.pdf.extract.md (ToolInvocation must have a result: {"state":"output-error","toolCallId":"call-b3a1aca3-b4e6-43e2-aadb-0b08e39b052c-2","toolName":"bible_vault","args":{"operation":"read","path":"_templates/source-note.md"},"errorText":"Bible Vault reads are limited to wiki notes, their sources, and schema documentation."})
- failed [pdf]: sources/personal-notes/ingest/Amos-Obadiah.pdf extract=sources/personal-notes/ingest/Amos-Obadiah.pdf.extract.md (ToolInvocation must have a result: {"state":"output-error","toolCallId":"call-b9467d05-3ec3-4b26-bef4-7816d2a4684b-2","toolName":"bible_vault","args":{"operation":"read","path":"_templates/source-note.md"},"errorText":"Bible Vault reads are limited to wiki notes, their sources, and schema documentation."})
- failed [pdf]: sources/commentaries_english/mcgee-thru-the-bible/Colossians.pdf extract=sources/commentaries_english/mcgee-thru-the-bible/Colossians.pdf.extract.md (ToolInvocation must have a result: {"state":"output-error","toolCallId":"call-8eec2844-a7a0-4659-9d1a-96bd7d1477be-2","toolName":"bible_vault","args":{"operation":"read","path":"_templates/source-note.md"},"errorText":"Bible Vault reads are limited to wiki notes, their sources, and schema documentation."})

## [2026-08-08] maintain | McGee path fix, extract links, bible_reference cleanup + gate

- Promoted 2-3_John and Amos-Obadiah PDFs + extracts from sources/personal-notes/ingest/ to sources/commentaries_english/mcgee-thru-the-bible/ (workflow misfile)
- Rewrote vault-wide McGee claim/source wikilinks to *.pdf.extract.md (lint-safe); source_path remains PDF
- Removed chapter-only bible_reference fields on 49 McGee-touched passage pages (schema requires verse range)
- Fixed broken [[wiki/passages/2 Kings 1]] link in McGee Kings source-note (page does not exist)
- Cleared personal-notes/ingest index
- Gate: doctor pass, build, lint pass, source-lint pass, lint_wiki pass, audit_public pass
- Note: many workflow-created files still root-owned; recommend chown -R zen:zen on mcgee extracts and wiki source-notes/people
- Batch failure context: template reads of _templates/ blocked by bible_vault tool path allowlist (logged 2026-08-08)

## [2026-08-08] maintain | McGee classifier, templates allowlist, 2 Kings 1

- assist-agent-1 classify.ts: normalize McGee stems (hyphen/underscore); add dual-book packs (amos_obadiah, 2_3_john, etc.) so bare PDFs no longer fall to personal-notes/ingest
- bible-vault-tool resolveVaultPath: allow _templates/ reads (fixes batch fail reading source-note template)
- bible_vault_processor + synthesize-item: cite extract sidecars for PDF claims (lint-safe); source_path remains original PDF
- smoke-llm-wiki-ingest: cover Amos-Obadiah and 2-3_John routes
- Created wiki/passages/2 Kings 1.md (Henry Complete + McGee); restored Kings source-note and 2 Kings 2 links
- Gate: build, lint, lint_wiki, source-scan, source-lint, audit_public, doctor

## [2026-08-08] ingest | Spurgeon MAE January concept mesh

- Meshed all 31 January Morning and Evening days into concept hubs (no month inventory note). Removed wiki/source-notes/Spurgeon Morning and Evening — January.md. Claims + source links on Prayer, Intercession, Christ, Covenant, Grace, Faith, Salvation, Hope, Worship, Holiness, Justification, Atonement, Redemption, Church, Discipleship, Spiritual Warfare, Suffering, Creation, Word of God, Holy Spirit. Updated Theme Enrichment + campaign tracker 4.5 January. Rebuild/coverage 6851/6851; lint clean.

## [2026-08-08] docs | MAE concept-mesh runbook

- Added temporary wiki/campaigns/mae-concept-mesh.md phased subagent runbook (Jan done, Feb–Dec pending). Linked from tracker §4.5, Theme Enrichment, campaigns index.

## [2026-08-08] ingest | Spurgeon MAE February concept mesh

- Meshed February into concepts (20 hubs); removed month inventory note; 29/29 day files linked from concept hubs; Theme Enrichment and tracker §4.5 updated.

## [2026-08-08] ingest | Spurgeon MAE March concept mesh

- Meshed March into concepts; removed month inventory note; 31 day files linked from concept hubs.

## [2026-08-08] ingest | Spurgeon MAE April concept mesh

- Meshed April into concepts (23 hubs); removed month inventory note; 30/30 day files linked from concept hubs. Passion/Calvary early month; exaltation, covenant renewal, promise-prayer, and watchfulness later.

## [2026-08-08] ingest | Spurgeon MAE May concept mesh

- Meshed May into concepts; removed month inventory note; 31/31 day files linked from concept hubs (23 hubs).

## [2026-08-08] ingest | Spurgeon MAE June concept mesh

- Meshed June into concepts; removed month inventory note; 30 day files linked from concept hubs.

## [2026-08-09] ingest | Spurgeon MAE July concept mesh

- Meshed July into concepts; removed month inventory note; 31 day files linked from concept hubs.

## [2026-08-09] ingest | Spurgeon MAE August concept mesh

- Meshed August into concepts; removed month inventory note; 31 day files linked from concept hubs.

## [2026-08-09] ingest | Spurgeon MAE September concept mesh

- Meshed September into concepts; removed month inventory note; 30 day files linked from concept hubs.
