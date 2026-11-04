# Bible data format (v0.2)

## Runtime constraint

Stillword is opened directly from a folder. Do not load local JSON with `fetch()` at runtime: browsers may block it under `file://`. The build pipeline emits JavaScript files that register local data on `window.BIBLE_LIBRARY`. The reader loads those files through local script elements.

## Canonical source format

Each translation source is a UTF-8 JSON file with this shape:

```json
{
  "schemaVersion": 2,
  "translation": {
    "code": "WEB",
    "name": "World English Bible",
    "language": "en",
    "edition": "2020 stable text",
    "source": "https://ebible.org/engwebp/",
    "license": "Public domain",
    "rights": "Preserve the text unaltered; WEB is a trademark.",
    "retrieved": "YYYY-MM-DD"
  },
  "books": [
    {
      "osis": "Gen",
      "name": "Genesis",
      "chapters": [
        {
          "number": 1,
          "verses": [
            { "number": "1", "text": "In the beginning..." }
          ]
        }
      ]
    }
  ]
}
```

Verse numbers are strings to preserve suffixes and nonstandard verse labels. Preserve source text exactly; do not silently normalize punctuation, spelling, or capitalization.

## Generated shard contract

Each generated file registers exactly one book:

```js
window.BIBLE_LIBRARY = window.BIBLE_LIBRARY || {};
window.BIBLE_LIBRARY.WEB = window.BIBLE_LIBRARY.WEB || {};
window.BIBLE_LIBRARY.WEB.Gen = {
  "osis": "Gen",
  "chapters": {
    "1": {
      "1": "In the beginning..."
    }
  }
};
```

The app must treat translation text as immutable source content. User annotations belong in localStorage and must be keyed by translation + OSIS book + chapter + verse so they remain distinct between translations.

## Provenance

Every source translation must have an entry in `sources/manifest.json` with:
- exact edition and language;
- original source URL and upstream project/revision;
- license or written permission evidence;
- retrieval date;
- SHA-256 of the untouched source file;
- any conversion notes.

Never mark a translation distributable based only on the fact that it can be downloaded.
