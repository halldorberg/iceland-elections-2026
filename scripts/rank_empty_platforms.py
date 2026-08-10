"""Rank parties with empty agendas by (1) muni population, (2) national-party
prominence, (3) other tiebreakers. Output: ranked TSV-like table."""
from __future__ import annotations
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).parent.parent
SRC = (ROOT / "js" / "data" / "candidates.js").read_text(encoding="utf-8")
MUNI_TXT = (ROOT / "js" / "data" / "municipalities.js").read_text(encoding="utf-8")

# parse muni populations
populations = {}
for m in re.finditer(r"id:\s*'([^']+)'.*?population:\s*(\d+)", MUNI_TXT, re.DOTALL):
    populations[m.group(1)] = int(m.group(2))

# parse party display names
PARTIES_TXT = (ROOT / "js" / "data" / "parties.js").read_text(encoding="utf-8")
party_names = {}
for m in re.finditer(r"(\w+):\s*\{[^}]*?code:\s*'([^']*)'[^}]*?name:\s*'([^']+)'", PARTIES_TXT, re.DOTALL):
    party_names[m.group(2)] = m.group(3)

# REAL_DATA mapping: var -> slug
mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", SRC)
slug_for_var = {}
for kv in re.finditer(r"(\w+):\s*([A-Z_]+)", mm.group(1)):
    slug_for_var[kv.group(2)] = kv.group(1)

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

# Party prominence tiers — lower = more prominent
PARTY_TIER = {
    'D': 1, 'B': 1, 'S': 1, 'V': 1, 'A': 1,
    'M': 2, 'C': 2,
    'P': 3, 'F': 3,
    # All other letters are local lists / regional / multi-letter codes
}
def party_tier(code):
    if code in PARTY_TIER:
        return PARTY_TIER[code]
    if len(code) > 1:  # multi-letter codes are nearly always local lists
        return 5
    return 4  # other single-letter (e.g. G, J, R for Reykjavík-only lists)

# walk every const muni and find empty-agenda parties
empties = []
const_starts = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"^const\s+([A-Z_]+)\s*=\s*\{", SRC, re.MULTILINE)]
const_starts.append((len(SRC), len(SRC), None))

for ci, (cs, ce, var) in enumerate(const_starts[:-1]):
    if var not in slug_for_var: continue
    slug = slug_for_var[var]
    pop = populations.get(slug, 0)
    next_cs = const_starts[ci+1][0]
    block = SRC[ce:next_cs]
    party_marks = list(re.finditer(r"^  ([A-Z]{1,4}):\s*\{", block, re.MULTILINE))
    for bi, pm in enumerate(party_marks):
        code = pm.group(1)
        body_end = (party_marks[bi+1].start() if bi+1 < len(party_marks) else len(block))
        party_body = block[pm.end():body_end]
        # has agenda content?
        agenda_m = re.search(r"\bagenda:\s*\[", party_body)
        has_items = False
        if agenda_m:
            ap = agenda_m.end()-1
            ac = find_close(party_body, ap, "[", "]")
            if ac > 0 and re.search(r"icon:\s*'[^']+'", party_body[ap+1:ac-1]):
                has_items = True
        if has_items:
            continue
        has_platform = bool(re.search(r"\bplatformUrl:\s*'[^']+'", party_body))
        # extract tagline (informational)
        tag_m = re.search(r"tagline:\s*'((?:[^'\\]|\\.)*)'", party_body)
        tagline = tag_m.group(1).replace("\\'", "'") if tag_m else ''
        # candidate count
        lm = re.search(r"\blist:\s*\[", party_body)
        n_cands = 0
        if lm:
            lo = lm.end()-1
            lc = find_close(party_body, lo, "[", "]")
            if lc > 0:
                n_cands = len(re.findall(r"^      \[\s*\d+", party_body[lo:lc], re.MULTILINE))
        empties.append({
            'slug': slug, 'population': pop,
            'party_code': code, 'party_name': party_names.get(code, ''),
            'tier': party_tier(code), 'has_platformUrl': has_platform,
            'tagline': tagline, 'n_candidates': n_cands,
        })

# rank
empties.sort(key=lambda e: (-e['population'], e['tier'], e['party_code']))

print(f"Total parties with empty agenda: {len(empties)}")
print(f"  (have platformUrl but no items: {sum(1 for e in empties if e['has_platformUrl'])})")
print()
print("=" * 100)
print(f"{'#':>3}  {'Pop':>7}  {'Muni':<22}  {'Code':<5}  {'Party / list':<32}  Tagline")
print("=" * 100)
for i, e in enumerate(empties, 1):
    pname = e['party_name'] or e['tagline'][:32]
    pname_disp = (pname[:30] + '..') if len(pname) > 32 else pname
    print(f"{i:>3}  {e['population']:>7}  {e['slug']:<22}  {e['party_code']:<5}  {pname_disp:<32}  {e['tagline'][:60]}")
