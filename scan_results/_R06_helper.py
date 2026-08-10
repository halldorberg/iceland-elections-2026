"""R06 audit helper - extract candidate-relevant text snippets."""
import json, re, sys, os
from html import unescape

CACHE_DIR = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
MANIFEST = json.load(open(os.path.join(CACHE_DIR, "_manifest.json"), encoding="utf-8"))

def html_to_text(html):
    # Strip scripts/styles/svg
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S|re.I)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S|re.I)
    html = re.sub(r"<svg[^>]*>.*?</svg>", " ", html, flags=re.S|re.I)
    html = re.sub(r"<noscript[^>]*>.*?</noscript>", " ", html, flags=re.S|re.I)
    # Replace breaks with newlines
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    html = re.sub(r"</(p|div|li|h[1-6]|tr|td|th)>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()

def cached_text(url):
    meta = MANIFEST.get(url)
    if not meta:
        return None, None
    p = os.path.join(CACHE_DIR, meta["file"])
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            html = f.read()
    except Exception as e:
        return None, str(e)
    return html_to_text(html), meta.get("status")

def find_snippets(text, terms, window=200):
    if not text:
        return []
    out = []
    low = text.lower()
    seen = set()
    for term in terms:
        t = term.lower()
        start = 0
        while True:
            idx = low.find(t, start)
            if idx < 0:
                break
            a = max(0, idx - window)
            b = min(len(text), idx + len(term) + window)
            sn = text[a:b].replace("\n", " ")
            sn = re.sub(r"\s+", " ", sn).strip()
            if sn not in seen:
                seen.add(sn)
                out.append(sn)
            start = idx + len(term)
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "snip":
        url = sys.argv[2]
        terms = sys.argv[3].split("||")
        text, status = cached_text(url)
        print(f"STATUS={status}")
        if text:
            for s in find_snippets(text, terms):
                print("---")
                print(s)
    elif cmd == "raw":
        url = sys.argv[2]
        text, status = cached_text(url)
        print(f"STATUS={status}")
        print(text[:50000] if text else "")
    elif cmd == "raw_after":
        url = sys.argv[2]
        marker = sys.argv[3]
        n = int(sys.argv[4]) if len(sys.argv) > 4 else 5000
        text, status = cached_text(url)
        if text:
            idx = text.lower().find(marker.lower())
            if idx >= 0:
                print(text[idx:idx+n])
            else:
                print("MARKER NOT FOUND")
