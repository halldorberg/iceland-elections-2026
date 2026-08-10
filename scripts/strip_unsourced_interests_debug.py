"""Debug the bracket imbalance — show each candidate slice being replaced."""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent
SRC  = ROOT / "js" / "data" / "candidates.js"

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
    m = re.search(r"\bheimild:\s*(null|\[)", obj_src)
    if not m or m.group(1) == "null":
        return False
    open_pos = m.end() - 1
    close = find_close(obj_src, open_pos, "[", "]")
    if close < 0: return False
    body = obj_src[open_pos+1:close-1]
    return bool(re.search(r"url:\s*'[^']+'", body))

src = SRC.read_text(encoding="utf-8")

mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", src)
slug_for_var = {}
if mm:
    for kv in re.finditer(r"(\w+):\s*([A-Z_]+)", mm.group(1)):
        slug_for_var[kv.group(2)] = kv.group(1)

const_starts = []
for m in re.finditer(r"^const\s+([A-Z_]+)\s*=\s*\{", src, re.MULTILINE):
    const_starts.append((m.start(), m.end(), m.group(1)))
const_starts.append((len(src), len(src), None))

bad = 0
edits = []
for ci, (cs, ce, var) in enumerate(const_starts[:-1]):
    if var not in slug_for_var: continue
    next_cs = const_starts[ci+1][0]
    block = src[ce:next_cs]
    muni_slug = slug_for_var[var]

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
            row = src[row_abs_start:list_offset + row_end]
            ip = row_end

            bm = re.match(r"\[\s*(\d+)\s*,", row)
            ballot = int(bm.group(1)) if bm else 0
            name_m = re.search(r"\[\s*\d+\s*,\s*'((?:\\.|[^'\\])*)'", row)
            name = (name_m.group(1).replace("\\'", "'")) if name_m else "?"

            obj_open = row.find("{")
            if obj_open < 0:
                continue
            obj_close = find_close(row, obj_open, "{", "}")
            if obj_close < 0: continue
            obj_src = row[obj_open:obj_close]

            bio = extract_string_field(obj_src, "bio")
            has_h = has_heimild_with_url(obj_src)

            if bio or has_h:
                continue

            int_m = re.search(r"\binterests:\s*\[", obj_src)
            if not int_m:
                continue
            int_open_in_obj = int_m.end() - 1
            int_close_in_obj = find_close(obj_src, int_open_in_obj, "[", "]")
            if int_close_in_obj < 0:
                continue
            int_body = obj_src[int_open_in_obj+1:int_close_in_obj-1]
            if not re.search(r"'[^']+'", int_body):
                continue

            slice_to_replace = obj_src[int_open_in_obj:int_close_in_obj]
            # Sanity: slice must start with [ and end with ]
            if not slice_to_replace.startswith("[") or not slice_to_replace.endswith("]"):
                bad += 1
                print(f"BAD slice for {var}.{code}.{ballot} {name}")
                print(f"  starts: {slice_to_replace[:60]!r}")
                print(f"  ends:   ...{slice_to_replace[-60:]!r}")
                print(f"  obj_src bracket counts: [={obj_src.count('[')} ]={obj_src.count(']')}")
                continue

            # Sanity: bracket count inside slice must match
            if slice_to_replace.count("[") != slice_to_replace.count("]"):
                bad += 1
                print(f"UNBALANCED slice for {var}.{code}.{ballot} {name}")
                print(f"  [={slice_to_replace.count('[')} ]={slice_to_replace.count(']')}")
                print(f"  slice: {slice_to_replace[:200]!r}")

            # Compute absolute positions
            int_abs_start = row_abs_start + obj_open + int_open_in_obj
            int_abs_end   = row_abs_start + obj_open + int_close_in_obj
            verify_slice  = src[int_abs_start:int_abs_end]
            if verify_slice != slice_to_replace:
                bad += 1
                print(f"POSITION MISMATCH for {var}.{code}.{ballot} {name}")
                print(f"  obj-relative: {slice_to_replace[:60]!r}")
                print(f"  src absolute: {verify_slice[:60]!r}")
            edits.append((int_abs_start, int_abs_end, "null", f"{var}.{code}.{ballot} {name}"))

print(f"\nBad slices: {bad}")
print(f"Total edits: {len(edits)}")

# Check for overlapping/duplicate positions
edits.sort()
for i in range(len(edits)-1):
    if edits[i][1] > edits[i+1][0]:
        print(f"OVERLAP: {edits[i][3]} ends {edits[i][1]} > {edits[i+1][3]} starts {edits[i+1][0]}")
    if edits[i][0] == edits[i+1][0]:
        print(f"DUPLICATE START: {edits[i][3]} and {edits[i+1][3]} both start at {edits[i][0]}")
