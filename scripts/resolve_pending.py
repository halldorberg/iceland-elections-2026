#!/usr/bin/env python3
"""
Resolve all pending translations manually and merge into strings_en/pl.json.
Occupation entries are already covered by the _occupations lookup — just mark done.
Taglines/agenda items are translated inline here.
"""
import json
from pathlib import Path

ROOT       = Path(__file__).parent.parent
PENDING    = ROOT / 'translations' / 'pending.json'
STRINGS_EN = ROOT / 'translations' / 'strings_en.json'
STRINGS_PL = ROOT / 'translations' / 'strings_pl.json'

# Manual translations for non-occupation keys
TRANSLATIONS = {
    # ── Snæfellsbær D listi ──────────────────────────────────────────────────
    'snaefellsbaer.D.tagline': {
        'en': 'D-list — Independence Party — Snæfellsbær 2026',
        'pl': 'Lista D — Partia Niepodległości — Snæfellsbær 2026',
    },
    'snaefellsbaer.D.agenda.0.title': {'en': 'Community',   'pl': 'Społeczność'},
    'snaefellsbaer.D.agenda.0.text':  {
        'en': 'Strengthen community and services on Snæfellsnes.',
        'pl': 'Wzmocnienie społeczności i usług na Snæfellsnes.',
    },
    'snaefellsbaer.D.agenda.1.title': {'en': 'Employment',  'pl': 'Zatrudnienie'},
    'snaefellsbaer.D.agenda.1.text':  {
        'en': 'Boost business and innovation in the area.',
        'pl': 'Wspieranie działalności gospodarczej i innowacji w regionie.',
    },
    'snaefellsbaer.D.agenda.2.title': {'en': 'Environment', 'pl': 'Środowisko'},
    'snaefellsbaer.D.agenda.2.text':  {
        'en': 'Sustainable development and protection of the Snæfellsnes nature.',
        'pl': 'Zrównoważony rozwój i ochrona przyrody Snæfellsnes.',
    },

    # ── Kjósarhreppur KJA ───────────────────────────────────────────────────
    'kjosarhreppur.KJA.tagline': {
        'en': 'Residents of Kjós — A-list of Kjósarhreppur 2026',
        'pl': 'Mieszkańcy Kjós — Lista A Kjósarhreppur 2026',
    },

    # ── Hörgársveit HGG (G listi — Grósku) ──────────────────────────────────
    'horgarsv.HGG.tagline': {
        'en': 'G list — Greens',
        'pl': 'Lista G — Zieloni',
    },
    'horgarsv.HGG.agenda.0.title': {'en': 'Environment',    'pl': 'Środowisko'},
    'horgarsv.HGG.agenda.0.text':  {
        'en': 'Environmental protection and sustainable development.',
        'pl': 'Ochrona środowiska i zrównoważony rozwój.',
    },
    'horgarsv.HGG.agenda.1.title': {'en': 'Green party',    'pl': 'Zielona partia'},
    'horgarsv.HGG.agenda.1.text':  {
        'en': 'Green solutions and sustainable communities.',
        'pl': 'Zielone rozwiązania i zrównoważone społeczności.',
    },
    'horgarsv.HGG.agenda.2.title': {'en': 'Cooperation',    'pl': 'Współpraca'},
    'horgarsv.HGG.agenda.2.text':  {
        'en': 'Cooperation and community development.',
        'pl': 'Współpraca i rozwój społeczności.',
    },
}

# Occupation translation (already in _occupations, but mark pending done)
OCC_EN = 'Candidate'
OCC_PL = 'Kandydat'


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'Saved {path}')


pending   = load_json(PENDING)
strings_en = load_json(STRINGS_EN)
strings_pl = load_json(STRINGS_PL)

all_entries = []
for day_entries in pending.values():
    all_entries.extend(day_entries)

print(f'Total pending entries: {len(all_entries)}')

for entry in all_entries:
    key = entry['key']
    is_val = entry['is']

    if key.endswith('.occupation'):
        # Already covered by _occupations lookup — just fill values
        entry['en'] = OCC_EN
        entry['pl'] = OCC_PL
        # No need to add to strings files since _occupations handles it
    elif key in TRANSLATIONS:
        entry['en'] = TRANSLATIONS[key]['en']
        entry['pl'] = TRANSLATIONS[key]['pl']
        strings_en[key] = TRANSLATIONS[key]['en']
        strings_pl[key] = TRANSLATIONS[key]['pl']
        print(f'  Translated: {key}')
    else:
        print(f'  WARNING: no translation for key: {key} (is: {is_val!r})')

save_json(STRINGS_EN, strings_en)
save_json(STRINGS_PL, strings_pl)

# Also fix the HGG tagline Icelandic value in pending (Grænsku → Grósku)
for entry in all_entries:
    if entry['key'] == 'horgarsv.HGG.tagline':
        entry['is'] = 'G listi — Grósku'

# Clear fully-translated entries from pending
cleaned = {}
for day, entries in pending.items():
    remaining = [e for e in entries if e.get('en') is None or e.get('pl') is None]
    if remaining:
        cleaned[day] = remaining

save_json(PENDING, cleaned if cleaned else {})
print(f'\nPending cleared. Remaining untranslated: {sum(len(v) for v in cleaned.values())}')
