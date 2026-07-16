#!/usr/bin/env python3
"""Bootstrap empty Qdrant Cloud collections for the Bible Vault.

Creates (idempotent ensure):
  - wiki_bm25   — sparse BM25 (IDF) for wiki synthesis
  - sources_e5  — dense 384-d cosine for sources (multilingual-e5-small)

Auth: QCLOUD_BIBLE_CLUSTER_API_KEY (database API key for the cluster).
Optional: QDRANT_URL (defaults to the bible_vault QCloud endpoint).

Never prints the API key. Does not embed or upsert documents.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any

DEFAULT_URL = (
    "https://af215873-0bcb-46d3-8a94-829541781b37"
    ".us-west-1-0.aws.cloud.qdrant.io:6333"
)
VAULT_ID = "bible_vault_francisco"

WIKI_COLLECTION = "wiki_bm25"
SOURCES_COLLECTION = "sources_e5"

WIKI_BODY: dict[str, Any] = {
    "sparse_vectors": {
        "bm25": {
            "modifier": "idf",
        }
    }
}

SOURCES_BODY: dict[str, Any] = {
    "vectors": {
        "size": 384,
        "distance": "Cosine",
    }
}

# Payload indexes required for filters under QCloud strict mode
# (unindexed_filtering_retrieve is disabled on this cluster).
WIKI_INDEXES: list[tuple[str, str]] = [
    ("vault_id", "keyword"),
    ("layer", "keyword"),
    ("page_type", "keyword"),
    ("status", "keyword"),
    ("bible_book_key", "integer"),
]

SOURCES_INDEXES: list[tuple[str, str]] = [
    ("vault_id", "keyword"),
    ("layer", "keyword"),
    ("source_corpus", "keyword"),
    ("content_kind", "keyword"),
    ("language", "keyword"),
    ("bible_book_key", "integer"),
]


class QdrantClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, Any] | list[Any] | None]:
        data = None
        headers = {
            "api-key": self.api_key,
            "Accept": "application/json",
        }
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read().decode("utf-8")
                parsed = json.loads(raw) if raw else None
                return resp.status, parsed
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = {"raw": raw}
            return exc.code, parsed


def collection_exists(client: QdrantClient, name: str) -> bool:
    code, payload = client.request("GET", "/collections")
    if code != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"list collections failed: HTTP {code} {payload}")
    result = payload.get("result") or {}
    names = {c.get("name") for c in result.get("collections") or []}
    return name in names


def ensure_collection(
    client: QdrantClient,
    name: str,
    body: dict[str, Any],
    *,
    recreate: bool,
) -> str:
    exists = collection_exists(client, name)
    if exists and recreate:
        code, payload = client.request("DELETE", f"/collections/{name}")
        if code not in (200, 202):
            raise RuntimeError(f"delete {name} failed: HTTP {code} {payload}")
        exists = False
    if exists:
        return "exists"
    code, payload = client.request("PUT", f"/collections/{name}", body)
    if code not in (200, 201):
        raise RuntimeError(f"create {name} failed: HTTP {code} {payload}")
    return "created"


def ensure_payload_indexes(
    client: QdrantClient,
    name: str,
    indexes: list[tuple[str, str]],
) -> list[str]:
    actions: list[str] = []
    code, payload = client.request("GET", f"/collections/{name}")
    if code != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"get {name} failed: HTTP {code} {payload}")
    schema = ((payload.get("result") or {}).get("payload_schema") or {})
    for field, field_type in indexes:
        current = schema.get(field) or {}
        if current.get("data_type") == field_type:
            actions.append(f"{field}=ok")
            continue
        body = {"field_name": field, "field_schema": field_type}
        code, resp = client.request("PUT", f"/collections/{name}/index", body)
        if code not in (200, 202):
            raise RuntimeError(
                f"index {name}.{field} failed: HTTP {code} {resp}"
            )
        actions.append(f"{field}=indexed")
    return actions


def describe(client: QdrantClient, name: str) -> dict[str, Any]:
    code, payload = client.request("GET", f"/collections/{name}")
    if code != 200 or not isinstance(payload, dict):
        raise RuntimeError(f"get {name} failed: HTTP {code} {payload}")
    result = payload.get("result") or {}
    params = (result.get("config") or {}).get("params") or {}
    return {
        "name": name,
        "status": result.get("status"),
        "points_count": result.get("points_count"),
        "indexed_vectors_count": result.get("indexed_vectors_count"),
        "vectors": params.get("vectors"),
        "sparse_vectors": params.get("sparse_vectors"),
        "payload_schema": sorted((result.get("payload_schema") or {}).keys()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        default=os.environ.get("QDRANT_URL", DEFAULT_URL),
        help="Qdrant REST base URL (or set QDRANT_URL)",
    )
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="Delete and recreate collections (destroys data)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Machine-readable summary on stdout",
    )
    args = parser.parse_args(argv)

    api_key = os.environ.get("QCLOUD_BIBLE_CLUSTER_API_KEY") or os.environ.get(
        "QDRANT_API_KEY"
    )
    if not api_key:
        print(
            "Missing QCLOUD_BIBLE_CLUSTER_API_KEY (or QDRANT_API_KEY).",
            file=sys.stderr,
        )
        return 2

    client = QdrantClient(args.url, api_key)

    # Connectivity check
    code, root = client.request("GET", "/")
    if code != 200:
        print(f"Qdrant root check failed: HTTP {code} {root}", file=sys.stderr)
        return 1

    summary: dict[str, Any] = {
        "url": args.url,
        "vault_id": VAULT_ID,
        "qdrant_version": (root or {}).get("version")
        if isinstance(root, dict)
        else None,
        "collections": {},
    }

    wiki_state = ensure_collection(
        client, WIKI_COLLECTION, WIKI_BODY, recreate=args.recreate
    )
    wiki_indexes = ensure_payload_indexes(client, WIKI_COLLECTION, WIKI_INDEXES)
    summary["collections"][WIKI_COLLECTION] = {
        "ensure": wiki_state,
        "indexes": wiki_indexes,
        **describe(client, WIKI_COLLECTION),
    }

    sources_state = ensure_collection(
        client, SOURCES_COLLECTION, SOURCES_BODY, recreate=args.recreate
    )
    sources_indexes = ensure_payload_indexes(
        client, SOURCES_COLLECTION, SOURCES_INDEXES
    )
    summary["collections"][SOURCES_COLLECTION] = {
        "ensure": sources_state,
        "indexes": sources_indexes,
        **describe(client, SOURCES_COLLECTION),
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"Qdrant {summary['qdrant_version']} @ {args.url}")
        print(f"vault_id contract: {VAULT_ID}")
        for name, info in summary["collections"].items():
            print(
                f"  {name}: ensure={info['ensure']} "
                f"status={info['status']} points={info['points_count']} "
                f"indexes={','.join(info['payload_schema'])}"
            )
            print(f"    index_actions: {', '.join(info['indexes'])}")
        print("Done. No points upserted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
