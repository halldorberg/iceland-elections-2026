#!/usr/bin/env python3
"""Quick check: do any of the 80 bio names appear as more than one candidate
row in candidates.js? If so, apply_bios's name-only regex risks updating the
wrong candidate (cross-muni collision)."""
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).parent.parent
src = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")

# Collect names from `[N, 'name', 'occ', ...` candidate rows
row_re = re.compile(r"\[\d+\s*,\s*'((?:[^'\\]|\\.)*?)'\s*,\s*'", re.DOTALL)
names = [m.group(1).replace("\\'", "'") for m in row_re.finditer(src)]
counts = Counter(names)

bio_names = []
for p in sorted((ROOT / "scan_results").glob("bios_2026-05-01_*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    for r in d.get("results", []):
        bio_names.append(r["name"])

risky = [n for n in bio_names if counts.get(n, 0) > 1]
print(f"Bio names checked: {len(bio_names)}")
print(f"Risky (name appears >1 times in candidates.js): {len(risky)}")
for n in risky:
    print(f'  "{n}" appears {counts[n]} times')
