"""Add photo paths to RVK.A candidate rows for all 46 candidates."""
import re, json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
CJS = ROOT / 'js' / 'data' / 'candidates.js'
photo_index = json.load(open(ROOT / 'temp' / 'vinstrid_raw' / 'index.json', encoding='utf-8'))
# list of [ballot, name, photo_filename]
PHOTOS = {b: f for b, _, f in photo_index}

src = CJS.read_text(encoding='utf-8')

# Find RVK const block
m = re.search(r'^const RVK\s*=\s*\{', src, re.M)
rvk_start = m.end() - 1
depth = 0; i = rvk_start; in_str = None
while i < len(src):
    c = src[i]
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
rvk_end = i

# Find A block
am = re.search(r'\n  A\s*:\s*\{', src[rvk_start:rvk_end])
a_start = rvk_start + am.end() - 1
depth = 0; i = a_start; in_str = None
while i < rvk_end:
    c = src[i]
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
a_end = i


def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


# Collect edits
edits = []
for ballot, photo in PHOTOS.items():
    img_path = f"images/candidates/{photo}"
    # Find row: `[BALLOT, 'name', 'occ'` then either ']' (plain) or `, 'images/...'` or `, null,` or `, {`
    # Pattern: match [BALLOT, 'name', 'occ' and capture what follows
    pat = re.compile(r"\n(\s+)\[(" + str(ballot) + r"),\s*'((?:[^'\\]|\\.)+)'\s*,\s*'((?:[^'\\]|\\.)*)'(\s*,?)")
    m2 = pat.search(src, a_start, a_end)
    if not m2:
        print(f'  ballot {ballot}: row not found')
        continue
    after = src[m2.end():m2.end()+200]
    indent = m2.group(1)
    name = m2.group(3)
    occ = m2.group(4)
    # Determine row format and rebuild
    if after.startswith(']'):
        # Plain: [N, 'name', 'occ']  →  [N, 'name', 'occ', 'images/...']
        new_row = f"\n{indent}[{ballot}, '{esc(name)}', '{esc(occ)}', '{img_path}']"
        # Need to also consume the ']'
        end_pos = m2.end() + 1  # include ']'
    elif after.startswith("null") or after.startswith(" null"):
        # [N, 'name', 'occ', null, { ... }]  →  [N, 'name', 'occ', 'images/...', { ... }]
        # Replace the `null` photo with image path, preserving the trailing comma
        new_row = f"\n{indent}[{ballot}, '{esc(name)}', '{esc(occ)}', '{img_path}'"
        null_start = m2.end() + (1 if after.startswith(" null") else 0)
        end_pos = null_start + 4  # past 'null'
    elif after.startswith(" 'images/") or after.startswith("'images/"):
        # Replace existing photo with new one
        new_row = f"\n{indent}[{ballot}, '{esc(name)}', '{esc(occ)}', '{img_path}'"
        # Find the closing ' of existing photo
        start_quote = src.find("'", m2.end())  # opening '
        end_quote = src.find("'", start_quote + 1)
        end_pos = end_quote + 1
    elif after.startswith(", '"):
        # Extra weird; skip
        continue
    elif after.startswith("{"):
        # No photo column; extended block immediately follows.
        # Format: [N, 'name', 'occ', { ... }]  → [N, 'name', 'occ', 'images/...', { ... }]
        new_row = f"\n{indent}[{ballot}, '{esc(name)}', '{esc(occ)}', '{img_path}',"
        end_pos = m2.end()  # leave the rest (incl. ',' just consumed in group 5)
        # Actually group 5 already captured ',' if present. Adjust:
        if m2.group(5).strip() == ',':
            # Comma already in match; new_row should not duplicate it
            new_row = f"\n{indent}[{ballot}, '{esc(name)}', '{esc(occ)}', '{img_path}',"
    else:
        # Unknown — print and skip
        print(f'  ballot {ballot}: unrecognized format after row: {after[:50]!r}')
        continue

    edits.append((m2.start(), end_pos, new_row, ballot))

# Apply in reverse
edits.sort(key=lambda x: x[0], reverse=True)
for s, e, r, b in edits:
    src = src[:s] + r + src[e:]
print(f'Applied {len(edits)} photo path edits.')

CJS.write_text(src, encoding='utf-8')
print('Wrote candidates.js')
