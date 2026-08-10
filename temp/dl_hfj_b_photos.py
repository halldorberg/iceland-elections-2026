"""Process 9 Framsókn Hornafjörður (HFJ.B) photos from user-provided folder."""
import hashlib, shutil, sys, io
from pathlib import Path
from PIL import Image, ImageOps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
SRC = Path(r'C:\Users\USER\Downloads\myndirafframbjendum')
DST = ROOT / 'images' / 'candidates'

# (seat, full_name, src_filename)
MAP = [
    (6,  'Finnur Smári Torfason',         '6.sæti_Finnur Smári.jpg'),
    (7,  'Erla Rún Guðmundsdóttir',       '7.sæti_Erla Rún.jpg'),
    (8,  'Þórdís Þórsdóttir',             '8.sæti_Þórdís Þórs.jpg'),
    (9,  'Lena Hrönn Marteinsdóttir',     '9.sæti_Lena Hrönn.jpg'),
    (10, 'Sigursteinn Ingvar Traustason', '10.sæti_Sigursteinn Ingvar.jpg'),
    (11, 'Lars Jóhann Andrésson Imsland', '11.sæti_Lars Andrésson.jpg'),
    (12, 'Haukur Ingi Einarsson',         '12.sæti_Haukur Ingi.jpg'),
    (13, 'Reynir Arnarson',               '13.sæti_Reynir Arnars.jpg'),
    (14, 'Ásgerður Kristín Gylfadóttir',  '14.sæti_Ásgerður Gylfa.jpg'),
]

results = []
for seat, name, fname in MAP:
    src = SRC / fname
    if not src.exists():
        print(f'  {seat:>2}  {name:<40}  SOURCE MISSING: {src}')
        continue

    fn_hash = hashlib.md5(f'hfj-b-{seat}-{name}'.encode()).hexdigest()[:16]
    out = DST / f'{fn_hash}.jpg'

    img = Image.open(src)
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
    print(f'  {seat:>2}  {name:<40}  {fn_hash}.jpg  ({sz//1024} KB, src {w}x{h})')
    results.append((seat, name, out.name))

print()
print('# Photo paths for candidates.js edits:')
for seat, name, fn in results:
    print(f"  {seat}: 'images/candidates/{fn}'  # {name}")
