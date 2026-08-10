"""Apply 14 H-listinn Fjallabyggð photo paths to candidates.js."""
import re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
JS = ROOT / 'js' / 'data' / 'candidates.js'

PHOTOS = {
    1:  ('Helgi Jóhannsson',          '41aa691853c69b7a'),
    2:  ('Kristinn Kristjánsson',     '04822fdf0e88a814'),
    3:  ('Ásgeir Logi Ásgeirsson',    'c58b457ad0ab57f5'),
    4:  ('Auður Ösp H. Magnúsdóttir', '56760e4c8b851003'),
    5:  ('Guðlaugur Magnús Ingason',  'a72b3ab04b9cfbda'),
    6:  ('Þorfinna Þrastardóttir',    '65fcd2c60e66afde'),
    7:  ('Þorgeir Bjarnason',         'ba98befdf23ab82e'),
    8:  ('Klara Mist Pálsdóttir',     '9b1da18b30382081'),
    9:  ('Jón Valgeir Baldursson',    'd77a3d9457f8ddb9'),
    10: ('Andri Viðar Víglundsson',   '30b4c95eb86df8ec'),
    11: ('Aðalbjörg Snorradóttir',    '563afc74495d1192'),
    12: ('Áki Berndsen',              '3f6839ad1463f2f9'),
    13: ('Katrín Freysdóttir',        'f88cc665f72ae54c'),
    14: ('Árni Helgason',             'a3944d8ce9c800e2'),
}

src = JS.read_text(encoding='utf-8')

# Find FJB.H block
m = re.search(r'const FJB\s*=\s*\{', src)
i = m.end() - 1; d = 0
while i < len(src):
    c = src[i]
    if c == '{': d += 1
    elif c == '}':
        d -= 1
        if d == 0: break
    i += 1
fjb_end = i + 1

hm = re.search(r'\n  H:\s*\{', src[m.end()-1:fjb_end])
hm_start = m.end() - 1 + hm.start()
j = hm_start + hm.end() - hm.start() - 1
d2 = 0; ins = None
while j < fjb_end:
    c = src[j]
    if ins:
        if c == chr(92): j += 2; continue
        if c == ins: ins = None
        j += 1; continue
    if c in ("'", '"', '`'): ins = c; j += 1; continue
    if c == '{': d2 += 1
    elif c == '}':
        d2 -= 1
        if d2 == 0: break
    j += 1
h_end = j + 1
h_block = src[hm_start:h_end]

new_block = h_block
edits = 0

for seat, (name, hash_) in PHOTOS.items():
    new_path = f"'images/candidates/{hash_}.jpg'"
    # Pattern 1: row already has a photo path → replace it
    p1 = re.compile(
        r"(\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'[^']*',\s*)"
        r"'images/candidates/[^']+'", re.S)
    m1 = p1.search(new_block)
    if m1:
        new_block = p1.sub(lambda mm: mm.group(1) + new_path, new_block, count=1)
        edits += 1
        print(f'  {seat:>2}  {name:<35}  REPLACED photo path')
        continue
    # Pattern 2: row has null in photo slot
    p2 = re.compile(
        r"(\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'[^']*',\s*)null", re.S)
    m2 = p2.search(new_block)
    if m2:
        new_block = p2.sub(lambda mm: mm.group(1) + new_path, new_block, count=1)
        edits += 1
        print(f'  {seat:>2}  {name:<35}  REPLACED null')
        continue
    # Pattern 3: row is [seat, name, occ] with no 4th element
    p3 = re.compile(
        r"\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'([^']*)'\]")
    m3 = p3.search(new_block)
    if m3:
        new_block = p3.sub(
            f"[{seat}, '{name}', '{m3.group(1)}', {new_path}]",
            new_block, count=1)
        edits += 1
        print(f'  {seat:>2}  {name:<35}  ADDED to bare row')
        continue
    print(f'  {seat:>2}  {name:<35}  NO MATCH')

if new_block != h_block:
    new_src = src[:hm_start] + new_block + src[h_end:]
    # bracket sanity
    print()
    print('braces:', new_src.count('{') - new_src.count('}'))
    print('brackets:', new_src.count('[') - new_src.count(']'))
    JS.write_text(new_src, encoding='utf-8')
    print(f'\nApplied {edits} photo paths to {JS}')
else:
    print('\nNo edits.')
