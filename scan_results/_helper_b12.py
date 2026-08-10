import json, re, html, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
CACHE = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
m = json.load(open(os.path.join(CACHE, "_manifest.json"), encoding="utf-8"))

def get_text(url):
    meta = m.get(url)
    if not meta or meta.get("status") != 200:
        return None
    p = os.path.join(CACHE, meta["file"])
    with open(p, encoding="utf-8", errors="ignore") as f:
        h = f.read()
    h = re.sub(r"<script[^>]*>.*?</script>", " ", h, flags=re.S|re.I)
    h = re.sub(r"<style[^>]*>.*?</style>", " ", h, flags=re.S|re.I)
    t = re.sub(r"<[^>]+>", " ", h)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    return t

def find(url, key, around=400, before=200):
    t = get_text(url)
    if t is None:
        print("NO CACHE", url)
        return
    i = t.lower().find(key.lower())
    if i < 0:
        print(f"NOT FOUND '{key}' in {url}")
        return
    seen = 0
    while i >= 0 and seen < 6:
        print(f"--- @ {i} ---")
        print(t[max(0,i-before):i+around])
        i = t.lower().find(key.lower(), i+1)
        seen += 1

if __name__ == "__main__":
    url = sys.argv[1]
    key = sys.argv[2] if len(sys.argv) > 2 else ""
    around = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    before = int(sys.argv[4]) if len(sys.argv) > 4 else 200
    if key:
        find(url, key, around, before)
    else:
        t = get_text(url)
        print(t[:8000] if t else "NO CACHE")
