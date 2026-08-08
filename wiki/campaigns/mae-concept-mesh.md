---
type: Campaign
title: MAE Concept Mesh (temporary runbook)
description: Phased subagent runbook to mesh Spurgeon Morning and Evening into concept hubs without month inventory notes.
tags: [christian-life, prayer, worship, christ]
status: developing
updated: 2026-08-08
---

# MAE Concept Mesh — Temporary Subagent Runbook

**Temporary.** Delete this page (and demote tracker pointers) when all twelve calendar months are concept-meshed and remaining month inventory notes are gone.

**Goal:** Turn Spurgeon *Morning and Evening* (`sources/commentaries_english/chspurgeon-mae/`) into **durable claims on concept pages**, not calendar inventory source-notes.

**User rule (2026-08-08):** mesh into concepts; **no month notes**.

---

## Status board

| Month | Day files | Concept mesh | Month inventory note | Notes |
|---|---:|---|---|---|
| January | 31 | **done** (2026-08-08) | **removed** | Template month — copy this pattern |
| February | 29 | **done** (2026-08-08) | **removed** | Concept-meshed; 29/29 day files linked |
| March | 31 | **done** (2026-08-08) | **removed** | Concept-meshed; 31/31 day files linked |
| April | 30 | **done** (2026-08-08) | **removed** | Concept-meshed; 30/30 day files linked |
| May | 31 | **done** (2026-08-08) | **removed** | Concept-meshed; 31/31 day files linked |
| June | 30 | **done** (2026-08-08) | **removed** | Concept-meshed; 30/30 day files linked |
| July | 31 | pending | exists | |
| August | 31 | pending | exists | |
| September | 30 | pending | exists | |
| October | 31 | pending | exists | |
| November | 30 | pending | exists | |
| December | 31 | pending | exists | |

**Source tree:** `sources/commentaries_english/chspurgeon-mae/<month>/<month>-N.md`  
Each day file has **Morning** and **Evening** sections (two readings per day).

**Legacy inventory notes to remove as each month meshes:**

```
wiki/source-notes/Spurgeon Morning and Evening — July.md
wiki/source-notes/Spurgeon Morning and Evening — August.md
wiki/source-notes/Spurgeon Morning and Evening — September.md
wiki/source-notes/Spurgeon Morning and Evening — October.md
wiki/source-notes/Spurgeon Morning and Evening — November.md
wiki/source-notes/Spurgeon Morning and Evening — December.md
```

(January–June already removed.)

**Related:**

- [[wiki/source-notes/Spurgeon Morning and Evening Theme Enrichment|Theme Enrichment]] — sample note; keep until months are meshed; update when a month completes
- [[wiki/campaigns/tracker|Campaign tracker]] §4.5 — coverage history; mesh progress lives here
- Concept hubs under `wiki/concepts/`

---

## Non-negotiables

1. **Do not create or keep month inventory source-notes** for meshed months. No “one bullet per day file list.”
2. **Do not create one wiki page per calendar day.**
3. **Do not rewrite** `sources/` bodies. Read only.
4. **Every material claim** must cite a full-path source wikilink, e.g.  
   `[[sources/commentaries_english/chspurgeon-mae/february/february-3|Spurgeon Morning and Evening, February 3]]`
5. MAE is **applicative / pastoral**. Doctrine weight stays on Henry, sermons, McGee, etc. Add a tension bullet when first introducing MAE claims to a concept (see January wording).
6. Prefer **existing concept pages**. Create a new concept only if a durable theme has no home and the user approved (anti-synonym rule).
7. After edits: **every day file in the month must be linked from at least one wiki concept** (coverage via concept Sources / claim links, not a month note).
8. `source_count` must equal unique `sources/` links under that page’s `## Sources` section.

---

## Phase overview (campaign-level)

