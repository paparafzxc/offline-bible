'use strict';
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const required = ['index.html', 'data/bible-data.js', 'electron/main.cjs', 'electron/preload.cjs'];
const missing = required.filter(file => !fs.existsSync(path.join(root, file)));
if (missing.length) {
  console.error('Desktop packaging preflight failed. Missing: ' + missing.join(', '));
  process.exit(1);
}
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
if (!html.includes('<script src="data/bible-data.js"></script>')) {
  console.error('Desktop packaging preflight failed: local Bible data script reference not found.');
  process.exit(1);
}
console.log('Desktop packaging preflight passed: entry point and local Bible data bundle found.');
