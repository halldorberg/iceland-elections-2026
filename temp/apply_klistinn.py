"""Apply K-listinn (BLV.MMM) candidate photos + bios to candidates.js
   AND merge facts into scan_results/ruv_bios.json for matching candidates."""
import json, re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
CJS = ROOT / 'js' / 'data' / 'candidates.js'
DATA = json.load(open(ROOT / 'temp' / 'klistinn_data.json', encoding='utf-8'))

txt = CJS.read_text(encoding='utf-8')

# Find the MMM block
m = re.search(r'  MMM:\s*\{', txt)
mmm_start = m.start()
# Walk to matching closing brace
i = m.end() - 1
depth = 0
in_str = None
while i < len(txt):
    c = txt[i]
    if in_str:
        if c == '\\':
            i += 2; continue
        if c == in_str:
            in_str = None
        i += 1; continue
    if c in ("'", '"', '`'):
        in_str = c; i += 1; continue
    if c == '{':
        depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0:
            break
    i += 1
mmm_end = i + 1
mmm_text = txt[mmm_start:mmm_end]
print(f'MMM block: {mmm_end - mmm_start} chars')

# Build replacement list rows
lookup = {d['ballot']: d for d in DATA}

def js_str(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")

def js_arr_strs(arr):
    return ', '.join(f"'{js_str(s)}'" for s in arr)


new_rows = []
for n in range(1, 15):
    d = lookup[n]
    name = d['name']
    occ = d['occupation']
    photo = f"images/candidates/{d['photo']}"
    bio = d['bio']
    interests = d.get('interests') or []
    interests_js = '[' + js_arr_strs(interests) + ']' if interests else 'null'
    heimild_js = "[{ url: 'https://www.klistinn.is/', label: 'klistinn.is' }, { url: 'https://bb.is/2026/03/bolungavik-mattur-manna-og-meyja-birtir-frambodslista/', label: 'bb.is' }]"
    extra = '\n      ' if n == 14 else ''  # last row alignment matches existing
    row = f"      [{n}, '{js_str(name)}', '{js_str(occ)}', '{photo}', {{ age: null, bio: '{js_str(bio)}', interests: {interests_js}, social: null, heimild: {heimild_js}, news: [] }}],"
    new_rows.append(row)

# Add a blank line before the final row to match existing pattern
# (existing files have a blank line before [14, ...])
final_block = '\n'.join(new_rows[:-1]) + '\n    \n' + new_rows[-1]

# Replace inside the MMM block: from "    list: [" through closing "    ]," before the "  },"
# Find list: [ ... ]  of MMM
list_m = re.search(r'(    list:\s*\[)(.*?)(\n    \],\s*\n  \})', mmm_text, re.S)
if not list_m:
    print('ERROR: could not find list pattern in MMM block')
    sys.exit(1)

new_list_block = list_m.group(1) + '\n' + final_block + list_m.group(3)
new_mmm = mmm_text[:list_m.start()] + new_list_block + mmm_text[list_m.end():]

txt2 = txt[:mmm_start] + new_mmm + txt[mmm_end:]
print(f'New file size delta: {len(txt2) - len(txt)}')

CJS.write_text(txt2, encoding='utf-8')
print('Wrote candidates.js')

# ─── RUV bio drafts merge ─────────────────────────────────────
RUV = ROOT / 'scan_results' / 'ruv_bios.json'
ruv = json.load(open(RUV, encoding='utf-8'))
print(f'\nRUV entries: {len(ruv)}')

# Find RUV entries for muni_const=BLV, party_code=MMM
matches = [(i, e) for i, e in enumerate(ruv)
           if e.get('muni_const') == 'BLV' and e.get('party_code') == 'MMM']
print(f'BLV.MMM RUV entries: {len(matches)}')

updated = 0
for i, e in matches:
    name = e.get('name', '')
    # Find matching candidate by name (loose match: first+last name overlap)
    match = None
    name_norm = name.lower()
    for d in DATA:
        d_name = d['name'].lower()
        # Match if all words of d_name occur in name or vice versa
        if d_name == name_norm or all(w in name_norm for w in d_name.split()) or all(w in d_name for w in name_norm.split()):
            match = d
            break
    if not match:
        # Try first+last match
        for d in DATA:
            d_first = d['name'].split()[0].lower()
            d_last = d['name'].split()[-1].lower()
            if d_first in name_norm and d_last in name_norm:
                match = d
                break
    if not match:
        print(f'  no match: {name}')
        continue
    # Replace the new_bio (and old_bio for context) with the source-faithful version
    new_bio = match['bio']
    # Append RUV-only facts that we may already have generated, if they don't duplicate
    old_new = e.get('new_bio') or ''
    # Look for an "Í svörum sínum á kosningaprófi RÚV" sentence in the previous draft
    ruv_para_m = re.search(r'(Í svörum sínum á kosningaprófi RÚV[^\n]*?)(?:\n\n|$)', old_new, re.S)
    extra_ruv = ''
    if ruv_para_m:
        # Try to keep RUV-derived sentences as a 2nd paragraph
        # but only the parts after "Í svörum sínum á kosningaprófi RÚV"
        idx = old_new.find('Í svörum sínum á kosningaprófi RÚV')
        if idx > 0:
            extra_ruv = '\n\n' + old_new[idx:].strip()
    e['new_bio'] = new_bio + extra_ruv
    e['_klistinn_merged'] = True
    updated += 1
    print(f'  merged: {name} (ballot {match["ballot"]})')

print(f'\nUpdated {updated} RUV bios')
json.dump(ruv, open(RUV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Wrote ruv_bios.json')