| Phase | Name | Owner | Exit criteria |
|---:|---|---|---|
| 0 | Orientation | any agent | Read this runbook + January mesh pattern; list target month |
| 1 | Month harvest | subagent (1 month) | Theme map for all days (M+E); candidate claims drafted |
| 2 | Concept mesh | subagent (1 month) | Claims + Sources on concepts; all day files linked; month note deleted |
| 3 | Gate | subagent or orchestrator | `build`, coverage, lint, log, status board updated |
| 4 | Closeout | orchestrator | All 12 months done; remove remaining inventory notes; delete this runbook |

**Subagent unit of work = one calendar month** (Phases 0–3 for that month). Do not fan out half-months unless the user asks.

---

## Phase 0 — Orientation (every subagent, every month)

1. Read this file end-to-end.
2. Confirm month status is **pending** on the status board above.
3. Skim one completed concept that already has January MAE claims (template quality):  
   - `wiki/concepts/Prayer.md`  
   - `wiki/concepts/Christ.md`  
   - `wiki/concepts/Faith.md`
4. Catalog check (do not invent hubs):

```bash
python3 .tools/scripts/wiki_tool.py search-catalog --type "Biblical Concept" --limit 40
ls wiki/concepts/
```

5. Locate sources:

```bash
ls sources/commentaries_english/chspurgeon-mae/<month>/
```

---

## Phase 1 — Month harvest (read + route)

### 1.1 Extract every reading

For each `sources/commentaries_english/chspurgeon-mae/<month>/<month>-N.md`:

- Capture **Morning** quote ref + first substantive idea  
- Capture **Evening** quote ref + first substantive idea  
- Prefer the theological / applicative point, not a truncated first sentence dump

Optional helper sketch (adapt month name):

```bash
python3 - <<'PY'
from pathlib import Path
import re
month = "february"  # change per slice
root = Path(f"sources/commentaries_english/chspurgeon-mae/{month}")
days = sorted(root.glob(f"{month}-*.md"), key=lambda p: int(p.stem.split("-")[1]))
for p in days:
    t = p.read_text()
    for part in ("Morning", "Evening"):
        m = re.search(rf"## {part}\n\n(.+?)(?=\n## |\Z)", t, re.S)
        if not m: continue
        sec = m.group(1)
        ref = re.search(r"> “([^”]+)” — ([^\n]+)", sec)
        body = re.sub(r"^>.*\n\n?", "", sec, count=1, flags=re.M)
        body = re.sub(r"\s+", " ", body).strip()[:280]
        print(f"{p.stem} {part} | {ref.group(2).strip() if ref else '?'}")
        print(f"  {body}\n")
PY
```

### 1.2 Route to concepts

Map each durable idea to an existing hub. Typical homes (January used these):

| Hub | Common MAE themes |
|---|---|
| Prayer | continue in prayer, sinking times, promises, closet, corporate stirring |
| Intercession | Christ’s never-ceasing prayer |
| Christ | fullness, fellowship, help, brotherhood, Lamb, belonging |
| Covenant | “I will be their God,” federal head, covenant-in-Christ |
| Grace | grow in grace, renewal, humbling of the vine |
| Faith | care-casting, assurance, rocky ground, providence, “Believe and live” |
| Salvation | whole work “to save,” live to Christ, security of Israel |
| Hope | rest, see God, forward gaze, ark/rest |
| Worship | joy, iniquity of holy things, delight, wonder, praise |
| Holiness | perfection in Christ, vanity, temptation, new-rule obedience |
| Justification | Lord our Righteousness, complete in him |
| Atonement | sinless yet cut off, types (Abel, etc.) |
| Redemption | bloody purchase, “ye are Christ’s” |
| Church | bridal titles, prayerful body |
| Discipleship | prepare the way, Martha cumbered, ponder, live to Christ, witness |
| Spiritual Warfare | snare of the fowler, constant temptation |
| Suffering | he careth, evening hand, providence |
| Creation | light / gospel light |
| Word of God | opens Scripture / understanding |
| Holy Spirit | light, conviction, unction |

Also consider when the month clearly warrants it: Resurrection, Repentance, Surrender, Stewardship, Wisdom, Sin and the Fall, Pastoral Ministry, etc.

**Routing rules:**

