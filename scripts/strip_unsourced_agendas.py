"""Strip the unsourced 3-bullet placeholder agendas from candidates.js for
party blocks listed in fb_platform_scan/worklist.json that didn't yield a
real platform after the FB-discovery + scrape pass.

For each entry whose scrape_status is anything other than 'scraped':
  • Locate the muni's const block in candidates.js.
  • Locate the party block within it (e.g. `^  M: {`).
  • Replace the body of `agenda: [ ... ]` with `agenda: []` in-place.
  • Add a one-line comment recording when + why it was stripped, plus the
    discovered FB URL if any so a future re-scan can pick it up.

The renderer treats `agenda: []` the same as a missing agenda — splash
falls back to "Stefnuskrá ekki til staðar" + the email CTA, no source
link is shown.

Backup written to candidates.js.bak_strip_<timestamp> before any edit.

Usage:
    python scripts/strip_unsourced_agendas.py --dry-run
    python scripts/strip_unsourced_agendas.py
"""
from __future__ import annotations
import argparse, json, re, shutil
from datetime import datetime
from pathlib import Path

ROOT  = Path(__file__).parent.parent
SRC   = ROOT / "js" / "data" / "candidates.js"
WL    = ROOT / "fb_platform_scan" / "worklist.json"

def find_const_block_extent(src: str, var_name: str) -> tuple[int, int] | None:
    """Return (start, end) of `const VAR = { ... };` body."""
    m = re.search(r"^const\s+" + re.escape(var_name) + r"\s*=\s*\{", src, re.MULTILINE)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    while i < len(src):
        c = src[i]
        if c in ("'", '"'):
            quote = c; i += 1
            while i < len(src):
                if src[i] == "\\":
                    i += 2; continue
                if src[i] == quote:
                    i += 1; break
                i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return open_pos + 1, i
        i += 1
    return None

def find_party_block(src: str, var_name: str, party_code: str) -> tuple[int, int] | None:
    """Return (start, end) span of `  CODE: { ... },` within a const block."""
    span = find_const_block_extent(src, var_name)
    if not span:
        return None
    body_start, body_end = span
    # Find `^  CODE:\s*\{` within the body
    pat = re.compile(r"^  " + re.escape(party_code) + r"\s*:\s*\{", re.MULTILINE)
    pm = pat.search(src, body_start, body_end)
    if not pm:
        return None
    open_pos = pm.end() - 1
    depth = 0
    i = open_pos
    while i < body_end:
        c = src[i]
        if c in ("'", '"'):
            quote = c; i += 1
            while i < body_end:
                if src[i] == "\\":
                    i += 2; continue
                if src[i] == quote:
                    i += 1; break
                i += 1
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return pm.start(), i + 1
        i += 1
    return None

def find_agenda_body(party_src: str) -> tuple[int, int] | None:
    """Return (start, end) of the `agenda: [ ... ]` array including the brackets."""
    m = re.search(r"\bagenda:\s*\[", party_src)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    while i < len(party_src):
        c = party_src[i]
        if c in ("'", '"'):
            quote = c; i += 1
            while i < len(party_src):
                if party_src[i] == "\\":
                    i += 2; continue
                if party_src[i] == quote:
                    i += 1; break
                i += 1
            continue
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return open_pos, i + 1
        i += 1
    return None

# Build var-name -> muni-slug mapping from REAL_DATA
def load_muni_var_mapping(src: str) -> dict[str, str]:
    """Returns slug -> var (e.g. 'reykjavik' -> 'RVK')."""
    mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", src)
    out = {}
    if mm:
        for kv in re.finditer(r"(\w+):\s*([A-Z]+)", mm.group(1)):
            out[kv.group(1)] = kv.group(2)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = SRC.read_text(encoding="utf-8")
    wl = json.loads(WL.read_text(encoding="utf-8"))
    var_for = load_muni_var_mapping(src)

    # Targets = every entry whose scrape didn't yield a real platform
    targets = [e for e in wl["entries"] if e.get("scrape_status") != "scraped"]
    print(f"  Stripping {len(targets)} placeholder agendas")

    if not args.dry_run:
        bak = SRC.with_name("candidates.js.bak_strip_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        bak.write_text(src, encoding="utf-8")
        print(f"  Backup: {bak.name}")

    new_src = src
    stripped, skipped = 0, []
    today = datetime.now().strftime("%Y-%m-%d")

    # Process from end to start so positions remain stable
    edits = []
    for entry in targets:
        muni_slug  = entry["muni_slug"]
        party_code = entry["party_code"]
        var = var_for.get(muni_slug)
        if not var:
            skipped.append((entry["id"], "no var")); continue
        block = find_party_block(new_src, var, party_code)
        if not block:
            skipped.append((entry["id"], f"party {party_code} not found in {var}")); continue
        b_start, b_end = block
        party_src = new_src[b_start:b_end]
        agenda_span = find_agenda_body(party_src)
        if not agenda_span:
            skipped.append((entry["id"], "no agenda block")); continue
        a_start, a_end = agenda_span
        # New agenda body — empty array. Comment captures the why + FB URL.
        comment = f"    // [stripped {today}] no source verifiable; "
        if entry.get("fb_url"):
            comment += f"FB: {entry['fb_url']}"
        else:
            comment += "no FB page found in 2026-05-04 sweep"
        new_party_src = party_src[:a_start] + "[],\n" + comment + "\n   " + party_src[a_end+1:] if party_src[a_end:a_end+1] == "," else party_src[:a_start] + "[]" + party_src[a_end:]
        edits.append((b_start, b_end, new_party_src))
        stripped += 1

    # Apply edits from highest position downward
    edits.sort(key=lambda e: -e[0])
    for b_start, b_end, replacement in edits:
        new_src = new_src[:b_start] + replacement + new_src[b_end:]

    # Sanity check
    if new_src.count("{") != new_src.count("}"):
        print(f"  ABORT: brace imbalance after edits ({new_src.count('{')} vs {new_src.count('}')})")
        return 1
    if new_src.count("[") != new_src.count("]"):
        print(f"  ABORT: bracket imbalance after edits ({new_src.count('[')} vs {new_src.count(']')})")
        return 1

    print(f"  Stripped: {stripped}  Skipped: {len(skipped)}")
    for cid, why in skipped:
        print(f"    {cid}: {why}")

    if args.dry_run:
        print(f"  (dry-run — no file written)")
        return 0
    SRC.write_text(new_src, encoding="utf-8")
    print(f"  Wrote {SRC}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
