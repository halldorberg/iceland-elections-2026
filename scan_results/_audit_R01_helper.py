"""Helper for batch R01 audit. Run with: python _audit_R01_helper.py <command> [args]
Commands:
  cache <url>           - print path of cached file (or NONE)
  text <url>            - print stripped visible text of cached file
  grep <url> <regex>    - print lines/blocks matching regex (case-insensitive)
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

CACHE_DIR = r"F:\Claude Projects\iceland-elections\scan_results\source_cache"
MANIFEST = json.load(open(os.path.join(CACHE_DIR, "_manifest.json"), encoding="utf-8"))


def cached_path(url):
    meta = MANIFEST.get(url)
    if meta and meta.get("status") == 200:
        return os.path.join(CACHE_DIR, meta["file"])
    return None


class TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg"}

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
        elif tag in ("br", "p", "div", "li", "h1", "h2", "h3", "h4", "h5", "tr", "td", "th"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth > 0:
            self.skip_depth -= 1
        elif tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "h5", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)


def get_text(url):
    p = cached_path(url)
    if not p:
        return None
    with open(p, encoding="utf-8", errors="replace") as f:
        html = f.read()
    ex = TextExtractor()
    ex.feed(html)
    text = "".join(ex.parts)
    # collapse whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()


def grep(url, pattern):
    text = get_text(url)
    if text is None:
        return f"NO CACHE for {url}"
    rx = re.compile(pattern, re.IGNORECASE)
    out = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if rx.search(line):
            ctx_start = max(0, i - 1)
            ctx_end = min(len(lines), i + 2)
            out.append("--- match at line %d ---" % i)
            for j in range(ctx_start, ctx_end):
                out.append(lines[j])
    return "\n".join(out) if out else "(no matches)"


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "cache":
        print(cached_path(sys.argv[2]) or "NONE")
    elif cmd == "text":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(get_text(sys.argv[2]))
    elif cmd == "grep":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(grep(sys.argv[2], sys.argv[3]))
    else:
        print("unknown cmd", cmd)
