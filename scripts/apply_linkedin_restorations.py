"""Parse temp/linkedin_restored.md and apply each NEW_REWRITE to
scan_results/audit_results.json under rescue.rewrite. Only acts on
entries with a NEW_REWRITE block; entries marked NO_CHANGE_NEEDED
are skipped.
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / 'scan_results' / 'audit_results.json'
REPORT = ROOT / 'temp' / 'linkedin_restored.md'

text = REPORT.read_text(encoding='utf-8')
blocks = re.split(r'\n## ID:\s*', text)
applied_rewrites = []
no_change = []
for blk in blocks[1:]:
    lines = blk.split('\n', 1)
    cid = lines[0].strip()
    body = lines[1] if len(lines) > 1 else ''
    if 'NO_CHANGE_NEEDED' in body[:200]:
        no_change.append(cid)
        continue
    m_new = re.search(r'^NEW_REWRITE:\s*(.+?)(?=\n---|\Z)', body, re.DOTALL | re.MULTILINE)
    if m_new:
        new = m_new.group(1).strip()
        applied_rewrites.append((cid, new))

print(f'Found {len(applied_rewrites)} rewrites + {len(no_change)} no-change')

audit = json.loads(AUDIT.read_text(encoding='utf-8'))
applied = 0
for cid, new in applied_rewrites:
    e = audit.get(cid)
    if not e:
        print(f'  ⚠ {cid}: not in audit')
        continue
    rescue = e.setdefault('rescue', {})
    old = rescue.get('rewrite') or ''
    rescue['rewrite'] = new
    rescue['rewrite_words'] = len(new.split())
    e['applied'] = False
    audit[cid] = e
    applied += 1
    print(f'  ✓ {cid}  ({len(old)} → {len(new)} ch)')

AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nApplied {applied} LinkedIn-restored rewrites')
print(f'Skipped (no change): {len(no_change)} → {no_change}')
