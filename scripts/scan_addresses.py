"""Scan every bio (in scan_results/bios_*.json, scan_results/audit_results*.json,
and the live js/data/candidates.js) for what looks like a home address —
i.e. an Icelandic street name + house number.

Reports each match with file, candidate id, name, and the matched span so we
can review before stripping.
"""
from __future__ import annotations
import json, re, sys, io, glob
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent

# Common Icelandic street-name endings (declined and undeclined). Match a
# capitalized word ending in one of these, followed by a small house number
# (1-3 digits, optionally with a letter suffix like 14a). Requires whitespace
# between the word and the number.
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

# A street name = capitalized prefix + one of the endings, then 1-3 digits.
# Numbers > 999 are likely years, exclude those.
ADDRESS_RE = re.compile(
    r"\b([A-ZÁÉÍÓÚÝÞÆÖ][a-záéíóúýþæöðA-ZÁÉÍÓÚÝÞÆÖ]{2,})(?:" + ENDINGS_RE + r")\s+(\d{1,3}[a-zA-Z]?)\b"
)

# false-positive keywords that often appear with numbers but aren't addresses
SKIP_PREFIXES = {
    # words that end with a streetlike suffix but aren't streets
    "Hagsmunafélag", "Atvinnuhús",
}

def extract_bios_from_file(path: Path):
    """Yield (id, name, bio_text) tuples from a JSON scan file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  parse-err {path.name}: {e}")
        return
    # bios_*.json shape: {results: [{id, name, bio, ...}]}
    if isinstance(data, dict) and "results" in data:
        for r in data["results"]:
            if not isinstance(r, dict): continue
            yield (r.get("id",""), r.get("name",""), r.get("bio") or r.get("rewrite") or "")
    # audit_results.json shape: {SFJ.D.1: {bio: ..., name: ...}}
    elif isinstance(data, dict):
        for k, v in data.items():
            if not isinstance(v, dict): continue
            yield (k, v.get("name", ""), v.get("bio") or v.get("rewrite") or "")
    # legacy list-shaped audit files
    elif isinstance(data, list):
        for r in data:
            if not isinstance(r, dict): continue
            yield (r.get("id",""), r.get("name",""), r.get("bio") or r.get("rewrite") or "")

def find_addresses_in_bio(bio: str):
    """Return list of (matched_substring, span_start, span_end)."""
    out = []
    for m in ADDRESS_RE.finditer(bio):
        prefix = m.group(1)
        if any(prefix.startswith(skip) for skip in SKIP_PREFIXES):
            continue
        out.append((m.group(0), m.start(), m.end()))
    return out

# ── walk scan files ──────────────────────────────────────────────────────────
hits = []
files = (
    sorted(ROOT.glob("scan_results/bios_*.json"))
    + sorted(ROOT.glob("scan_results/audit_results*.json"))
)
files = [f for f in files if not f.name.endswith(".bak_pre_apply")]

for path in files:
    for cid, name, bio in extract_bios_from_file(path):
        if not bio:
            continue
        addrs = find_addresses_in_bio(bio)
        for addr_text, _, _ in addrs:
            hits.append({
                "file": str(path.relative_to(ROOT)),
                "id": cid, "name": name,
                "matched": addr_text,
                "context": bio[max(0,bio.find(addr_text)-60):bio.find(addr_text)+len(addr_text)+60],
            })

# ── walk live candidates.js ──────────────────────────────────────────────────
src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")
# Match bio: '...' literal and scan within
for bm in re.finditer(r"bio:\s*'((?:[^'\\]|\\.)*)'", src):
    bio = bm.group(1).replace("\\'", "'")
    # Identify candidate name from preceding row
    row_start = src.rfind("[", 0, bm.start())
    if row_start < 0:
        name = "?"
    else:
        nm = re.match(r"\[\s*\d+\s*,\s*'((?:[^'\\]|\\.)*)'", src[row_start:row_start+200])
        name = nm.group(1).replace("\\'", "'") if nm else "?"
    addrs = find_addresses_in_bio(bio)
    for addr_text, _, _ in addrs:
        hits.append({
            "file": "js/data/candidates.js",
            "id": "(live)", "name": name,
            "matched": addr_text,
            "context": bio[max(0,bio.find(addr_text)-60):bio.find(addr_text)+len(addr_text)+60],
        })

# ── report ───────────────────────────────────────────────────────────────────
print(f"Found {len(hits)} possible home-address mentions:\n")
for h in hits:
    print(f"  [{h['file']}]  {h['id']}  {h['name']}")
    print(f"     match: {h['matched']!r}")
    print(f"     ...{h['context']!r}...")
    print()
