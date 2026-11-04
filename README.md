# G-Word — Offline Bible

Stillword is a folder-portable Bible reader. Open `index.html` directly in a modern browser; the app is designed to work without a local server.

## Complete offline text library (v0.2)

The initial `data/bible-data.js` is starter/demo content. To build a complete, locally bundled public-domain corpus, run once from the repository root on a computer with internet access:

```powershell
py -3 -m pip install datasets huggingface_hub
py -3 scripts/import_public_domain_bibles.py
py -3 scripts/import_tagalog_bibles.py
py -3 scripts/validate_library.py
```

The English importer downloads verified public-domain WEB and ASV books from a pinned Midvash revision. The Tagalog importer adds Ang Dating Biblia (1905) and Tagalog Unlocked Literal Bible (2018). Both pipelines validate 66 books and 1,189 chapters, and preserve source/license provenance. Run both importers before validation.

After import, open `index.html` directly. No runtime download, API, server, or internet connection is used. Keep the generated data file and manifest together when copying or packaging Stillword.

**Important:** the importer is committed, but generated full-text data is not yet present in a fresh clone until the import command is run. Do not describe the starter repository as containing complete Bible texts before the validator passes.

## Licensing

The imported WEB and ASV English texts are identified by the upstream dataset as verified public domain. KJV is intentionally excluded from the importer because the pinned source metadata does not yet verify its provenance., with source metadata recorded in `sources/manifest.json`. Copyright status can vary by jurisdiction; review source notes before redistribution. The WEB name is a trademark and the text must not be altered while represented as the World English Bible.

Ang Biblia 2001 is not included; obtain written redistribution permission from the Philippine Bible Society before bundling it. Ang Biblia 1905 must be sourced from a specific, verified edition with a documented redistribution basis before inclusion.

## Personal data

Bookmarks, highlights, notes, theme, and reading preferences are stored in browser local storage. Export a backup before clearing browser data or moving to another browser profile.

## Filipino / Tagalog editions

The v0.2 branch now tracks two redistributable Tagalog candidates: Ang Dating Biblia (1905), identified as public domain subject to exact-source verification, and Tagalog Unlocked Literal Bible (2018), licensed CC BY-SA 4.0. See `docs/TAGALOG-TRANSLATIONS.md` and `sources/tagalog-translations.json` for sources, rights, and import gates.

The Tagalog importer is a build-time step; these texts are not present in a fresh clone until the importers have been run and validation passes. The Tagalog editions must be imported, normalized, and validated before they appear in the reader. Ang Biblia 2001, Magandang Balita Biblia, and Ang Salita ng Diyos remain permission-pending; do not bundle their full text without written authorization.
