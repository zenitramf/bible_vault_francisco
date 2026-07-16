#!/usr/bin/env python3
"""Deterministic structural lint for the generated Bible Wiki layer."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WIKI = ROOT / "wiki"
SOURCES = ROOT / "sources"
REQUIRED_FIELDS = ("type", "title", "description", "tags")
BIBLE_REFERENCE = re.compile(r'^bible_reference:\s*"?[1-3]?[a-z]+ \d+:\d+(?:-\d+)?"?\s*$')
WIKILINK = re.compile(r"!?\[\[([^\]]+)\]\]")


def frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    return None if end < 0 else text[4:end]


def value_for(metadata: str, field: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.+)$", metadata)
    return match.group(1).strip() if match else None


def resolve_link(source: Path, raw_target: str, all_markdown: list[Path]) -> list[Path]:
    target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
    if not target:
        return [source]
    target_path = Path(target)
    if target_path.suffix != ".md":
        target_path = target_path.with_suffix(".md")
    if "/" in target:
        return [ROOT / target_path] if (ROOT / target_path).is_file() else []
    return [path for path in all_markdown if path.stem == target_path.stem]


def main() -> int:
    errors: list[str] = []
    all_markdown = [
        path
        for path in ROOT.rglob("*.md")
        if not any(part in {".git", ".obsidian", "__pycache__", "node_modules"} for part in path.parts)
    ]

    for tree in (WIKI, SOURCES):
        for directory in sorted({path.parent for path in tree.rglob("*.md")}):
            index = directory / "index.md"
            if not index.is_file():
                errors.append(f"missing index: {index.relative_to(ROOT)}")
                continue
            index_text = index.read_text(encoding="utf-8")
            if index_text.startswith("---\n"):
                errors.append(f"index has frontmatter: {index.relative_to(ROOT)}")
            if "# Contents" not in index_text:
                errors.append(f"index lacks # Contents: {index.relative_to(ROOT)}")

    for path in sorted(WIKI.rglob("*.md")):
        if path.name == "index.md":
            continue
        text = path.read_text(encoding="utf-8")
        metadata = frontmatter(text)
        relative = path.relative_to(ROOT)
        if metadata is None:
            errors.append(f"missing frontmatter: {relative}")
            continue
        for field in REQUIRED_FIELDS:
            value = value_for(metadata, field)
            if value is None or value in {"", "[]", "''", '""'}:
                errors.append(f"missing {field}: {relative}")
        reference_lines = [line for line in metadata.splitlines() if line.startswith("bible_reference:")]
        if reference_lines and not BIBLE_REFERENCE.match(reference_lines[0]):
            errors.append(f"invalid bible_reference: {relative}")

        in_claims = False
        for line in text.splitlines():
            if line == "## Core claims":
                in_claims = True
                continue
            if in_claims and line.startswith("## "):
                in_claims = False
            if in_claims and line.startswith("- ") and "[[" not in line:
                errors.append(f"uncited core claim: {relative}: {line}")

        for raw_target in WIKILINK.findall(text):
            matches = resolve_link(path, raw_target, all_markdown)
            if not matches:
                errors.append(f"broken wikilink in {relative}: [[{raw_target}]]")
            elif "/" not in raw_target and len(matches) > 1:
                errors.append(f"ambiguous wikilink in {relative}: [[{raw_target}]]")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} wiki lint error(s)")
        return 1

    print("Wiki lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
