"""Recover party_code values in ruv_bios.json by matching
   (muni_const, ballot_letter_from_ruv_id) to candidates.js party blocks.

   Strategy: for each muni_const, scan its const block in candidates.js for
   party sub-keys. Each party has a tagline that mentions its ballot letter
   ("A-listi", "B-listi", etc.). Build a (muni_const, ballot_letter) ->
   party_code map. Then for each ruv_bios entry, if its party_code is just
   the ballot letter (single char), look it up in the map and replace with
   the proper candidates.js key."""
import json, re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
CJS = ROOT / 'js' / 'data' / 'candidates.js'
RUV = ROOT / 'scan_results' / 'ruv_bios.json'

src = CJS.read_text(encoding='utf-8')


def find_const_block(s, name):
    m = re.search(r'^const ' + re.escape(name) + r'\s*=\s*\{', s, re.M)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    in_str = None
    while i < len(s):
        c = s[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue
        if c in ("'", '"', '`'):
            in_str = c
            i += 1
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return open_pos + 1, i
        i += 1


# Get all muni constants and the parties inside them
real_data_m = re.search(r"const REAL_DATA\s*=\s*\{([^}]+)\}", src)
muni_consts = []
for pm in re.finditer(r'(\w+):\s*([A-Z][A-Z0-9_]*)', real_data_m.group(1)):
    muni_consts.append(pm.group(2))

# For each muni const, find parties and try to detect their ballot letter
# from the tagline or first row.
muni_party_letter = {}  # (muni_const, letter) -> party_key
party_letter_of = {}    # (muni_const, party_key) -> letter

for muni in muni_consts:
    rng = find_const_block(src, muni)
    if not rng:
        continue
    cs, ce = rng
    body = src[cs:ce]
    for pm in re.finditer(r'\n  ([A-Z][A-Z0-9]*)\s*:\s*\{', body):
        party = pm.group(1)
        if party == 'DEFAULT_AGENDAS':
            continue
        # Find party block end
        i = pm.end() - 1
        depth = 0
        in_str = None
        while i < len(body):
            c = body[i]
            if in_str:
                if c == '\\':
                    i += 2
                    continue
                if c == in_str:
                    in_str = None
                i += 1
                continue
            if c in ("'", '"', '`'):
                in_str = c
                i += 1
                continue
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        ptext = body[pm.end() - 1:i + 1]

        # Try to extract ballot letter from tagline or list
        # Pattern 1: tagline mentions "X-lista" / "X-listi" / "X-listinn"
        tag_m = re.search(r"tagline:\s*'([^']{1,200})'", ptext)
        letter = None
        if tag_m:
            tl = tag_m.group(1)
            lm = re.search(r'\b([A-ZÁÉÍÓÚÝÞÆÖ])-list', tl)
            if lm:
                letter = lm.group(1)
        # Fallback: the party key itself if it's a single uppercase letter
        if not letter and len(party) == 1 and party.isupper():
            letter = party
        # Fallback: first letter of the party key (most "MYA" → A, "MYZ" → Z, "BBK" → B?)
        # NOPE — that's unreliable. Skip.

        if letter:
            muni_party_letter[(muni, letter)] = party
            party_letter_of[(muni, party)] = letter

print(f'Built {len(muni_party_letter)} (muni, letter) → party_code mappings')

# Now load ruv_bios.json and fix party_code
data = json.load(open(RUV, encoding='utf-8'))
fixed = 0
unmatched = []
for e in data:
    rid = e.get('ruv_id', '') or ''
    parts = rid.split('-')
    if len(parts) != 3:
        continue
    muni_short, letter, ballot_str = parts
    muni = e.get('muni_const')
    pc = e.get('party_code')
    # If party_code is the SHORT letter (likely corrupted), look up the real one
    if pc == letter and (muni, letter) in muni_party_letter:
        new_pc = muni_party_letter[(muni, letter)]
        if new_pc != pc:
            e['party_code'] = new_pc
            fixed += 1

print(f'Recovered party_code for {fixed} entries')

json.dump(data, open(RUV, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Wrote ruv_bios.json')
