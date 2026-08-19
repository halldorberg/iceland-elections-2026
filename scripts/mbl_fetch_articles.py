# -*- coding: utf-8 -*-
"""Fetch article pages from search_hits.json, extract metadata for classification. v2: latin-1 decode."""
import json, re, subprocess, sys, os, hashlib, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
CACHE = r"F:/Claude Projects/iceland-elections/scripts/mbl_cache"

hits = json.load(open(os.path.join(CACHE, "search_hits.json"), encoding="utf-8"))

def decode(raw):
    m = re.search(rb'charset=["\']?([\w-]+)', raw[:3000])
    enc = m.group(1).decode() if m else "iso-8859-1"
    try:
        return raw.decode(enc, errors="replace")
    except LookupError:
        return raw.decode("iso-8859-1", errors="replace")

def fetch_cached(url):
    h = hashlib.md5(url.encode()).hexdigest()[:16]
    p = os.path.join(CACHE, "b_" + h + ".bin")
    if os.path.exists(p) and os.path.getsize(p) > 5000:
        raw = open(p, "rb").read()
    else:
        r = subprocess.run(["curl", "-s", "-A", UA, "-L", url], capture_output=True)
        raw = r.stdout
        open(p, "wb").write(raw)
        time.sleep(0.4)
    return decode(raw)

def extract(html):
    d = {}
    m = re.search(r'<meta[^>]*property="og:description"[^>]*content="([^"]*)"', html)
    d["desc"] = m.group(1).strip() if m else None
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
    d["h1"] = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else None
    d["is_adsend"] = ("grein úr Morgunblaðinu" in html) or (d["h1"] or "").lower().startswith("aðsend grein") or ("Aðsent efni" in html)
    # author: main image link title attribute (portrait of author on adsendar greinar)
    author = None
    m = re.search(r'newsitem-image is-main-img.*?title="([^"]+)"', html, re.S)
    if m:
        t = m.group(1).strip()
        if re.match(r"^[A-ZÁÐÉÍÓÚÝÞÆÖ][a-záðéíóúýþæö]+(\s[A-ZÁÐÉÍÓÚÝÞÆÖ][\wáðéíóúýþæö\.]*){1,3}$", t):
            author = t
    d["author_img"] = author
    m = re.search(r"Höfundur(?:inn)? er ([^<.]{3,140})", html)
    d["hofundur_er"] = m.group(1).strip() if m else None
    # first meaningful body paragraphs
    paras = []
    for p in re.findall(r"<p[^>]*>(.*?)</p>", html, re.S):
        t = re.sub(r"<[^>]+>", " ", p)
        t = t.replace("&nbsp;", " ").replace("&quot;", '"').replace("&amp;", "&")
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) < 60:
            continue
        if "Innskráning" in t or "áskrifendur" in t or "skemmtunar" in t:
            continue
        paras.append(t)
        if len(paras) >= 8:
            break
    d["paras"] = paras
    return d

out = []
for i, it in enumerate(hits):
    html = fetch_cached(it["url"])
    d = extract(html)
    d.update(it)
    d["title"] = d["h1"] or d["title"]
    out.append(d)
    sys.stderr.write(f"{i+1}/{len(hits)} adsend={d['is_adsend']} author={d['author_img']}\n")

with open(os.path.join(CACHE, "articles_raw.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
adsend = [a for a in out if a["is_adsend"]]
print(f"fetched {len(out)}, adsend greinar: {len(adsend)}")
