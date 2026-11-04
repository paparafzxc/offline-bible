# G-word Windows portable desktop build

G-word is packaged as a Windows x64 portable executable using Electron. The desktop wrapper loads the existing local `index.html` and `data/bible-data.js`; it does not fetch Bible content or require a web server at runtime.

## Build locally on Windows

Requirements: Windows 10/11 x64, Node.js 22, and internet access for the one-time dependency install/build.

From the repository root in PowerShell:

```powershell
npm install
npm run check:desktop
npm run dist:portable
```

Output: `release/G-word-Portable.exe`.

Run the executable from a writable folder or USB drive. In portable mode, Chromium application data (including localStorage) is stored in a sibling folder named `G-word-data`. Keep that folder beside the executable to preserve bookmarks, highlights, notes, theme, and reading position. Back it up with the executable.

## Build through GitHub Actions

Open the repository Actions tab, choose **Build G-word Portable for Windows**, then select **Run workflow**. Download the `G-word-Portable-Windows-x64` artifact when the job succeeds. Relevant pushes to this branch also trigger the workflow.

## Security and runtime

- Node integration is disabled in the renderer.
- Context isolation and Chromium sandboxing are enabled.
- The preload exposes no Node.js APIs.
- In-app navigation to other pages is blocked; HTTP(S) popup links are handed to the system browser.
- The Bible reader and data bundle are local; no local server is needed.

## Known limitations

- The repository currently contains starter/demo passages only. The executable is not a complete Bible library until full licensed corpus data is imported and the library validator passes.
- This first build targets Windows x64.
- The executable is not code-signed; Windows SmartScreen may show an unknown-publisher warning.
- Portable mode writes user data beside the executable. Do not run it from a protected, non-writable folder such as Program Files.
- Browser localStorage is not automatically imported. Use the reader's Settings & Data backup export/import feature to transfer existing study data.
- The workflow produces a CI artifact, not a published GitHub Release.

## Release acceptance checks

1. GitHub Actions succeeds and produces `G-word-Portable.exe`.
2. It launches on a clean Windows x64 PC without Node.js installed.
3. The reader and local data load with networking disabled.
4. A bookmark, highlight, note, and theme persist after restart.
5. The `G-word-data` folder preserves settings when moved with the executable.
6. Export/import of an existing browser backup is verified.
