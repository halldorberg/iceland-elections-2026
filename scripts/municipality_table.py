#!/usr/bin/env python3
"""Generate overview table of all 61 municipalities."""
import re, json

# ── Parse municipalities.js ──────────────────────────────────────────────────
with open('../js/data/municipalities.js', encoding='utf-8') as f:
    muni_src = f.read()

# Extract each municipality object: id, name, partyIds
munis = []
for m in re.finditer(
    r'\{\s*id\s*:\s*[\'"](\w+)[\'"].*?name\s*:\s*[\'"]([^\'"]+)[\'"].*?partyIds\s*:\s*(\[[^\]]*\])',
    muni_src, re.DOTALL
):
    muni_id = m.group(1)
    name = m.group(2)
    party_ids_raw = m.group(3)
    party_ids = re.findall(r'[\'"]([^\'"]+)[\'"]', party_ids_raw)
    munis.append({'id': muni_id, 'name': name, 'partyIds': party_ids})

# ── Parse candidates.js ──────────────────────────────────────────────────────
with open('../js/data/candidates.js', encoding='utf-8') as f:
    js_src = f.read()

real_data_match = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', js_src, re.DOTALL)
muni_var_map = {}
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data_match.group(1)):
    muni_var_map[m.group(1)] = m.group(2)

var_data = {}
for cb in re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', js_src):
    var_name = cb.group(1)
    if var_name == 'REAL_DATA': continue
    start = cb.end() - 1
    depth, pos = 0, start
    while pos < len(js_src):
        if js_src[pos] == '{': depth += 1
        elif js_src[pos] == '}':
            depth -= 1
            if depth == 0: break
        pos += 1
    block = js_src[start:pos+1]
    party_data = {}
    for pm in re.finditer(r'\b([A-Z]{1,5})\s*:\s*\{', block):
        pc = pm.group(1)
        p_start = pm.end() - 1
        d2, pp = 0, p_start
        while pp < len(block):
            if block[pp] == '{': d2 += 1
            elif block[pp] == '}':
                d2 -= 1
                if d2 == 0: break
            pp += 1
        pb = block[p_start:pp+1]
        lm = re.search(r'\blist\s*:\s*\[', pb)
        if lm:
            ls = lm.end()-1; d3, lp = 0, ls
            while lp < len(pb):
                if pb[lp] == '[': d3 += 1
                elif pb[lp] == ']':
                    d3 -= 1
                    if d3 == 0: break
                lp += 1
            names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', pb[ls:lp+1])
            party_data[pc] = len(names)
    if party_data:
        var_data[var_name] = party_data

# ── Build table ──────────────────────────────────────────────────────────────
rows = []
for muni in munis:
    pid = muni['id']
    name = muni['name']
    party_ids = muni['partyIds']

    if len(party_ids) == 0:
        mtype = 'Óbundið'
    elif len(party_ids) == 1:
        mtype = 'Sjálfkjörið'
    else:
        mtype = 'Venjulegt'

    var_name = muni_var_map.get(pid, '')
    party_data = var_data.get(var_name, {})

    counts = []
    for key in party_ids:
        counts.append(party_data.get(key, 0))

    n_lists = len(party_ids)
    total_cands = sum(counts)

    # Candidates per list: show as single number if uniform, else each count
    if len(counts) == 0:
        per_list = '-'
    elif len(set(counts)) == 1:
        per_list = str(counts[0])
    else:
        per_list = ', '.join(str(c) for c in counts)

    party_letters = ', '.join(party_ids)

    rows.append({
        'name': name,
        'type': mtype,
        'n_lists': n_lists,
        'per_list': per_list,
        'total': total_cands,
        'parties': party_letters,
    })

# Sort: normal first, then sjálfkjörið, then óbundið, alpha within
order = {'Venjulegt': 0, 'Sjálfkjörið': 1, 'Óbundið': 2}
rows.sort(key=lambda r: (order[r['type']], r['name']))

# ── Print table ──────────────────────────────────────────────────────────────
# Column widths
w_name = max(len(r['name']) for r in rows) + 2
w_type = 12
w_lists = 7
w_per = 30
w_total = 8
w_parties = max(len(r['parties']) for r in rows) + 2

header = (f"{'Sveitarfélag':<{w_name}} {'Tegund':<{w_type}} {'Listar':>{w_lists}} "
          f"{'Framb./lista':<{w_per}} {'Samtals':>{w_total}}  {'Listabókstafir'}")
sep = '-' * (w_name + w_type + w_lists + w_per + w_total + w_parties + 10)

print(header)
print(sep)

total_lists = 0
total_cands = 0
for r in rows:
    print(f"{r['name']:<{w_name}} {r['type']:<{w_type}} {r['n_lists']:>{w_lists}} "
          f"{r['per_list']:<{w_per}} {r['total']:>{w_total}}  {r['parties']}")
    total_lists += r['n_lists']
    total_cands += r['total']

print(sep)
print(f"{'SAMTALS':<{w_name}} {'':<{w_type}} {total_lists:>{w_lists}} "
      f"{'':<{w_per}} {total_cands:>{w_total}}")
