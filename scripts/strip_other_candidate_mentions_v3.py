"""Comprehensive sweep for ALL bios in pending audit that talk about
other candidates (oddviti, list-leader, '... leiddur af X', '... leitt
er af X', 'X leiðir listann'). Trims them in-place.

Patterns (applied in order, first match wins per bio):

  1. Trailing sentence "Listinn/Framboðslistinn/Fullskipaður/D-listinn ... er leiddur af X"
     — remove from sentence start to end of string.
  2. Trailing fragment ", en listinn er leiddur af X" — remove from comma to end.
  3. Trailing fragment "; listinn er leiddur af X" — remove from semicolon to end.
  4. Trailing fragment "; oddviti listans er X" — remove from semicolon to end.
  5. Trailing fragment ", en oddviti listans er X" — remove from comma to end.
  6. Trailing fragment ", þar sem X leiðir listann/X er oddviti listans" — remove.
  7. Trailing sentence ". D-listinn/S-listinn/Listi <party> er leiddur af X" — remove sentence + any continuation.
  8. Mid-sentence ", en Vinstrið/<party> er sameiginlegt framboð ... sem leitt er af X" — remove.
  9. Embedded relative clause ", óháðu sveitarstjórnarframboði sem leitt er af X," — collapse.

Edge cases (handled manually):
  - ISF.B.3 has multi-sentence trailing detail about list-leader history
  - SNB.S.3 has mid-sentence run-on listing the leader and the #2
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / 'scan_results' / 'audit_results.json'

# A "leader phrase" tail — used in many patterns
LEADER_TAIL = r'(?:er\s+leidd(?:ur|ir)|er\s+leiddur)\s+af\s[\s\S]+$'

TRIM_PATTERNS = [
    # ── Trailing sentences (anchor at sentence start, eat to end) ───────────
    # 7. ". D-listinn / S-listinn / Listi <party> ... er leiddur af X" + trailing
    (re.compile(rf'\.\s+(?:[A-ZÁÉÍÓÚÝÞÆÖÐ]-listinn(?:\s+\w+){{0,3}}|Listi\s+\w+(?:\s+og\s+\w+)?)\s+(?:er\s+leiddur\s+af\s)[\s\S]+$', re.IGNORECASE),
     'period-d-listinn-er-leiddur'),

    # 1. ". Listinn/Framboðslistinn/Fullskipaður framboðslisti ... og er leiddur af X"
    (re.compile(rf'\.\s+(?:Listinn|Framboðslistinn|Fullskipaður\s+framboðslisti|Listinn\s+er\s+einn[^.]*)\s+[\s\S]+?\bog\s+er\s+leiddur\s+af\s[\s\S]+$', re.IGNORECASE),
     'period-listinn-...-og-er-leiddur'),

    # ── Trailing fragments after comma/semicolon ────────────────────────────
    # 2/3. ", en listinn er leiddur af X" or "; listinn er leiddur af X" → drop
    (re.compile(r'[,;]\s+(?:en\s+)?listinn\s+er\s+leiddur\s+af\s[\s\S]+$', re.IGNORECASE),
     'comma-en-listinn-leiddur'),

    # 4. "; oddviti listans er X."
    (re.compile(r'\s*;\s+oddviti(?:\s+\w+)?\s+(?:listans|hans|hennar)\s+er\s[\s\S]+$', re.IGNORECASE),
     'semicolon-oddviti'),

    # 5. ", en oddviti listans er X."
    (re.compile(r',\s+en\s+oddviti(?:\s+\w+)?\s+(?:listans|hans|hennar)\s+er\s[\s\S]+$', re.IGNORECASE),
     'comma-en-oddviti'),

    # 6/7. ", þar sem X leiðir listann/X er oddviti listans" → drop tail
    (re.compile(r',\s+þar\s+sem\s+[\s\S]+?(?:leiðir\s+(?:listann|listans)|er\s+oddviti\s+(?:listans|hans|hennar))[^.]*\.\s*$', re.IGNORECASE),
     'thar-sem-leider-listann'),

    # 8. ", en Vinstrið/<party> ... sem leitt er af X"
    (re.compile(r',\s+(?:en\s+)?[A-ZÁÉÍÓÚÝÞÆÖÐ]\w+\s+er\s+sameiginleg(?:t|ur)\s+framboð[\s\S]+?sem\s+leitt\s+er\s+af\s[\s\S]+$', re.IGNORECASE),
     'comma-en-party-sem-leitt'),
]

# Cases the patterns can't cleanly handle — manual rewrites
MANUAL = {
    'ISF.B.3': (
        # Drop final two sentences talking about list-leader and 2022 holdovers
        'Stefán Hannibal Hafberg er sjávarútvegsfræðingur og skipar 3. sæti á B-lista Framsóknar og óháðra í Ísafjarðarbæ í sveitarstjórnarkosningum 2026. '
        'Hann hefur menntað sig á sviði auðlindafræða og hefur tengingar við Háskólann á Akureyri þar sem hann hefur stundað rannsóknir á sviði fiskeldis og auðlindavísinda. '
        'Stefán Hannibal hefur starfað í íslensku fiskeldi og laxeldi og hefur m.a. fengið styrk úr nýsköpunarverkefninu „Hafsjór af hugmyndum" á vegum Vestfjarðastofu fyrir verkefni um eldislax í neytendapakkningum.'
    ),
    'SNB.S.3': (
        # Drop the run-on about S-listinn leader and #2
        'Egill Rúnar Sigurðsson er stjórnmálafræðingur, atvinnurekandi og ökukennari, búsettur í Garði, og skipar 3. sæti á S-lista Samfylkingarinnar og óháðra í Suðurnesjabæ í sveitarstjórnarkosningum 2026. '
        'Hann hefur verið virkur í þjóðfélagsumræðunni um árabil og rekur bloggið „Pólitík og pælingar" þar sem hann hefur skrifað um atvinnumál, sjávarútveg og samfélagsmál á Suðurnesjum.'
    ),
    'RTY.RYA.13': (
        # Already lightly trimmed; remove the embedded "óháðu sveitarstjórnarframboði sem leitt er af X" relative clause
        'Gabríel Snær Ólafsson er pípulagninganemi. Hann skipar 13. sæti á Á-lista í Rangárþingi ytra fyrir sveitarstjórnarkosningarnar 16. maí 2026.'
    ),
    'HAF.A.5': (
        # Drop the trailing ", en Vinstrið er sameiginlegt framboð ... sem leitt er af X" segment
        'Margrét Pétursdóttir er leiðsögumaður og verkakona, fædd 3. nóvember 1966 og búsett í Hafnarfirði. '
        'Hún hefur lengi tekið þátt í starfi Vinstrihreyfingarinnar – græns framboðs og var varaþingmaður Suðvesturkjördæmis fyrir hreyfinguna í mars–júní og september 2010 og janúar–febrúar 2013. '
        'Margrét skipar 5. sæti á A-lista Vinstrisins í Hafnarfirði í sveitarstjórnarkosningunum 16. maí 2026.'
    ),
    'HAF.A.6': (
        # Drop the trailing ", þar sem oddviti listans er X."
        'Anna Sigríður Sigurðardóttir starfar sem framhaldsskólakennari og hefur verið virk innan Vinstri grænna. '
        'Hún hefur átt sæti sem meðstjórnandi í kjördæmisráði flokksins. '
        'Anna Sigríður skipar sjötta sæti á sameiginlegum lista Vinstrisins (A-lista) — sameiginlegs framboðs Vinstri grænna og Vors til vinstri — í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026.'
    ),
    'GRN.D.14': (
        # Special case — has the leader phrase + #2 mention; drop sentence
        'Otti Rafn Sigmarsson skipar 14. sæti á framboðslista Sjálfstæðisflokksins í Grindavík fyrir sveitarstjórnarkosningarnar 2026.'
    ),
}

# Detect bios with other-candidate talk
DETECT = [
    re.compile(r'\bOddviti(?:\s+\w+)?\s+(?:listans|hans|hennar)\s+er\b', re.IGNORECASE),
    re.compile(r'\bListinn\s+(?:samanstendur\s+(?:af|úr)\s+)?er\s+leiddur\s+af\b', re.IGNORECASE),
    re.compile(r'\bleiddur\s+af\s+[A-ZÁÉÍÓÚÝÞÆÖÐ]', re.IGNORECASE),
    re.compile(r'\bleitt\s+er\s+af\s+[A-ZÁÉÍÓÚÝÞÆÖÐ]'),
    re.compile(r'\b(?:leiðir|er\s+oddviti)\s+(?:listans|listann)\b', re.IGNORECASE),
    re.compile(r'\bMiðflokksdeild\s+\w+\s+var\s+stofnuð\b', re.IGNORECASE),
]

def has_other_talk(text):
    return any(rx.search(text) for rx in DETECT)

audit = json.loads(AUDIT.read_text(encoding='utf-8'))
hits = []
for cid, e in audit.items():
    if e.get('applied'): continue
    text = ((e.get('rescue') or {}).get('rewrite') or e.get('bio') or '').strip()
    if not text: continue
    if has_other_talk(text):
        hits.append((cid, text))

print(f'Found {len(hits)} pending bios with other-candidate talk\n')

trimmed, manual_used, missed = 0, 0, []
for cid, text in hits:
    new = text
    if cid in MANUAL:
        new = MANUAL[cid]
        manual_used += 1
        flag = '✋ manual'
    else:
        applied_label = None
        for rx, label in TRIM_PATTERNS:
            if rx.search(new):
                new = rx.sub('', new)
                applied_label = label
                break
        if applied_label is None:
            missed.append((cid, text))
            continue
        flag = f'✓ [{applied_label}]'

    new = re.sub(r'\s{2,}', ' ', new).strip()
    if new and not new.endswith('.'):
        new = new.rstrip(',;:- ') + '.'

    # Verify the trim actually removed the trigger
    if has_other_talk(new):
        missed.append((cid, text))
        print(f'  ✗ {cid}: trim left detection still firing — needs review')
        print(f'    after: {new[:200]}')
        continue

    e = audit.setdefault(cid, {})
    rescue = e.setdefault('rescue', {})
    rescue['rewrite'] = new
    rescue['rewrite_words'] = len(new.split())
    e['rescue'] = rescue
    e['applied'] = False
    trimmed += 1
    print(f'  {flag} {cid}  ({len(text)} → {len(new)} ch)')

if missed:
    print(f'\nMissed {len(missed)}:')
    for cid, text in missed:
        print(f'  {cid}: {text[:300]}')

AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nTrimmed: {trimmed} | Manual: {manual_used} | Missed: {len(missed)}')
