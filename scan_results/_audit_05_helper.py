"""Helper for batch 05 audit. Reads cached HTML and prints text content."""
import json, re, sys
from pathlib import Path
from html.parser import HTMLParser

CACHE = Path(r"F:\Claude Projects\iceland-elections\scan_results\source_cache")
MANIFEST = json.load(open(CACHE / "_manifest.json", encoding="utf-8"))

def cached_path(url):
    meta = MANIFEST.get(url)
    if meta and meta.get("status") == 200:
        return CACHE / meta["file"]
    return None

class Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag in ("p","div","li","br","h1","h2","h3","h4","tr","td"):
            self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1
    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)

def extract_text(path):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    # strip script/style first crudely too
    raw = re.sub(r"<script[\s\S]*?</script>", "", raw, flags=re.I)
    raw = re.sub(r"<style[\s\S]*?</style>", "", raw, flags=re.I)
    s = Stripper()
    try:
        s.feed(raw)
    except Exception:
        pass
    txt = "".join(s.parts)
    # collapse whitespace per line
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in txt.split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)

def show(url, search=None, ctx=2):
    path = cached_path(url)
    if not path:
        print(f"NO CACHE: {url}")
        return
    txt = extract_text(path)
    if search:
        lines = txt.split("\n")
        for i, ln in enumerate(lines):
            if re.search(search, ln, re.I):
                lo = max(0, i-ctx); hi = min(len(lines), i+ctx+1)
                print(f"--- match @{i} ---")
                for j in range(lo, hi):
                    print(f"{j:4}: {lines[j]}")
                print()
    else:
        print(txt)

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    url = sys.argv[1]
    search = sys.argv[2] if len(sys.argv) > 2 else None
    ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    show(url, search, ctx)
