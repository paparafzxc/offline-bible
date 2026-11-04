# Bible data

## Runtime constraint

Stillword opens directly from a folder. Do not use runtime `fetch()` for local JSON: browsers may block it under `file://`. The current reader consumes a locally bundled JavaScript data file, `data/bible-data.js`.

## Build the complete English corpus

From the repository root, run:

```powershell
py -3 -m pip install datasets huggingface_hub
py -3 scripts/import_public_domain_bibles.py
py -3 scripts/import_tagalog_bibles.py
py -3 scripts/validate_library.py
```

The importer is a one-time build-time operation. It fetches source books from the pinned `midvash/bible-data` commit, checks source metadata, validates book/chapter/verse structure, and writes the generated reader bundle plus `sources/manifest.json`. The running app never downloads anything.

Default translations:
- WEB — World English Bible
- ASV — American Standard Version (1901)

KJV is not imported yet: the selected upstream revision marks its public-domain provenance as unverified, so the importer rejects it rather than silently accepting a legal uncertainty.

Use `--translations WEB` to import only WEB. The Tagalog importer adds ADB1905 and TGLULB. Run both importers before validation; keep all generated manifests with the bundle.

## Provenance and integrity

For each translation, the manifest records the upstream commit, source URL, source verification flag, declared corpus statistics, and SHA-256 hash for each of the 66 source book files. The importer refuses versions that the upstream metadata does not mark as verified public domain.

The validator checks all 66 canonical books and 1,189 expected chapters, no missing or extra chapter keys, non-empty verse text, verified public-domain metadata, 66 source hashes per translation, and verse totals matching upstream metadata.

Structural validation is not a substitute for textual proofreading or jurisdiction-specific legal review.

## Philippine Bible Society translations

Ang Biblia 2001 is not bundled because redistribution permission is required. Ang Biblia 1905 must be sourced from a specific, verifiable edition with a documented redistribution basis before inclusion. Never infer permission from an online copy being accessible.
