#!/usr/bin/env python3
"""Phase 4 full-corpus coverage helpers.

Generate volume/month source-notes that cite every content source file, and
thicken matching passage pages for mhenry-complete and chspurgeon-tod.

Usage examples:
  python3 .tools/scripts/phase4_cover.py complete-volume 1
  python3 .tools/scripts/phase4_cover.py tod-volume 1
  python3 .tools/scripts/phase4_cover.py sermon-volumes 1 10
  python3 .tools/scripts/phase4_cover.py fcb-month january
  python3 .tools/scripts/phase4_cover.py mae-month january
  python3 .tools/scripts/phase4_cover.py fcb-root
  python3 .tools/scripts/phase4_cover.py mae-root
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "sources" / "commentaries_english"
WIKI = ROOT / "wiki"
SOURCE_NOTES = WIKI / "source-notes"
PASSAGES = WIKI / "passages"

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n?", re.S)
WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")

BOOK_FOLDER_TO_PASSAGE = {
    "genesis": "Genesis",
    "exodus": "Exodus",
    "leviticus": "Leviticus",
    "numbers": "Numbers",
    "deuteronomy": "Deuteronomy",
    "joshua": "Joshua",
    "judges": "Judges",
    "ruth": "Ruth",
    "1-samuel": "1 Samuel",
    "2-samuel": "2 Samuel",
    "1-kings": "1 Kings",
    "2-kings": "2 Kings",
    "1-chronicles": "1 Chronicles",
    "2-chronicles": "2 Chronicles",
    "ezra": "Ezra",
    "nehemiah": "Nehemiah",
    "esther": "Esther",
    "job": "Job",
    "psalms": "Psalm",
    "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes",
    "song-of-solomon": "Song of Solomon",
    "isaiah": "Isaiah",
    "jeremiah": "Jeremiah",
    "lamentations": "Lamentations",
    "ezekiel": "Ezekiel",
    "daniel": "Daniel",
    "hosea": "Hosea",
    "joel": "Joel",
    "amos": "Amos",
    "obadiah": "Obadiah",
    "jonah": "Jonah",
    "micah": "Micah",
    "nahum": "Nahum",
    "habakkuk": "Habakkuk",
    "zephaniah": "Zephaniah",
    "haggai": "Haggai",
    "zechariah": "Zechariah",
    "malachi": "Malachi",
    "matthew": "Matthew",
    "mark": "Mark",
    "luke": "Luke",
    "john": "John",
    "acts": "Acts",
    "romans": "Romans",
    "1-corinthians": "1 Corinthians",
    "2-corinthians": "2 Corinthians",
    "galatians": "Galatians",
    "ephesians": "Ephesians",
    "philippians": "Philippians",
    "colossians": "Colossians",
    "1-thessalonians": "1 Thessalonians",
    "2-thessalonians": "2 Thessalonians",
    "1-timothy": "1 Timothy",
    "2-timothy": "2 Timothy",
    "titus": "Titus",
    "philemon": "Philemon",
    "hebrews": "Hebrews",
    "james": "James",
    "1-peter": "1 Peter",
    "2-peter": "2 Peter",
    "1-john": "1 John",
    "2-john": "2 John",
    "3-john": "3 John",
    "jude": "Jude",
    "revelation": "Revelation",
}

BOOK_FOLDER_TO_DISPLAY = {k: ("Psalms" if v == "Psalm" else v) for k, v in BOOK_FOLDER_TO_PASSAGE.items()}

COMPLETE_TAGS = {
    1: ["creation", "covenant", "holiness", "redemption", "worship"],
    2: ["covenant", "faith", "justice", "worship", "discipleship"],
    3: ["wisdom", "prayer", "worship", "holiness", "faith"],
    4: ["prophecy", "christ", "salvation", "justice", "covenant"],
    5: ["christ", "discipleship", "salvation", "faith", "church"],
    6: ["church", "holy-spirit", "faith", "salvation", "prophecy"],
}

TOD_TAGS = ["prayer", "worship", "christ", "faith", "holiness"]
SERMON_TAGS = ["salvation", "christ", "faith", "church", "prayer"]
FCB_TAGS = ["faith", "christian-life", "prayer", "salvation", "covenant"]
MAE_TAGS = ["christian-life", "christ", "prayer", "holiness", "faith"]


def today() -> str:
    return date.today().isoformat()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    m = FRONTMATTER.match(text)
    if not m:
        return None
    meta: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def body_after_frontmatter(text: str) -> str:
    m = FRONTMATTER.match(text)
    return text[m.end() :] if m else text


def first_claim_excerpt(text: str, limit: int = 220) -> str:
    body = body_after_frontmatter(text)
    # drop headings and blockquotes-only noise; take first substantial prose line/paragraph
    paras: list[str] = []
    buf: list[str] = []
    for line in body.splitlines():
        s = line.strip()
        if not s:
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        if s.startswith("#") or s.startswith(">"):
            if buf:
                paras.append(" ".join(buf))
                buf = []
            continue
        if s.startswith("---"):
            continue
        # strip simple markdown bold/italic markers for cleaner claim text
        s = re.sub(r"[*_`]", "", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            buf.append(s)
    if buf:
        paras.append(" ".join(buf))
    for para in paras:
        # skip pure short titles
        if len(para) < 40:
            continue
        claim = para
        if len(claim) > limit:
            claim = claim[: limit - 1].rsplit(" ", 1)[0] + "…"
        return claim
    # fallback: title-ish
    meta = parse_frontmatter(text) or {}
    title = meta.get("title") or "Source digest"
    return f"Digest of {title}."


def content_md_files(directory: Path) -> list[Path]:
    files = []
    for path in sorted(directory.rglob("*.md")):
        if path.name == "index.md":
            continue
        files.append(path)
    return files


def source_wikilink(path: Path, label: str) -> str:
    target = rel(path)
    if target.endswith(".md"):
        target = target[:-3]
    # escape pipe in label
    label = label.replace("|", "-")
    return f"[[{target}|{label}]]"


def yaml_list(tags: list[str]) -> str:
    return "[" + ", ".join(tags) + "]"


def ensure_passage_link(
    passage_path: Path,
    source_path: Path,
    claim: str,
    label: str,
    related_note: str | None = None,
    tension_note: str | None = None,
) -> bool:
    """Add claim + Sources link to passage page if source not already linked. Returns True if changed."""
    if not passage_path.is_file():
        return False
    text = read_text(passage_path)
    src_rel = rel(source_path)
    src_no_md = src_rel[:-3] if src_rel.endswith(".md") else src_rel
    if src_no_md in text or src_rel in text:
        return False

    link = source_wikilink(source_path, label)
    claim_line = f"- {claim} {link}"

    # Insert claim before next ## after Core claims, or append under Core claims
    if "## Core claims" in text:
        parts = text.split("## Core claims", 1)
        head, rest = parts[0], parts[1]
        # rest starts with newline then content until next ##
        m = re.match(r"(\n+)(.*?)(\n## )", rest, re.S)
        if m:
            claims_body = m.group(2).rstrip()
            claims_body = claims_body + "\n" + claim_line
            rest = m.group(1) + claims_body + "\n" + m.group(3) + rest[m.end() :]
            text = head + "## Core claims" + rest
        else:
            text = text.rstrip() + "\n" + claim_line + "\n"
    else:
        text = text.rstrip() + "\n\n## Core claims\n\n" + claim_line + "\n"

    # Sources section
    src_bullet = f"- {link}"
    if "## Sources" in text:
        parts = text.split("## Sources", 1)
        head, rest = parts[0], parts[1]
        # rest begins after the heading; find next ## or end
        m = re.match(r"(\n*)(.*)", rest, re.S)
        assert m
        leading_nl, after = m.group(1), m.group(2)
        next_h = re.search(r"\n## ", after)
        if next_h:
            sources_body = after[: next_h.start()].rstrip()
            tail = after[next_h.start() :]
        else:
            sources_body = after.rstrip()
            tail = ""
        if src_no_md not in sources_body and src_rel not in sources_body:
            sources_body = (sources_body + "\n" if sources_body else "") + src_bullet
        links = set()
        for raw in WIKILINK.findall(sources_body):
            t = raw.split("|", 1)[0].split("#", 1)[0].strip()
            if t.startswith("sources/"):
                if not t.endswith(".md"):
                    t = t + ".md"
                links.add(t)
        count = len(links)
        text = head + "## Sources" + leading_nl + sources_body + "\n" + tail
        text = re.sub(
            r"(?m)^source_count:\s*\d+\s*$",
            f"source_count: {count}",
            text,
            count=1,
        )
    else:
        text = text.rstrip() + "\n\n## Sources\n\n" + src_bullet + "\n"
        text = re.sub(r"(?m)^source_count:\s*\d+\s*$", "source_count: 1", text, count=1)

    text = re.sub(r"(?m)^updated:\s*.*$", f"updated: {today()}", text, count=1)

    if related_note and related_note not in text:
        if "## Related pages" in text:
            text = text.replace(
                "## Related pages\n",
                f"## Related pages\n\n- [[{related_note}|{related_note.split('/')[-1]}]]\n",
                1,
            )

    if tension_note and "## Agreements and tensions" in text and tension_note not in text:
        text = text.replace(
            "## Agreements and tensions\n",
            f"## Agreements and tensions\n\n{tension_note}\n",
            1,
        )

    write_text(passage_path, text)
    return True


def write_source_note(
    path: Path,
    *,
    title: str,
    description: str,
    tags: list[str],
    summary: str,
    claims: list[tuple[str, Path, str]],
    sources: list[tuple[Path, str]],
    related: list[str],
    biblical: str,
    tensions: str,
    open_q: str,
    extra_fm: dict[str, str] | None = None,
) -> None:
    # claims: (claim_text, source_path, label)
    source_count = len({rel(p) for p, _ in sources})
    fm_lines = [
        "---",
        "type: Source Note",
        f"title: {title}",
        f"description: {description}",
        f"tags: {yaml_list(tags)}",
        "status: developing",
        f"updated: {today()}",
        f"source_count: {source_count}",
    ]
    if extra_fm:
        for k, v in extra_fm.items():
            if v.startswith('"') or v.startswith("'") or v.startswith("["):
                fm_lines.append(f"{k}: {v}")
            elif any(c in v for c in ":#{}[]&*!|>'\"%@`"):
                fm_lines.append(f'{k}: "{v}"')
            else:
                fm_lines.append(f"{k}: {v}")
    fm_lines.append("---")

    claim_lines = [f"- {c} {source_wikilink(p, lab)}" for c, p, lab in claims]
    source_lines = [f"- {source_wikilink(p, lab)}" for p, lab in sources]
    related_lines = [f"- [[{r}|{r.split('/')[-1]}]]" for r in related]

    body = "\n".join(
        [
            f"# {title}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Core claims",
            "",
            *claim_lines,
            "",
            "## Agreements and tensions",
            "",
            tensions,
            "",
            "## Biblical passages",
            "",
            biblical,
            "",
            "## Related pages",
            "",
            *related_lines,
            "",
            "## Sources",
            "",
            *source_lines,
            "",
            "## Open questions",
            "",
            open_q,
            "",
        ]
    )
    write_text(path, "\n".join(fm_lines) + "\n\n" + body)


def complete_volume(vol: int) -> None:
    vol_dir = SOURCES / "mhenry-complete" / f"volume-{vol}"
    if not vol_dir.is_dir():
        raise SystemExit(f"missing {vol_dir}")
    files = content_md_files(vol_dir)
    note_path = SOURCE_NOTES / f"Matthew Henry Complete Volume {vol}.md"
    note_rel = f"wiki/source-notes/Matthew Henry Complete Volume {vol}"

    claims: list[tuple[str, Path, str]] = []
    sources: list[tuple[Path, str]] = []
    related_passages: list[str] = []
    thickened = 0

    for path in files:
        rel_parts = path.relative_to(vol_dir).parts
        label = path.stem
        passage_path: Path | None = None
        if path.name == "preface.md":
            label = f"Complete Vol {vol} preface"
        elif len(rel_parts) >= 2:
            book_folder = rel_parts[0]
            book = BOOK_FOLDER_TO_PASSAGE.get(book_folder)
            m = re.match(r"(?:chapter|psalm)-(\d+)$", path.stem)
            if book and m:
                num = int(m.group(1))
                passage_name = f"{book} {num}"
                label = f"Matthew Henry Complete on {passage_name}"
                passage_path = PASSAGES / f"{passage_name}.md"
                related_passages.append(f"wiki/passages/{passage_name}")
        claim = first_claim_excerpt(read_text(path))
        claims.append((claim, path, label))
        sources.append((path, label))
        if passage_path:
            if ensure_passage_link(
                passage_path,
                path,
                claim,
                label,
                related_note=note_rel,
                tension_note=(
                    "Complete commentary on this chapter deepens the Concise atlas with fuller pastoral and doctrinal exposition (Phase 4.1)."
                ),
            ):
                thickened += 1

    # unique related passages (cap list size for huge volumes by sorting unique)
    uniq_passages = sorted(set(related_passages))
    related = uniq_passages[:40] + [
        "wiki/campaigns/tracker",
        "wiki/source-notes/Matthew Henry Complete Hub Deepening",
    ]
    # concept mesh pointers by volume
    concept_map = {
        1: ["wiki/concepts/Creation", "wiki/concepts/Covenant", "wiki/concepts/Redemption"],
        2: ["wiki/concepts/Covenant", "wiki/concepts/Faith", "wiki/concepts/Justice"],
        3: ["wiki/concepts/Wisdom", "wiki/concepts/Prayer", "wiki/concepts/Worship"],
        4: ["wiki/concepts/Prophecy", "wiki/concepts/Christ", "wiki/concepts/Salvation"],
        5: ["wiki/concepts/Christ", "wiki/concepts/Discipleship", "wiki/concepts/Church"],
        6: ["wiki/concepts/Church", "wiki/concepts/Holy Spirit", "wiki/concepts/Prophecy"],
    }
    related.extend(concept_map.get(vol, []))

    write_source_note(
        note_path,
        title=f"Matthew Henry Complete Volume {vol}",
        description=(
            f"Full-file Phase 4.1 coverage of Matthew Henry Complete volume {vol}: "
            f"every chapter/preface file cited; matching passage atlas thickened."
        ),
        tags=COMPLETE_TAGS.get(vol, ["christian-life"]),
        summary=(
            f"Phase 4.1 full coverage for **Matthew Henry Complete volume {vol}** "
            f"({len(files)} content files under `{rel(vol_dir)}`). "
            f"Each file is listed under Sources with a short digest claim. "
            f"Matching [[wiki/passages/index|passage]] pages receive a Complete claim/link when a chapter map exists "
            f"({thickened} passage pages updated this run)."
        ),
        claims=claims,
        sources=sources,
        related=related,
        biblical=f"All chapters covered by Complete volume {vol} source tree.",
        tensions=(
            "Complete is fuller and more pastoral-doctrinal than Concise on the same chapters; "
            "retain Concise atlas summaries and add Complete claims without erasing Concise wording."
        ),
        open_q="Which Complete chapters still need dual-source tension notes beyond the auto digest?",
        extra_fm={"source_path": f'"sources/commentaries_english/mhenry-complete/volume-{vol}/"'},
    )
    print(f"complete volume {vol}: {len(files)} files, {thickened} passages thickened -> {rel(note_path)}")


def tod_volume(vol: int) -> None:
    vol_dir = SOURCES / "chspurgeon-tod" / f"volume-{vol}"
    if not vol_dir.is_dir():
        raise SystemExit(f"missing {vol_dir}")
    files = content_md_files(vol_dir)
    note_path = SOURCE_NOTES / f"Spurgeon Treasury of David Volume {vol}.md"
    note_rel = f"wiki/source-notes/Spurgeon Treasury of David Volume {vol}"

    claims: list[tuple[str, Path, str]] = []
    sources: list[tuple[Path, str]] = []
    related_passages: list[str] = []
    thickened = 0
    psalm_linked: set[int] = set()

    for path in files:
        claim = first_claim_excerpt(read_text(path))
        m = re.search(r"psalm-(\d+)", path.as_posix())
        if path.name == "preface.md":
            label = f"Treasury of David Vol {vol} preface"
            passage_path = None
        elif m:
            pnum = int(m.group(1))
            if path.parent.name == f"psalm-{pnum}" or path.stem.startswith("verses-"):
                label = f"Treasury of David, Psalm {pnum} ({path.stem})"
            else:
                label = f"Treasury of David, Psalm {pnum}"
            passage_path = PASSAGES / f"Psalm {pnum}.md"
            related_passages.append(f"wiki/passages/Psalm {pnum}")
        else:
            label = f"Treasury of David {path.stem}"
            passage_path = None

        claims.append((claim, path, label))
        sources.append((path, label))

        if passage_path and passage_path.is_file():
            # one claim per source file on the passage if multi-file (119); else one per psalm file
            if ensure_passage_link(
                passage_path,
                path,
                claim,
                label,
                related_note=note_rel,
                tension_note=(
                    "Treasury of David thickens the Concise Psalm atlas with homiletical exposition and historical citations (Phase 4.2)."
                ),
            ):
                thickened += 1
            if m:
                psalm_linked.add(int(m.group(1)))

    related = sorted(set(related_passages))[:50] + [
        "wiki/concepts/Prayer",
        "wiki/concepts/Worship",
        "wiki/concepts/Christ",
        "wiki/source-notes/Matthew Henry Concise on Psalms",
        "wiki/campaigns/tracker",
    ]
    write_source_note(
        note_path,
        title=f"Spurgeon Treasury of David Volume {vol}",
        description=(
            f"Phase 4.2 full-file coverage of Treasury of David volume {vol}: "
            f"every psalm/preface content file listed; Psalm passage pages thickened."
        ),
        tags=TOD_TAGS,
        summary=(
            f"Phase 4.2 full coverage for **Treasury of David volume {vol}** "
            f"({len(files)} content files). Every file is cited under Sources with a digest claim. "
            f"Matching Psalm passage pages updated where present ({thickened} writes; "
            f"{len(psalm_linked)} distinct psalms touched)."
        ),
        claims=claims,
        sources=sources,
        related=related,
        biblical=f"Psalms covered by ToD volume {vol} tree.",
        tensions=(
            "ToD is more homiletical and citation-rich than Henry Concise. "
            "Where Christological reading intensity differs, keep both claims on the passage page."
        ),
        open_q="Which non-hub psalms still need dual Henry/Spurgeon tension notes beyond digests?",
        extra_fm={
            "source_path": f'"sources/commentaries_english/chspurgeon-tod/volume-{vol}/"',
            "bible_book_key": "19",
            "bible_book_name": '"Psalms"',
        },
    )
    print(f"tod volume {vol}: {len(files)} files, {thickened} passage writes -> {rel(note_path)}")


def sermon_volumes(start: int, end: int) -> list[Path]:
    notes: list[Path] = []
    for vol in range(start, end + 1):
        vol_dir = SOURCES / "chspurgeon-sermons" / f"volume-{vol}"
        if not vol_dir.is_dir():
            print(f"skip missing {vol_dir}", file=sys.stderr)
            continue
        files = content_md_files(vol_dir)
        note_path = SOURCE_NOTES / f"Spurgeon Sermons Volume {vol}.md"
        claims: list[tuple[str, Path, str]] = []
        sources: list[tuple[Path, str]] = []
        for path in files:
            meta = parse_frontmatter(read_text(path)) or {}
            title = meta.get("title") or path.stem.replace("_", "-")
            # short label
            label = title.split("|")[0].strip() if "|" in title else title
            if len(label) > 80:
                label = label[:77] + "…"
            claim = first_claim_excerpt(read_text(path), limit=200)
            claims.append((claim, path, label))
            sources.append((path, label))
        write_source_note(
            note_path,
            title=f"Spurgeon Sermons Volume {vol}",
            description=(
                f"Phase 4.3 volume source-note listing every sermon file in Spurgeon sermons volume {vol}."
            ),
            tags=SERMON_TAGS,
            summary=(
                f"Phase 4.3 full coverage for **Spurgeon sermons volume {vol}** "
                f"({len(files)} sermon files). Theme mesh belongs on concept pages; "
                f"this note ensures every sermon file is wiki-linked (no one-page-per-sermon)."
            ),
            claims=claims,
            sources=sources,
            related=[
                "wiki/concepts/Salvation",
                "wiki/concepts/Faith",
                "wiki/concepts/Christ",
                "wiki/concepts/Church",
                "wiki/concepts/Prayer",
                "wiki/source-notes/Spurgeon Theme Batch — Salvation and Justification",
                "wiki/campaigns/tracker",
            ],
            biblical="Multiple passages across the volume (see individual sermon frontmatter).",
            tensions=(
                "Sermon rhetoric is applicative and often more particularistic than Henry's chapter expositions; "
                "record Henry vs Spurgeon tensions on concept pages rather than forcing consensus here."
            ),
            open_q="Which sermons in this volume deserve concept-level claims beyond the volume inventory?",
            extra_fm={"source_path": f'"sources/commentaries_english/chspurgeon-sermons/volume-{vol}/"'},
        )
        notes.append(note_path)
        print(f"sermon volume {vol}: {len(files)} files -> {rel(note_path)}")
    return notes


def month_corpus(corpus: str, month: str, *, title_prefix: str, tags: list[str]) -> None:
    month = month.lower()
    base = SOURCES / corpus / month
    if not base.is_dir():
        raise SystemExit(f"missing {base}")
    files = content_md_files(base)
    pretty = month.capitalize()
    if corpus == "chspurgeon-fcb":
        title = f"Spurgeon Faith's Checkbook — {pretty}"
        fname = f"Spurgeon Faith's Checkbook — {pretty}.md"
        concept = "wiki/source-notes/Spurgeon Faith's Checkbook Theme Enrichment"
    else:
        title = f"Spurgeon Morning and Evening — {pretty}"
        fname = f"Spurgeon Morning and Evening — {pretty}.md"
        concept = "wiki/source-notes/Spurgeon Morning and Evening Theme Enrichment"
    note_path = SOURCE_NOTES / fname
    claims: list[tuple[str, Path, str]] = []
    sources: list[tuple[Path, str]] = []
    for path in files:
        meta = parse_frontmatter(read_text(path)) or {}
        label = (meta.get("title") or path.stem).split("|")[0].strip()
        if len(label) > 90:
            label = label[:87] + "…"
        claim = first_claim_excerpt(read_text(path), limit=200)
        claims.append((claim, path, label))
        sources.append((path, label))
    write_source_note(
        note_path,
        title=title,
        description=(
            f"Phase 4 full-calendar month source-note for {title_prefix} {pretty}: "
            f"every daily entry file listed."
        ),
        tags=tags,
        summary=(
            f"Phase 4 full coverage for **{title_prefix} — {pretty}** "
            f"({len(files)} day files under `{rel(base)}`). "
            f"Light applicative digests only; doctrine stays on fuller commentary sources."
        ),
        claims=claims,
        sources=sources,
        related=[
            concept,
            "wiki/concepts/Faith",
            "wiki/concepts/Prayer",
            "wiki/concepts/Christian Life" if (WIKI / "concepts" / "Christian Life.md").is_file() else "wiki/concepts/Discipleship",
            "wiki/campaigns/tracker",
        ],
        biblical="Daily texts vary; see individual entry frontmatter/body.",
        tensions=(
            "Devotional entries are applicative and brief; do not overweight them against Complete/Concise or full sermons on contested doctrine."
        ),
        open_q="Any day in this month that should promote a durable concept claim beyond the month note?",
        extra_fm={"source_path": f'"sources/commentaries_english/{corpus}/{month}/"'},
    )
    print(f"{corpus} {month}: {len(files)} files -> {rel(note_path)}")


def fcb_root() -> None:
    root = SOURCES / "chspurgeon-fcb"
    files = [p for p in root.glob("*.md") if p.name != "index.md"]
    if not files:
        print("fcb-root: nothing")
        return
    note_path = SOURCE_NOTES / "Spurgeon Faith's Checkbook — Front Matter.md"
    claims = []
    sources = []
    for path in files:
        claim = first_claim_excerpt(read_text(path))
        label = f"Faith's Checkbook {path.stem}"
        claims.append((claim, path, label))
        sources.append((path, label))
    write_source_note(
        note_path,
        title="Spurgeon Faith's Checkbook — Front Matter",
        description="Phase 4 coverage of FCB root preface/verses files outside monthly folders.",
        tags=FCB_TAGS,
        summary=f"Covers {len(files)} root-level Faith's Checkbook content files (preface/verses).",
        claims=claims,
        sources=sources,
        related=["wiki/source-notes/Spurgeon Faith's Checkbook Theme Enrichment", "wiki/campaigns/tracker"],
        biblical="Front matter / verse index for the annual promise cycle.",
        tensions="N/A — apparatus files.",
        open_q="None.",
    )
    print(f"fcb-root: {len(files)} -> {rel(note_path)}")


def mae_root() -> None:
    root = SOURCES / "chspurgeon-mae"
    files = [p for p in root.glob("*.md") if p.name != "index.md"]
    if not files:
        print("mae-root: no root content md (ok)")
        return
    note_path = SOURCE_NOTES / "Spurgeon Morning and Evening — Front Matter.md"
    claims = []
    sources = []
    for path in files:
        claim = first_claim_excerpt(read_text(path))
        label = f"Morning and Evening {path.stem}"
        claims.append((claim, path, label))
        sources.append((path, label))
    write_source_note(
        note_path,
        title="Spurgeon Morning and Evening — Front Matter",
        description="Phase 4 coverage of MAE root content files outside monthly folders.",
        tags=MAE_TAGS,
        summary=f"Covers {len(files)} root-level Morning and Evening content files.",
        claims=claims,
        sources=sources,
        related=["wiki/source-notes/Spurgeon Morning and Evening Theme Enrichment", "wiki/campaigns/tracker"],
        biblical="Front matter for the daily morning/evening cycle.",
        tensions="N/A — apparatus files.",
        open_q="None.",
    )
    print(f"mae-root: {len(files)} -> {rel(note_path)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 4 coverage generators")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("complete-volume")
    p.add_argument("volume", type=int)

    p = sub.add_parser("tod-volume")
    p.add_argument("volume", type=int)

    p = sub.add_parser("sermon-volumes")
    p.add_argument("start", type=int)
    p.add_argument("end", type=int)

    p = sub.add_parser("fcb-month")
    p.add_argument("month")

    p = sub.add_parser("mae-month")
    p.add_argument("month")

    sub.add_parser("fcb-root")
    sub.add_parser("mae-root")

    args = parser.parse_args(argv)
    if args.cmd == "complete-volume":
        complete_volume(args.volume)
    elif args.cmd == "tod-volume":
        tod_volume(args.volume)
    elif args.cmd == "sermon-volumes":
        sermon_volumes(args.start, args.end)
    elif args.cmd == "fcb-month":
        month_corpus("chspurgeon-fcb", args.month, title_prefix="Faith's Checkbook", tags=FCB_TAGS)
    elif args.cmd == "mae-month":
        month_corpus("chspurgeon-mae", args.month, title_prefix="Morning and Evening", tags=MAE_TAGS)
    elif args.cmd == "fcb-root":
        fcb_root()
    elif args.cmd == "mae-root":
        mae_root()
    else:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
