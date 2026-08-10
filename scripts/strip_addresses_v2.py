"""Strip exact street addresses (Vesturbrún 23, Pálsbúð 25, etc.) from
scan-review rewrites, leaving the muni/place name intact.

Patterns handled:
  "búsett(ur)? að <STREET> <NUM>[<LETTER>] (í|á) <PLACE>"  →  "búsett(ur)? (í|á) <PLACE>"
  "býr að <STREET> <NUM>[<LETTER>] (í|á) <PLACE>"         →  "býr (í|á) <PLACE>"
  "býr við <STREET> <NUM>[<LETTER>] (í|á) <PLACE>"        →  "býr (í|á) <PLACE>"
  "með búsetu að <STREET> <NUM>[<LETTER>] (í|á) <PLACE>"  →  "með búsetu (í|á) <PLACE>"
  "[…] búsett(ur)? að <STREET> <NUM>[<LETTER>]." (no place) → drop the address sentence

Anything that matches a non-address pattern (year suffix, "á Stöð 2",
graduation date) is NOT touched because the regex insists on a digit
that's NOT immediately followed by `. mars/apríl/...` or 4-digit year.
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent
AUDIT = ROOT / 'scan_results' / 'audit_results.json'

# Months & "ára" suffix (so "18 ára" / "5. mars 2026" / "1993" don't get matched as addresses)
MONTHS = r'(?:jan|feb|mar|apr|maí|jún|júl|ág|sept|okt|nóv|des)\w*'
NEG_LOOKAHEAD = rf'(?!\d{{2,4}}\b)(?!\s*\.\s*(?:{MONTHS}))(?!\s+ára\b)(?!\s*\.\s+\d{{4}}\b)'

# Street name component: capitalized Icelandic word, optionally hyphenated/multi-word
STREET = r'[A-ZÁÉÍÓÚÝÞÆÖÐ][\wáéíóúýþæöð\-]{2,}(?:\s+[A-ZÁÉÍÓÚÝÞÆÖÐ][\wáéíóúýþæöð\-]+)?'
# Number (1–3 digits), optionally followed by a single letter (e.g. "17 D")
NUM = rf'\d{{1,3}}{NEG_LOOKAHEAD}(?:\s+[A-ZÁÉÍÓÚÝÞÆÖÐ])?'

# Verb stem variants for "lives at"
VERB = r'(?:búsett(?:ur)?|býr|með búsetu|skráð(?:ur)? til heimilis)'
# Address-prefixing prepositions
PREP = r'(?:að|við)'

# Pattern A: full form with trailing place. Replaces with "<verb> <í|á> <place>".
# Capture group 1 = verb segment ; 2 = í/á ; 3 = place phrase
PATTERN_WITH_PLACE = re.compile(
    rf'\b({VERB})\s+{PREP}\s+{STREET}\s+{NUM}\s*,?\s+(í|á)\s+([A-ZÁÉÍÓÚÝÞÆÖÐ][\wáéíóúýþæöð\-]+(?:\s+[\wáéíóúýþæöð\-]+)?)',
    re.IGNORECASE,
)

# Pattern B: trailing address with no place name (typically a sentence end)
# "býr að Freyvangi 9." → drop sentence fragment
PATTERN_NO_PLACE = re.compile(
    rf'\.\s*[A-ZÁÉÍÓÚÝÞÆÖÐ][\wáéíóúýþæöð]+\s+{VERB}\s+{PREP}\s+{STREET}\s+{NUM}\.\s*',
)

# Pattern C: parenthetical "(með búsetu …)" or similar — strip whole parenthetical
PATTERN_PAREN = re.compile(
    rf',?\s*{VERB}\s+{PREP}\s+{STREET}\s+{NUM}\s*,?',
)

bios_in_review = {}
for path in sorted(Path('scan_results').glob('bios_*.json')):
    data = json.load(open(path, encoding='utf-8'))
    for r in data.get('results', []) or []:
        cid = r.get('id')
        if cid: bios_in_review[cid] = r

audit = json.loads(AUDIT.read_text(encoding='utf-8'))

KNOWN_ADDR_IDS = ['HNT.D.8','HMR.D.8','HMR.D.9','HMR.D.10','OLF.D.11','OLF.D.12','OLF.D.13','OLF.S.13',
                  'HFJ.HFJK.11','RTY.D.13','RTY.RYA.13','RTY.D.14','HNT.D.11','HGS.D.1','HGS.HGH.2']

print(f'Processing {len(KNOWN_ADDR_IDS)} entries with known address residues…\n')
modified = 0
for cid in KNOWN_ADDR_IDS:
    a = audit.get(cid)
    if not a:
        print(f'  ⚠ {cid}: no audit entry')
        continue
    rescue = a.setdefault('rescue', {})
    text = (rescue.get('rewrite') or (bios_in_review.get(cid, {}) or {}).get('bio') or '').strip()
    if not text:
        print(f'  ⚠ {cid}: no text')
        continue

    # Try Pattern A first (verb+address+place)
    new_text = PATTERN_WITH_PLACE.sub(lambda m: f'{m.group(1)} {m.group(2)} {m.group(3)}', text)

    if new_text == text:
        # Try Pattern B (no trailing place — drop the sentence)
        new_text = PATTERN_NO_PLACE.sub('. ', text)

    if new_text == text:
        # Try Pattern C (parenthetical/comma-bounded)
        new_text = PATTERN_PAREN.sub('', text)

    new_text = re.sub(r'\s+', ' ', new_text).strip()
    new_text = re.sub(r'\.\s*\.', '.', new_text)
    new_text = re.sub(r'\s+,', ',', new_text)

    if new_text == text:
        print(f'  ✗ {cid}: pattern did not match — REVIEW NEEDED')
        print(f'    {text[:200]}')
        continue

    rescue['rewrite'] = new_text
    rescue['rewrite_words'] = len(new_text.split())
    a['applied'] = False
    audit[cid] = a
    modified += 1
    print(f'  ✓ {cid}  ({len(text)} → {len(new_text)} ch)')
    print(f'    OLD: {text[:200]}')
    print(f'    NEW: {new_text[:200]}')
    print()

AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nUpdated {modified} entries.')
