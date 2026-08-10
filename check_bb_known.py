import urllib.request, re, hashlib, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://bb.is/"
}

target = {"07177f3466a6bdd4","1fdfe34efa2a58a0","6c85cd28322afd51","90c3eb32ae1bcc1d","986e09ab185abe10","a7232dbfe98f9898"}

articles = [
    "https://bb.is/2026/04/vikuvidtalid-hlynur-arsaelsson/",
    "https://bb.is/2026/03/vikuvidtalid-jonas-thor-birgisson/",
    "https://bb.is/2026/04/vikuvidtalid-kristjan-jon-gudmundsson/",
    "https://bb.is/2026/04/vikuvidtalid-gudfinnur-ragnar-johannsson/",
    "https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/",
    "https://bb.is/2026/03/strandabyggd-framsokn-og-ohadir-bjoda-fram/",
    "https://bb.is/2026/04/isafjardarbaer-saevar-oli-efstur-a-lista-midflokksins/",
    "https://bb.is/2026/04/fjolmenni-vid-opnun-kosningarmidstodvar-o-listans-i-bolungarvik/",
    "https://bb.is/2026/04/vesturbyggd-enginn-d-listi-i-vor/",
    "https://bb.is/2026/04/reykholahreppur-tveir-listar-i-frambodi/",
    "https://bb.is/2026/04/sjalfstaedisflokkurinn-i-isafjardarbae-opnadi-kosningaskrifstofu-i-gamla-bakariinu-vid-silfurtorg/",
    "https://bb.is/2026/04/midflokkurinn-isafjardarbae-aherslur/",
    "https://bb.is/2026/04/islenska-sem-annad-mal-i-isafjardarbae-spurningar-til-allra-frambjodanda-til-sveitastjornarkosninga-vorid-2026/",
    "https://bb.is/2026/04/sveitarstjornarkosningar-fjor-ad-faerast-i-frambodin/",
    "https://bb.is/2026/04/fyrir-folkid/",
    "https://bb.is/2025/11/verdur-kosid-i-sjavarbyggd-arid-2026/",
    "https://bb.is/2026/01/vestfirsk-politik-arid-2026/",
]

results = {}
checked_imgs = set()

for url in articles:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
            html = r.read().decode("utf-8", errors="replace")

        # Find bb.is images
        img_pat = r"https://bb\.is/wp-content/[^\s'\"<>]+\.(?:jpg|jpeg|png|webp)"
        imgs = set(re.findall(img_pat, html, re.IGNORECASE))
        checked = 0
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
                    # Find context
                    fname = img_url.split("/")[-1]
                    idx = html.find(fname)
                    ctx_text = ""
                    if idx != -1:
                        snippet = html[max(0,idx-400):min(len(html),idx+400)]
                        ctx_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", snippet)).strip()[:250]
                    print(f"MATCH: {h}")
                    print(f"  URL: {img_url}")
                    print(f"  Article: {url}")
                    print(f"  Context: {ctx_text[:120]}")
                    results[h] = {"url": img_url, "page": url, "context": ctx_text}
                checked += 1
            except:
                pass
        print(f"{url}: {checked} images checked")
        time.sleep(0.3)
    except Exception as e:
        print(f"ERROR {url}: {e}")

print(f"\n=== {len(results)}/{len(target)} matched ===")
for h, info in results.items():
    print(f"  {h}: {info['url']}")

import json
with open("F:/Claude Projects/iceland-elections/orphan_matches_bb2.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
