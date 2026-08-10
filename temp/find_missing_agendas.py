"""Find lists that have NO agenda block at all (vs placeholder)."""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('js/data/candidates.js', encoding='utf-8').read()

m = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', src)
muni_const_to_id = {}
for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', m.group(1)):
    muni_const_to_id[pm.group(2)] = pm.group(1)


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


no_agenda = []
for const, muni_id in muni_const_to_id.items():
    rng = find_const_block(src, const)
    if not rng:
        continue
    cs, ce = rng
    body = src[cs:ce]
    for pm in re.finditer(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', body):
        party = pm.group(1)
        i = pm.end() - 1
        depth = 0
        in_str = None
        while i < len(body):
            c = body[i]
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
                    break
            i += 1
        ptext = body[pm.end() - 1:i + 1]
        if 'agenda:' not in ptext:
            no_agenda.append(f'{muni_id}.{party}')

print(f'Lists with NO agenda block: {len(no_agenda)}')
for x in sorted(no_agenda):
    print(f'  {x}')
