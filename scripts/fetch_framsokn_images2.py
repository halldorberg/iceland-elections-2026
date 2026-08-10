"""Fetch all candidate images from the Framsókn Suðurnesjabaer listing page."""
import sys, urllib.request, re, hashlib, os, io
from urllib.parse import urlparse
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join('images', 'candidates')
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Known candidate image URLs from profile pages (first 6)
KNOWN = {
    1:  'https://framerusercontent.com/images/wwDleJCJhmrik2Yw11iX6ybyuaI.jpg?width=800',
    2:  'https://framerusercontent.com/images/br9QFnALaeiCqktFSA3H1wbnM.jpg?width=800',
    3:  'https://framerusercontent.com/images/G9KUbhN7AJ65XYKvl3An2DtDY.jpg?width=800',
    4:  'https://framerusercontent.com/images/qmyOJMFKQp0EYFY3b9IXDbBQUg.jpg?width=800',
    5:  'https://framerusercontent.com/images/VHRDbwDG78TBgYmw2uqvWlvo0E.jpg?width=800',
    6:  'https://framerusercontent.com/images/VasoBneHkogLKtCxJKmFUlWSM.jpg?width=800',
}

NAMES = [
    'Anton Kristinn Guðmundsson',
    'Magnús Sigfús Magnússon',
    'Ólöf Ólafsdóttir',
    'Sindri Lars Ómarsson',
    'Ewa Krysztopa',
    'Gísli Jónatan Pálsson',
    'Óskar Helgason',
    'Þórsteina Þöll Árnadóttir',
    'Guðrún Sif Pétursdóttir',
    'Gissur Þór Grétarsson',
    'Bjarki Dagsson',
    'Gunnlaug María Óskarsdóttir',
    'Róbert Páll Arason',
    'Bylgja Dröfn Olsen Jónsdóttir',
    'Hallur Jónas Gunnarsson',
    'Guðrún Elva Friðriksdóttir',
    'Haraldur Hinriksson',
    'Guðjón Ólafsson',
]

# Fetch main listing page to get images for candidates 7-18
print('Fetching main listing page...')
req = urllib.request.Request('https://www.framsokn.is/sveitarfelog/sudurnesjabaer', headers=HEADERS)
with urllib.request.urlopen(req, timeout=20) as resp:
    html = resp.read().decode('utf-8', errors='replace')

# Find all framerusercontent image URLs
all_imgs = re.findall(r'https://framerusercontent\.com/images/[A-Za-z0-9]+\.(?:jpg|jpeg|png|webp)(?:\?[^"\'<>\s&]*)?', html)
# Clean up HTML entities
all_imgs = [i.replace('&amp;', '&') for i in all_imgs]

# Deduplicate preserving order
seen = set()
unique_imgs = []
for img in all_imgs:
    base = img.split('?')[0]
    if base not in seen:
        seen.add(base)
        unique_imgs.append(img)

print(f'Found {len(unique_imgs)} unique images on listing page:')
for i, u in enumerate(unique_imgs):
    print(f'  {i}: {u}')

# Download known images (1-6)
print('\nDownloading candidate images...')
results = {}

for pos, url in KNOWN.items():
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        ext = 'jpg' if '.jpg' in url else 'png'
        fname = hashlib.md5(data).hexdigest()[:16] + '.' + ext
        with open(os.path.join(OUTPUT_DIR, fname), 'wb') as f:
            f.write(data)
        results[pos] = 'images/candidates/' + fname
        print(f'  #{pos} {NAMES[pos-1]}: {fname} ({len(data)//1024}KB)')
    except Exception as e:
        print(f'  #{pos} {NAMES[pos-1]}: ERROR - {e}')
        results[pos] = None