- One day may feed **multiple** concepts (morning → one hub, evening → another).
- Prefer **2–8 high-quality claims per concept per month**, not 60 micro-claims.
- Still **link every day file** somewhere (claim and/or `## Sources`) so coverage does not depend on the inventory note.
- Skip pure fluff; keep what a future agent would want when answering a doctrine/practice question.

### 1.3 Deliverable of Phase 1

A short routing table (in the agent transcript or a scratch section of the log entry):

```text
Feb 1 M → Hope | claim: …
Feb 1 E → Worship | claim: …
…
Days with no concept yet: (must be empty before Phase 2 ends)
```

---

## Phase 2 — Concept mesh (write wiki)

### 2.1 Edit concept pages

For each affected `wiki/concepts/*.md`:

1. **Core claims** — add synthesized bullets (paraphrase + cite), not raw first-line dumps.  
   Example shape:

   ```markdown
   - Sinking times are praying times: distress drives the soul to petition it neglected in calm. [[sources/commentaries_english/chspurgeon-mae/january/january-14|Spurgeon Morning and Evening, January 14]]
   ```

2. **Summary** — one short sentence that the month’s MAE material was meshed (avoid duplicating if already present for that month).

3. **Agreements and tensions** — if this concept did not already have the MAE caution, add:

   ```markdown
   - Spurgeon *Morning and Evening* is brief and applicative: use for pastoral color and experiential edges; do not overweight against fuller Henry/sermon treatments of the same doctrines.
   ```

4. **Sources** — add each newly cited day file under `## Sources` (unique paths only).

5. **Frontmatter** — set `updated:` to today; set `source_count:` to the count of **unique** `sources/` targets listed under `## Sources`.

### 2.2 Coverage completeness

Before deleting the month note, verify every day file is linked from concepts:

```bash
python3 - <<'PY'
from pathlib import Path
import re
month = "february"  # change
days = {int(p.stem.split("-")[1]) for p in Path(f"sources/commentaries_english/chspurgeon-mae/{month}").glob(f"{month}-*.md")}
linked = set()
for p in Path("wiki/concepts").glob("*.md"):
    for m in re.findall(rf"chspurgeon-mae/{month}/{month}-(\d+)", p.read_text()):
        linked.add(int(m))
print("missing from concepts:", sorted(days - linked))
print("linked", len(linked), "of", len(days))
PY
```

`missing` must be empty.

### 2.3 Remove the month inventory note

1. Delete `wiki/source-notes/Spurgeon Morning and Evening — <Month>.md`
2. Strip any wikilinks to that path from other wiki pages (other month notes, indexes if hand-edited, Theme Enrichment related lists).
3. Do **not** leave a replacement month note.

### 2.4 Update progress surfaces

1. This runbook status board → mark month **done** with date.  
2. `wiki/source-notes/Spurgeon Morning and Evening Theme Enrichment.md` — note the month as concept-meshed (summary).  
3. `wiki/campaigns/tracker.md` §4.5 row for that month → concept-meshed note (same style as January).

---

## Phase 3 — Gate (required before reporting done)

Run from vault root:

```bash
python3 .tools/scripts/wiki_tool.py build
python3 .tools/scripts/wiki_tool.py source-scan --update --accept-covered
python3 .tools/scripts/wiki_tool.py source-coverage   # expect 0 uncovered overall; MAE days covered via concepts
python3 .tools/scripts/wiki_tool.py lint
python3 .tools/scripts/wiki_tool.py source-lint
python3 .tools/scripts/lint_wiki.py
python3 .tools/scripts/audit_public.py
python3 .tools/scripts/wiki_tool.py log --title "ingest | Spurgeon MAE <Month> concept mesh" --details "Meshed <Month> into concepts; removed month inventory note; N day files linked from concept hubs."
```

**Accept only if:**

- lint / source-lint / lint_wiki / audit_public pass  
- no `source_count` mismatches  
- no uncited core claims  
- month inventory note path gone  
- all day files for the month appear in concept wikilinks  
- catalog rebuild no longer lists the deleted month note  

---

