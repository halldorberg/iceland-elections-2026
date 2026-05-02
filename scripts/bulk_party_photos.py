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
    """Return list of dicts per candidate row in this party block.
    Each dict has either:
      - photo_replace_start/photo_replace_end (existing photo string or null to replace)
      - insertion_point (no 4th field; insert ", '<photo>'" before this offset)
    """
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
            row_end_in_text = p  # absolute file offset of `]` is party_start + p - 1
            # Match `[N, 'name', 'occ'`
            m = re.match(
                r"\[\s*(\d+)\s*,\s*'((?:\\'|[^'])*)'\s*,\s*'((?:\\'|[^'])*)'(.*)",
                row_text, re.DOTALL,
            )
            if not m:
                continue
            ballot = int(m.group(1))
            name = m.group(2).replace("\\'", "'")
            rest_off_in_row = m.start(4)  # offset of 4th group in row_text
            rest = m.group(4)
            row_text_len = len(row_text)
            # ABSOLUTE file offset of where `rest` starts (right after closing `'` of occupation)
            rest_abs = party_start + row_start + rest_off_in_row
            row_close_abs = party_start + p - 1  # absolute offset of the row's closing `]`

            photo_value = None
            photo_replace_start = None
            photo_replace_end = None
            insertion_point = None

            if rest.startswith(","):
                after_comma = rest[1:]
                after_strip = after_comma.lstrip()
                leading_ws = len(after_comma) - len(after_strip)
                photo_field_abs = rest_abs + 1 + leading_ws  # absolute position of 4th field
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
                    photo_replace_start = photo_field_abs
                    photo_replace_end = photo_field_abs + (end_q + 1)
                elif after_strip.startswith("null"):
                    photo_value = None
                    photo_replace_start = photo_field_abs
                    photo_replace_end = photo_field_abs + 4
            else:
                # No 4th field. Insert ", '<photo>'" RIGHT BEFORE the closing `]` of the row.
                insertion_point = row_close_abs
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


