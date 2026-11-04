# Stillword — Offline Bible

Stillword is a folder-portable Bible reader. Open `index.html` directly in a modern browser; the app is designed to work without a local server.

## Complete offline text library (v0.2)

The initial `data/bible-data.js` is starter/demo content. To build a complete, locally bundled public-domain corpus, run once from the repository root on a computer with internet access:

```powershell
py -3 scripts/import_public_domain_bibles.py
py -3 scripts/validate_library.py
```

The importer downloads the verified public-domain WEB, KJV, and ASV source books from a pinned Midvash Bible Data revision, checks all 66 books and 1,189 chapters for each translation, and writes `data/bible-data.js` plus `sources/manifest.json` with source metadata and SHA-256 hashes.

After import, open `index.html` directly. No runtime download, API, server, or internet connection is used. Keep the generated data file and manifest together when copying or packaging Stillword.

**Important:** the importer is committed, but generated full-text data is not yet present in a fresh clone until the import command is run. Do not describe the starter repository as containing complete Bible texts before the validator passes.

## Licensing

The imported English texts are identified by the upstream dataset as public domain, with source metadata recorded in `sources/manifest.json`. Copyright status can vary by jurisdiction; review source notes before redistribution. The WEB name is a trademark and the text must not be altered while represented as the World English Bible.

Ang Biblia 2001 is not included; obtain written redistribution permission from the Philippine Bible Society before bundling it. Ang Biblia 1905 must be sourced from a specific, verified edition with a documented redistribution basis before inclusion.

## Personal data

Bookmarks, highlights, notes, theme, and reading preferences are stored in browser local storage. Export a backup before clearing browser data or moving to another browser profile.
