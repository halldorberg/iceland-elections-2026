"""Add to pending.json any IS keys that are missing from EN overlay,
   for specific muni.party prefixes."""
import json, re
from pathlib import Path
from datetime import date

ROOT = Path(r'F:\Claude Projects\iceland-elections')
prefixes = ('grindavik.M.', 'bolungarvik.MMM.', 'floahreppur.FLT.', 'stykkisholmur.IBU.')

IS = json.load(open(ROOT / 'translations' / 'strings_is.json', encoding='utf-8'))
EN = (ROOT / 'js' / 'data' / 'candidates.en.js').read_text(encoding='utf-8')

en_keys = set(re.findall(r'^  "([^"]+)":', EN, re.M))
en_values = dict(re.findall(r'^  "([^"]+)":\s*"((?:[^"\\]|\\.)*)"', EN, re.M))

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
for k, v in IS.items():
    if k == '_occupations':
        continue
    if not any(k.startswith(p) for p in prefixes):
        continue
    if k in existing_keys_today:
        continue
    # Always re-translate agenda items for these lists since source rewritten
    is_agenda = '.agenda.' in k
    if k in en_keys and not is_agenda:
        continue
    existing[today].append({'key': k, 'is': v, 'en': None, 'pl': None})
    added += 1

json.dump(existing, open(PENDING, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'Added {added} new pending entries (total today: {len(existing[today])})')
