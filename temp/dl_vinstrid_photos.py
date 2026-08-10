"""Download all 46 Vinstrið candidate photos + crop to 400x400 JPEG."""
import hashlib, urllib.request, sys, io
from pathlib import Path
from PIL import Image, ImageOps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
DST = ROOT / 'images' / 'candidates'
TMP = ROOT / 'temp' / 'vinstrid_raw'
TMP.mkdir(exist_ok=True, parents=True)

NAMES = [
    'Sanna Magdalena Mörtudóttir', 'Líf Magneudóttir', 'Stefán Pálsson',
    'Ásta Þórdís Skjalddal Guðjónsdóttir', 'Arna Magnea Danks',
    'Finnur Ricart Andrason', 'Laufey Líndal Ólafsdóttir',
    'Riitta Anne Maarit Kaipainen', 'Tinna Jóhannsdóttir', 'Steinar Harðarson',
    'Viðar Gunnarsson', 'Bergrún Andradóttir', 'María Hjálmtýsdóttir',
    'Illugi Gunnarsson', 'Halldór Auðar Svansson', 'Brynhildur Björnsdóttir',
    'Signý Sigurðardóttir', 'Sveinn Rúnar Hauksson', 'Armando Garcia Teixeira',
    'Nína Aradóttir', 'Þórdís Nadia Semichat', 'Kristinn Schram',
    'Sigurður Andrés Sigurðarson', 'Ragnhildur Björt Björnsdóttir', 'Davíð Sól',
    'Ari Orrason', 'Ragnheiður Guðmundsdóttir', 'Birna Björg Guðmundsdóttir',
    'Björn Rúnar Guðmundsson', 'Sæmundur Helgason', 'Sóley Lóa Smáradóttir',
    'Auður Alfífa Ketilsdóttir', 'Þórir Jónsson Hraundal', 'Ingileif Jónsdóttir',
    'Silva Ásthildur Skjalddal Eggertsdóttir', 'Viktor Árnason', 'Alex da Silva',
    'Sigrún Jóhannsdóttir', 'Rakel Hildardóttir', 'Anna Lára Steindal',
    'Jón Helgi Þórarinsson', 'René Biasone', 'Úlfhildur Melkorka Magnadóttir',
    'Sjöfn Ingólfsdóttir', 'Sigrún Jónsdóttir', 'Guðrún Ágústsdóttir',
]

results = []
for n in range(1, 47):
    name = NAMES[n - 1]
    url = f'https://vinstrid.is/candidates/{n:02d}.png'
    raw = TMP / f'{n:02d}.png'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            raw.write_bytes(r.read())
    except Exception as e:
        print(f'  {n:>2}  {name:<40}  DOWNLOAD ERROR: {e}')
        continue

    fn_hash = hashlib.md5(f'vinstrid-rvk-{n}-{name}'.encode()).hexdigest()[:16]
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
    sz = out.stat().st_size
    print(f'  {n:>2}  {name:<40}  {fn_hash}.jpg  ({sz//1024} KB, src {w}x{h})')
    results.append((n, name, out.name))

import json
json.dump(results, open(TMP / 'index.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n{len(results)} photos saved.')
