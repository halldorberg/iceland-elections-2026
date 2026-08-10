"""End-to-end gap analysis of the published site.

Inventories every content surface and reports counts/ratios so we can rank
remaining gaps by impact."""
from __future__ import annotations
import re, sys, io, json
from collections import defaultdict, Counter
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent
SRC = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")

# helpers shared with audit_unsourced
def find_close(s, op, oc, cc):
    depth, i, in_str = 0, op, None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == "\\": i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c == "/" and i+1 < len(s) and s[i+1] == "/":
            nl = s.find("\n", i+2); i = (nl+1) if nl >= 0 else len(s); continue
        if c == "/" and i+1 < len(s) and s[i+1] == "*":
            end = s.find("*/", i+2); i = (end+2) if end >= 0 else len(s); continue
        if c in ("'", '"'): in_str = c; i += 1; continue
        if c == oc: depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0: return i + 1
        i += 1
    return -1

def extract_string_field(obj_src, key):
    m = re.search(r"\b"+re.escape(key)+r":\s*(null|')", obj_src)
    if not m or m.group(1) == "null": return None
    start = m.end()-1
    i = start+1; out = []
    while i < len(obj_src):
        c = obj_src[i]
        if c == "\\" and i+1 < len(obj_src):
            out.append(obj_src[i:i+2]); i += 2; continue
        if c == "'": return "".join(out)
        out.append(c); i += 1
    return None

def has_array_field(obj_src, key, content_re=r"."):
    m = re.search(r"\b"+re.escape(key)+r":\s*(null|\[)", obj_src)
    if not m or m.group(1) == "null": return False
    op = m.end()-1
    cl = find_close(obj_src, op, "[", "]")
    if cl < 0: return False
    return bool(re.search(content_re, obj_src[op+1:cl-1]))

def heimild_url_count(obj_src):
    m = re.search(r"\bheimild:\s*(null|\[)", obj_src)
    if not m or m.group(1) == "null": return 0
    op = m.end()-1
    cl = find_close(obj_src, op, "[", "]")
    if cl < 0: return 0
    return len(re.findall(r"url:\s*'[^']+'", obj_src[op+1:cl-1]))

# ── load REAL_DATA mapping ───────────────────────────────────────────────────
mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", SRC)
slug_for_var = {}
if mm:
    for kv in re.finditer(r"(\w+):\s*([A-Z_]+)", mm.group(1)):
        slug_for_var[kv.group(2)] = kv.group(1)

# ── walk every candidate row ─────────────────────────────────────────────────
const_starts = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"^const\s+([A-Z_]+)\s*=\s*\{", SRC, re.MULTILINE)]
const_starts.append((len(SRC), len(SRC), None))

per_muni = defaultdict(lambda: {"parties": 0, "candidates": 0, "with_bio": 0, "with_heimild": 0, "with_photo": 0, "with_news": 0, "with_social": 0, "agendas_full": 0, "agendas_empty": 0})
totals = Counter()

for ci, (cs, ce, var) in enumerate(const_starts[:-1]):
    if var not in slug_for_var: continue
    next_cs = const_starts[ci+1][0]
    block = SRC[ce:next_cs]
    muni_slug = slug_for_var[var]
    party_marks = list(re.finditer(r"^  ([A-Z]{1,4}):\s*\{", block, re.MULTILINE))

    for bi, pm in enumerate(party_marks):
        per_muni[muni_slug]["parties"] += 1
        totals["parties"] += 1
        body_end = (party_marks[bi+1].start() if bi+1 < len(party_marks) else len(block))
        body_start = pm.end()
        party_body = block[body_start:body_end]

        # agenda has items?
        agenda_m = re.search(r"\bagenda:\s*\[", party_body)
        if agenda_m:
            ap = agenda_m.end()-1
            ac = find_close(party_body, ap, "[", "]")
            if ac > 0:
                if re.search(r"icon:\s*'[^']+'", party_body[ap+1:ac-1]):
                    per_muni[muni_slug]["agendas_full"] += 1
                    totals["agendas_full"] += 1
                else:
                    per_muni[muni_slug]["agendas_empty"] += 1
                    totals["agendas_empty"] += 1
        # platformUrl?
        if re.search(r"\bplatformUrl:\s*'[^']+'", party_body):
            totals["agendas_with_platform"] += 1

        # candidate list
        lm = re.search(r"\blist:\s*\[", party_body)
        if not lm: continue
        list_open = lm.end()-1
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

            per_muni[muni_slug]["candidates"] += 1
            totals["candidates"] += 1

            # Photo: 4th positional arg in row
            commas = []
            depth_in_str = None
            depth = 0
            for j, c in enumerate(row):
                if depth_in_str:
                    if c == depth_in_str: depth_in_str = None
                    continue
                if c in ("'", '"'): depth_in_str = c; continue
                if c == "[": depth += 1
                elif c == "]": depth -= 1
                elif c in ("{", "}"): pass
                elif c == "," and depth == 1:
                    commas.append(j)
            if len(commas) >= 3:
                photo_arg = row[commas[2]+1:commas[3] if len(commas) > 3 else -1].strip()
                if photo_arg.startswith("'images/") or "images/candidates" in photo_arg:
                    per_muni[muni_slug]["with_photo"] += 1
                    totals["with_photo"] += 1

            obj_open = row.find("{")
            if obj_open < 0: continue
            obj_close = find_close(row, obj_open, "{", "}")
            if obj_close < 0: continue
            obj_src = row[obj_open:obj_close]

            bio = extract_string_field(obj_src, "bio")
            if bio:
                per_muni[muni_slug]["with_bio"] += 1
                totals["with_bio"] += 1
            if heimild_url_count(obj_src) > 0:
                per_muni[muni_slug]["with_heimild"] += 1
                totals["with_heimild"] += 1
            if has_array_field(obj_src, "news", r"url:\s*'[^']+'"):
                per_muni[muni_slug]["with_news"] += 1
                totals["with_news"] += 1
            if has_array_field(obj_src, "social", r"url:\s*'[^']+'"):
                per_muni[muni_slug]["with_social"] += 1
                totals["with_social"] += 1

