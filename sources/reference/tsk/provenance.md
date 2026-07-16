---
type: Reference Dataset
title: Treasury of Scripture Knowledge (TSK) — provenance
description: Provenance and schema for the immutable TSK verse cross-reference table used by wiki_tool.py tsk.
tags: [scripture, bible-study]
updated: 2026-07-16
---

# Treasury of Scripture Knowledge (TSK) — provenance

## What this is

The **Treasury of Scripture Knowledge** is a classic verse-by-verse cross-reference work. Entries are keyed by a word or phrase in a verse and list related biblical references (not free-form commentary).

This folder holds a developer-oriented export intended for application lookup, not a rewritten commentary.

## Files (immutable)

| File | Role |
|---|---|
| `sources/reference/tsk/tskxref.txt` | Tab-delimited TSK rows (primary data). **Do not rewrite.** |
| `sources/reference/tsk/readme.txt` | Original export documentation (schema, book keys, abbreviations). **Do not rewrite.** |
| This note (`provenance.md`) | Vault provenance and usage only. |

## Export packaging

- Source of the table of contents / packaging note date in `readme.txt`: **2011-06-28**.
- Ingested into this vault: **2026-07-16** from a local copy at `~/TSK/` (byte-identical `tskxref.txt`).
- Format: TAB-delimited text; original packaging notes CRLF line endings on `readme.txt`.

## Schema (`tskxref.txt`)

Each line is one TSK entry for a verse:

| Field | Type | Meaning |
|---|---|---|
| `book_key` | integer | 1–66 (Genesis–Revelation); same keys as vault `BOOK_TABLE` / AGENTS.md |
| `chapter_nbr` | integer | Chapter within the book |
| `verse_nbr` | integer | Verse within the chapter |
| `sort_order` | integer | Display order of this word/phrase on the verse |
| `word` | string | TSK keyword or phrase for the entry |
| `reference_list` | string | Semicolon-delimited lowercase refs using vault-compatible abbreviations (`mt 6:9`, `pr 8:22-24`, `ps 33:6,9`, …) |

## Book keys and abbreviations

Identical in intent to the vault Bible reference table (see `readme.txt` and AGENTS.md). Protestant canon books 1–66 only in this export.

## How agents and tools use this

Do **not** open or scan `tskxref.txt` by hand for study questions. Use the deterministic CLI:

```bash
python3 .tools/scripts/wiki_tool.py tsk --ref "mt 6:9"
python3 .tools/scripts/wiki_tool.py tsk --chapter "ge 1"
python3 .tools/scripts/wiki_tool.py tsk --ref "john 1:1" --format json
```

Compiled synthesis still lives under `wiki/` (especially `wiki/passages/`). TSK is evidence for **cross-reference chains**, not a substitute for passage or concept notes.

## Related wiki

- [[wiki/source-notes/Treasury of Scripture Knowledge|Source note: Treasury of Scripture Knowledge]]
