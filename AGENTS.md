---
type: Metadata Convention
title: Bible Vault Metadata Conventions
description: Rules for OKF metadata, tags, Bible references, and navigation in this vault.
tags: [scripture, bible-study]
---

# Bible Vault Metadata Conventions

This vault is an OKF knowledge bundle. Every concept document has YAML frontmatter with a non-empty `type`, `title`, `description`, and `tags` list. Reserved `index.md` files do not have frontmatter.

## Tags

`tags` is a YAML list of short, lowercase, hyphenated strings for cross-cutting **Biblical concepts and themes**. Use tags such as `covenant`, `creation`, `redemption`, `faith`, `prayer`, `holiness`, `worship`, `discipleship`, `justice`, `prophecy`, `church`, `pastoral-ministry`, `salvation`, `christ`, `holy-spirit`, and `christian-life`.

Do not use generic document/source labels as tags, including `commentary`, `sermon`, `devotional`, `english`, `spanish`, author names, collection names, or publication formats. Do not use Bible books, chapters, verses, or reference abbreviations as tags. A fallback tag such as `christian-life` is acceptable when the document's specific theme cannot be determined reliably.

## Bible reference fields

When a document has a clear primary biblical passage, add these custom frontmatter fields:

```yaml
bible_reference: "<abbrev> <chapter>:<verse>[-<last-verse>]"
bible_book_key: <book_key>
bible_book_name: "<name>"
```

`bible_reference` must use the abbreviation table below and the format `<ref> <chapter>:<verse>[-<last-verse>]`; do not place Bible references in `tags`. If a document's primary scope is an entire chapter but no specific verse range is known, omit `bible_reference` rather than inventing a verse range; still add `bible_book_key` and `bible_book_name` when the book is known.

| book_key | name | abbrev |
|---:|---|---|
| 1 | Genesis | ge |
| 2 | Exodus | ex |
| 3 | Leviticus | le |
| 4 | Numbers | nu |
| 5 | Deuteronomy | de |
| 6 | Joshua | jos |
| 7 | Judges | jud |
| 8 | Ruth | ru |
| 9 | 1 Samuel | 1sa |
| 10 | 2 Samuel | 2sa |
| 11 | 1 Kings | 1ki |
| 12 | 2 Kings | 2ki |
| 13 | 1 Chronicles | 1ch |
| 14 | 2 Chronicles | 2ch |
| 15 | Ezra | ezr |
| 16 | Nehemiah | ne |
| 17 | Esther | es |
| 18 | Job | job |
| 19 | Psalms | ps |
| 20 | Proverbs | pr |
| 21 | Ecclesiates | ec |
| 22 | Song of Solomon | so |
| 23 | Isaiah | isa |
| 24 | Jeremiah | jer |
| 25 | Lamentations | la |
| 26 | Ezekiel | eze |
| 27 | Daniel | da |
| 28 | Hosea | ho |
| 29 | Joel | joe |
| 30 | Amos | am |
| 31 | Obadiah | ob |
| 32 | Jonah | jon |
| 33 | Micah | mic |
| 34 | Nahum | na |
| 35 | Habakkuk | hab |
| 36 | Zephaniah | zep |
| 37 | Haggi | hag |
| 38 | Zechariah | zec |
| 39 | Malachi | mal |
| 40 | Matthew | mt |
| 41 | Mark | mr |
| 42 | Luke | lu |
| 43 | John | joh |
| 44 | Acts | ac |
| 45 | Romans | ro |
| 46 | 1 Corinthians | 1co |
| 47 | 2 Corinthians | 2co |
| 48 | Galatians | ga |
| 49 | Ephesians | eph |
| 50 | Philippians | php |
| 51 | Colossians | col |
| 52 | 1 Thessalonians | 1th |
| 53 | 2 Thessalonians | 2th |
| 54 | 1 Timothy | 1ti |
| 55 | 2 Timothy | 2ti |
| 56 | Titus | tit |
| 57 | Philemon | phm |
| 58 | Hebrews | heb |
| 59 | James | jas |
| 60 | 1 Peter | 1pe |
| 61 | 2 Peter | 2pe |
| 62 | 1 John | 1jo |
| 63 | 2 John | 2jo |
| 64 | 3 John | 3jo |
| 65 | Jude | jude |
| 66 | Revelation | re |

## Indexes

Every content directory has a frontmatter-free `index.md` with a title and `# Contents` list. Do not create `_index.md` or `README.md` navigation documents.
