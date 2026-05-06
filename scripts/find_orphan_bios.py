"""Find candidates whose bio in scan-review is already published live in
candidates.js but where audit_results doesn't have applied=true.
These are 'orphan' approvals — bios applied inline that never closed
the loop with the scan-review pipeline."""
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path

# 1) Live bios from candidates.js (id → first 80 chars of bio)
src = open('js/data/candidates.js', encoding='utf-8').read()
mm = re.search(r"const REAL_DATA\s*=\s*\{([\s\S]+?)\};", src)
slug_for_var = {}
if mm:
    for kv in re.finditer(r"(\w+):\s*([A-Z_]+)", mm.group(1)):
        slug_for_var[kv.group(2)] = kv.group(1)

def find_close(s, op, oc, cc):
    depth, i, in_str = 0, op, None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c == "/" and i+1 < len(s) and s[i+1] == "/":
            nl = s.find("\n", i+2)
            i = (nl+1) if nl >= 0 else len(s)
            continue
        if c == "/" and i+1 < len(s) and s[i+1] == "*":
            end = s.find("*/", i+2)
            i = (end+2) if end >= 0 else len(s)
            continue
        if c in ("'", '"'):
            in_str = c
            i += 1
            continue
        if c == oc:
            depth += 1
        elif c == cc:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1

def extract_string_field(obj_src, key):
    m = re.search(r"\b" + re.escape(key) + r":\s*(null|')", obj_src)
    if not m or m.group(1) == 'null':
        return None
    start = m.end() - 1
    i = start + 1
    out = []
    while i < len(obj_src):
        c = obj_src[i]
        if c == "\\" and i+1 < len(obj_src):
            out.append(obj_src[i:i+2])
            i += 2
            continue
        if c == "'":
            return "".join(out)
        out.append(c)
        i += 1
    return None

const_starts = [(m.start(), m.end(), m.group(1)) for m in re.finditer(r"^const\s+([A-Z_]+)\s*=\s*\{", src, re.MULTILINE)]
const_starts.append((len(src), len(src), None))

live_bios = {}  # id → bio_text first 200 chars
for ci, (cs, ce, var) in enumerate(const_starts[:-1]):
    if var not in slug_for_var: continue
    next_cs = const_starts[ci+1][0]
    block = src[ce:next_cs]
    party_marks = list(re.finditer(r"^  ([A-Z]{1,4}):\s*\{", block, re.MULTILINE))
    for bi, pm in enumerate(party_marks):
        code = pm.group(1)
        body_end = (party_marks[bi+1].start() if bi+1 < len(party_marks) else len(block))
        party_body = block[pm.end():body_end]
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
            obj_open = row.find("{")
            if obj_open < 0: continue
            obj_close = find_close(row, obj_open, "{", "}")
            if obj_close < 0: continue
            obj_src = row[obj_open:obj_close]
            bio = extract_string_field(obj_src, "bio")
            if bio:
                live_bios[f'{var}.{code}.{ballot}'] = bio[:200]

audit = json.load(open('scan_results/audit_results.json', encoding='utf-8'))

bios_in_review = {}
for path in sorted(Path('scan_results').glob('bios_*.json')):
    data = json.load(open(path, encoding='utf-8'))
    for r in data.get('results', []) or []:
        cid = r.get('id')
        if cid:
            bios_in_review[cid] = r

# Build name→live_id map for fallback
def name_from_bio(bio):
    if not bio: return ''
    if ' er ' in bio:
        return bio.split(' er ', 1)[0].strip()
    return ''

live_name_to_id = {}
for cid, bio in live_bios.items():
    n = name_from_bio(bio)
    if n:
        live_name_to_id.setdefault(n, cid)

orphans_by_bucket = {}
for cid, b in bios_in_review.items():
    is_applied = (audit.get(cid) or {}).get('applied') is True
    if is_applied: continue
    # Direct ID match
    if cid in live_bios:
        bucket = '.'.join(cid.split('.')[:2])
        orphans_by_bucket.setdefault(bucket, []).append((cid, 'direct'))
        continue
    # Name fallback disabled — too many false positives from common names

print(f'Orphan IDs (in scan-review but already published): {sum(len(v) for v in orphans_by_bucket.values())} across {len(orphans_by_bucket)} (muni, party) buckets\n')
for bucket in sorted(orphans_by_bucket.keys(), key=lambda b: -len(orphans_by_bucket[b])):
    rows = orphans_by_bucket[bucket]
    ids = sorted(r[0] for r in rows)
    print(f'  {bucket:>10}: {len(rows):>3}  → {", ".join(ids)}')
