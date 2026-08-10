"""Helper for batch 15 audit."""
import json
import re
import sys
import os
from html.parser import HTMLParser

MANIFEST = json.load(open(r"F:\Claude Projects\iceland-elections\scan_results\source_cache\_manifest.json", encoding="utf-8"))

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','nav','footer','header','noscript'):
            self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script','style','nav','footer','header','noscript'):
            self.skip = max(0,self.skip-1)
    def handle_data(self, d):
        if self.skip == 0:
            self.parts.append(d)

def cached_path(url):
    meta = MANIFEST.get(url)
    if meta and meta.get("status") == 200:
        return r"F:\Claude Projects\iceland-elections\scan_results\source_cache\\" + meta["file"]
    return None

def cache_status(url):
    meta = MANIFEST.get(url)
    if not meta:
        return None
    return meta.get("status")

def text_for(url):
    p = cached_path(url)
    if not p:
        return None
    with open(p,'r',encoding='utf-8',errors='ignore') as f:
        html = f.read()
    parser = TextExtractor()
    parser.feed(html)
    text = ' '.join(''.join(parser.parts).split())
    return text

def write_text(url, out_path):
    t = text_for(url)
    if t is None:
        with open(out_path,'w',encoding='utf-8') as f:
            f.write(f"NO CACHE for {url} (status={cache_status(url)})")
        return False
    with open(out_path,'w',encoding='utf-8') as f:
        f.write(t)
    return True

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dump":
        url = sys.argv[2]
        out = sys.argv[3]
        ok = write_text(url, out)
        print("OK" if ok else "FAIL")
    elif cmd == "search":
        # search a phrase across cached file
        url = sys.argv[2]
        phrase = sys.argv[3]
        t = text_for(url) or ""
        idx = t.lower().find(phrase.lower())
        if idx == -1:
            print("NOT FOUND")
        else:
            start = max(0, idx-100)
            end = min(len(t), idx+200)
            with open(sys.argv[4],'w',encoding='utf-8') as f:
                f.write(t[start:end])
            print("WROTE")
