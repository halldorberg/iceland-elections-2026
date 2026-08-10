import urllib.request, re, hashlib, json, time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

orphan_hashes = [
    "07177f3466a6bdd4", "1fdfe34efa2a58a0", "374e8ac39a5d315b",
    "5805651a7ceea639", "6c85cd28322afd51", "8137bfe569d1b15e",
    "8b2d275ffe18e180", "90c3eb32ae1bcc1d", "986e09ab185abe10",
    "a7232dbfe98f9898"
]

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
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")

def extract_candidates(html):
    """Extract all candidates with their photoIds from the xd.is page JS data"""
    candidates = []

    # Find all JSON-like objects with seat and name and photoId
    # Pattern: { "seat": N, "name": "...", ..., "photoId": "..." }
    cand_pattern = re.compile(
        r'\{\s*"seat"\s*:\s*(\d+)\s*,\s*"name"\s*:\s*"([^"]+)"[^{}]*?"photoId"\s*:\s*"([^"]+)"',
        re.DOTALL
    )
    # Also try reverse order
    cand_pattern2 = re.compile(
        r'"photoId"\s*:\s*"([^"]+)"[^{}]*?"seat"\s*:\s*(\d+)\s*,\s*"name"\s*:\s*"([^"]+)"',
        re.DOTALL
    )

    for m in cand_pattern.finditer(html):
        candidates.append({"seat": int(m.group(1)), "name": m.group(2), "photoId": m.group(3)})

    if not candidates:
        for m in cand_pattern2.finditer(html):
            candidates.append({"seat": int(m.group(2)), "name": m.group(3), "photoId": m.group(1)})

    return candidates

def extract_parties(html):
    """Extract party info: party name, code, and list of candidates"""
    # Look for party blocks - each starts with a partyCode or similar
    # The structure seems to be: candidates: [ {...}, {...} ] within party blocks

    # Try to find the full JS data structure
    # Look for something like: { partyCode: "...", candidates: [...] }
    parties = []

    # Extract raw candidate blocks with surrounding context
    # Find all occurrences of "candidates:" followed by array
    # Actually, let's extract ALL candidate entries with their context

    # Find each candidate block and get context (party name) 100 chars before
    cand_blocks = []

    pattern = re.compile(
        r'"seat"\s*:\s*(\d+)\s*,\s*"name"\s*:\s*"([^"]+)"(?:[^{}]|(?:\{[^{}]*\}))*?"photoId"\s*:\s*"([^"]+)"',
        re.DOTALL
    )

    # Try a simpler JSON extraction approach
    # Find all complete candidate JSON objects
    # Look for { seat: N, name: "...", title: "...", photoId: "...", ... }

    all_cands = []

    # Use finditer with a broad pattern
    pos = 0
    while True:
        idx = html.find('"photoId"', pos)
        if idx == -1:
            break

        # Get context around this photoId
        start = max(0, idx - 500)
        end = min(len(html), idx + 200)
        snippet = html[start:end]

        # Extract photoId value
        photo_match = re.search(r'"photoId"\s*:\s*"([^"]+)"', html[idx:idx+100])
        if not photo_match:
            pos = idx + 1
            continue
        photo_id = photo_match.group(1)

        # Find seat and name in surrounding context
        seat_match = re.search(r'"seat"\s*:\s*(\d+)', snippet)
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', snippet)

        if seat_match and name_match:
            # Find party context (further back)
            party_start = max(0, idx - 2000)
            party_snippet = html[party_start:idx]
            # Look for partyCode or partyName
            party_code_match = re.findall(r'"(?:partyCode|listCode|code)"\s*:\s*"([^"]+)"', party_snippet)
            party_name_match = re.findall(r'"(?:partyName|listName|name)"\s*:\s*"([^"]+)"', party_snippet)

            all_cands.append({
                "seat": int(seat_match.group(1)),
                "name": name_match.group(1),
                "photoId": photo_id,
                "party_codes": party_code_match[-3:] if party_code_match else [],
                "party_names": party_name_match[-3:] if party_name_match else [],
            })

        pos = idx + 1

    return all_cands

def download_and_hash(photo_id):
    url = f"https://drive.google.com/uc?export=download&id={photo_id}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        if len(data) < 1000:
            return None, None, url
        h = hashlib.md5(data).hexdigest()[:16]
        return h, data, url
    except Exception as e:
        print(f"  Download error for {photo_id}: {e}")
        return None, None, url

all_matches = {}

for muni_slug, page_url in xd_pages.items():
    print(f"\n=== {muni_slug}: {page_url} ===")
    try:
        html = fetch_html(page_url)
    except Exception as e:
        print(f"  ERROR: {e}")
        continue

    candidates = extract_parties(html)
    print(f"  Found {len(candidates)} candidates with photos")

    for cand in candidates:
        photo_id = cand["photoId"]
        h, data, url = download_and_hash(photo_id)
        if h is None:
            print(f"    Seat {cand['seat']} {cand['name']}: download failed")
            continue

        match_status = " *** MATCH ***" if h in orphan_hashes else ""
        print(f"    Seat {cand['seat']} {cand['name']}: {h}{match_status}")

        if h in orphan_hashes:
            all_matches[h] = {
                "url": url,
                "page": page_url,
                "name": cand["name"],
                "seat": cand["seat"],
                "muni_slug": muni_slug,
                "party_codes": cand["party_codes"],
                "party_names": cand["party_names"],
                "photo_id": photo_id,
            }

        time.sleep(0.2)

print(f"\n\n=== MATCHES FOUND: {len(all_matches)}/{len(orphan_hashes)} ===")
for h, info in all_matches.items():
    print(f"\n{h}: {info['name']} (seat {info['seat']}, {info['muni_slug']})")
    print(f"  URL: {info['url']}")
    print(f"  Party codes context: {info['party_codes']}")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(all_matches, f, ensure_ascii=False, indent=2)

print("\nSaved to orphan_matches.json")
