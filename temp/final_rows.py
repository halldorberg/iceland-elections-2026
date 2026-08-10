"""Build final candidates.js list rows for Vinir Mos L."""
import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
cands = json.load(open(ROOT / 'temp' / 'vinirmos_processed.json', encoding='utf-8'))
by_ballot = {c['ballot']: c for c in cands}

def title_case_is(s):
    """Icelandic sentence-case: only first word capitalized."""
    s = s.strip()
    if not s: return s
    if s.isupper():
        s = s.lower()
        # Capitalize first letter
        return s[0].upper() + s[1:]
    return s

def js_str(s):
    return s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')

NAME_FIX = {
    7: 'Katarzyna Krystyna Krolikowska',
    18: 'Kristín Eva Ólafsdóttir',
    4: 'Guðrún Elísa Sævarsdóttir (Gunna Lísa)',  # remove double space
}

HEIMILD = "[{ url: 'https://www.vinirmos.is/frambjodendur-1', label: 'vinirmos.is' }]"

def make_row(c):
    ballot = c['ballot']
    name = NAME_FIX.get(ballot, c['name']).strip()
    occ = title_case_is(c['occupation'])
    img = c.get('image_path')
    img_part = f", 'images/candidates/{img.split('/')[-1]}'" if img else ''
    bio = c.get('bio_3p', '').strip()
    if bio:
        # collapse internal whitespace, keep single spaces
        bio = ' '.join(bio.split())
        details = f", {{ age: null, bio: '{js_str(bio)}', interests: null, social: null, heimild: {HEIMILD}, news: [] }}"
    else:
        # No bio, but include heimild via a slim object
        details = f", {{ age: null, bio: null, interests: null, social: null, heimild: {HEIMILD}, news: [] }}"
    return f"      [{ballot}, '{js_str(name)}', '{js_str(occ)}'{img_part}{details}],"

# Existing Orri row (no page data)
ORRI_ROW = "      [17, 'Orri Grétar Valgeirsson', 'Óþekkt'],"

rows = []
for n in range(1, 23):
    if n == 17:
        rows.append(ORRI_ROW)
    elif n in by_ballot:
        rows.append(make_row(by_ballot[n]))

result = '\n'.join(rows)
(ROOT / 'temp' / 'vinirmos_rows.txt').write_text(result + '\n', encoding='utf-8')
print(result[:3000])
print(f'\n... total {len(rows)} rows, wrote temp/vinirmos_rows.txt')
