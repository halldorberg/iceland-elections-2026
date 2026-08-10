"""Count actual totals from candidates.js for frontpage stats."""
import re

with open('F:/Claude Projects/iceland-elections/js/data/candidates.js', encoding='utf-8') as f:
    text = f.read()

# Count municipalities (unique top-level keys in getMunicipalityPartyData)
# Municipalities are defined in municipalities.js — 61 total, that's fixed

# Count party lists: each party block inside a municipality
# Pattern: a letter key like  A: { or  B: { inside a municipality block
# Better: count ballotOrder occurrences to count candidates, and count party code blocks

# Count candidates: each { ballotOrder: N, name: '...' } entry
candidates = re.findall(r'ballotOrder:\s*\d+', text)
print(f'Total candidates: {len(candidates)}')

# Count party lists: look for party code objects  e.g.  A: { tagline or  B: { tagline or candidates: [
# A party block starts with a single letter key followed by {
party_blocks = re.findall(r'\b([A-Z]{1,4}):\s*\{', text)
# Filter to just known party codes (1-4 uppercase letters)
# Remove false positives - we need ones that are actually party entries
# Better: count from the structure
party_sections = re.findall(r'\n\s{4,8}([A-Z]{1,4}):\s*\{[^}]*?candidates:', text, re.DOTALL)
print(f'Party lists (with candidates array): {len(party_sections)}')

# Even simpler - count 'candidates: [' occurrences
cand_arrays = text.count('candidates: [')
print(f'candidates: [ occurrences: {cand_arrays}')

# Count by looking for party entries with actual structure
# Each municipality has a set of party letter codes
import ast

# Extract via JSON-like approach - find all "X: {" inside getMunicipalityPartyData
# Count unique municipality+party combos
muni_party = re.findall(r"case '([^']+)':[^{]*?\{([^}]*?)\}", text[:500])

# Simpler: use the excel ground truth
import json
with open('F:/Claude Projects/iceland-elections/scripts/excel_ground_truth.json', encoding='utf-8') as f:
    excel = json.load(f)

excel_munis = len(excel)
excel_lists = sum(len(v) for v in excel.values())
excel_cands = sum(len(c) for v in excel.values() for c in v.values())
print(f'\nExcel ground truth:')
print(f'  Municipalities with candidates: {excel_munis}')
print(f'  Total lists: {excel_lists}')
print(f'  Total candidates: {excel_cands}')
print(f'\nWith 7 obundnar + 4 sjalkjort = 61 total municipalities')
print(f'Stats to show on frontpage:')
print(f'  Municipalities: 61')
print(f'  Party lists: {excel_lists}')
print(f'  Candidates: {excel_cands}')
