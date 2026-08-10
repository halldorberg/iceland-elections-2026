"""Recover party_code by matching candidate name to candidates.js rows."""
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
src = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')
data = json.load(open(ROOT / 'scan_results' / 'ruv_bios.json', encoding='utf-8'))


def find_const_block(s, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', s, re.M)
    if not m: return None
    op = m.end()-1; depth = 0; i = op; in_str = None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == '\\': i+=2; continue
            if c == in_str: in_str = None
            i+=1; continue
        if c in ("'",'"','`'): in_str = c; i+=1; continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return op+1, i
        i+=1


# For each muni, build (muni, party) -> list of (ballot, name) rows
muni_party_rows = {}  # (muni_const, party) -> [(ballot, name), ...]

real_data_m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
munis = [pm.group(2) for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', real_data_m.group(1))]

for muni in munis:
    rng = find_const_block(src, muni)
    if not rng: continue
    cs, ce = rng
    body = src[cs:ce]
    for pm in re.finditer(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', body):
        party = pm.group(1)
        # Walk party block
        i = pm.end()-1; depth = 0; in_str = None
        while i < len(body):
            c = body[i]
            if in_str:
                if c == '\\': i+=2; continue
                if c == in_str: in_str = None
                i+=1; continue
            if c in ("'",'"','`'): in_str = c; i+=1; continue
            if c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0: break
            i+=1
        ptext = body[pm.end()-1:i+1]
        rows = re.findall(r"\[(\d+),\s*'([^']+)'", ptext)
        muni_party_rows[(muni, party)] = [(int(b), n) for b, n in rows]

# Build (muni, name) -> [parties] (for disambiguation)
muni_name_parties = {}
for (muni, party), rows in muni_party_rows.items():
    for ballot, name in rows:
        key = (muni, name)
        muni_name_parties.setdefault(key, []).append((party, ballot))

# Fix ruv_bios entries where party_code doesn't match a real party in candidates.js
fixed = 0
no_match = []
for e in data:
    if not e.get('ruv_id'):
        continue
    muni = e['muni_const']
    pc = e['party_code']
    name = e['name']
    ballot = e['ballot']
    if (muni, pc) in muni_party_rows:
        # Already valid; check if name+ballot matches a row
        rows = muni_party_rows[(muni, pc)]
        if any(b == ballot for b, n in rows):
            continue
    # Try to find by name
    matches = muni_name_parties.get((muni, name), [])
    if not matches:
        # Try by name prefix/suffix
        for (m2, n2), parties in muni_name_parties.items():
            if m2 != muni: continue
            if all(w in n2 for w in name.split()) or all(w in name for w in n2.split()):
                matches = parties
                break
    if not matches:
        no_match.append((muni, pc, ballot, name))
        continue
    # Pick the match with the same ballot if available, else first
    chosen = next((p for p, b in matches if b == ballot), matches[0][0])
    if chosen != pc:
        e['party_code'] = chosen
        fixed += 1

print(f'Fixed: {fixed}')
print(f'Could not match: {len(no_match)}')
for m, p, b, n in no_match[:20]:
    print(f'  {m}.{p}.{b}: {n!r}')

json.dump(data, open(ROOT / 'scan_results' / 'ruv_bios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\nWrote ruv_bios.json')
