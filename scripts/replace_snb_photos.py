#!/usr/bin/env python
"""
Replace existing SNB D-party photos with xd.is versions (higher quality).
Unlike apply_xd_photos.py, this handles candidates that already have a photo path.
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
        print(f'    saved {fname}')
    else:
        print(f'    cached {fname}')
    return f'images/candidates/{fname}'

def main():
    xd_data = json.load(open(XD_JSON, encoding='utf-8'))
    # Filter to SNB D-list candidates with photos
    snb = [c for c in xd_data if 'Suðurnesja' in c.get('municipality', '') and c.get('photoId')]
    print(f'SNB xd.is candidates with photoId: {len(snb)}')

    with open(CANDS_JS, encoding='utf-8') as f:
        content = f.read()

    # For each SNB candidate, find their entry by name and replace photo path
    replaced = 0
    errors = 0

    for c in snb:
        name_norm = normalize(c['name'])
        photo_id  = c['photoId']
        seat      = c['seat']

        # Find a matching candidate entry in candidates.js by normalized name
        # The entry looks like: [N, 'Name', 'occupation', 'some/path.ext'  (with or without , { bio })
        # We search for entries whose name normalizes to match
        # Strategy: find all candidate lines with a photo path, match by name
        pat = re.compile(
            r"(\[\s*\d+\s*,\s*'([^']+)'\s*,\s*'[^']*'\s*,\s*)'([^']+)'",
            re.DOTALL
        )
        matched = False
        for m in pat.finditer(content):
            entry_name = m.group(2)
            if normalize(entry_name) == name_norm:
                old_path = m.group(3)
                try:
                    new_path = download_image(photo_id)
                    print(f'  [seat {seat}] {c["name"]}')
                    print(f'    {old_path} -> {new_path}')
                    # Replace just this occurrence's photo path
                    old_full = m.group(0)
                    new_full = m.group(1) + f"'{new_path}'"
                    content = content[:m.start()] + new_full + content[m.end():]
                    replaced += 1
                    matched = True
                except Exception as e:
                    print(f'  ERROR {c["name"]}: {e}')
                    errors += 1
                    matched = True
                break  # stop after first match per candidate

        if not matched:
            print(f'  NO MATCH for seat {seat}: {c["name"]} (norm: {name_norm})')

    with open(CANDS_JS, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'\nDone!')
    print(f'  Photos replaced: {replaced}')
    print(f'  Errors:          {errors}')

if __name__ == '__main__':
    main()
