"""Apply GRN.M photos+bios to candidates.js (replace placeholder rows 2-11),
   then merge into ruv_bios.json drafts."""
import json, re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
CJS = ROOT / 'js' / 'data' / 'candidates.js'
DATA = json.load(open(ROOT / 'temp' / 'grn_m_candidates_final.json', encoding='utf-8'))

txt = CJS.read_text(encoding='utf-8')

# Find the GRN.M block within const GRN = { ... M: { ... }, ... };
m = re.search(r'^const GRN\s*=\s*\{', txt, re.M)
assert m, 'GRN const not found'
grn_start = m.end() - 1  # position of '{'
# Walk to matching close
depth = 0
i = grn_start
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
grn_end = i + 1
grn_text = txt[grn_start:grn_end]

# Inside GRN, find the M: { ... } block (after agenda)
mb = re.search(r'\n  M:\s*\{', grn_text)
assert mb, 'M block not found'
m_start = mb.end() - 1
depth = 0; i = m_start; in_str = None
while i < len(grn_text):
    c = grn_text[i]
    if in_str:
        if c == '\\': i+=2; continue
        if c == in_str: in_str = None
        i += 1; continue
    if c in ("'", '"', '`'): in_str = c; i += 1; continue
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: break
    i += 1
m_end = i + 1
m_text = grn_text[m_start:m_end]

# Find the list array within M block
lm = re.search(r'(    list:\s*\[)(.*?)(\n    \],\s*\n  \})', m_text, re.S)
assert lm, 'list block not found in GRN.M'

old_list_body = lm.group(2)
# Parse existing rows to retain row 1 (Magnús Már) unchanged
# Rows look like:  [N, 'Name', 'Occ' (optional), null/path, { ... }]?
# We'll parse just the row-1 line(s) and keep them; replace rows 2-11.

# Split rows by lines starting with [<digit>
lines = old_list_body.splitlines()
row1_lines = []
in_row1 = False
depth_b = 0; in_str = None
captured = False
for line in lines:
    s = line.lstrip()
    if not captured and s.startswith('[1,'):
        in_row1 = True
    if in_row1:
        row1_lines.append(line)
        # Count brackets and braces to detect end (where ],)
        for ch in line:
            if in_str:
                if ch == '\\': pass
                elif ch == in_str: in_str = None
                continue
            if ch in ("'", '"', '`'): in_str = ch; continue
            if ch == '[': depth_b += 1
            elif ch == ']':
                depth_b -= 1
                if depth_b == 0:
                    captured = True
        if captured:
            break

row1_text = '\n'.join(row1_lines)
print(f'Row 1 captured: {len(row1_lines)} lines')

def js_str(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")

def js_arr_strs(arr):
    return ', '.join(f"'{js_str(s)}'" for s in arr)


new_rows = [row1_text]
for d in DATA:
    n = d['ballot']
    name = d['name']
    occ = d['occupation']
    photo = f"images/candidates/{d['photo']}"
    bio = d['bio']
    interests = d.get('interests') or []
    interests_js = '[' + js_arr_strs(interests) + ']' if interests else 'null'
    heimild_js = "[{ url: 'https://www.facebook.com/midflokkurinngrindavik', label: 'facebook.com/midflokkurinngrindavik' }]"
    row = f"      [{n}, '{js_str(name)}', '{js_str(occ)}', '{photo}', {{ age: null, bio: '{js_str(bio)}', interests: {interests_js}, social: null, heimild: {heimild_js}, news: [] }}],"
    new_rows.append(row)

# Existing list had a blank line before [11, ...] (separator pattern). Mirror that.
final_block = '\n' + '\n'.join(new_rows[:-1]) + '\n    \n' + new_rows[-1]
new_list_block = lm.group(1) + final_block + lm.group(3)
new_m_text = m_text[:lm.start()] + new_list_block + m_text[lm.end():]
new_grn_text = grn_text[:m_start] + new_m_text + grn_text[m_end:]
new_txt = txt[:grn_start] + new_grn_text + txt[grn_end:]

CJS.write_text(new_txt, encoding='utf-8')
print(f'Wrote candidates.js (delta {len(new_txt)-len(txt):+d} chars)')

# ─── RUV merge ─────────────────────────────────────────────
RUV = ROOT / 'scan_results' / 'ruv_bios.json'
ruv = json.load(open(RUV, encoding='utf-8'))
matches = [(i, e) for i, e in enumerate(ruv) if e.get('muni_const') == 'GRN' and e.get('party_code') == 'M']
print(f'\nGRN.M RUV entries: {len(matches)}')

updated = 0
created = 0
for i, e in matches:
    name = e.get('name', '').lower()
    match = None
    for d in DATA:
        d_name = d['name'].lower()
        if all(w in name for w in d_name.split()) or all(w in d_name for w in name.split()):
            match = d; break
    if not match:
        for d in DATA:
            d_first = d['name'].split()[0].lower()
            d_last  = d['name'].split()[-1].lower()
            if d_first in name and d_last in name:
                match = d; break
    if not match:
        print(f'  no match: {e.get("name")}')
        continue
    new_bio = match['bio']
    old_new = e.get('new_bio') or ''
    extra = ''
    idx = old_new.find('Í svörum sínum á kosningaprófi RÚV')
    if idx > 0:
        extra = '\n\n' + old_new[idx:].strip()
    e['new_bio'] = new_bio + extra
    e['_grn_m_merged'] = True
    updated += 1
    print(f'  merged: {e.get("name")} (ballot {match["ballot"]})')

print(f'\nUpdated {updated} RUV bios')
json.dump(ruv, open(RUV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Wrote ruv_bios.json')
