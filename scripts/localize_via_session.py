#!/usr/bin/env python3
"""
Try to fetch the remaining external photos using requests.Session — first
warm up each host (so Vercel's anti-bot challenge sets a cookie) then
fetch the image URLs.
"""
import hashlib
import re
import sys
import time
from pathlib import Path
import requests

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")


def detect_ext(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff": return "jpg"
    if data[:4] == b"\x89PNG": return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return "webp"
    if data[:6] in (b"GIF87a", b"GIF89a"): return "gif"
    return "jpg"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    pat = re.compile(
        r"(\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*)"
        r"'(https?://[^']+)'"
    )
    url_to_names = {}
    for m in pat.finditer(src):
        name = m.group(2).replace("\\'", "'")
        url = m.group(3)
        url_to_names.setdefault(url, []).append(name)
    print(f"Remaining: {len(url_to_names)}")

    sess = requests.Session()
    sess.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "is,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
    })

    # Per-host warmup
    hosts_seen = set()
    for url in url_to_names:
        host = url.split('/')[0] + '//' + url.split('/')[2]
        # framsoknrvk.is redirects to www. — visit www directly
        if 'framsoknrvk.is' in host and 'www.' not in host:
            host = host.replace('framsoknrvk.is', 'www.framsoknrvk.is')
        if host in hosts_seen: continue
        hosts_seen.add(host)
        print(f"Warming {host} ...")
        try:
            r = sess.get(host + '/', timeout=30)
            print(f"  -> {r.status_code} ({len(r.content)} bytes)")
        except Exception as e:
            print(f"  -> error: {e}")
        time.sleep(1)

    # Now fetch each image with image-fetch headers
    img_headers = {
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Sec-Fetch-Dest": "image",
        "Sec-Fetch-Mode": "no-cors",
    }

    url_to_local = {}
    failed = []
    for i, (url, names) in enumerate(url_to_names.items(), 1):
        # framsoknrvk.is needs www.
        fetch_url = url
        if '://framsoknrvk.is' in url:
            fetch_url = url.replace('://framsoknrvk.is', '://www.framsoknrvk.is', 1)
        try:
            host_root = fetch_url.split('/')[0] + '//' + fetch_url.split('/')[2] + '/'
            r = sess.get(fetch_url, headers={**img_headers, 'Referer': host_root}, timeout=30)
        except Exception as e:
            print(f"[{i}] {names[0][:30]:<32} ✗ {e}")
            failed.append((url, names))
            continue
        if r.status_code != 200 or not r.content.startswith((b'\xff\xd8\xff', b'\x89PNG', b'RIFF', b'GIF8')):
            print(f"[{i}] {names[0][:30]:<32} ✗ {r.status_code} ({r.headers.get('content-type','?')})")
            failed.append((url, names))
            continue
        h = hashlib.sha256(r.content).hexdigest()[:16]
        ext = detect_ext(r.content)
        out = IMG_DIR / f"{h}.{ext}"
        if not out.exists():
            out.write_bytes(r.content)
        url_to_local[url] = f"images/candidates/{h}.{ext}"
        print(f"[{i}] {names[0][:30]:<32} ✓ {out.name} ({len(r.content)} bytes)")

    new_src = src
    for old_url, local_path in url_to_local.items():
        new_src = new_src.replace(f"'{old_url}'", f"'{local_path}'")
    if new_src != src:
        CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\nLocalised {len(url_to_local)}, failed {len(failed)}")


if __name__ == "__main__":
    main()
