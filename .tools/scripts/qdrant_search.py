#!/usr/bin/env python3
"""Agent-facing multi-channel Qdrant search (wiki BM25 + sources E5).

Always scopes to vault_id=bible_vault_francisco.

  .qmd/bin/qdrant-search "prayer without hypocrisy"
  .qmd/bin/qdrant-search "Spirit intercession" --channel both --json
  .qmd/bin/qdrant-search "creation of light" --channel sources --corpus mhenry-concise --book-key 1

Channels:
  wiki     — sparse BM25 over wiki_bm25
  sources  — dense E5 over sources_e5 (pilot: mhenry-concise)
  both     — wiki first, then sources (default for agents when evidence may be needed)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_common import VAULT_ID  # noqa: E402
from qdrant_sources_search import search_sources  # noqa: E402
from qdrant_wiki_search import search_wiki  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Natural-language or keyword query")
    parser.add_argument(
        "--channel",
        choices=("wiki", "sources", "both"),
        default="both",
        help="Which Qdrant collections to query (default both)",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=6,
        help="Max hits per channel (default 6)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--corpus",
        default="",
        help="sources only: source_corpus filter (e.g. mhenry-concise)",
    )
    parser.add_argument(
        "--book-key",
        type=int,
        default=0,
        help="sources only: bible_book_key filter",
    )
    parser.add_argument(
        "--page-type",
        default="",
        help="wiki only: page_type filter",
    )
    parser.add_argument(
        "--min-score-sources",
        type=float,
        default=0.0,
        help="sources cosine floor (0 = none)",
    )
    parser.add_argument(
        "--min-score-wiki",
        type=float,
        default=0.0,
        help="wiki BM25 score floor (0 = none)",
    )
    args = parser.parse_args(argv)

    query = args.query.strip()
    if not query:
        print("Empty query.", file=sys.stderr)
        return 2

    channels_run: list[str] = []
    hits: list[dict[str, Any]] = []
    errors: list[str] = []

    if args.channel in ("wiki", "both"):
        channels_run.append("wiki_bm25")
        try:
            hits.extend(
                search_wiki(
                    query,
                    limit=args.limit,
                    page_type=args.page_type,
                    min_score=args.min_score_wiki,
                )
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"wiki_bm25: {exc}")

    if args.channel in ("sources", "both"):
        channels_run.append("sources_e5")
        try:
            hits.extend(
                search_sources(
                    query,
                    limit=args.limit,
                    corpus=args.corpus,
                    book_key=args.book_key,
                    min_score=args.min_score_sources,
                )
            )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"sources_e5: {exc}")

    # Keep channel order (wiki block then sources); within channel already ranked.
    # Optional: stable re-sort is wrong across score scales — do not mix scores.

    payload = {
        "query": query,
        "vault_id": VAULT_ID,
        "channels": channels_run,
        "count": len(hits),
        "hits": hits,
        "errors": errors or None,
        "note": (
            "Scores are not comparable across wiki_bm25 and sources_e5. "
            "Open vault_rel_path on disk for citations."
        ),
    }

    if errors and not hits:
        print(json.dumps(payload, indent=2) if args.json else "\n".join(errors), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(
            f"qdrant-search · vault_id={VAULT_ID} · query={query!r} · "
            f"channels={','.join(channels_run)} · n={len(hits)}"
        )
        if errors:
            for e in errors:
                print(f"  ! {e}", file=sys.stderr)
        current = None
        n = 0
        for r in hits:
            ch = r.get("channel")
            if ch != current:
                current = ch
                n = 0
                print(f"\n[{ch}]")
            n += 1
            path = r.get("vault_rel_path")
            score = r.get("score")
            if ch == "wiki_bm25":
                print(
                    f"  {n}. {score:.4f}  {path}\n"
                    f"      title={r.get('title')!r}  type={r.get('page_type')}\n"
                    f"      {r.get('wikilink')}"
                )
            else:
                print(
                    f"  {n}. {score:.4f}  {path}#{r.get('chunk_index')}\n"
                    f"      {r.get('section_heading')!r}  book={r.get('bible_book_name')}\n"
                    f"      {r.get('wikilink')}\n"
                    f"      {(r.get('text_preview') or '')[:160]!r}…"
                )
        if not hits:
            print("  (no hits)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
