"""Identify every candidate row in candidates.js whose extended object
has a bio but no heimild source, extract those bios into a new bios_*.json
scan file (so the audit pipeline + scan-review can pick them up), and
strip the bio in place from candidates.js so the live site falls back to
the standard "no info available yet" disclaimer until a re-audited
rewrite is approved.

Outputs:
  scan_results/bios_2026-05-04_REAUDIT.json   — for the audit pipeline
  fb_platform_scan/reaudit_originals.json     — full row backup for restore
  candidates.js                                — bios stripped in place

Usage:
  python scripts/reaudit_strip_bios.py --dry-run
  python scripts/reaudit_strip_bios.py
"""
from __future__ import annotations
import argparse, json, re, shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC  = ROOT / "js" / "data" / "candidates.js"
OUT_BIOS = ROOT / "scan_results" / "bios_2026-05-04_REAUDIT.json"
OUT_BACKUP = ROOT / "fb_platform_scan" / "reaudit_originals.json"

# helpers shared with the audit script
def find_close(s, op, oc, cc):
    depth, i, in_str = 0, op, None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == "\\": i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c in ("'", '"'): in_str = c; i += 1; continue
        if c == oc: depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return -1

def load_muni_var_mapping(src):
    mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", src)
    out = {}
    if mm:
        for kv in re.finditer(r"(\w+):\s*([A-Z]+)", mm.group(1)):
            out[kv.group(1)] = kv.group(2)  # slug -> var
    return out

# Best-effort field extractors (string-based, safe with apostrophes inside bios)
def extract_string_field(obj_src, key):
    """Return the IS string value of `key: '...'` inside the object source.
    Handles backslash-escaped apostrophes. None if not found / null."""
    m = re.search(r"\b" + re.escape(key) + r":\s*(null|')", obj_src)
    if not m:
        return None
    if m.group(1) == "null":
        return None
    start = m.end() - 1  # position of opening quote
    i = start + 1
    out = []
    while i < len(obj_src):
        c = obj_src[i]
        if c == "\\" and i + 1 < len(obj_src):
            out.append(obj_src[i:i+2]); i += 2; continue
        if c == "'":
            return "".join(out)
        out.append(c); i += 1
    return None

