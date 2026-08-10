"""Apply pct fixes to results2022.js, skipping flagged low-confidence rows.
Backs up the file before editing."""
import re, json, sys, io, shutil
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

SKIP = {('dalvikurbyggd', 'DVA'), ('hunabyggd', 'HBA'), ('thingeyjarsveit', 'THVA')}

proposals = json.load(open(ROOT / 'temp' / 'fix_proposals.json', encoding='utf-8'))
to_apply = [p for p in proposals if (p['muni'], p['code']) not in SKIP]
print(f'proposals: {len(proposals)}, applying: {len(to_apply)}, skipped (low confidence): {len(proposals) - len(to_apply)}')

PATH = ROOT / 'js' / 'data' / 'results2022.js'
src = PATH.read_text(encoding='utf-8')
backup = PATH.with_suffix(f'.js.bak_pctfix_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
shutil.copy(PATH, backup)
print(f'backup: {backup.name}')

def find_muni_block(src, muni_id):
    """Return (start, end) of the muni's parties block."""
    m = re.search(r'^\s*' + re.escape(muni_id) + r':\s*\{\s*$', src, re.M)
    if not m:
        return None
    open_pos = src.find('{', m.start())
    depth = 0; i = open_pos
    while i < len(src):
        c = src[i]
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0: return open_pos, i
        i += 1
    return None

applied = 0
errors = []

# Group fixes by muni for efficiency
by_muni = {}
for p in to_apply:
    by_muni.setdefault(p['muni'], []).append(p)

for muni_id, fixes in by_muni.items():
    span = find_muni_block(src, muni_id)
    if not span:
        for p in fixes: errors.append((p['muni'], p['code'], 'muni block not found'))
        continue
    start, end = span
    block = src[start:end+1]
    new_block = block
    for p in fixes:
        # Find the party row inside this block
        # Pattern: <CODE>: { pct: <number>, seats: <N> ... }
        pat = re.compile(r'(' + re.escape(p['code']) + r')(\s*:\s*\{\s*pct:\s*)([\d\.]+)(\s*,\s*seats:\s*' + str(p['seats']) + r')')
        m = pat.search(new_block)
        if not m:
            errors.append((p['muni'], p['code'], 'party row not found / seat mismatch'))
            continue
        # Verify old pct
        old_pct = float(m.group(3))
        if abs(old_pct - p['old_pct']) > 0.01:
            errors.append((p['muni'], p['code'], f'old pct mismatch: file has {old_pct}, proposal has {p["old_pct"]}'))
            continue
        new_block = new_block[:m.start(3)] + str(p['new_pct']) + new_block[m.end(3):]
        applied += 1
    src = src[:start] + new_block + src[end+1:]

PATH.write_text(src, encoding='utf-8')
print(f'\napplied: {applied}/{len(to_apply)}')
if errors:
    print(f'errors: {len(errors)}')
    for e in errors: print(' ', e)
