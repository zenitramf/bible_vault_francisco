---
type: Biblical Question
title: Core Query Suite
description: Benchmark questions used to test whether the wiki can answer without broad source RAG.
tags: [christian-life, faith, salvation, prayer, church, pastoral-ministry]
status: developing
updated: 2026-07-16
source_count: 0
---

# Core Query Suite

Use these questions after material wiki batches. Prefer catalog + wiki search only; open sources only to score a miss.

## Doctrine and gospel

1. How does the gospel reveal a righteousness from faith to faith (Romans 1)?
2. Why can no one be justified by works of the law (Romans 3)?
3. What is justification by faith, and how does Abraham illustrate it (Romans 4)?
4. What fruits follow justification—peace, access, hope (Romans 5)?
5. How are Adam and Christ related in condemnation and grace (Romans 5)?
6. Does free grace encourage sin? How does Romans 6 answer?
7. How does the Spirit help weak prayer (Romans 8:26–27)?
8. What does it mean that there is no condemnation in Christ (Romans 8)?
9. How should election and Israel’s unbelief be spoken of without pride (Romans 9–11)?
10. What is the living sacrifice of Romans 12:1–2?

## Christian life and church

11. How should strong and weak believers treat indifferent matters (Romans 14)?
12. What is holiness’s relation to justification without legalism?
13. What is Christian discipleship’s cost (self-denial, cross)?
14. How does the Spirit act as Comforter and Paraclete?
15. What sustains Christian ministry (1 Timothy 1:12 and related)?

## Pastoral and vault-local

16. What questions should I ask when studying a passage in context?
17. Which little-known Bible figures model hidden faithfulness?
18. How did a local sermon describe the Spirit (Andy Doss note)?
19. What is the pastor’s interior war and care for the flock (Andrés Gómez)?
20. How should prayer avoid hypocrisy (Matthew 6)?

## Scoring

After each major campaign slice, answer a sample of 5–10 items from wiki alone:

| Result | Meaning |
|---|---|
| Hit | Wiki pages suffice with source-backed claims |
| Thin | Wiki mentions topic but lacks claims or links |
| Miss | Must open sources or invent |

Target for Romans slice completion: hits on questions 1–10 from wiki passages/concepts without opening commentary files.

## Phase 5 smoke (2026-07-16)

Wiki-only path: `wiki_tool.py search-catalog` (no `sources/` opens for scoring). Sample of **13** suite items after Phase 4 full-corpus coverage (doctrine, life/church, pastoral/vault-local).

| # | Question (short) | Result | Primary wiki pages |
|---|---|---|---|
| 1 | Gospel righteousness faith to faith (Rom 1) | **Hit** | [[wiki/passages/Romans 1]], [[wiki/concepts/Faith]] |
| 3 | Justification by faith; Abraham (Rom 4) | **Hit** | [[wiki/passages/Romans 4]], [[wiki/concepts/Justification]] |
| 6 | Free grace and sin (Rom 6) | **Hit** | [[wiki/passages/Romans 6]], [[wiki/concepts/Holiness]] |
| 7 | Spirit helps weak prayer (Rom 8:26–27) | **Hit** | [[wiki/passages/Romans 8]], [[wiki/passages/Romans 8 26-27]], [[wiki/concepts/Prayer]] |
| 9 | Election / Israel without pride (Rom 9–11) | **Hit** | [[wiki/passages/Romans 9]], [[wiki/passages/Romans 11]] |
| 10 | Living sacrifice (Rom 12:1–2) | **Hit** | [[wiki/passages/Romans 12]], [[wiki/concepts/Discipleship]] |
| 12 | Holiness and justification without legalism | **Hit** | [[wiki/concepts/Holiness]], [[wiki/concepts/Justification]] |
| 13 | Cost of discipleship (cross, self-denial) | **Hit** | [[wiki/concepts/Discipleship]], [[wiki/passages/Matthew 16]] |
| 15 | What sustains Christian ministry | **Hit** | [[wiki/questions/What Sustains Christian Ministry]], [[wiki/source-notes/Devotional on 1 Timothy 1 12]] |
| 16 | Contextual study questions | **Hit** | [[wiki/source-notes/Ayudas en el estudio biblico]] |
| 18 | Local sermon on the Spirit (Andy Doss) | **Hit** | [[wiki/source-notes/Pastor Andy Doss y Merced Baptist Church]], [[wiki/concepts/Holy Spirit]] |
| 19 | Pastor’s interior war and flock (Gómez) | **Hit** | [[wiki/source-notes/THE PASTOR AND HIS CHURCH - Pastor Andrés Gómez]] |
| 20 | Prayer without hypocrisy (Mt 6) | **Hit** | [[wiki/passages/Matthew 6]], [[wiki/passages/Matthew 6 5-15]], [[wiki/concepts/Prayer]] |

