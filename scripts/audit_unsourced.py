"""Comprehensive audit: flag every unsourced content surface in candidates.js.

For every party block: agenda items present but no platformUrl.
For every candidate row: bio present but no heimild url.
Soft flag: interests array present but no bio + no heimild.
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent
SRC  = ROOT / "js" / "data" / "candidates.js"

src = SRC.read_text(encoding="utf-8")

# ── helpers ───────────────────────────────────────────────────────────────────
def find_close(s, op, oc, cc):
    depth, i, in_str = 0, op, None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == "\\": i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c == "/" and i + 1 < len(s) and s[i+1] == "/":
            nl = s.find("\n", i + 2)
            i = (nl + 1) if nl >= 0 else len(s); continue
        if c == "/" and i + 1 < len(s) and s[i+1] == "*":
            end = s.find("*/", i + 2)
            i = (end + 2) if end >= 0 else len(s); continue
        if c in ("'", '"'): in_str = c; i += 1; continue
        if c == oc: depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return -1

def extract_string_field(obj_src, key):
    m = re.search(r"\b" + re.escape(key) + r":\s*(null|')", obj_src)
    if not m or m.group(1) == "null":
        return None
    start = m.end() - 1
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

def has_heimild_with_url(obj_src):
    """heimild present AND contains at least one {url:'…'} entry."""
    m = re.search(r"\bheimild:\s*(null|\[)", obj_src)
    if not m or m.group(1) == "null":
        return False
    open_pos = m.end() - 1
    close = find_close(obj_src, open_pos, "[", "]")
    if close < 0: return False
    body = obj_src[open_pos+1:close-1]
    return bool(re.search(r"url:\s*'[^']+'", body))

def has_interests(obj_src):
    m = re.search(r"\binterests:\s*(null|\[)", obj_src)
    if not m or m.group(1) == "null":
        return False
    open_pos = m.end() - 1
    close = find_close(obj_src, open_pos, "[", "]")
    if close < 0: return False
    body = obj_src[open_pos+1:close-1].strip()
    # any non-empty string in array
    return bool(re.search(r"'[^']+'", body))

def has_news(obj_src):
    m = re.search(r"\bnews:\s*(null|\[)", obj_src)
    if not m or m.group(1) == "null":
        return False
    open_pos = m.end() - 1
    close = find_close(obj_src, open_pos, "[", "]")
    if close < 0: return False
    body = obj_src[open_pos+1:close-1].strip()
    return bool(re.search(r"url:\s*'[^']+'", body))

# ── load REAL_DATA mapping ────────────────────────────────────────────────────
mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", src)
slug_for_var = {}
if mm:
    for kv in re.finditer(r"(\w+):\s*([A-Z_]+)", mm.group(1)):
        slug_for_var[kv.group(2)] = kv.group(1)  # var -> slug

# ── walk every const muni ─────────────────────────────────────────────────────
const_starts = []
for m in re.finditer(r"^const\s+([A-Z_]+)\s*=\s*\{", src, re.MULTILINE):
    const_starts.append((m.start(), m.end(), m.group(1)))
const_starts.append((len(src), len(src), None))

unsourced_bios   = []   # bio present, no heimild
empty_heimild    = []   # bio + heimild but heimild has no url
unsourced_agendas= []   # agenda items present, no platformUrl
empty_agendas    = []   # agenda: [] but party block exists (info-only, not flagged)
suspect_interests= []   # interests present but no heimild AND no bio

for ci, (cs, ce, var) in enumerate(const_starts[:-1]):
    if var not in slug_for_var: continue
    next_cs = const_starts[ci+1][0]
    block = src[ce:next_cs]
    muni_slug = slug_for_var[var]

    party_marks = list(re.finditer(r"^  ([A-Z]{1,4}):\s*\{", block, re.MULTILINE))
    for bi, pm in enumerate(party_marks):
        code = pm.group(1)
        body_end = (party_marks[bi+1].start() if bi+1 < len(party_marks) else len(block))
        party_body = block[pm.end():body_end]

        # ── agenda check ─────────────────────────────────────────────────
        agenda_m = re.search(r"\bagenda:\s*\[", party_body)
        if agenda_m:
            ap = agenda_m.end() - 1
            ac = find_close(party_body, ap, "[", "]")
            if ac > 0:
                agenda_body = party_body[ap+1:ac-1]
                has_items = bool(re.search(r"icon:\s*'[^']+'", agenda_body))
                if has_items:
                    has_platform = bool(re.search(r"\bplatformUrl:\s*'[^']+'", party_body))
                    if not has_platform:
                        unsourced_agendas.append({
                            "muni": muni_slug, "party": code,
                        })

        # ── candidate list ───────────────────────────────────────────────
        lm = re.search(r"\blist:\s*\[", party_body)
        if not lm: continue
        list_open = lm.end() - 1
        list_close = find_close(party_body, list_open, "[", "]")
        if list_close < 0: continue
        list_body = party_body[list_open+1:list_close-1]

        ip = 0
        while ip < len(list_body):
            while ip < len(list_body) and list_body[ip] != "[":
                ip += 1
            if ip >= len(list_body): break
            row_end = find_close(list_body, ip, "[", "]")
            if row_end < 0: break
            row = list_body[ip:row_end]
            ip = row_end

            bm = re.match(r"\[\s*(\d+)\s*,", row)
            ballot = int(bm.group(1)) if bm else 0
            name_m = re.search(r"\[\s*\d+\s*,\s*'((?:\\.|[^'\\])*)'", row)
            name = name_m.group(1).replace("\\'", "'") if name_m else "?"

            obj_open = row.find("{")
            if obj_open < 0:
                continue
            obj_close = find_close(row, obj_open, "{", "}")
            if obj_close < 0: continue
            obj_src = row[obj_open:obj_close]

            bio = extract_string_field(obj_src, "bio")
            has_h = has_heimild_with_url(obj_src)

            if bio and not has_h:
                unsourced_bios.append({
                    "muni": muni_slug, "party": code, "ballot": ballot, "name": name,
                    "bio_excerpt": bio[:140] + ("…" if len(bio) > 140 else ""),
                })
            elif bio and has_h:
                # could check if heimild items all 404 — out of scope here
                pass

            # interests with no heimild and no bio = soft flag (claims about person)
            if not bio and has_interests(obj_src) and not has_h:
                suspect_interests.append({
                    "muni": muni_slug, "party": code, "ballot": ballot, "name": name,
                })

# ── output ────────────────────────────────────────────────────────────────────
print("=" * 70)
print(f"UNSOURCED BIOS  ({len(unsourced_bios)} candidates)")
print("=" * 70)
by_muni = defaultdict(list)
for r in unsourced_bios:
    by_muni[r["muni"]].append(r)
for muni in sorted(by_muni):
    print(f"\n  {muni}  ({len(by_muni[muni])})")
    for r in sorted(by_muni[muni], key=lambda x: (x["party"], x["ballot"])):
        print(f"    {r['party']}.{r['ballot']:>2}  {r['name']}")
        print(f"             › {r['bio_excerpt']}")

print()
print("=" * 70)
print(f"UNSOURCED AGENDAS  ({len(unsourced_agendas)} parties)")
print("=" * 70)
by_muni = defaultdict(list)
for r in unsourced_agendas:
    by_muni[r["muni"]].append(r["party"])
for muni in sorted(by_muni):
    parties = ", ".join(sorted(by_muni[muni]))
    print(f"  {muni:<22}  {parties}")

print()
print("=" * 70)
print(f"INTERESTS WITHOUT BIO/SOURCE  ({len(suspect_interests)} candidates)")
print("(soft flag — interests aren't bio claims, but they assert the person)")
print("=" * 70)
by_muni = defaultdict(list)
for r in suspect_interests:
    by_muni[r["muni"]].append(r)
for muni in sorted(by_muni):
    print(f"\n  {muni}  ({len(by_muni[muni])})")
    for r in sorted(by_muni[muni], key=lambda x: (x["party"], x["ballot"])):
        print(f"    {r['party']}.{r['ballot']:>2}  {r['name']}")

# also dump JSON for downstream tooling
out = {
    "unsourced_bios":     unsourced_bios,
    "unsourced_agendas":  unsourced_agendas,
    "suspect_interests":  suspect_interests,
}
(ROOT / "audit_unsourced_report.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print()
print(f"  JSON report → audit_unsourced_report.json")
print()
print(f"SUMMARY: bios={len(unsourced_bios)} agendas={len(unsourced_agendas)} interests={len(suspect_interests)}")
