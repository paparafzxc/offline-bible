# Stillword — Offline Bible

A portable, static Bible-reading web app. Open `index.html` directly in a modern browser; no backend, package manager, account, CDN, or network connection is required.

## Included in this initial repository commit

- Responsive desktop/mobile interface and light/dark themes
- 66-book Protestant Bible navigation metadata
- WEB, KJV and ASV translation selectors
- Sample text only: Genesis 1:1–5, Psalm 23:1–3, and John 3:16
- Bookmarks, colored highlights, personal notes
- Search across installed sample verses
- Basic reading-plan outlines
- Browser-local storage and JSON backup/restore
- Local translation JSON import for the current session

## Important: this is not yet a complete Bible text library

The repository currently contains only a small set of sample verses. The 66-book catalogue is navigation metadata, not complete chapter content. Do not represent this version as a complete offline Bible.

## Translation and redistribution status

| Translation | Status |
|---|---|
| World English Bible (WEB) | Public domain; preserve the text unaltered and observe WEB trademark requirements |
| King James Version (KJV) | Public domain outside the United Kingdom; verify applicable jurisdiction |
| American Standard Version (ASV, 1901) | Public domain |
| Ang Biblia 1905 | Reported public domain; verify exact source and edition before bundling |
| Ang Biblia 2001 | Copyright Philippine Bible Society; obtain permission before distributing full text |

The application code license does not grant rights to Bible translations. Keep text-source attribution and licensing notices with every imported dataset.

## Run

1. Download or clone this repository.
2. Open `index.html` in Chrome, Edge, Firefox, or another modern browser.
3. Use Settings to export personal data before moving to another browser profile or computer.

Local storage is scoped to the browser profile and may vary for `file://` origins. Backup/restore is provided for portability.

## Dataset format

```json
{
  "code": "WEB",
  "name": "World English Bible",
  "rights": "License and attribution notice",
  "chapters": {
    "Gen.1": {
      "1": "Verse one text",
      "2": "Verse two text"
    },
    "John.3": {
      "16": "Verse text"
    }
  }
}
```

For permanent bundling, add the translation under `window.BIBLE_DATA.translations` in `data/bible-data.js`. The current import control loads a dataset into the current browser session only.

## Next milestone

Acquire and validate complete, legally redistributable text datasets; add persistent translation management, indexed full-text search, chapter completeness checks, and automated browser/offline tests.
