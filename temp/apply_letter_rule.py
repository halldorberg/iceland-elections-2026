"""Apply letter-rule fixes to results2022.js:
- REMOVE entries where 2026 letter ≠ 2022 letter
- RESTORE entries that match by letter (previously removed by mistake)
- UPDATE entries with refined kosningasaga pct values
Backs up the file."""
import re, sys, io, shutil
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

REMOVE = [
    ('fjallabyggd', 'S'),
    ('horgarsv', 'HGG'),
    ('thingeyjarsveit', 'THVA'),
    ('thingeyjarsveit', 'THVL'),
    ('svalbardsstrond', 'SVSS'),
    ('svalbardsstrond', 'SVSH'),
    ('grimsnesgrafningur', 'GGA'),
]

# (muni, code, pct, seats, comment)
RESTORE = [
    ('fjallabyggd', 'H', 31.52, 2, 'H-listinn 2022'),
    ('floahreppur', 'FLT', 33.59, 2, 'T-listinn 2022'),
    ('hrunamannahreppur', 'HRL', 43.45, 2, 'L-listinn 2022'),
    ('rangarthingytra', 'RYA', 50.56, 4, 'Á-listinn 2022'),
    ('vogar', 'VOE', 37.00, 3, 'E-listi 2022'),
]

# (muni, code, new_pct)
UPDATE_PCT = [
    ('eyjafjardarsveit', 'EJF', 58.99),
    ('eyjafjardarsveit', 'EJK', 41.01),
]

PATH = ROOT / 'js' / 'data' / 'results2022.js'
src = PATH.read_text(encoding='utf-8')
backup = PATH.with_suffix(f'.js.bak_letter_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
shutil.copy(PATH, backup)
print(f'backup: {backup.name}')

def find_muni_block(src, muni_id):
    m = re.search(r'^\s*' + re.escape(muni_id) + r':\s*\{\s*$', src, re.M)
    if not m: return None
    open_pos = src.find('{', m.start())
    depth=0; i=open_pos
    while i < len(src):
        c=src[i]
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return open_pos, i
        i+=1

# REMOVE
removed = 0
for muni_id, code in REMOVE:
    span = find_muni_block(src, muni_id)
    if not span: print(f'  REMOVE: muni {muni_id} not found'); continue
    start, end = span
    block = src[start:end+1]
    pat = re.compile(r'\n\s+' + re.escape(code) + r':\s*\{\s*pct:[^}]*\}\s*,?[^\n]*')
    m = pat.search(block)
    if not m: print(f'  REMOVE: {muni_id}.{code} not found in block'); continue
    new_block = block[:m.start()] + block[m.end():]
    src = src[:start] + new_block + src[end+1:]
    removed += 1
print(f'removed: {removed}/{len(REMOVE)}')

# UPDATE_PCT
updated = 0
for muni_id, code, new_pct in UPDATE_PCT:
    span = find_muni_block(src, muni_id)
    if not span: print(f'  UPDATE: muni {muni_id} not found'); continue
    start, end = span
    block = src[start:end+1]
    pat = re.compile(r'(' + re.escape(code) + r'\s*:\s*\{\s*pct:\s*)([\d\.]+)')
    m = pat.search(block)
    if not m: print(f'  UPDATE: {muni_id}.{code} not found'); continue
    new_block = block[:m.start(2)] + str(new_pct) + block[m.end(2):]
    src = src[:start] + new_block + src[end+1:]
    updated += 1
print(f'updated: {updated}/{len(UPDATE_PCT)}')

# RESTORE — insert before the closing } of the parties block
restored = 0
for muni_id, code, pct, seats, comment in RESTORE:
    span = find_muni_block(src, muni_id)
    if not span: print(f'  RESTORE: muni {muni_id} not found'); continue
    start, end = span
    block = src[start:end+1]
    # Find parties block
    pm = re.search(r'parties:\s*\{', block)
    if not pm: print(f'  RESTORE: {muni_id} no parties block'); continue
    # Walk to closing }
    depth=0; i=pm.end()-1
    while i < len(block):
        c=block[i]
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: break
        i+=1
    # i is at closing } of parties block — insert before
    # Format the new line at indent matching surrounding
    line = f"      {code}: {{ pct: {pct}, seats: {seats} }},  // {comment}\n    "
    new_block = block[:i] + line + block[i:]
    src = src[:start] + new_block + src[end+1:]
    restored += 1
print(f'restored: {restored}/{len(RESTORE)}')

PATH.write_text(src, encoding='utf-8')
print(f'\ntotal: removed {removed}, updated {updated}, restored {restored}')
