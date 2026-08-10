"""Add NEW entries to ruv_bios.json for the 8 GRN.M candidates without
   RÚV kosningapróf draft, using their klistinn-style FB intro as new_bio."""
import json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
DATA = json.load(open(ROOT / 'temp' / 'grn_m_candidates_final.json', encoding='utf-8'))
RUV = ROOT / 'scan_results' / 'ruv_bios.json'
ruv = json.load(open(RUV, encoding='utf-8'))

# Existing GRN.M ballots
existing_ballots = {e['ballot'] for e in ruv if e.get('muni_const') == 'GRN' and e.get('party_code') == 'M'}
print(f'GRN.M existing RUV ballots: {sorted(existing_ballots)}')

added = 0
for d in DATA:
    if d['ballot'] in existing_ballots:
        continue
    entry = {
        'ruv_id': None,  # no RÚV survey for this candidate
        'muni_const': 'GRN',
        'party_code': 'M',
        'ballot': d['ballot'],
        'name': d['name'],
        'js_name': d['name'],
        'muni_name': 'Grindavík',
        'old_bio': None,
        'new_bio': d['bio'],
        'fact_check': [],
        'sources': [
            {'url': 'https://www.facebook.com/midflokkurinngrindavik', 'label': 'facebook.com/midflokkurinngrindavik'},
        ],
        'ruv_profile_url': None,
        '_source': 'fb_only',
    }
    ruv.append(entry)
    added += 1
    print(f'  + {d["name"]} (ballot {d["ballot"]})')

print(f'\nAdded {added} new GRN.M entries')
json.dump(ruv, open(RUV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'Wrote ruv_bios.json (now {len(ruv)} total entries)')
