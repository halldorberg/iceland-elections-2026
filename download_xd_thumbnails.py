"""
Download thumbnail versions of xd.is candidates to visually compare with orphans.
The xd.is candidates use Google Drive, which provides thumbnails via:
https://drive.google.com/thumbnail?id={photoId}&sz=w400
"""
import urllib.request, re, hashlib, json, os, time, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

def fetch_html(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

# Extract all candidates from all xd.is pages with their photoIds
xd_pages = {
    "skagafjordur": "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "borgarbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "dalvikurbyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "hunabyggd": "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "rangarthing-eystra": "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "hunathing-vestra": "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
}

orphan_files = [
    "374e8ac39a5d315b",  # Young man, dark suit, red tie, grey background, D-list pin
    "5805651a7ceea639",  # Older man, blue background, blue tie, D-list pin
    "8137bfe569d1b15e",  # Man with glasses and beard, blue background, D-list pin
    "8b2d275ffe18e180",  # Man with cap, outdoor winter Icelandic scene
    # These 6 have matching hashes - need to identify their sources differently:
    "07177f3466a6bdd4",  # Young man, grey background (bb.is or other)
    "1fdfe34efa2a58a0",  # Stocky man, wood-panel bb.is frame, green tie
    "6c85cd28322afd51",  # Man with red beard, orange background (bb.is style)
    "90c3eb32ae1bcc1d",  # Young man in blue suit, wood-panel bb.is frame
    "986e09ab185abe10",  # Older man, wood-panel bb.is frame
    "a7232dbfe98f9898",  # Woman with glasses, outdoor
]

all_candidates = []

for muni_slug, page_url in xd_pages.items():
    print(f"Fetching {muni_slug}...")
    html = fetch_html(page_url)

    # Extract all candidates with photoIds
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

        # Get context - look back for seat and name
        start = max(0, idx - 500)
        snippet = html[start:idx+100]

        seat_match = re.search(r'"seat"\s*:\s*(\d+)', snippet)
        name_match = re.search(r'"name"\s*:\s*"([^"]+)"', snippet)

        if seat_match and name_match:
            # Find party - look further back
            party_start = max(0, idx - 3000)
            party_snippet = html[party_start:idx]

            # Find the last partyCode before this candidate
            party_codes = re.findall(r'"(?:partyCode|listCode)"\s*:\s*"([^"]+)"', party_snippet)
            party_names = re.findall(r'"partyName"\s*:\s*"([^"]+)"', party_snippet)

            all_candidates.append({
                "muni_slug": muni_slug,
                "seat": int(seat_match.group(1)),
                "name": name_match.group(1),
                "photoId": photo_id,
                "party_code": party_codes[-1] if party_codes else "?",
                "party_name": party_names[-1] if party_names else "?",
            })

        pos = idx + 1

# Deduplicate by photoId
seen_ids = set()
unique_cands = []
for c in all_candidates:
    if c["photoId"] not in seen_ids:
        seen_ids.add(c["photoId"])
        unique_cands.append(c)

print(f"\nTotal unique candidates: {len(unique_cands)}")

# Now download thumbnail for each and compute hash
# Google Drive thumbnail URL (smaller, different from full download)
# Also try the direct download URL
print("\nDownloading and hashing candidate photos...")
print("Format: hash | muni | party | seat | name")

orphan_set = set(orphan_files)
results = {}

for cand in unique_cands:
    photo_id = cand["photoId"]

    # Try thumbnail URL
    thumb_url = f"https://drive.google.com/thumbnail?id={photo_id}&sz=w800"
    dl_url = f"https://drive.google.com/uc?export=download&id={photo_id}"

    for url in [thumb_url, dl_url]:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                data = r.read()
            if len(data) < 1000:
                continue
            h = hashlib.md5(data).hexdigest()[:16]
            match = " <<< MATCH" if h in orphan_set else ""
            print(f"  {h} | {cand['muni_slug']} | {cand['party_code']} | seat {cand['seat']} | {cand['name']} | {url.split('?')[0]}{match}")
            if h in orphan_set:
                results[h] = {
                    "url": url,
                    "page": xd_pages[cand["muni_slug"]],
                    "name": cand["name"],
                    "seat": cand["seat"],
                    "muni_slug": cand["muni_slug"],
                    "party_code": cand["party_code"],
                    "party_name": cand["party_name"],
                    "photo_id": photo_id,
                }
            break  # If first URL worked, skip second
        except Exception as e:
            continue

    time.sleep(0.15)

print(f"\n=== MATCHES: {len(results)}/{len(orphan_files)} ===")
for h, info in results.items():
    print(f"  {h}: {info['name']} ({info['muni_slug']}, {info['party_code']}, seat {info['seat']})")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Saved results")
