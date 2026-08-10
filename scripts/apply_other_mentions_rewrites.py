"""Parse temp/other_mentions_audit.md and apply each PROPOSED rewrite
to scan_results/audit_results.json under rescue.rewrite.
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / 'scan_results' / 'audit_results.json'
REPORT = ROOT / 'temp' / 'other_mentions_audit.md'

text = REPORT.read_text(encoding='utf-8')
# Split on '## ID:' headers
blocks = re.split(r'\n## ID:\s*', text)
parsed = []
for blk in blocks[1:]:
    # First line is the cid
    lines = blk.split('\n', 1)
    cid = lines[0].strip()
    body = lines[1] if len(lines) > 1 else ''
    m_orig = re.search(r'^ORIGINAL:\s*(.+?)(?=\nPROPOSED:|\Z)', body, re.DOTALL | re.MULTILINE)
    m_prop = re.search(r'^PROPOSED:\s*(.+?)(?=\nREASON:|\Z)', body, re.DOTALL | re.MULTILINE)
    if m_orig and m_prop:
        parsed.append((cid, m_orig.group(1).strip(), m_prop.group(1).strip()))

print(f'Parsed {len(parsed)} rewrites from report\n')

audit = json.loads(AUDIT.read_text(encoding='utf-8'))
applied = 0
missing = []
for cid, orig, prop in parsed:
    e = audit.get(cid)
    if not e:
        missing.append(cid)
        continue
    rescue = e.setdefault('rescue', {})
    rescue['rewrite'] = prop
    rescue['rewrite_words'] = len(prop.split())
    e['applied'] = False
    audit[cid] = e
    applied += 1
    print(f'  ✓ {cid}  ({len(orig)} → {len(prop)} ch)')

if missing:
    print(f'\n⚠ Missing in audit: {missing}')

AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nApplied {applied} rewrites → {AUDIT}')
