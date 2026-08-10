"""
Download all xd.is candidate photos to disk for visual comparison.
Save as tmp/{muni}_{seat}_{name}.jpg
"""
import urllib.request, re, hashlib, json, ssl, time, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

tmp_dir = r"F:\Claude Projects\iceland-elections\tmp_candidates"
os.makedirs(tmp_dir, exist_ok=True)

xd_pages = {
    "ska": "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "bor": "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "dal": "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "hun": "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "ran": "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "hvv": "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
}

def fetch_html(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_candidates(html):
    candidates = []
    seen_ids = set()
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
        if photo_id in seen_ids:
            pos = idx + 1
            continue
        seen_ids.add(photo_id)

        snippet = html[max(0, idx-400):idx+200]
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

def download_photo(photo_id, save_path):
    url = f"https://drive.google.com/uc?export=download&id={photo_id}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            data = r.read()
        if len(data) < 5000:
            return False
        with open(save_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Skip candidates already identified in results file
already_done = {
    "ska_1", "bor_1", "dal_1", "hun_1", "ran_1", "hvv_1"  # seat 1 of each
}

for muni, page_url in xd_pages.items():
    print(f"\n{muni}:")
    html = fetch_html(page_url)
    candidates = extract_candidates(html)

    for cand in candidates:
        key = f"{muni}_{cand['seat']}"
        # Clean name for filename
        name_clean = re.sub(r'[^\w\s-]', '', cand['name']).strip()[:30]
        fname = f"{muni}_seat{cand['seat']:02d}_{name_clean}.jpg"
        save_path = os.path.join(tmp_dir, fname)

        if os.path.exists(save_path):
            print(f"  Seat {cand['seat']} {cand['name']}: already exists")
            continue

        success = download_photo(cand['photoId'], save_path)
        if success:
            # Compute hash
            with open(save_path, 'rb') as f:
                data = f.read()
            h = hashlib.md5(data).hexdigest()[:16]
            print(f"  Seat {cand['seat']} {cand['name']}: saved ({h})")
        else:
            print(f"  Seat {cand['seat']} {cand['name']}: FAILED")
        time.sleep(0.3)

print("\nDone. Check F:/Claude Projects/iceland-elections/tmp_candidates/")
