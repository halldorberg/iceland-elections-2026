"""Download all 14 K-listinn candidate photos and crop to 400x400 JPEG."""
import sys, io, os, hashlib, urllib.request
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PHOTOS = {
    1:  ('Guðfinnur',  'ec8ac9_841a0876a5b948af864c5e3b591cded5'),
    2:  ('Magnús',     'ec8ac9_9f35c8059aaa4819a4c8993e8db71ed6'),
    3:  ('Rebekka',    'ec8ac9_475ec97bce804f0b8e857c83cfe02240'),
    4:  ('Karen',      'ec8ac9_ab59bce6383c4d0eb91631983e1517b3'),
    5:  ('Hjörtur',    'ec8ac9_53e50d03e535478f91dd4bd4fca725e0'),
    6:  ('Katrín',     'ec8ac9_c755f655e2d74d4db835bfabbadd3ade'),
    7:  ('Sigtryggur', 'ec8ac9_839cfbb8868547759343d5a08460c1f3'),
    8:  ('Olga',       'ec8ac9_efa2018e03dd41b3bae59444b2cba701'),
    9:  ('Ketill',     'ec8ac9_d98fc54e35944132811691b42b0cc349'),
    10: ('Helga',      'ec8ac9_50db132b07b447489d208672f9d552a4'),
    11: ('Unnur',      'ec8ac9_f43350252d18441db44c6e0cbecc1673'),
    12: ('Guðbergur',  'ec8ac9_0cf5e151a0b0469eab85409c7db9d866'),
    13: ('Stefán',     'ec8ac9_1b05fc1bdc374e94b26154d29883796c'),
    14: ('Matthildur', 'ec8ac9_e20cdd377cba4b2e8884dae8b5f39eeb'),
}

ROOT = Path(r'F:\Claude Projects\iceland-elections')
DST = ROOT / 'images' / 'candidates'
TMP = ROOT / 'temp' / 'klistinn_raw'
TMP.mkdir(exist_ok=True, parents=True)

results = {}
for n, (name, base) in PHOTOS.items():
    # Wix high-res URL: full original
    url = f'https://static.wixstatic.com/media/{base}~mv2.jpg'
    raw = TMP / f'{n:02d}-{name}.jpg'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw.write_bytes(r.read())
    except Exception as e:
        print(f'  {n}: ERROR download: {e}')
        continue

    fn_hash = hashlib.md5(f'klistinn-{n}-{name}'.encode()).hexdigest()[:16]
    out = DST / f'{fn_hash}.jpg'

    img = Image.open(raw).convert('RGB')
    w, h = img.size
    # Center-crop to square
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    if side > 400:
        img = img.resize((400, 400), Image.LANCZOS)
    img.save(out, 'JPEG', quality=88, optimize=True)
    sz = out.stat().st_size
    print(f'  {n:>2}  {name:<12}  {fn_hash}.jpg  ({sz//1024} KB, src {w}x{h})')
    results[n] = (name, f'{fn_hash}.jpg')

print(f'\nDone. {len(results)} photos saved.')
