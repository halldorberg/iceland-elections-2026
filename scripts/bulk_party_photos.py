#!/usr/bin/env python3
"""
bulk_party_photos.py
────────────────────
Scrape candidate photos from a target list of party-source URLs and write them
into js/data/candidates.js as local /images/candidates/<hash>.<ext> paths.

Each scrape source has a hand-coded extractor that returns ordered (name, photo_url)
tuples, then we match by ballot order or by name into the corresponding party
list block in candidates.js.

Run with:
    python scripts/bulk_party_photos.py [--source <name>] [--dry-run]
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
IMG_DIR = ROOT / "images" / "candidates"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")


# ─── HTTP fetchers ────────────────────────────────────────────────────────────

def fetch_html(url, referer=None):
    cmd = ["curl", "-sL", "-A", UA, "--compressed", "--max-time", "25"]
    if referer:
        cmd += ["-H", f"Referer: {referer}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=40)
        return r.stdout.decode("utf-8", errors="replace") if r.returncode == 0 else ""
    except Exception:
        return ""


def fetch_image(url, referer=None):
    cmd = ["curl", "-sL", "-A", UA, "--compressed", "--max-time", "30",
           "-H", "Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
           "-H", "Sec-Fetch-Dest: image",
           "-H", "Sec-Fetch-Mode: no-cors",
           "-H", "Sec-Fetch-Site: cross-site"]
    if referer:
        cmd += ["-H", f"Referer: {referer}"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=40)
        if r.returncode == 0 and len(r.stdout) > 500:
            return r.stdout
    except Exception:
        pass
    return None


def detect_ext(d):
    if d[:3] == b"\xff\xd8\xff": return "jpg"
    if d[:4] == b"\x89PNG": return "png"
    if d[:4] == b"RIFF" and d[8:12] == b"WEBP": return "webp"
    if d[:4] == b"\x00\x00\x00 " and d[4:12] == b"ftypavif": return "avif"
    return "jpg"


# ─── candidates.js parser ────────────────────────────────────────────────────

def find_party_block(src, muni_const, party_code):
    m = re.search(r"\bconst " + muni_const + r"\s*=\s*\{", src)
    if not m: return None, None
    p, d = m.end() - 1, 0
    while p < len(src):
        if src[p] == "{": d += 1
        elif src[p] == "}":
            d -= 1
            if d == 0: break
        p += 1
    muni_start = m.end() - 1
    muni_end = p + 1
    muni_block = src[muni_start:muni_end]
    pm = re.search(r"\n  " + party_code + r"\s*:\s*\{", muni_block)
    if not pm: return None, None
    p, d = pm.end() - 1, 0
    while p < len(muni_block):
        if muni_block[p] == "{": d += 1
        elif muni_block[p] == "}":
            d -= 1
            if d == 0: break
        p += 1
    return muni_start + pm.end() - 1, muni_start + p + 1


def parse_party_rows(src, party_start, party_end):
    """Return list of dicts per candidate row in this party block."""
    text = src[party_start:party_end]
    lm = re.search(r"\n\s+list\s*:\s*\[", text)
    if not lm:
        return []
    p = lm.end()
    rows = []
    depth = 1
    while p < len(text) and depth > 0:
        ch = text[p]
        if ch == "[":
            row_start = p
            local_d = 1
            p += 1
            in_str = False
            str_ch = None
            while p < len(text) and local_d > 0:
                c = text[p]
                if in_str:
                    if c == "\\":
                        p += 2
                        continue
                    if c == str_ch:
                        in_str = False
                elif c in ('"', "'"):
                    in_str = True
                    str_ch = c
                elif c == "[":
                    local_d += 1
                elif c == "]":
                    local_d -= 1
                p += 1
            row_text = text[row_start:p]
            m = re.match(
                r"\[\s*(\d+)\s*,\s*'((?:\\'|[^'])*)'\s*,\s*'(?:\\'|[^'])*'(.*)",
                row_text, re.DOTALL,
            )
            if m:
                ballot = int(m.group(1))
                name = m.group(2).replace("\\'", "'")
                rest_start = m.start(3)
                rest = m.group(3)
                photo_value = None
                photo_replace_start = None
                photo_replace_end = None
                # Position of next non-whitespace, non-comma after occupation
                if rest.startswith(","):
                    after_comma = rest[1:]
                    after_strip = after_comma.lstrip()
                    leading_ws = len(after_comma) - len(after_strip)
                    photo_field_start = rest_start + 1 + leading_ws
                    if after_strip.startswith("'"):
                        end_q = 1
                        s2 = after_strip
                        while end_q < len(s2):
                            if s2[end_q] == "\\":
                                end_q += 2
                                continue
                            if s2[end_q] == "'":
                                break
                            end_q += 1
                        photo_value = s2[1:end_q]
                        # absolute offsets within the file
                        photo_replace_start = party_start + row_start + photo_field_start
                        photo_replace_end = photo_replace_start + (end_q + 1)
                    elif after_strip.startswith("null"):
                        photo_value = None
                        photo_replace_start = party_start + row_start + photo_field_start
                        photo_replace_end = photo_replace_start + 4
                # Insertion point if no photo field at all (insert ", 'X'" before next , or ])
                insertion_point = None
                if photo_replace_start is None:
                    # rest is either "," "]" or ", { … }". We insert before the , or ]
                    rs = rest.lstrip()
                    insertion_point = party_start + row_start + rest_start + (len(rest) - len(rest.lstrip()))
                rows.append({
                    "ballot": ballot,
                    "name": name,
                    "photo_value": photo_value,
                    "photo_replace_start": photo_replace_start,
                    "photo_replace_end": photo_replace_end,
                    "insertion_point": insertion_point,
                })
        elif ch == "]":
            depth -= 1
            p += 1
        else:
            p += 1
    rows.sort(key=lambda r: r["ballot"])
    return rows


# ─── Name matching ────────────────────────────────────────────────────────────

def normalize_name(s):
    """Strip diacritics, lowercase, split CamelCase, drop punctuation."""
    if not s:
        return ""
    # Normalize NFC first to recombine combining marks (xs.is filenames use NFD)
    s = unicodedata.normalize("NFC", s)
    # Split CamelCase: insert space before uppercase that follows lowercase
    s = re.sub(r"([a-zæöáéíóúýþð])([A-ZÆÖÁÉÍÓÚÝÞÐ])", r"\1 \2", s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("ð", "d").replace("Ð", "d").replace("þ", "th").replace("Þ", "th")
    s = s.replace("æ", "ae").replace("Æ", "ae").replace("ö", "o").replace("Ö", "o")
    s = re.sub(r"[^a-zA-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def match_candidate(scraped_name, rows, used):
    """Return the row whose name best matches scraped_name. Strict: at least
    the last-name token of the scraped string MUST also appear in the row's
    name (or vice-versa for single-name scrapes). Otherwise prevent first-name
    only false positives like "Katrín" matching "Ketill"."""
    if not scraped_name:
        return None
    target = normalize_name(scraped_name)
    target_tokens = target.split()
    if not target_tokens:
        return None
    target_set = set(target_tokens)
    best = None
    best_score = 0
    for r in rows:
        if r["ballot"] in used:
            continue
        cand = normalize_name(r["name"])
        cand_tokens = cand.split()
        cand_set = set(cand_tokens)
        if not cand_set:
            continue
        common = target_set & cand_set
        if not common:
            continue
        # Strict requirement: at least 2 tokens must match, OR the single
        # matching token must be a last-name (≥6 chars heuristic — first names
        # in Icelandic tend to be shorter and more common).
        if len(common) < 2:
            sole = next(iter(common))
            if len(sole) < 6:
                continue
            # If single match is the scraped's last token AND the candidate's
            # last token, accept; otherwise reject.
            if not (sole == target_tokens[-1] and sole == cand_tokens[-1]):
                continue
        score = len(common) / max(len(target_set), len(cand_set))
        if score > best_score:
            best_score = score
            best = r
    if best_score >= 0.4:
        return best
    return None


# ─── Source extractors — return list of (name, photo_url) ────────────────────

def extract_alisti_rty():
    """alisti.is/frambjodendur — Á-listinn Rangárþing ytra (RTY.RYA).
    File pattern: NNN-First-Middle-Last1-...jpg → ballot NNN."""
    html = fetch_html("https://alisti.is/frambjodendur/")
    pat = re.compile(
        r'src="(https?://alisti\.is/wp-content/uploads/2022/05/(\d+)-([A-Za-z0-9-]+)-\d+x\d+\.(?:jpg|jpeg|png|webp))"'
    )
    pairs = []
    seen = set()
    for m in pat.finditer(html):
        url, ballot, name_slug = m.group(1), int(m.group(2)), m.group(3)
        if ballot in seen:
            continue
        seen.add(ballot)
        # Reconstruct a "name" from the slug — used only for fuzzy matching.
        name = name_slug.replace("-", " ")
        pairs.append({"ballot": ballot, "name": name, "photo_url": url})
    return pairs


def extract_framsokn_mulathing():
    """framsokn.is/sveitarfelog/mulathing — Framsókn Múlaþing (MUT.B).
    Each candidate appears as <name> + img. We walk the HTML and pair img URL
    with the next preceding 'X. sæti á lista' text-block name."""
    html = fetch_html("https://www.framsokn.is/sveitarfelog/mulathing")
    pairs = []
    # Find the "Kjörnir fulltrúar" section start, then walk every framerusercontent img,
    # and for each grab the closest preceding 'Name' (stripped HTML) up to the previous image.
    section_start = html.find("Kjörnir fulltrúar")
    if section_start < 0:
        return pairs
    # Use everything after the section start
    body = html[section_start:]
    img_pat = re.compile(
        r'src="(https://framerusercontent\.com/images/[A-Za-z0-9]+\.(?:jpg|jpeg|png|webp))[^"]*"'
    )
    name_pat = re.compile(r'>\s*([A-ZÁÉÍÓÚÝÞÆÖa-záéíóúýþæö][\w\sÁÉÍÓÚÝÞÆÖáéíóúýþæö.\-]+?)\s*<.*?(\d+)\.\s*sæti á lista', re.DOTALL)
    # For each candidate-list image (we expect the FIRST image of the relevant section to be a banner),
    # find the matching name block by searching backwards from the image.
    matches = list(name_pat.finditer(body))
    img_matches = list(img_pat.finditer(body))
    # Build a list of candidates from the name patterns.
    cands_by_ballot = {}
    for m in matches:
        nm = re.sub(r"\s+", " ", m.group(1)).strip()
        # Skip generic strings like "Kjörnir fulltrúar"
        if "sæti" in nm.lower() or len(nm) < 3:
            continue
        ballot = int(m.group(2))
        cands_by_ballot.setdefault(ballot, nm)
    # For each candidate, find the framerusercontent image that occurs JUST BEFORE the name match.
    for m in matches:
        nm = re.sub(r"\s+", " ", m.group(1)).strip()
        if "sæti" in nm.lower() or len(nm) < 3:
            continue
        ballot = int(m.group(2))
        pos = m.start()
        # Last img before pos
        prev_img = None
        for im in img_matches:
            if im.start() > pos:
                break
            prev_img = im.group(1)
        if prev_img:
            # Avoid the section's banner image (first img); enforce that the same image
            # is NOT used by an earlier ballot (we sweep in order).
            if any(p["photo_url"] == prev_img for p in pairs):
                continue
            pairs.append({"ballot": ballot, "name": nm, "photo_url": prev_img})
    return pairs


def extract_midflokkurinn_mulathing():
    """midflokkurinn.is/mulathing — Miðflokkurinn Múlaþing (MUT.M).
    Files: /2026/04/<NN>.-<Name>.jpg or .jpeg (NN may have leading dot/dash variations)."""
    html = fetch_html("https://midflokkurinn.is/mulathing")
    pat = re.compile(
        r'src="(https://midflokkurinn\.is/wp-content/uploads/2026/04/(\d+)\.-?([A-Za-z0-9\-]+?)(?:-rotated|-scaled)?\.(?:jpg|jpeg|png|webp))"'
    )
    pairs = []
    seen = set()
    for m in pat.finditer(html):
        url, ballot, slug = m.group(1), int(m.group(2)), m.group(3)
        if ballot in seen:
            continue
        seen.add(ballot)
        pairs.append({"ballot": ballot, "name": slug.replace("-", " "), "photo_url": url})
    return pairs


def extract_xs_fjardabyggd():
    """xs.is/frambjodendur-i-fjardabyggd — Samfylkingin Fjarðabyggð (FJD.S).
    Photos are prismic.io URLs in DOM order. Use ballot order from DOM."""
    html = fetch_html("https://xs.is/frambjodendur-i-fjardabyggd")
    pat = re.compile(r'src="(https://images\.prismic\.io/samfylkingin/[A-Za-z0-9_]+_[^"]+\.(?:png|jpg|jpeg|webp))[^"]*"')
    urls = []
    for m in pat.finditer(html):
        u = m.group(1)
        if u not in urls:
            urls.append(u)
    # Filter out obvious banner images (no name fragment after underscore).
    pairs = []
    for i, u in enumerate(urls, start=1):
        # Filename portion after the imgix-id underscore is the name encoded.
        fname = u.rsplit("/", 1)[-1]
        if "_" not in fname:
            continue
        name_part = fname.split("_", 1)[1].rsplit(".", 1)[0]
        # Skip if it looks like a banner like "Akranes" or "Akranes.sæti"
        if name_part.lower() in {"akranes", "fjardabyggd", "logo"}:
            continue
        # Decode percent-encoded combining chars by NFC
        try:
            from urllib.parse import unquote
            name_part = unquote(name_part)
        except Exception:
            pass
        pairs.append({"ballot": len(pairs) + 1, "name": name_part, "photo_url": u})
    return pairs


def extract_vidreisn_mulathing():
    """vidreisn.is/mulathing/frambjodendur — Viðreisn Múlaþing (MUT.L).
    Photos at /wp-content/uploads/2026/04/<Name>-...jpg or <NN>.<Name>-...jpg."""
    html = fetch_html("https://vidreisn.is/mulathing/frambjodendur/")
    pat = re.compile(
        r'src="(https://vidreisn\.is/wp-content/uploads/2026/04/[^"]+\.(?:jpg|jpeg|png|webp))"'
    )
    pairs = []
    seen = set()
    for m in pat.finditer(html):
        url = m.group(1)
        if url in seen:
            continue
        seen.add(url)
        fname = url.rsplit("/", 1)[-1]
        # Skip obvious non-portraits (1-1024x576.png — banner)
        if re.match(r"^\d+-\d+x\d+\.", fname):
            continue
        # Extract a name guess from filename
        base = re.sub(r"-\d+x\d+\..*$", "", fname)  # drop -WIDTHxHEIGHT.ext
        base = re.sub(r"-scaled$|-e\d+$", "", base)
        # Strip leading "<NN>." or "<NN>" prefix
        base = re.sub(r"^\d+\.?", "", base)
        # Strip random-id trailing digits like 3108862899
        base = re.sub(r"\d{6,}$", "", base)
        # Replace - with space
        name = re.sub(r"[-]+", " ", base).strip()
        pairs.append({"ballot": None, "name": name, "photo_url": url})
    return pairs


def extract_vg_reykjavik():
    """vg.is front page — Vinstrið in Reykjavík (RVK.A; the merged VG + Vor til vinstri list).
    Files: /uploads/2026/04/Vinstrid-<NN>-<Name>.jpg, NN = ballot."""
    html = fetch_html("https://www.vg.is/")
    pat = re.compile(
        r'src="(https://vg\.is/wp-content/uploads/2026/04/Vinstrid-(\d+)-([A-Za-z0-9.\-]+?)(?:-scaled|-\d+x\d+)?\.(?:jpg|jpeg|png|webp))"'
    )
    pairs = []
    seen = set()
    for m in pat.finditer(html):
        url, ballot, slug = m.group(1), int(m.group(2)), m.group(3)
        if ballot in seen:
            continue
        seen.add(ballot)
        # Use the largest/canonical URL by stripping size suffix back to base.
        base = re.sub(r"-\d+x\d+\.(?:jpg|jpeg|png|webp)$", lambda m: "." + m.group(0).split(".")[-1], url)
        pairs.append({"ballot": ballot, "name": slug.replace("-", " "), "photo_url": base})
    return pairs


def extract_klistinn_bolungarvik():
    """klistinn.is/frambjodendur — wix site, photos as static.wixstatic.com.
    Filename ends with /<NN>-<FirstName>.jpg (after fill/crop transforms)."""
    html = fetch_html("https://www.klistinn.is/frambjodendur")
    pat = re.compile(
        r'src="(https://static\.wixstatic\.com/media/[^"]+/(\d+)-([^/."]+?)\.(?:jpg|jpeg|png|webp))"'
    )
    pairs = []
    seen = set()
    for m in pat.finditer(html):
        url, ballot, slug = m.group(1), int(m.group(2)), m.group(3)
        if ballot in seen:
            continue
        seen.add(ballot)
        from urllib.parse import unquote
        first_name = unquote(slug)
        pairs.append({"ballot": ballot, "name": first_name, "photo_url": url})
    return pairs


# ─── Main pipeline ────────────────────────────────────────────────────────────

SOURCES = {
    "alisti": {
        "extractor": extract_alisti_rty,
        "muni": "RTY", "party": "RYA",
        "label": "Á-listinn Rangárþing ytra",
        "match_by": "ballot",  # ballot prefix in filename matches candidate ballot
    },
    "framsokn-mulathing": {
        "extractor": extract_framsokn_mulathing,
        "muni": "MUT", "party": "B",
        "label": "Framsókn Múlaþing",
        "match_by": "name",
    },
    "midflokkurinn-mulathing": {
        "extractor": extract_midflokkurinn_mulathing,
        "muni": "MUT", "party": "M",
        "label": "Miðflokkurinn Múlaþing",
        "match_by": "ballot",
    },
    "xs-fjardabyggd": {
        "extractor": extract_xs_fjardabyggd,
        "muni": "FJD", "party": "S",
        "label": "Samfylkingin Fjarðabyggð",
        "match_by": "name",  # ballot order in DOM is approximate
    },
    "vidreisn-mulathing": {
        "extractor": extract_vidreisn_mulathing,
        "muni": "MUT", "party": "L",
        "label": "Viðreisn (L-listinn) Múlaþing",
        "match_by": "name",
    },
    "vg-reykjavik": {
        "extractor": extract_vg_reykjavik,
        "muni": "RVK", "party": "A",
        "label": "Vinstrið Reykjavík (RVK.A)",
        "match_by": "ballot",
    },
    # K-listinn intentionally NOT processed: BLV in candidates.js only has parties
    # MMM (Máttur meyja og manna) and BBK (Betri Bolungarvík). The klistinn.is
    # candidate set (Magnús, Karen, Hjörtur, Rebekka, Katrín, …) is a separate
    # list not present in the data — adding it requires creating a new BLV.K
    # party entry.
}


def apply_source(src_text, source_name, dry_run=False):
    cfg = SOURCES[source_name]
    label = cfg["label"]
    muni = cfg["muni"]
    party = cfg["party"]
    print(f"\n=== {source_name}: {label} ({muni}.{party}) ===")
    pairs = cfg["extractor"]()
    print(f"  scraped {len(pairs)} candidate-photo pairs")
    if not pairs:
        print("  ✗ extractor returned nothing")
        return src_text, 0
    s, e = find_party_block(src_text, muni, party)
    if s is None:
        print(f"  ✗ party {muni}.{party} not in candidates.js")
        return src_text, 0
    rows = parse_party_rows(src_text, s, e)
    print(f"  party has {len(rows)} candidates")
    if not rows:
        return src_text, 0

    # Match each scraped pair to a row.
    used = set()
    swaps = []  # (row, photo_url, scraped_name)
    if cfg["match_by"] == "ballot":
        rows_by_ballot = {r["ballot"]: r for r in rows}
        for p in pairs:
            ballot = p.get("ballot")
            if ballot is None or ballot not in rows_by_ballot:
                continue
            if ballot in used:
                continue
            row = rows_by_ballot[ballot]
            used.add(ballot)
            swaps.append((row, p["photo_url"], p["name"]))
    else:
        # name fuzzy matching
        for p in pairs:
            row = match_candidate(p["name"], rows, used)
            if row:
                used.add(row["ballot"])
                swaps.append((row, p["photo_url"], p["name"]))

    # Now download + replace
    print(f"  matched {len(swaps)} → candidates")
    new_src = src_text
    n_done = 0
    n_already = 0
    n_failed = 0
    # Apply replacements from end of file backwards so offsets remain valid.
    apply_list = []
    for row, photo_url, scraped_name in swaps:
        # Skip if row already has a local photo
        if row["photo_value"] and "images/candidates/" in row["photo_value"]:
            n_already += 1
            print(f"    · #{row['ballot']:>2} {row['name'][:35]:<37} (already local)")
            continue
        data = fetch_image(photo_url, referer="https://example.com/")
        if not data:
            n_failed += 1
            print(f"    ✗ #{row['ballot']:>2} {row['name'][:35]:<37} fetch fail")
            continue
        h = hashlib.sha256(data).hexdigest()[:16]
        ext = detect_ext(data)
        out = IMG_DIR / f"{h}.{ext}"
        if not dry_run and not out.exists():
            out.write_bytes(data)
        local_path = f"images/candidates/{h}.{ext}"
        apply_list.append((row, local_path, scraped_name))
        n_done += 1
        print(f"    ✓ #{row['ballot']:>2} {row['name'][:35]:<37} → {h}.{ext}")

    # Sort apply_list by replacement offset, descending, so insertion shifts don't break later offsets.
    if not dry_run:
        # Order: those with photo_replace_start first (replacement), then insertion_point
        replace_ops = [(row, lp, sn) for (row, lp, sn) in apply_list if row["photo_replace_start"] is not None]
        insert_ops = [(row, lp, sn) for (row, lp, sn) in apply_list if row["photo_replace_start"] is None]
        # Replace in descending order by start offset
        for row, lp, sn in sorted(replace_ops, key=lambda x: -x[0]["photo_replace_start"]):
            s2 = row["photo_replace_start"]
            e2 = row["photo_replace_end"]
            new_src = new_src[:s2] + f"'{lp}'" + new_src[e2:]
        # Insert in descending order by insertion point (row had no photo field)
        for row, lp, sn in sorted(insert_ops, key=lambda x: -x[0]["insertion_point"]):
            ip = row["insertion_point"]
            new_src = new_src[:ip] + f", '{lp}'" + new_src[ip:]
    print(f"  done: {n_done} swapped, {n_already} already-local, {n_failed} failed")
    return new_src, n_done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="Run only this source (default: all)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src_text = CANDIDATES_JS.read_text(encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    sources = [args.source] if args.source else list(SOURCES.keys())
    total = 0
    for sname in sources:
        if sname not in SOURCES:
            print(f"unknown source: {sname}")
            continue
        src_text, n = apply_source(src_text, sname, dry_run=args.dry_run)
        total += n

    if not args.dry_run:
        CANDIDATES_JS.write_text(src_text, encoding="utf-8")
    print(f"\nTotal applied: {total}")


if __name__ == "__main__":
    main()
