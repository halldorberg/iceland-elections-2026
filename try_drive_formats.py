"""
Try many different Google Drive URL formats to find one that matches the original hashes.
The original agent downloaded images and computed md5[:16] which became the filename.
We need to find the exact URL format that reproduces those bytes.
"""
import urllib.request, re, hashlib, json, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

# Target orphan hashes (the 4 that don't match their filename = content changed)
target_hashes = {
    "374e8ac39a5d315b",
    "5805651a7ceea639",
    "8137bfe569d1b15e",
    "8b2d275ffe18e180",
}

# From the xd.is D-list pages, these are candidate photoIds
# skagafjordur D-list candidates (from earlier extraction):
skagafjordur_d_candidates = [
    (1, "Magnús Barðdal", "1VtbP2FxwwBtLkhNwwxNYJW4BgOvlHH2E"),
    (2, "Sólborg S. Borgarsdóttir", "1hRDiYnFvK4sUKu2_LGPJQGlT8aZ3MyON"),  # estimated
    (3, "Guðlaugur Skálason", "18lWl6A_46jp9fCfg1Ri1PKE5v63oBamN"),  # estimated
    (4, "Rósanna Valdimársdóttir", "1T9mIBJDtXbZBevMM45UYOxYJfDYAwVkH"),
    (6, "Guðbjörg Konráðsdóttir", "1AXbo-A7ESzCJAZawgNvLxT-ZWx-STeBE"),
    (7, "Jóhann Daði Gíslason", "1G9YPvY7nE5cLv2hT991zKxjYDNqSZA-d"),
    (9, "Anton Þorri Axelsson", "18GtlibbS8orw3rsEtFMwIxY4AOyMooXW"),
]

# Get actual photo IDs from the xd.is pages
def fetch_xd_candidates(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        html = r.read().decode("utf-8", errors="replace")

    candidates = []
    pos = 0
    while True:
        idx = html.find('"photoId"', pos)
        if idx == -1:
            break
        photo_match = re.search(r'"photoId"\s*:\s*"([^"]+)"', html[idx:idx+100])
        if not photo_match:
            pos = idx + 1
            continue
        photo_id = photo_match.group(1)
        start = max(0, idx - 500)
        snippet = html[start:idx+100]
        seat_match = re.search(r'"seat"\s*:\s*(\d+)', snippet)
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', snippet)
        if seat_match and name_match:
            candidates.append({
                "seat": int(seat_match.group(1)),
                "name": name_match.group(1),
                "photoId": photo_id,
            })
        pos = idx + 1
    return candidates

# Get all candidates from all xd.is pages
xd_pages = {
    "skagafjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "borgarbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "dalvikurbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "hunabyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "rangarthing-eystra": "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "hunathing-vestra": "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
}

all_photo_ids = {}  # photoId -> (muni, seat, name)
for muni, url in xd_pages.items():
    print(f"Fetching {muni}...")
    cands = fetch_xd_candidates(url)
    seen = set()
    for c in cands:
        pid = c["photoId"]
        if pid not in seen:
            seen.add(pid)
            all_photo_ids[pid] = (muni, c["seat"], c["name"])

print(f"\nTotal unique photo IDs: {len(all_photo_ids)}")

# Try various URL formats for each photo ID
url_formats = [
    "https://drive.google.com/uc?export=download&id={id}",
    "https://drive.google.com/uc?id={id}&export=download",
    "https://drive.google.com/uc?export=view&id={id}",
    "https://lh3.googleusercontent.com/d/{id}",
    "https://drive.google.com/thumbnail?id={id}&sz=w1200",
    "https://drive.google.com/thumbnail?id={id}&sz=w600",
    "https://drive.google.com/thumbnail?id={id}",
]

found = {}

for photo_id, (muni, seat, name) in all_photo_ids.items():
    for fmt in url_formats:
        url = fmt.format(id=photo_id)
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                data = r.read()
            if len(data) < 1000:
                continue
            h = hashlib.md5(data).hexdigest()[:16]
            if h in target_hashes:
                print(f"*** MATCH: {h} -> {muni} seat {seat} {name}")
                print(f"    URL: {url}")
                found[h] = {"url": url, "muni": muni, "seat": seat, "name": name, "photo_id": photo_id}
                break
        except Exception as e:
            continue
        time.sleep(0.1)

print(f"\n=== Found {len(found)}/{len(target_hashes)} target hashes ===")
for h, info in found.items():
    print(f"  {h}: {info['name']} ({info['muni']}, seat {info['seat']})")
