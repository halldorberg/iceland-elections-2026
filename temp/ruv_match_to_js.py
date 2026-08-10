"""Match every RÚV kosningapróf candidate to a row in candidates.js.

Output: temp/ruv_to_js_mapping.json
  [
    {
      "ruv_id": "2505-B-17",
      "ruv_name": "Haraldur Hinriksson",
      "muni_const": "SNB",
      "party_code": "B",
      "ballot": 17,
      "match_status": "matched" | "no_muni" | "no_row",
      "existing_bio": "...",
      "existing_heimild": [...]
    },
    ...
  ]
"""
import json, re, sys, io, os, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'F:\Claude Projects\iceland-elections'

# Map RÚV constituency name (Icelandic) -> candidates.js const name.
# Built from MUNICIPALITIES + REAL_DATA mapping.
RUV_MUNI_TO_CONST = {
    'Reykjavíkurborg': 'RVK',
    'Reykjavík': 'RVK',
    'Kópavogur': 'KOP',
    'Hafnarfjarðarkaupstaður': 'HAF',
    'Hafnarfjörður': 'HAF',
    'Garðabær': 'GAR',
    'Mosfellsbær': 'MOS',
    'Akureyrarbær': 'AKU',
    'Akureyri': 'AKU',
    'Seltjarnarnesbær': 'SEL',
    'Seltjarnarnes': 'SEL',
    'Reykjanesbær': 'RNB',
    'Sveitarfélagið Vogar': 'VOG',
    'Vogar': 'VOG',
    'Grindavíkurbær': 'GRN',
    'Grindavík': 'GRN',
    'Suðurnesjabær': 'SNB',
    'Sveitarfélagið Árborg': 'ARB',
    'Árborg': 'ARB',
    'Vestmannaeyjabær': 'VME',
    'Vestmannaeyjar': 'VME',
    'Norðurþing': 'NPG',
    'Fjallabyggð': 'FJB',
    'Fjarðabyggð': 'FJD',
    'Sveitarfélagið Hornafjörður': 'HFJ',
    'Hornafjörður': 'HFJ',
    'Akraneskaupstaður': 'AKR',
    'Akranes': 'AKR',
    'Borgarbyggð': 'BBD',
    'Ísafjarðarbær': 'ISF',
    'Ísafjörður': 'ISF',
    'Hveragerðisbær': 'HVG',
    'Hveragerði': 'HVG',
    'Rangárþing eystra': 'RTE',
    'Rangárþing ytra': 'RTY',
    'Sveitarfélagið Ölfus': 'OLF',
    'Ölfus': 'OLF',
    'Skaftárhreppur': 'SKR',
    'Mýrdalshreppur': 'MYR',
    'Bláskógabyggð': 'BSG',
    'Flóahreppur': 'FHR',
    'Hrunamannahreppur': 'HMR',
    'Grímsnes- og Grafningshreppur': 'GGR',
    'Skeiða- og Gnúpverjahreppur': 'SGN',
    'Dalvíkurbyggð': 'DVB',
    'Eyjafjarðarsveit': 'EJA',
    'Hörgársveit': 'HGS',
    'Húnabyggð': 'HNB',
    'Húnaþing vestra': 'HNT',
    'Skagafjörður': 'SFJ',
    'Sveitarfélagið Skagaströnd': 'SST',
    'Skagaströnd': 'SST',
    'Stykkishólmsbær': 'STK',
    'Stykkishólmur': 'STK',
    'Sveitarfélagið Stykkishólmur': 'STK',
    'Grundarfjarðarbær': 'GFJ',
    'Grundarfjörður': 'GFJ',
    'Bolungarvíkurkaupstaður': 'BLV',
    'Bolungarvík': 'BLV',
    'Súðavíkurhreppur': 'SDV',
    'Vesturbyggð': 'VBG',
    'Strandabyggð': 'STD',
    'Reykhólahreppur': 'RKH',
    'Múlaþing': 'MUT',
    'Þingeyjarsveit': 'THV',
    'Hvalfjarðarsveit': 'HVF',
    'Snæfellsbær': 'SNF',
    'Svalbarðsstrandarhreppur': 'SVS',
    'Kjósarhreppur': 'KJO',
    'Vopnafjarðarhreppur': 'VPF',
    'Tjörneshreppur': 'TJR',
    'Árneshreppur': 'ARN',
}

def normalize_name(s):
    if not s:
        return ''
    s = unicodedata.normalize('NFC', s).lower()
    s = re.sub(r'\s+', ' ', s).strip()
    s = s.replace('.', '').replace(',', '').replace('-', ' ')
    return s

