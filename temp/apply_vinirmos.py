"""Download photos + bios from vinirmos and update Vinir Mosfellsbæjar L-list."""
import re, sys, io, json, hashlib, urllib.request, time
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')

candidates = json.load(open(ROOT / 'temp' / 'vinirmos_candidates.json', encoding='utf-8'))
print(f'processing {len(candidates)} candidates...\n')

def title_case_is(s):
    """Lowercase Icelandic title case (first letter cap, rest lower)."""
    s = s.strip()
    if not s: return s
    if s.isupper():
        return s[0] + s[1:].lower()
    return s

# Download + process photos
for c in candidates:
    img_url = c['image_url']
    # Download (high res — strip query params, use ?format=2500w if possible)
    if '?' not in img_url:
        url = img_url + '?format=1500w'
    else:
        url = img_url
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read()
    except Exception as e:
        print(f'  [{c["ballot"]:2d}] {c["name"]} — fetch err: {e}')
        c['image_path'] = None
        continue
    # Process
    try:
        from io import BytesIO
        im = Image.open(BytesIO(data))
        if im.mode != 'RGB':
            im = im.convert('RGB')
        w, h = im.size
        # Resize to max 1200 on long side
        scale = 1200 / max(w, h) if max(w, h) > 1200 else 1.0
        if scale != 1.0:
            im = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
        buf = BytesIO()
        im.save(buf, 'JPEG', quality=85, optimize=True)
        out_data = buf.getvalue()
        h16 = hashlib.sha256(out_data).hexdigest()[:16]
        path = ROOT / 'images' / 'candidates' / f'{h16}.jpg'
        path.write_bytes(out_data)
        c['image_path'] = f'images/candidates/{h16}.jpg'
        print(f'  [{c["ballot"]:2d}] {c["name"]:30s} -> {h16}.jpg ({len(out_data):,} B, {im.size})')
    except Exception as e:
        print(f'  [{c["ballot"]:2d}] {c["name"]} — process err: {e}')
        c['image_path'] = None
    time.sleep(0.3)

# Save enriched
json.dump(candidates, open(ROOT / 'temp' / 'vinirmos_processed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\nwrote temp/vinirmos_processed.json')
