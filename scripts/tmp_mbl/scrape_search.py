# -*- coding: utf-8 -*-
"""Scrape mbl.is search results for adsendar greinar about EU referendum."""
import subprocess, re, json, sys, urllib.parse, html as htmlmod

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

def fetch(url):
    p = subprocess.run(["curl", "-s", "-A", UA, "-L", url], capture_output=True, timeout=60)
    return p.stdout.decode("iso-8859-1", errors="replace")

QUERIES = [
    '"aðsend grein" ESB',
    '"aðsend grein" aðildarviðræður',
    '"aðsend grein" Evrópusambandið',
    '"ESB þjóðaratkvæðagreiðsla"',
    '"aðsend grein" evra',
    '"aðsend grein" þjóðaratkvæðagreiðsla',
]

ITEM_RE = re.compile(r'<div class="newslist-item[^"]*" id="newslist-item-(\d+)">(.*?)</div>\s*\n', re.S)

def clean(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = htmlmod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

results = {}
for q in QUERIES:
    qs = urllib.parse.quote(q)
    for offset in range(0, 400, 20):
        url = f"https://www.mbl.is/frettir/search/?qs={qs}&offset={offset}&limit=20&sort=1"
        page = fetch(url)
        items = re.findall(r'<div class="newslist-item autohyphenated" id="newslist-item-\d+">.*?</p>\s*\n\s*</div>', page, re.S)
        if not items:
            sys.stderr.write(f"q={q!r} offset={offset}: 0 items, stop\n")
            break
        n_new = 0
        oldest = None
        for it in items:
            m_url = re.search(r'<h4[^>]*><a href="(/frettir/[^"]+)">(.*?)</a></h4>', it, re.S)
            if not m_url: continue
            path = m_url.group(1)
            title = clean(m_url.group(2))
            m_date = re.search(r'<span class="sep">\|</span>\s*(\d+\.\d+\.\d+)', it)
            date = m_date.group(1) if m_date else None
            m_sn = re.search(r'<p class="smallish">(.*?)<span class="meira_hnapp">', it, re.S)
            snippet = clean(m_sn.group(1)) if m_sn else ""
            m_img = re.search(r'<img data-mbl-postload="[^"]+" alt="([^"]*)"', it)
            imgalt = htmlmod.unescape(m_img.group(1)) if m_img else None
            oldest = date
            if path not in results:
                results[path] = {"url": "https://www.mbl.is" + path, "title": title,
                                 "date": date, "snippet": snippet, "imgalt": imgalt}
                n_new += 1
        sys.stderr.write(f"q={q!r} offset={offset}: {len(items)} items, {n_new} new, oldest={oldest}\n")
        # stop paginating this query when oldest result is before May 2026
        if oldest:
            d, mo, y = oldest.split(".")
            if int(y) < 2026 or (int(y) == 2026 and int(mo) < 5):
                break

with open("search_results.json", "w", encoding="utf-8") as f:
    json.dump(list(results.values()), f, ensure_ascii=False, indent=1)
print(len(results), "unique urls")
