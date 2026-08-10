#!/usr/bin/env python3
"""Localize the 11 prismic.io URLs (Reykjavík S candidates ballot 7-17)
using fresh URLs scraped from the live xs.is/frambjodendur-i-reykjavik-2026
page. Match by ballot order — the live page lists candidates in order."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"

# Live URLs scraped from xs.is/frambjodendur-i-reykjavik-2026 in DOM order.
# First 10 are the top-10 candidate cards (ballots 1-10), then mid-list etc.
LIVE_URLS_BY_BALLOT = {
    1:  "https://images.prismic.io/samfylkingin/adUVO5GXnQHGZU3Z_PéturMarteinn.png",
    2:  "https://images.prismic.io/samfylkingin/adUVRpGXnQHGZU3b_HeiðaBjörg.png",
    3:  "https://images.prismic.io/samfylkingin/adUVUpGXnQHGZU3i_Steinunn.png",
    4:  "https://images.prismic.io/samfylkingin/adUVXJGXnQHGZU3t_Skúli.png",
    5:  "https://images.prismic.io/samfylkingin/adUVaZGXnQHGZU31_Stein.png",
    6:  "https://images.prismic.io/samfylkingin/adUVcpGXnQHGZU35_Birta.png",
    7:  "https://images.prismic.io/samfylkingin/adUVf5GXnQHGZU3__Regína.png",
    8:  "https://images.prismic.io/samfylkingin/adUVkJGXnQHGZU4H_Birkir.png",
    9:  "https://images.prismic.io/samfylkingin/adUVq5GXnQHGZU4T_Isabell.png",
    10: "https://images.prismic.io/samfylkingin/adUVt5GXnQHGZU4d_Sara.png",
}


def fetch_curl(url):
    from urllib.parse import urlsplit, urlunsplit, quote
    parts = urlsplit(url)
    encoded_path = quote(parts.path, safe="/-_.~")
    encoded = urlunsplit((parts.scheme, parts.netloc, encoded_path, parts.query, parts.fragment))
    full = encoded + "?auto=format,compress" if "?" not in encoded else encoded
    try:
        r = subprocess.run(
            ["curl", "-sf", "-A", UA, "-H", "Referer: https://xs.is/frambjodendur-i-reykjavik-2026",
             full],
            capture_output=True, timeout=30,
        )
        if r.returncode == 0 and len(r.stdout) > 1000:
            return r.stdout
        print(f"   curl rc={r.returncode} bytes={len(r.stdout)}")
    except Exception as e:
        print(f"   curl error: {e}")
    return None


def detect_ext(d):
    if d[:3] == b"\xff\xd8\xff": return "jpg"
    if d[:4] == b"\x89PNG": return "png"
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP": return "webp"
    return "png"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # Find Reykjavík S list block
    m = re.search(r"\bconst RVK\s*=\s*\{", src)
    p, d = m.end() - 1, 0
    while p < len(src):
        if src[p] == '{': d += 1
        elif src[p] == '}':
            d -= 1
            if d == 0: break
        p += 1
    rvk = src[m.end() - 1:p + 1]
    sm = re.search(r"\n  S\s*:\s*\{", rvk)
    p, d = sm.end() - 1, 0
    while p < len(rvk):
        if rvk[p] == '{': d += 1
        elif rvk[p] == '}':
            d -= 1
            if d == 0: break
        p += 1
    s_block = rvk[sm.end() - 1:p + 1]

    # Per-row: ballot, name, prismic URL
    row_re = re.compile(
        r"\[\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*"
        r"'(https://images\.prismic\.io[^']+)'"
    )
    rows = row_re.findall(s_block)
    print(f"Found {len(rows)} RVK S candidates with stale prismic URLs")

    new_src = src
    swapped, missed = 0, 0
    for ballot_str, name, old_url in rows:
        ballot = int(ballot_str)
        live_url = LIVE_URLS_BY_BALLOT.get(ballot)
        if not live_url:
            print(f"  ? no live URL mapped for ballot {ballot} ({name})")
            missed += 1
            continue
        data = fetch_curl(live_url)
        if not data:
            print(f"  ✗ ballot {ballot} {name[:30]}")
            missed += 1
            continue
        h = hashlib.sha256(data).hexdigest()[:16]
        ext = detect_ext(data)
        out = IMG_DIR / f"{h}.{ext}"
        if not out.exists():
            out.write_bytes(data)
        local_path = f"images/candidates/{h}.{ext}"
        new_src = new_src.replace(f"'{old_url}'", f"'{local_path}'", 1)
        swapped += 1
        print(f"  ✓ #{ballot:>2} {name[:32]:<34} ← {live_url.split('/')[-1][:40]}")

    if new_src != src:
        CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\nSwapped: {swapped}, missed: {missed}")


if __name__ == "__main__":
    main()
