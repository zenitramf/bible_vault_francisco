#!/usr/bin/env python3
"""Upsert wiki pages into Qdrant wiki_bm25 (sparse BM25 via Cloud Inference).

Embedding runs on Qdrant Cloud (model Qdrant/bm25), not on hermes.
One point per wiki markdown page.

  .qmd/bin/qdrant-wiki-upsert
  .qmd/bin/qdrant-wiki-upsert --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.http import models as qm  # noqa: E402

from qdrant_common import (  # noqa: E402
    BM25_FINGERPRINT,
    BM25_MODEL,
    BM25_VECTOR_NAME,
    VAULT_ID,
    WIKI_COLLECTION,
    git_commit,
    iter_wiki_markdown,
    make_client,
    parse_frontmatter,
    point_id,
    sparse_document,
    strip_wikilinks,
    vault_root,
    wiki_page_type,
)


def build_document_text(meta: dict, body: str, title_fallback: str) -> str:
    title = str(meta.get("title") or title_fallback)
    description = str(meta.get("description") or "")
    tags = meta.get("tags") or []
    if isinstance(tags, list):
        tag_s = " ".join(str(t) for t in tags)
    else:
        tag_s = str(tags)
    cleaned = strip_wikilinks(body)
    parts = [title, description, tag_s, cleaned]
    return "\n".join(p for p in parts if p and str(p).strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0, help="Max pages (0=all)")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Cloud Inference upsert batch size (default 16)",
    )
    args = parser.parse_args(argv)

    root = vault_root()
    paths = iter_wiki_markdown(root)
    if args.limit and args.limit > 0:
        paths = paths[: args.limit]
    if not paths:
        print("No wiki markdown pages found.", file=sys.stderr)
        return 1

    commit = git_commit(root)
    records: list[dict] = []

    for path in paths:
        rel = path.relative_to(root).as_posix()
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        text = build_document_text(meta, body, path.stem)
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        doc_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        pid = point_id(VAULT_ID, rel, 0)
        payload = {
            "vault_id": VAULT_ID,
            "vault_rel_path": rel,
            "layer": "wiki",
            "page_type": wiki_page_type(rel),
            "title": str(meta.get("title") or path.stem),
            "status": str(meta.get("status") or ""),
            "tags": meta.get("tags") if isinstance(meta.get("tags"), list) else [],
            "type": str(meta.get("type") or ""),
            "description": str(meta.get("description") or ""),
            "text": text[:8000],
            "content_hash": content_hash,
            "doc_hash": doc_hash,
            "chunk_index": 0,
            "chunk_count": 1,
            "embed_model": BM25_MODEL,
            "embed_fingerprint": BM25_FINGERPRINT,
            "embed_backend": "qdrant-cloud-inference",
            "git_commit": commit,
        }
        if meta.get("bible_book_key") is not None:
            try:
                payload["bible_book_key"] = int(meta["bible_book_key"])
            except (TypeError, ValueError):
                pass
        if meta.get("bible_reference"):
            payload["bible_reference"] = str(meta["bible_reference"])
        records.append({"id": pid, "text": text, "payload": payload})

    print(
        f"Wiki pages: {len(records)} (vault_id={VAULT_ID}) "
        f"embed={BM25_MODEL} via Cloud Inference"
    )
    if args.dry_run:
        for r in records[:5]:
            print(f"  dry-run {r['payload']['vault_rel_path']}")
        if len(records) > 5:
            print(f"  ... +{len(records) - 5} more")
        return 0

    client = make_client()
    batch = max(1, args.batch_size)
    for i in range(0, len(records), batch):
        chunk = records[i : i + batch]
        points = [
            qm.PointStruct(
                id=r["id"],
                payload=r["payload"],
                vector={BM25_VECTOR_NAME: sparse_document(r["text"])},
            )
            for r in chunk
        ]
        client.upsert(collection_name=WIKI_COLLECTION, points=points)
        print(f"  upserted {min(i + batch, len(records))}/{len(records)}")

    info = client.get_collection(WIKI_COLLECTION)
    print(
        f"Done. {WIKI_COLLECTION} points_count={info.points_count} "
        f"status={info.status}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
