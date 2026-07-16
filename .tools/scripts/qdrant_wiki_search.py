#!/usr/bin/env python3
"""Search wiki_bm25 (sparse BM25) on Qdrant Cloud.

Always filters by vault_id=bible_vault_francisco.

  python3 .tools/scripts/qdrant_wiki_search.py "prayer and the Father"
  python3 .tools/scripts/qdrant_wiki_search.py "intercession" --limit 5 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastembed import SparseTextEmbedding  # noqa: E402
from qdrant_client.http import models as qm  # noqa: E402

from qdrant_common import (  # noqa: E402
    BM25_MODEL,
    BM25_VECTOR_NAME,
    VAULT_ID,
    WIKI_COLLECTION,
    make_client,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Free-text query")
    parser.add_argument(
        "--limit", "-n", type=int, default=8, help="Max hits (default 8)"
    )
    parser.add_argument(
        "--json", action="store_true", help="JSON array on stdout"
    )
    parser.add_argument(
        "--page-type",
        default="",
        help="Optional page_type filter (concept, passage, …)",
    )
    args = parser.parse_args(argv)

    query = args.query.strip()
    if not query:
        print("Empty query.", file=sys.stderr)
        return 2

    model = SparseTextEmbedding(model_name=BM25_MODEL)
    emb = list(model.embed([query]))[0]

    must = [
        qm.FieldCondition(
            key="vault_id", match=qm.MatchValue(value=VAULT_ID)
        )
    ]
    if args.page_type:
        must.append(
            qm.FieldCondition(
                key="page_type",
                match=qm.MatchValue(value=args.page_type),
            )
        )
    query_filter = qm.Filter(must=must)

    client = make_client()
    # qdrant-client 1.12+ query_points API
    response = client.query_points(
        collection_name=WIKI_COLLECTION,
        query=qm.SparseVector(
            indices=emb.indices.tolist(),
            values=emb.values.tolist(),
        ),
        using=BM25_VECTOR_NAME,
        query_filter=query_filter,
        limit=args.limit,
        with_payload=True,
    )
    hits = response.points

    rows = []
    for h in hits:
        payload = h.payload or {}
        rows.append(
            {
                "score": h.score,
                "vault_rel_path": payload.get("vault_rel_path"),
                "title": payload.get("title"),
                "page_type": payload.get("page_type"),
                "status": payload.get("status"),
                "tags": payload.get("tags") or [],
                "bible_reference": payload.get("bible_reference"),
                "vault_id": payload.get("vault_id"),
            }
        )

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    else:
        print(f"wiki_bm25 · vault_id={VAULT_ID} · query={query!r} · n={len(rows)}")
        if not rows:
            print("  (no hits — run qdrant_wiki_upsert.py first?)")
        for i, r in enumerate(rows, 1):
            tags = ",".join(r["tags"]) if r["tags"] else "-"
            print(
                f"  {i}. {r['score']:.4f}  {r['vault_rel_path']}\n"
                f"      title={r['title']!r}  type={r['page_type']}  tags={tags}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
