---
type: Source Note
title: Treasury of Scripture Knowledge
description: Vault ingest note for the TSK verse cross-reference table—tool-only lookup, not passage-atlas synthesis.
tags: [scripture, bible-study]
status: developing
updated: 2026-07-16
source_count: 1
source_path: "sources/reference/tsk/provenance.md"
---

# Treasury of Scripture Knowledge

## Summary

The Treasury of Scripture Knowledge (TSK) is a classic chain-reference work: for many verses it lists keywords or phrases and points to related passages. This vault holds an immutable tab-delimited export under `sources/reference/tsk/` and exposes it through `wiki_tool.py tsk` rather than expanding every row into wiki pages.

## Core claims

- TSK entries are **phrase-keyed cross-references**, not doctrinal commentary; each row attaches a word/phrase on a verse to a semicolon-delimited reference list. [[sources/reference/tsk/provenance|TSK provenance]]
- Book keys (1–66) and abbreviations align with the vault Bible reference table, so CLI output uses the same forms as `bible_reference` / catalog `--ref` search. [[sources/reference/tsk/provenance|TSK provenance]]
- Agents should query by reference (`--ref`, `--chapter`) instead of scanning `tskxref.txt`; passage and concept synthesis remains under `wiki/passages/` and `wiki/concepts/`. [[sources/reference/tsk/provenance|TSK provenance]]

## Agreements and tensions

- TSK is a traditional Protestant concordance-style chain, not a critical apparatus. Chains can be associative (word links) rather than strong exegetical parallels; use them as study prompts, then verify in passage hubs and commentaries.
- Tool-only integration deliberately avoids dumping ~64k rows into chapter notes. Future optional generated sections on passage hubs remain possible but are out of scope for this ingest.

## Biblical passages

TSK covers the Protestant canon (Genesis–Revelation) at verse granularity. No single primary `bible_reference` applies to the dataset as a whole.

## Related pages

- [[wiki/passages/index|Passage studies]] — primary chapter hubs for synthesis
- [[sources/reference/tsk/index|TSK source folder]]

## Sources

- [[sources/reference/tsk/provenance|TSK provenance]] (schema and usage; data files live beside it as `tskxref.txt` and `readme.txt`)

## Open questions

- Should high-traffic passage hubs later gain a short generated “TSK sample” section, or stay tool-only indefinitely?
- Is a reverse index (“verses that point *to* X”) worth a second CLI mode?
