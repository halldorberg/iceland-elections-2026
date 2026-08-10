"""Find every IS string that's missing from strings_en.json or strings_pl.json
and force them into pending.json for translation."""
import json, os
from pathlib import Path
from datetime import date

ROOT = Path(r'F:\Claude Projects\iceland-elections')
isd = json.load(open(ROOT / 'translations' / 'strings_is.json', encoding='utf-8'))
en  = json.load(open(ROOT / 'translations' / 'strings_en.json', encoding='utf-8'))
pl  = json.load(open(ROOT / 'translations' / 'strings_pl.json', encoding='utf-8'))

# Skip the _occupations bucket
occ_is = isd.get('_occupations', {})
occ_en = en.get('_occupations', {})
occ_pl = pl.get('_occupations', {})

main_is = {k: v for k, v in isd.items() if k != '_occupations'}

missing = []
for k, v in main_is.items():
    en_v = en.get(k)
    pl_v = pl.get(k)
    if not en_v or not pl_v:
        missing.append({'key': k, 'is': v, 'en': en_v if en_v else None, 'pl': pl_v if pl_v else None})

# Also check occupations
for occ in occ_is.keys():
    en_o = occ_en.get(occ)
    pl_o = occ_pl.get(occ)
    if not en_o or not pl_o:
        missing.append({'key': f'_occ:{occ}', 'is': occ, 'en': en_o if en_o else None, 'pl': pl_o if pl_o else None})

print(f'missing translations: {len(missing)}')
print(f'  bios: {sum(1 for m in missing if m["key"].endswith(".bio"))}')
print(f'  occupations: {sum(1 for m in missing if m["key"].startswith("_occ:"))}')

# Write to pending.json
PENDING = ROOT / 'translations' / 'pending.json'
pending = json.load(open(PENDING, encoding='utf-8')) if PENDING.exists() else {}
today = str(date.today())
pending.setdefault(today, [])
existing_keys = {e['key'] for e in pending[today]}
added = 0
for m in missing:
    if m['key'] not in existing_keys:
        pending[today].append(m)
        added += 1
json.dump(pending, open(PENDING, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'wrote {added} new entries to pending.json')
