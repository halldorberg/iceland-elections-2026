"""Restore the 39 originals from a pre-trim backup, then re-strip with a
smarter regex that doesn't break at ordinal periods (like "í 2. sæti.").

Strategy: anchor each trim pattern to END OF STRING. The "Listinn er
leiddur af …" / "Oddviti listans er …" trailers always sit at the end
of the bio, so we can safely greedy-match to $.

Mid-sentence cases (a leadership reference embedded inside another
sentence) are reported but NOT auto-trimmed — they need a hand fix.
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / 'scan_results' / 'audit_results.json'
BAK_PRIMARY  = ROOT / 'scan_results' / 'audit_results.json.bak_strip_addr'
BAK_FALLBACK = ROOT / 'scan_results' / 'audit_results.json.bak_pre_apply'

TARGETS = """
SNB.B.3 SNB.D.3 VME.D.17 SFJ.M.17 BBD.D.16 ISF.M.3 OLF.D.3 OLF.S.3
DVB.B.3 FJB.D.3 RTE.B.3 RTE.D.3 HNB.D.3 AKR.S.13 HVG.OKH.11 HVG.S.11
HVG.OKH.12 HVG.S.12 HVG.OKH.13 HVG.S.13 OLF.D.11 OLF.D.12 OLF.D.13
OLF.D.14 HFJ.HFJK.11 RTY.RYA.11 RTY.D.12 RTY.D.13 AKR.D.7 AKR.D.8
AKR.D.9 MUT.B.6 FJD.D.7 SNB.B.6 SNB.M.8 SNB.M.9 KOP.S.18
HFJ.D.3
""".split()
# Note SNB.S.6 was tiny in original; included for completeness
TARGETS += ['SNB.S.6']

# Trim patterns — anchored to END of string so we capture trailing
# leadership sentences in full, regardless of internal "N. sæti" periods.
TRIM_PATTERNS = [
    (re.compile(r'\s*\bListinn(?:\s+samanstendur\s+(?:af|úr))?\s+er\s+leiddur\s+af\s[\s\S]+$', re.IGNORECASE),
     'listinn-leiddur'),
    (re.compile(r'\s*\bOddviti(?:\s+\w+)?\s+(?:listans|hans|hennar)\s+er\s[\s\S]+$', re.IGNORECASE),
     'oddviti'),
    (re.compile(r'\s*\bMiðflokksdeild\s+\w+\s+var\s+stofnuð\s[\s\S]+$', re.IGNORECASE),
     'midflokksdeild'),
]

audit_now = json.loads(AUDIT.read_text(encoding='utf-8'))
bak1 = json.loads(BAK_PRIMARY.read_text(encoding='utf-8'))
bak2 = json.loads(BAK_FALLBACK.read_text(encoding='utf-8'))

def get_original(cid):
    """Return (rewrite_text, source_label) — falls through bak1 → bak2."""
    for src_name, src in [('bak_strip_addr', bak1), ('bak_pre_apply', bak2)]:
        e = src.get(cid) or {}
        rew = (e.get('rescue') or {}).get('rewrite')
        if rew: return rew, src_name
    return None, None

print(f'Re-trimming {len(TARGETS)} entries…\n')
restored, retrimmed, manual_needed = 0, 0, 0
for cid in TARGETS:
    orig, src_name = get_original(cid)
    if not orig:
        print(f'  ⚠ {cid}: no original in either backup — skipping (current text left as-is)')
        continue

    # Restore + re-trim
    new_text = orig
    removed_labels = []
    for rx, label in TRIM_PATTERNS:
        m = rx.search(new_text)
        if m:
            removed_labels.append(label)
            new_text = rx.sub('', new_text)

    new_text = re.sub(r'\s{2,}', ' ', new_text).strip()
    # Make sure we end with a period
    if new_text and not new_text.endswith('.'):
        new_text = new_text.rstrip(',;:- ') + '.'

    if not removed_labels:
        # Pattern didn't match — needs manual review (mid-sentence cases)
        # Restore the original text anyway so the user sees a clean rewrite.
        manual_needed += 1
        flag = '🤔 needs-manual-trim'
    else:
        retrimmed += 1
        flag = f'✓ trimmed [{",".join(removed_labels)}]'

    # Write back into current audit
    e = audit_now.setdefault(cid, {})
    rescue = e.setdefault('rescue', {})
    rescue['rewrite'] = new_text
    rescue['rewrite_words'] = len(new_text.split())
    e['rescue'] = rescue
    e['applied'] = False

    print(f'  {flag} {cid}  ({len(orig)} → {len(new_text)} ch)')
    restored += 1

AUDIT.write_text(json.dumps(audit_now, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nRestored + re-trimmed: {retrimmed}')
print(f'Restored but pattern did not match: {manual_needed}')
print(f'Total touched: {restored}')
print(f'Saved → {AUDIT}')
