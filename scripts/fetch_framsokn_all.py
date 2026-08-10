"""Download all 18 Framsókn SNB candidate images from the listing page."""
import sys, urllib.request, re, hashlib, os
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join('images', 'candidates')
os.makedirs(OUTPUT_DIR, exist_ok=True)
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Ordered candidate images from listing page (indices 3–18 = candidates 1–16,
# then individual profile pages for 17-18 if they exist)
CANDIDATE_URLS = [
    'https://framerusercontent.com/images/wwDleJCJhmrik2Yw11iX6ybyuaI.jpg',   # 1 Anton
    'https://framerusercontent.com/images/br9QFnALaeiCqktFSA3H1wbnM.jpg',    # 2 Magnús
    'https://framerusercontent.com/images/G9KUbhN7AJ65XYKvl3An2DtDY.jpg',    # 3 Ólöf
    'https://framerusercontent.com/images/qmyOJMFKQp0EYFY3b9IXDbBQUg.jpg',   # 4 Sindri
    'https://framerusercontent.com/images/VHRDbwDG78TBgYmw2uqvWlvo0E.jpg',   # 5 Ewa
    'https://framerusercontent.com/images/VasoBneHkogLKtCxJKmFUlWSM.jpg',    # 6 Gísli
    'https://framerusercontent.com/images/vcO6d0nVczIaJVFV64ZiAdQ0io.jpg',   # 7 Óskar
    'https://framerusercontent.com/images/uCDcpkoB08MMrBKtfJ4s9rg1m4.jpg',   # 8 Þórsteina
    'https://framerusercontent.com/images/WH8Ol3ZJ9vpu7l2bQGYBugJ5OzM.jpg',  # 9 Guðrún Sif
    'https://framerusercontent.com/images/2miKmP0gZrRN4PPZL1bVTWZqlU.jpg',   # 10 Gissur
    'https://framerusercontent.com/images/cZTzM5PUOCTs278ILtltVJnDGFk.jpg',  # 11 Bjarki
    'https://framerusercontent.com/images/KrlAN3yEolSW4aImJT9f3tv130.png',   # 12 Gunnlaug
    'https://framerusercontent.com/images/hvAGOjAlgeP5CsgCCi8D8nqqnmM.png',  # 13 Róbert
    'https://framerusercontent.com/images/VuIjTZkhBgrHHMVbsu9INrqzl0I.jpg',  # 14 Bylgja
    'https://framerusercontent.com/images/kMgIECW2nAihPZbzubMFEuJrZ0.png',   # 15 Hallur
    'https://framerusercontent.com/images/hIJVNSHf7baUhhCdbeePwZVxQY.jpg',   # 16 Guðrún Elva
]

NAMES = [
    'Anton Kristinn Guðmundsson', 'Magnús Sigfús Magnússon', 'Ólöf Ólafsdóttir',
    'Sindri Lars Ómarsson', 'Ewa Krysztopa', 'Gísli Jónatan Pálsson',
    'Óskar Helgason', 'Þórsteina Þöll Árnadóttir', 'Guðrún Sif Pétursdóttir',
    'Gissur Þór Grétarsson', 'Bjarki Dagsson', 'Gunnlaug María Óskarsdóttir',
    'Róbert Páll Arason', 'Bylgja Dröfn Olsen Jónsdóttir', 'Hallur Jónas Gunnarsson',
    'Guðrún Elva Friðriksdóttir', 'Haraldur Hinriksson', 'Guðjón Ólafsson',
]

results = {}

for i, url in enumerate(CANDIDATE_URLS):
    pos = i + 1
    name = NAMES[i]
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
        ext = 'png' if url.endswith('.png') else 'jpg'
        fname = hashlib.md5(data).hexdigest()[:16] + '.' + ext
        fpath = os.path.join(OUTPUT_DIR, fname)
        with open(fpath, 'wb') as f:
            f.write(data)
        results[pos] = 'images/candidates/' + fname
        print(f'  #{pos:2d} {name}: {fname} ({len(data)//1024}KB)')
    except Exception as e:
        results[pos] = None
        print(f'  #{pos:2d} {name}: ERROR - {e}')

# Candidates 17-18: try their profile pages
for pos, slug in [(17, 'haraldur-hinriksson'), (18, 'gudjon-olafsson')]:
    url = f'https://www.framsokn.is/{slug}'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        imgs = re.findall(r'https://framerusercontent\.com/images/[A-Za-z0-9]+\.(?:jpg|jpeg|png)', html)
        # Skip logos (known logo IDs)
        logos = {'dIx821OlNMay4cQgysKMNgLeU6U', 'L8TAkbFHPfmbXNjM2AFOgct6I'}
        candidate_imgs = [i for i in imgs if i.split('/')[-1].split('.')[0] not in logos]
        if candidate_imgs:
            img_url = candidate_imgs[0]
            req2 = urllib.request.Request(img_url, headers=HEADERS)
            with urllib.request.urlopen(req2, timeout=15) as resp2:
                data = resp2.read()
            ext = 'png' if img_url.endswith('.png') else 'jpg'
            fname = hashlib.md5(data).hexdigest()[:16] + '.' + ext
            with open(os.path.join(OUTPUT_DIR, fname), 'wb') as f:
                f.write(data)
            results[pos] = 'images/candidates/' + fname
            print(f'  #{pos:2d} {NAMES[pos-1]}: {fname} ({len(data)//1024}KB)')
        else:
            results[pos] = None
            print(f'  #{pos:2d} {NAMES[pos-1]}: no image found on profile page')
    except Exception as e:
        results[pos] = None
        print(f'  #{pos:2d} {NAMES[pos-1]}: ERROR - {e}')

print('\n=== Results ===')
for pos in range(1, 19):
    print(f'  #{pos:2d} {NAMES[pos-1]}: {results.get(pos) or "NO IMAGE"}')
