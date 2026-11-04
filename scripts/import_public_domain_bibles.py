#!/usr/bin/env python3
"""Import complete WEB/KJV/ASV corpora into Stillword's file://-safe data bundle.

Run from the repository root:
    python scripts/import_public_domain_bibles.py

The importer downloads source JSON once, verifies upstream license metadata,
checks all 66 books and 1,189 chapters, records SHA-256 hashes, then writes
data/bible-data.js and sources/manifest.json. The app itself makes no requests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "bible-data.js"
MANIFEST_FILE = ROOT / "sources" / "manifest.json"
UPSTREAM_COMMIT = "9586bd8228a747962df1ee8692730422fb7eb2ec"
UPSTREAM = (
    "https://raw.githubusercontent.com/midvash/bible-data/"
    + UPSTREAM_COMMIT
    + "/versions/en/{slug}/{path}"
)
TRANSLATIONS = {
    "WEB": {"slug": "web", "name": "World English Bible"},
    "KJV": {"slug": "kjv", "name": "King James Version"},
    "ASV": {"slug": "asv", "name": "American Standard Version"},
}


def fetch_json(url: str, attempts: int = 4) -> tuple[dict, bytes]:
    request = urllib.request.Request(
        url, headers={"User-Agent": "Stillword-Offline-Bible/0.2 corpus-import"}
    )
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                raw = response.read()
            return json.loads(raw.decode("utf-8")), raw
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt + 1 == attempts:
                raise RuntimeError(f"Unable to retrieve {url}: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    raise AssertionError("unreachable")


def load_catalogue() -> dict:
    source = DATA_FILE.read_text(encoding="utf-8")
    match = re.fullmatch(
        r"\s*/\*.*?\*/\s*window\.BIBLE_DATA\s*=\s*(\{.*\})\s*;?\s*",
        source,
        flags=re.DOTALL,
    )
    if not match:
        raise RuntimeError("Cannot parse existing data/bible-data.js catalogue.")
    return json.loads(match.group(1))


def normalize_book(raw: dict, expected: dict) -> tuple[dict, int]:
    osis = expected["osis"]
    if raw.get("book") != osis:
        raise RuntimeError(f"Expected {osis}, source returned {raw.get('book')!r}")
    chapters = raw.get("chapters")
    if not isinstance(chapters, list) or len(chapters) != expected["chapters"]:
        raise RuntimeError(
            f"{osis}: expected {expected['chapters']} chapters, "
            f"found {len(chapters) if isinstance(chapters, list) else 'invalid'}"
        )
    chapter_map: dict[str, dict[str, str]] = {}
    verse_total = 0
    for expected_chapter, chapter in enumerate(chapters, start=1):
        number = chapter.get("chapter")
        if number != expected_chapter:
            raise RuntimeError(f"{osis}: chapter sequence gap at {expected_chapter}")
        verse_map: dict[str, str] = {}
        for verse in chapter.get("verses", []):
            verse_number = str(verse.get("number", "")).strip()
            text = verse.get("text")
            if not verse_number or verse_number in verse_map:
                raise RuntimeError(f"{osis} {number}: missing/duplicate verse number")
            if not isinstance(text, str) or not text.strip():
                raise RuntimeError(f"{osis} {number}:{verse_number}: blank verse")
            verse_map[verse_number] = text
            verse_total += 1
        if not verse_map:
            raise RuntimeError(f"{osis} {number}: chapter has no verses")
        chapter_map[f"{osis}.{number}"] = verse_map
    return chapter_map, verse_total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--translations", nargs="+", choices=TRANSLATIONS,
        default=["WEB", "KJV", "ASV"],
        help="translation codes to import (default: WEB KJV ASV)",
    )
    args = parser.parse_args()

    catalogue = load_catalogue()
    books = catalogue.get("books", [])
    if len(books) != 66 or sum(b["chapters"] for b in books) != 1189:
        raise RuntimeError("Existing book catalogue is not the 66-book/1,189-chapter canon.")

    output_translations: dict[str, dict] = {}
    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "upstream": "midvash/bible-data",
        "upstreamCommit": UPSTREAM_COMMIT,
        "upstreamCommitUrl": f"https://github.com/midvash/bible-data/commit/{UPSTREAM_COMMIT}",
        "translations": {},
    }

    for code in args.translations:
        spec = TRANSLATIONS[code]
        slug = spec["slug"]
        meta_url = UPSTREAM.format(slug=slug, path="metadata.json")
        metadata, metadata_raw = fetch_json(meta_url)
        if metadata.get("license") != "public-domain" or metadata.get("sourceVerified") is not True:
            raise RuntimeError(
                f"{code}: upstream metadata does not confirm public-domain status; refusing import."
            )
        stats = metadata.get("stats", {})
        if stats.get("books") != 66 or stats.get("chapters") != 1189:
            raise RuntimeError(f"{code}: upstream metadata does not declare 66 books / 1,189 chapters.")

        chapter_map: dict[str, dict[str, str]] = {}
        book_hashes: dict[str, str] = {}
        verse_total = 0
        for index, book in enumerate(books, start=1):
            url = UPSTREAM.format(slug=slug, path=f"books/{book['osis']}.json")
            raw_book, raw_bytes = fetch_json(url)
            mapped, count = normalize_book(raw_book, book)
            chapter_map.update(mapped)
            verse_total += count
            book_hashes[book["osis"]] = hashlib.sha256(raw_bytes).hexdigest()
            print(f"{code}: [{index:02}/66] {book['name']} — {count} verses")

        if verse_total != stats.get("verses"):
            raise RuntimeError(
                f"{code}: downloaded {verse_total} verses, metadata declares {stats.get('verses')}."
            )

        output_translations[code] = {
            "name": spec["name"],
            "rights": metadata.get("licenseNote", "Public domain"),
            "coverage": "complete",
            "source": metadata.get("sourceUrl"),
            "chapters": chapter_map,
        }
        manifest["translations"][code] = {
            "name": spec["name"],
            "language": metadata.get("language"),
            "editionYear": metadata.get("year"),
            "license": metadata.get("license"),
            "licenseNote": metadata.get("licenseNote"),
            "sourceUrl": metadata.get("sourceUrl"),
            "sourceVerified": metadata.get("sourceVerified"),
            "upstreamMetadataSha256": hashlib.sha256(metadata_raw).hexdigest(),
            "stats": stats,
            "bookSourceSha256": book_hashes,
        }
        print(f"PASS {code}: 66 books, 1,189 chapters, {verse_total:,} verses")

    catalogue["schemaVersion"] = 2
    catalogue["translations"] = output_translations
    DATA_FILE.write_text(
        "/* Generated by scripts/import_public_domain_bibles.py. Do not edit by hand. */\n"
        "window.BIBLE_DATA = "
        + json.dumps(catalogue, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {DATA_FILE.relative_to(ROOT)}")
    print(f"Wrote {MANIFEST_FILE.relative_to(ROOT)}")
    print("The app remains offline: all text is bundled locally; no runtime download is used.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"IMPORT FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
