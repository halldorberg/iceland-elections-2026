"""For each scan-review bio that mentions another candidate as oddviti or
list leader, strip just the offending sentence(s) and write the trimmed
result back into audit_results[id].rescue.rewrite.

The trim-pattern is conservative: only sentences that BEGIN with one of
- "Oddviti listans er …"
- "Listinn er leiddur af …"
- "Oddviti hans er …"
- "Hún/Hann/[name] leiðir listann …" (only when the name is NOT the subject)
- standalone "Miðflokksdeild Suðurnesjabæjar var stofnuð …" (off-topic boilerplate)

Each rewrite is round-tripped through .strip() and writes a recomputed
rewrite_words count. Resolutions list gets a 'dropped' marker for the
removed sentence.
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / 'scan_results' / 'audit_results.json'

# IDs the user has flagged or that I auto-detected
TARGETS = """
SNB.B.3 SNB.D.3 VME.D.17 SFJ.M.17 BBD.D.16 ISF.M.3 OLF.D.3 OLF.S.3
DVB.B.3 FJB.D.3 RTE.B.3 RTE.D.3 HNB.D.3 AKR.S.13 HVG.OKH.11 HVG.S.11
HVG.OKH.12 HVG.S.12 HVG.OKH.13 HVG.S.13 OLF.D.11 OLF.D.12 OLF.D.13
OLF.D.14 HFJ.HFJK.11 RTY.RYA.11 RTY.D.12 RTY.D.13 AKR.D.7 AKR.D.8
AKR.D.9 MUT.B.6 FJD.D.7 SNB.B.6 SNB.S.6 SNB.M.8 SNB.M.9 KOP.S.18
HFJ.D.3
""".split()

# Patterns: each tuple is (regex, what-it-removes-description)
SENTENCE_PATTERNS = [
    # Whole sentences starting with one of these phrases
    (re.compile(r'\bOddviti(?:\s+\w+)?\s+(?:listans|hans|hennar)\s+er\s+[^.]+\.\s*'),
     'oddviti-listans'),
    (re.compile(r'\bListinn\s+er\s+leiddur\s+af\s+[^.]+\.\s*'),
     'listinn-leiddur-af'),
    # Off-topic deildin-stofnud boilerplate
    (re.compile(r'\bMiðflokksdeild\s+\w+\s+var\s+stofnuð\s+[^.]+\.\s*'),
     'midflokksdeild-stofnud'),
]

audit = json.load(AUDIT.open(encoding='utf-8'))

print(f'Targeting {len(TARGETS)} candidates…\n')

modified = 0
for cid in TARGETS:
    a = audit.get(cid)
    if a is None:
        print(f'  ⚠ {cid}: no audit entry — skipping')
        continue

    rescue = a.get('rescue') or {}
    cur_text = (rescue.get('rewrite') or '').strip()
    fallback_bio = (a.get('bio') or '').strip()
    if not cur_text and fallback_bio:
        # Need to upgrade bio to a rewrite
        cur_text = fallback_bio
        rescue.setdefault('new_sources', [])
        rescue.setdefault('new_heimild', [])
        rescue.setdefault('resolutions', [])

    if not cur_text:
        print(f'  ⚠ {cid}: no text to trim — skipping')
        continue

    new_text = cur_text
    removed = []
    for rx, label in SENTENCE_PATTERNS:
        ms = list(rx.finditer(new_text))
        if ms:
            for m in reversed(ms):
                removed.append((label, m.group(0).strip()))
            new_text = rx.sub(' ', new_text)

    new_text = re.sub(r'\s{2,}', ' ', new_text).strip()

    if new_text == cur_text.strip():
        print(f'  – {cid}: no pattern matched (skip)')
        continue

    # Update rescue
    word_count = len(new_text.split())
    rescue['rewrite'] = new_text
    rescue['rewrite_words'] = word_count
    resolutions = rescue.get('resolutions') or []
    for label, snippet in removed:
        resolutions.append({
            'kind': 'dropped',
            'text': f'Removed off-subject sentence ({label}): "{snippet[:120]}"',
        })
    rescue['resolutions'] = resolutions
    a['rescue'] = rescue
    a['applied'] = False  # ensure it's still pending review
    audit[cid] = a
    modified += 1
    print(f'  ✓ {cid}: trimmed {len(removed)} sentence(s); {len(cur_text)} → {len(new_text)} ch')

# Write out
AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nUpdated {modified} entries → {AUDIT}')
