"""Take the captured intros from xb_intros.json + Kristín Anna's photo URL,
extract clean IS bios per candidate, download every photo to images/candidates/
with sha-256-prefixed filename, and write a final structured JSON for the
candidates.js update step.
"""
from __future__ import annotations
import hashlib, json, re, urllib.request
from pathlib import Path

SRC  = Path("C:/Windows/Temp/xb_intros.json")
OUT  = Path("C:/Windows/Temp/xb_bios.json")
DEST = Path("images/candidates")
DEST.mkdir(parents=True, exist_ok=True)

# Kristín Anna's photo wasn't in the script's original capture; fetched separately.
EXTRA_PHOTOS = {
    2: "https://scontent-dub4-1.xx.fbcdn.net/v/t39.30808-6/659087642_122121980751195973_9208913944046374712_n.jpg?stp=cp6_dst-jpg_p526x296_tt6&_nc_cat=104&ccb=1-7&_nc_sid=7b2446&_nc_ohc=k0Li5-XUorkQ7kNvwE7qEo",
}

# Names from the existing list (so we keep canonical Icelandic spelling)
NAMES = {
    1:  "Sigurbjörn Rafn Úlfarsson",
    2:  "Kristín Anna Oddsdóttir",
    3:  "Valgeir Örn Kristjánsson",
    4:  "Ragnheiður Ingimundardóttir",
    5:  "Röfn Friðriksdóttir",
    6:  "Silja Dagrún Júlíusdóttir",
    7:  "Halldór Jónsson",
    8:  "Andri Hrafn Ásgeirsson",
    9:  "Árný Helga Birkisdóttir",
    10: "Sigríður Drífa Þórólfsdóttir",
}

def extract_is_bio(n: int, raw: str) -> str:
    """Pull just the IS half of the bilingual post for candidate n.
    Cuts at 'Candidate Introduction'/'Candidate Presentation' (start of EN
    translation) or at the next 'Kynning á frambjóðanda' marker (next post)."""
    # find the 'Kynning á frambjóðanda - N' marker
    m = re.search(r"Kynning\s+á\s+frambjóðanda\s*-\s*" + str(n) + r"[.\s]*[Ss]æti", raw)
    if not m:
        return ""
    body = raw[m.start():]
    # cut at FB English translation header or next intro / chrome
    cut = re.search(
        r"(Candidate\s+(?:Introduction|Presentation)|All reactions|"
        r"Kynning\s+á\s+frambjóðanda\s*-\s*(?!" + str(n) + r")\d|FacebookFacebookFacebook)",
        body,
    )
    if cut:
        body = body[:cut.start()]
    body = re.sub(r"\.{2,}\s*See more\s*$", "", body.strip())
    body = re.sub(r"\s+\.{2,}\s*See more.*$", "", body.strip())
    body = re.sub(r"^Kynning\s+á\s+frambjóðanda[^.]+?[Ss]æti[.\s]*", "", body)
    return body.strip()

def hash_save(url: str, n: int, name: str) -> tuple[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req).read()
    h = hashlib.sha256(data).hexdigest()[:16]
    out_path = DEST / f"{h}.jpg"
    if not out_path.exists():
        out_path.write_bytes(data)
    print(f"  {n:>2}  {name:35s}  {len(data):>7d}b  {h}.jpg")
    return h, str(out_path).replace("\\", "/")

def main():
    src = json.loads(SRC.read_text(encoding="utf-8"))
    rows = []
    for c in sorted(src["candidates"], key=lambda x: x["n"]):
        n = c["n"]
        bio = extract_is_bio(n, c["text"])
        photo_url = c["photo_url"] or EXTRA_PHOTOS.get(n)
        h, path = (None, None)
        if photo_url:
            h, path = hash_save(photo_url, n, NAMES.get(n, "?"))
        rows.append({
            "n": n,
            "name": NAMES.get(n, "?"),
            "bio_is": bio,
            "photo_url": photo_url,
            "photo_hash": h,
            "image_path": path.replace("F:/Claude Projects/iceland-elections/", "") if path else None,
        })
    OUT.write_text(json.dumps({"candidates": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(rows)} entries -> {OUT}")

if __name__ == "__main__":
    main()
