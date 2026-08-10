"""Find agenda items that look like placeholders (short text, no source_quote)."""
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()


def find_const_block(s, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', s, re.M)
    if not m: return None
    op = m.end() - 1
    depth = 0; i = op; in_str = None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == '\\': i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c in ("'",'"','`'): in_str = c; i += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return op + 1, i
        i += 1


# Get muni constants
real_data_m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
muni_const_to_id = {}
for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', real_data_m.group(1)):
    muni_const_to_id[pm.group(2)] = pm.group(1)

results = []  # (muni_id, const, party, has_source_quote, items, total_chars, avg_chars)

for const, muni_id in muni_const_to_id.items():
    rng = find_const_block(src, const)
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
                if c == '\\': i += 2; continue
                if c == in_str: in_str = None
                i += 1; continue
            if c in ("'",'"','`'): in_str = c; i += 1; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0: break
            i += 1
        ptext = body[pm.end()-1:i+1]

        # Find agenda block
        ag_m = re.search(r'agenda:\s*\[(.*?)\]\s*,?\s*(?:platformUrl|list|tagline|//)', ptext, re.S)
        if not ag_m: continue
        ag_body = ag_m.group(1)
        # Parse each agenda item — single-line or multi-line
        items = []
        # Single-line: { icon: '...', title: '...', text: '...' }
        for sm in re.finditer(
            r"\{\s*icon:\s*'[^']*',\s*title:\s*'((?:[^'\\]|\\.)+)',\s*text:\s*'((?:[^'\\]|\\.)+)'(?:,\s*source_quote:\s*'[^']*')?",
            ag_body):
            items.append((sm.group(1), sm.group(2)))
        # Multi-line items already include source_quote info inline; parse by walking
        # Reset and use a better walker: find each { icon: ... } block
        mitems = []
        idx = 0
        while idx < len(ag_body):
            om = re.search(r'\{', ag_body[idx:])
            if not om: break
            obj_start = idx + om.start()
            j = obj_start
            depth2 = 0; in_str2 = None
            while j < len(ag_body):
                c = ag_body[j]
                if in_str2:
                    if c == '\\': j += 2; continue
                    if c == in_str2: in_str2 = None
                    j += 1; continue
                if c in ("'", '"', '`'): in_str2 = c; j += 1; continue
                if c == '{': depth2 += 1
                elif c == '}':
                    depth2 -= 1
                    if depth2 == 0: break
                j += 1
            block = ag_body[obj_start:j+1]
            tm = re.search(r"title:\s*'((?:[^'\\]|\\.)+)'", block)
            xm = re.search(r"text:\s*'((?:[^'\\]|\\.)+)'", block)
            sq = re.search(r"source_quote:\s*'", block) is not None
            if tm and xm:
                mitems.append((tm.group(1), xm.group(1), sq))
            idx = j + 1

        if not mitems: continue
        avg_text_len = sum(len(x[1]) for x in mitems) / len(mitems)
        any_source_quote = any(x[2] for x in mitems)
        # Placeholder heuristics: avg text length < 100 chars AND no source_quote
        if avg_text_len < 100 and not any_source_quote:
            results.append({
                'muni_id': muni_id,
                'const': const,
                'party': party,
                'items': len(mitems),
                'avg_text_len': avg_text_len,
                'sample': mitems[0][0] + ' → ' + mitems[0][1][:60],
            })

print(f'Suspected placeholder agendas: {len(results)}')
print()
for r in sorted(results, key=lambda x: x['avg_text_len']):
    print(f"  {r['muni_id']:25s} {r['const']}.{r['party']:6s}  {r['items']} items, avg {r['avg_text_len']:.0f} chars  — {r['sample']}")
