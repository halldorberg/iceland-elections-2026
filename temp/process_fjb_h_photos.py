"""Process H-listinn Fjallabyggð campaign photos: center-crop → 400x400 JPEG."""
import hashlib, sys, io
from pathlib import Path
from PIL import Image, ImageOps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
SRC = ROOT / 'temp' / 'hlistinn_fjb'
DST = ROOT / 'images' / 'candidates'

PHOTOS = [
    (1,  'Helgi Jóhannsson',           '01_Helgi.webp'),
    (2,  'Kristinn Kristjánsson',      '02_Kristinn.webp'),
    (3,  'Ásgeir Logi Ásgeirsson',     '03_Asgeir_Logi.webp'),
    (4,  'Auður Ösp H. Magnúsdóttir',  '04_Audur_Osp.webp'),
    (5,  'Guðlaugur Magnús Ingason',   '05_Gudlaugur_Magnus.webp'),
    (6,  'Þorfinna Þrastardóttir',     '06_Thorfinna_Ellen.webp'),
    (7,  'Þorgeir Bjarnason',          '07_Thorgeir.webp'),
    (8,  'Klara Mist Pálsdóttir',      '08_Klara_Mist.webp'),
    (9,  'Jón Valgeir Baldursson',     '09_Jon_Valgeir.webp'),
    (10, 'Andri Viðar Víglundsson',    '10_Andri_Vidar.webp'),
    (11, 'Aðalbjörg Snorradóttir',     '11_Adalbjorg.webp'),
    (12, 'Áki Berndsen',               '12_Aki.webp'),
    (13, 'Katrín Freysdóttir',         '13_Katrin.webp'),
    (14, 'Árni Helgason',              '14_Arni_Helga.webp'),
]

for seat, name, fn in PHOTOS:
    src = SRC / fn
    if not src.exists():
        print(f'  {seat:>2}  {name:<35}  MISSING {src.name}')
        continue
    fn_hash = hashlib.md5(f'fjb-h-{seat}-{name}'.encode()).hexdigest()[:16]
    out = DST / f'{fn_hash}.jpg'
    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    img = img.convert('RGB')
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    # These are studio shots with faces in upper-third. Take TOP-square.
    top = 0
    sq = img.crop((left, top, left + side, top + side))
    if side > 400:
        sq = sq.resize((400, 400), Image.LANCZOS)
    sq.save(out, 'JPEG', quality=88, optimize=True)
    print(f'  {seat:>2}  {name:<35}  {fn_hash}.jpg  ({out.stat().st_size//1024} KB, src {w}x{h})')

print()
print('# Photo paths for candidates.js edits:')
for seat, name, fn in PHOTOS:
    fn_hash = hashlib.md5(f'fjb-h-{seat}-{name}'.encode()).hexdigest()[:16]
    print(f"  {seat}: 'images/candidates/{fn_hash}.jpg'  # {name}")
