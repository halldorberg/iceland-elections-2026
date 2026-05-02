#!/usr/bin/env python3
"""
bulk_vg_munis.py
────────────────
Pull all VG (Vinstri Græn / Vinstrið) candidate photos from vg.is for the
6 munis it has lists in. The vg.is front page uses a JetSmartFilters
"Sveitafélög" radio filter to swap which muni's candidates show; the actual
data lives behind /wp-admin/admin-ajax.php?action=jet_smart_filters.

This script POSTs that AJAX endpoint per muni term-ID, parses the returned
HTML for (ballot, name, photo_url) per candidate, then matches each one to
the correct party block in candidates.js (V for most munis, A for those
where VG runs as a coalition list).
"""
import hashlib
import json
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

# Per-muni: (term-id-on-vg.is, candidates.js muni const, party-code-to-fill).
# Term IDs scraped from vg.is JetSmartFilters. Party codes verified against
# candidates.js: VG runs as 'V' in most munis, but as 'A' in BBD/HAF/RVK
# where it's a coalition list ("Vinstrið og óháð" etc.).
MUNI_TARGETS = [
    (158, "AKU", "V"),   # Akureyri
    (164, "BBD", "A"),   # Borgarbyggð (coalition)
    (160, "HAF", "A"),   # Hafnarfjörður (coalition)
    (161, "KOP", "V"),   # Kópavogur
    (159, "MUT", "V"),   # Múlaþing
    (157, "RVK", "A"),   # Reykjavík (Vinstrið — coalition with Vor til vinstri)
]


# ─── HTTP ────────────────────────────────────────────────────────────────────

def fetch_ajax(term_id):
    cmd = [
        "curl", "-sL", "-A", UA, "--compressed", "--max-time", "30",
        "-X", "POST",
        "https://www.vg.is/wp-admin/admin-ajax.php",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-H", "Referer: https://www.vg.is/",
        "-H", "X-Requested-With: XMLHttpRequest",
        "--data-urlencode", "action=jet_smart_filters",
        "--data-urlencode", "provider=jet-engine/frambodin",
        "--data", f"query[_tax_query_sveitafelag]={term_id}",
        "--data-urlencode", "defaults[lisitng_id]=14772",
        "--data-urlencode", "defaults[posts_num]=1",
        "--data-urlencode", "defaults[custom_query]=yes",
        "--data-urlencode", "defaults[custom_query_id]=14",
        "--data-urlencode", "settings[lisitng_id]=14772",
        "--data-urlencode", "settings[posts_num]=1",
        "--data-urlencode", "settings[custom_query]=yes",
        "--data-urlencode", "settings[custom_query_id]=14",
        "--data-urlencode", "settings[is_archive_template]=",
        "--data-urlencode", "settings[post_status][]=publish",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=40)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception as e:
        print(f"   AJAX error: {e}")
        return None


def fetch_image(url):
    cmd = [
        "curl", "-sL", "-A", UA, "--compressed", "--max-time", "30",
        "-H", "Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "-H", "Sec-Fetch-Dest: image",
        "-H", "Sec-Fetch-Mode: no-cors",
        "-H", "Sec-Fetch-Site: cross-site",
        "-H", "Referer: https://www.vg.is/",
        url,
    ]
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
    return "jpg"


# ─── Parse VG AJAX response ──────────────────────────────────────────────────

def parse_vg_response(j):
    """Return list of {ballot, name, photo_url}.
    Each candidate is wrapped in jet-listing-dynamic-post-<post-id>; inside
    we have an <h*> with 'N. sæti', another <h*> with the name, and an <img>
    with the photo."""
    if not j:
        return []
    html = j.get("content", "")
    if not html:
        return []
    posts = re.split(r'jet-listing-dynamic-post-(\d+)', html)
    pairs = []
    # posts[0] = preamble; then alternating (post_id, content)
    for i in range(1, len(posts), 2):
        block = posts[i + 1] if i + 1 < len(posts) else ""
        # Extract image (first jpg/png/webp src)
        img_m = re.search(r'src="([^"]+\.(?:jpg|jpeg|png|webp))"', block)
        # Extract ballot from "X. sæti" inside an <h*>
        ballot_m = re.search(r'>(\d+)\.\s*sæti<', block)
        # Extract name — second <h*> after ballot, but easier to find any
        # <h*> that contains the candidate name (it's the only multi-word capitalised one)
        name_m = re.search(
            r'<h\d[^>]*>\s*([A-ZÁÉÍÓÚÝÞÆÖ][\w\sÁÉÍÓÚÝÞÆÖáéíóúýþæö.\-]{4,80}?)\s*</h\d>',
            block,
        )
        names = re.findall(
            r'<h\d[^>]*>\s*([^<]+?)\s*</h\d>',
            block,
        )
        # Strip tabs/newlines from each name candidate, drop "X. sæti"
        clean = [re.sub(r'\s+', ' ', n).strip() for n in names]
        clean = [n for n in clean if n and not re.match(r'^\d+\.\s*sæti$', n)]
        # The candidate name is the LAST <h*> in the block, typically
        name = clean[-1] if clean else None
        if img_m and ballot_m and name:
            pairs.append({
                "ballot": int(ballot_m.group(1)),
                "name": name,
                "photo_url": img_m.group(1),
            })
    return pairs


