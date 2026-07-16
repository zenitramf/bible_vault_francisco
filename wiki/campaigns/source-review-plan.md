---
type: Campaign Plan
title: Source-review plan
description: Section-by-section campaign to flesh out the wiki as the primary retrieval surface; Phase 4 covers remaining corpora; Phase 5 expands and matures the concept graph.
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
- Status lifecycle:
  - **`seed`** — first synthesis; may be thin or single-angle.
  - **`developing`** — multi-source **and** multi-claim; tensions begun; usable for wiki-first answers.
  - **`reviewed`** — second-pass explicit QA (promotion rubric); not automatic after coverage.
- Prefer synthesis density over empty stubs; **Phase 4 additionally requires full file coverage** of remaining corpora (see tracker).
- Do not create empty stubs. For Spurgeon sermons, prefer **volume source-notes that cite every sermon file** over one wiki page per sermon.
- **Phase 5** grows concepts from **existing source-notes** first; do not re-ingest corpora to “find” themes.

## Phase order

1. **Phase 0** — Operating system (this plan, tracker, core query suite). **Done.**
2. **Phase 1** — Personal notes (vault voice). **Done.**
3. **Phase 2** — mhenry-concise NT backbone. **Done.**
4. **Phase 3** — Selective remaining ingest (concise OT full; others partial). **Done.**
5. **Phase 4** — **Full remaining-corpus coverage** into the wiki layer (see tracker):
   - **4.0** Coverage baseline and commit-per-subphase discipline
   - **4.1** mhenry-complete 100% (by Complete volume; thicken passage atlas)
   - **4.2** chspurgeon-tod 100% (every psalm file / volume)
   - **4.3** chspurgeon-sermons 100% (volume source-notes listing every sermon)
   - **4.4** chspurgeon-fcb 100% (month source-notes listing every day)
   - **4.5** chspurgeon-mae 100% (month source-notes listing every day)
   - **4.6** Concept mesh during slices
   - **4.7** Coverage closeout (0 uncovered in the five corpora)
   - **Done (2026-07-16).**
6. **Phase 5** — Concept graph expansion and maturation (see tracker):
   - **5.1** Initial step: Core Query Suite smoke (wiki-only). **Done.**
   - **5.2** Expand concepts from source-notes; deepen all `seed` → `developing`.
   - **5.3** Plan (and schedule) conversion of `developing` → `reviewed`.
   - Hygiene lint sweeps as needed.

## Phase 5 detail

### 5.1 — Initial smoke

Answer a sample of [[wiki/questions/Core Query Suite|Core Query Suite]] items from catalog + wiki only. Score Hit / Thin / Miss. Establishes a baseline before concept graph surgery.

### 5.2 — Expand and deepen to `developing`

| Workstream | Deliverable |
|---|---|
| Harvest | Themes in source-notes that lack a concept page |
| Expand | New concept pages as `seed` with ≥2 source-backed claims, meshed to parent notes |
| Deepen | Every `seed` (old + new) reaches multi-source multi-claim `developing`, or is explicitly deferred |
| Gate | `wiki_tool.py build` + `lint`; log; tracker rows |

**Primary harvest surfaces:** Spurgeon theme batches, FCB/MAE theme enrichments, Matthew Henry Complete hub deepening, personal notes, ToD/volume notes only where they assert thematic claims (not mere file lists).

**Anti-pattern:** Creating synonym stubs (e.g. Sanctification next to Holiness) without a source-driven distinction.

### 5.3 — Plan `developing` → `reviewed`

Write the promotion rubric, priority order, per-page checklist, and defer rules. Execution of promotions follows that plan (complete within 5.3 or as a subsequent phase if the plan says so). `reviewed` is never granted by coverage count alone.

Draft bar: multi-claim, multi-source, substantive tensions, curated Related pages, accurate `source_count`, residual open questions only, no invented citations.

## Section units (Phase 4 coverage)

| Corpus | Section unit | Coverage product |
|---|---|---|
| mhenry-complete | Complete volume (1–6) / book | Passage thicken + links to every Complete chapter file |
| chspurgeon-tod | ToD volume / psalm | Every psalm file linked; Psalm passage pages thickened |
| chspurgeon-sermons | Sermon volume (1–63), reviewed in bands | Volume source-note Sources list = all sermon files |
| chspurgeon-fcb | Calendar month | Month source-note Sources list = all day files |
| chspurgeon-mae | Calendar month | Month source-note Sources list = all day files |

A tracker row is `reviewed` only when uncovered count for that path scope is **zero**.

## Anti-goals

- Inflating coverage with empty stubs or broken links.
- One wiki page per Spurgeon sermon (use volume digests with full file lists instead).
- Rewriting `sources/` or `raw/`.
- Embedding full `bible-sources` without approval.
- Flattening Henry and Spurgeon into false consensus.
