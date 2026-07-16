#!/usr/bin/env python3
"""Upsert source commentary chunks into Qdrant sources_e5 (dense E5).

Pilot corpus: mhenry-concise under sources/commentaries_english/.

  .qmd/bin/qdrant-sources-upsert
  .qmd/bin/qdrant-sources-upsert --corpus mhenry-concise --limit-files 20
  .qmd/bin/qdrant-sources-upsert --dry-run

Embeddings: local multilingual-e5-small (ONNX) with passage: prefix.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.http import models as qm  # noqa: E402

from e5_embed import E5Encoder  # noqa: E402
from qdrant_chunk import chunk_markdown  # noqa: E402
from qdrant_common import (  # noqa: E402
    E5_DIM,
    E5_MODEL_ID,
    SOURCES_COLLECTION,
    VAULT_ID,
    git_commit,
    make_client,
    parse_frontmatter,
    point_id,
    vault_root,
)

CORPUS_ROOTS = {
    "mhenry-concise": Path("sources/commentaries_english/mhenry-concise"),
    "mhenry-complete": Path("sources/commentaries_english/mhenry-complete"),
    "chspurgeon-fcb": Path("sources/commentaries_english/chspurgeon-fcb"),
    "chspurgeon-mae": Path("sources/commentaries_english/chspurgeon-mae"),
    "chspurgeon-tod": Path("sources/commentaries_english/chspurgeon-tod"),
    "chspurgeon-sermons": Path("sources/commentaries_english/chspurgeon-sermons"),
    "personal-notes": Path("sources/personal-notes"),
}


def iter_source_files(root: Path, corpus: str) -> list[Path]:
    rel = CORPUS_ROOTS.get(corpus)
    if rel is None:
        raise SystemExit(
            f"Unknown corpus {corpus!r}. Choose from: {', '.join(sorted(CORPUS_ROOTS))}"
        )
    base = root / rel
    if not base.is_dir():
        raise SystemExit(f"Corpus directory missing: {base}")
    paths = sorted(
        p
        for p in base.rglob("*.md")
        if p.name != "index.md" and p.is_file()
    )
    return paths


def content_kind_for(corpus: str) -> str:
    if corpus == "personal-notes":
        return "personal-note"
    if "sermon" in corpus:
        return "sermon"
    if corpus.endswith("-fcb") or corpus.endswith("-mae"):
        return "devotional"
    return "commentary"


def build_chunks_for_file(
    root: Path,
    path: Path,
    *,
    corpus: str,
    commit: str | None,
    encoder_fingerprint: str,
    max_chars: int,
) -> list[dict]:
    rel = path.relative_to(root).as_posix()
    raw = path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_frontmatter(raw)
    title = str(meta.get("title") or path.stem)
    # Short title for prefix: prefer book + chapter from path
    book = path.parent.name.replace("-", " ").title()
    chapter = path.stem.replace("chapter-", "ch. ")
    short_title = f"{book} {chapter}".strip()

    chunks = chunk_markdown(body, title=short_title, max_chars=max_chars)
    doc_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    kind = content_kind_for(corpus)
    out: list[dict] = []
    n = len(chunks)
    for ch in chunks:
        content_hash = hashlib.sha256(ch.text.encode("utf-8")).hexdigest()
        pid = point_id(VAULT_ID, rel, ch.index)
        payload = {
            "vault_id": VAULT_ID,
            "vault_rel_path": rel,
            "layer": "sources" if corpus != "personal-notes" else "personal-notes",
            "source_corpus": corpus,
            "content_kind": kind,
            "title": title,
            "section_heading": ch.heading,
            "text": ch.text[:6000],
            "chunk_index": ch.index,
            "chunk_count": n,
            "doc_hash": doc_hash,
            "content_hash": content_hash,
            "embed_model": E5_MODEL_ID,
            "embed_dim": E5_DIM,
            "embed_fingerprint": encoder_fingerprint,
            "language": "en",
            "git_commit": commit,
        }
        if meta.get("bible_book_key") is not None:
            try:
                payload["bible_book_key"] = int(meta["bible_book_key"])
            except (TypeError, ValueError):
                pass
        if meta.get("bible_book_name"):
            payload["bible_book_name"] = str(meta["bible_book_name"])
        if meta.get("bible_reference"):
            payload["bible_reference"] = str(meta["bible_reference"])
        tags = meta.get("tags")
        if isinstance(tags, list):
            payload["tags"] = tags
        out.append({"id": pid, "text": ch.text, "payload": payload})
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus",
        default="mhenry-concise",
        help="Source corpus key (default: mhenry-concise)",
    )
    parser.add_argument(
        "--limit-files",
        type=int,
        default=0,
        help="Process only first N files (0 = all)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="E5 encode batch size (default 8)",
    )
    parser.add_argument(
        "--upsert-batch",
        type=int,
        default=32,
        help="Qdrant upsert batch size (default 32)",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=1400,
        help="Max body chars per chunk piece (default 1400)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chunk and report counts without embedding/upsert",
    )
    args = parser.parse_args(argv)

    root = vault_root()
    paths = iter_source_files(root, args.corpus)
    if args.limit_files and args.limit_files > 0:
        paths = paths[: args.limit_files]
    if not paths:
        print("No source files matched.", file=sys.stderr)
        return 1

    commit = git_commit(root)
    print(
        f"Corpus={args.corpus} files={len(paths)} "
        f"collection={SOURCES_COLLECTION} vault_id={VAULT_ID}"
    )

    # First pass: build all chunk records (memory OK for concise pilot ~few MB text)
    all_records: list[dict] = []
    for path in paths:
        # fingerprint filled after encoder load for dry-run use placeholder
        recs = build_chunks_for_file(
            root,
            path,
            corpus=args.corpus,
            commit=commit,
            encoder_fingerprint="pending",
            max_chars=args.max_chars,
        )
        all_records.extend(recs)

    print(f"Chunks prepared: {len(all_records)}")
    if args.dry_run:
        sample = all_records[:3]
        for r in sample:
            print(
                f"  dry-run {r['payload']['vault_rel_path']}#"
                f"{r['payload']['chunk_index']} chars={len(r['text'])}"
            )
        return 0

    print("Loading E5 encoder …")
    t0 = time.time()
    encoder = E5Encoder()
    load_s = time.time() - t0
    print(f"  ready in {load_s:.1f}s  fingerprint={encoder.fingerprint}")

    for r in all_records:
        r["payload"]["embed_fingerprint"] = encoder.fingerprint

    client = make_client()
    upserted = 0
    t_embed = 0.0
    t_up = 0.0
    batch = max(1, args.batch_size)
    up_batch = max(1, args.upsert_batch)

    # Process in encode batches, accumulate points, flush upsert batches
    pending_points: list[qm.PointStruct] = []

    def flush() -> None:
        nonlocal upserted, t_up, pending_points
        if not pending_points:
            return
        t1 = time.time()
        client.upsert(collection_name=SOURCES_COLLECTION, points=pending_points)
        t_up += time.time() - t1
        upserted += len(pending_points)
        print(
            f"  upserted {upserted}/{len(all_records)} "
            f"(embed {t_embed:.0f}s upsert {t_up:.0f}s)"
        )
        pending_points = []

    for i in range(0, len(all_records), batch):
        chunk_recs = all_records[i : i + batch]
        texts = [r["text"] for r in chunk_recs]
        t1 = time.time()
        vectors = encoder.encode(texts, kind="passage", batch_size=batch)
        t_embed += time.time() - t1
        for rec, vec in zip(chunk_recs, vectors, strict=True):
            pending_points.append(
                qm.PointStruct(
                    id=rec["id"],
                    vector=vec.tolist(),
                    payload=rec["payload"],
                )
            )
        if len(pending_points) >= up_batch:
            flush()

    flush()

    info = client.get_collection(SOURCES_COLLECTION)
    print(
        f"Done. {SOURCES_COLLECTION} points_count={info.points_count} "
        f"status={info.status} embed_s={t_embed:.1f} upsert_s={t_up:.1f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
