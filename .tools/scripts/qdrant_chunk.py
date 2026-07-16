"""Markdown chunking for Qdrant source upserts.

Prefer ## sections (Matthew Henry verse blocks). Oversized sections are
split on paragraph boundaries under max_chars, keeping a heading prefix.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

HEADING_SPLIT = re.compile(r"(?m)^(#{1,3})[ \t]+(.+?)\s*$")
SKIP_SECTION_TITLES = {
    "chapter outline",
    "outline",
    "contents",
}


@dataclass
class Chunk:
    heading: str
    text: str
    index: int


def _split_long(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []
    paras = re.split(r"\n\s*\n", text)
    parts: list[str] = []
    buf: list[str] = []
    size = 0
    for para in paras:
        p = para.strip()
        if not p:
            continue
        extra = len(p) + (2 if buf else 0)
        if buf and size + extra > max_chars:
            parts.append("\n\n".join(buf))
            buf = [p]
            size = len(p)
        else:
            buf.append(p)
            size += extra
    if buf:
        parts.append("\n\n".join(buf))
    # Hard-split any remaining oversize paragraph
    final: list[str] = []
    for part in parts:
        if len(part) <= max_chars:
            final.append(part)
            continue
        for i in range(0, len(part), max_chars):
            final.append(part[i : i + max_chars])
    return final


def chunk_markdown(
    body: str,
    *,
    title: str = "",
    max_chars: int = 1400,
    min_chars: int = 40,
) -> list[Chunk]:
    """Chunk markdown body into retrieval units.

    max_chars is for the *body* before title prefix; leave room for E5 512 tokens.
    """
    body = body.strip()
    if not body:
        return []

    matches = list(HEADING_SPLIT.finditer(body))
    sections: list[tuple[str, str]] = []

    if not matches:
        sections.append((title or "", body))
    else:
        # Preamble before first heading
        pre = body[: matches[0].start()].strip()
        if pre and len(pre) >= min_chars:
            sections.append((title or "", pre))
        for i, m in enumerate(matches):
            heading = m.group(2).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            content = body[start:end].strip()
            if heading.lower() in SKIP_SECTION_TITLES:
                continue
            if not content or len(content) < min_chars:
                continue
            sections.append((heading, content))

    chunks: list[Chunk] = []
    for heading, content in sections:
        pieces = _split_long(content, max_chars)
        for piece in pieces:
            if len(piece) < min_chars:
                continue
            # Prefix for retrieval context (not stored twice in payload text beyond this)
            if heading and title and heading != title:
                prefixed = f"{title}\n## {heading}\n\n{piece}"
            elif heading:
                prefixed = f"## {heading}\n\n{piece}"
            elif title:
                prefixed = f"{title}\n\n{piece}"
            else:
                prefixed = piece
            chunks.append(Chunk(heading=heading, text=prefixed, index=len(chunks)))

    # Fallback: whole body if nothing survived filters
    if not chunks and body:
        for piece in _split_long(body, max_chars):
            text = f"{title}\n\n{piece}".strip() if title else piece
            chunks.append(Chunk(heading=title, text=text, index=len(chunks)))

    # Re-number
    for i, c in enumerate(chunks):
        c.index = i
    return chunks
