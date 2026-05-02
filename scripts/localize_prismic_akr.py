#!/usr/bin/env python3
"""Localize the 11 prismic.io URLs in AKR.S (Akranes Samfylkingin)
using fresh URLs scraped live from xs.is/frambjoendur-a-akranesi.

Imgix path-matches the full filename (the bare imgix-id alone returns
403). Magic header combo (Edge UA + Sec-Fetch-* + --compressed) bypasses
imgix's hotlink guard."""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")

# Live URLs scraped from xs.is/frambjoendur-a-akranesi (per-ballot, AKR.S).
# These are the ONLY URL strings imgix will serve — the ones in candidates.js
# have a stale " " (vs no-space) and 403.
LIVE_URLS_BY_BALLOT = {
    5:  "https://images.prismic.io/samfylkingin/ad_Dx51ZCF7ETOWN_J%C3%B3nHj%C3%B6rvar-2-.png",
    7:  "https://images.prismic.io/samfylkingin/ad_D1J1ZCF7ETOWQ_7.Bj%C3%B6rnGu%C3%B0mundsson.png",
    9:  "https://images.prismic.io/samfylkingin/ad5N4Z1ZCF7ETLpx_9.Gunn%C3%BE%C3%B3runnValsd%C3%B3ttir.png",
    10: "https://images.prismic.io/samfylkingin/ad5N-J1ZCF7ETLpy_10.%C3%96rnArnarson.png",
    11: "https://images.prismic.io/samfylkingin/ad_D3J1ZCF7ETOWR_11.Margr%C3%A9tBjarnad%C3%B3ttir.png",
    12: "https://images.prismic.io/samfylkingin/ad_D4Z1ZCF7ETOWW_12.%C3%81sbj%C3%B6rn%C3%9E%C3%B3r%C3%81sbj%C3%B6rnsson.png",
    13: "https://images.prismic.io/samfylkingin/ad_D551ZCF7ETOWX_13.AglaHar%C3%B0ard%C3%B3ttir.png",
    14: "https://images.prismic.io/samfylkingin/ad5OMp1ZCF7ETLqb_14.ElvarSigurj%C3%B3nsson.png",
    15: "https://images.prismic.io/samfylkingin/ad_D7p1ZCF7ETOWa_15.GunnhildurBj%C3%B6rnsd%C3%B3ttir.png",
    16: "https://images.prismic.io/samfylkingin/ad5Oc51ZCF7ETLqf_16.BjarniV%C3%A9steinsson.png",
    17: "https://images.prismic.io/samfylkingin/ad5Ojp1ZCF7ETLqn_17.%C3%81staEgilsd%C3%B3ttir.png",
}


def fetch(url):
    full = url + ("&" if "?" in url else "?") + "auto=format,compress"
    try:
        r = subprocess.run(
            ["curl", "-sf", "-A", UA,
             "-H", "Referer: https://xs.is/",
             "-H", "Accept: image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
             "-H", "Sec-Fetch-Dest: image",
             "-H", "Sec-Fetch-Mode: no-cors",
             "-H", "Sec-Fetch-Site: cross-site",
             "--compressed", full],
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

    # Locate AKR.S list block
    akr = re.search(r"\bconst AKR\s*=\s*\{", src)
    p, d = akr.end() - 1, 0
    while p < len(src):
        if src[p] == '{': d += 1
        elif src[p] == '}':
            d -= 1
            if d == 0: break
        p += 1
    akr_block = src[akr.end() - 1:p + 1]
    sm = re.search(r"\n  S\s*:\s*\{", akr_block)
    p, d = sm.end() - 1, 0
    while p < len(akr_block):
        if akr_block[p] == '{': d += 1
        elif akr_block[p] == '}':
            d -= 1
            if d == 0: break
        p += 1
    s_block = akr_block[sm.end() - 1:p + 1]

    row_re = re.compile(
        r"\[\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*"
        r"'(https://images\.prismic\.io[^']+)'"
    )
    rows = row_re.findall(s_block)
    print(f"Found {len(rows)} AKR.S candidates with prismic URLs")

    new_src = src
    swapped, missed = 0, 0
    for ballot_str, name, old_url in rows:
        ballot = int(ballot_str)
        live_url = LIVE_URLS_BY_BALLOT.get(ballot)
        if not live_url:
            print(f"  ? no live URL mapped for ballot {ballot} ({name})")
            missed += 1
            continue
        data = fetch(live_url)
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
        print(f"  ✓ #{ballot:>2} {name[:32]:<34} → {out.name}")

    if new_src != src:
        CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\nSwapped: {swapped}, missed: {missed}")


if __name__ == "__main__":
    main()
