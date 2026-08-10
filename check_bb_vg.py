import urllib.request, re, hashlib, json, time, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

orphan_hashes = [
    "07177f3466a6bdd4", "1fdfe34efa2a58a0", "374e8ac39a5d315b",
    "5805651a7ceea639", "6c85cd28322afd51", "8137bfe569d1b15e",
    "8b2d275ffe18e180", "90c3eb32ae1bcc1d", "986e09ab185abe10",
    "a7232dbfe98f9898"
]

found_hashes = set()  # Track already found hashes

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace"), r.geturl()
    except Exception as e:
        return "", url

def download_and_hash(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
        if len(data) < 1000:
            return None, None
        h = hashlib.md5(data).hexdigest()[:16]
        return h, data
    except Exception:
        return None, None

def extract_all_img_urls(html, base_url):
    from urllib.parse import urlparse, urljoin
    found = set()
    # Very broad: get all URLs that look like images
    all_urls = re.findall(r'https?://[^\s\'"<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\'"<>]*)?', html, re.IGNORECASE)
    # Also get escaped versions
    escaped = re.findall(r'https?:\\/\\/[^\s\'"<>\\]+\.(?:jpg|jpeg|png|webp)', html, re.IGNORECASE)
    for u in all_urls + [e.replace('\\/','/',) for e in escaped]:
        if '1x1' not in u and 'favicon' not in u.lower():
            found.add(u)
    return list(found)

def find_context(html, url):
    filename = url.split("/")[-1].split("?")[0]
    for term in [url, filename]:
        idx = html.find(term)
        if idx != -1:
            start = max(0, idx - 500)
            end = min(len(html), idx + 500)
            snippet = html[start:end]
            text = re.sub(r'<[^>]+>', ' ', snippet)
            return re.sub(r'\s+', ' ', text).strip()[:300]
    return ""

results = {}

# Check bb.is vikuvidtal pages (weekly interview pages) - these are where candidate images appear
# Also check the bb.is categories and individual pages
bb_urls_to_check = [
    "https://bb.is/category/vikuvidtal/",
    "https://bb.is/category/vikuvidtal/page/2/",
    "https://bb.is/category/vikuvidtal/page/3/",
    "https://bb.is/category/frettir/",
]

# Also look at individual bb.is articles the previous agent found
known_bb_articles = [
    "https://bb.is/2026/04/vikuvidtalid-hlynur-arsaelsson/",
    "https://bb.is/2026/03/vikuvidtalid-jonas-thor-birgisson/",
    "https://bb.is/2026/04/vikuvidtalid-kristjan-jon-gudmundsson/",
    "https://bb.is/2026/04/vikuvidtalid-gudfinnur-ragnar-johannsson/",
    "https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/",
    "https://bb.is/2026/03/strandabyggd-framsokn-og-ohadir-bjoda-fram/",
    "https://bb.is/2026/04/isafjardarbaer-saevar-oli-efstur-a-lista-midflokksins/",
]

print("=== Checking known bb.is articles for new images ===")
for url in known_bb_articles:
    html, final_url = fetch_html(url)
    if not html:
        continue
    img_urls = extract_all_img_urls(html, final_url)
    img_urls = [u for u in img_urls if 'bb.is/wp-content' in u]
    print(f"  {url}: {len(img_urls)} images")
    for u in img_urls:
        h, data = download_and_hash(u)
        if h and h in orphan_hashes and h not in found_hashes:
            ctx_text = find_context(html, u)
            print(f"  *** MATCH: {h} -> {u}")
            results[h] = {"url": u, "page": url, "context": ctx_text}
            found_hashes.add(h)
    time.sleep(0.2)

# Now check bb.is vikuvidtal category to find more articles
print("\n=== Checking bb.is vikuvidtal category pages ===")
for bb_url in bb_urls_to_check:
    html, final_url = fetch_html(bb_url)
    if not html:
        print(f"  Failed: {bb_url}")
        continue
    # Find all article links
    article_links = re.findall(r'href=["\'](https://bb\.is/20\d\d/[^"\']+/)["\']', html)
    article_links = list(set(article_links))
    print(f"  {bb_url}: {len(article_links)} articles found")
    for link in article_links[:30]:
        art_html, _ = fetch_html(link)
        if not art_html:
            continue
        art_urls = extract_all_img_urls(art_html, link)
        art_urls = [u for u in art_urls if 'bb.is/wp-content' in u]
        for u in art_urls:
            h, data = download_and_hash(u)
            if h and h in orphan_hashes and h not in found_hashes:
                ctx_text = find_context(art_html, u)
                print(f"  *** MATCH in {link}: {h} -> {u}")
                results[h] = {"url": u, "page": link, "context": ctx_text}
                found_hashes.add(h)
        time.sleep(0.15)

# Check vg.is main page and candidate pages
print("\n=== Checking vg.is ===")
vg_urls_to_try = [
    "https://vg.is/",
    "https://vg.is/frettir/",
    "https://vg.is/frambjodendur/",
]
for url in vg_urls_to_try:
    html, final_url = fetch_html(url)
    if not html:
        print(f"  Failed: {url}")
        continue
    print(f"  {url}: {len(html)} chars, final: {final_url}")
    # Look for any image in vg.is domain
    img_urls = extract_all_img_urls(html, final_url)
    print(f"  Images: {len(img_urls)}")
    for u in img_urls[:50]:
        h, data = download_and_hash(u)
        if h and h in orphan_hashes and h not in found_hashes:
            ctx_text = find_context(html, u)
            print(f"  *** MATCH: {h} -> {u}")
            results[h] = {"url": u, "page": url, "context": ctx_text}
            found_hashes.add(h)
    time.sleep(0.2)

# Check skessuhorn.is with proper redirect handling
print("\n=== Checking skessuhorn.is ===")
skessuhorn_url = "https://www.skessuhorn.is/adsendar-greinar/"
html, final_url = fetch_html(skessuhorn_url)
if html:
    print(f"  Got HTML ({len(html)} chars), final: {final_url}")
    img_urls = extract_all_img_urls(html, final_url)
    img_urls = [u for u in img_urls if 'umsjon.skessuhorn.is' in u or 'skessuhorn.is' in u]
    print(f"  Skessuhorn images: {len(img_urls)}")
    for u in img_urls:
        h, data = download_and_hash(u)
        if h and h in orphan_hashes and h not in found_hashes:
            ctx_text = find_context(html, u)
            print(f"  *** MATCH: {h} -> {u}")
            results[h] = {"url": u, "page": skessuhorn_url, "context": ctx_text}
            found_hashes.add(h)
else:
    print(f"  Failed to fetch, trying alternative URLs...")
    # Try fetching without www
    for try_url in ["http://skessuhorn.is/adsendar-greinar/", "https://skessuhorn.is/"]:
        html, final_url = fetch_html(try_url)
        if html:
            print(f"  Got HTML ({len(html)} chars) from {try_url}, final: {final_url}")
            break

print(f"\n\n=== SUMMARY: {len(results)}/{len(orphan_hashes)} matched ===")
for h, info in results.items():
    print(f"\n{h}: {info['url']}")
    print(f"  Context: {info['context'][:150]}")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
