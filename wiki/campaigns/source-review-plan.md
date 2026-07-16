---
type: Campaign Plan
title: Source-review plan
description: Section-by-section campaign to flesh out the wiki as the primary retrieval surface.
tags: [christian-life]
status: developing
updated: 2026-07-16
source_count: 0
---

# Source-review plan

## Goal

Make the compiled wiki dense enough that ordinary biblical and pastoral questions are answered from `wiki/` first. Sources remain immutable evidence; source search is for verification, disagreement, and missing depth—not the default product.

## Products

| Product | Role |
|---|---|
| Passage atlas | Chapter/pericope synthesis linked to concise (then complete) commentary |
| Concept graph | Cross-cutting doctrine and practice with multi-source claims and tensions |
| Source notes | Selective digests of rich, personal, or contested sources |
| People / questions | Named figures and durable investigations as needed |
| Campaign tracker | Progress and section status |

## Section units

| Corpus | Section unit |
|---|---|
| mhenry-concise | Book → chapter file |
| mhenry-complete | Same chapter when deepening a hub |
| chspurgeon-sermons | Theme or passage batch (not sequential 1–3536) |
| chspurgeon-tod | Psalm / volume |
| fcb / mae | Month, only for thematic enrichment |
| personal-notes | Whole note |

## Per-section workflow

1. Pick section from [[wiki/campaigns/tracker|tracker]].
2. Search catalog and wiki for related pages.
3. Read the section (do not rewrite the source).
4. Optional source-note if the material is dense, personal, or contested.
5. Create or update passage pages.
6. Fan claims into concept (and people) pages; record agreements and tensions.
7. Mesh related-page links.
8. Run `wiki_tool.py build`, `lint`, `source-scan --update --accept-covered`, `source-lint`, `audit_public`.
9. Append `wiki/log.md` entry.
10. Mark the section reviewed on the tracker.
11. Smoke-test 1–3 natural questions against wiki-only search.

## Quality bar

- Material claims cite full-path source wikilinks.
- No invented citations.
- Status: `seed` → `developing` when multi-source and multi-claim; `reviewed` only after a second pass or explicit QA.
- Prefer synthesis density over coverage percentage.
- Do not create empty stubs or one wiki page per Spurgeon sermon.

## Phase order

1. **Phase 0** — Operating system (this plan, tracker, core query suite). **Done.**
2. **Phase 1** — Personal notes (vault voice). **Done.**
3. **Phase 2** — mhenry-concise NT backbone. **Done.**
4. **Phase 3** — Remaining source ingest. **Done** (see tracker):
   - **3.1** mhenry-concise OT priority (Genesis, Psalms, Isaiah, Proverbs)
   - **3.2** mhenry-concise OT remainder (all other OT books)
   - **3.3** Spurgeon sermons as theme/hub batches (not sequential)
   - **3.4** Treasury of David (Psalm / volume + hub thickening)
   - **3.5** mhenry-complete hub deepening (on demand hubs)
   - **3.6** FCB / MAE thematic enrichment (not calendar mirror)
   - **3.7** articles / books / transcripts empty waiting state
   - **3.8** Concept mesh checkpoint (continuous; hubs at `developing`)
5. **Phase 4+** — QA polish: query-suite smokes, second-pass concept `reviewed`, lint sweeps. **Queued.**

## Anti-goals

- Mass-ingest to inflate coverage %.
- Rewriting `sources/` or `raw/`.
- Embedding full `bible-sources` without approval.
- Flattening Henry and Spurgeon into false consensus.
