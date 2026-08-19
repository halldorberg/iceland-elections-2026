# -*- coding: utf-8 -*-
"""Collect mbl.is search results for EU referendum adsendar greinar (May-Aug 2026)."""
import json, re, subprocess, sys, time, os
from urllib.parse import quote

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
CACHE = r"F:/Claude Projects/iceland-elections/scripts/mbl_cache"
os.makedirs(CACHE, exist_ok=True)

QUERIES = [
    '"aðsend grein" ESB',
    '"aðsend grein" aðildarviðræður',
    'ESB þjóðaratkvæðagreiðsla',
]

def fetch(url):
    r = subprocess.run(["curl", "-s", "-A", UA, "-L", url], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")

ITEM_RE = re.compile(
    r'newslist-item[^"]*" id="newslist-item-\d+">.*?'
    r'<span class="sep">\|</span>\s*([\d\.]+)\s*'      # date d.m.yyyy
    r'<span class="sep">\|</span>.*?'
    r'<h4[^>]*><a href="(/frettir/[^"]+)">(.*?)</a></h4>',
    re.S)

def parse_page(html):
    out = []
    for m in ITEM_RE.finditer(html):
        d, url, title = m.groups()
        title = re.sub(r"<[^>]+>", "", title).strip()
        parts = d.strip().split(".")
        try:
            iso = "%04d-%02d-%02d" % (int(parts[2]), int(parts[1]), int(parts[0]))
        except Exception:
            continue
        out.append({"date": iso, "url": "https://www.mbl.is" + url, "title": title})
    return out

results = {}
for q in QUERIES:
    qenc = quote(q, safe="")
    for offset in range(0, 400, 20):
        url = f"https://www.mbl.is/frettir/search/?qs={qenc}&offset={offset}&limit=20&sort=1"
        html = fetch(url)
        items = parse_page(html)
        sys.stderr.write(f"q={q!r} offset={offset}: {len(items)} items\n")
        if not items:
            break
        for it in items:
            results.setdefault(it["url"], it)
        # stop when whole page is older than May 2026
        if all(it["date"] < "2026-05-01" for it in items):
            break
        time.sleep(0.5)

items = sorted(results.values(), key=lambda x: x["date"], reverse=True)
in_range = [it for it in items if "2026-05-01" <= it["date"] <= "2026-08-31"]
with open(os.path.join(CACHE, "search_hits.json"), "w", encoding="utf-8") as f:
    json.dump(in_range, f, ensure_ascii=False, indent=1)
print(f"total unique: {len(items)}, in range May-Aug 2026: {len(in_range)}")
