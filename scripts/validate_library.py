#!/usr/bin/env python3
"""Validate the generated Stillword data/bible-data.js bundle.

Run after scripts/import_public_domain_bibles.py:
    python scripts/validate_library.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "bible-data.js"
MANIFEST_FILE = ROOT / "sources" / "manifest.json"


def fail(message: str) -> None:
    raise RuntimeError(message)


def main() -> int:
    source = DATA_FILE.read_text(encoding="utf-8")
    match = re.search(r"window\.BIBLE_DATA\s*=\s*(\{.*\})\s*;?\s*$", source, re.DOTALL)
    if not match:
        fail("Cannot parse data/bible-data.js")
    data = json.loads(match.group(1))
    if data.get("schemaVersion") != 2:
        fail("Library is still starter data. Run scripts/import_public_domain_bibles.py first.")

    books = data.get("books")
    translations = data.get("translations")
    if not isinstance(books, list) or len(books) != 66:
        fail("Expected exactly 66 canonical books.")
    expected_chapters = {f"{b['osis']}.{n}" for b in books for n in range(1, b["chapters"] + 1)}
    if len(expected_chapters) != 1189:
        fail("Canonical catalogue must contain 1,189 chapters.")
    if not isinstance(translations, dict) or not translations:
        fail("No translation corpus found.")

    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    errors: list[str] = []
    for code, translation in translations.items():
        if translation.get("coverage") != "complete":
            errors.append(f"{code}: coverage is not marked complete")
        chapters = translation.get("chapters", {})
        actual_chapters = set(chapters)
        missing = sorted(expected_chapters - actual_chapters)
        extra = sorted(actual_chapters - expected_chapters)
        if missing:
            errors.append(f"{code}: {len(missing)} missing chapters; first: {missing[:5]}")
        if extra:
            errors.append(f"{code}: unexpected chapter keys: {extra[:5]}")
        verses = 0
        for chapter_key, verse_map in chapters.items():
            if not isinstance(verse_map, dict) or not verse_map:
                errors.append(f"{code} {chapter_key}: empty or invalid chapter")
                continue
            for verse_number, text in verse_map.items():
                if not str(verse_number).strip() or not isinstance(text, str) or not text.strip():
                    errors.append(f"{code} {chapter_key}:{verse_number}: invalid verse text")
                verses += 1
        record = manifest.get("translations", {}).get(code)
        if not record:
            errors.append(f"{code}: missing provenance manifest entry")
        else:
            if record.get("license") != "public-domain" or record.get("sourceVerified") is not True:
                errors.append(f"{code}: license/provenance is not verified public domain")
            if len(record.get("bookSourceSha256", {})) != 66:
                errors.append(f"{code}: expected SHA-256 for all 66 source books")
            declared = record.get("stats", {}).get("verses")
            if declared != verses:
                errors.append(f"{code}: verse count {verses} != manifest count {declared}")
        print(f"{code}: {len(actual_chapters)}/1,189 chapters, {verses:,} verses")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {len(translations)} complete translation(s), all chapters present.")
    print("Note: structural checks do not prove textual accuracy or jurisdiction-specific copyright status.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
