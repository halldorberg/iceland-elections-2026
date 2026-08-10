"""
1. Verify that downloading known bb.is photos gives the expected hash
2. Find new bb.is uploads for 2026 election candidates
3. Search bb.is uploads directory patterns
"""
import urllib.request, re, hashlib, ssl, time, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
}

target_hashes = {
    "07177f3466a6bdd4",
    "1fdfe34efa2a58a0",
    "6c85cd28322afd51",
    "90c3eb32ae1bcc1d",
    "986e09ab185abe10",
    "a7232dbfe98f9898",
}

# Known bb.is photos from results file
known_bb_photos = [
    ("VES.STV.1", "https://bb.is/wp-content/uploads/2026/04/HlynurArsaelsson26.jpeg", "f3d1e0ae80fa4360"),
    ("ISA.D.1", "https://bb.is/wp-content/uploads/2026/02/Jonas_Thor.jpg", "c70f5e54006c8107"),
    ("BOL.BBK.1", "https://bb.is/wp-content/uploads/2026/04/KJG26.jpg", "9fff44cb8d031b7d"),
    ("BOL.MMM.1", "https://bb.is/wp-content/uploads/2026/04/mynd-gudfinnur.jpeg", "4ca9cb8a0ecb3089"),
    ("STR.SBD.1", "https://bb.is/wp-content/uploads/2021/06/THorgeir_visir.is_-1.jpg", "cda79e211931d636"),
    ("STR.B.1", "https://bb.is/wp-content/uploads/2026/03/Sigurbjorn-Rafn.jpg", "ddabb46d32358897"),
    ("ISA.M.1", "https://bb.is/wp-content/uploads/2026/04/saevarOli.jpg", "592f3a47e798c187"),
]

print("=== Verifying known bb.is photo hashes ===")
for cand_id, url, expected_hash in known_bb_photos:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
        actual_hash = hashlib.md5(data).hexdigest()[:16]
        match = "OK" if actual_hash == expected_hash else f"MISMATCH (got {actual_hash})"
        print(f"  {cand_id}: {match}")
        if actual_hash in target_hashes:
            print(f"    *** THIS IS AN ORPHAN MATCH: {actual_hash}")
    except Exception as e:
        print(f"  {cand_id}: ERROR - {e}")

# Now try to find NEW bb.is uploads for 2026 election candidates
# bb.is seems to be a Westfjords (Vestfirðir) publication
# Let me look for more candidate-related articles
print("\n=== Searching for more bb.is vikuvidtal/election articles ===")

# Try to access the bb.is RSS feed to get all articles
rss_urls = [
    "https://bb.is/feed/",
    "https://bb.is/feed/rss2/",
    "https://bb.is/category/vikuvidtal/feed/",
    "https://bb.is/category/frettir/feed/",
]

article_urls = set()
for rss_url in rss_urls:
    try:
        req = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            rss = r.read().decode("utf-8", errors="replace")
        # Extract article links from RSS
        links = re.findall(r'<link><!.*?>(https://bb\.is/[^<]+)</link>', rss)
        links += re.findall(r'<guid[^>]*>(https://bb\.is/[^<]+)</guid>', rss)
        for l in links:
            l = l.strip()
            if "/20" in l:
                article_urls.add(l)
        print(f"  {rss_url}: {len(links)} items")
    except Exception as e:
        print(f"  {rss_url}: {e}")

# Also try search for specific vikuvidtal slug patterns
vikuvidtal_names = [
    # Vestfirðir municipalities - Ísafjörður, Vesturbyggð, Bolungarvík, Strandabyggð, Reykhólahreppur
    # These are the main bb.is coverage area
    "aldey-unnar-traustadottir",
    "viktor-ingi-jonsson",
    "omar-gunnarsson",
    "helena-eydis-ingolfsdottir",
    "eysteinn-heidar-kristjansson",
    "rafn-bergsson",
    "tomas-birgir-magnusson",
    "sigurdur-gudmundsson",
    "ragnhildur-eva-jonsdottir",
    "kristjan-agust-magnusson",
    "davith-sigurdsson",
    "birgir-heidar-andresson",
    "svana-hronn-johannsdottir",
    "olafur-tryggvason",
    "fannar-kristjansson",
    "gudlaugur-skalason",
    "sindri-olafsson",
    "orn-arnarson",
]

for name in vikuvidtal_names:
    for prefix in ["vikuvidtalid-", ""]:
        for month in ["2026/04", "2026/03", "2026/02"]:
            url = f"https://bb.is/{month}/{prefix}{name}/"
            article_urls.add(url)

print(f"\nTotal article URLs to check: {len(article_urls)}")

results = {}
checked_imgs = set()

for url in sorted(article_urls):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            html = r.read().decode("utf-8", errors="replace")

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
                if h in target_hashes and h not in results:
                    fname = img_url.split("/")[-1]
                    idx = html.find(fname)
                    ctx_text = ""
                    if idx != -1:
                        snippet = html[max(0,idx-400):min(len(html),idx+400)]
                        ctx_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", snippet)).strip()[:300]
                    print(f"\n*** MATCH: {h} in {url}")
                    print(f"  IMG: {img_url}")
                    print(f"  Context: {ctx_text[:150]}")
                    results[h] = {"url": img_url, "page": url, "context": ctx_text}
            except:
                pass

        if imgs:
            print(f"{url}: {len(imgs)} images")
        time.sleep(0.2)
    except Exception as e:
        pass  # Skip 404s silently

print(f"\n=== {len(results)}/{len(target_hashes)} matched ===")
for h, info in results.items():
    print(f"  {h}: {info['url']}")

with open("F:/Claude Projects/iceland-elections/orphan_matches_bb3.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
