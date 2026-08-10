"""Re-crop GRN.M campaign-poster photos to remove the 'xM GRINDAVÍK NAME' footer band.

Each existing 400x400 jpg is a campaign-poster snapshot where the photo
takes the top ~78% and the bottom ~22% is a dark navy footer with
'xM GRINDAVÍK <NAME>' text. We crop the top portion and re-square to
400x400 so face detection can target the actual subject.
"""
import sys, io
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
DST = ROOT / 'images' / 'candidates'

# GRN.M campaign-poster photos (seats 2-11). Magnús's (seat 1,
# e8c52db6f43322af.jpg) was already cropped on import.
PHOTOS = [
    ('794d5f1e0403b525.jpg', 'Björn Steinar'),
    ('82d9f9eaadd1ab29.jpg', 'Gunnar Már'),
    ('41fd0bdb674946ae.jpg', 'Signý Lind'),
    ('1e9815df98ff07a3.jpg', 'Eydís'),
    ('36db8dcade1613be.jpg', 'Aníta Sif'),
    ('f685e0d8b362eb3a.jpg', 'Páll Gíslason'),
    ('8e764cb9c850f57c.jpg', 'Páll Árni'),
    ('fa4c670ff3ad7977.jpg', 'Hajie Flores'),
    ('96b104c7375f2e91.jpg', 'Andri Hrafn'),
    ('185b80acaeeb346a.jpg', 'Ragna'),
]

# Empirically: footer band is ~22% of poster height. We keep top 78%.
KEEP_RATIO = 0.78

for fn, name in PHOTOS:
    p = DST / fn
    if not p.exists():
        print(f'  {fn}  MISSING'); continue
    img = Image.open(p).convert('RGB')
    w, h = img.size
    # 1) Drop the footer band
    keep_h = int(h * KEEP_RATIO)
    no_footer = img.crop((0, 0, w, keep_h))
    # 2) Center-crop to a square within the photo region
    nw, nh = no_footer.size
    side = min(nw, nh)
    left = (nw - side) // 2
    top  = 0  # head sits near the top in poster crops
    sq = no_footer.crop((left, top, left + side, top + side))
    # 3) Resize back to 400x400 to keep filenames + paths unchanged
    if sq.size != (400, 400):
        sq = sq.resize((400, 400), Image.LANCZOS)
    sq.save(p, 'JPEG', quality=88, optimize=True)
    print(f'  {fn}  {name}  ({p.stat().st_size//1024} KB)')
