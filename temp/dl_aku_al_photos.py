"""Download + crop AKU.AL candidate photos from akureyrarlistinn.is."""
import hashlib, urllib.request, sys, io
from pathlib import Path
from PIL import Image, ImageOps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
DST = ROOT / 'images' / 'candidates'
TMP = ROOT / 'temp' / 'aku_al_raw'
TMP.mkdir(exist_ok=True, parents=True)

UA = 'Mozilla/5.0'

# (seat, name, image_filename_on_site)
PHOTOS = [
    (1,  'Þórhallur Jónsson',             'thorhallur'),
    (2,  'Karen Sigurbjörnsdóttir',       'karen'),
    (3,  'Helgi Steinar Halldórsson',     'helgi'),
    (4,  'Kristrún María Björnsdóttir',   'kristrun'),
    (5,  'Darri Rafn Hólmarsson',         'darri'),
    (6,  'Dana Rán Jónsdóttir',           'dana'),
    (7,  'Vilmundur Aðalsteinn Árnason',  'villi'),
    (8,  'Guðjón Andri Gylfason',         'andri'),
    (9,  'Elfa Ágústsdóttir',             'elfa'),
    (10, 'Pavel Víking Landa',            'pavel'),
    (11, 'Rannveig Hansen Jónsdóttir',    'rannveig'),
    (12, 'Hilmar Friðjónsson',            'hilmar'),
    (13, 'Fríða Kristín Hreiðarsdóttir',  'frida'),
    (14, 'Friðbjörn Benediktsson',        'fridbjorn'),
    (15, 'Harpa Þórey Sigurðardóttir',    'harpa'),
    (16, 'Elvar Freyr Pálsson',           'elvar'),
    (17, 'Axel Darri Þórhallsson',        'axel'),
    (19, 'Rúnar Þór Björnsson',           'runar'),
    (20, 'Ingibjörg Margrét Þórhallsdóttir', 'ingibjorgmargret'),
]

for seat, name, fname in PHOTOS:
    # Try .jpeg, then .jpg
    raw = None
    for ext in ('jpeg', 'jpg'):
        url = f'https://www.akureyrarlistinn.is/images/{fname}.{ext}'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                raw = r.read()
                if len(raw) > 5000:
                    break
                raw = None
        except Exception:
            continue
    if not raw:
        print(f'  {seat:>2}  {name:<35}  DOWNLOAD FAIL')
        continue

    src = TMP / f'{fname}.jpg'
    src.write_bytes(raw)

    fn_hash = hashlib.md5(f'aku-al-{seat}-{name}'.encode()).hexdigest()[:16]
    out = DST / f'{fn_hash}.jpg'

    img = Image.open(src)
    img = ImageOps.exif_transpose(img)
    img = img.convert('RGB')
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    # Portrait photos — take top-square so face stays visible
    top = 0
    sq = img.crop((left, top, left + side, top + side))
    if side > 400:
        sq = sq.resize((400, 400), Image.LANCZOS)
    sq.save(out, 'JPEG', quality=88, optimize=True)
    print(f'  {seat:>2}  {name:<35}  {fn_hash}.jpg  ({out.stat().st_size//1024} KB)')
