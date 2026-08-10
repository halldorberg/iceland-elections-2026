"""Extract candidate data from Ísafjörður xd.is page"""
import urllib.request, re, ssl, hashlib, json, time

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

# Extended list of xd.is pages to check
pages_to_check = {
    "isafjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/isafjardarbaer/",
    "akureyri": "https://xd.is/sveitarstjornarkosningar-2026-2/akureyrarbaer/",
    "kopavogur": "https://xd.is/sveitarstjornarkosningar-2026-2/kopavogsbaer/",
    "gardabaer": "https://xd.is/sveitarstjornarkosningar-2026-2/gardabaer/",
    "hafnarfjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/hafnarfjardarkaupstadur/",
    "reykjavik": "https://xd.is/sveitarstjornarkosningar-2026-2/reykjavikurborg-4/",
    "akranes": "https://xd.is/sveitarstjornarkosningar-2026-2/akraneskaupstadur/",
    "horgarsveit": "https://xd.is/sveitarstjornarkosningar-2026-2/horgarsveit/",
    "hveragerdi": "https://xd.is/sveitarstjornarkosningar-2026-2/hveragerDisbaer/",
    "vestmannaeyjar": "https://xd.is/sveitarstjornarkosningar-2026-2/vestmannaeyjabaer/",
    "nordurthing": "https://xd.is/sveitarstjornarkosningar-2026-2/nordurthing/",
    "sudurnesjabaer": "https://xd.is/sveitarstjornarkosningar-2026-2/sudurnesjabaer/",
    "grindavik": "https://xd.is/sveitarstjornarkosningar-2026-2/grindavikurbaer/",
    "arborg": "https://xd.is/sveitarstjornarkosningar-2026-2/sveitarfelagid-arborg/",
    "olfus": "https://xd.is/sveitarstjornarkosningar-2026-2/sveitarfelagid-olfus/",
    "seltjarnarnes": "https://xd.is/sveitarstjornarkosningar-2026-2/seltjarnarnesbaer/",
    "mosfellsbaer": "https://xd.is/sveitarstjornarkosningar-2026-2/mosfellsbaer/",
}

def fetch_html(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_candidates(html):
    candidates = []
    seen_ids = set()
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

for muni_slug, page_url in pages_to_check.items():
    print(f"\n=== {muni_slug} ===")
    try:
        html = fetch_html(page_url)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    candidates = extract_candidates(html)
    if not candidates:
        print(f"  No candidates with photos")
        continue

    print(f"  List: {candidates[0].get('list_name', '?')}")
    print(f"  {len(candidates)} candidates")

    for cand in candidates:
        h, data, url = download_photo(cand['photoId'])
        if h is None:
            continue

        match = " <<< MATCH!" if h in all_orphan_hashes else ""
        if h in all_orphan_hashes:
            print(f"  Seat {cand['seat']} {cand['name']}: {h}{match}")
            results[h] = {
                "url": url,
                "page": page_url,
                "name": cand["name"],
                "seat": cand["seat"],
                "muni_slug": muni_slug,
                "list_name": cand.get("list_name", "?"),
                "photo_id": cand["photoId"],
            }
        time.sleep(0.2)

print(f"\n=== MATCHES: {len(results)} ===")
for h, info in results.items():
    print(f"  {h}: {info['name']} ({info['muni_slug']}, seat {info['seat']})")

with open("F:/Claude Projects/iceland-elections/orphan_matches_extended.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
