#!/usr/bin/env python3
"""Match framsoknrvk.is wp-content URLs to live /assets/candidates/<NN-name>.jpg
filenames by ballot number (the NN prefix). Download via curl-with-Referer.
"""
import hashlib
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
REFERER = "https://www.framsoknrvk.is/frambjodendur"

# Live filenames scraped via Edge from the /frambjodendur page.
LIVE_FILES = [
    "01-einar.jpg", "02-magnea.jpg", "03-valdi.jpg", "04-halldor.jpg",
    "05-andrea.jpg", "06-thordis-jona.jpg", "07-ina.jpg",
    "08-gudmundur-ingi.jpg", "09-asrun.jpg", "10-skuli-bragi.jpg",
    "11-kristjana.jpg", "12-dagbjort.jpg", "13-jon-finnbogason.jpg",
    "14-thordis-arna.jpg", "15-fanny.jpg", "16-haraldur.jpg",
    "17-ragnhildur.jpg", "18-hordur.jpg", "19-saethor.jpg",
    "20-asta-bjorg.jpg", "21-gisli.jpg", "22-drofn.jpg", "23-agust.jpg",
    "24-hafsteinn.jpg", "25-bjorg-osk.jpg", "26-bjorn-ivar.jpg",
    "27-gyda.jpg", "28-arnar-mar.jpg", "29-linda-bjork.jpg",
    "30-arnthor.jpg", "31-bragi.jpg", "32-steinthor.jpg", "33-olga.jpg",
    "34-breki.jpg", "35-inga.jpg", "36-olafur.jpg", "37-johann-karl.jpg",
    "38-ivar-orri.jpg", "39-milla.jpg", "40-larus.jpg", "41-hulda.jpg",
    "42-adalsteinn.jpg", "43-arelia.jpg", "44-niels.jpg", "45-hjalmar.jpg",
]
BY_NN = {f.split('-', 1)[0]: f for f in LIVE_FILES}


def detect_ext(data):
    if data[:3] == b"\xff\xd8\xff": return "jpg"
    if data[:4] == b"\x89PNG": return "png"
    return "jpg"


def fetch_with_curl(url):
    """curl is the only thing Vercel doesn't 403 here."""
    try:
        r = subprocess.run(
            ["curl", "-sf", "-A", UA, "-H", f"Referer: {REFERER}", url],
            capture_output=True, timeout=30,
        )
        if r.returncode == 0 and r.stdout.startswith((b"\xff\xd8\xff", b"\x89PNG")):
            return r.stdout
    except Exception as e:
        print(f"   curl error: {e}")
    return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # Extract framsoknrvk rows: (name, old_url) plus the NN prefix
    pat = re.compile(
        r"\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*"
        r"'(https?://[^']*framsoknrvk\.is/wp-content/uploads/2026/04/(\d+)[^']*)'"
    )
    rows = pat.findall(src)
    print(f"Found {len(rows)} framsoknrvk wp-content URLs")

    new_src = src
    swapped, missed = 0, 0
    for name, old_url, nn in rows:
        nn_padded = nn.zfill(2)
        live_file = BY_NN.get(nn_padded)
        if not live_file:
            print(f"  ? no live filename for NN={nn_padded} ({name})")
            missed += 1
            continue
        new_url = f"https://www.framsoknrvk.is/assets/candidates/{live_file}"
        data = fetch_with_curl(new_url)
        if not data:
            print(f"  ✗ {name[:32]:<34} fetch failed for {live_file}")
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
        print(f"  ✓ #{nn_padded} {name[:32]:<34} → {out.name}")

    if new_src != src:
        CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\nSwapped: {swapped}, missed: {missed}")


if __name__ == "__main__":
    main()
