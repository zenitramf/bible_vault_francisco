#!/usr/bin/env python3
"""Upsert source chunks into Qdrant sources_e5 via Cloud Inference.

Dense embeddings: intfloat/multilingual-e5-small on Qdrant Cloud (not hermes).
Default corpus: mhenry-concise.

  .qmd/bin/qdrant-sources-upsert
  .qmd/bin/qdrant-sources-upsert --corpus mhenry-concise --limit-files 20
  .qmd/bin/qdrant-sources-upsert --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.http import models as qm  # noqa: E402

from qdrant_chunk import chunk_markdown  # noqa: E402
from qdrant_common import (  # noqa: E402
    E5_DIM,
    E5_FINGERPRINT,
    E5_MODEL_ID,
    SOURCES_COLLECTION,
    VAULT_ID,
    dense_document,
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
    return sorted(
        p for p in base.rglob("*.md") if p.name != "index.md" and p.is_file()
    )


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
    max_chars: int,
) -> list[dict]:
    rel = path.relative_to(root).as_posix()
    raw = path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_frontmatter(raw)
    title = str(meta.get("title") or path.stem)
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
            "embed_fingerprint": E5_FINGERPRINT,
            "embed_backend": "qdrant-cloud-inference",
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
    parser.add_argument("--corpus", default="mhenry-concise")
    parser.add_argument("--limit-files", type=int, default=0)
    parser.add_argument(
        "--upsert-batch",
        type=int,
        default=16,
        help="Points per Cloud Inference upsert (default 16)",
    )
    parser.add_argument("--max-chars", type=int, default=1400)
    parser.add_argument("--dry-run", action="store_true")
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
        f"collection={SOURCES_COLLECTION} vault_id={VAULT_ID}\n"
        f"Embed: {E5_MODEL_ID} via Qdrant Cloud Inference (no local ONNX)"
    )

    all_records: list[dict] = []
    for path in paths:
        all_records.extend(
            build_chunks_for_file(
                root,
                path,
                corpus=args.corpus,
                commit=commit,
                max_chars=args.max_chars,
            )
        )

    print(f"Chunks prepared: {len(all_records)}")
    if args.dry_run:
        for r in all_records[:3]:
            print(
                f"  dry-run {r['payload']['vault_rel_path']}#"
                f"{r['payload']['chunk_index']} chars={len(r['text'])}"
            )
        return 0

    client = make_client(timeout=300)
    batch = max(1, args.upsert_batch)
    upserted = 0
    t0 = time.time()
    errors = 0

    for i in range(0, len(all_records), batch):
        chunk = all_records[i : i + batch]
        points = [
            qm.PointStruct(
                id=r["id"],
                payload=r["payload"],
                vector=dense_document(r["text"]),
            )
            for r in chunk
        ]
        try:
            client.upsert(collection_name=SOURCES_COLLECTION, points=points)
            upserted += len(points)
        except Exception as exc:  # noqa: BLE001
            errors += 1
            print(f"  batch {i}-{i + len(chunk)} failed: {exc}", file=sys.stderr)
            # Retry one-by-one for the failed batch
            for r in chunk:
                try:
                    client.upsert(
                        collection_name=SOURCES_COLLECTION,
                        points=[
                            qm.PointStruct(
                                id=r["id"],
                                payload=r["payload"],
                                vector=dense_document(r["text"]),
                            )
                        ],
                    )
                    upserted += 1
                except Exception as exc2:  # noqa: BLE001
                    print(
                        f"  point fail {r['payload']['vault_rel_path']}#"
                        f"{r['payload']['chunk_index']}: {exc2}",
                        file=sys.stderr,
                    )
        elapsed = time.time() - t0
        print(
            f"  upserted {min(i + batch, len(all_records))}/{len(all_records)} "
            f"({elapsed:.0f}s, cloud inference)"
        )

    info = client.get_collection(SOURCES_COLLECTION)
    print(
        f"Done. {SOURCES_COLLECTION} points_count={info.points_count} "
        f"status={info.status} upserted={upserted} batch_errors={errors} "
        f"elapsed={time.time() - t0:.1f}s"
    )
    return 0 if upserted else 1


if __name__ == "__main__":
    raise SystemExit(main())