def name_tokens(s):
    n = normalize_name(s)
    # drop single-letter middle initials
    return [t for t in n.split() if len(t) > 1]

def fuzzy_name_match(a, b):
    """Match if first names match and last names match by prefix or full."""
    ta = name_tokens(a)
    tb = name_tokens(b)
    if not ta or not tb:
        return False
    # First-name comparison
    if ta[0] != tb[0]:
        return False
    # Last token: allow truncation (one is prefix of the other) or equality
    last_a, last_b = ta[-1], tb[-1]
    if last_a == last_b:
        # Verify all tokens overlap loosely
        return set(ta) & set(tb) >= {ta[0], last_a}
    if last_a.startswith(last_b) or last_b.startswith(last_a):
        # Prefix — likely truncation
        if min(len(last_a), len(last_b)) >= 4:
            return True
    # Try checking middle tokens
    if set(ta[:2]) == set(tb[:2]):
        return True
    return False

# Load candidates.js to extract rows
src = open(os.path.join(ROOT, 'js', 'data', 'candidates.js'), encoding='utf-8').read()

def find_const_block(src, const_name):
    m = re.search(r'^const ' + re.escape(const_name) + r'\s*=\s*\{', src, re.M)
    if not m:
        return None
    open_pos = m.end() - 1
    depth = 0
    i = open_pos
    n = len(src)
    while i < n:
        c = src[i]
        if c == '/' and i+1 < n and src[i+1] == '/':
            i = src.find('\n', i+2); i = i if i != -1 else n; continue
        if c == '/' and i+1 < n and src[i+1] == '*':
            j = src.find('*/', i+2); i = (j+2) if j != -1 else n; continue
        if c in ("'", '"', '`'):
            q = c; i += 1
            while i < n:
                if src[i] == '\\': i += 2; continue
                if src[i] == q: i += 1; break
                i += 1
            continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return open_pos+1, i
        i += 1
    return None

def party_blocks(src, const_name):
    span = find_const_block(src, const_name)
    if not span:
        return {}
    body_start, body_end = span
    parties = {}
    pat = re.compile(r'\n  ([A-Z][A-Za-z0-9_]*)\s*:\s*\{')
    for pm in pat.finditer(src, body_start, body_end):
        code = pm.group(1)
        if code in ('list', 'tagline', 'agenda', 'platformUrl'):
            continue
        # find matching close
        i = pm.end() - 1  # at {
        depth = 0
        in_str = None
        n = body_end
        while i < n:
            c = src[i]
            if in_str:
                if c == '\\': i += 2; continue
                if c == in_str: in_str = None
                i += 1; continue
            if c in ("'", '"', '`'):
                in_str = c; i += 1; continue
            if c == '{': depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        parties[code] = (pm.end()-1, i+1)
    return parties

def extract_rows(src, const_name, party_code):
    parties = party_blocks(src, const_name)
    if party_code not in parties:
        return {}
    block_start, block_end = parties[party_code]
    rows = {}
    # Walk top-level [ at indent 6
    i = block_start
    while i < block_end:
        # Look for newline + 6 spaces + [
        j = src.find('\n      [', i, block_end)
        if j == -1:
            break
        bracket_pos = j + len('\n      ')
        # walk to matching ]
        depth = 0
        k = bracket_pos
        in_str = None
        while k < block_end:
            c = src[k]
            if in_str:
                if c == '\\': k += 2; continue
                if c == in_str: in_str = None
                k += 1; continue
            if c in ("'", '"', '`'):
                in_str = c; k += 1; continue
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0: break
            k += 1
        row_text = src[bracket_pos:k+1]
        # Parse [N, 'Name', ...]
        m_ballot = re.match(r"\[\s*(\d+)\s*,\s*'((?:[^'\\]|\\.)*)'", row_text)
        if m_ballot:
            ballot = int(m_ballot.group(1))
            name = m_ballot.group(2).replace("\\'", "'").replace('\\\\', '\\')
            # Extract bio
            bm = re.search(r"bio:\s*'((?:[^'\\]|\\.)*)'", row_text)
            bio = None
            if bm:
                bio = bm.group(1).replace("\\'", "'").replace('\\\\', '\\')
            elif re.search(r'bio:\s*null', row_text):
                bio = None
            # Extract heimild raw
            hm = re.search(r"heimild:\s*\[((?:.|\n)*?)\]\s*,?\s*(?=interests|social|news|\}|$)", row_text)
            heimild_raw = hm.group(1) if hm else ''
            heimild = []
            for hu in re.finditer(r"\{\s*url:\s*'((?:[^'\\]|\\.)*)'\s*,\s*label:\s*'((?:[^'\\]|\\.)*)'\s*\}", heimild_raw):
                heimild.append({'url': hu.group(1), 'label': hu.group(2)})
            rows[ballot] = {'name': name, 'bio': bio, 'heimild': heimild, 'row_text': row_text[:50]}
        i = k + 1
    return rows

