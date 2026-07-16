#!/usr/bin/env python3
"""Dense search over sources_e5 (multilingual-e5-small).

Always filters vault_id. Optional corpus / book filters.

  .qmd/bin/qdrant-sources-search "how to pray without hypocrisy"
  .qmd/bin/qdrant-sources-search "oración hipocresía" --corpus mhenry-concise --json
  .qmd/bin/qdrant-sources-search "creation of light" --book-key 1 --min-score 0.8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.http import models as qm  # noqa: E402

from e5_embed import E5Encoder  # noqa: E402
from qdrant_common import (  # noqa: E402
    E5_MODEL_ID,
    SOURCES_COLLECTION,
    VAULT_ID,
    make_client,
)


def build_filter(
    *,
    corpus: str = "",
    book_key: int = 0,
    language: str = "",
    content_kind: str = "",
) -> qm.Filter:
    must: list[qm.Condition] = [
        qm.FieldCondition(key="vault_id", match=qm.MatchValue(value=VAULT_ID))
    ]
    if corpus:
        must.append(
            qm.FieldCondition(
                key="source_corpus", match=qm.MatchValue(value=corpus)
            )
        )
    if book_key:
        must.append(
            qm.FieldCondition(
                key="bible_book_key", match=qm.MatchValue(value=book_key)
            )
        )
    if language:
        must.append(
            qm.FieldCondition(
                key="language", match=qm.MatchValue(value=language)
            )
        )
    if content_kind:
        must.append(
            qm.FieldCondition(
                key="content_kind", match=qm.MatchValue(value=content_kind)
            )
        )
    return qm.Filter(must=must)


def search_sources(
    query: str,
    *,
    limit: int = 8,
    corpus: str = "",
    book_key: int = 0,
    language: str = "",
    content_kind: str = "",
    min_score: float = 0.0,
    preview_chars: int = 280,
    encoder: E5Encoder | None = None,
) -> list[dict[str, Any]]:
    enc = encoder or E5Encoder()
    qvec = enc.encode_one(query, kind="query")
    client = make_client()
    response = client.query_points(
        collection_name=SOURCES_COLLECTION,
        query=qvec,
        query_filter=build_filter(
            corpus=corpus,
            book_key=book_key,
            language=language,
            content_kind=content_kind,
        ),
        limit=limit,
        with_payload=True,
        score_threshold=min_score if min_score > 0 else None,
    )
    rows: list[dict[str, Any]] = []
    for h in response.points:
        p = h.payload or {}
        path = p.get("vault_rel_path") or ""
        text = p.get("text") or ""
        rows.append(
            {
                "channel": "sources_e5",
                "score": h.score,
                "vault_id": p.get("vault_id") or VAULT_ID,
                "vault_rel_path": path,
                "wikilink": f"[[{path}]]" if path else "",
                "chunk_index": p.get("chunk_index"),
                "chunk_count": p.get("chunk_count"),
                "section_heading": p.get("section_heading"),
                "title": p.get("title"),
                "source_corpus": p.get("source_corpus"),
                "content_kind": p.get("content_kind"),
                "bible_book_key": p.get("bible_book_key"),
                "bible_book_name": p.get("bible_book_name"),
                "bible_reference": p.get("bible_reference"),
                "language": p.get("language"),
                "embed_model": p.get("embed_model") or E5_MODEL_ID,
                "text_preview": text[:preview_chars],
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language query")
    parser.add_argument("--limit", "-n", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--corpus",
        default="",
        help="Optional source_corpus filter (e.g. mhenry-concise)",
    )
    parser.add_argument(
        "--book-key",
        type=int,
        default=0,
        help="Optional bible_book_key filter",
    )
    parser.add_argument("--language", default="", help="Optional language filter")
    parser.add_argument(
        "--content-kind",
        default="",
        help="Optional content_kind filter (commentary, sermon, …)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Drop hits below this cosine score (0 = no floor)",
    )
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=280,
        help="Chars of text_preview (default 280)",
    )
    args = parser.parse_args(argv)

    query = args.query.strip()
    if not query:
        print("Empty query.", file=sys.stderr)
        return 2

    try:
        rows = search_sources(
            query,
            limit=args.limit,
            corpus=args.corpus,
            book_key=args.book_key,
            language=args.language,
            content_kind=args.content_kind,
            min_score=args.min_score,
            preview_chars=args.preview_chars,
        )
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"sources search failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "query": query,
                    "vault_id": VAULT_ID,
                    "collection": SOURCES_COLLECTION,
                    "filters": {
                        "source_corpus": args.corpus or None,
                        "bible_book_key": args.book_key or None,
                        "language": args.language or None,
                        "content_kind": args.content_kind or None,
                        "min_score": args.min_score or None,
                    },
                    "count": len(rows),
                    "hits": rows,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        filt = []
        if args.corpus:
            filt.append(f"corpus={args.corpus}")
        if args.book_key:
            filt.append(f"book_key={args.book_key}")
        if args.language:
            filt.append(f"lang={args.language}")
        extra = (" · " + " · ".join(filt)) if filt else ""
        print(
            f"sources_e5 · vault_id={VAULT_ID} · query={query!r} · n={len(rows)}{extra}"
        )
        if not rows:
            print("  (no hits — run qdrant-sources-upsert first?)")
        for i, r in enumerate(rows, 1):
            print(
                f"  {i}. {r['score']:.4f}  {r['vault_rel_path']}"
                f"#{r['chunk_index']}\n"
                f"      {r['section_heading']!r}  book={r.get('bible_book_name')}\n"
                f"      {r['wikilink']}\n"
                f"      {r['text_preview']!r}…"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
