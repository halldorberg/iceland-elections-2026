import re, sys, io, json
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()
real_data_m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
munis = []
for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', real_data_m.group(1)):
    munis.append(pm.group(2))


def find_const_block(s, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', s, re.M)
    if not m:
        return None
    op = m.end() - 1
    depth = 0
    i = op
    in_str = None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return op + 1, i
        i += 1


muni_parties = {}
for m in munis:
    rng = find_const_block(src, m)
    if not rng:
        continue
    cs, ce = rng
    parties = re.findall(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', src[cs:ce])
    muni_parties[m] = parties

data = json.load(open('scan_results/ruv_bios.json', encoding='utf-8'))
muni_pc = Counter((e['muni_const'], e['party_code']) for e in data if e.get('ruv_id'))
unmatched = []
for (m, p), v in muni_pc.items():
    if p not in muni_parties.get(m, []):
        unmatched.append((m, p, v))

print(f'Muni-party combos in ruv_bios.json NOT in candidates.js: {len(unmatched)}')
for m, p, v in sorted(unmatched, key=lambda x: -x[2])[:30]:
    print(f'  {m}.{p}: {v} entries  (candidates.js has: {muni_parties.get(m,[])})')
