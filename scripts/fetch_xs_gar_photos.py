#!/usr/bin/env python3
"""
Fetch all candidate photos from xs.is/frambjodendur-i-gardabae,
download each, build a photos result JSON for GAR.S candidates.
The user wants ALL existing photos replaced with the official party-site versions.
"""
import json
import re
import sys
import urllib.request
import hashlib
from pathlib import Path

ROOT = Path(__file__).parent.parent
HTML_PATH = ROOT / "tmp_xs_gar.html"
IMG_DIR = ROOT / "images" / "candidates"
OUT = ROOT / "scan_results" / "photos_2026-05-01_GAR_S_AUDITED.json"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    html = HTML_PATH.read_text(encoding="utf-8")
    # Strip scripts/styles
    body = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    body = re.sub(r"<style[\s\S]*?</style>", " ", body, flags=re.IGNORECASE)

    # Split on img tags
    parts = re.split(r"(<img[^>]+>)", body)

    pairs = []
    for i, part in enumerate(parts):
        if not part.startswith("<img"):
            continue
        src_m = re.search(r'src="([^"]+)"', part)
        if not src_m or not src_m.group(1).startswith("http"):
            continue
        url = src_m.group(1)
        following = re.sub(r"<[^>]+>", " ", parts[i + 1] if i + 1 < len(parts) else "")
        following = re.sub(r"\s+", " ", following).strip()
        # Extract ballot number + full name
        ballot_m = re.match(r"(\d+)\.\s*(.+?)(?:\s+\S+(?:fræðingur|stjóri|maður|nemi|þjálfari|kennari|starfsmaður|fulltrúi|ráðgjafi|stjóri|læknir|fulltrúi|verkfræðingur))", following)
        if not ballot_m:
            # fallback: take first two-three words after the ballot number
            ballot_m = re.match(r"(\d+)\.\s*((?:\S+\s+){1,4}\S+)\s", following)
        if not ballot_m:
            continue
        ballot = int(ballot_m.group(1))
        # Capture name as the first 3 words (Icelandic names are typically 2-4 words)
        words_m = re.match(r"(\d+)\.\s*((?:\S+\s+){1,4}\S+?)\s+([a-záéíóúýþæö])", following.lower())
        # Better: capture up to a comma or known title keyword
        name_m = re.match(r"\d+\.\s*([^,]+?)\s+(?:Stjórn|Fjárm|Kennari|Sérfræðingur|Viðskipti|F\.v\.|Grunnskóla|F\.v|Stjór|Lögfr|Deildarstjóri|Bókmennta|Launaráðg|Hjúkr|Rafverk|Slökkvi|Íþrótta)", following)
        if name_m:
            name = name_m.group(1).strip().rstrip(",").strip()
        else:
            # take the chars between "<ballot>. " and the first comma or end
            name = re.match(r"\d+\.\s*([^,\.]+?)\s+\S+\s+\S", following)
            name = name.group(1).strip() if name else following[:60]
        pairs.append({
            "ballot": ballot,
            "name_from_page": name,
            "url": url,
            "context": following[:140],
        })

    print(f"Extracted {len(pairs)} photo candidates from page:")
    for p in pairs:
        print(f"  #{p['ballot']:>2} {p['name_from_page']:<40} -> ...{p['url'][-50:]}")

    # Now match against candidates.js GAR.S list (verified by reading the file ourselves)
    src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")
    i = src.find("const GAR")
    s_open = re.search(r"\n  S\s*:\s*\{", src[i:])
    list_open = re.search(r"\n    list:\s*\[", src[i + s_open.end():])
    list_start = i + s_open.end() + list_open.end()
    # Find list end (the matching `]` at the same indent)
    list_end = src.find("\n    ],", list_start)
    list_block = src[list_start:list_end]
    # Parse rows: [N, 'Name', 'Occ', ...]
    rows = re.findall(r"\[(\d+)\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,", list_block)
    gar_s_names = {int(b): n.replace("\\'", "'") for b, n in rows}
    print(f"\nGAR.S candidates in candidates.js: {len(gar_s_names)}")

    # Match
    matched = []
    for p in pairs:
        if p["ballot"] not in gar_s_names:
            print(f"  ! ballot {p['ballot']} not in GAR.S; skipping")
            continue
        full_name = gar_s_names[p["ballot"]]
        p["name"] = full_name
        matched.append(p)

    print(f"\nMatched {len(matched)}/{len(pairs)} to candidates.js")

    # Download each image
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for p in matched:
        url = p["url"]
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
        except Exception as e:
            print(f"  ! download failed for {p['name']}: {e}")
            continue
        # Detect type from header bytes
        ext = "png"
        if data[:3] == b"\xff\xd8\xff":
            ext = "jpg"
        elif data[:4] == b"\x89PNG":
            ext = "png"
        elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
            ext = "webp"
        h = hashlib.sha256(data).hexdigest()[:16]
        local_path = IMG_DIR / f"{h}.{ext}"
        local_path.write_bytes(data)
        rel_path = f"images/candidates/{h}.{ext}"
        print(f"  ✓ #{p['ballot']:>2} {p['name']:<40} {rel_path}")
        results.append({
            "id": f"GAR.S.{p['ballot']}",
            "muni_slug": "gardabaer",
            "party_code": "S",
            "ballot": p["ballot"],
            "name": p["name"],
            "photo_url": url,
            "photo_local": rel_path,
            "source": "https://xs.is/frambjodendur-i-gardabae",
        })

    out = {
        "scan_type": "photos",
        "scan_date": "2026-05-01",
        "agent_note": "GAR.S photos from xs.is/frambjodendur-i-gardabae — official party site, replace all existing",
        "results": results,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {OUT.relative_to(ROOT)} — {len(results)} entries.")


if __name__ == "__main__":
    main()
