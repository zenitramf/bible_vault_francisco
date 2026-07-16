#!/usr/bin/env python3
"""Search wiki_bm25 via Qdrant Cloud Inference (sparse BM25).

Always filters by vault_id. Query embedding runs on Qdrant, not hermes.

  .qmd/bin/qdrant-wiki-search "prayer and the Father"
  .qmd/bin/qdrant-wiki-search "intercession" --limit 5 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.http import models as qm  # noqa: E402

from qdrant_common import (  # noqa: E402
    BM25_MODEL,
    BM25_VECTOR_NAME,
    VAULT_ID,
    WIKI_COLLECTION,
    make_client,
    sparse_document,
)


def search_wiki(
    query: str,
    *,
    limit: int = 8,
    page_type: str = "",
    min_score: float = 0.0,
) -> list[dict[str, Any]]:
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
        query=sparse_document(query),
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
                "embed_model": payload.get("embed_model") or BM25_MODEL,
            }
        )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Free-text query")
    parser.add_argument("--limit", "-n", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--page-type", default="")
    parser.add_argument("--min-score", type=float, default=0.0)
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
                    "embed_backend": "qdrant-cloud-inference",
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
            f"wiki_bm25 · vault_id={VAULT_ID} · query={query!r} · n={len(rows)} "
            f"· embed=cloud:{BM25_MODEL}"
        )
        if not rows:
            print("  (no hits — run qdrant-wiki-upsert first?)")
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
