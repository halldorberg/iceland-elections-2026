"""Build pending.json with all BLV.MMM (and Sveinn Óskar) keys that
   need re-translation: occupations, bios, interests."""
import json, re, sys, io
from pathlib import Path
from datetime import date

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
STRINGS_IS = json.load(open(ROOT / 'translations' / 'strings_is.json', encoding='utf-8'))

want_prefixes = ('bolungarvik.MMM.list.',)
want_extra_keys = (
    'mosfellsbaer.M.list.1.bio',
)

to_translate = []
for k, v in STRINGS_IS.items():
    if k == '_occupations':
        continue
    if any(k.startswith(p) for p in want_prefixes) or k in want_extra_keys:
        # Restrict to these field types we care about
        if any(k.endswith(s) or s in k for s in ('.bio', '.occupation', '.interests.', '.tagline')):
            to_translate.append((k, v))

to_translate.sort()

PENDING = ROOT / 'translations' / 'pending.json'
existing = {}
if PENDING.exists():
    try:
        existing = json.load(open(PENDING, encoding='utf-8'))
    except Exception:
        existing = {}

today = str(date.today())
existing.setdefault(today, [])
existing_keys_today = {e['key'] for e in existing[today]}
added = 0
for k, v in to_translate:
    if k in existing_keys_today:
        continue
    existing[today].append({'key': k, 'is': v, 'en': None, 'pl': None})
    added += 1

json.dump(existing, open(PENDING, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'Added {added} new pending entries (total today: {len(existing[today])})')
print(f'\nKeys (sample):')
for e in existing[today]:
    val = e['is'][:80].replace('\n', ' ')
    print(f'  {e["key"]:<55s} : {val}')
