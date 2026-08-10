"""Download Reykjavík Miðflokkurinn candidate photos (7, 8, 9, 11)."""
import hashlib, urllib.request, sys, io
from pathlib import Path
from PIL import Image, ImageOps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
DST = ROOT / 'images' / 'candidates'
TMP = ROOT / 'temp' / 'rvk_m_raw'
TMP.mkdir(exist_ok=True, parents=True)

PHOTOS = {
    7:  ('Eva',    'https://midflokkurinn.is/wp-content/uploads/2026/03/Eva-THorsteinsdottir.jpg'),
    8:  ('Katrín', 'https://midflokkurinn.is/wp-content/uploads/2026/03/Katrin-.jpg'),
    9:  ('Breki',  'https://midflokkurinn.is/wp-content/uploads/2026/03/Breki-.jpg'),
    11: ('Sóldís', 'https://midflokkurinn.is/wp-content/uploads/2026/03/Soldis.jpg'),
}

for n, (name, url) in PHOTOS.items():
    raw = TMP / f'{n:02d}-{name}.jpg'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw.write_bytes(r.read())
    except Exception as e:
        print(f'  {n}: DL error {e}')
        continue

    fn_hash = hashlib.md5(f'rvk-m-{n}-{name}'.encode()).hexdigest()[:16]
    out = DST / f'{fn_hash}.jpg'
    img = Image.open(raw)
    img = ImageOps.exif_transpose(img)
    img = img.convert('RGB')
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    if side > 400:
        img = img.resize((400, 400), Image.LANCZOS)
    img.save(out, 'JPEG', quality=88, optimize=True)
    print(f'  {n:>2}  {name:<10}  {fn_hash}.jpg  ({out.stat().st_size//1024} KB, src {w}x{h})')
