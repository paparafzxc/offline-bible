# G-word — Offline Bible

G-word is an offline Bible reader with a folder-portable browser version and a Windows desktop packaging target.

## Run the browser version

Open `index.html` directly in a modern browser. The app is designed to run without a local server. Keep the `data` folder beside `index.html`.

## Windows portable executable

This branch includes an Electron wrapper that packages the existing reader as `G-word-Portable.exe`.

Requirements for building: Windows 10/11 x64, Node.js 22, and internet access for the one-time dependency installation.

```powershell
npm install
npm run check:desktop
npm run dist:portable
```

The executable is written to `release/G-word-Portable.exe`. It can be copied to a writable folder or USB drive. Keep the generated `G-word-data` folder beside the executable to preserve local study data. See [docs/DESKTOP-PORTABLE.md](docs/DESKTOP-PORTABLE.md) for the build workflow, storage behavior, security settings, and release checks.

A Windows GitHub Actions workflow is also available under **Actions → Build G-word Portable for Windows**.

## Complete offline text library

The initial `data/bible-data.js` is starter/demo content. To build a complete locally bundled public-domain corpus, run once from the repository root on a computer with internet access:

```powershell
py -3 -m pip install datasets huggingface_hub
py -3 scripts/import_public_domain_bibles.py
py -3 scripts/import_tagalog_bibles.py
py -3 scripts/validate_library.py
```

The English importer downloads public-domain WEB and ASV books from a pinned upstream revision. The Tagalog importer adds Ang Dating Biblia (1905) and Tagalog Unlocked Literal Bible (2018), subject to the source and license checks documented in [docs/TAGALOG-TRANSLATIONS.md](docs/TAGALOG-TRANSLATIONS.md). Generated full-text data is not present in a fresh clone until import and validation have completed successfully. Do not describe the starter repository or its executable as containing complete Bible texts before the validator passes.

After import, the app uses the bundled local data. No runtime download, API, server, or internet connection is required.

## Licensing

Review source notes and license metadata before redistributing any generated corpus. Ang Biblia 2001 and Magandang Balita Biblia are not included unless written redistribution permission is obtained from the Philippine Bible Society. Never infer redistribution permission from an online copy being accessible.

## Personal data

Bookmarks, highlights, notes, theme, and reading preferences are stored locally. Export a backup before clearing browser data or moving between browser profiles. The portable desktop build keeps its application data in the sibling `G-word-data` folder; keep that folder when moving the executable.
