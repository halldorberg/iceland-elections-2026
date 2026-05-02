"""
report_photo_no_bio.py
──────────────────────
Report candidates that have a photo but no bio (or only a minimal bio).

A "minimal bio" is one whose only informational content is name + occupation +
position on a list — i.e. text matching templates like:
  "X er <occupation> og er á N. sæti Y-listans í <muni> 2026."
  "X er <occupation>. Hann/Hún er á framboðslista Y í <muni> 2026."

Heuristic: a bio is minimal if (a) it is short (<= 220 chars), and (b) after
stripping the candidate's name, occupation, list-position phrasing, and
"sveitarstjórnarkosningum 2026"-type tokens, less than ~40 chars of substantive
text remains.

Usage:
    python scripts/report_photo_no_bio.py
    python scripts/report_photo_no_bio.py --max-len 250    # tweak threshold
    python scripts/report_photo_no_bio.py --include-leaders  # include ballot 1
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"

# Reuse labels from generate_manifest
sys.path.insert(0, str(Path(__file__).parent))
from generate_manifest import MUNI_LABELS, PARTY_LABELS  # noqa: E402


# ── String/bracket-balanced helpers ──────────────────────────────────────────

def _skip_string(src: str, i: int) -> int:
    """src[i] is the opening '. Return index just past the closing '."""
    quote = src[i]
    i += 1
    while i < len(src):
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == quote:
            return i + 1
        i += 1
    return i


def _find_matching(src: str, i: int) -> int:
    """src[i] is an opening bracket. Return index of matching close, +1."""
    open_ch = src[i]
    close_ch = {"{": "}", "[": "]", "(": ")"}[open_ch]
    depth = 0
    while i < len(src):
        c = src[i]
        if c in ("'", '"'):
            i = _skip_string(src, i)
            continue
        if c == "/" and i + 1 < len(src) and src[i + 1] == "/":
            # line comment
            nl = src.find("\n", i)
            i = nl + 1 if nl != -1 else len(src)
            continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return i


def _split_top_level(src: str, sep: str = ",") -> list[tuple[int, int]]:
    """Yield (start, end) ranges of top-level segments separated by `sep`.
    Skips brackets and strings."""
    out: list[tuple[int, int]] = []
    start = 0
    i = 0
    while i < len(src):
        c = src[i]
        if c in ("'", '"'):
            i = _skip_string(src, i)
            continue
        if c in "{[(":
            i = _find_matching(src, i)
            continue
        if c == sep:
            out.append((start, i))
            start = i + 1
        i += 1
    if start < len(src):
        out.append((start, len(src)))
    return out


# ── Main parser ──────────────────────────────────────────────────────────────

def parse_real_data_map(src: str) -> dict[str, str]:
    """Parse REAL_DATA = { slug: CONST, ... } → {const: slug}."""
    m = re.search(r"const REAL_DATA\s*=\s*\{([^}]*)\}", src)
    if not m:
        return {}
    inner = m.group(1)
    out: dict[str, str] = {}
    for seg_start, seg_end in _split_top_level(inner):
        seg = inner[seg_start:seg_end].strip()
        if not seg:
            continue
        kv = re.match(r"(\w+)\s*:\s*([A-Z][A-Z0-9_]*)", seg)
        if kv:
            out[kv.group(2)] = kv.group(1)
    return out


def find_const_blocks(src: str, names: set[str]) -> dict[str, tuple[int, int]]:
    """Return {const_name: (body_start, body_end)} where body is between {...}."""
    out: dict[str, tuple[int, int]] = {}
    for m in re.finditer(r"const\s+([A-Z][A-Z0-9_]*)\s*=\s*\{", src):
        name = m.group(1)
        if name not in names:
            continue
        brace_open = m.end() - 1
        body_close = _find_matching(src, brace_open)
        out[name] = (brace_open + 1, body_close - 1)
    return out


def parse_party_blocks(src: str, body_start: int, body_end: int) -> list[tuple[str, int, int]]:
    """Return [(party_code, body_start, body_end), ...] for each party in this muni body."""
    body = src[body_start:body_end]
    out: list[tuple[str, int, int]] = []
    # Walk top-level keys: PARTY_CODE: { ... }
    i = 0
    while i < len(body):
        c = body[i]
        if c in ("'", '"'):
            i = _skip_string(body, i)
            continue
        if c in "{[(":
            i = _find_matching(body, i)
            continue
        # try to match key: {
        m = re.match(r"\s*([A-Z][A-Z0-9]{0,3})\s*:\s*\{", body[i:])
        if m:
            party = m.group(1)
            brace_pos = i + m.end() - 1
            close = _find_matching(body, brace_pos)
            out.append((party, body_start + brace_pos + 1, body_start + close - 1))
            i = close
            continue
        i += 1
    return out


def find_list_array(src: str, body_start: int, body_end: int) -> tuple[int, int] | None:
    """Find `list: [ ... ]` inside a party body. Returns (start, end) of array contents."""
    body = src[body_start:body_end]
    # Find `list:` at top level
    i = 0
    while i < len(body):
        c = body[i]
        if c in ("'", '"'):
            i = _skip_string(body, i)
            continue
        if c in "{[(":
            i = _find_matching(body, i)
            continue
        m = re.match(r"list\s*:\s*\[", body[i:])
        if m:
            bracket_pos = i + m.end() - 1
            close = _find_matching(body, bracket_pos)
            return (body_start + bracket_pos + 1, body_start + close - 1)
        i += 1
    return None


def parse_candidate_row(src: str, row_start: int, row_end: int) -> dict | None:
    """Parse one [ballot, name, occupation, image?, details?] row."""
    inner = src[row_start:row_end]
    parts = _split_top_level(inner)
    if len(parts) < 3:
        return None

    def get(idx: int) -> str:
        a, b = parts[idx]
        return inner[a:b].strip()

    ballot_s = get(0)
    name_s = get(1)
    occ_s = get(2)
    image_s = get(3) if len(parts) >= 4 else "null"
    details_s = get(4) if len(parts) >= 5 else ""

    try:
        ballot = int(ballot_s)
    except ValueError:
        return None

    name = _strip_quotes(name_s)
    occupation = _strip_quotes(occ_s)

    has_photo = bool(re.search(r"^['\"]images/", image_s)) or "images/candidates/" in image_s

    # Extract bio from details_s (which is `{ ... }` or empty)
    bio = None
    if details_s.startswith("{"):
        bm = re.search(
            r"bio\s*:\s*'((?:[^'\\]|\\.)*)'",
            details_s,
        )
        if bm:
            bio = bm.group(1).replace("\\'", "'").replace('\\"', '"')
        else:
            # Could be `bio: null` or absent
            bio = None

    return {
        "ballot": ballot,
        "name": name,
        "occupation": occupation,
        "has_photo": has_photo,
        "bio": bio,
    }


def _strip_quotes(s: str) -> str:
    s = s.strip()
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1].replace("\\'", "'")
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1].replace('\\"', '"')
    return s


def split_list_rows(src: str, list_start: int, list_end: int) -> list[tuple[int, int]]:
    """Split list array contents into top-level [...] rows."""
    body = src[list_start:list_end]
    out: list[tuple[int, int]] = []
    i = 0
    while i < len(body):
        c = body[i]
        if c == "[":
            close = _find_matching(body, i)
            out.append((list_start + i + 1, list_start + close - 1))
            i = close
            continue
        if c in ("'", '"'):
            i = _skip_string(body, i)
            continue
        if c == "{":
            i = _find_matching(body, i)
            continue
        i += 1
    return out


# ── Bio classification ──────────────────────────────────────────────────────

# Tokens that indicate boilerplate "name + occupation + list position" content.
BOILERPLATE_PATTERNS = [
    r"\b(Hann|Hún|Þau)\b",
    r"\b(er|var|skipar)\b",
    r"\b(á|í)\s+\d+\.\s*sæti\b",
    r"\d+\.\s*sæti",
    r"\b[A-ZÁÉÍÓÚÝÞÆÖa-záéíóúýþæö]-list[a-záéíóúýþæö]+",
    r"framboðslist[a-záéíóúýþæö]+",
    r"sveitarstjórnarkosning[a-záéíóúýþæö]+",
    r"borgarstjórnarkosning[a-záéíóúýþæö]+",
    r"bæjarstjórnarkosning[a-záéíóúýþæö]+",
    r"\bkosningum?\b",
    r"\bkosningar(?:nar|na)?\b",
    r"\b2026\b",
    r"\bog\b",
    r"\bað mennt\b",
    r"\b(fyrir|frambjóðandi)\b",
    r"\bleiðir\s+listann\b",
    r"\boddvit[a-záéíóúýþæö]+\b",
    r"\([^)]*\)",  # parenthetical asides like "(Framsóknarflokks)"
]


def is_minimal_bio(name: str, occupation: str, bio: str, max_len: int = 220) -> bool:
    """Return True if the bio is essentially template-only."""
    if bio is None:
        return True
    bio = bio.strip()
    if not bio:
        return True
    # Long bios: not minimal
    if len(bio) > max_len:
        return False

    # Strip name (first names, last name) and occupation tokens, then strip
    # boilerplate. If less than 30 substantive chars remain, it's minimal.
    txt = bio

    # Strip the candidate's name (any contiguous subsequence)
    for token in name.split():
        if len(token) >= 3:
            txt = re.sub(re.escape(token), "", txt, flags=re.IGNORECASE)

    # Strip occupation tokens
    for token in re.split(r"[\s,/]+", occupation):
        if len(token) >= 4:
            txt = re.sub(re.escape(token), "", txt, flags=re.IGNORECASE)

    # Strip municipality names
    for muni_label in MUNI_LABELS.values():
        for token in muni_label.split():
            if len(token) >= 4:
                txt = re.sub(re.escape(token), "", txt, flags=re.IGNORECASE)

    # Strip party labels
    for plabel in PARTY_LABELS.values():
        for token in plabel.split():
            if len(token) >= 4:
                txt = re.sub(re.escape(token), "", txt, flags=re.IGNORECASE)

    for pat in BOILERPLATE_PATTERNS:
        txt = re.sub(pat, "", txt, flags=re.IGNORECASE)

    # Collapse non-letter chars
    residual = re.sub(r"[^A-Za-zÁÉÍÓÚÝÞÆÖáéíóúýþæöÐð]+", "", txt)
    return len(residual) < 30


# ── Driver ──────────────────────────────────────────────────────────────────

def run(max_len: int, include_leaders: bool) -> int:
    src = CANDIDATES_JS.read_text(encoding="utf-8")
    const_to_slug = parse_real_data_map(src)
    if not const_to_slug:
        print("ERROR: Could not parse REAL_DATA map", file=sys.stderr)
        return 1

    const_blocks = find_const_blocks(src, set(const_to_slug.keys()))

    # Order municipalities by their appearance in the file (preserves layout).
    ordered = sorted(const_blocks.items(), key=lambda kv: kv[1][0])

    # Group findings by muni → party → list of (ballot, name, occupation, kind)
    report: dict[str, dict[str, list[dict]]] = {}
    total_rows = 0
    total_with_photo = 0
    total_no_bio = 0
    total_minimal = 0

    for const, (bs, be) in ordered:
        muni_slug = const_to_slug[const]
        for party_code, pbs, pbe in parse_party_blocks(src, bs, be):
            larr = find_list_array(src, pbs, pbe)
            if not larr:
                continue
            ls, le = larr
            for rs, re_ in split_list_rows(src, ls, le):
                row = parse_candidate_row(src, rs, re_)
                if not row:
                    continue
                total_rows += 1
                if not row["has_photo"]:
                    continue
                total_with_photo += 1
                if not include_leaders and row["ballot"] == 1:
                    pass  # still consider — leaders can be missing too
                bio = row["bio"]
                if bio is None or not bio.strip():
                    kind = "no_bio"
                    total_no_bio += 1
                elif is_minimal_bio(row["name"], row["occupation"], bio, max_len):
                    kind = "minimal"
                    total_minimal += 1
                else:
                    continue
                report.setdefault(muni_slug, {}).setdefault(party_code, []).append({
                    "ballot": row["ballot"],
                    "name": row["name"],
                    "occupation": row["occupation"],
                    "kind": kind,
                    "bio": bio,
                })

    # Render report
    print(f"# Candidates with photo but missing or minimal bio\n")
    print(f"_Generated from `js/data/candidates.js` (max bio length for minimal: {max_len} chars)._\n")
    print(f"- Total candidates: **{total_rows}**")
    print(f"- With photo: **{total_with_photo}**")
    print(f"- Of those, missing bio: **{total_no_bio}**")
    print(f"- Of those, minimal bio: **{total_minimal}**")
    print(f"- **Combined needing bio work: {total_no_bio + total_minimal}**\n")

    # Order munis as in file
    for const, _ in ordered:
        muni = const_to_slug[const]
        if muni not in report:
            continue
        muni_label = MUNI_LABELS.get(muni, muni)
        muni_count = sum(len(v) for v in report[muni].values())
        print(f"## {muni_label} — {muni_count} entries\n")
        for party_code, items in sorted(report[muni].items()):
            party_label = PARTY_LABELS.get(party_code, party_code)
            no_bio = [i for i in items if i["kind"] == "no_bio"]
            minimal = [i for i in items if i["kind"] == "minimal"]
            print(f"### {party_label} ({party_code}) — {len(no_bio)} no bio, {len(minimal)} minimal\n")
            for item in sorted(items, key=lambda x: x["ballot"]):
                marker = "🚫" if item["kind"] == "no_bio" else "✏️"
                bio_preview = ""
                if item["bio"]:
                    bp = item["bio"][:120].replace("\n", " ")
                    if len(item["bio"]) > 120:
                        bp += "…"
                    bio_preview = f" — _{bp}_"
                print(f"- {marker} **#{item['ballot']}** {item['name']} ({item['occupation']}){bio_preview}")
            print()
    return 0


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--max-len", type=int, default=220, help="Bio length threshold for 'minimal' classification")
    ap.add_argument("--include-leaders", action="store_true", help="(no-op now; leaders are included by default)")
    ap.add_argument("--out", type=Path, default=None, help="Optional path to write the markdown report to")
    args = ap.parse_args()

    if args.out:
        # Capture stdout
        import io
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        rc = run(args.max_len, args.include_leaders)
        sys.stdout = old
        args.out.write_text(buf.getvalue(), encoding="utf-8")
        print(f"[OK] Wrote {args.out}")
        return rc
    return run(args.max_len, args.include_leaders)


if __name__ == "__main__":
    sys.exit(main())
