"""Shared Qdrant Cloud helpers for the Bible Vault.

Auth env (first match wins for the API key):
  QCLOUD_BIBLE_CLUSTER_API_KEY, QDRANT_API_KEY

Optional:
  QDRANT_URL — REST base URL including port
"""

from __future__ import annotations

import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient

DEFAULT_URL = (
    "https://af215873-0bcb-46d3-8a94-829541781b37"
    ".us-west-1-0.aws.cloud.qdrant.io:6333"
)
VAULT_ID = "bible_vault_francisco"
WIKI_COLLECTION = "wiki_bm25"
SOURCES_COLLECTION = "sources_e5"
BM25_VECTOR_NAME = "bm25"
BM25_MODEL = "Qdrant/bm25"
E5_MODEL_ID = "intfloat/multilingual-e5-small"
E5_DIM = 384
# Embeddings run on Qdrant Cloud Inference (not on hermes).
EMBED_BACKEND = "qdrant-cloud-inference"
E5_FINGERPRINT = f"{E5_MODEL_ID}|{EMBED_BACKEND}|dim={E5_DIM}"
BM25_FINGERPRINT = f"{BM25_MODEL}|{EMBED_BACKEND}"

# Stable namespace for deterministic point IDs (not a secret).
POINT_NS = uuid.UUID("6b1b1e2a-0c4d-4f3a-9e5f-2a7d8c1b0e9f")

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def vault_root() -> Path:
    """Resolve vault root (worktree or main) from this file location."""
    # .tools/scripts/qdrant_common.py → repo root
    return Path(__file__).resolve().parents[2]


def api_key() -> str:
    key = os.environ.get("QCLOUD_BIBLE_CLUSTER_API_KEY") or os.environ.get(
        "QDRANT_API_KEY"
    )
    if not key:
        raise SystemExit(
            "Missing QCLOUD_BIBLE_CLUSTER_API_KEY (or QDRANT_API_KEY)."
        )
    return key


def qdrant_url() -> str:
    return os.environ.get("QDRANT_URL", DEFAULT_URL).rstrip("/")


def make_client(*, timeout: int | None = None) -> QdrantClient:
    """Qdrant Cloud client with Cloud Inference enabled.

    cloud_inference=True sends Document(...) embed requests to Qdrant
    instead of running models locally (FastEmbed/ONNX).
    """
    # Inference upserts/queries can be slower than raw vector ops.
    t = timeout
    if t is None:
        t = int(os.environ.get("QDRANT_TIMEOUT", "180"))
    return QdrantClient(
        url=qdrant_url(),
        api_key=api_key(),
        timeout=t,
        cloud_inference=True,
    )


def dense_document(text: str, *, model: str = E5_MODEL_ID):
    """Cloud Inference document for dense E5 (passage/query prefixes applied by Qdrant)."""
    from qdrant_client.http import models as qm

    return qm.Document(text=text, model=model)


def sparse_document(text: str, *, model: str = BM25_MODEL):
    """Cloud Inference document for sparse BM25."""
    from qdrant_client.http import models as qm

    return qm.Document(text=text, model=model)


def point_id(*parts: str | int) -> str:
    """Deterministic UUID string for upserts."""
    key = ":".join(str(p) for p in parts)
    return str(uuid.uuid5(POINT_NS, key))


def git_commit(root: Path | None = None) -> str | None:
    root = root or vault_root()
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Minimal YAML-ish frontmatter parser (no external dependency required)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    body = text[m.end() :]
    meta: dict[str, Any] = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        if not key:
            continue
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            if not inner:
                meta[key] = []
            else:
                meta[key] = [
                    p.strip().strip("'\"") for p in inner.split(",") if p.strip()
                ]
        elif (raw.startswith('"') and raw.endswith('"')) or (
            raw.startswith("'") and raw.endswith("'")
        ):
            meta[key] = raw[1:-1]
        else:
            # unquoted scalar
            if raw.isdigit():
                meta[key] = int(raw)
            else:
                meta[key] = raw
    return meta, body


def strip_wikilinks(md: str) -> str:
    """Replace [[path|label]] / [[path]] with label or path tail for BM25 text."""

    def repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if "|" in inner:
            return inner.split("|", 1)[1].strip()
        return Path(inner).name

    return re.sub(r"\[\[([^\]]+)\]\]", repl, md)


def wiki_page_type(rel_path: str) -> str:
    parts = Path(rel_path).parts
    if len(parts) >= 2 and parts[0] == "wiki":
        folder = parts[1]
        mapping = {
            "concepts": "concept",
            "people": "person",
            "passages": "passage",
            "questions": "question",
            "source-notes": "source-note",
        }
        return mapping.get(folder, "wiki")
    return "wiki"


def iter_wiki_markdown(root: Path | None = None) -> list[Path]:
    root = root or vault_root()
    wiki = root / "wiki"
    skip_names = {"index.md", "log.md", "catalog.jsonl"}
    skip_dirs = {"indexes"}
    paths: list[Path] = []
    for p in sorted(wiki.rglob("*.md")):
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.name in skip_names:
            continue
        paths.append(p)
    return paths


def vault_filter(vault_id: str = VAULT_ID) -> dict[str, Any]:
    """Qdrant filter dict requiring vault_id (for REST / client Filter)."""
    from qdrant_client.http import models as qm

    return qm.Filter(
        must=[
            qm.FieldCondition(
                key="vault_id",
                match=qm.MatchValue(value=vault_id),
            )
        ]
    )
