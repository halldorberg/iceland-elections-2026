"""Fix the 2 mislabeled entries in ruv_bios.json."""
import json
from pathlib import Path

ROOT = Path(r'F:\Claude Projects\iceland-elections')
RUV = ROOT / 'scan_results' / 'ruv_bios.json'
data = json.load(open(RUV, encoding='utf-8'))

fixed = 0
for e in data:
    rid = e.get('ruv_id', '') or ''
    parts = rid.split('-')
    if len(parts) != 3:
        continue
    muni_short, party_actual, ballot_actual = parts[0], parts[1], parts[2]
    try:
        ballot_actual = int(ballot_actual)
    except ValueError:
        continue

    # If the embedded party/ballot doesn't match current fields, re-categorize.
    if e.get('party_code') != party_actual or e.get('ballot') != ballot_actual:
        print(f'  ruv_id={rid} → re-categorizing from '
              f'({e.get("muni_const")},{e.get("party_code")},{e.get("ballot")}) '
              f'to (?,{party_actual},{ballot_actual})')
        e['party_code'] = party_actual
        e['ballot'] = ballot_actual
        fixed += 1

print(f'\nFixed {fixed} entries')
json.dump(data, open(RUV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Wrote ruv_bios.json')
