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
from typing import Any

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

_sparse_model: SparseTextEmbedding | None = None


def get_bm25_model() -> SparseTextEmbedding:
    global _sparse_model
    if _sparse_model is None:
        _sparse_model = SparseTextEmbedding(model_name=BM25_MODEL)
    return _sparse_model


def search_wiki(
    query: str,
    *,
    limit: int = 8,
    page_type: str = "",
    min_score: float = 0.0,
    model: SparseTextEmbedding | None = None,
) -> list[dict[str, Any]]:
    m = model or get_bm25_model()
    emb = list(m.embed([query]))[0]
    must: list[qm.Condition] = [
        qm.FieldCondition(key="vault_id", match=qm.MatchValue(value=VAULT_ID))
    ]
    if page_type:
        must.append(
            qm.FieldCondition(
                key="page_type", match=qm.MatchValue(value=page_type)
            )
        )
    client = make_client()
    response = client.query_points(
        collection_name=WIKI_COLLECTION,
        query=qm.SparseVector(
            indices=emb.indices.tolist(),
            values=emb.values.tolist(),
        ),
        using=BM25_VECTOR_NAME,
        query_filter=qm.Filter(must=must),
        limit=limit,
        with_payload=True,
        score_threshold=min_score if min_score > 0 else None,
    )
    rows: list[dict[str, Any]] = []
    for h in response.points:
        payload = h.payload or {}
        path = payload.get("vault_rel_path") or ""
        rows.append(
            {
                "channel": "wiki_bm25",
                "score": h.score,
                "vault_id": payload.get("vault_id") or VAULT_ID,
                "vault_rel_path": path,
                "wikilink": f"[[{path}]]" if path else "",
                "title": payload.get("title"),
                "page_type": payload.get("page_type"),
                "status": payload.get("status"),
                "tags": payload.get("tags") or [],
                "bible_reference": payload.get("bible_reference"),
                "text_preview": (payload.get("text") or "")[:280],
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Free-text query")
    parser.add_argument(
        "--limit", "-n", type=int, default=8, help="Max hits (default 8)"
    )
    parser.add_argument(
        "--json", action="store_true", help="JSON object on stdout"
    )
    parser.add_argument(
        "--page-type",
        default="",
        help="Optional page_type filter (concept, passage, …)",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=0.0,
        help="Drop hits below this score (0 = no floor)",
    )
    args = parser.parse_args(argv)

    query = args.query.strip()
    if not query:
        print("Empty query.", file=sys.stderr)
        return 2

    try:
        rows = search_wiki(
            query,
            limit=args.limit,
            page_type=args.page_type,
            min_score=args.min_score,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"wiki search failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(
            json.dumps(
                {
                    "query": query,
                    "vault_id": VAULT_ID,
                    "collection": WIKI_COLLECTION,
                    "filters": {
                        "page_type": args.page_type or None,
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
        print(
            f"wiki_bm25 · vault_id={VAULT_ID} · query={query!r} · n={len(rows)}"
        )
        if not rows:
            print("  (no hits — run qdrant_wiki_upsert.py first?)")
        for i, r in enumerate(rows, 1):
            tags = ",".join(r["tags"]) if r["tags"] else "-"
            print(
                f"  {i}. {r['score']:.4f}  {r['vault_rel_path']}\n"
                f"      title={r['title']!r}  type={r['page_type']}  tags={tags}\n"
                f"      {r['wikilink']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
