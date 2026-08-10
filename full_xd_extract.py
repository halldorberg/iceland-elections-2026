"""
Full extraction of xd.is candidate data with party names and photoIds.
Download photos and match against all 10 orphan hashes.
The xd.is pages serve the D-list (Sjálfstæðisflokkurinn) only for each municipality.
"""
import urllib.request, re, hashlib, json, ssl, time, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

all_orphan_hashes = {
    "07177f3466a6bdd4", "1fdfe34efa2a58a0", "374e8ac39a5d315b",
    "5805651a7ceea639", "6c85cd28322afd51", "8137bfe569d1b15e",
    "8b2d275ffe18e180", "90c3eb32ae1bcc1d", "986e09ab185abe10",
    "a7232dbfe98f9898"
}

xd_pages = {
    "skagafjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "borgarbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "dalvikurbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "hunabyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "rangarthing-eystra": "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "hunathing-vestra": "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
}

def fetch_html(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_xd_data(html):
    """Extract the XDM_DATA JS structure"""
    # Find the script tag with XDM_DATA
    idx = html.find("XDM_DATA")
    if idx == -1:
        return None

    # Find listName
    list_name_match = re.search(r'listName\s*:\s*"([^"]+)"', html[idx:idx+500])
    list_name = list_name_match.group(1) if list_name_match else "Unknown"

    # Extract all candidates
    candidates = []
    pos = html.find('"candidates"', idx)
    if pos == -1:
        pos = html.find('candidates:', idx)

    # Find all photoId entries after candidates
    photo_pos = pos
    while True:
        pidx = html.find('"photoId"', photo_pos)
        if pidx == -1 or pidx > idx + 20000:
            break
        photo_match = re.search(r'"photoId"\s*:\s*"([^"]+)"', html[pidx:pidx+100])
        if not photo_match:
            photo_pos = pidx + 1
            continue
        photo_id = photo_match.group(1)

        # Find seat and name nearby
        snippet = html[max(pos, pidx-400):pidx+200]
        seat_match = re.search(r'"seat"\s*:\s*(\d+)', snippet)
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', snippet)

        if seat_match and name_match:
            candidates.append({
                "seat": int(seat_match.group(1)),
                "name": name_match.group(1),
                "photoId": photo_id,
            })
        photo_pos = pidx + 1

    return {"listName": list_name, "candidates": candidates}

def download_photo(photo_id):
    """Try multiple URL formats to get the photo"""
    urls = [
        f"https://drive.google.com/uc?export=download&id={photo_id}",
        f"https://drive.google.com/uc?export=view&id={photo_id}",
        f"https://lh3.googleusercontent.com/d/{photo_id}",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                data = r.read()
            if len(data) > 5000 and data[:3] in [b'\xff\xd8\xff', b'\x89PN', b'GIF']:
                # Valid image (JPEG, PNG, or GIF magic bytes)
                return hashlib.md5(data).hexdigest()[:16], data, url
            if len(data) > 5000:
                # Check if it might be a valid image despite magic bytes
                h = hashlib.md5(data).hexdigest()[:16]
                return h, data, url
        except Exception as e:
            continue
    return None, None, None

results = {}
all_candidates_info = []

for muni_slug, page_url in xd_pages.items():
    print(f"\n=== {muni_slug} ===")
    html = fetch_html(page_url)
    data = extract_xd_data(html)
    if not data:
        print("  No data found")
        continue

    list_name = data["listName"]
    candidates = data["candidates"]
    print(f"  List: {list_name}")
    print(f"  Candidates with photos: {len(candidates)}")

    seen_ids = set()
    for cand in candidates:
        pid = cand["photoId"]
        if pid in seen_ids:
            continue
        seen_ids.add(pid)

        h, img_data, url = download_photo(pid)
        if h is None:
            print(f"  Seat {cand['seat']} {cand['name']}: DOWNLOAD FAILED")
            continue

        match = " <<< ORPHAN MATCH!" if h in all_orphan_hashes else ""
        print(f"  Seat {cand['seat']} {cand['name']}: {h}{match}")

        all_candidates_info.append({
            "muni_slug": muni_slug,
            "list_name": list_name,
            "seat": cand["seat"],
            "name": cand["name"],
            "photo_id": pid,
            "hash": h,
            "photo_url": url,
        })

        if h in all_orphan_hashes:
            results[h] = {
                "url": url,
                "page": page_url,
                "name": cand["name"],
                "seat": cand["seat"],
                "muni_slug": muni_slug,
                "list_name": list_name,
                "photo_id": pid,
            }

        time.sleep(0.2)

print(f"\n\n=== MATCHES: {len(results)}/{len(all_orphan_hashes)} ===")
for h, info in results.items():
    print(f"  {h}: {info['name']} (seat {info['seat']}, {info['muni_slug']})")
    print(f"    List: {info['list_name']}")
    print(f"    URL: {info['url']}")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

with open("F:/Claude Projects/iceland-elections/all_xd_candidates.json", "w", encoding="utf-8") as f:
    json.dump(all_candidates_info, f, ensure_ascii=False, indent=2)

print("\nSaved results")
