"""Check bb.is sitemap pages for 2026 election articles"""
import urllib.request, ssl, re, hashlib, time, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"}

target = {"07177f3466a6bdd4","1fdfe34efa2a58a0","6c85cd28322afd51","90c3eb32ae1bcc1d","986e09ab185abe10","a7232dbfe98f9898"}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        return r.read().decode("utf-8", errors="replace")

# Get all sitemap pages
article_urls = set()
for i in range(1, 21):
    url = f"https://bb.is/wp-sitemap-posts-post-{i}.xml"
    try:
        xml = fetch(url)
        links = re.findall(r"<loc>(https://bb\.is/[^<]+)</loc>", xml)
        print(f"Sitemap {i}: {len(links)} articles")
        for l in links:
            article_urls.add(l)
    except Exception as e:
        print(f"Sitemap {i}: {e}")
        break

# Filter 2026 articles
articles_2026 = [u for u in article_urls if "/2026/" in u]
print(f"\nTotal 2026 articles: {len(articles_2026)}")
for u in sorted(articles_2026):
    print(f"  {u}")

results = {}
checked_imgs = set()

for url in sorted(articles_2026):
    try:
        html = fetch(url)
        if len(html) < 5000:
            continue

        img_pat = r"https://bb\.is/wp-content/[^\s'\"<>]+\.(?:jpg|jpeg|png|webp)"
        imgs = set(re.findall(img_pat, html, re.IGNORECASE))

        for img_url in imgs:
            if img_url in checked_imgs:
                continue
            checked_imgs.add(img_url)

            try:
                ireq = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(ireq, timeout=10, context=ctx) as ir:
                    data = ir.read()
                if len(data) < 2000:
                    continue
                h = hashlib.md5(data).hexdigest()[:16]
                if h in target and h not in results:
                    fname = img_url.split("/")[-1]
                    idx = html.find(fname)
                    ctx_text = ""
                    if idx != -1:
                        snippet = html[max(0,idx-400):min(len(html),idx+400)]
                        ctx_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", snippet)).strip()[:300]
                    print(f"\n*** MATCH: {h}")
                    print(f"  URL: {img_url}")
                    print(f"  Article: {url}")
                    print(f"  Context: {ctx_text[:150]}")
                    results[h] = {"url": img_url, "page": url, "context": ctx_text}
            except:
                pass

        if imgs:
            print(f"{url}: {len(imgs)} images")
        time.sleep(0.2)
    except Exception as e:
        pass

print(f"\n=== {len(results)}/{len(target)} matched ===")
for h, info in results.items():
    print(f"  {h}: {info['url']}")

with open("F:/Claude Projects/iceland-elections/orphan_matches_bb_sitemap.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
