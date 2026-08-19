"""Fetch dv.is/eyjan articles listed in /tmp/dv_links.txt, extract text, cache as JSON."""
import json, os, re, sys, time, html
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OUT = "C:/Users/USER/AppData/Local/Temp/dv_texts"
os.makedirs(OUT, exist_ok=True)

links = [l.strip().rstrip("/") for l in open("C:/Users/USER/AppData/Local/Temp/dv_links.txt", encoding="utf-8") if l.strip()]
existing = set(l.strip().rstrip("/") for l in open("F:/Claude Projects/iceland-elections/scripts/dv_existing_urls.txt", encoding="utf-8") if l.strip())
links = [l for l in links if l not in existing]

TAG = re.compile(r"<[^>]+>")

def extract(htm, url):
    m = re.search(r"<title>([^<]*)</title>", htm)
    title = html.unescape(m.group(1)).split(" | DV")[0].strip() if m else ""
    m = re.search(r'<meta name="description" content="([^"]*)"', htm)
    desc = html.unescape(m.group(1)) if m else ""
    m = re.search(r'class="article-body[^"]*"(.*?)</article>', htm, re.S)
    body_html = m.group(1) if m else ""
    if not body_html:
        m = re.search(r'field--name-body[^"]*field__item">(.*)', htm, re.S)
        body_html = m.group(1)[:60000] if m else ""
    body_html = re.sub(r"<script.*?</script>", " ", body_html, flags=re.S)
    body_html = re.sub(r"<style.*?</style>", " ", body_html, flags=re.S)
    body = html.unescape(TAG.sub(" ", body_html))
    body = re.sub(r"\s+", " ", body).strip()
    dm = re.search(r"/eyjan/(\d{4})/(\d{2})/(\d{2})/", url + "/")
    date = "-".join(dm.groups()) if dm else None
    return {"url": url, "title": title, "desc": desc, "date": date, "body": body[:20000]}

done = 0
for i, url in enumerate(links):
    slug = url.rsplit("/", 1)[-1][:120]
    path = os.path.join(OUT, slug + ".json")
    if os.path.exists(path):
        continue
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        htm = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        rec = extract(htm, url)
        json.dump(rec, open(path, "w", encoding="utf-8"), ensure_ascii=False)
        done += 1
    except Exception as e:
        print("ERR", url, e, flush=True)
    if (i + 1) % 50 == 0:
        print(i + 1, "processed", flush=True)
print("fetched", done, "total files", len(os.listdir(OUT)))