# ─── candidates.js parser (copy of bulk_party_photos.py logic) ──────────────

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
                r"\[\s*(\d+)\s*,\s*'((?:\\'|[^'])*)'\s*,\s*'((?:\\'|[^'])*)'(.*)",
                row_text, re.DOTALL,
            )
            if not m:
                continue
            ballot = int(m.group(1))
            name = m.group(2).replace("\\'", "'")
            rest_off_in_row = m.start(4)
            rest = m.group(4)
            rest_abs = party_start + row_start + rest_off_in_row
            row_close_abs = party_start + p - 1

            photo_value = None
            photo_replace_start = None
            photo_replace_end = None
            insertion_point = None

            if rest.startswith(","):
                after_comma = rest[1:]
                after_strip = after_comma.lstrip()
                leading_ws = len(after_comma) - len(after_strip)
                photo_field_abs = rest_abs + 1 + leading_ws
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
                insertion_point = row_close_abs
            rows.append({
                "ballot": ballot, "name": name,
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
    """Strict last-name match. ≥2 token overlap, OR a single ≥6-char last-name."""
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


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    src_text = CANDIDATES_JS.read_text(encoding="utf-8")
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    grand_total = 0
    for term_id, muni_const, party_code in MUNI_TARGETS:
        print(f"\n=== {muni_const}.{party_code} (vg.is term {term_id}) ===")
        j = fetch_ajax(term_id)
        if not j:
            print("  ✗ AJAX failed")
            continue
        pairs = parse_vg_response(j)
        print(f"  scraped {len(pairs)} candidate-photo pairs")
        if not pairs:
            continue
        s, e = find_party_block(src_text, muni_const, party_code)
        if s is None:
            print(f"  ✗ {muni_const}.{party_code} not in candidates.js")
            continue
        rows = parse_party_rows(src_text, s, e)
        print(f"  party has {len(rows)} candidates")

        # Match by name (ballot from vg.is may not align with our ballot — they sometimes differ)
        used = set()
        swaps = []
        for p in pairs:
            row = match_candidate(p["name"], rows, used)
            if row:
                used.add(row["ballot"])
                swaps.append((row, p["photo_url"], p["name"]))
            else:
                print(f"    ? no match for vg.is {p['name']!r}")

        # Apply
        apply_list = []
        n_done = n_already = n_failed = 0
        for row, photo_url, scraped_name in swaps:
            if row["photo_value"] and "images/candidates/" in row["photo_value"]:
                n_already += 1
                print(f"    · #{row['ballot']:>2} {row['name'][:35]:<37} (already local)")
                continue
            data = fetch_image(photo_url)
            if not data:
                n_failed += 1
                print(f"    ✗ #{row['ballot']:>2} {row['name'][:35]:<37} fetch fail")
                continue
            h = hashlib.sha256(data).hexdigest()[:16]
            ext = detect_ext(data)
            out = IMG_DIR / f"{h}.{ext}"
            if not out.exists():
                out.write_bytes(data)
            local_path = f"images/candidates/{h}.{ext}"
            if row["photo_replace_start"] is not None:
                apply_list.append(("replace", row["photo_replace_start"], row["photo_replace_end"],
                                   f"'{local_path}'"))
            else:
                apply_list.append(("insert", row["insertion_point"], None,
                                   f", '{local_path}'"))
            n_done += 1
            print(f"    ✓ #{row['ballot']:>2} {row['name'][:35]:<37} → {h}.{ext}")

        # Single descending-offset pass
        for kind, off, end, payload in sorted(apply_list, key=lambda x: -x[1]):
            if kind == "replace":
                src_text = src_text[:off] + payload + src_text[end:]
            else:
                src_text = src_text[:off] + payload + src_text[off:]
        print(f"  done: {n_done} swapped, {n_already} already-local, {n_failed} failed")
        grand_total += n_done

    CANDIDATES_JS.write_text(src_text, encoding="utf-8")
    print(f"\nTotal applied: {grand_total}")


if __name__ == "__main__":
    main()
