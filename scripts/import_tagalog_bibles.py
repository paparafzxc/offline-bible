#!/usr/bin/env python3
"""Import licensed Tagalog Bible texts into Stillword's offline bundle.

Default: Ang Dating Biblia (1905) and Tagalog Unlocked Literal Bible (2018).
Run from the repository root:
    py -3 -m pip install datasets huggingface_hub
    py -3 scripts/import_tagalog_bibles.py
    py -3 scripts/validate_library.py

The script runs at build time. The resulting reader bundle is local JavaScript,
so Stillword continues to work directly from file:// without network access.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "bible-data.js"
MANIFEST_FILE = ROOT / "sources" / "tagalog-manifest.json"

# Standard USFM book IDs mapped to the OSIS identifiers in Stillword.
USFM_TO_OSIS = {
    "GEN":"Gen","EXO":"Exod","LEV":"Lev","NUM":"Num","DEU":"Deut",
    "JOS":"Josh","JDG":"Judg","RUT":"Ruth","1SA":"1Sam","2SA":"2Sam",
    "1KI":"1Kgs","2KI":"2Kgs","1CH":"1Chr","2CH":"2Chr","EZR":"Ezra",
    "NEH":"Neh","EST":"Esth","JOB":"Job","PSA":"Ps","PRO":"Prov",
    "ECC":"Eccl","SNG":"Song","ISA":"Isa","JER":"Jer","LAM":"Lam",
    "EZK":"Ezek","DAN":"Dan","HOS":"Hos","JOL":"Joel","AMO":"Amos",
    "OBA":"Obad","JON":"Jonah","MIC":"Mic","NAM":"Nah","HAB":"Hab",
    "ZEP":"Zeph","HAG":"Hag","ZEC":"Zech","MAL":"Mal","MAT":"Matt",
    "MRK":"Mark","LUK":"Luke","JHN":"John","ACT":"Acts","ROM":"Rom",
    "1CO":"1Cor","2CO":"2Cor","GAL":"Gal","EPH":"Eph","PHP":"Phil",
    "COL":"Col","1TH":"1Thess","2TH":"2Thess","1TI":"1Tim","2TI":"2Tim",
    "TIT":"Titus","PHM":"Phlm","HEB":"Heb","JAS":"Jas","1PE":"1Pet",
    "2PE":"2Pet","1JN":"1John","2JN":"2John","3JN":"3John","JUD":"Jude",
    "REV":"Rev"
}


def parse_catalogue():
    text = DATA_FILE.read_text(encoding="utf-8")
    match = re.search(r"window\.BIBLE_DATA\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not match:
        raise RuntimeError("Cannot parse data/bible-data.js")
    return json.loads(match.group(1))


def verify_chapters(chapters, books, code):
    expected = {f"{b['osis']}.{n}" for b in books for n in range(1, b["chapters"] + 1)}
    actual = set(chapters)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise RuntimeError(f"{code}: chapter coverage mismatch; missing={missing[:8]}, extra={extra[:8]}")
    total = 0
    for key, verses in chapters.items():
        if not verses:
            raise RuntimeError(f"{code}: empty chapter {key}")
        for number, text in verses.items():
            if not str(number).strip() or not isinstance(text, str) or not text.strip():
                raise RuntimeError(f"{code}: invalid verse {key}:{number}")
            total += 1
    return total


def import_adb1905(books):
    try:
        from datasets import load_dataset
        from huggingface_hub import HfApi
    except ImportError as exc:
        raise RuntimeError("Install dependencies first: py -3 -m pip install datasets huggingface_hub") from exc

    repo = "k-mktr/tagalog_bible_tl"
    revision = HfApi().dataset_info(repo).sha
    if not revision:
        raise RuntimeError("Could not resolve immutable Hugging Face dataset revision.")
    rows = load_dataset(repo, split="train", revision=revision)
    chapters = {}
    for row in rows:
        book_number = int(row["book_number"])
        if not 1 <= book_number <= 66:
            raise RuntimeError(f"ADB1905: invalid book_number {book_number}")
        osis = books[book_number - 1]["osis"]
        chapter_number = int(row["chapter"])
        verse_number = str(row["verse"]).strip()
        key = f"{osis}.{chapter_number}"
        verse_map = chapters.setdefault(key, {})
        if verse_number in verse_map:
            raise RuntimeError(f"ADB1905: duplicate verse {key}:{verse_number}")
        verse_map[verse_number] = str(row["text"]).strip()

    count = verify_chapters(chapters, books, "ADB1905")
    if count != 31102:
        raise RuntimeError(f"ADB1905: expected 31,102 verses from source card; found {count}")
    return {
        "name": "Ang Dating Biblia (1905)",
        "rights": "Public domain (1905 edition); source and edition provenance recorded in sources/tagalog-manifest.json",
        "coverage": "complete",
        "language": "tl",
        "chapters": chapters,
    }, {
        "code": "ADB1905",
        "name": "Ang Dating Biblia (1905)",
        "language": "tl",
        "sourceUrl": f"https://huggingface.co/datasets/{repo}",
        "sourceRevision": revision,
        "license": "Public domain (1905 edition; source dataset declares copyright expired)",
        "sourceVerified": True,
        "verses": count,
    }


def clean_usfm(text):
    text = re.sub(r"\f .*?\f\*", " ", text, flags=re.S)
    text = re.sub(r"\x .*?\x\*", " ", text, flags=re.S)
    # Preserve the displayed word and discard lexical attributes.
    text = re.sub(r"\w\s+([^|\\]+)\|[^\\]*?\w\*", r"\1", text)
    text = re.sub(r"\zaln-[^\\]*", " ", text)
    text = re.sub(r"\[+]?[-a-zA-Z0-9]+\*?", " ", text)
    text = re.sub(r"\s+", " ", text)
    return html.unescape(text).strip()


def import_tglulb(books):
    url = "https://ebible.org/Scriptures/tglulb_usfm.zip"
    request = urllib.request.Request(url, headers={"User-Agent":"Stillword Offline Bible corpus importer"})
    with urllib.request.urlopen(request, timeout=60) as response:
        archive_bytes = response.read()
    digest = hashlib.sha256(archive_bytes).hexdigest()
    chapters = {}

    with zipfile.ZipFile(BytesIO(archive_bytes)) as archive:
        usfm_files = [n for n in archive.namelist() if n.lower().endswith(".usfm")]
        if not usfm_files:
            raise RuntimeError("TGLULB archive contains no .usfm files.")
        seen_books = set()
        for filename in usfm_files:
            raw = archive.read(filename).decode("utf-8-sig")
            id_match = re.search(r"(?m)^\id\s+([A-Z0-9]{3})", raw)
            if not id_match:
                continue
            usfm_id = id_match.group(1)
            osis = USFM_TO_OSIS.get(usfm_id)
            if not osis:
                raise RuntimeError(f"TGLULB: unsupported USFM book ID {usfm_id} in {filename}")
            if osis in seen_books:
                raise RuntimeError(f"TGLULB: duplicate book file for {osis}")
            seen_books.add(osis)

            chapter_matches = list(re.finditer(r"(?m)\c\s+(\d+)\s*", raw))
            if not chapter_matches:
                raise RuntimeError(f"TGLULB: no chapters in {filename}")
            for ci, cm in enumerate(chapter_matches):
                chapter_number = int(cm.group(1))
                end = chapter_matches[ci + 1].start() if ci + 1 < len(chapter_matches) else len(raw)
                chunk = raw[cm.end():end]
                verse_matches = list(re.finditer(r"(?m)\v\s+([0-9]+[a-z]?)\s*", chunk))
                if not verse_matches:
                    raise RuntimeError(f"TGLULB: no verses in {osis}.{chapter_number}")
                verse_map = {}
                for vi, vm in enumerate(verse_matches):
                    verse_number = vm.group(1)
                    vend = verse_matches[vi + 1].start() if vi + 1 < len(verse_matches) else len(chunk)
                    verse_text = clean_usfm(chunk[vm.end():vend])
                    if not verse_text:
                        raise RuntimeError(f"TGLULB: blank verse {osis}.{chapter_number}:{verse_number}")
                    if verse_number in verse_map:
                        raise RuntimeError(f"TGLULB: duplicate verse {osis}.{chapter_number}:{verse_number}")
                    verse_map[verse_number] = verse_text
                chapters[f"{osis}.{chapter_number}"] = verse_map

    if len(seen_books) != 66:
        raise RuntimeError(f"TGLULB: expected 66 book files, found {len(seen_books)}")
    count = verify_chapters(chapters, books, "TGLULB")
    return {
        "name": "Tagalog Unlocked Literal Bible (2018)",
        "rights": "© 2018 Door43 World Missions Community; CC BY-SA 4.0. Attribution and ShareAlike apply.",
        "coverage": "complete",
        "language": "tl",
        "source": url,
        "license": "CC BY-SA 4.0",
        "attribution": "Tagalog Unlocked Literal Bible © 2018 Door43 World Missions Community, licensed under CC BY-SA 4.0.",
        "chapters": chapters,
    }, {
        "code": "TGLULB",
        "name": "Tagalog Unlocked Literal Bible (2018)",
        "language": "tl",
        "sourceUrl": url,
        "archiveSha256": digest,
        "license": "CC BY-SA 4.0",
        "attribution": "Tagalog Unlocked Literal Bible © 2018 Door43 World Missions Community, licensed under CC BY-SA 4.0.",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "sourceVerified": True,
        "verses": count,
    }


def main():
    data = parse_catalogue()
    books = data.get("books", [])
    if len(books) != 66 or sum(b["chapters"] for b in books) != 1189:
        raise RuntimeError("Stillword catalogue must contain 66 books and 1,189 chapters.")

    translations = data.setdefault("translations", {})
    adb, adb_meta = import_adb1905(books)
    ulb, ulb_meta = import_tglulb(books)
    translations["ADB1905"] = adb
    translations["TGLULB"] = ulb
    data["schemaVersion"] = 2

    DATA_FILE.write_text(
        "/* Generated by scripts/import_tagalog_bibles.py. Do not edit by hand. */\n"
        "window.BIBLE_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "translations": [adb_meta, ulb_meta],
    }
    MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Imported ADB1905 and TGLULB. Run scripts/validate_library.py next.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"TAGALOG IMPORT FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
