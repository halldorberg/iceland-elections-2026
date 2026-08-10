// Wrap each data file in a try/catch to find syntax errors
import { readFileSync } from 'fs';
import { pathToFileURL } from 'url';

const ROOT = 'F:/Claude Projects/iceland-elections/';

const modules = [
  'js/data/municipalities.js',
  'js/data/parties.js',
  'js/data/results2022.js',
  'js/data/polls.js',
  'js/data/cleavages.js',
  'js/data/party_slugs.js',
];

for (const mod of modules) {
  try {
    // Strip export keyword so we can eval
    const src = readFileSync(ROOT + mod, 'utf8').replace(/^﻿/, ''); // strip BOM
    // Check for common issues
    const fn = new Function(src.replace(/^export\s+(const|function|let|var)\s+/gm, '$1 '));
    fn();
    console.log(`OK: ${mod}`);
  } catch(e) {
    console.log(`ERROR: ${mod} → ${e.message.split('\n')[0]}`);
  }
}
