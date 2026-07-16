#!/usr/bin/env python3
"""Local Multilingual E5 Small encoder (384-d, L2-normalized).

Model identity: intfloat/multilingual-e5-small
Runtime: ONNX quantized (Xenova export) via onnxruntime — fits this host better
than full PyTorch. Prefix policy matches E5 training:

  passage: …   for documents / chunks to store
  query: …     for search queries

Cache dir: $BIBLE_VAULT_E5_CACHE or ~/.cache/bible_vault_e5

Examples:
  python3 .tools/scripts/e5_embed.py passage "Prayer is address to the Father"
  python3 .tools/scripts/e5_embed.py query "how should Christians pray" --json
  python3 .tools/scripts/e5_embed.py self-test
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

E5_MODEL_ID = "intfloat/multilingual-e5-small"
E5_DIM = 384
ONNX_REPO = "Xenova/multilingual-e5-small"
ONNX_FILE = "onnx/model_quantized.onnx"
DEFAULT_CACHE = Path(
    os.environ.get("BIBLE_VAULT_E5_CACHE", Path.home() / ".cache" / "bible_vault_e5")
)


def cache_dir() -> Path:
    p = DEFAULT_CACHE
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_assets(cache: Path | None = None) -> dict[str, Path]:
    """Download ONNX + tokenizer once into cache."""
    from huggingface_hub import hf_hub_download

    cache = cache or cache_dir()
    files = {
        "onnx": ONNX_FILE,
        "tokenizer": "tokenizer.json",
        "tokenizer_config": "tokenizer_config.json",
        "config": "config.json",
    }
    paths: dict[str, Path] = {}
    for key, rel in files.items():
        local = hf_hub_download(
            repo_id=ONNX_REPO,
            filename=rel,
            local_dir=str(cache),
        )
        paths[key] = Path(local)
    return paths


class E5Encoder:
    """Encode text with multilingual-e5-small (ONNX backend)."""

    def __init__(self, cache: Path | None = None) -> None:
        import onnxruntime as ort
        from tokenizers import Tokenizer

        paths = ensure_assets(cache)
        self.tokenizer = Tokenizer.from_file(str(paths["tokenizer"]))
        self.tokenizer.enable_truncation(max_length=512)
        self.tokenizer.enable_padding(pad_id=0, pad_token="<pad>")
        self.session = ort.InferenceSession(
            str(paths["onnx"]),
            providers=["CPUExecutionProvider"],
        )
        self.model_id = E5_MODEL_ID
        self.dim = E5_DIM
        self.backend = f"onnx:{ONNX_REPO}/{ONNX_FILE}"
        self.fingerprint = f"{E5_MODEL_ID}|onnx-quantized|prefix=passage_query_v1|dim={E5_DIM}"

    @staticmethod
    def with_prefix(kind: str, text: str) -> str:
        kind = kind.lower().strip()
        text = text.strip()
        if kind in ("query", "q"):
            if text.startswith("query:"):
                return text
            return f"query: {text}"
        if kind in ("passage", "document", "doc", "p"):
            if text.startswith("passage:"):
                return text
            return f"passage: {text}"
        raise ValueError(f"kind must be query or passage, got {kind!r}")

    def encode(
        self,
        texts: list[str],
        *,
        kind: str,
        batch_size: int = 8,
    ) -> np.ndarray:
        """Return float32 array shape (n, 384), L2-normalized."""
        if not texts:
            return np.zeros((0, E5_DIM), dtype=np.float32)

        prefixed = [self.with_prefix(kind, t) for t in texts]
        out_rows: list[np.ndarray] = []
        for i in range(0, len(prefixed), batch_size):
            batch = prefixed[i : i + batch_size]
            out_rows.append(self._encode_batch(batch))
        return np.vstack(out_rows).astype(np.float32)

    def encode_one(self, text: str, *, kind: str) -> list[float]:
        vec = self.encode([text], kind=kind)[0]
        return vec.tolist()

    def _encode_batch(self, prefixed: list[str]) -> np.ndarray:
        enc = self.tokenizer.encode_batch(prefixed)
        input_ids = np.array([e.ids for e in enc], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in enc], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids)
        feeds = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids,
        }
        outputs = self.session.run(None, feeds)
        last_hidden = outputs[0]  # (B, T, 384)
        mask = attention_mask[..., np.newaxis].astype(np.float32)
        summed = (last_hidden * mask).sum(axis=1)
        counts = mask.sum(axis=1).clip(min=1.0)
        emb = summed / counts
        norms = np.linalg.norm(emb, axis=1, keepdims=True).clip(min=1e-12)
        return emb / norms


def self_test(encoder: E5Encoder) -> int:
    q = encoder.encode(["how should a Christian pray"], kind="query")
    p_good = encoder.encode(
        ["Prayer is sincere address to the Father who sees in secret."],
        kind="passage",
    )
    p_other = encoder.encode(
        ["Genealogies of the tribes of Israel after the exile."],
        kind="passage",
    )
    sim_good = float(q[0] @ p_good[0])
    sim_other = float(q[0] @ p_other[0])
    print(f"model={encoder.model_id}")
    print(f"backend={encoder.backend}")
    print(f"fingerprint={encoder.fingerprint}")
    print(f"dim={encoder.dim}  dtype={q.dtype}")
    print(f"||q||={np.linalg.norm(q[0]):.4f} (expect ~1.0)")
    print(f"cosine(query, prayer_passage)={sim_good:.4f}")
    print(f"cosine(query, genealogy_passage)={sim_other:.4f}")
    if sim_good <= sim_other:
        print("WARN: expected prayer passage to score higher than genealogy.", file=sys.stderr)
        return 1
    if abs(float(np.linalg.norm(q[0])) - 1.0) > 0.05:
        print("WARN: vector not L2-normalized.", file=sys.stderr)
        return 1
    print("self-test OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_pass = sub.add_parser("passage", help="Encode passage text(s)")
    p_pass.add_argument("texts", nargs="+", help="Text to encode as passage")
    p_pass.add_argument("--json", action="store_true")

    p_q = sub.add_parser("query", help="Encode query text(s)")
    p_q.add_argument("texts", nargs="+", help="Text to encode as query")
    p_q.add_argument("--json", action="store_true")

    p_st = sub.add_parser("self-test", help="Smoke-test similarity ranking")
    p_st.add_argument("--json", action="store_true")

    p_info = sub.add_parser("info", help="Print model paths / fingerprint")
    p_info.add_argument("--download", action="store_true", help="Ensure cache assets")

    args = parser.parse_args(argv)

    if args.cmd == "info":
        if args.download:
            paths = ensure_assets()
        else:
            paths = {k: cache_dir() / v for k, v in {
                "onnx": ONNX_FILE,
                "tokenizer": "tokenizer.json",
            }.items()}
        print(
            json.dumps(
                {
                    "model_id": E5_MODEL_ID,
                    "dim": E5_DIM,
                    "onnx_repo": ONNX_REPO,
                    "onnx_file": ONNX_FILE,
                    "cache": str(cache_dir()),
                    "paths": {k: str(v) for k, v in paths.items()},
                    "prefix_policy": {
                        "document": "passage: {text}",
                        "query": "query: {text}",
                    },
                },
                indent=2,
            )
        )
        return 0

    encoder = E5Encoder()

    if args.cmd == "self-test":
        if args.json:
            q = encoder.encode_one("how should a Christian pray", kind="query")
            print(
                json.dumps(
                    {
                        "model_id": encoder.model_id,
                        "fingerprint": encoder.fingerprint,
                        "dim": len(q),
                        "sample_norm": float(np.linalg.norm(q)),
                    },
                    indent=2,
                )
            )
            return 0
        return self_test(encoder)

    kind = "passage" if args.cmd == "passage" else "query"
    vectors = encoder.encode(args.texts, kind=kind)
    if args.json:
        print(
            json.dumps(
                {
                    "model_id": encoder.model_id,
                    "fingerprint": encoder.fingerprint,
                    "kind": kind,
                    "dim": E5_DIM,
                    "count": len(args.texts),
                    "vectors": [v.tolist() for v in vectors],
                }
            )
        )
    else:
        for i, text in enumerate(args.texts):
            v = vectors[i]
            print(
                f"[{kind}] dim={len(v)} ||v||={np.linalg.norm(v):.4f} "
                f"preview={text[:60]!r}"
            )
            print("  first8:", " ".join(f"{x:.5f}" for x in v[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
