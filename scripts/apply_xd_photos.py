#!/usr/bin/env python
"""
Match xd.is candidates (Google Drive photoIds) to candidates.js and
download/apply photos. Handles all three candidate formats:
  1. [N, 'name', 'occ', 'photo', { bio }]   -- already has photo
  2. [N, 'name', 'occ', null]  or  [..., null, { bio }]  -- null photo
  3. [N, 'name', 'occ'],                     -- no photo field at all
"""
import json, re, os, hashlib, urllib.request, unicodedata

XD_JSON   = r'F:\Claude Projects\iceland-elections\scan_results\xd_candidates_cdp.json'
CANDS_JS  = r'F:\Claude Projects\iceland-elections\js\data\candidates.js'
IMG_DIR   = r'F:\Claude Projects\iceland-elections\images\candidates'
DRIVE_URL = 'https://lh3.googleusercontent.com/d/{}'

def normalize(name):
    n = unicodedata.normalize('NFD', name)
    n = ''.join(c for c in n if unicodedata.category(c) != 'Mn')
    return ' '.join(n.lower().split())

def download_image(photo_id):
    url = DRIVE_URL.format(photo_id)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req, timeout=20).read()
    hexhash = hashlib.md5(data).hexdigest()[:16]
    fname = hexhash + '.jpg'
    fpath = os.path.join(IMG_DIR, fname)
    if not os.path.exists(fpath):
        with open(fpath, 'wb') as f:
            f.write(data)
    return f'images/candidates/{fname}', url

def main():
    xd_candidates = json.load(open(XD_JSON, encoding='utf-8'))
    xd_by_name = {}
    for c in xd_candidates:
        if c.get('photoId'):
            xd_by_name[normalize(c['name'])] = c['photoId']
    print(f'xd.is candidates with photoId: {len(xd_by_name)}')

    with open(CANDS_JS, encoding='utf-8') as f:
        content = f.read()

    replacements = []
    patched_null = 0
    patched_missing = 0
    skipped = 0
    errors = 0

    # ── FORMAT 2: null photo (followed by , or ]) ──────────────────────────
    null_pat = re.compile(
        r'(\[\s*\d+\s*,\s*\'([^\']+)\'\s*,\s*\'[^\']*\'\s*,\s*)(null)(\s*[,\]])',
        re.DOTALL
    )
    for m in null_pat.finditer(content):
        name = m.group(2)
        norm = normalize(name)
        if norm not in xd_by_name:
            skipped += 1
            continue
        try:
            local, _ = download_image(xd_by_name[norm])
            print(f'  [null] {name} -> {local}')
            replacements.append((m.start(), m.end(),
                                  m.group(1) + f"'{local}'" + m.group(4)))
            patched_null += 1
        except Exception as e:
            print(f'  ERROR {name}: {e}')
            errors += 1

    # ── FORMAT 3: no photo field — entry ends with 'occ'], ────────────────
    # Pattern: [N, 'name', 'occ'],   (closing bracket, no 4th arg)
    missing_pat = re.compile(
        r'(\[\s*\d+\s*,\s*\'([^\']+)\'\s*,\s*\'[^\']*\'\s*)(\])',
        re.DOTALL
    )
    # Build set of already-replaced positions to avoid double-applying
    replaced_spans = set()
    for start, end, _ in replacements:
        replaced_spans.add((start, end))

    for m in missing_pat.finditer(content):
        # Skip if this position overlaps with a format-2 replacement
        if any(start <= m.start() <= end for start, end, _ in replacements):
            continue
        name = m.group(2)
        norm = normalize(name)
        if norm not in xd_by_name:
            skipped += 1
            continue
        try:
            local, _ = download_image(xd_by_name[norm])
            print(f'  [miss] {name} -> {local}')
            # Insert photo before the closing ]
            new_text = m.group(1) + f", '{local}'" + m.group(3)
            replacements.append((m.start(), m.end(), new_text))
            patched_missing += 1
        except Exception as e:
            print(f'  ERROR {name}: {e}')
            errors += 1

    # Apply all replacements in reverse order
    for start, end, new_text in sorted(replacements, key=lambda x: -x[0]):
        content = content[:start] + new_text + content[end:]

    with open(CANDS_JS, 'w', encoding='utf-8') as f:
        f.write(content)

    total = patched_null + patched_missing
    print(f'\nDone!')
    print(f'  Patched null-photo entries:    {patched_null}')
    print(f'  Patched no-photo entries:      {patched_missing}')
    print(f'  Total new photos applied:      {total}')
    print(f'  Skipped (no xd.is match):      {skipped}')
    print(f'  Errors:                        {errors}')

if __name__ == '__main__':
    main()
