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
MANIFEST = SCHEMA / "source-manifest.jsonl"
LOG = WIKI / "log.md"

REQUIRED_WIKI_FIELDS = ("type", "title", "description", "tags")
ALLOWED_STATUS = {"seed", "developing", "reviewed"}
BIBLE_REFERENCE = re.compile(r'^bible_reference:\s*"?[1-3]?[a-z]+ \d+:\d+(?:-\d+)?"?\s*$')
WIKILINK = re.compile(r"!?\[\[([^\]]+)\]\]")
MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
YAML_LIST_ITEM = re.compile(r"^\s*-\s+[\"']?(.+?)[\"']?\s*$")
TAG_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")

WIKI_DIR_META = {
    "concepts": ("Concepts", "Source-backed syntheses of biblical doctrines, themes, and practices."),
    "people": ("People", "Syntheses about biblical people and relevant historical figures."),
    "passages": ("Passages", "Maintained studies organized around biblical passages."),
    "questions": ("Questions", "Durable investigations, comparisons, and answered questions."),
    "source-notes": ("Source notes", "Summaries and evaluations of intentionally ingested sources."),
}

SKIP_DIR_PARTS = {".git", ".qmd", ".obsidian", "__pycache__", "node_modules"}


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
    if path.name in {"index.md", "catalog.jsonl"}:
        return False
    if path.name == "log.md":
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


def extract_wikilink_targets(text: str) -> list[str]:
    targets: list[str] = []
    for raw in WIKILINK.findall(text):
        target = raw.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            if not target.endswith(".md"):
                target = f"{target}.md"
            targets.append(unquote(target))
    return targets


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
                if not target.endswith(".md"):
                    target = f"{target}.md"
                links.append(unquote(target))
    return links


def resolve_source_paths_from_wiki(path: Path, text: str, meta: dict[str, Any]) -> list[str]:
    found: list[str] = []
    source_path = meta.get("source_path")
    if isinstance(source_path, str) and source_path.strip():
        sp = source_path.strip().strip("\"'")
        if not sp.endswith(".md"):
            sp = f"{sp}.md"
        found.append(sp)

    for target in sources_section_links(text):
        if target.startswith("sources/"):
            found.append(target)

    for target in extract_wikilink_targets(text):
        if target.startswith("sources/"):
            found.append(target)

    # de-dupe preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for item in found:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


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
    print(f"  qmd lint: {'present' if (ROOT / '.qmd/bin/lint-wiki').is_file() else 'missing'}")

    if CATALOG.is_file():
        print(f"  catalog rows: {len(load_jsonl(CATALOG))}")
    if MANIFEST.is_file():
        rows = load_jsonl(MANIFEST)
        covered = sum(1 for r in rows if r.get("covered_by"))
        print(f"  manifest rows: {len(rows)} (covered: {covered})")

    for warning in warnings:
        print(f"WARN {warning}")
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} doctor error(s)")
        return 1
    print("Doctor passed")
    return 0


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
    return {
        "path": rel(path),
        "title": str(meta.get("title") or path.stem),
        "type": str(meta.get("type") or ""),
        "tags": tags,
        "status": str(meta.get("status") or ""),
        "updated": str(meta.get("updated") or ""),
        "source_count": source_count,
        "description": str(meta.get("description") or ""),
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
            # URL-encode spaces for markdown relative links
            href = path.name.replace(" ", "%20")
            entries.append((page_title.lower(), f"* [{page_title}]({href}) - {description}".rstrip(" -"), page_title))
        entries.sort(key=lambda item: item[0])
        lines = [f"# {title}", "", "# Contents", ""]
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
        "# Contents",
        "",
    ]
    for dirname, (title, blurb) in WIKI_DIR_META.items():
        wiki_index_lines.append(f"* [{title}]({dirname}/) - {blurb}")
    wiki_index_lines.append("* [Wiki log](log.md) - Chronological record of ingests, filed queries, lint passes, and maintenance.")
    wiki_index_lines.append("")
    (WIKI / "index.md").write_text("\n".join(wiki_index_lines), encoding="utf-8")


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
    print(f"Wrote {rel(CATALOG)} ({len(rows)} rows)")
    print("Regenerated wiki index.md files")
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
    # also include log.md? no
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
        # If first run, compute coverage anyway as helpful default? No — honor flags.
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


def cmd_source_coverage(_: argparse.Namespace) -> int:
    rows = load_jsonl(MANIFEST)
    if not rows:
        # fall back to live scan
        rows = build_manifest_rows(accept_covered=True)
    covered = [r for r in rows if r.get("covered_by")]
    open_rows = [r for r in rows if not r.get("covered_by")]
    print(f"Total sources: {len(rows)}")
    print(f"Covered: {len(covered)}")
    print(f"Uncovered: {len(open_rows)}")
    print("Covered detail:")
    for row in covered:
        print(f"  {row['path']}")
        for wp in row.get("covered_by") or []:
            print(f"    <- {wp}")
    return 0


def cmd_search_catalog(args: argparse.Namespace) -> int:
    query = (args.query or "").strip().lower()
    if not query:
        print("ERROR --query is required")
        return 1
    if not CATALOG.is_file():
        print(f"ERROR missing catalog: {rel(CATALOG)} (run build)")
        return 1
    terms = [t for t in re.split(r"\s+", query) if t]
    hits: list[tuple[int, dict[str, Any]]] = []
    for row in load_jsonl(CATALOG):
        blob = " ".join(
            [
                str(row.get("title", "")),
                str(row.get("description", "")),
                str(row.get("type", "")),
                " ".join(row.get("tags") or []),
                str(row.get("path", "")),
            ]
        ).lower()
        score = sum(1 for t in terms if t in blob)
        if score:
            hits.append((score, row))
    hits.sort(key=lambda item: (-item[0], item[1].get("path", "")))
    limit = args.limit or 10
    print(f"{len(hits)} hit(s) for {query!r} (showing up to {limit})")
    for score, row in hits[:limit]:
        print(f"  [{score}] {row.get('path')} — {row.get('title')} ({row.get('type')})")
        if row.get("description"):
            print(f"       {row['description']}")
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
    sub.add_parser("build", help="Generate catalog and wiki indexes")
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
    sub.add_parser("source-coverage", help="Show wiki coverage of sources")

    search = sub.add_parser("search-catalog", help="Search wiki/catalog.jsonl")
    search.add_argument("--query", required=True, help="Search text")
    search.add_argument("--limit", type=int, default=10, help="Max hits")

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
        "log": cmd_log,
    }
    return dispatch[command](args)


if __name__ == "__main__":
    sys.exit(main())
