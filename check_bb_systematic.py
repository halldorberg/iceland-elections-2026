"""
Systematically search bb.is for ALL 2026 election-related articles
and check their images against orphan hashes.
"""
import urllib.request, re, hashlib, json, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

target_hashes = {
    "07177f3466a6bdd4",
    "1fdfe34efa2a58a0",
    "6c85cd28322afd51",
    "90c3eb32ae1bcc1d",
    "986e09ab185abe10",
    "a7232dbfe98f9898",
}

def fetch_html(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            return r.read().decode("utf-8", errors="replace"), r.geturl()
    except Exception as e:
        return "", url

def download_hash(url):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
        if len(data) < 2000:
            return None
        return hashlib.md5(data).hexdigest()[:16]
    except:
        return None

def find_ctx(html, url):
    fname = url.split("/")[-1].split("?")[0]
    for term in [url, fname]:
        idx = html.find(term)
        if idx != -1:
            snippet = html[max(0,idx-400):min(len(html),idx+400)]
            text = re.sub(r'<[^>]+>', ' ', snippet)
            return re.sub(r'\s+', ' ', text).strip()[:300]
    return ""

results = {}
checked_imgs = set()
checked_articles = set()

def check_article(url):
    if url in checked_articles:
        return
    checked_articles.add(url)

    html, final_url = fetch_html(url)
    if not html or len(html) < 5000:
        return

    # Get all bb.is images
    imgs = set(re.findall(r'https?://bb\.is/wp-content/[^\s\'"<>]+\.(?:jpg|jpeg|png|webp)', html, re.IGNORECASE))

    for img_url in imgs:
        if img_url in checked_imgs:
            continue
        checked_imgs.add(img_url)

        h = download_hash(img_url)
        if h and h in target_hashes and h not in results:
            ctx_text = find_ctx(html, img_url)
            print(f"\n*** MATCH: {h}")
            print(f"    URL: {img_url}")
            print(f"    Article: {url}")
            print(f"    Context: {ctx_text[:150]}")
            results[h] = {"url": img_url, "page": url, "context": ctx_text}
    time.sleep(0.15)

# Strategy 1: Search bb.is for various election keywords
search_queries = [
    "kosningar+2026",
    "vikuvidtalid+2026",
    "frambjodandi+2026",
    "sveitarstjornarkosningar",
    "oddviti+2026",
]

article_urls = set()

for q in search_queries:
    for page in range(1, 5):
        url = f"https://bb.is/?s={q}&paged={page}" if page > 1 else f"https://bb.is/?s={q}"
        html, _ = fetch_html(url)
        if not html:
            continue
        links = re.findall(r'href=["\'](https://bb\.is/20\d\d/\d\d/[^"\']+/)["\']', html)
        for l in set(links):
            article_urls.add(l)
    time.sleep(0.2)

# Strategy 2: Look at bb.is sitemap or archive for 2026 articles
for month in ["2026/01", "2026/02", "2026/03", "2026/04"]:
    url = f"https://bb.is/{month}/"
    html, _ = fetch_html(url)
    if html:
        links = re.findall(r'href=["\'](https://bb\.is/20\d\d/\d\d/[^"\']+/)["\']', html)
        for l in set(links):
            article_urls.add(l)
    time.sleep(0.2)

print(f"Found {len(article_urls)} bb.is article URLs to check")

# Check all articles
for url in sorted(article_urls):
    check_article(url)

print(f"\n=== RESULTS: {len(results)}/{len(target_hashes)} matched ===")
for h, info in results.items():
    print(f"\n{h}:")
    print(f"  URL: {info['url']}")
    print(f"  Article: {info['page']}")
    print(f"  Context: {info['context'][:100]}")

with open("F:/Claude Projects/iceland-elections/orphan_matches_bb2.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
