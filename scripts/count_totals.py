import re
with open('../js/data/candidates.js', encoding='utf-8') as f:
    src = f.read()

total_lists = 0
total_candidates = 0

for cb in re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', src):
    var_name = cb.group(1)
    if var_name == 'REAL_DATA':
        continue
    start = cb.end() - 1
    depth, pos = 0, start
    while pos < len(src):
        if src[pos] == '{': depth += 1
        elif src[pos] == '}':
            depth -= 1
            if depth == 0: break
        pos += 1
    block = src[start:pos+1]
    for pm in re.finditer(r'\b([A-Z]{1,5})\s*:\s*\{', block):
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
            ls = lm.end() - 1
            d3, lp = 0, ls
            while lp < len(pb):
                if pb[lp] == '[': d3 += 1
                elif pb[lp] == ']':
                    d3 -= 1
                    if d3 == 0: break
                lp += 1
            lb = pb[ls:lp+1]
            names = re.findall(r'\[\s*\d+\s*,\s*[\'"]([^\'"]+)[\'"]', lb)
            total_lists += 1
            total_candidates += len(names)

print('Lists:', total_lists)
print('Candidates:', total_candidates)