# Load RÚV candidates
ruv = json.load(open(os.path.join(ROOT, 'temp', 'ruv_answers.json'), encoding='utf-8'))
ruv_cands = ruv.get('candidates', [])
print(f'RÚV candidates: {len(ruv_cands)}')

# For each RÚV candidate, look up the row
mapping = []
matched = 0
no_muni = 0
no_party = 0
no_row = 0
name_mismatch = 0
ambig_party = 0

# Cache rows by (const, party_code)
rows_cache = {}

for c in ruv_cands:
    muni_name = c.get('constituencyName', '')
    party_abbr = c.get('partyAbbreviation', '')
    ballot = c.get('partyListPosition')
    name = c.get('fullName', '')
    ruv_id = c.get('id')

    const_name = RUV_MUNI_TO_CONST.get(muni_name)
    if not const_name:
        no_muni += 1
        mapping.append({'ruv_id': ruv_id, 'ruv_name': name, 'muni_name': muni_name, 'party_abbr': party_abbr, 'ballot': ballot, 'match_status': 'no_muni'})
        continue

    # Find candidates.js party that matches party_abbr
    parties = party_blocks(src, const_name)
    candidate_party_codes = []
    if party_abbr in parties:
        candidate_party_codes.append(party_abbr)
    else:
        # try local-list codes (e.g. THVA, SCS, BSP etc.) — look for ones that match by ballot+name later
        candidate_party_codes = list(parties.keys())

    found = None
    for pc in candidate_party_codes:
        cache_key = (const_name, pc)
        if cache_key not in rows_cache:
            rows_cache[cache_key] = extract_rows(src, const_name, pc)
        rows = rows_cache[cache_key]
        if ballot in rows:
            row = rows[ballot]
            if normalize_name(row['name']) == normalize_name(name) or fuzzy_name_match(row['name'], name):
                found = (pc, row)
                break

    if not found:
        # Fallback: name-only match across all party codes for this muni
        for pc in parties.keys():
            cache_key = (const_name, pc)
            if cache_key not in rows_cache:
                rows_cache[cache_key] = extract_rows(src, const_name, pc)
            rows = rows_cache[cache_key]
            for b, row in rows.items():
                if normalize_name(row['name']) == normalize_name(name) or fuzzy_name_match(row['name'], name):
                    found = (pc, row)
                    ballot = b
                    break
            if found:
                break

    if found:
        pc, row = found
        matched += 1
        mapping.append({
            'ruv_id': ruv_id, 'ruv_name': name, 'muni_name': muni_name,
            'muni_const': const_name, 'party_abbr': party_abbr, 'party_code_in_js': pc,
            'ballot': ballot,
            'js_name': row['name'], 'existing_bio': row['bio'], 'existing_heimild': row['heimild'],
            'match_status': 'matched',
        })
    else:
        no_row += 1
        mapping.append({
            'ruv_id': ruv_id, 'ruv_name': name, 'muni_name': muni_name,
            'muni_const': const_name, 'party_abbr': party_abbr, 'ballot': ballot,
            'match_status': 'no_row',
        })

print(f'\nmatched: {matched}')
print(f'no_muni:  {no_muni}')
print(f'no_row:   {no_row}')

# Sample failures
print('\nSample no_muni:')
for m in mapping:
    if m['match_status'] == 'no_muni':
        print(' ', m['ruv_name'], '|', m['muni_name'])
        if [x for x in mapping if x['match_status']=='no_muni'].index(m) >= 6: break

print('\nSample no_row:')
shown = 0
for m in mapping:
    if m['match_status'] == 'no_row':
        print(' ', m['ruv_name'], f'-> {m["muni_const"]}.{m["party_abbr"]}.{m["ballot"]}', f'({m["muni_name"]})')
        shown += 1
        if shown >= 10: break

json.dump(mapping, open(os.path.join(ROOT, 'temp', 'ruv_to_js_mapping.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print(f'\nWrote temp/ruv_to_js_mapping.json with {len(mapping)} entries')
