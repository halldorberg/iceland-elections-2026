"""
Download group photo and crop 18 circular portraits for SNB D-list (Sjálfstæðisflokkurinn).
Image layout: 3 rows × 6 portraits, numbered 1–18.
"""
import sys, os, hashlib, urllib.request
from PIL import Image
import io

sys.stdout.reconfigure(encoding='utf-8')

URL = "https://scontent-dub4-1.xx.fbcdn.net/v/t39.30808-6/670741721_1276874197968484_4331551733826577128_n.png?_nc_cat=100&ccb=1-7&_nc_sid=2a1932&_nc_ohc=PSXdbuQFeeQQ7kNvwFt7Sv5&_nc_oc=AdqJE0Ha0RuTdl-gHN3s-tTy1VltFPYgkwJjHSSJvD4ps7jeFBANeYPHQFsJ91HeroM&_nc_zt=23&_nc_ht=scontent-dub4-1.xx&_nc_gid=U_bT9u2CMzn3zE9vzFf2ww&_nc_ss=7b2a8&oh=00_Af0BAFmm-y4QtQh1hZxo4LI0NfGg-w1UPT5y6PlOcv2Fow&oe=69F6F81A"

OUTPUT_DIR = os.path.join('images', 'candidates')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download image
print('Downloading group photo...')
req = urllib.request.Request(URL, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
with urllib.request.urlopen(req, timeout=30) as resp:
    data = resp.read()

img = Image.open(io.BytesIO(data))
W, H = img.size
print(f'Image size: {W}×{H}')

# Portrait centers — measured from the image layout.
# 3 rows of 6, circles with number labels.
# We crop a square around each circle centre, then save.
# Tuned for 1456×816 image.
RADIUS = int(W * 0.058)   # ~95px at 1640 wide

row_y = [
    int(H * 0.238),   # row 1  (~220)  — confirmed good
    int(H * 0.490),   # row 2  (~453)
    int(H * 0.730),   # row 3  (~674)
]
col_x = [
    int(W * 0.082),   # col 1  (~134)  — confirmed good
    int(W * 0.210),   # col 2  (~344)  — confirmed good
    int(W * 0.338),   # col 3  (~554)
    int(W * 0.465),   # col 4  (~763)
    int(W * 0.593),   # col 5  (~972)
    int(W * 0.721),   # col 6  (~1182)
]

# Build ordered list: row 1 → positions 1-6, row 2 → 7-12, row 3 → 13-18
positions = []
for ry in row_y:
    for cx in col_x:
        positions.append((cx, ry))

pad = int(RADIUS * 1.08)   # slight padding outside the circle

results = []   # (position, filename)

for i, (cx, cy) in enumerate(positions):
    pos = i + 1
    left   = max(0, cx - pad)
    top    = max(0, cy - pad)
    right  = min(W, cx + pad)
    bottom = min(H, cy + pad)

    crop = img.crop((left, top, right, bottom))

    # Save as PNG
    buf = io.BytesIO()
    crop.save(buf, format='PNG')
    raw = buf.getvalue()
    fname = hashlib.md5(raw).hexdigest()[:16] + '.png'
    fpath = os.path.join(OUTPUT_DIR, fname)
    with open(fpath, 'wb') as f:
        f.write(raw)

    local = 'images/candidates/' + fname
    print(f'  #{pos:2d}: {local}')
    results.append((pos, local))

print()
print('=== candidates.js snippet (D-list SNB) ===')
names = [
    'Haukur Andreásson',
    'Haraldur Helgason',
    'Oddný Kristrún Ásgeirsdóttir',
    'María Kjartansdóttir',
    'Berglind Lára Haraldsdóttir',
    'Margrét Edda Arnardóttir',
    'Fannar Logi Waldorff Sigurðsson',
    'Arnar Geir Gestsson',
    'Sólmundur Ingi Einvarðsson',
    'Sigurður Þór Magnússon',
    'Bergljót Bára Theódórsdóttir',
    'Guðmundur Torfi Rafnsson',
    'Jónatan Már Sigurjónsson',
    'Oliwia Klaudia Fierka',
    'Bogi Jónsson',
    'Jón Kristinn Snæhólm',
    'Gunnar Hámundarson Häsler',
    'Einar Jón Pálsson',
]
for pos, path in results:
    print(f"  # {pos}: '{path}'  # {names[pos-1]}")
