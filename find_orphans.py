import urllib.request, re, hashlib, json, os, sys

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

orphan_hashes = [
    "07177f3466a6bdd4", "1fdfe34efa2a58a0", "374e8ac39a5d315b",
    "5805651a7ceea639", "6c85cd28322afd51", "8137bfe569d1b15e",
    "8b2d275ffe18e180", "90c3eb32ae1bcc1d", "986e09ab185abe10",
    "a7232dbfe98f9898"
]

source_pages = [
    "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
    "https://bb.is/?s=kosningar+2026",
    "https://skessuhorn.is/adsendar-greinar/",
    "https://vg.is/sveitarfelog/",
    "https://samfylkingin.is/kosningar/sveitarstjornarkosningar/",
]

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  FETCH ERROR: {e}")
        return ""

def extract_image_urls(html, base_url):
    """Extract all candidate image URLs from HTML"""
    # Match src, data-src, data-lazy-src etc
    pattern = r'(?:data-lazy-src|data-src|data-original|srcset|src)\s*=\s*["\']([^"\']+?\.(?:jpg|jpeg|png|webp)(?:\?[^"\']*)?)["\']'
    urls = re.findall(pattern, html, re.IGNORECASE)
    # Also find google drive URLs
    drive = re.findall(r'https?://drive\.google\.com/[^\s\'"<>&]+', html)
    # Make absolute
    result = []
    for u in urls:
        if u.startswith("http"):
            result.append(u)
        elif u.startswith("//"):
            result.append("https:" + u)
        elif u.startswith("/"):
            # relative URL
            from urllib.parse import urlparse
            p = urlparse(base_url)
            result.append(f"{p.scheme}://{p.netloc}{u}")
    for d in drive:
        # Convert to direct download
        file_id_match = re.search(r'/d/([^/]+)', d)
        if file_id_match:
            result.append(f"https://drive.google.com/uc?export=download&id={file_id_match.group(1)}")
        elif 'id=' in d:
            result.append(d if d.startswith("http") else "https://" + d)
    return list(set(result))

def download_and_hash(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        return hashlib.md5(data).hexdigest()[:16], data
    except Exception as e:
        return None, None

# Extract candidate context from HTML near images
def find_candidate_context(html, img_url):
    """Try to find candidate name near the image URL in the HTML"""
    idx = html.find(img_url)
    if idx == -1:
        # Try partial match
        partial = img_url.split("/")[-1]
        idx = html.find(partial)
    if idx == -1:
        return "Unknown"
    # Get surrounding 500 chars
    start = max(0, idx - 300)
    end = min(len(html), idx + 300)
    snippet = html[start:end]
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', snippet)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:200]

print("Starting orphan image identification...")
print(f"Looking for {len(orphan_hashes)} orphan hashes: {orphan_hashes}")
print()

results = {}  # hash -> {url, page, context}

for page_url in source_pages:
    print(f"\n=== Fetching: {page_url} ===")
    html = fetch_html(page_url)
    if not html:
        continue

    img_urls = extract_image_urls(html, page_url)
    # Filter out likely non-candidate images (logos, icons, etc)
    img_urls = [u for u in img_urls if "1x1.trans" not in u and "logo" not in u.lower() and "icon" not in u.lower()]
    print(f"  Found {len(img_urls)} potential image URLs")

    for img_url in img_urls:
        # Skip already identified
        h, data = download_and_hash(img_url)
        if h is None:
            continue
        if h in orphan_hashes:
            context = find_candidate_context(html, img_url)
            print(f"  MATCH FOUND: {h} -> {img_url}")
            print(f"    Context: {context}")
            results[h] = {"url": img_url, "page": page_url, "context": context}

print("\n\n=== SUMMARY ===")
print(f"Found {len(results)} matches out of {len(orphan_hashes)} orphans")
for h, info in results.items():
    print(f"  {h}: {info['url']}")
    print(f"    Context: {info['context'][:100]}")

# Save results
with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved to orphan_matches.json")