def normalize_name(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"([a-zæöáéíóúýþð])([A-ZÆÖÁÉÍÓÚÝÞÐ])", r"\1 \2", s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("ð", "d").replace("Ð", "d").replace("þ", "th").replace("Þ", "th")
    s = s.replace("æ", "ae").replace("Æ", "ae").replace("ö", "o").replace("Ö", "o")
    s = re.sub(r"[^a-zA-Z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def match_candidate(scraped_name, rows, used):
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
        if len(common) < 2:
            sole = next(iter(common))
            if len(sole) < 6:
                continue
            if not (sole == target_tokens[-1] and sole == cand_tokens[-1]):
                continue
        score = len(common) / max(len(target_set), len(cand_set))
        if score > best_score:
            best_score = score
            best = r
    if best_score >= 0.4:
        return best
    return None


# ─── Source extractors ───────────────────────────────────────────────────────

def extract_alisti_rty():
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
        pairs.append({"ballot": ballot, "name": name_slug.replace("-", " "), "photo_url": url})
    return pairs


def extract_framsokn_mulathing():
    html = fetch_html("https://www.framsokn.is/sveitarfelog/mulathing")
    pairs = []
    section_start = html.find("Kjörnir fulltrúar")
    if section_start < 0:
        return pairs
    body = html[section_start:]
    img_pat = re.compile(
        r'src="(https://framerusercontent\.com/images/[A-Za-z0-9]+\.(?:jpg|jpeg|png|webp))[^"]*"'
    )
    name_pat = re.compile(
        r'>\s*([A-ZÁÉÍÓÚÝÞÆÖa-záéíóúýþæö][\w\sÁÉÍÓÚÝÞÆÖáéíóúýþæö.\-]+?)\s*<.*?(\d+)\.\s*sæti á lista',
        re.DOTALL,
    )
    matches = list(name_pat.finditer(body))
    img_matches = list(img_pat.finditer(body))
    for m in matches:
        nm = re.sub(r"\s+", " ", m.group(1)).strip()
        if "sæti" in nm.lower() or len(nm) < 3:
            continue
        ballot = int(m.group(2))
        pos = m.start()
        prev_img = None
        for im in img_matches:
            if im.start() > pos:
                break
            prev_img = im.group(1)
        if prev_img:
            if any(p["photo_url"] == prev_img for p in pairs):
                continue
            pairs.append({"ballot": ballot, "name": nm, "photo_url": prev_img})
    return pairs


def extract_midflokkurinn_mulathing():
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
    html = fetch_html("https://xs.is/frambjodendur-i-fjardabyggd")
    pat = re.compile(r'src="(https://images\.prismic\.io/samfylkingin/[A-Za-z0-9_]+_[^"]+\.(?:png|jpg|jpeg|webp))[^"]*"')
    urls = []
    for m in pat.finditer(html):
        u = m.group(1)
        if u not in urls:
            urls.append(u)
    pairs = []
    for i, u in enumerate(urls, start=1):
        fname = u.rsplit("/", 1)[-1]
        if "_" not in fname:
            continue
        name_part = fname.split("_", 1)[1].rsplit(".", 1)[0]
        if name_part.lower() in {"akranes", "fjardabyggd", "logo"}:
            continue
        try:
            from urllib.parse import unquote
            name_part = unquote(name_part)
        except Exception:
            pass
        pairs.append({"ballot": len(pairs) + 1, "name": name_part, "photo_url": u})
    return pairs


def extract_vidreisn_mulathing():
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
        if re.match(r"^\d+-\d+x\d+\.", fname):
            continue
        base = re.sub(r"-\d+x\d+\..*$", "", fname)
        base = re.sub(r"-scaled$|-e\d+$", "", base)
        base = re.sub(r"^\d+\.?", "", base)
        base = re.sub(r"\d{6,}$", "", base)
        name = re.sub(r"[-]+", " ", base).strip()
        pairs.append({"ballot": None, "name": name, "photo_url": url})
    return pairs


def extract_vg_reykjavik():
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
        base = re.sub(r"-\d+x\d+\.(?:jpg|jpeg|png|webp)$", lambda mm: "." + mm.group(0).split(".")[-1], url)
        pairs.append({"ballot": ballot, "name": slug.replace("-", " "), "photo_url": base})
    return pairs


SOURCES = {
    "alisti": {
        "extractor": extract_alisti_rty,
        "muni": "RTY", "party": "RYA",
        "label": "Á-listinn Rangárþing ytra",
        "match_by": "ballot",
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
        "match_by": "name",
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

    used = set()
    swaps = []
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
        for p in pairs:
            row = match_candidate(p["name"], rows, used)
            if row:
                used.add(row["ballot"])
                swaps.append((row, p["photo_url"], p["name"]))

    print(f"  matched {len(swaps)} → candidates")
    apply_list = []  # list of (op_kind, offset, end_offset_or_None, payload, row, scraped_name)
    n_done = 0
    n_already = 0
    n_failed = 0
    for row, photo_url, scraped_name in swaps:
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
        if row["photo_replace_start"] is not None:
            apply_list.append(("replace",
                               row["photo_replace_start"],
                               row["photo_replace_end"],
                               f"'{local_path}'",
                               row, scraped_name))
        else:
            apply_list.append(("insert",
                               row["insertion_point"],
                               None,
                               f", '{local_path}'",
                               row, scraped_name))
        n_done += 1
        print(f"    ✓ #{row['ballot']:>2} {row['name'][:35]:<37} → {h}.{ext}")

    new_src = src_text
    if not dry_run:
        # Single descending pass — applies BOTH replaces and inserts in one sorted order
        # so an insert at offset N never invalidates a replace's offset > N.
        for kind, off, end, payload, row, sn in sorted(apply_list, key=lambda x: -x[1]):
            if kind == "replace":
                new_src = new_src[:off] + payload + new_src[end:]
            else:  # insert before offset
                new_src = new_src[:off] + payload + new_src[off:]

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
