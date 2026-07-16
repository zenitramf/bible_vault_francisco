#!/usr/bin/env python3
"""Lightweight fixtures for enriched catalog + reverse indexes + search ranking."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Allow importing wiki_tool from the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
import wiki_tool as wt  # noqa: E402


class CatalogExtractionTests(unittest.TestCase):
    def test_normalize_abbrev_ref(self) -> None:
        self.assertEqual(wt.normalize_abbrev_ref_string("1ti 1:12"), "1ti 1:12")
        self.assertEqual(wt.normalize_abbrev_ref_string("mt 6:5-15"), "mt 6:5-15")
        self.assertIsNone(wt.normalize_abbrev_ref_string("not a ref"))

    def test_extract_display_refs_en_dash(self) -> None:
        text = "Key loci: Matthew 6:5–15; John 17; Romans 8:26–27."
        refs = wt.extract_display_refs(text)
        self.assertIn("mt 6:5-15", refs)
        self.assertIn("joh 17", refs)
        self.assertIn("ro 8:26-27", refs)

    def test_prayer_catalog_row_from_vault(self) -> None:
        path = wt.WIKI / "concepts" / "Prayer.md"
        if not path.is_file():
            self.skipTest("Prayer.md not in vault")
        row = wt.catalog_row(path)
        assert row is not None
        self.assertEqual(row["title"], "Prayer")
        self.assertIn("prayer", row["tags"])
        self.assertTrue(row["source_paths"], "expected source_paths on Prayer")
        self.assertTrue(
            any(p.startswith("sources/") for p in row["source_paths"]),
            row["source_paths"],
        )
        self.assertTrue(row["bible_references"], "expected derived bible_references")
        joined = " ".join(row["bible_references"])
        self.assertIn("mt 6", joined)
        self.assertTrue(row["related_paths"])
        self.assertTrue(any("Holy Spirit" in p or "holy" in p.lower() for p in row["related_paths"]) or row["related_paths"])

    def test_reverse_indexes_shape(self) -> None:
        rows = [
            {
                "path": "wiki/concepts/Prayer.md",
                "tags": ["prayer", "christ"],
                "type": "Biblical Concept",
                "source_paths": ["sources/commentaries_english/chspurgeon-sermons/volume-26/sermon_1532.md"],
                "bible_reference": None,
                "bible_references": ["mt 6:5-15", "ro 8:26-27"],
                "bible_book_keys": [40, 45],
            }
        ]
        with tempfile.TemporaryDirectory() as tmp:
            # redirect INDEXES_DIR
            old = wt.INDEXES_DIR
            wt.INDEXES_DIR = Path(tmp) / "indexes"
            try:
                wt.rebuild_reverse_indexes(rows)
                by_tag = [json.loads(l) for l in (wt.INDEXES_DIR / "by-tag.jsonl").read_text().splitlines() if l]
                keys = {r["key"] for r in by_tag}
                self.assertIn("prayer", keys)
                by_source = [json.loads(l) for l in (wt.INDEXES_DIR / "by-source.jsonl").read_text().splitlines() if l]
                self.assertEqual(by_source[0]["count"], 1)
                by_passage = [json.loads(l) for l in (wt.INDEXES_DIR / "by-passage.jsonl").read_text().splitlines() if l]
                passage_keys = {r["key"] for r in by_passage}
                self.assertIn("mt 6:5-15", passage_keys)
                self.assertIn("book:40", passage_keys)
            finally:
                wt.INDEXES_DIR = old

    def test_search_ranks_prayer_for_prayer_query(self) -> None:
        if not wt.CATALOG.is_file():
            self.skipTest("catalog missing; run build")
        rows = wt.load_jsonl(wt.CATALOG)
        if not rows:
            self.skipTest("empty catalog")
        hits = []
        terms = wt.tokenize_query("prayer")
        hints = wt.query_to_ref_hints("prayer")
        for row in rows:
            result = wt.score_catalog_row(row, terms, "prayer", hints)
            if result:
                hits.append((result[0], row.get("path")))
        hits.sort(key=lambda x: -x[0])
        self.assertTrue(hits, "expected hits for prayer")
        self.assertIn("Prayer.md", hits[0][1])

    def test_search_matthew_6_hits_prayer(self) -> None:
        if not wt.CATALOG.is_file():
            self.skipTest("catalog missing; run build")
        rows = wt.load_jsonl(wt.CATALOG)
        terms = wt.tokenize_query("matthew 6")
        hints = wt.query_to_ref_hints("matthew 6")
        hits = []
        for row in rows:
            result = wt.score_catalog_row(row, terms, "matthew 6", hints)
            if result:
                hits.append((result[0], row.get("path"), result[1]))
        hits.sort(key=lambda x: -x[0])
        paths = [h[1] for h in hits]
        self.assertTrue(any(p and "Prayer" in p for p in paths), paths[:5])


class IndexBaseGenerationTests(unittest.TestCase):
    def test_select_base_profile(self) -> None:
        self.assertEqual(wt.select_base_profile("wiki"), "wiki_hub")
        self.assertEqual(wt.select_base_profile("wiki/concepts"), "wiki_concepts")
        self.assertEqual(wt.select_base_profile("wiki/passages"), "wiki_passages")
        self.assertEqual(wt.select_base_profile("wiki/source-notes"), "wiki_source_notes")
        self.assertEqual(wt.select_base_profile("wiki/people"), "wiki_generic")
        self.assertEqual(wt.select_base_profile("wiki/indexes"), "wiki_generic")
        self.assertEqual(wt.select_base_profile("sources"), "sources_generic")
        self.assertEqual(
            wt.select_base_profile("sources/commentaries_english/chspurgeon-sermons/volume-1"),
            "sources_generic",
        )
        self.assertEqual(wt.select_base_profile("raw"), "simple")
        self.assertEqual(wt.select_base_profile("schema"), "simple")
        self.assertEqual(wt.select_base_profile("_templates"), "simple")
        with self.assertRaises(ValueError):
            wt.select_base_profile("")

    def test_render_index_base_folder_token(self) -> None:
        body = wt.render_index_base("wiki/concepts")
        self.assertIn('file.inFolder("wiki/concepts")', body)
        self.assertNotIn("__FOLDER__", body)
        self.assertNotIn("---\n", body)
        self.assertIn('type == "Biblical Concept"', body)

        sources = wt.render_index_base("sources/articles")
        self.assertIn('file.inFolder("sources/articles")', sources)
        self.assertIn("bible_book_name", sources)

    def test_render_bases_base(self) -> None:
        body = wt.render_bases_base()
        self.assertIn('file.ext == "base"', body)
        self.assertIn("is_index_base", body)
        self.assertIn("Index counterparts only", body)

    def test_rebuild_index_bases_temp_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Point module roots at temp vault
            old_root = wt.ROOT
            wt.ROOT = root
            try:
                (root / "wiki" / "concepts").mkdir(parents=True)
                (root / "wiki" / "concepts" / "index.md").write_text(
                    "# Concepts\n\n# Contents\n\n", encoding="utf-8"
                )
                (root / "sources" / "books").mkdir(parents=True)
                (root / "sources" / "books" / "index.md").write_text(
                    "# Books\n\n# Contents\n\n", encoding="utf-8"
                )
                (root / "index.md").write_text("# Root\n\n# Contents\n\n", encoding="utf-8")

                stats = wt.rebuild_index_bases()
                self.assertEqual(stats["index_bases"], 2)
                self.assertTrue((root / "bases.base").is_file())
                self.assertFalse((root / "index.base").is_file())
                concepts_base = (root / "wiki" / "concepts" / "index.base").read_text(encoding="utf-8")
                self.assertIn('file.inFolder("wiki/concepts")', concepts_base)
                books_base = (root / "sources" / "books" / "index.base").read_text(encoding="utf-8")
                self.assertIn('file.inFolder("sources/books")', books_base)
                self.assertIn('file.ext == "base"', (root / "bases.base").read_text(encoding="utf-8"))
            finally:
                wt.ROOT = old_root


if __name__ == "__main__":
    unittest.main()
