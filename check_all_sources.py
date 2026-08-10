import urllib.request, re, hashlib, json, time, ssl

# Create SSL context that's permissive
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

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace"), r.geturl()
    except urllib.error.HTTPError as e:
        if e.code == 308:
            loc = e.headers.get("Location", "")
            print(f"  308 redirect to: {loc}")
            if loc:
                return fetch_html(loc)
        print(f"  HTTP Error: {e.code} {e.reason}")
        return "", url
    except Exception as e:
        print(f"  Error: {e}")
        return "", url

def download_and_hash(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
        if len(data) < 500:
            return None, None
        h = hashlib.md5(data).hexdigest()[:16]
        return h, data
    except Exception as e:
        return None, None

def extract_image_urls(html, base_url):
    from urllib.parse import urlparse, urljoin
    patterns = [
        r'data-lazy-src=["\']([^"\']+)["\']',
        r'data-src=["\']([^"\']+)["\']',
        r'data-original=["\']([^"\']+)["\']',
        r'<img[^>]+src=["\']([^"\']+)["\']',
        r'srcset=["\']([^"\']+)["\']',
    ]
    found = set()
    for pat in patterns:
        for m in re.findall(pat, html, re.IGNORECASE):
            for part in m.split(','):
                u = part.strip().split(' ')[0].strip()
                if u and not u.startswith('data:') and not '1x1.trans' in u:
                    if u.startswith('//'):
                        u = 'https:' + u
                    elif u.startswith('/'):
                        p = urlparse(base_url)
                        u = f"{p.scheme}://{p.netloc}{u}"
                    elif not u.startswith('http'):
                        u = urljoin(base_url, u)
                    if re.search(r'\.(jpg|jpeg|png|webp)', u, re.IGNORECASE):
                        if 'favicon' not in u.lower() and 'logo' not in u.lower():
                            found.add(u)
    return list(found)

def find_context(html, url):
    filename = url.split("/")[-1].split("?")[0]
    for term in [url, filename]:
        idx = html.find(term)
        if idx != -1:
            start = max(0, idx - 400)
            end = min(len(html), idx + 400)
            snippet = html[start:end]
            text = re.sub(r'<[^>]+>', ' ', snippet)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:300]
    return ""

results = {}

# 1. Check skessuhorn.is adsendar-greinar with redirect handling
print("\n=== skessuhorn.is/adsendar-greinar/ ===")
html, final_url = fetch_html("https://skessuhorn.is/adsendar-greinar/")
if html:
    print(f"  Got HTML ({len(html)} chars), final URL: {final_url}")
    urls = extract_image_urls(html, final_url)
    print(f"  Image URLs: {len(urls)}")
    for u in urls:
        h, data = download_and_hash(u)
        if h and h in orphan_hashes:
            ctx_text = find_context(html, u)
            print(f"  *** MATCH: {h} -> {u}")
            results[h] = {"url": u, "page": "https://skessuhorn.is/adsendar-greinar/", "context": ctx_text}

# 2. Check bb.is search results pages - look at multiple pages
for page_num in ["", "&paged=2", "&paged=3"]:
    bb_url = f"https://bb.is/?s=kosningar+2026{page_num}"
    print(f"\n=== {bb_url} ===")
    html, final_url = fetch_html(bb_url)
    if not html:
        continue
    print(f"  Got HTML ({len(html)} chars)")
    urls = extract_image_urls(html, final_url)
    print(f"  Image URLs: {len(urls)}")
    for u in urls:
        if any(ext in u.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            h, data = download_and_hash(u)
            if h and h in orphan_hashes:
                ctx_text = find_context(html, u)
                print(f"  *** MATCH: {h} -> {u}")
                results[h] = {"url": u, "page": bb_url, "context": ctx_text}
    time.sleep(0.3)

# 3. Look at individual bb.is articles that might have candidate photos
# Search for 2026 kosningar articles
print(f"\n=== bb.is - extracting article links ===")
html, _ = fetch_html("https://bb.is/?s=kosningar+2026")
if html:
    article_links = re.findall(r'href=["\'](' + re.escape("https://bb.is/") + r'[^"\']+)["\']', html)
    article_links = [l for l in set(article_links) if "2026" in l or "kosning" in l.lower() or "vikuvidtal" in l.lower()]
    print(f"  Found {len(article_links)} article links")
    for link in article_links[:20]:
        print(f"    {link}")
        art_html, _ = fetch_html(link)
        if not art_html:
            continue
        art_urls = extract_image_urls(art_html, link)
        for u in art_urls:
            h, data = download_and_hash(u)
            if h and h in orphan_hashes:
                ctx_text = find_context(art_html, u)
                print(f"  *** MATCH in {link}: {h} -> {u}")
                results[h] = {"url": u, "page": link, "context": ctx_text}
        time.sleep(0.2)

# 4. Check xs.is (Samfylkingin)
print(f"\n=== xs.is (Samfylkingin) ===")
html, final_url = fetch_html("https://xs.is/")
if html:
    print(f"  Got HTML ({len(html)} chars)")
    # Find all internal links about local elections
    links = re.findall(r'href=["\']([^"\']+/(?:sveitarfelog|kosningar|frambjodendur)[^"\']*)["\']', html)
    links = list(set(links))[:30]
    print(f"  Candidate page links: {len(links)}")
    for link in links:
        if not link.startswith("http"):
            link = "https://xs.is" + link
        print(f"    Checking: {link}")
        page_html, _ = fetch_html(link)
        if page_html:
            page_urls = extract_image_urls(page_html, link)
            for u in page_urls:
                h, data = download_and_hash(u)
                if h and h in orphan_hashes:
                    ctx_text = find_context(page_html, u)
                    print(f"  *** MATCH: {h} -> {u}")
                    results[h] = {"url": u, "page": link, "context": ctx_text}
        time.sleep(0.2)

# 5. Check vg.is (Vinstri Grænir)
print(f"\n=== vg.is ===")
for vg_url in ["https://vg.is/", "https://vg.is/kosningar/", "https://vg.is/sveitarstjornarkosningar/"]:
    html, final_url = fetch_html(vg_url)
    if html:
        print(f"  {vg_url}: Got HTML ({len(html)} chars)")
        urls = extract_image_urls(html, final_url)
        for u in urls:
            h, data = download_and_hash(u)
            if h and h in orphan_hashes:
                ctx_text = find_context(html, u)
                print(f"  *** MATCH: {h} -> {u}")
                results[h] = {"url": u, "page": vg_url, "context": ctx_text}

print(f"\n\n=== FINAL SUMMARY: {len(results)}/{len(orphan_hashes)} matched ===")
for h, info in results.items():
    print(f"\n{h}: {info['url']}")
    print(f"  Context: {info['context'][:100]}")

with open("F:/Claude Projects/iceland-elections/orphan_matches.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved to orphan_matches.json")
