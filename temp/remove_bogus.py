"""Remove bogus or 'no 2022 history' party entries from results2022.js
so the site renders the 'new party' / N/A message instead."""
import re, sys, io, shutil
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

REMOVE = [
    ('fjallabyggd', 'H'),
    ('floahreppur', 'FLT'),
    ('grimsnesgrafningur', 'GGO'),
    ('hrunamannahreppur', 'HRL'),
    ('rangarthingytra', 'RYA'),
    ('vogar', 'VOE'),
    ('thingeyjarsveit', 'THVL'),
    ('isafjordur', 'S'),
    ('isafjordur', 'C'),
]

PATH = ROOT / 'js' / 'data' / 'results2022.js'
src = PATH.read_text(encoding='utf-8')
backup = PATH.with_suffix(f'.js.bak_remove_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
shutil.copy(PATH, backup)
print(f'backup: {backup.name}')

def find_muni_block(src, muni_id):
    m = re.search(r'^\s*' + re.escape(muni_id) + r':\s*\{\s*$', src, re.M)
    if not m: return None
    open_pos = src.find('{', m.start())
    depth=0; i=open_pos
    while i < len(src):
        c = src[i]
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return open_pos, i
        i+=1

removed = 0
errors = []
by_muni = {}
for m, c in REMOVE:
    by_muni.setdefault(m, []).append(c)

for muni_id, codes in by_muni.items():
    span = find_muni_block(src, muni_id)
    if not span:
        for c in codes: errors.append((muni_id, c, 'muni not found'))
        continue
    start, end = span
    block = src[start:end+1]
    new_block = block
    for code in codes:
        # Remove a line like:  CODE: { pct: X, seats: Y },[\n]
        # Be flexible with whitespace and trailing comment.
        pat = re.compile(r'\n\s+' + re.escape(code) + r':\s*\{\s*pct:[^}]*\}\s*,?[^\n]*')
        m = pat.search(new_block)
        if not m:
            errors.append((muni_id, code, 'party row not found'))
            continue
        new_block = new_block[:m.start()] + new_block[m.end():]
        removed += 1
    src = src[:start] + new_block + src[end+1:]

PATH.write_text(src, encoding='utf-8')
print(f'removed: {removed}/{len(REMOVE)}')
for e in errors: print(' ', e)
