#!/usr/bin/env python3
"""Validate a v0.2 canonical Bible translation JSON file.

Usage:
  python scripts/validate_library.py path/to/WEB.json
  python scripts/validate_library.py path/to/WEB.json --expected-books 66

This validates structural completeness against the source file's declared
book/chapter contents. It does not establish copyright or redistribution rights.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXPECTED_BOOKS = 66


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--expected-books", type=int, default=EXPECTED_BOOKS)
    args = parser.parse_args()

    try:
        data = json.loads(args.source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read valid UTF-8 JSON: {exc}")

    if data.get("schemaVersion") != 2:
        fail("schemaVersion must be 2")
    translation = data.get("translation")
    if not isinstance(translation, dict) or not translation.get("code"):
        fail("translation.code is required")
    books = data.get("books")
    if not isinstance(books, list):
        fail("books must be an array")
    if len(books) != args.expected_books:
        fail(f"expected {args.expected_books} books, found {len(books)}")

    seen_books: set[str] = set()
    total_chapters = 0
    total_verses = 0
    errors: list[str] = []

    for book in books:
        osis = str(book.get("osis", ""))
        if not osis or osis in seen_books:
            errors.append(f"missing or duplicate OSIS book identifier: {osis!r}")
            continue
        seen_books.add(osis)
        chapters = book.get("chapters")
        if not isinstance(chapters, list) or not chapters:
            errors.append(f"{osis}: chapters must be a non-empty array")
            continue

        chapter_numbers: set[int] = set()
        for chapter in chapters:
            number = chapter.get("number")
            if not isinstance(number, int) or number < 1 or number in chapter_numbers:
                errors.append(f"{osis}: invalid or duplicate chapter number {number!r}")
                continue
            chapter_numbers.add(number)
            verses = chapter.get("verses")
            if not isinstance(verses, list) or not verses:
                errors.append(f"{osis} {number}: no verses")
                continue

            verse_numbers: set[str] = set()
            for verse in verses:
                verse_number = str(verse.get("number", "")).strip()
                text = verse.get("text")
                if not verse_number or verse_number in verse_numbers:
                    errors.append(f"{osis} {number}: missing or duplicate verse number {verse_number!r}")
                    continue
                verse_numbers.add(verse_number)
                if not isinstance(text, str) or not text.strip():
                    errors.append(f"{osis} {number}:{verse_number}: empty verse text")
                else:
                    total_verses += 1
            total_chapters += 1

        if chapter_numbers and chapter_numbers != set(range(1, max(chapter_numbers) + 1)):
            errors.append(f"{osis}: chapter numbering has gaps")

    if errors:
        for error in errors[:100]:
            print(f"ERROR: {error}")
        if len(errors) > 100:
            print(f"... and {len(errors) - 100} more errors")
        return 1

    print(
        f"PASS: {translation['code']} — {len(seen_books)} books, "
        f"{total_chapters} chapters, {total_verses} non-empty verses"
    )
    print("NOTE: structural validation does not verify textual accuracy or legal rights.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
