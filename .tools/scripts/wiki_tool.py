#!/usr/bin/env python3
"""Deterministic maintenance tooling for the Bible Vault LLM Wiki (OKF bundle)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"
SOURCES = ROOT / "sources"
RAW = ROOT / "raw"
SCHEMA = ROOT / "schema"
CATALOG = WIKI / "catalog.jsonl"
INDEXES_DIR = WIKI / "indexes"
MANIFEST = SCHEMA / "source-manifest.jsonl"
LOG = WIKI / "log.md"
TSK_XREF = SOURCES / "reference" / "tsk" / "tskxref.txt"
TSK_PROVENANCE = SOURCES / "reference" / "tsk" / "provenance.md"

REQUIRED_WIKI_FIELDS = ("type", "title", "description", "tags")
ALLOWED_STATUS = {"seed", "developing", "reviewed"}
BIBLE_REFERENCE = re.compile(r'^bible_reference:\s*"?[1-3]?[a-z]+ \d+:\d+(?:-\d+)?"?\s*$')
WIKILINK = re.compile(r"!?\[\[([^\]]+)\]\]")
MD_LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
YAML_LIST_ITEM = re.compile(r"^\s*-\s+[\"']?(.+?)[\"']?\s*$")
TAG_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
# Normalized abbrev refs: "mt 6:5-15" or chapter-only "joh 17"
ABBREV_REF = re.compile(
    r"\b([1-3]?[a-z]{1,5})\s+(\d+)(?::(\d+)(?:-(\d+))?)?\b",
    re.IGNORECASE,
)

WIKI_DIR_META = {
    "concepts": ("Concepts", "Source-backed syntheses of biblical doctrines, themes, and practices."),
    "people": ("People", "Syntheses about biblical people and relevant historical figures."),
    "passages": ("Passages", "Maintained studies organized around biblical passages."),
    "questions": ("Questions", "Durable investigations, comparisons, and answered questions."),
    "source-notes": ("Source notes", "Summaries and evaluations of intentionally ingested sources."),
}

SKIP_DIR_PARTS = {".git", ".obsidian", "__pycache__", "node_modules"}

# book_key, name, abbrev — matches AGENTS.md
BOOK_TABLE: list[tuple[int, str, str]] = [
    (1, "Genesis", "ge"),
    (2, "Exodus", "ex"),
    (3, "Leviticus", "le"),
    (4, "Numbers", "nu"),
    (5, "Deuteronomy", "de"),
    (6, "Joshua", "jos"),
    (7, "Judges", "jud"),
    (8, "Ruth", "ru"),
    (9, "1 Samuel", "1sa"),
    (10, "2 Samuel", "2sa"),
    (11, "1 Kings", "1ki"),
    (12, "2 Kings", "2ki"),
    (13, "1 Chronicles", "1ch"),
    (14, "2 Chronicles", "2ch"),
    (15, "Ezra", "ezr"),
    (16, "Nehemiah", "ne"),
    (17, "Esther", "es"),
    (18, "Job", "job"),
    (19, "Psalms", "ps"),
    (20, "Proverbs", "pr"),
    (21, "Ecclesiastes", "ec"),
    (22, "Song of Solomon", "so"),
    (23, "Isaiah", "isa"),
    (24, "Jeremiah", "jer"),
    (25, "Lamentations", "la"),
    (26, "Ezekiel", "eze"),
    (27, "Daniel", "da"),
    (28, "Hosea", "ho"),
    (29, "Joel", "joe"),
    (30, "Amos", "am"),
    (31, "Obadiah", "ob"),
    (32, "Jonah", "jon"),
    (33, "Micah", "mic"),
    (34, "Nahum", "na"),
    (35, "Habakkuk", "hab"),
    (36, "Zephaniah", "zep"),
    (37, "Haggai", "hag"),
    (38, "Zechariah", "zec"),
    (39, "Malachi", "mal"),
    (40, "Matthew", "mt"),
    (41, "Mark", "mr"),
    (42, "Luke", "lu"),
    (43, "John", "joh"),
    (44, "Acts", "ac"),
    (45, "Romans", "ro"),
    (46, "1 Corinthians", "1co"),
    (47, "2 Corinthians", "2co"),
    (48, "Galatians", "ga"),
    (49, "Ephesians", "eph"),
    (50, "Philippians", "php"),
    (51, "Colossians", "col"),
    (52, "1 Thessalonians", "1th"),
    (53, "2 Thessalonians", "2th"),
    (54, "1 Timothy", "1ti"),
    (55, "2 Timothy", "2ti"),
    (56, "Titus", "tit"),
    (57, "Philemon", "phm"),
    (58, "Hebrews", "heb"),
    (59, "James", "jas"),
    (60, "1 Peter", "1pe"),
    (61, "2 Peter", "2pe"),
    (62, "1 John", "1jo"),
    (63, "2 John", "2jo"),
    (64, "3 John", "3jo"),
    (65, "Jude", "jude"),
    (66, "Revelation", "re"),
]

# Common display aliases (lowercase) → abbrev
BOOK_ALIASES: dict[str, str] = {}
ABBREV_TO_KEY: dict[str, int] = {}
ABBREV_TO_NAME: dict[str, str] = {}
KEY_TO_ABBREV: dict[int, str] = {}
KEY_TO_NAME: dict[int, str] = {}

for _key, _name, _abbrev in BOOK_TABLE:
    ABBREV_TO_KEY[_abbrev] = _key
    ABBREV_TO_NAME[_abbrev] = _name
    KEY_TO_ABBREV[_key] = _abbrev
    KEY_TO_NAME[_key] = _name
    BOOK_ALIASES[_name.lower()] = _abbrev
    BOOK_ALIASES[_abbrev] = _abbrev

# Extra English display forms (conservative)
for _alias, _abbrev in {
    "psalm": "ps",
    "song of songs": "so",
    "canticles": "so",
    "ecclesiastes": "ec",
    "qoheleth": "ec",
    "apocalypse": "re",
    "rom": "ro",
    "rom.": "ro",
    "matt": "mt",
    "matt.": "mt",
    "mat": "mt",
    "jn": "joh",
    "jhn": "joh",
    "gen": "ge",
    "exod": "ex",
    "exo": "ex",
    "lev": "le",
    "num": "nu",
    "deut": "de",
    "josh": "jos",
    "judg": "jud",
    "1 sam": "1sa",
    "2 sam": "2sa",
    "1 kgs": "1ki",
    "2 kgs": "2ki",
    "1 chr": "1ch",
    "2 chr": "2ch",
    "1 cor": "1co",
    "2 cor": "2co",
    "1 thess": "1th",
    "2 thess": "2th",
    "1 tim": "1ti",
    "2 tim": "2ti",
    "1 pet": "1pe",
    "2 pet": "2pe",
    "1 jn": "1jo",
    "2 jn": "2jo",
    "3 jn": "3jo",
    "phil": "php",
    "phm": "phm",
    "rev": "re",
    "isaiah": "isa",
    "jeremiah": "jer",
    "ezekiel": "eze",
    "micah": "mic",
    "ephesians": "eph",
    "galatians": "ga",
    "colossians": "col",
    "hebrews": "heb",
    "james": "jas",
    "jude": "jude",
    "acts": "ac",
    "luke": "lu",
    "mark": "mr",
    "john": "joh",
    "matthew": "mt",
    "romans": "ro",
    "revelation": "re",
    "genesis": "ge",
    "exodus": "ex",
}.items():
    BOOK_ALIASES[_alias] = _abbrev

# Longest-first book name pattern for body extraction
_BOOK_NAME_ALTS = sorted(
    {name for name, _ in ((n, a) for _, n, a in BOOK_TABLE)}
    | {
        "Psalm",
        "Psalms",
        "Song of Songs",
        "1 Sam",
        "2 Sam",
        "1 Kgs",
        "2 Kgs",
        "1 Chr",
        "2 Chr",
        "1 Cor",
        "2 Cor",
        "1 Thess",
        "2 Thess",
        "1 Tim",
        "2 Tim",
        "1 Pet",
        "2 Pet",
        "1 Jn",
        "2 Jn",
        "3 Jn",
        "Rom",
        "Matt",
        "Gen",
        "Exod",
        "Rev",
    },
    key=len,
    reverse=True,
)
# Use [^\S\n] (horizontal whitespace) so verse ranges cannot span newlines
# (avoids "1 Timothy 1:11\n- 2 Corinthians" → "1ti 1:11-2").
_BOOK_NAME_RE = re.compile(
    r"\b(" + "|".join(re.escape(n) for n in _BOOK_NAME_ALTS) + r")\b"
    r"(?:\.|[^\S\n])+(\d+)(?:[^\S\n]*[:.][^\S\n]*(\d+)(?:[^\S\n]*[-–—][^\S\n]*(\d+))?)?",
    re.IGNORECASE,
)


def today() -> str:
    return date.today().isoformat()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, Any] | None:
    match = FRONTMATTER.match(text)
    if not match:
        return None
    raw = match.group(1)
    data: dict[str, Any] = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value == "" or value == "|" or value == ">":
            # block list or folded — collect following indented list items
            items: list[str] = []
            j = i + 1
            while j < len(lines):
                item = YAML_LIST_ITEM.match(lines[j])
                if item:
                    items.append(item.group(1).strip().strip("'\""))
                    j += 1
                    continue
                if lines[j].startswith(" ") or lines[j].startswith("\t"):
                    j += 1
                    continue
                break
            if items:
                data[key] = items
            else:
                data[key] = ""
            i = j
            continue
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                data[key] = []
            else:
                parts = [p.strip().strip("'\"") for p in inner.split(",")]
                data[key] = [p for p in parts if p]
        else:
            data[key] = value.strip("'\"").strip()
        i += 1
    return data


def body_after_frontmatter(text: str) -> str:
    match = FRONTMATTER.match(text)
    return text[match.end() :] if match else text


def is_wiki_concept(path: Path) -> bool:
    if path.suffix != ".md":
        return False
    if not path.is_relative_to(WIKI):
        return False
    if path.name in {"index.md", "catalog.jsonl", "log.md"}:
        return False
    try:
        rel_parts = path.relative_to(WIKI).parts
    except ValueError:
        return False
    # Generated reverse-index tree is not synthesis
    if rel_parts and rel_parts[0] == "indexes":
        return False
    return True


def iter_wiki_concepts() -> list[Path]:
    return sorted(p for p in WIKI.rglob("*.md") if is_wiki_concept(p))


def iter_source_docs() -> list[Path]:
    docs: list[Path] = []
    for path in SOURCES.rglob("*.md"):
        if path.name == "index.md":
            continue
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        docs.append(path)
    return sorted(docs)


def obsidian_link_target(path: Path, *, keep_extension: bool = False) -> str:
    """Return a vault-root-relative Obsidian wikilink target."""
    target = rel(path)
    if not keep_extension and target.endswith(".md"):
        target = target[:-3]
    return target


def is_external_link_target(target: str) -> bool:
    normalized = target.strip().strip("<>").lower()
    return normalized.startswith(("http://", "https://", "mailto:", "tel:", "obsidian://"))


def in_inline_code(line: str, pos: int) -> bool:
    """Best-effort inline-code detector for linting/rewrite safety."""
    return line[:pos].count("`") % 2 == 1


def internal_markdown_links(text: str) -> list[tuple[int, str, str]]:
    """Return non-image, non-external Markdown links outside fenced/inline code."""
    links: list[tuple[int, str, str]] = []
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in MD_LINK.finditer(line):
            if in_inline_code(line, match.start()):
                continue
            label = match.group(1).strip()
            target = match.group(2).strip().strip("<>")
            if not target or target.startswith(("#", "^")) or is_external_link_target(target):
                continue
            links.append((line_no, label, target))
    return links


def extract_wikilink_targets(text: str) -> list[str]:
    targets: list[str] = []
    for raw in WIKILINK.findall(text):
        target = raw.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            if not target.endswith(".md"):
                target = f"{target}.md"
            targets.append(unquote(target))
    return targets


def normalize_source_path(path: str) -> str:
    sp = unquote(path.strip().strip("'\""))
    sp = sp.split("#", 1)[0].strip()
    if not sp:
        return ""
    if not sp.endswith(".md"):
        sp = f"{sp}.md"
    return sp


def sources_section_links(text: str) -> list[str]:
    body = body_after_frontmatter(text)
    lines = body.splitlines()
    in_sources = False
    links: list[str] = []
    for line in lines:
        if line.strip() in {"## Sources", "# Sources"}:
            in_sources = True
            continue
        if in_sources and line.startswith("## "):
            break
        if in_sources:
            for raw in WIKILINK.findall(line):
                target = raw.split("|", 1)[0].split("#", 1)[0].strip()
                if not target:
                    continue
                links.append(normalize_source_path(target))
    return [x for x in links if x]


def resolve_source_paths_from_wiki(path: Path, text: str, meta: dict[str, Any]) -> list[str]:
    found: list[str] = []
    source_path = meta.get("source_path")
    if isinstance(source_path, str) and source_path.strip():
        sp = normalize_source_path(source_path)
        if sp:
            found.append(sp)

    for target in sources_section_links(text):
        if target.startswith("sources/"):
            found.append(target)

    for target in extract_wikilink_targets(text):
        if target.startswith("sources/"):
            found.append(normalize_source_path(target))

    # de-dupe preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for item in found:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def resolve_related_wiki_paths(text: str) -> list[str]:
    found: list[str] = []
    for target in extract_wikilink_targets(text):
        if target.startswith("wiki/"):
            found.append(unquote(target))
    seen: set[str] = set()
    ordered: list[str] = []
    for item in found:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def extract_headings(text: str) -> list[str]:
    body = body_after_frontmatter(text)
    headings: list[str] = []
    for line in body.splitlines():
        match = HEADING.match(line)
        if not match:
            continue
        title = match.group(1).strip()
        # skip the page H1 when it duplicates the note title style
        if title:
            headings.append(title)
    return headings


def lookup_abbrev(token: str) -> str | None:
    cleaned = token.strip().lower().rstrip(".")
    if cleaned in BOOK_ALIASES:
        return BOOK_ALIASES[cleaned]
    if cleaned in ABBREV_TO_KEY:
        return cleaned
    return None


def format_norm_ref(abbrev: str, chapter: int, verse: int | None = None, end: int | None = None) -> str:
    if verse is None:
        return f"{abbrev} {chapter}"
    if end is None or end == verse:
        return f"{abbrev} {chapter}:{verse}"
    return f"{abbrev} {chapter}:{verse}-{end}"


def normalize_abbrev_ref_string(raw: str) -> str | None:
    """Normalize a primary frontmatter-style ref string to vault abbrev form."""
    text = raw.strip().strip("'\"").replace("–", "-").replace("—", "-")
    match = re.match(
        r"^([1-3]?[a-z]+)\s+(\d+):(\d+)(?:-(\d+))?$",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    abbrev = lookup_abbrev(match.group(1))
    if not abbrev:
        return None
    chapter = int(match.group(2))
    verse = int(match.group(3))
    end = int(match.group(4)) if match.group(4) else None
    return format_norm_ref(abbrev, chapter, verse, end)


def extract_display_refs(text: str) -> list[str]:
    """Conservatively extract Bible refs from display English forms in body text."""
    # Normalize dashes for verse ranges
    normalized = text.replace("–", "-").replace("—", "-")
    found: list[str] = []
    for match in _BOOK_NAME_RE.finditer(normalized):
        name = match.group(1)
        abbrev = lookup_abbrev(name)
        if not abbrev:
            continue
        chapter = int(match.group(2))
        verse = int(match.group(3)) if match.group(3) else None
        end = int(match.group(4)) if match.group(4) else None
        found.append(format_norm_ref(abbrev, chapter, verse, end))
    return found


def biblical_passages_section_text(text: str) -> str:
    body = body_after_frontmatter(text)
    lines = body.splitlines()
    in_section = False
    chunk: list[str] = []
    for line in lines:
        if line.strip() in {"## Biblical passages", "# Biblical passages"}:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            chunk.append(line)
    return "\n".join(chunk)


def extract_bible_references(meta: dict[str, Any], text: str) -> list[str]:
    """Derive refs from frontmatter primary + ## Biblical passages only.

    Full-body scan is intentionally avoided: claim prose and source path labels
    produce false positives. Prefer conservative, section-scoped extraction.
    """
    refs: list[str] = []

    primary = meta.get("bible_reference")
    if isinstance(primary, str) and primary.strip():
        norm = normalize_abbrev_ref_string(primary)
        if norm:
            refs.append(norm)

    section = biblical_passages_section_text(text)
    if section.strip():
        refs.extend(extract_display_refs(section))

    # Deduplicate preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            ordered.append(ref)
    return ordered


def book_keys_from_refs(refs: list[str]) -> list[int]:
    keys: list[int] = []
    seen: set[int] = set()
    for ref in refs:
        match = ABBREV_REF.match(ref)
        if not match:
            # chapter-only already matches ABBREV_REF with optional verse
            parts = ref.split()
            if len(parts) >= 1:
                abbrev = lookup_abbrev(parts[0])
                if abbrev and abbrev in ABBREV_TO_KEY:
                    key = ABBREV_TO_KEY[abbrev]
                    if key not in seen:
                        seen.add(key)
                        keys.append(key)
            continue
        abbrev = lookup_abbrev(match.group(1))
        if abbrev and abbrev in ABBREV_TO_KEY:
            key = ABBREV_TO_KEY[abbrev]
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys


def optional_int(meta: dict[str, Any], key: str) -> int | None:
    value = meta.get(key)
    if value is None or value == "":
        return None
    try:
        return int(str(value))
    except ValueError:
        return None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in read_text(path).splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def catalog_row(path: Path) -> dict[str, Any] | None:
    text = read_text(path)
    meta = parse_frontmatter(text)
    if meta is None:
        return None
    tags = meta.get("tags") if isinstance(meta.get("tags"), list) else []
    try:
        source_count = int(str(meta.get("source_count", "0")))
    except ValueError:
        source_count = 0

    source_paths = resolve_source_paths_from_wiki(path, text, meta)
    related_paths = resolve_related_wiki_paths(text)
    headings = extract_headings(text)
    bible_references = extract_bible_references(meta, text)
    bible_book_keys = book_keys_from_refs(bible_references)

    primary_ref = meta.get("bible_reference")
    primary_ref_s = str(primary_ref).strip() if primary_ref not in (None, "") else None
    if primary_ref_s:
        normalized_primary = normalize_abbrev_ref_string(primary_ref_s)
        primary_ref_out: str | None = normalized_primary or primary_ref_s
    else:
        primary_ref_out = None

    book_key = optional_int(meta, "bible_book_key")
    book_name = str(meta.get("bible_book_name") or "").strip() or None
    if book_key is None and bible_book_keys:
        # do not invent frontmatter; derived list is separate
        pass

    primary_source_path = None
    sp = meta.get("source_path")
    if isinstance(sp, str) and sp.strip():
        primary_source_path = normalize_source_path(sp)

    aliases: list[str] = []
    raw_aliases = meta.get("aliases")
    if isinstance(raw_aliases, list):
        aliases = [str(a).strip() for a in raw_aliases if str(a).strip()]
    elif isinstance(raw_aliases, str) and raw_aliases.strip():
        aliases = [raw_aliases.strip()]

    return {
        "path": rel(path),
        "title": str(meta.get("title") or path.stem),
        "type": str(meta.get("type") or ""),
        "tags": tags,
        "status": str(meta.get("status") or ""),
        "updated": str(meta.get("updated") or ""),
        "source_count": source_count,
        "description": str(meta.get("description") or ""),
        "bible_reference": primary_ref_out,
        "bible_book_key": book_key,
        "bible_book_name": book_name,
        "bible_references": bible_references,
        "bible_book_keys": bible_book_keys if book_key is None else (
            [book_key] + [k for k in bible_book_keys if k != book_key]
        ),
        "source_paths": source_paths,
        "related_paths": related_paths,
        "primary_source_path": primary_source_path,
        "headings": headings,
        "aliases": aliases,
    }


def rebuild_wiki_indexes() -> None:
    # Per-folder indexes for known wiki subdirs
    for dirname, (title, blurb) in WIKI_DIR_META.items():
        folder = WIKI / dirname
        folder.mkdir(parents=True, exist_ok=True)
        entries: list[tuple[str, str, str]] = []
        for path in sorted(folder.glob("*.md")):
            if path.name == "index.md":
                continue
            text = read_text(path)
            meta = parse_frontmatter(text) or {}
            page_title = str(meta.get("title") or path.stem)
            description = str(meta.get("description") or "").strip()
            target = obsidian_link_target(path)
            entries.append((page_title.lower(), f"* [[{target}|{page_title}]] - {description}".rstrip(" -"), page_title))
        entries.sort(key=lambda item: item[0])
        base_link = f"wiki/{dirname}/index.base"
        lines = [
            f"# {title}",
            "",
            f"Live database view: [[{base_link}|Folder base]]. Static OKF list remains below.",
            "",
            "# Contents",
            "",
        ]
        if entries:
            lines.extend(item[1] for item in entries)
        else:
            lines.append("* No pages yet.")
        lines.append("")
        (folder / "index.md").write_text("\n".join(lines), encoding="utf-8")

    # wiki/index.md
    wiki_index_lines = [
        "# Bible Wiki",
        "",
        "Live database view: [[wiki/index.base|Wiki hub base]]. Static OKF list remains below.",
        "",
        "# Contents",
        "",
    ]
    for dirname, (title, blurb) in WIKI_DIR_META.items():
        wiki_index_lines.append(f"* [[wiki/{dirname}/index|{title}]] - {blurb}")
    wiki_index_lines.append(
        "* [[wiki/indexes/index|Generated indexes]] - Machine-built reverse indexes (tag, passage, source, type)."
    )
    wiki_index_lines.append(
        "* [[wiki/log|Wiki log]] - Chronological record of ingests, filed queries, lint passes, and maintenance."
    )
    wiki_index_lines.append("")
    (WIKI / "index.md").write_text("\n".join(wiki_index_lines), encoding="utf-8")


def rebuild_reverse_indexes(rows: list[dict[str, Any]]) -> None:
    """Emit wiki/indexes/*.jsonl reverse indexes from enriched catalog rows."""
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)

    by_tag: dict[str, list[str]] = defaultdict(list)
    by_type: dict[str, list[str]] = defaultdict(list)
    by_source: dict[str, list[str]] = defaultdict(list)
    by_passage: dict[str, dict[str, Any]] = {}

    def passage_entry(key: str, kind: str, book_key: int | None) -> dict[str, Any]:
        if key not in by_passage:
            by_passage[key] = {
                "key": key,
                "kind": kind,
                "book_key": book_key,
                "pages": [],
            }
        return by_passage[key]

    for row in rows:
        path = str(row.get("path") or "")
        if not path:
            continue
        for tag in row.get("tags") or []:
            tag_s = str(tag).strip().lower()
            if tag_s:
                by_tag[tag_s].append(path)
        type_s = str(row.get("type") or "").strip()
        if type_s:
            by_type[type_s].append(path)
        for sp in row.get("source_paths") or []:
            sp_s = normalize_source_path(str(sp))
            if sp_s:
                by_source[sp_s].append(path)
        # Primary + derived refs
        refs = list(row.get("bible_references") or [])
        primary = row.get("bible_reference")
        if primary:
            refs = [str(primary)] + refs
        seen_refs: set[str] = set()
        for ref in refs:
            ref_s = str(ref).strip().lower()
            if not ref_s or ref_s in seen_refs:
                continue
            seen_refs.add(ref_s)
            # Parse book key from ref
            m = re.match(r"^([1-3]?[a-z]+)\s+(\d+)", ref_s)
            book_key = ABBREV_TO_KEY.get(m.group(1)) if m else None
            entry = passage_entry(ref_s, "ref", book_key)
            if path not in entry["pages"]:
                entry["pages"].append(path)
            if book_key is not None:
                book_key_s = f"book:{book_key}"
                b_entry = passage_entry(book_key_s, "book", book_key)
                if path not in b_entry["pages"]:
                    b_entry["pages"].append(path)

        for bk in row.get("bible_book_keys") or []:
            try:
                book_key = int(bk)
            except (TypeError, ValueError):
                continue
            book_key_s = f"book:{book_key}"
            b_entry = passage_entry(book_key_s, "book", book_key)
            if path not in b_entry["pages"]:
                b_entry["pages"].append(path)

    def finalize_map(mapping: dict[str, list[str]]) -> list[dict[str, Any]]:
        rows_out: list[dict[str, Any]] = []
        for key in sorted(mapping):
            pages = sorted(set(mapping[key]))
            rows_out.append({"key": key, "pages": pages, "count": len(pages)})
        return rows_out

    write_jsonl(INDEXES_DIR / "by-tag.jsonl", finalize_map(by_tag))
    write_jsonl(INDEXES_DIR / "by-type.jsonl", finalize_map(by_type))
    write_jsonl(INDEXES_DIR / "by-source.jsonl", finalize_map(by_source))

    passage_rows: list[dict[str, Any]] = []
    for key in sorted(by_passage):
        entry = by_passage[key]
        pages = sorted(set(entry["pages"]))
        passage_rows.append(
            {
                "key": entry["key"],
                "kind": entry["kind"],
                "book_key": entry["book_key"],
                "pages": pages,
                "count": len(pages),
            }
        )
    write_jsonl(INDEXES_DIR / "by-passage.jsonl", passage_rows)

    index_md = "\n".join(
        [
            "# Generated indexes",
            "",
            "Live database view: [[wiki/indexes/index.base|Folder base]]. Static OKF list remains below.",
            "",
            "# Contents",
            "",
            "* Machine-built reverse indexes regenerated by `wiki_tool.py build`.",
            "* Do not hand-edit JSONL files in this directory.",
            "",
            "* [[wiki/indexes/by-tag.jsonl|by-tag.jsonl]] - tag → wiki pages",
            "* [[wiki/indexes/by-passage.jsonl|by-passage.jsonl]] - normalized Bible ref / book → wiki pages",
            "* [[wiki/indexes/by-source.jsonl|by-source.jsonl]] - source path → wiki pages",
            "* [[wiki/indexes/by-type.jsonl|by-type.jsonl]] - page type → wiki pages",
            "",
        ]
    )
    (INDEXES_DIR / "index.md").write_text(index_md, encoding="utf-8")


# ---------------------------------------------------------------------------
# Side-by-side Obsidian Bases (index.base) — paired with every index.md
# except vault root, which has only bases.base ("base of bases").
# ---------------------------------------------------------------------------

BASES_BASE_TEMPLATE = """\
# Base of bases — every Obsidian .base file in this vault.
# Regenerated by wiki_tool.py build. Root has no index.base.
filters:
  and:
    - 'file.ext == "base"'

formulas:
  is_index_base: 'if(file.name == "index.base", "index", "other")'
  area: 'if(file.folder == "wiki" || file.folder.startsWith("wiki/"), "wiki", if(file.folder == "sources" || file.folder.startsWith("sources/"), "sources", if(file.folder == "schema" || file.folder.startsWith("schema/"), "schema", if(file.folder == "_templates" || file.folder.startsWith("_templates/"), "templates", if(file.folder == "raw" || file.folder.startsWith("raw/"), "raw", "root")))))'

properties:
  formula.is_index_base:
    displayName: Role
  formula.area:
    displayName: Area
  file.folder:
    displayName: Folder
  file.name:
    displayName: Name

views:
  - type: table
    name: "All bases"
    order:
      - file.path
      - file.folder
      - file.name
      - formula.area
      - formula.is_index_base
    summaries:
      file.name: Unique

  - type: table
    name: "By area"
    order:
      - file.path
      - file.name
      - formula.is_index_base
    groupBy:
      property: formula.area
      direction: ASC

  - type: table
    name: "Index counterparts only"
    filters:
      and:
        - 'file.name == "index.base"'
    order:
      - file.folder
      - file.path
    groupBy:
      property: formula.area
      direction: ASC

  - type: table
    name: "Wiki bases"
    filters:
      and:
        - 'file.folder == "wiki" || file.folder.startsWith("wiki/")'
    order:
      - file.path
      - file.name

  - type: table
    name: "Sources bases"
    filters:
      and:
        - 'file.folder == "sources" || file.folder.startsWith("sources/")'
    order:
      - file.path
      - file.name

  - type: list
    name: "List"
    order:
      - file.path
      - formula.area

  - type: cards
    name: "Cards"
    order:
      - file.name
      - file.folder
      - formula.area
"""

# Templates use the literal token __FOLDER__ (vault-relative path).
INDEX_BASE_TEMPLATES: dict[str, str] = {
    "sources_generic": """\
# Auto-generated counterpart to index.md in __FOLDER__.
# Pairs with the static OKF index.md; does not replace it.
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - 'file.ext == "md"'
    - 'file.name != "index.md"'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  type:
    displayName: Type
  tags:
    displayName: Tags
  bible_book_name:
    displayName: Book
  bible_reference:
    displayName: Reference
  linkTitle:
    displayName: Link title
  weight:
    displayName: Weight

views:
  - type: table
    name: "Contents"
    order:
      - file.name
      - title
      - type
      - bible_book_name
      - tags
      - description
    summaries:
      file.name: Unique

  - type: table
    name: "By book"
    order:
      - file.name
      - title
      - tags
      - description
    groupBy:
      property: bible_book_name
      direction: ASC

  - type: table
    name: "By type"
    order:
      - file.name
      - title
      - tags
      - description
    groupBy:
      property: type
      direction: ASC

  - type: cards
    name: "Cards"
    order:
      - file.name
      - title
      - tags
      - description
""",
    "simple": """\
# Auto-generated counterpart to index.md in __FOLDER__.
# Pairs with the static OKF index.md; does not replace it.
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - 'file.ext == "md"'
    - 'file.name != "index.md"'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  type:
    displayName: Type
  tags:
    displayName: Tags

views:
  - type: table
    name: "Contents"
    order:
      - file.name
      - type
      - title
      - tags
      - description
    summaries:
      file.name: Unique

  - type: table
    name: "By type"
    order:
      - file.name
      - title
      - description
    groupBy:
      property: type
      direction: ASC

  - type: cards
    name: "Cards"
    order:
      - file.name
      - type
      - description
""",
    "wiki_hub": """\
# Wiki hub base (pairs with index.md; does not replace it).
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - or:
        - 'file.name == "index.md"'
        - 'file.path == "wiki/log.md"'
    - 'file.path != "wiki/index.md"'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  type:
    displayName: Type

views:
  - type: table
    name: "Wiki sections"
    order:
      - file.folder
      - file.name
      - type
      - title
      - description

  - type: list
    name: "List"
    order:
      - file.folder
      - file.name
""",
    "wiki_concepts": """\
# Dynamic index of wiki biblical concepts (pairs with index.md; does not replace it).
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - 'file.ext == "md"'
    - 'file.name != "index.md"'
    - 'type == "Biblical Concept"'

formulas:
  maturity: 'if(status == "reviewed", "✅ Reviewed", if(status == "developing", "🔨 Developing", "🌱 Seed"))'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  tags:
    displayName: Tags
  status:
    displayName: Status
  source_count:
    displayName: Sources
  updated:
    displayName: Updated
  formula.maturity:
    displayName: Maturity

views:
  - type: table
    name: "All concepts"
    order:
      - file.name
      - formula.maturity
      - tags
      - source_count
      - updated
      - description
    summaries:
      source_count: Sum
      file.name: Unique

  - type: table
    name: "By status"
    order:
      - file.name
      - tags
      - source_count
      - description
    groupBy:
      property: status
      direction: ASC

  - type: table
    name: "Developing"
    filters:
      and:
        - 'status == "developing"'
    order:
      - file.name
      - tags
      - source_count
      - updated
      - description

  - type: table
    name: "Lightly sourced"
    filters:
      and:
        - 'source_count < 2'
    order:
      - file.name
      - status
      - source_count
      - tags
      - description

  - type: cards
    name: "Browse cards"
    order:
      - file.name
      - formula.maturity
      - tags
      - source_count
      - description
""",
    "wiki_passages": """\
# Dynamic index of wiki passage studies (pairs with index.md; does not replace it).
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - 'file.ext == "md"'
    - 'file.name != "index.md"'
    - 'type == "Passage Study"'

formulas:
  sources_label: 'if(source_count, source_count.toString() + " src", "")'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  bible_book_name:
    displayName: Book
  bible_reference:
    displayName: Reference
  tags:
    displayName: Tags
  status:
    displayName: Status
  source_count:
    displayName: Sources
  updated:
    displayName: Updated
  formula.sources_label:
    displayName: Sources

views:
  - type: table
    name: "All passages"
    order:
      - file.name
      - bible_book_name
      - tags
      - status
      - source_count
      - description
    summaries:
      source_count: Sum
      file.name: Unique

  - type: table
    name: "By book"
    order:
      - file.name
      - bible_reference
      - tags
      - status
      - source_count
    groupBy:
      property: bible_book_name
      direction: ASC

  - type: table
    name: "Developing"
    filters:
      and:
        - 'status == "developing"'
    order:
      - file.name
      - bible_book_name
      - tags
      - source_count
      - updated
      - description

  - type: table
    name: "Prayer passages"
    filters:
      and:
        - 'file.hasTag("prayer")'
    order:
      - file.name
      - bible_book_name
      - tags
      - status
      - description

  - type: cards
    name: "Browse cards"
    order:
      - file.name
      - bible_book_name
      - tags
      - status
      - description
""",
    "wiki_source_notes": """\
# Dynamic index of wiki source notes (pairs with index.md; does not replace it).
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - 'file.ext == "md"'
    - 'file.name != "index.md"'
    - 'type == "Source Note"'

formulas:
  maturity: 'if(status == "reviewed", "✅ Reviewed", if(status == "developing", "🔨 Developing", "🌱 Seed"))'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  tags:
    displayName: Tags
  status:
    displayName: Status
  source_count:
    displayName: Sources
  source_path:
    displayName: Source path
  bible_book_name:
    displayName: Book
  updated:
    displayName: Updated
  formula.maturity:
    displayName: Maturity

views:
  - type: table
    name: "All source notes"
    order:
      - file.name
      - formula.maturity
      - tags
      - source_count
      - bible_book_name
      - source_path
      - description
    summaries:
      source_count: Sum
      file.name: Unique

  - type: table
    name: "By book"
    order:
      - file.name
      - tags
      - source_count
      - description
    groupBy:
      property: bible_book_name
      direction: ASC

  - type: table
    name: "By status"
    order:
      - file.name
      - tags
      - source_count
      - description
    groupBy:
      property: status
      direction: ASC

  - type: cards
    name: "Cards"
    order:
      - file.name
      - formula.maturity
      - tags
      - description
""",
    "wiki_generic": """\
# Auto-generated counterpart to index.md in __FOLDER__.
# Pairs with the static OKF index.md; does not replace it.
filters:
  and:
    - 'file.inFolder("__FOLDER__")'
    - 'file.ext == "md"'
    - 'file.name != "index.md"'

formulas:
  maturity: 'if(status == "reviewed", "✅ Reviewed", if(status == "developing", "🔨 Developing", if(status, "🌱 " + status, "")))'

properties:
  title:
    displayName: Title
  description:
    displayName: Summary
  type:
    displayName: Type
  tags:
    displayName: Tags
  status:
    displayName: Status
  source_count:
    displayName: Sources
  bible_book_name:
    displayName: Book
  bible_reference:
    displayName: Reference
  updated:
    displayName: Updated
  formula.maturity:
    displayName: Maturity

views:
  - type: table
    name: "Contents"
    order:
      - file.name
      - type
      - formula.maturity
      - tags
      - source_count
      - bible_book_name
      - description
    summaries:
      source_count: Sum
      file.name: Unique

  - type: table
    name: "By type"
    order:
      - file.name
      - status
      - tags
      - description
    groupBy:
      property: type
      direction: ASC

  - type: table
    name: "By book"
    order:
      - file.name
      - tags
      - status
      - description
    groupBy:
      property: bible_book_name
      direction: ASC

  - type: cards
    name: "Cards"
    order:
      - file.name
      - type
      - tags
      - description
""",
}


def folder_rel_for_dir(directory: Path) -> str:
    """Vault-relative folder path for file.inFolder (POSIX, no trailing slash)."""
    if directory == ROOT:
        return ""
    return directory.relative_to(ROOT).as_posix()


def select_base_profile(folder_rel: str) -> str:
    """Choose an index.base profile for a vault-relative folder path."""
    if not folder_rel or folder_rel == ".":
        raise ValueError("vault root has no index.base profile (use bases.base)")
    if folder_rel == "wiki":
        return "wiki_hub"
    if folder_rel == "wiki/concepts":
        return "wiki_concepts"
    if folder_rel == "wiki/passages":
        return "wiki_passages"
    if folder_rel == "wiki/source-notes":
        return "wiki_source_notes"
    if folder_rel == "wiki" or folder_rel.startswith("wiki/"):
        return "wiki_generic"
    if folder_rel == "sources" or folder_rel.startswith("sources/"):
        return "sources_generic"
    return "simple"


def render_index_base(folder_rel: str) -> str:
    profile = select_base_profile(folder_rel)
    template = INDEX_BASE_TEMPLATES[profile]
    return template.replace("__FOLDER__", folder_rel)


def render_bases_base() -> str:
    return BASES_BASE_TEMPLATE


def iter_index_md_dirs() -> list[Path]:
    """Directories that contain index.md (including vault root)."""
    dirs: list[Path] = []
    for path in ROOT.rglob("index.md"):
        if any(part in SKIP_DIR_PARTS for part in path.parts):
            continue
        dirs.append(path.parent)
    return sorted(set(dirs), key=lambda p: str(p))


def rebuild_index_bases() -> dict[str, int]:
    """Write index.base next to every non-root index.md; write root bases.base."""
    written = 0
    profile_counts: dict[str, int] = defaultdict(int)

    for directory in iter_index_md_dirs():
        if directory == ROOT:
            continue
        folder_rel = folder_rel_for_dir(directory)
        profile = select_base_profile(folder_rel)
        content = render_index_base(folder_rel)
        out = directory / "index.base"
        out.write_text(content, encoding="utf-8")
        written += 1
        profile_counts[profile] += 1

    bases_path = ROOT / "bases.base"
    bases_path.write_text(render_bases_base(), encoding="utf-8")
    profile_counts["base_of_bases"] = 1

    return {"index_bases": written, **{f"profile:{k}": v for k, v in sorted(profile_counts.items())}}


def catalog_is_stale() -> bool:
    if not CATALOG.is_file():
        return True
    cat_mtime = CATALOG.stat().st_mtime
    for path in iter_wiki_concepts():
        if path.stat().st_mtime > cat_mtime:
            return True
    return False


def cmd_doctor(_: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if sys.version_info < (3, 10):
        errors.append(f"Python >= 3.10 required (found {sys.version.split()[0]})")

    for required in (WIKI, SOURCES, RAW, SCHEMA, ROOT / "AGENTS.md"):
        if not required.exists():
            errors.append(f"missing required path: {rel(required) if required.is_relative_to(ROOT) else required}")

    for sub in WIKI_DIR_META:
        d = WIKI / sub
        if not d.is_dir():
            warnings.append(f"missing wiki subdir: wiki/{sub}")
        index = d / "index.md"
        if d.is_dir() and not index.is_file():
            errors.append(f"missing index: wiki/{sub}/index.md")

    concepts = iter_wiki_concepts()
    sources = iter_source_docs()

    print("Bible Vault wiki doctor")
    print(f"  root: {ROOT}")
    print(f"  python: {sys.version.split()[0]}")
    print(f"  wiki concepts: {len(concepts)}")
    print(f"  source docs (excl. index.md): {len(sources)}")
    print(f"  catalog: {'present' if CATALOG.is_file() else 'missing'}")
    print(f"  source-manifest: {'present' if MANIFEST.is_file() else 'missing'}")
    print(f"  reverse indexes: {'present' if INDEXES_DIR.is_dir() else 'missing'}")
    print(f"  lint_wiki: {'present' if (ROOT / '.tools/scripts/lint_wiki.py').is_file() else 'missing'}")
    if TSK_XREF.is_file():
        try:
            size_mb = TSK_XREF.stat().st_size / 1_000_000
        except OSError:
            size_mb = 0.0
        print(f"  TSK data: present ({rel(TSK_XREF)}, {size_mb:.2f} MB)")
    else:
        warnings.append(f"TSK data missing: {rel(TSK_XREF)} (wiki_tool.py tsk will fail)")
    if not TSK_PROVENANCE.is_file():
        warnings.append(f"TSK provenance missing: {rel(TSK_PROVENANCE)}")

    if CATALOG.is_file():
        rows = load_jsonl(CATALOG)
        print(f"  catalog rows: {len(rows)}")
        with_refs = sum(1 for r in rows if r.get("bible_references"))
        with_sources = sum(1 for r in rows if r.get("source_paths"))
        print(f"  catalog with bible_references: {with_refs}")
        print(f"  catalog with source_paths: {with_sources}")
        if catalog_is_stale():
            warnings.append("catalog may be stale (a wiki page is newer than catalog.jsonl; run build)")
    if INDEXES_DIR.is_dir():
        for name in ("by-tag.jsonl", "by-passage.jsonl", "by-source.jsonl", "by-type.jsonl"):
            p = INDEXES_DIR / name
            if p.is_file():
                print(f"  {name}: {len(load_jsonl(p))} rows")
            else:
                warnings.append(f"missing reverse index: wiki/indexes/{name}")
    if MANIFEST.is_file():
        rows = load_jsonl(MANIFEST)
        covered = sum(1 for r in rows if r.get("covered_by"))
        print(f"  manifest rows: {len(rows)} (covered: {covered})")

    index_md_dirs = iter_index_md_dirs()
    index_bases = [
        d / "index.base"
        for d in index_md_dirs
        if d != ROOT and (d / "index.base").is_file()
    ]
    expected_pairs = sum(1 for d in index_md_dirs if d != ROOT)
    print(f"  index.md dirs: {len(index_md_dirs)} (root + {expected_pairs} content)")
    print(f"  index.base files: {len(index_bases)}")
    print(f"  bases.base: {'present' if (ROOT / 'bases.base').is_file() else 'missing'}")
    if not (ROOT / "bases.base").is_file():
        warnings.append("missing bases.base at vault root (base of bases)")
    if (ROOT / "index.base").is_file():
        warnings.append("root has index.base; root should use only bases.base")
    if len(index_bases) != expected_pairs:
        warnings.append(
            f"index.base pairing mismatch: {len(index_bases)} bases for {expected_pairs} non-root index.md"
        )

    for warning in warnings:
        print(f"WARN {warning}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} doctor error(s)")
        return 1
    print("Doctor passed")
    return 0


def cmd_build(_: argparse.Namespace) -> int:
    rows: list[dict[str, Any]] = []
    missing_fm = 0
    for path in iter_wiki_concepts():
        row = catalog_row(path)
        if row is None:
            missing_fm += 1
            print(f"WARN missing frontmatter, skipped in catalog: {rel(path)}")
            continue
        rows.append(row)
    rows.sort(key=lambda r: r["path"])
    write_jsonl(CATALOG, rows)
    rebuild_wiki_indexes()
    rebuild_reverse_indexes(rows)
    base_stats = rebuild_index_bases()
    print(f"Wrote {rel(CATALOG)} ({len(rows)} rows)")
    print(f"Wrote reverse indexes under {rel(INDEXES_DIR)}")
    print("Regenerated wiki index.md files")
    print(f"Regenerated {base_stats['index_bases']} index.base files + bases.base")
    if missing_fm:
        print(f"{missing_fm} file(s) skipped for missing frontmatter")
        return 1
    return 0


def tags_nonempty(meta: dict[str, Any]) -> bool:
    tags = meta.get("tags")
    if isinstance(tags, list):
        return any(str(t).strip() for t in tags)
    if isinstance(tags, str):
        return bool(TAG_TOKEN.findall(tags))
    return False


def cmd_lint(_: argparse.Namespace) -> int:
    errors: list[str] = []
    all_markdown = [
        p
        for p in ROOT.rglob("*.md")
        if not any(part in SKIP_DIR_PARTS for part in p.parts)
    ]

    # Obsidian link standard: vault-internal links should be wikilinks.
    # Source/raw document bodies are immutable evidence; navigation index.md files are still checked.
    for path in all_markdown:
        if path.is_relative_to(SOURCES) and path.name != "index.md":
            continue
        if path.is_relative_to(RAW) and path.name != "index.md":
            continue
        text = read_text(path)
        for line_no, label, target in internal_markdown_links(text):
            errors.append(
                f"internal markdown link should be wikilink: {rel(path)}:{line_no}: [{label}]({target})"
            )

    # index checks under wiki and sources
    for tree in (WIKI, SOURCES, RAW):
        if not tree.is_dir():
            continue
        dirs = {p.parent for p in tree.rglob("*.md")}
        dirs.add(tree)
        for directory in sorted(dirs):
            index = directory / "index.md"
            if not index.is_file():
                # only require indexes where markdown siblings exist or known wiki folders
                siblings = list(directory.glob("*.md"))
                subdirs = [d for d in directory.iterdir() if d.is_dir()] if directory.is_dir() else []
                if not siblings and not subdirs:
                    continue
                if directory == tree or any(p.name != "index.md" for p in siblings) or subdirs:
                    errors.append(f"missing index: {rel(index)}")
                continue
            text = read_text(index)
            if text.startswith("---\n"):
                errors.append(f"index has frontmatter: {rel(index)}")
            if "# Contents" not in text:
                errors.append(f"index lacks # Contents: {rel(index)}")

    # Side-by-side index.base pairing (every index.md except vault root)
    if (ROOT / "index.base").is_file():
        errors.append("root must not have index.base (use bases.base only)")
    if not (ROOT / "bases.base").is_file():
        errors.append("missing bases.base at vault root")
    else:
        bases_text = read_text(ROOT / "bases.base")
        if 'file.ext == "base"' not in bases_text and "file.ext == 'base'" not in bases_text:
            errors.append("bases.base must filter file.ext == \"base\"")

    for directory in iter_index_md_dirs():
        if directory == ROOT:
            continue
        folder_rel = folder_rel_for_dir(directory)
        base_path = directory / "index.base"
        if not base_path.is_file():
            errors.append(f"missing index.base: {folder_rel}/index.base")
            continue
        base_text = read_text(base_path)
        needle = f'file.inFolder("{folder_rel}")'
        if needle not in base_text:
            errors.append(f"index.base folder mismatch: {folder_rel}/index.base (expected {needle})")

    for path in iter_wiki_concepts():
        text = read_text(path)
        relative = rel(path)
        meta = parse_frontmatter(text)
        if meta is None:
            errors.append(f"missing frontmatter: {relative}")
            continue
        for field in REQUIRED_WIKI_FIELDS:
            value = meta.get(field)
            if value is None or value == "" or value == []:
                errors.append(f"missing {field}: {relative}")
        if not tags_nonempty(meta):
            errors.append(f"empty tags: {relative}")

        status = meta.get("status")
        if status and str(status) not in ALLOWED_STATUS:
            errors.append(f"invalid status: {relative}: {status}")

        if "bible_reference" in meta:
            # re-check raw line format from file for quote flexibility
            fm = FRONTMATTER.match(text)
            if fm:
                ref_lines = [ln for ln in fm.group(1).splitlines() if ln.startswith("bible_reference:")]
                if ref_lines and not BIBLE_REFERENCE.match(ref_lines[0]):
                    errors.append(f"invalid bible_reference: {relative}")

        # source_count vs Sources section + source_path
        listed = resolve_source_paths_from_wiki(path, text, meta)
        # Prefer ## Sources section count when present; else all sources/ links
        section = sources_section_links(text)
        if section:
            expected = len({s for s in section})
        else:
            expected = len(listed)
        if "source_count" in meta:
            try:
                sc = int(str(meta.get("source_count")))
            except ValueError:
                errors.append(f"invalid source_count: {relative}")
                sc = -1
            if sc >= 0 and sc != expected and expected > 0:
                errors.append(
                    f"source_count mismatch: {relative}: source_count={sc} sources_listed={expected}"
                )
            if sc > 0 and expected == 0:
                errors.append(f"source_count > 0 but no source links: {relative}")

        # uncited core claims
        in_claims = False
        for line in text.splitlines():
            if line.strip() == "## Core claims":
                in_claims = True
                continue
            if in_claims and line.startswith("## "):
                in_claims = False
            if in_claims and line.startswith("- ") and "[[" not in line:
                errors.append(f"uncited core claim: {relative}: {line}")

        # broken / ambiguous wikilinks
        for raw_target in WIKILINK.findall(text):
            target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
            if not target:
                continue
            target_path = Path(unquote(target))
            if target_path.suffix != ".md":
                target_path = target_path.with_suffix(".md")
            if "/" in target:
                if not (ROOT / target_path).is_file():
                    errors.append(f"broken wikilink in {relative}: [[{raw_target}]]")
            else:
                matches = [p for p in all_markdown if p.stem == target_path.stem]
                if not matches:
                    errors.append(f"broken wikilink in {relative}: [[{raw_target}]]")
                elif len(matches) > 1:
                    errors.append(f"ambiguous wikilink in {relative}: [[{raw_target}]]")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} lint error(s)")
        return 1
    print("Wiki lint passed")
    return 0


def wiki_coverage_map() -> dict[str, list[str]]:
    """Map source path -> list of wiki paths that reference it."""
    coverage: dict[str, list[str]] = defaultdict(list)
    for path in iter_wiki_concepts():
        text = read_text(path)
        meta = parse_frontmatter(text) or {}
        for source_path in resolve_source_paths_from_wiki(path, text, meta):
            coverage[source_path].append(rel(path))
    return {k: sorted(set(v)) for k, v in coverage.items()}


def build_manifest_rows(accept_covered: bool) -> list[dict[str, Any]]:
    coverage = wiki_coverage_map() if accept_covered else {}
    existing = {row.get("path"): row for row in load_jsonl(MANIFEST)}
    rows: list[dict[str, Any]] = []
    for path in iter_source_docs():
        rpath = rel(path)
        text = read_text(path)
        meta = parse_frontmatter(text) or {}
        title = str(meta.get("title") or path.stem)
        covered_by = coverage.get(rpath, [])
        if not accept_covered and rpath in existing:
            covered_by = list(existing[rpath].get("covered_by") or [])
        rows.append(
            {
                "path": rpath,
                "title": title,
                "type": str(meta.get("type") or ""),
                "covered_by": covered_by,
                "updated": today(),
            }
        )
    rows.sort(key=lambda r: r["path"])
    return rows


def cmd_source_scan(args: argparse.Namespace) -> int:
    accept = bool(args.accept_covered)
    update = bool(args.update)
    rows = build_manifest_rows(accept_covered=accept if update else False)
    covered = sum(1 for r in rows if r.get("covered_by"))
    print(f"Source docs: {len(rows)} (currently covered by wiki links: {covered})")
    if not update:
        for row in rows:
            flag = "covered" if row.get("covered_by") else "open"
            if args.verbose or row.get("covered_by"):
                print(f"  [{flag}] {row['path']}")
        if not args.verbose:
            print("  (use --verbose to list all; covered files always listed when present)")
            for row in rows:
                if row.get("covered_by"):
                    print(f"  [covered] {row['path']} <- {', '.join(row['covered_by'])}")
        return 0

    # When update without accept-covered, preserve prior covered_by but refresh inventory
    if update and not accept:
        prior = {r.get("path"): r for r in load_jsonl(MANIFEST)}
        for row in rows:
            old = prior.get(row["path"])
            if old and old.get("covered_by"):
                row["covered_by"] = list(old["covered_by"])
    if update and accept:
        rows = build_manifest_rows(accept_covered=True)

    write_jsonl(MANIFEST, rows)
    covered = sum(1 for r in rows if r.get("covered_by"))
    print(f"Wrote {rel(MANIFEST)} ({len(rows)} rows, {covered} covered)")
    return 0


def cmd_source_lint(_: argparse.Namespace) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    if not MANIFEST.is_file():
        errors.append(f"missing manifest: {rel(MANIFEST)} (run source-scan --update --accept-covered)")
        for error in errors:
            print(f"ERROR {error}")
        return 1

    rows = load_jsonl(MANIFEST)
    on_disk = {rel(p) for p in iter_source_docs()}
    coverage = wiki_coverage_map()
    in_manifest = set()

    for row in rows:
        path = row.get("path")
        if not isinstance(path, str):
            errors.append("manifest row missing path")
            continue
        in_manifest.add(path)
        if path not in on_disk:
            errors.append(f"manifest path missing on disk: {path}")
            continue
        covered_by = row.get("covered_by") or []
        if covered_by:
            for wiki_path in covered_by:
                if not (ROOT / wiki_path).is_file():
                    errors.append(f"covered_by target missing: {path} -> {wiki_path}")
            # must still actually be referenced
            actual = coverage.get(path, [])
            if not actual:
                errors.append(f"marked covered but no wiki source links: {path}")

    # delta is warning only
    missing = sorted(on_disk - in_manifest)
    if missing:
        warnings.append(f"{len(missing)} source file(s) not in manifest (run source-scan --update)")

    for warning in warnings:
        print(f"WARN {warning}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} source-lint error(s)")
        return 1
    print(f"Source lint passed ({len(rows)} manifest rows)")
    return 0


def cmd_source_delta(_: argparse.Namespace) -> int:
    on_disk = {rel(p) for p in iter_source_docs()}
    in_manifest = {r.get("path") for r in load_jsonl(MANIFEST) if r.get("path")}
    missing = sorted(on_disk - in_manifest)
    extra = sorted(p for p in in_manifest if p not in on_disk)
    print(f"On disk but not in manifest: {len(missing)}")
    for path in missing[:50]:
        print(f"  + {path}")
    if len(missing) > 50:
        print(f"  ... and {len(missing) - 50} more")
    print(f"In manifest but missing on disk: {len(extra)}")
    for path in extra[:50]:
        print(f"  - {path}")
    return 0


def cmd_source_coverage(args: argparse.Namespace) -> int:
    """Report covered vs uncovered sources; optional path filter for Phase 4 gates."""
    rows = load_jsonl(MANIFEST)
    if not rows:
        # fall back to live scan
        rows = build_manifest_rows(accept_covered=True)

    path_filter = (getattr(args, "path", None) or "").strip()
    if path_filter:
        rows = [r for r in rows if path_filter in str(r.get("path") or "")]

    covered = [r for r in rows if r.get("covered_by")]
    open_rows = [r for r in rows if not r.get("covered_by")]
    scope = f" (filter: {path_filter!r})" if path_filter else ""
    print(f"Total sources{scope}: {len(rows)}")
    print(f"Covered: {len(covered)}")
    print(f"Uncovered: {len(open_rows)}")

    uncovered_only = bool(getattr(args, "uncovered_only", False))
    list_limit = int(getattr(args, "limit", 0) or 0)

    if uncovered_only:
        print("Uncovered paths:")
        to_show = open_rows if list_limit <= 0 else open_rows[:list_limit]
        for row in to_show:
            print(f"  {row['path']}")
        if list_limit > 0 and len(open_rows) > list_limit:
            print(f"  ... and {len(open_rows) - list_limit} more")
    elif not path_filter:
        # Full-vault default: covered detail (legacy behavior)
        print("Covered detail:")
        to_show = covered if list_limit <= 0 else covered[:list_limit]
        for row in to_show:
            print(f"  {row['path']}")
            for wp in row.get("covered_by") or []:
                print(f"    <- {wp}")
        if list_limit > 0 and len(covered) > list_limit:
            print(f"  ... and {len(covered) - list_limit} more")
    else:
        # Scoped filter: compact summary; optional uncovered list with --uncovered-only
        if open_rows and getattr(args, "verbose", False):
            print("Uncovered paths:")
            to_show = open_rows if list_limit <= 0 else open_rows[:list_limit]
            for row in to_show:
                print(f"  {row['path']}")
            if list_limit > 0 and len(open_rows) > list_limit:
                print(f"  ... and {len(open_rows) - list_limit} more")
        elif covered and getattr(args, "verbose", False):
            print("Covered detail:")
            for row in covered:
                print(f"  {row['path']}")
                for wp in row.get("covered_by") or []:
                    print(f"    <- {wp}")

    if bool(getattr(args, "require_zero", False)) and open_rows:
        print(f"FAIL: {len(open_rows)} uncovered source(s) in scope (require-zero)")
        return 1
    if bool(getattr(args, "require_zero", False)):
        print("OK: zero uncovered in scope")
    return 0


def tokenize_query(query: str) -> list[str]:
    return [t for t in re.split(r"[^\w:.-]+", query.lower()) if t]


def query_to_ref_hints(query: str) -> list[str]:
    """Extract normalized ref / book hints from a free-text query."""
    hints: list[str] = []
    q = query.replace("–", "-").replace("—", "-")
    # Display forms in the query itself
    for ref in extract_display_refs(q):
        hints.append(ref.lower())
    # Abbrev forms
    for match in ABBREV_REF.finditer(q.lower()):
        abbrev = lookup_abbrev(match.group(1))
        if not abbrev:
            continue
        chapter = int(match.group(2))
        verse = int(match.group(3)) if match.group(3) else None
        end = int(match.group(4)) if match.group(4) else None
        hints.append(format_norm_ref(abbrev, chapter, verse, end))
    # Book-name-only tokens (e.g. "matthew")
    for token in tokenize_query(query):
        abbrev = lookup_abbrev(token)
        if abbrev and abbrev in ABBREV_TO_KEY:
            hints.append(f"book:{ABBREV_TO_KEY[abbrev]}")
            hints.append(abbrev)
    # Dedup
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hints:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def score_catalog_row(
    row: dict[str, Any],
    terms: list[str],
    query: str,
    ref_hints: list[str],
    *,
    require_tag: str | None = None,
    require_ref: str | None = None,
    require_source: str | None = None,
    require_type: str | None = None,
) -> tuple[float, list[str]] | None:
    """Return (score, reasons) or None if filtered out / no match."""
    reasons: list[str] = []
    score = 0.0

    title = str(row.get("title") or "")
    title_l = title.lower()
    path = str(row.get("path") or "")
    path_l = path.lower()
    desc = str(row.get("description") or "")
    desc_l = desc.lower()
    type_s = str(row.get("type") or "")
    type_l = type_s.lower()
    tags = [str(t).lower() for t in (row.get("tags") or [])]
    aliases = [str(a).lower() for a in (row.get("aliases") or [])]
    refs = [str(r).lower() for r in (row.get("bible_references") or [])]
    if row.get("bible_reference"):
        refs = [str(row["bible_reference"]).lower()] + refs
    source_paths = [str(s).lower() for s in (row.get("source_paths") or [])]
    book_keys = set()
    for bk in row.get("bible_book_keys") or []:
        try:
            book_keys.add(int(bk))
        except (TypeError, ValueError):
            pass
    if row.get("bible_book_key") is not None:
        try:
            book_keys.add(int(row["bible_book_key"]))
        except (TypeError, ValueError):
            pass

    # Hard filters
    if require_tag and require_tag.lower() not in tags:
        return None
    if require_type and require_type.lower() not in type_l:
        return None
    if require_source:
        rs = require_source.lower()
        if not any(rs in sp for sp in source_paths):
            return None
    if require_ref:
        rr = require_ref.lower().replace("–", "-")
        # allow book name or abbrev or partial ref
        ref_ok = any(rr in r or r in rr for r in refs)
        # book filter: "mt" or "matthew" or "book:40"
        if not ref_ok:
            abbrev = lookup_abbrev(rr) if " " not in rr else None
            if abbrev and ABBREV_TO_KEY.get(abbrev) in book_keys:
                ref_ok = True
            if rr.startswith("book:"):
                try:
                    if int(rr.split(":", 1)[1]) in book_keys:
                        ref_ok = True
                except ValueError:
                    pass
            for hint_ref in extract_display_refs(require_ref):
                if any(hint_ref.lower() in r or r.startswith(hint_ref.lower()) for r in refs):
                    ref_ok = True
            # chapter-level: "mt 6" matches "mt 6:5-15"
            if not ref_ok:
                for r in refs:
                    if r.startswith(rr) or rr.startswith(r.split(":")[0]):
                        # stronger: same book+chapter prefix
                        if r.split(":")[0] == rr or r.startswith(rr + ":") or r.startswith(rr + " "):
                            ref_ok = True
                            break
                        parts_q = rr.split()
                        parts_r = r.split()
                        if len(parts_q) >= 2 and len(parts_r) >= 2:
                            if parts_q[0] == parts_r[0] and parts_q[1].split(":")[0] == parts_r[1].split(":")[0]:
                                ref_ok = True
                                break
        if not ref_ok:
            return None

    # If only filters and empty query, include with base score
    query_empty = not terms and not query.strip()

    # Title
    if query.strip() and query.strip().lower() == title_l:
        score += 10
        reasons.append("exact title")
    else:
        for t in terms:
            if t == title_l:
                score += 10
                reasons.append("exact title")
            elif t in title_l:
                score += 5
                reasons.append(f"title:{t}")

    # Tags
    for t in terms:
        if t in tags:
            score += 5
            reasons.append(f"tag:{t}")
        else:
            for tag in tags:
                if t in tag:
                    score += 2
                    reasons.append(f"tag-part:{tag}")
                    break

    # Aliases (frontmatter only)
    for t in terms:
        for alias in aliases:
            if t == alias or t in alias:
                score += 4
                reasons.append(f"alias:{alias}")
                break

    # Path basename
    base = Path(path).stem.lower()
    for t in terms:
        if t in base or t in path_l:
            score += 3
            reasons.append(f"path:{t}")
            break

    # Type token
    for t in terms:
        if t in type_l:
            score += 1
            reasons.append(f"type:{t}")

    # Description (lower weight; boilerplate-heavy)
    boilerplate = desc_l.startswith("a source-backed")
    desc_weight = 0.5 if boilerplate else 1.0
    for t in terms:
        if t in desc_l:
            score += desc_weight
            reasons.append(f"description:{t}")

    # Bible refs
    for hint in ref_hints:
        hint_l = hint.lower()
        if hint_l.startswith("book:"):
            try:
                bk = int(hint_l.split(":", 1)[1])
            except ValueError:
                continue
            if bk in book_keys:
                score += 4
                reasons.append(f"book:{bk}")
            continue
        # abbrev-only hint
        if re.fullmatch(r"[1-3]?[a-z]{1,5}", hint_l):
            abbrev = lookup_abbrev(hint_l)
            if abbrev and ABBREV_TO_KEY.get(abbrev) in book_keys:
                score += 2
                reasons.append(f"book-abbrev:{abbrev}")
            continue
        for r in refs:
            if r == hint_l:
                score += 8
                reasons.append(f"ref:{r}")
                break
            # chapter match: hint "mt 6" vs "mt 6:5-15"
            if r.startswith(hint_l + ":") or r.startswith(hint_l):
                score += 6
                reasons.append(f"ref-prefix:{r}")
                break
            hint_chapter = hint_l.split(":")[0]
            ref_chapter = r.split(":")[0]
            if hint_chapter == ref_chapter:
                score += 5
                reasons.append(f"ref-chapter:{r}")
                break

    # Source path tokens (skip pure numbers / very short tokens — too noisy)
    for t in terms:
        if t.isdigit() or len(t) < 3:
            continue
        for sp in source_paths:
            if t in sp:
                score += 3
                reasons.append(f"source:{t}")
                break

    # Status / source_count soft boosts
    status = str(row.get("status") or "")
    if status == "reviewed":
        score += 1
        reasons.append("status:reviewed")
    elif status == "developing":
        score += 0.5
    try:
        sc = int(row.get("source_count") or 0)
    except (TypeError, ValueError):
        sc = 0
    if sc > 0:
        score += min(sc, 5) * 0.2

    # Filter-only mode: matched filters already applied
    if query_empty and (
        require_tag or require_ref or require_source or require_type
    ):
        if score <= 0:
            score = 1.0
            reasons.append("filter-match")
        return (score, reasons)

    if score <= 0 and not reasons:
        return None
    # Require some substantive match when there is a query
    substantive = [
        r
        for r in reasons
        if not r.startswith("status:") and r not in {"filter-match"}
    ]
    # source_count boost alone should not match
    if not substantive and terms:
        return None
    return (score, reasons)


def cmd_search_catalog(args: argparse.Namespace) -> int:
    query = (args.query or "").strip()
    require_tag = getattr(args, "tag", None)
    require_ref = getattr(args, "ref", None)
    require_source = getattr(args, "source", None)
    require_type = getattr(args, "type", None)

    if not query and not any([require_tag, require_ref, require_source, require_type]):
        print("ERROR provide --query and/or a filter (--tag/--ref/--source/--type)")
        return 1
    if not CATALOG.is_file():
        print(f"ERROR missing catalog: {rel(CATALOG)} (run build)")
        return 1

    terms = tokenize_query(query) if query else []
    ref_hints = query_to_ref_hints(query) if query else []
    if require_ref:
        ref_hints = list(dict.fromkeys(ref_hints + query_to_ref_hints(require_ref)))

    hits: list[tuple[float, list[str], dict[str, Any]]] = []
    for row in load_jsonl(CATALOG):
        result = score_catalog_row(
            row,
            terms,
            query,
            ref_hints,
            require_tag=require_tag,
            require_ref=require_ref,
            require_source=require_source,
            require_type=require_type,
        )
        if result is None:
            continue
        score, reasons = result
        hits.append((score, reasons, row))

    hits.sort(key=lambda item: (-item[0], item[2].get("path", "")))
    limit = args.limit or 10
    label = query if query else "(filters only)"
    print(f"{len(hits)} hit(s) for {label!r} (showing up to {limit})")
    for score, reasons, row in hits[:limit]:
        # de-dupe reasons preserving order
        seen_r: set[str] = set()
        reason_list: list[str] = []
        for r in reasons:
            if r not in seen_r:
                seen_r.add(r)
                reason_list.append(r)
        reason_s = ", ".join(reason_list[:8])
        print(f"  [{score:.1f}] {row.get('path')} — {row.get('title')} ({row.get('type')})")
        if row.get("description"):
            print(f"       {row['description']}")
        if reason_s:
            print(f"       match: {reason_s}")
        refs = row.get("bible_references") or []
        if refs:
            print(f"       refs: {', '.join(str(r) for r in refs[:6])}")
    return 0


# ---------------------------------------------------------------------------
# Treasury of Scripture Knowledge (TSK) lookup
# ---------------------------------------------------------------------------

# Cache: book_key -> chapter -> verse -> list of {sort, word, refs: list[str]}
_TSK_INDEX: dict[int, dict[int, dict[int, list[dict[str, Any]]]]] | None = None
_TSK_STATS: dict[str, int] | None = None

# Single TSK ref token: "mt 6:9", "pr 8:22-24", "ps 33:6,9", "ps 33:6,9-11"
_TSK_TOKEN_RE = re.compile(
    r"^([1-3]?[a-z]+)\s+(\d+)(?::(.+))?$",
    re.IGNORECASE,
)


def tsk_data_path() -> Path:
    """Return path to tskxref.txt (overrideable in tests via TSK_XREF)."""
    return TSK_XREF


def load_tsk_index(force: bool = False) -> dict[int, dict[int, dict[int, list[dict[str, Any]]]]]:
    """Parse tskxref.txt into a nested dict. Cached for the process lifetime."""
    global _TSK_INDEX, _TSK_STATS
    if _TSK_INDEX is not None and not force:
        return _TSK_INDEX

    path = tsk_data_path()
    if not path.is_file():
        raise FileNotFoundError(
            f"TSK data missing: {rel(path) if path.is_relative_to(ROOT) else path}. "
            "Expected sources/reference/tsk/tskxref.txt"
        )

    index: dict[int, dict[int, dict[int, list[dict[str, Any]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    rows = 0
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        for line in handle:
            line = line.rstrip("\r\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            try:
                book = int(parts[0])
                chapter = int(parts[1])
                verse = int(parts[2])
                sort_order = int(parts[3])
            except ValueError:
                continue
            word = parts[4]
            ref_field = parts[5]
            refs = [r.strip() for r in ref_field.split(";") if r.strip()]
            index[book][chapter][verse].append(
                {"sort": sort_order, "word": word, "refs": refs}
            )
            rows += 1

    # Freeze nested defaultdicts into plain dicts; sort entries by sort order
    frozen: dict[int, dict[int, dict[int, list[dict[str, Any]]]]] = {}
    verse_count = 0
    for book, chapters in index.items():
        frozen[book] = {}
        for chapter, verses in chapters.items():
            frozen[book][chapter] = {}
            for verse, entries in verses.items():
                entries.sort(key=lambda e: (e["sort"], e["word"]))
                frozen[book][chapter][verse] = entries
                verse_count += 1

    _TSK_INDEX = frozen
    _TSK_STATS = {"rows": rows, "verses": verse_count}
    return _TSK_INDEX


def tsk_stats() -> dict[str, int]:
    load_tsk_index()
    assert _TSK_STATS is not None
    return dict(_TSK_STATS)


def parse_tsk_query(raw: str) -> tuple[int, int, int | None, int | None] | None:
    """Parse user ref/chapter query into (book_key, chapter, verse_start|None, verse_end|None).

    Accepts vault abbrevs and English book names, e.g.:
      mt 6:9 | Matthew 6:9 | mt 6 | mt 6:1-15 | joh 1:1-3
    """
    text = raw.strip().strip("'\"").replace("–", "-").replace("—", "-")
    if not text:
        return None

    # Prefer full book-name match (handles "1 Timothy 1:12")
    m = _BOOK_NAME_RE.match(text)
    if m and m.end() >= len(text.strip()):
        abbrev = lookup_abbrev(m.group(1))
        if not abbrev or abbrev not in ABBREV_TO_KEY:
            return None
        chapter = int(m.group(2))
        verse = int(m.group(3)) if m.group(3) else None
        end = int(m.group(4)) if m.group(4) else None
        return ABBREV_TO_KEY[abbrev], chapter, verse, end

    # Abbrev form: "mt 6:9", "1ti 1:12-14", "ge 1"
    m = re.match(
        r"^([1-3]?[a-z]+)\s+(\d+)(?::(\d+)(?:-(\d+))?)?\s*$",
        text,
        re.IGNORECASE,
    )
    if not m:
        return None
    abbrev = lookup_abbrev(m.group(1))
    if not abbrev or abbrev not in ABBREV_TO_KEY:
        return None
    chapter = int(m.group(2))
    verse = int(m.group(3)) if m.group(3) else None
    end = int(m.group(4)) if m.group(4) else None
    return ABBREV_TO_KEY[abbrev], chapter, verse, end


def format_tsk_ref_token(token: str) -> str:
    """Normalize a single TSK reference_list token for display; pass through unknowns."""
    token = token.strip()
    if not token:
        return token
    m = _TSK_TOKEN_RE.match(token)
    if not m:
        return token
    abbrev = lookup_abbrev(m.group(1))
    if not abbrev:
        return token
    chapter = m.group(2)
    rest = m.group(3)
    if not rest:
        return f"{abbrev} {chapter}"
    return f"{abbrev} {chapter}:{rest}"


def passage_hub_path(book_key: int, chapter: int) -> Path | None:
    """Return wiki/passages/<Book> <chapter>.md if it exists."""
    name = KEY_TO_NAME.get(book_key)
    if not name:
        return None
    path = WIKI / "passages" / f"{name} {chapter}.md"
    return path if path.is_file() else None


def tsk_entries_for(
    book_key: int,
    chapter: int,
    verse_start: int | None = None,
    verse_end: int | None = None,
) -> list[tuple[int, list[dict[str, Any]]]]:
    """Return sorted (verse, entries) pairs for a chapter or verse range."""
    index = load_tsk_index()
    chapters = index.get(book_key, {})
    verses_map = chapters.get(chapter, {})
    if not verses_map:
        return []

    if verse_start is None:
        keys = sorted(verses_map.keys())
    else:
        end = verse_end if verse_end is not None else verse_start
        if end < verse_start:
            verse_start, end = end, verse_start
        keys = [v for v in sorted(verses_map.keys()) if verse_start <= v <= end]

    return [(v, verses_map[v]) for v in keys]


def render_tsk_markdown(
    book_key: int,
    chapter: int,
    verse_start: int | None,
    verse_end: int | None,
    pairs: list[tuple[int, list[dict[str, Any]]]],
    *,
    max_refs: int = 0,
) -> str:
    abbrev = KEY_TO_ABBREV[book_key]
    book_name = KEY_TO_NAME[book_key]
    if verse_start is None:
        scope = f"{abbrev} {chapter}"
        title_scope = f"{book_name} {chapter}"
    elif verse_end is None or verse_end == verse_start:
        scope = f"{abbrev} {chapter}:{verse_start}"
        title_scope = f"{book_name} {chapter}:{verse_start}"
    else:
        scope = f"{abbrev} {chapter}:{verse_start}-{verse_end}"
        title_scope = f"{book_name} {chapter}:{verse_start}-{verse_end}"

    lines: list[str] = [
        f"# TSK — {title_scope}",
        "",
        f"Query: `{scope}`",
        f"Data: `{rel(tsk_data_path())}`",
        f"Provenance: `{rel(TSK_PROVENANCE)}`",
        "",
    ]
    hub = passage_hub_path(book_key, chapter)
    if hub:
        lines.append(f"Passage hub: [[{obsidian_link_target(hub)}|{book_name} {chapter}]]")
        lines.append("")

    if not pairs:
        lines.append("_No TSK entries for this reference._")
        lines.append("")
        return "\n".join(lines)

    for verse, entries in pairs:
        lines.append(f"## {abbrev} {chapter}:{verse}")
        lines.append("")
        for entry in entries:
            refs = entry["refs"]
            if max_refs and max_refs > 0:
                shown = refs[:max_refs]
                suffix = f"; … (+{len(refs) - max_refs} more)" if len(refs) > max_refs else ""
            else:
                shown = refs
                suffix = ""
            pretty = "; ".join(format_tsk_ref_token(r) for r in shown) + suffix
            word = entry["word"].strip() or "(phrase)"
            lines.append(f"- **{word}** — {pretty}")
        lines.append("")

    stats = tsk_stats()
    lines.append(
        f"_TSK table: {stats['rows']} entries across {stats['verses']} verses. "
        "Cross-references are traditional chains, not vault synthesis._"
    )
    lines.append("")
    return "\n".join(lines)


def render_tsk_plain(
    book_key: int,
    chapter: int,
    pairs: list[tuple[int, list[dict[str, Any]]]],
    *,
    max_refs: int = 0,
) -> str:
    abbrev = KEY_TO_ABBREV[book_key]
    out: list[str] = []
    if not pairs:
        return f"(no TSK entries for {abbrev} {chapter})"
    for verse, entries in pairs:
        for entry in entries:
            refs = entry["refs"]
            if max_refs and max_refs > 0:
                shown = refs[:max_refs]
                extra = f" …+{len(refs) - max_refs}" if len(refs) > max_refs else ""
            else:
                shown = refs
                extra = ""
            ref_s = ";".join(shown) + extra
            out.append(f"{abbrev} {chapter}:{verse}\t{entry['word']}\t{ref_s}")
    return "\n".join(out) + ("\n" if out else "")


def render_tsk_json(
    book_key: int,
    chapter: int,
    verse_start: int | None,
    verse_end: int | None,
    pairs: list[tuple[int, list[dict[str, Any]]]],
    *,
    max_refs: int = 0,
) -> str:
    abbrev = KEY_TO_ABBREV[book_key]
    book_name = KEY_TO_NAME[book_key]
    verses_out: list[dict[str, Any]] = []
    for verse, entries in pairs:
        entry_rows: list[dict[str, Any]] = []
        for entry in entries:
            refs = entry["refs"]
            if max_refs and max_refs > 0:
                refs = refs[:max_refs]
            entry_rows.append(
                {
                    "sort": entry["sort"],
                    "word": entry["word"],
                    "refs": refs,
                    "refs_display": [format_tsk_ref_token(r) for r in refs],
                }
            )
        verses_out.append({"verse": verse, "entries": entry_rows})

    hub = passage_hub_path(book_key, chapter)
    payload = {
        "book_key": book_key,
        "book_name": book_name,
        "abbrev": abbrev,
        "chapter": chapter,
        "verse_start": verse_start,
        "verse_end": verse_end,
        "passage_hub": rel(hub) if hub else None,
        "data_path": rel(tsk_data_path()),
        "verses": verses_out,
        "stats": tsk_stats(),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def cmd_tsk(args: argparse.Namespace) -> int:
    """Look up Treasury of Scripture Knowledge cross-references by verse or chapter."""
    raw = (args.ref or args.chapter or "").strip()
    if not raw:
        print("ERROR: provide --ref (verse or range) or --chapter", file=sys.stderr)
        return 2

    # --chapter forces chapter-wide even if a verse was typed
    parsed = parse_tsk_query(raw)
    if not parsed:
        print(f"ERROR: could not parse reference: {raw!r}", file=sys.stderr)
        print('  examples: --ref "mt 6:9"  --ref "Matthew 6:9-13"  --chapter "ge 1"', file=sys.stderr)
        return 2

    book_key, chapter, verse_start, verse_end = parsed
    if args.chapter is not None and args.ref is None:
        verse_start, verse_end = None, None

    try:
        pairs = tsk_entries_for(book_key, chapter, verse_start, verse_end)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    max_refs = int(args.max_refs or 0)
    fmt = (args.format or "markdown").lower()
    if fmt in {"md", "markdown"}:
        sys.stdout.write(
            render_tsk_markdown(
                book_key, chapter, verse_start, verse_end, pairs, max_refs=max_refs
            )
        )
    elif fmt == "plain":
        sys.stdout.write(render_tsk_plain(book_key, chapter, pairs, max_refs=max_refs))
    elif fmt == "json":
        sys.stdout.write(
            render_tsk_json(
                book_key, chapter, verse_start, verse_end, pairs, max_refs=max_refs
            )
        )
    else:
        print(f"ERROR: unknown --format {args.format!r} (use markdown|plain|json)", file=sys.stderr)
        return 2

    if not pairs:
        return 1
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    title = (args.title or "").strip()
    details = (args.details or "").strip()
    if not title:
        print("ERROR --title is required")
        return 1
    if not LOG.is_file():
        print(f"ERROR missing log: {rel(LOG)}")
        return 1
    entry_lines = [f"## [{today()}] {title}", ""]
    if details:
        for line in details.split("\n"):
            line = line.strip()
            if not line:
                continue
            if not line.startswith("- "):
                line = f"- {line}"
            entry_lines.append(line)
    else:
        entry_lines.append("- (no details provided)")
    entry_lines.append("")
    existing = read_text(LOG)
    prefix = "" if existing.endswith("\n\n") or existing.endswith("\n") and existing.splitlines()[-1] == "" else "\n"
    if existing and not existing.endswith("\n"):
        prefix = "\n\n"
    elif existing and not existing.endswith("\n\n"):
        prefix = "\n"
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(prefix + "\n".join(entry_lines))
    print(f"Appended log entry to {rel(LOG)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bible Vault wiki maintenance tool")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Non-mutating health check")
    sub.add_parser(
        "build",
        help="Generate catalog, reverse indexes, wiki index.md, and side-by-side index.base files",
    )
    sub.add_parser("lint", help="Validate wiki notes")

    scan = sub.add_parser("source-scan", help="List or update source manifest")
    scan.add_argument("--update", action="store_true", help="Write schema/source-manifest.jsonl")
    scan.add_argument(
        "--accept-covered",
        action="store_true",
        help="Derive covered_by from wiki source links",
    )
    scan.add_argument("--verbose", action="store_true", help="List every source path")

    sub.add_parser("source-lint", help="Validate source manifest consistency")
    sub.add_parser("source-delta", help="Show disk vs manifest deltas")
    cov = sub.add_parser(
        "source-coverage",
        help="Show wiki coverage of sources (optional path filter for Phase 4 zero-uncovered gates)",
    )
    cov.add_argument(
        "--path",
        default="",
        help="Substring filter on source path (e.g. chspurgeon-sermons, mhenry-complete/volume-1, chspurgeon-fcb/january)",
    )
    cov.add_argument(
        "--uncovered-only",
        action="store_true",
        help="List uncovered paths instead of covered detail",
    )
    cov.add_argument(
        "--require-zero",
        action="store_true",
        help="Exit 1 if any uncovered files remain in scope (campaign gate)",
    )
    cov.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Max paths to print in detail lists (0 = no limit)",
    )
    cov.add_argument(
        "--verbose",
        action="store_true",
        help="With --path, also print uncovered (or covered) path detail",
    )

    search = sub.add_parser("search-catalog", help="Search wiki/catalog.jsonl")
    search.add_argument("--query", default="", help="Search text (optional if a filter is set)")
    search.add_argument("--tag", default=None, help="Require this thematic tag")
    search.add_argument("--ref", default=None, help="Require Bible ref/book match (e.g. 'mt 6' or 'Matthew')")
    search.add_argument("--source", default=None, help="Require source path substring")
    search.add_argument("--type", default=None, help="Require page type substring")
    search.add_argument("--limit", type=int, default=10, help="Max hits")

    tsk = sub.add_parser(
        "tsk",
        help="Look up Treasury of Scripture Knowledge cross-references (tool-only; data under sources/reference/tsk/)",
    )
    tsk_scope = tsk.add_mutually_exclusive_group(required=True)
    tsk_scope.add_argument(
        "--ref",
        default=None,
        help="Verse or range (e.g. 'mt 6:9', 'Matthew 6:9-13', 'ge 1:1')",
    )
    tsk_scope.add_argument(
        "--chapter",
        default=None,
        help="Full chapter (e.g. 'mt 6', 'Genesis 1'); ignores any verse if present",
    )
    tsk.add_argument(
        "--format",
        choices=("markdown", "md", "plain", "json"),
        default="markdown",
        help="Output format (default: markdown)",
    )
    tsk.add_argument(
        "--max-refs",
        type=int,
        default=0,
        help="Cap refs listed per keyword entry (0 = all)",
    )

    log = sub.add_parser("log", help="Append an entry to wiki/log.md")
    log.add_argument("--title", required=True, help="Log title after the date")
    log.add_argument("--details", default="", help="Details (newline-separated bullets ok)")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command = args.command.replace("-", "_")
    dispatch = {
        "doctor": cmd_doctor,
        "build": cmd_build,
        "lint": cmd_lint,
        "source_scan": cmd_source_scan,
        "source_lint": cmd_source_lint,
        "source_delta": cmd_source_delta,
        "source_coverage": cmd_source_coverage,
        "search_catalog": cmd_search_catalog,
        "tsk": cmd_tsk,
        "log": cmd_log,
    }
    return dispatch[command](args)


if __name__ == "__main__":
    sys.exit(main())
