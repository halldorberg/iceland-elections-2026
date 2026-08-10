#!/usr/bin/env python3
"""
Fresh scrape of all candidate lists from island.is/__NEXT_DATA__.
Saves to island_candidates_fresh.json
"""
import json, re, urllib.request, sys

URL = 'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'

print('Fetching page...', file=sys.stderr)
req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode('utf-8')

# Extract __NEXT_DATA__
m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
if not m:
    print('ERROR: __NEXT_DATA__ not found', file=sys.stderr)
    sys.exit(1)

data = json.loads(m.group(1))
apollo = data['props']['pageProps']['apolloState']
print(f'Apollo state keys: {len(apollo)}', file=sys.stderr)


def get_names(html_ref):
    node = apollo.get(html_ref)
    if not node or 'document' not in node:
        return []
    names = []
    def walk(n):
        if not n:
            return
        if n.get('nodeType') == 'text' and n.get('value', '').strip():
            names.append(n['value'].strip())
        for child in n.get('content', []):
            walk(child)
    walk(node['document'])
    return names


result = {}

# Multi-list municipalities (accordionItems >= 2)
for acc in apollo.values():
    if acc.get('__typename') != 'AccordionSlice':
        continue
    items = acc.get('accordionItems', [])
    if len(items) < 2:
        continue
    muni = acc.get('title', '').strip()
    if not muni:
        continue
    if muni not in result:
        result[muni] = {}
    for item_ref in items:
        item = apollo.get(item_ref.get('__ref', ''))
        if not item or item.get('__typename') != 'OneColumnText':
            continue
        candidates = []
        for c_ref in item.get('content', []):
            candidates.extend(get_names(c_ref.get('__ref', '')))
        result[muni][item['title']] = candidates

# Single-list municipalities (sjálfkjörið etc.)
FAQ_SKIP = ['kýs', 'kjósa', 'Utankjör', 'Framboðs', 'skilríki', 'Aðstoð',
            'Kærur', 'Meðmæla', 'Óbundnar', 'forsíðu', 'Efni', 'Grindavík']
for acc in apollo.values():
    if acc.get('__typename') != 'AccordionSlice':
        continue
    items = acc.get('accordionItems', [])
    if len(items) != 1:
        continue
    title = acc.get('title', '').strip()
    if not title or any(title.startswith(f) or title == f for f in FAQ_SKIP):
        continue
    item = apollo.get(items[0].get('__ref', ''))
    if not item or item.get('__typename') != 'OneColumnText':
        continue
    candidates = []
    for c_ref in item.get('content', []):
        candidates.extend(get_names(c_ref.get('__ref', '')))
    if candidates:
        if title not in result:
            result[title] = {}
        result[title][item['title']] = candidates

# Stats
total_lists = sum(len(v) for v in result.values())
total_cands = sum(len(c) for v in result.values() for c in v.values())
print(f'Municipalities: {len(result)}', file=sys.stderr)
print(f'Lists: {total_lists}', file=sys.stderr)
print(f'Candidates: {total_cands}', file=sys.stderr)

out_path = 'island_candidates_fresh.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'Saved to {out_path}', file=sys.stderr)
