"""
Check additional xd.is municipality pages (beyond the 6 listed as sources) for orphan matches.
Download and save candidate photos for visual comparison.
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

# Additional xd.is pages NOT in the original 6 source pages
additional_xd_pages = {
    "reykjavik": "https://xd.is/sveitarstjornarkosningar-2026-2/reykjavikurborg-4/",
    "kopavogur": "https://xd.is/sveitarstjornarkosningar-2026-2/kopavogsbaer/",
    "gardabaer": "https://xd.is/sveitarstjornarkosningar-2026-2/gardabaer/",
    "hafnarfjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/hafnarfjardarkaupstadur/",
    "seltjarnarnes": "https://xd.is/sveitarstjornarkosningar-2026-2/seltjarnarnesbaer/",
    "mosfellsbaer": "https://xd.is/sveitarstjornarkosningar-2026-2/mosfellsbaer/",
    "vogar": "https://xd.is/sveitarstjornarkosningar-2026-2/sveitarfelagid-vogar/",
    "reykjanesbaer": "https://xd.is/sveitarstjornarkosningar-2026-2/reykjanesbaer/",
    "sudurnesjabaer": "https://xd.is/sveitarstjornarkosningar-2026-2/sudurnesjabaer/",
    "grindavik": "https://xd.is/sveitarstjornarkosningar-2026-2/grindavikurbaer/",
    "olfus": "https://xd.is/sveitarstjornarkosningar-2026-2/sveitarfelagid-olfus/",
    "hveragerdi": "https://xd.is/sveitarstjornarkosningar-2026-2/hveragerDisbaer/",
    "arborg": "https://xd.is/sveitarstjornarkosningar-2026-2/sveitarfelagid-arborg/",
    "rangarthingytra": "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-ytra/",
    "vestmannaeyjar": "https://xd.is/sveitarstjornarkosningar-2026-2/vestmannaeyjabaer/",
    "nordurthing": "https://xd.is/sveitarstjornarkosningar-2026-2/nordurthing/",
    "akureyri": "https://xd.is/sveitarstjornarkosningar-2026-2/akureyrarbaer/",
    "horgarsv": "https://xd.is/sveitarstjornarkosningar-2026-2/horgarsveit/",
    "fjallabyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/fjallabyggd/",
    "isafjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/isafjardarbaer/",
    "snaefellsbaer": "https://xd.is/sveitarstjornarkosningar-2026-2/snaefellsbaer/",
    "grundarfjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/grundarfjardarbaer/",
    "akranes": "https://xd.is/sveitarstjornarkosningar-2026-2/akraneskaupstadur/",
    "fjardabyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/fjardabyggd/",
    "mulathing": "https://xd.is/sveitarstjornarkosningar-2026-2/mulathing-3/",
}

tmp_dir = r"F:\Claude Projects\iceland-elections\tmp_candidates2"
os.makedirs(tmp_dir, exist_ok=True)

def fetch_html(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_candidates(html):
    candidates = []
    seen_ids = set()
    # Get list name
    list_name_match = re.search(r'listName\s*:\s*"([^"]+)"', html)
    list_name = list_name_match.group(1) if list_name_match else "?"

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
                "list_name": list_name,
            })
        pos = idx + 1
    return candidates

def download_photo(photo_id):
    url = f"https://drive.google.com/uc?export=download&id={photo_id}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            data = r.read()
        if len(data) < 5000:
            return None, None, url
        h = hashlib.md5(data).hexdigest()[:16]
        return h, data, url
    except:
        return None, None, None

results = {}

for muni_slug, page_url in additional_xd_pages.items():
    print(f"\n=== {muni_slug} ===")
    try:
        html = fetch_html(page_url)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    candidates = extract_candidates(html)
    if not candidates:
        print(f"  No candidates found")
        continue

    print(f"  List: {candidates[0].get('list_name', '?')}")
    print(f"  Candidates: {len(candidates)}")

    for cand in candidates:
        h, data, url = download_photo(cand['photoId'])
        if h is None:
            continue

        match = " <<< MATCH!" if h in all_orphan_hashes else ""
        print(f"  Seat {cand['seat']} {cand['name']}: {h}{match}")

        if h in all_orphan_hashes:
            results[h] = {
                "url": url,
                "page": page_url,
                "name": cand["name"],
                "seat": cand["seat"],
                "muni_slug": muni_slug,
                "list_name": cand.get("list_name", "?"),
                "photo_id": cand["photoId"],
            }

            # Save the matched image
            fname = os.path.join(tmp_dir, f"MATCH_{h}_{muni_slug}_seat{cand['seat']}.jpg")
            with open(fname, 'wb') as f:
                f.write(data)

        time.sleep(0.2)

print(f"\n\n=== MATCHES: {len(results)}/{len(all_orphan_hashes)} ===")
for h, info in results.items():
    print(f"  {h}: {info['name']} ({info['muni_slug']}, seat {info['seat']})")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved")