**Score:** 13/13 sampled **Hit**; 0 Thin; 0 Miss.

**Retrieval notes (not scoring failures):**

- Catalog (`search-catalog` / `--ref` / `--tag` / `--source`) is the primary first hop for passage and vault-local titles.
- Reverse indexes under `wiki/indexes/` help browse by tag, passage, source, or type.
- Several Romans/Matthew passage pages remain `status: seed` with Concise-primary claims; Complete links are present. Depth for second-pass concept `reviewed` is a separate Phase 5 row.

**Spot-check answers (wiki-only, compressed):**

1. Gospel reveals Christ’s righteousness as acceptance by faith from first to last—not faith-to-works; Gentile guilt under suppressed natural revelation ([[wiki/passages/Romans 1|Romans 1]]).
3. Abraham justified by faith without boasting works; history written so later ages share the same way of believing ([[wiki/passages/Romans 4|Romans 4]], [[wiki/concepts/Justification|Justification]]).
6. Free grace does not license sin; justification and holiness are inseparable; baptismal dying/rising and yielding members to God ([[wiki/passages/Romans 6|Romans 6]]).
7. Believers often do not know what to pray; the Spirit helps infirmities and intercedes according to God’s will ([[wiki/passages/Romans 8|Romans 8]]).
9. Remnant by election of grace; Gentile inclusion without high-mindedness against natural branches; adore the depth of God’s wisdom ([[wiki/passages/Romans 11|Romans 11]]).
10. By mercies of God, present the body a living sacrifice; refuse world-conformity; renew the mind ([[wiki/passages/Romans 12|Romans 12]]).
12. Free grace does not explain away holiness; dead-to-sin reckoning and Spirit-walk without works as the ground of justification ([[wiki/concepts/Holiness|Holiness]]).
13. Deny self, take up the cross, follow Christ; count the cost; supreme love for Christ ([[wiki/concepts/Discipleship|Discipleship]]).
15. Christ supplies purpose, enablement, and stewardship character for ministry ([[wiki/questions/What Sustains Christian Ministry|What Sustains…]]).
16. Ask when written, to whom, and by whom ([[wiki/source-notes/Ayudas en el estudio biblico|Ayudas…]]).
18. Local series pictured the Spirit as oil (anointing) ([[wiki/source-notes/Pastor Andy Doss y Merced Baptist Church|Andy Doss note]]).
19. Pastor feeds/warns/cares under Eph 4; bears interior war and silent wounds; church must honor and pray ([[wiki/source-notes/THE PASTOR AND HIS CHURCH - Pastor Andrés Gómez|Gómez note]]).
20. Prayer is secret address to the Father, not hypocritical display; Lord’s Prayer gives matter and method ([[wiki/passages/Matthew 6|Matthew 6]]).

## Related pages

- [[wiki/campaigns/tracker|Campaign tracker]]
- [[wiki/campaigns/source-review-plan|Source-review plan]]
- [[wiki/concepts/Salvation|Salvation]]
- [[wiki/concepts/Faith|Faith]]
- [[wiki/concepts/Justification|Justification]]
- [[wiki/passages/Romans 1|Romans 1]]