## Phase 4 — Campaign closeout (orchestrator only)

When **all 12 months** are concept-meshed:

1. Confirm zero files match `wiki/source-notes/Spurgeon Morning and Evening — *.md` except Theme Enrichment (optional: fold Theme Enrichment into concepts and delete it too).  
2. Update tracker §4.5 / §4.6 notes: MAE mesh complete; inventory strategy deprecated.  
3. Delete **this** runbook (`wiki/campaigns/mae-concept-mesh.md`) or mark `status: reviewed` and archive one line in `wiki/log.md`.  
4. Final `build` + lint gate.

---

## Subagent prompt template

Copy/paste for a month worker:

```text
You are meshing Spurgeon Morning and Evening for ONE calendar month into Bible Vault concept pages.

Read and follow: wiki/campaigns/mae-concept-mesh.md (all phases).
Month: <MONTH>   # e.g. February
Sources: sources/commentaries_english/chspurgeon-mae/<month>/
Template quality: wiki/concepts/Prayer.md, Christ.md, Faith.md (January MAE claims).

Hard rules:
- No month inventory source-note (delete existing for this month when mesh is done).
- No per-day wiki pages.
- Do not rewrite sources/.
- Durable paraphrased claims with full-path source wikilinks.
- Link every day file from at least one concept.
- MAE is applicative; keep doctrine weight on fuller sources; add tension note if missing.
- source_count = unique Sources links.
- Run Phase 3 gate; update status board in mae-concept-mesh.md, Theme Enrichment, tracker §4.5.

Report: routing summary, concepts touched, day coverage count, lint results, files deleted.
```

Parallelism: safe to run **different months** in parallel only if concepts’ edits are coordinated (merge conflicts on popular hubs: Prayer, Christ, Faith, Worship). Prefer **sequential months** or lock hub sets per agent.

---

## January template (completed 2026-08-08)

What “done” looked like for January:

- **31/31** day files linked from concepts  
- **20** hubs updated: Prayer, Intercession, Christ, Covenant, Grace, Faith, Salvation, Hope, Worship, Holiness, Justification, Atonement, Redemption, Church, Discipleship, Spiritual Warfare, Suffering, Creation, Word of God, Holy Spirit  
- Month note removed  
- Coverage held via concept links (no inventory)  
- Lint clean  

Use January claim wording as quality bar: short synthesis + citation, not “first sentence of morning truncated…”

---

## Anti-patterns (reject)

| Bad | Why |
|---|---|
| Recreate month source-note with 28–31 day bullets | User forbade month notes |
| One wiki page per day | Violates vault MAE rule |
| Claims without full-path source wikilinks | Lint fails; unverifiable |
| Only link mornings; ignore evenings | Half the corpus dropped |
| Dump inventory quotes as “synthesis” | Not meshable knowledge |
| Overwrite multi-source doctrine with MAE alone | False consensus / overweight devotionals |
| Leave day files uncovered after deleting month note | Coverage regression |
| Wrong `source_count` | `wiki_tool.py lint` fails |

---

## Quick file index for agents

| Path | Role |
|---|---|
| `wiki/campaigns/mae-concept-mesh.md` | **This runbook** (temporary) |
| `sources/commentaries_english/chspurgeon-mae/` | Immutable day sources |
| `wiki/concepts/*.md` | Write targets |
| `wiki/source-notes/Spurgeon Morning and Evening — <Month>.md` | Delete after that month meshes |
| `wiki/source-notes/Spurgeon Morning and Evening Theme Enrichment.md` | Progress note / sample residue |
| `wiki/campaigns/tracker.md` | §4.5 historical coverage + mesh status line |
| `wiki/log.md` | Append-only work log via `wiki_tool.py log` |

---

## Open decisions (do not block monthly slices)

- Whether Theme Enrichment remains after all months mesh, or is folded away.  
- Whether FCB (`chspurgeon-fcb`) gets the same “no month notes → concept mesh” pass later (out of scope unless user asks).  
- How thick each month’s mesh should be if concepts become crowded (prefer quality + coverage links over claim inflation).
