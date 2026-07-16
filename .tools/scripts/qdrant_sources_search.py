#!/usr/bin/env python3
"""Dense search over sources_e5 (multilingual-e5-small).

Always filters vault_id. Optional --corpus filter (e.g. mhenry-concise).

  .qmd/bin/qdrant-sources-search "how to pray without hypocrisy"
  .qmd/bin/qdrant-sources-search "oración hipocresía" --corpus mhenry-concise --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.http import models as qm  # noqa: E402

from e5_embed import E5Encoder  # noqa: E402
from qdrant_common import (  # noqa: E402
    SOURCES_COLLECTION,
    VAULT_ID,
    make_client,
)


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
    args = parser.parse_args(argv)

    query = args.query.strip()
    if not query:
        print("Empty query.", file=sys.stderr)
        return 2

    encoder = E5Encoder()
    qvec = encoder.encode_one(query, kind="query")

    must = [
        qm.FieldCondition(
            key="vault_id", match=qm.MatchValue(value=VAULT_ID)
        )
    ]
    if args.corpus:
        must.append(
            qm.FieldCondition(
                key="source_corpus",
                match=qm.MatchValue(value=args.corpus),
            )
        )
    if args.book_key:
        must.append(
            qm.FieldCondition(
                key="bible_book_key",
                match=qm.MatchValue(value=args.book_key),
            )
        )

    client = make_client()
    response = client.query_points(
        collection_name=SOURCES_COLLECTION,
        query=qvec,
        query_filter=qm.Filter(must=must),
        limit=args.limit,
        with_payload=True,
    )

    rows = []
    for h in response.points:
        p = h.payload or {}
        rows.append(
            {
                "score": h.score,
                "vault_rel_path": p.get("vault_rel_path"),
                "chunk_index": p.get("chunk_index"),
                "section_heading": p.get("section_heading"),
                "title": p.get("title"),
                "source_corpus": p.get("source_corpus"),
                "bible_book_key": p.get("bible_book_key"),
                "bible_book_name": p.get("bible_book_name"),
                "vault_id": p.get("vault_id"),
                "text_preview": (p.get("text") or "")[:240],
            }
        )

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        print(
            f"sources_e5 · vault_id={VAULT_ID} · query={query!r} · n={len(rows)}"
            + (f" · corpus={args.corpus}" if args.corpus else "")
        )
        if not rows:
            print("  (no hits — run qdrant-sources-upsert first?)")
        for i, r in enumerate(rows, 1):
            print(
                f"  {i}. {r['score']:.4f}  {r['vault_rel_path']}"
                f"#{r['chunk_index']}\n"
                f"      {r['section_heading']!r}  book={r.get('bible_book_name')}\n"
                f"      {r['text_preview']!r}…"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
