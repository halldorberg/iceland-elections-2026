"""Helper for batch R03 audit - extract text from cached HTML."""
import json
import os
import sys
import re
from html.parser import HTMLParser

CACHE_DIR = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
MANIFEST = json.load(open(os.path.join(CACHE_DIR, "_manifest.json"), encoding="utf-8"))


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)
        if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "tr", "td"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip == 0:
            self.parts.append(data)


def cached_path(url):
    meta = MANIFEST.get(url)
    if meta and meta.get("status") == 200:
        return os.path.join(CACHE_DIR, meta["file"])
    return None


def status(url):
    meta = MANIFEST.get(url)
    return meta.get("status") if meta else None


def get_text(url):
    p = cached_path(url)
    if not p:
        return None
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    parser = TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass
    text = "".join(parser.parts)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text


def search(url, *needles, context=120):
    """Find substring matches in text and return surrounding context."""
    text = get_text(url)
    if text is None:
        return f"[NO TEXT for {url}]"
    out = []
    for n in needles:
        # case-insensitive search
        lower = text.lower()
        nl = n.lower()
        idx = 0
        hits = []
        while True:
            i = lower.find(nl, idx)
            if i < 0:
                break
            start = max(0, i - context)
            end = min(len(text), i + len(n) + context)
            hits.append(text[start:end].replace("\n", " ").strip())
            idx = i + len(n)
            if len(hits) >= 3:
                break
        if hits:
            out.append(f"-- '{n}' --\n" + "\n".join(hits))
        else:
            out.append(f"-- '{n}' -- NOT FOUND")
    return "\n\n".join(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "text":
        url = sys.argv[2]
        max_chars = int(sys.argv[3]) if len(sys.argv) > 3 else 8000
        t = get_text(url) or "[no text]"
        print(t[:max_chars])
    elif cmd == "search":
        url = sys.argv[2]
        needles = sys.argv[3:]
        print(search(url, *needles))
    elif cmd == "status":
        url = sys.argv[2]
        print(status(url))
