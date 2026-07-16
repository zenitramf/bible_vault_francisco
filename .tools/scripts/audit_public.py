#!/usr/bin/env python3
"""Fail on secrets, private keys, and machine-local paths in committed vault text."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SKIP_DIR_PARTS = {
    ".git",
    ".qmd",
    ".obsidian",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
}

SKIP_SUFFIXES = {
    ".sqlite",
    ".sqlite-shm",
    ".sqlite-wal",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".gz",
    ".pyc",
}

# Patterns that should never appear in a public knowledge bundle.
PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
)
AWS_KEY = re.compile(r"AKIA[0-9A-Z]{16}")
GENERIC_SECRET_ASSIGN = re.compile(
    r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|password)\s*[:=]\s*['\"][^'\"]{12,}"
)
# Machine-local absolute home paths (not generic /home placeholders in docs about systems).
HOME_PATH = re.compile(r"(?m)(?<![\w-])(/home/(?!hermes\b)[A-Za-z0-9._-]+|/Users/[A-Za-z0-9._-]+)")
# Explicit hermes server path is this machine — flag outside tooling configs that already know ROOT.
# Allow project path itself; flag other user homes only (handled above).
SSH_PRIV = re.compile(r"(?i)BEGIN OPENSSH PRIVATE KEY")


def should_scan(path: Path) -> bool:
    if any(part in SKIP_DIR_PARTS for part in path.parts):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    if path.is_symlink():
        return False
    try:
        if path.stat().st_size > 2_000_000:
            return False
    except OSError:
        return False
    return path.is_file()


def main() -> int:
    errors: list[str] = []
    scanned = 0
    for path in sorted(ROOT.rglob("*")):
        if not should_scan(path):
            continue
        # Only text-ish extensions
        if path.suffix and path.suffix.lower() not in {
            ".md",
            ".py",
            ".sh",
            ".yml",
            ".yaml",
            ".json",
            ".jsonl",
            ".txt",
            ".toml",
            ".cfg",
            ".ini",
            "",
        }:
            # allow extensionless small scripts already covered; skip binaries
            if path.suffix:
                continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        rel = path.relative_to(ROOT).as_posix()
        for label, pattern in (
            ("private-key-block", PRIVATE_KEY),
            ("openssh-private-key", SSH_PRIV),
            ("aws-access-key-id", AWS_KEY),
            ("secret-assignment", GENERIC_SECRET_ASSIGN),
            ("machine-local-home-path", HOME_PATH),
        ):
            if pattern.search(text):
                # Avoid false positive on this audit script's own pattern strings
                if path.name in {"audit_public.py"} and label in {
                    "private-key-block",
                    "openssh-private-key",
                    "aws-access-key-id",
                    "secret-assignment",
                    "machine-local-home-path",
                }:
                    continue
                errors.append(f"{label}: {rel}")

    if errors:
        for error in errors:
            print(f"ERROR {error}")
        print(f"{len(errors)} public-audit error(s) ({scanned} files scanned)")
        return 1
    print(f"Public audit passed ({scanned} files scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
