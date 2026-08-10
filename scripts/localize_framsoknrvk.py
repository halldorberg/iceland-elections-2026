#!/usr/bin/env python3
"""
The 40 framsoknrvk.is photo URLs in candidates.js point at stale
/wp-content/uploads/2026/04/<NN>.jpg paths — the live site moved to
/assets/candidates/<NN-name>.jpg. Old paths now 403 (Vercel anti-bot).

This script:
  1. Uses Edge CDP to scrape the live /frambjodendur page for current
     (name → new URL) pairs.
  2. Downloads each new URL via curl-style fetch with Referer.
  3. Matches names to candidates.js rows and rewrites their photo path
     to the locally-saved /images/candidates/<hash>.jpg.
"""
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
REFERER = "https://www.framsoknrvk.is/frambjodendur"

# Scraped from Edge CDP — name → new URL on /assets/candidates/
NAME_TO_NEW_URL = {
    "Einar Þorsteinsson": "01-einar.jpg",
    "Magnea Gná Jóhannsdóttir": "02-magnea.jpg",
    "Þorvaldur Daníelsson": "03-valdi.jpg",
    "Halldór Bachmann": "04-halldor.jpg",
    "Andrea Edda Guðlaugsdóttir": "05-andrea.jpg",
    # Page positions 6-46 from /frambjodendur — names match candidates.js
    "Þórdís Jóna Jakobsdóttir": "06-thordis.jpg",
    "Ína Holoyad": "07-ina.jpg",
    "Guðmundur Ingi Þorvaldsson": "08-gudmundur.jpg",
    "Ásrún Kristjánsdóttir": "09-asrun.jpg",
    "Stefán Gauti Magnússon": "10-stefan.jpg",
    "Stefán Karl Magnússon": "10-stefan.jpg",  # in case name format differs
    "Ragnhildur Helga Ragnarsdóttir": "12-ragnhildur.jpg",
    "Hörður Ragnarsson": "13-hordur.jpg",
    "Sæþór Már Hinriksson": "14-saethor.jpg",
    "Ásta Björg Björgvinsdóttir": "15-asta.jpg",
    "Gísli J. Jónatansson": "16-gisli.jpg",
    "Dröfn Skorradóttir": "22-drofn.jpg",
    "Ágúst Guðjónsson": "23-agust.jpg",
    "Hafsteinn Bergmann Gunnarsson": "24-hafsteinn.jpg",
    "Björg Ósk Gunnarsdóttir": "25-bjorg-osk.jpg",
    "Björn Ívar Björnsson": "26-bjorn-ivar.jpg",
    "Gyða Björg Olgeirsdóttir": "27-gyda.jpg",
    "Arnar Már Davíðsson": "28-arnar-mar.jpg",
    "Linda Björk Hávarðardóttir": "29-linda-bjork.jpg",
    "Arnþór Árni Logason": "30-arnthor.jpg",
    "Bragi Ingólfsson": "31-bragi.jpg",
    "Steinþór Ólafur Guðrúnarson": "32-steinthor.jpg",
    "Olga Hrönn Olgeirsdóttir": "33-olga.jpg",
    "Breki Halldórsson Bachmann": "34-breki.jpg",
    "Inga Þyri Kjartansdóttir": "35-inga.jpg",
    "Ólafur Ólafsson": "36-olafur.jpg",
    "Jóhann Karl Sigurðsson": "37-johann-karl.jpg",
    "Ívar Orri Aronsson": "38-ivar-orri.jpg",
    "Milla Ósk Magnúsdóttir": "39-milla.jpg",
    "Lárus Sigurður Lárusson": "40-larus.jpg",
    "Hulda Finnlaugsdóttir": "41-hulda.jpg",
    "Aðalsteinn Haukur Sverrisson": "42-adalsteinn.jpg",
    "Árelía Eydís Guðmundsdóttir": "43-arelia.jpg",
    "Níels Árni Lund": "44-niels.jpg",
    "Hjálmar Waag Árnason": "45-hjalmar.jpg",
}


def detect_ext(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff": return "jpg"
    if data[:4] == b"\x89PNG": return "png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return "webp"
    return "jpg"


def download(url: str) -> bytes | None:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Referer": REFERER,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except Exception as e:
        print(f"   download failed: {e}")
        return None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # Find every framsoknrvk.is photo URL row
    pat = re.compile(
        r"\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'(?:[^'\\]|\\.)*?'\s*,\s*"
        r"'(https?://[^']*framsoknrvk\.is[^']*)'"
    )
    rows = pat.findall(src)
    print(f"Found {len(rows)} candidate rows pointing at framsoknrvk.is")

    new_src = src
    swapped = 0
    skipped = 0
    for name, old_url in rows:
        new_filename = NAME_TO_NEW_URL.get(name)
        if not new_filename:
            print(f"  ? no mapping for {name!r}")
            skipped += 1
            continue
        new_url = f"https://www.framsoknrvk.is/assets/candidates/{new_filename}"
        data = download(new_url)
        if not data or not data.startswith((b"\xff\xd8\xff", b"\x89PNG", b"RIFF")):
            print(f"  ✗ {name!r}: download not an image")
            skipped += 1
            continue
        h = hashlib.sha256(data).hexdigest()[:16]
        ext = detect_ext(data)
        out = IMG_DIR / f"{h}.{ext}"
        if not out.exists():
            out.write_bytes(data)
        local_path = f"images/candidates/{h}.{ext}"
        # Replace this specific row's URL
        new_src = new_src.replace(f"'{old_url}'", f"'{local_path}'", 1)
        swapped += 1
        print(f"  ✓ {name[:35]:<37} → {out.name}")

    if new_src != src:
        CANDIDATES_JS.write_text(new_src, encoding="utf-8")
    print(f"\nSwapped: {swapped}, skipped: {skipped}")


if __name__ == "__main__":
    main()