print("=" * 70)
print("OVERALL TOTALS")
print("=" * 70)
print(f"  Munis with candidate data:       {len(per_muni)}")
print(f"  Parties (lists):                 {totals['parties']}")
print(f"  Candidates:                      {totals['candidates']}")
print()
print(f"  Agendas with content:            {totals['agendas_full']}  ({totals['agendas_full']/totals['parties']*100:.0f}%)")
print(f"  Agendas empty:                   {totals['agendas_empty']}")
print(f"  Parties with platformUrl:        {totals['agendas_with_platform']}  ({totals['agendas_with_platform']/totals['parties']*100:.0f}%)")
print()
print(f"  Candidates with photo:           {totals['with_photo']}  ({totals['with_photo']/totals['candidates']*100:.0f}%)")
print(f"  Candidates with bio:             {totals['with_bio']}  ({totals['with_bio']/totals['candidates']*100:.0f}%)")
print(f"  Candidates with heimild URLs:    {totals['with_heimild']}  ({totals['with_heimild']/totals['candidates']*100:.0f}%)")
print(f"  Candidates with news items:      {totals['with_news']}  ({totals['with_news']/totals['candidates']*100:.0f}%)")
print(f"  Candidates with social links:    {totals['with_social']}  ({totals['with_social']/totals['candidates']*100:.0f}%)")
print()
print("=" * 70)
print("MUNIS WITH WORST AGENDA COVERAGE (parties without content)")
print("=" * 70)
ranked = sorted(per_muni.items(), key=lambda x: -x[1]["agendas_empty"])
for slug, s in ranked[:20]:
    if s["agendas_empty"] > 0:
        print(f"  {slug:<22} {s['agendas_empty']}/{s['parties']} parties empty  ({s['agendas_full']} have content)")
print()
print("=" * 70)
print("MUNIS WITH WORST PHOTO COVERAGE")
print("=" * 70)
ranked = sorted(per_muni.items(), key=lambda x: x[1]["with_photo"]/max(1,x[1]["candidates"]))
for slug, s in ranked[:15]:
    pct = s['with_photo']/max(1,s['candidates'])*100
    print(f"  {slug:<22} {s['with_photo']}/{s['candidates']} candidates have photo  ({pct:.0f}%)")
print()
print("=" * 70)
print("MUNIS WITH WORST BIO COVERAGE")
print("=" * 70)
ranked = sorted(per_muni.items(), key=lambda x: x[1]["with_bio"]/max(1,x[1]["candidates"]))
for slug, s in ranked[:15]:
    pct = s['with_bio']/max(1,s['candidates'])*100
    print(f"  {slug:<22} {s['with_bio']}/{s['candidates']} candidates have bio  ({pct:.0f}%)")

# ── Polls coverage ───────────────────────────────────────────────────────────
import importlib.util
polls_text = (ROOT / "js" / "data" / "polls.js").read_text(encoding="utf-8")
poll_munis = re.findall(r"^\s+(\w+):\s*\{\s*$", polls_text, re.MULTILINE)
print()
print("=" * 70)
print(f"POLLS: {len(poll_munis)} of {len(per_muni)} munis have polling data")
print(f"  Covered: {', '.join(poll_munis)}")
print("=" * 70)
