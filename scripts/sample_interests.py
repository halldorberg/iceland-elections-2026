"""Dump the actual interests strings for the 85 candidates flagged as
interests-without-bio-or-source."""
import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent
report = json.loads((ROOT / "audit_unsourced_report.json").read_text(encoding="utf-8"))
src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")

import re
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

for r in report["suspect_interests"]:
    name = r["name"]
    pattern = re.escape(name) + r"'[^,]*,\s*'[^']*'\s*,\s*(?:[^,]+),\s*\{"
    m = re.search(pattern, src)
    if not m:
        # fall back to simpler search
        m = re.search(r"'" + re.escape(name) + r"'", src)
        if not m:
            continue
    obj_open = src.find("{", m.end()-1)
    if obj_open < 0:
        continue
    obj_close = find_close(src, obj_open, "{", "}")
    if obj_close < 0:
        continue
    obj_src = src[obj_open:obj_close]
    int_m = re.search(r"\binterests:\s*\[([^\]]*)\]", obj_src)
    if not int_m:
        continue
    interests = re.findall(r"'((?:[^'\\]|\\.)*)'", int_m.group(1))
    interests = [i.replace("\\'", "'") for i in interests]
    print(f"{r['muni']}/{r['party']}.{r['ballot']:>2} {name}")
    print(f"   {interests}")
