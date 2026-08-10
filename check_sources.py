import urllib.request, re, hashlib, json, os, time

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

orphan_hashes = [
    "07177f3466a6bdd4", "1fdfe34efa2a58a0", "374e8ac39a5d315b",
    "5805651a7ceea639", "6c85cd28322afd51", "8137bfe569d1b15e",
    "8b2d275ffe18e180", "90c3eb32ae1bcc1d", "986e09ab185abe10",
    "a7232dbfe98f9898"
]

def fetch_html(url, follow_redirects=True):
    try:
        opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
        req = urllib.request.Request(url, headers=headers)
        with opener.open(req, timeout=20) as r:
            return r.read().decode("utf-8", errors="replace"), r.geturl()
    except Exception as e:
        print(f"  FETCH ERROR {url}: {e}")
        return "", url

def extract_image_urls(html, base_url):
    """Extract all image URLs from HTML"""
    from urllib.parse import urlparse, urljoin
    # Match various image src attributes
    patterns = [
        r'data-lazy-src=["\']([^"\']+)["\']',
        r'data-src=["\']([^"\']+)["\']',
        r'data-original=["\']([^"\']+)["\']',
        r'srcset=["\']([^"\']+)["\']',
        r'<img[^>]+src=["\']([^"\']+)["\']',
        r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)',
    ]
    found = set()
    for pat in patterns:
        matches = re.findall(pat, html, re.IGNORECASE)
        for m in matches:
            # srcset may have multiple URLs
            for part in m.split(','):
                u = part.strip().split(' ')[0].strip()
                if u and not u.startswith('data:'):
                    if u.startswith('//'):
                        u = 'https:' + u
                    elif u.startswith('/'):
                        p = urlparse(base_url)
                        u = f"{p.scheme}://{p.netloc}{u}"
                    elif not u.startswith('http'):
                        u = urljoin(base_url, u)
                    if re.search(r'\.(jpg|jpeg|png|webp|JPG|PNG|JPEG|WEBP)', u):
                        found.add(u)

    # Google Drive links
    drive_matches = re.findall(r'https?://drive\.google\.com/[^\s\'"<>&]+', html)
    for d in drive_matches:
        file_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', d)
        if file_id_match:
            found.add(f"https://drive.google.com/uc?export=download&id={file_id_match.group(1)}")
        elif 'id=' in d:
            found.add(d)

    return list(found)

def download_and_hash(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
        if len(data) < 1000:  # Skip tiny images (icons, etc)
            return None, None
        h = hashlib.md5(data).hexdigest()[:16]
        return h, data
    except Exception as e:
        return None, None

def find_candidate_context(html, img_url):
    """Find candidate name near image URL in HTML"""
    # Try to find the URL or filename in the HTML
    search_terms = [img_url, img_url.split("/")[-1].split("?")[0]]
    for term in search_terms:
        idx = html.find(term)
        if idx != -1:
            start = max(0, idx - 500)
            end = min(len(html), idx + 500)
            snippet = html[start:end]
            text = re.sub(r'<[^>]+>', ' ', snippet)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:300]
    return "Context not found"

# Pages to check
source_pages = [
    "https://skessuhorn.is/adsendar-greinar/",
    "https://bb.is/?s=kosningar+2026",
    "https://xs.is/",
    "https://samfylkingin.is/kosningar/sveitarstjornarkosningar/",
]

# Also check the xd.is pages by getting their full HTML including JS data
xd_pages = [
    "https://xd.is/sveitarstjornarkosningar-2026-2/skagafjordur/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/borgarbyggd/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/dalvikurbyggd/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/hunabyggd/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/rangarthing-eystra/",
    "https://xd.is/sveitarstjornarkosningar-2026-2/hunathing-vestra/",
]

all_pages = xd_pages + source_pages

results = {}
checked_urls = set()

for page_url in all_pages:
    print(f"\n=== Fetching: {page_url} ===")
    html, final_url = fetch_html(page_url)
    if not html:
        continue

    print(f"  Final URL: {final_url}, HTML size: {len(html)} chars")

    img_urls = extract_image_urls(html, final_url)
    # Filter out small/irrelevant images
    img_urls = [u for u in img_urls
                if "1x1.trans" not in u
                and "favicon" not in u.lower()
                and "logo" not in u.lower()
                and "banner" not in u.lower()
                and u not in checked_urls]

    print(f"  Found {len(img_urls)} candidate image URLs to check")

    for img_url in img_urls:
        checked_urls.add(img_url)
        h, data = download_and_hash(img_url)
        if h is None:
            continue
        if h in orphan_hashes:
            context = find_candidate_context(html, img_url)
            print(f"\n  *** MATCH FOUND: {h} ***")
            print(f"  URL: {img_url}")
            print(f"  Page: {page_url}")
            print(f"  Context: {context[:150]}")
            results[h] = {
                "url": img_url,
                "page": page_url,
                "context": context
            }
        time.sleep(0.1)

print(f"\n\n=== FINAL SUMMARY ===")
print(f"Matched {len(results)}/{len(orphan_hashes)} orphan hashes")
for h, info in results.items():
    print(f"\n{h}:")
    print(f"  URL: {info['url']}")
    print(f"  Context: {info['context'][:100]}")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved to orphan_matches.json")
