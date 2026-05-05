"""Strip street-address mentions (street name + house number) from every bio
across scan_results/bios_*.json, scan_results/audit_results*.json, and the
live js/data/candidates.js. Town/region context is preserved — only the
street + number is removed (along with the preceding preposition, e.g.
"búsettur á Dalatúni 14 í Skagafirði" → "búsettur í Skagafirði").

False-positive guard: matches followed by a "." and a month name are
treated as date ordinals, not addresses, and skipped.

Usage:
  python scripts/strip_addresses.py --dry-run
  python scripts/strip_addresses.py
"""
from __future__ import annotations
import argparse, json, re, sys, io, shutil
from datetime import datetime
from pathlib import Path
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent

STREET_ENDINGS = (
    "tún", "túni",
    "gata", "götu",
    "braut", "brautin",
    "stígur", "stígi", "stíg",
    "vegur", "vegi", "veg",
    "garður", "garði",
    "holt", "holti",
    "ás", "ási",
    "tröð",
    "heiði",
    "hraun", "hrauni",
    "lundur", "lundi",
    "bakki", "bakka",
    "mörk",
    "fold",
    "tangi", "tanga",
    "slóð",
    "hús", "húsi",
    "hella", "hellu",
    "nes", "nesi",
    "kringla", "kringlu",
    "smári", "smára",
)
ENDINGS_RE = "|".join(sorted(set(STREET_ENDINGS), key=len, reverse=True))

# Months for false-positive (ordinal-date) detection
MONTHS = (
    "janúar", "febrúar", "mars", "apríl", "maí", "júní",
    "júlí", "ágúst", "september", "október", "nóvember", "desember",
)
MONTH_RE = "|".join(MONTHS)

# Match: optional preposition + street word + number, NOT followed by
# `. <month>`. Group 1 = preposition (may be empty). Group 2 = street word.
# Group 3 = number.
ADDRESS_PATTERN = re.compile(
    r"(?P<prep>\s*(?:á|við|að|í)\s+)?"
    r"(?P<street>[A-ZÁÉÍÓÚÝÞÆÖ][a-záéíóúýþæöðA-ZÁÉÍÓÚÝÞÆÖ]+(?:" + ENDINGS_RE + r"))"
    r"\s+(?P<num>\d{1,3}[a-zA-Z]?)"
    r"(?!\d)"                                     # no further digit (year guard)
    r"(?![–—\-]\s*\d)"                  # not followed by –/- + digit (date range)
    r"(?!\.\s*(?:" + MONTH_RE + r"))",            # not followed by .<month>
)

# Place / town names whose declined form ends in a street-ish suffix.
# These should NEVER be treated as street addresses.
TOWN_STEMS = {
    "Akranes", "Akranesi", "Akraness",
    "Borgarnes", "Borgarnesi",
    "Álftanes", "Álftanesi",
    "Kjalarnes", "Kjalarnesi",
    "Reykjanes", "Reykjanesi", "Reykjanesbær",
    "Seltjarnarnes", "Seltjarnarnesi",
    "Vatnsnes", "Vatnsnesi",
}

SKIP_STREET_PREFIXES = ("Hagsmuna", "Atvinnu")  # words like Hagsmunafélag, Atvinnuhúsnæði

def strip_addresses(text: str) -> tuple[str, int]:
    """Return (cleaned_text, count_stripped)."""
    if not text:
        return text, 0
    count = 0
    def _replace(m):
        nonlocal count
        street = m.group("street")
        if any(street.startswith(skip) for skip in SKIP_STREET_PREFIXES):
            return m.group(0)
        if street in TOWN_STEMS:
            return m.group(0)
        count += 1
        return ""
    out = ADDRESS_PATTERN.sub(_replace, text)
    # Collapse double-spaces, ", ," double-commas, " ." stranded periods
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r"  +", " ", out)
    out = re.sub(r"\s+\.", ".", out)
    out = re.sub(r"\.\s*\.", ".", out)
    # cleanup orphan trailing prepositions left by sentence-fragment removal
    out = re.sub(r"\s+(?:á|við|að|í|hjá)\s*\.", ".", out)
    out = re.sub(r"\s+(?:á|við|að|í|hjá)\s*,", ",", out)
    # cleanup stranded " og " before a comma (left over when an address was
    # the second item in a list like "Álftarima og Vallholti 27,")
    out = re.sub(r"\s+og\s*,", ",", out)
    out = re.sub(r"\s+og\s*\.", ".", out)
    out = re.sub(r"  +", " ", out)
    return out.strip(), count

# ── Walk JSON files ──────────────────────────────────────────────────────────
def walk_json_files(dry_run: bool) -> int:
    total = 0
    files = (
        sorted(ROOT.glob("scan_results/bios_*.json"))
        + sorted(ROOT.glob("scan_results/audit_results*.json"))
    )
    files = [f for f in files if not f.name.endswith(".bak_pre_apply")]
    for path in files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  parse-err {path.name}: {e}")
            continue
        before = json.dumps(data, ensure_ascii=False)
        # mutate
        def _walk(obj):
            nonlocal total
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str) and k in ("bio", "rewrite", "claim", "text"):
                        new, n = strip_addresses(v)
                        if n > 0:
                            obj[k] = new
                            total += n
                    else:
                        _walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    _walk(item)
        _walk(data)
        after = json.dumps(data, ensure_ascii=False)
        if before != after:
            print(f"  ✓ {path.relative_to(ROOT)}")
            if not dry_run:
                bak = path.with_suffix(path.suffix + ".bak_strip_addr")
                if not bak.exists():
                    bak.write_text(before, encoding="utf-8")
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return total

# ── Walk candidates.js ───────────────────────────────────────────────────────
def walk_candidates_js(dry_run: bool) -> int:
    src_path = ROOT / "js" / "data" / "candidates.js"
    src = src_path.read_text(encoding="utf-8")
    new_src = src
    total = 0
    # iterate bio: '...' literals — work backwards to keep positions stable
    matches = list(re.finditer(r"bio:\s*'((?:[^'\\]|\\.)*)'", src))
    for m in reversed(matches):
        raw = m.group(1)
        bio = raw.replace("\\'", "'")
        cleaned, n = strip_addresses(bio)
        if n == 0:
            continue
        # re-escape for JS single-quoted string
        cleaned_js = cleaned.replace("\\", "\\\\").replace("'", "\\'")
        before = m.group(0)
        after = f"bio: '{cleaned_js}'"
        new_src = new_src[:m.start()] + after + new_src[m.end():]
        total += n
    if new_src != src:
        print(f"  ✓ js/data/candidates.js (stripped {total} address{'es' if total != 1 else ''})")
        if not dry_run:
            bak = src_path.with_name(f"candidates.js.bak_strip_addr_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            bak.write_text(src, encoding="utf-8")
            # bracket sanity
            if new_src.count("{") != new_src.count("}"):
                print(f"  ABORT brace imbalance"); return 0
            if new_src.count("[") != new_src.count("]"):
                print(f"  ABORT bracket imbalance"); return 0
            src_path.write_text(new_src, encoding="utf-8")
    return total

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Scanning JSON scan files…")
    json_count = walk_json_files(args.dry_run)
    print(f"\nScanning live candidates.js…")
    js_count = walk_candidates_js(args.dry_run)

    suffix = " (dry-run, nothing written)" if args.dry_run else ""
    print(f"\nStripped {json_count} addresses across scan files + {js_count} in candidates.js{suffix}")
