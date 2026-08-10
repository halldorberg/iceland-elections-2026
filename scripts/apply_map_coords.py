"""Apply approved coordinates from temp/munis_proposed.json into
js/data/municipalities.js. Surgical regex edit per muni id.
"""
from __future__ import annotations
import json, re, sys, io, shutil
from datetime import datetime
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
MUNI_JS = ROOT / 'js' / 'data' / 'municipalities.js'
PROPOSED = ROOT / 'temp' / 'munis_proposed.json'

data = json.loads(PROPOSED.read_text(encoding='utf-8'))
src = MUNI_JS.read_text(encoding='utf-8')

# Backup
bak = MUNI_JS.with_suffix(MUNI_JS.suffix + '.bak_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
shutil.copy(MUNI_JS, bak)
print(f'Backup: {bak.name}')

applied, skipped, missing = 0, 0, []
for d in data:
    mid = d['id']
    new_lat = d['new_lat']
    new_lng = d['new_lng']
    # Match the muni block: id: 'X', ... coords: { lat: N, lng: N }
    pat = re.compile(
        r"(id:\s*'" + re.escape(mid) + r"',[\s\S]*?coords:\s*\{\s*lat:\s*)(-?\d+\.?\d*)(\s*,\s*lng:\s*)(-?\d+\.?\d*)(\s*\})"
    )
    m = pat.search(src)
    if not m:
        missing.append(mid)
        continue
    old_lat, old_lng = float(m.group(2)), float(m.group(4))
    if abs(old_lat - new_lat) < 1e-5 and abs(old_lng - new_lng) < 1e-5:
        skipped += 1
        continue
    src = pat.sub(
        lambda mo: mo.group(1) + f'{new_lat}' + mo.group(3) + f'{new_lng}' + mo.group(5),
        src,
        count=1,
    )
    applied += 1
    print(f'  ✓ {mid:25s} ({old_lat:.4f}, {old_lng:.4f}) → ({new_lat}, {new_lng})')

if missing:
    print(f'\n⚠ Not found in municipalities.js: {missing}')

MUNI_JS.write_text(src, encoding='utf-8')
print(f'\nApplied: {applied} | already-matching: {skipped} | missing: {len(missing)}')
print(f'Wrote → {MUNI_JS}')