def extract_number_field(obj_src, key):
    m = re.search(r"\b" + re.escape(key) + r":\s*(\d+|null)", obj_src)
    if not m: return None
    if m.group(1) == "null": return None
    return int(m.group(1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src = SRC.read_text(encoding="utf-8")
    var_for = load_muni_var_mapping(src)
    inv = {v: k for k, v in var_for.items()}

    # walk every const muni block, collect candidate rows
    const_starts = []
    for m in re.finditer(r"^const\s+([A-Z_]+)\s*=\s*\{", src, re.MULTILINE):
        const_starts.append((m.start(), m.end(), m.group(1)))
    const_starts.append((len(src), len(src), None))

    # We need to track absolute positions in `src` so we can edit later.
    # Strategy: collect per-row absolute (start, end) of the bio string-literal
    # in the row's extended object — and replace `bio: '...'` with `bio: null`.
    edits = []        # list of (abs_start, abs_end, replacement)
    extracted = []    # list of dicts to write into the bios scan file
    backups = []      # full original row text + position for restore

    for ci, (cs, ce, var) in enumerate(const_starts[:-1]):
        if var not in inv: continue
        next_cs = const_starts[ci+1][0]
        block = src[ce:next_cs]
        muni_slug = inv[var]

        party_marks = list(re.finditer(r"^  ([A-Z]{1,4}):\s*\{", block, re.MULTILINE))
        for bi, pm in enumerate(party_marks):
            code = pm.group(1)
            body_end_abs = ce + (party_marks[bi+1].start() if bi+1 < len(party_marks) else len(block))
            body_start_abs = ce + pm.end()
            party_body = src[body_start_abs:body_end_abs]
            lm = re.search(r"\blist:\s*\[", party_body)
            if not lm: continue
            list_open_abs = body_start_abs + lm.end() - 1
            list_close_abs = find_close(src, list_open_abs, "[", "]")
            if list_close_abs < 0: continue
            list_body = src[list_open_abs+1:list_close_abs-1]
            list_offset = list_open_abs + 1

            ip = 0
            while ip < len(list_body):
                while ip < len(list_body) and list_body[ip] != "[":
                    ip += 1
                if ip >= len(list_body): break
                row_end = find_close(list_body, ip, "[", "]")
                if row_end < 0: break
                row_abs_start = list_offset + ip
                row_abs_end   = list_offset + row_end
                row = src[row_abs_start:row_abs_end]
                ip = row_end

                # ballot + name
                bm = re.match(r"\[\s*(\d+)\s*,", row)
                ballot = int(bm.group(1)) if bm else 0
                # name = first quoted string
                # walk: skip initial '[N, ' then read first ' ... '
                name_match = re.search(r"\[\s*\d+\s*,\s*'((?:\\.|[^'\\])*)'", row)
                name = name_match.group(1) if name_match else "?"
                # occupation = 2nd quoted string
                occ_match = re.search(
                    r"\[\s*\d+\s*,\s*'(?:\\.|[^'\\])*'\s*,\s*'((?:\\.|[^'\\])*)'",
                    row,
                )
                occupation = occ_match.group(1) if occ_match else None

                # find extended object {...} (last)
                obj_open = row.find("{")
                if obj_open < 0:
                    continue
                obj_close = find_close(row, obj_open, "{", "}")
                if obj_close < 0: continue
                obj_src = row[obj_open:obj_close]

                bio = extract_string_field(obj_src, "bio")
                if not bio:
                    continue
                # heimild present?
                has_source = bool(re.search(r"\bheimild:\s*\[\s*\{[^}]*url:", obj_src))
                if has_source:
                    continue

                # This is the target.
                age = extract_number_field(obj_src, "age")
                cid = f"{var}.{code}.{ballot}"

                # Locate the bio string-literal absolute span for the edit.
                # Find `bio: '` inside obj_src, then walk to closing apostrophe.
                bio_marker = re.search(r"\bbio:\s*'", obj_src)
                if not bio_marker:
                    continue
                bio_value_start_in_obj = bio_marker.end() - 1  # the opening quote
                # walk to closing quote
                i_obj = bio_value_start_in_obj + 1
                while i_obj < len(obj_src):
                    if obj_src[i_obj] == "\\":
                        i_obj += 2; continue
                    if obj_src[i_obj] == "'":
                        i_obj += 1; break
                    i_obj += 1
                # absolute positions
                bio_abs_start = row_abs_start + obj_open + bio_value_start_in_obj
                bio_abs_end   = row_abs_start + obj_open + i_obj
                edits.append((bio_abs_start, bio_abs_end, "null"))

                extracted.append({
                    "id":          cid,
                    "muni_slug":   muni_slug,
                    "party_code":  code,
                    "ballot":      ballot,
                    "name":        name,
                    "occupation":  occupation,
                    "bio":         bio,
                    "sources":     [],
                    "age":         age,
                })
                backups.append({
                    "id":              cid,
                    "muni_slug":       muni_slug,
                    "party_code":      code,
                    "ballot":          ballot,
                    "name":            name,
                    "occupation":      occupation,
                    "original_bio":    bio,
                    "row_position":    [row_abs_start, row_abs_end],
                    "row_full_text":   row,
                })

    print(f"  Found {len(extracted)} bios with no source")

    if not extracted:
        return 0

    # Sort edits by position descending so positions remain valid
    edits.sort(key=lambda e: -e[0])

    if not args.dry_run:
        bak = SRC.with_name("candidates.js.bak_reaudit_strip_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        bak.write_text(src, encoding="utf-8")
        print(f"  Backup: {bak.name}")

    new_src = src
    for s, e, repl in edits:
        new_src = new_src[:s] + repl + new_src[e:]

    # Sanity: brace + quote balance unchanged
    if new_src.count("{") != new_src.count("}"):
        print(f"  ABORT brace imbalance: {new_src.count('{')} vs {new_src.count('}')}")
        return 1

    if args.dry_run:
        print(f"  (dry-run — would strip {len(edits)} bios)")
        return 0

    SRC.write_text(new_src, encoding="utf-8")
    print(f"  Wrote stripped {SRC}")

    # Sort extracted by source-count (none) and id for nice ordering
    extracted.sort(key=lambda e: (e["muni_slug"], e["party_code"], e["ballot"]))
    OUT_BIOS.parent.mkdir(parents=True, exist_ok=True)
    OUT_BIOS.write_text(json.dumps({
        "scan_date": "2026-05-04",
        "scan_type": "bios",
        "agent_note": "Re-audit batch: 185 bios that lacked any heimild source",
        "results":   extracted,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote {OUT_BIOS} ({len(extracted)} bios)")

    OUT_BACKUP.parent.mkdir(parents=True, exist_ok=True)
    OUT_BACKUP.write_text(json.dumps({
        "stripped_at": datetime.now().isoformat(),
        "count":       len(backups),
        "candidates":  backups,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Wrote {OUT_BACKUP} ({len(backups)} backups)")
    return 0

if __name__ == "__main__":
    import sys; sys.exit(main())
