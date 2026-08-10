"""
Systematically check bb.is vikuvidtal articles for 2026 and download all candidate images
to find matches for the 6 orphan files with matching hashes.
"""
import urllib.request, re, hashlib, json, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

# The 6 orphans with CORRECT matching hashes (content is what was originally downloaded)
target_hashes = {
    "07177f3466a6bdd4",  # Young man, grey background, professional headshot
    "1fdfe34efa2a58a0",  # Stocky man, wood-panel bb.is frame, green tie
    "6c85cd28322afd51",  # Man with red beard, orange background, wood-panel bb.is frame
    "90c3eb32ae1bcc1d",  # Young man in blue suit, wood-panel bb.is frame
    "986e09ab185abe10",  # Older man, wood-panel bb.is frame
    "a7232dbfe98f9898",  # Woman with glasses, outdoor
}

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

def extract_imgs(html, base):
    from urllib.parse import urlparse, urljoin
    found = set()
    urls = re.findall(r'https?://[^\s\'"<>]+\.(?:jpg|jpeg|png|webp)(?:\?[^\s\'"<>]*)?', html, re.IGNORECASE)
    for u in urls:
        if '1x1' not in u and 'favicon' not in u.lower() and 'icon' not in u.lower():
            found.add(u)
    return list(found)

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
checked = set()

# bb.is vikuvidtal 2026 articles - build comprehensive list
# These are articles with candidate interview photos
bb_search_urls = [
    "https://bb.is/?s=vikuvidtal",
    "https://bb.is/?s=2026+vikuvidtal",
    "https://bb.is/?s=2026+frambjodandi",
    "https://bb.is/?s=2026+oddviti",
    "https://bb.is/?s=2026+lista",
]

article_urls = set()

# Known articles from previous agent results
known_articles = [
    "https://bb.is/2026/04/vikuvidtalid-hlynur-arsaelsson/",
    "https://bb.is/2026/03/vikuvidtalid-jonas-thor-birgisson/",
    "https://bb.is/2026/04/vikuvidtalid-kristjan-jon-gudmundsson/",
    "https://bb.is/2026/04/vikuvidtalid-gudfinnur-ragnar-johannsson/",
    "https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/",
    "https://bb.is/2026/03/strandabyggd-framsokn-og-ohadir-bjoda-fram/",
    "https://bb.is/2026/04/isafjardarbaer-saevar-oli-efstur-a-lista-midflokksins/",
    # Add more potential vikuvidtal articles from 2026
    "https://bb.is/2026/04/vikuvidtalid-gudfinnur-ragnar-johannsson/",
    "https://bb.is/2026/04/vikuvidtalid-sigurbjorn-rafn-ulfarsson/",
    "https://bb.is/2026/04/vikuvidtalid-thorgeir-palsson/",
    "https://bb.is/2026/04/vikuvidtalid-aldey-unnar-traustadottir/",
    "https://bb.is/2026/04/vikuvidtalid-omar-gunnarsson/",
    "https://bb.is/2026/03/vikuvidtalid-helena-eydis-ingolfsdottir/",
    "https://bb.is/2026/04/vikuvidtalid-eysteinn-heidar-kristjansson/",
    "https://bb.is/2026/03/vikuvidtalid-aldey-unnar-traustadottir/",
    "https://bb.is/2025/11/verdur-kosid-i-sjavarbyggd-arid-2026/",
    "https://bb.is/2026/01/vestfirsk-politik-arid-2026/",
]
for a in known_articles:
    article_urls.add(a)

# Search bb.is for more articles
for search_url in bb_search_urls:
    html, final_url = fetch_html(search_url)
    if not html:
        continue
    links = re.findall(r'href=["\'](https://bb\.is/20\d\d/[^"\']+)["\']', html)
    for l in links:
        if l.endswith('/'):
            article_urls.add(l)

print(f"Total article URLs to check: {len(article_urls)}")

# Also try systematic vikuvidtal URL patterns
for name_slug in [
    "omar-gunnarsson", "sigurbjorn-rafn-ulfarsson", "thorgeir-palsson",
    "aldey-unnar-traustadottir", "helena-eydis-ingolfsdottir",
    "saevar-oli-hjorvarsson", "eysteinn-heidar-kristjansson",
    "jonas-thor-birgisson", "hlynur-arsaelsson",
    "kristjan-jon-gudmundsson", "gudfinnur-ragnar-johannsson",
    "viktor-ingi-jonsson", "gudmundur-haukur-jakobsson",
    "orn-arnarson", "benedikt-snaer-magnusson",
    "arni-jonsson", "sigurdur-gudmundsson",
    "davith-sigurdsson", "magnur-bardal",
    "monika-margret-stefansdottir", "anton-kari-halldorsson",
]:
    for year_month in ["2026/04", "2026/03", "2026/02"]:
        article_urls.add(f"https://bb.is/{year_month}/vikuvidtalid-{name_slug}/")

print(f"Total article URLs after adding patterns: {len(article_urls)}")

for art_url in sorted(article_urls):
    html, final_url = fetch_html(art_url)
    if not html or len(html) < 5000:
        continue

    imgs = extract_imgs(html, final_url)
    bb_imgs = [u for u in imgs if 'bb.is/wp-content' in u]

    if bb_imgs:
        print(f"\n{art_url}: {len(bb_imgs)} images")
        for img_url in bb_imgs:
            if img_url in checked:
                continue
            checked.add(img_url)
            h, data = download_and_hash(img_url)
            if h and h in target_hashes and h not in results:
                ctx_text = find_ctx(html, img_url)
                print(f"  *** MATCH: {h} -> {img_url}")
                print(f"  Context: {ctx_text[:120]}")
                results[h] = {"url": img_url, "page": art_url, "context": ctx_text}
    time.sleep(0.2)

print(f"\n\n=== SUMMARY: {len(results)}/{len(target_hashes)} matched ===")
for h, info in results.items():
    print(f"  {h}: {info['url']}")
    print(f"  Context: {info['context'][:100]}")

with open("F:/Claude Projects/iceland-elections/orphan_matches_bb.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
