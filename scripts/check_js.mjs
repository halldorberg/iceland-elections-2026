// Syntax check: try to parse key data files using Node's module resolution
import { readFileSync } from 'fs';

function checkBraces(content, filename) {
  let depth = 0;
  for (const ch of content) {
    if (ch === '{') depth++;
    else if (ch === '}') depth--;
  }
  console.log(`${filename}: brace depth at end = ${depth}`);
}

const files = [
  'js/data/municipalities.js',
  'js/data/parties.js',
  'js/data/results2022.js',
  'js/data/polls.js',
  'js/data/cleavages.js',
  'js/data/party_slugs.js',
  'js/municipality.js',
];

const ROOT = 'F:/Claude Projects/iceland-elections/';
for (const f of files) {
  const content = readFileSync(ROOT + f, 'utf8');
  checkBraces(content, f);
}
console.log('All checked.');
