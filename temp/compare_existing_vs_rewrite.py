"""For each approved ID, find the existing bio in candidates.js (if any) and
compare it to the proposed rewrite. Flag rows that need manual merging."""
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
src = open(ROOT / 'js' / 'data' / 'candidates.js', encoding='utf-8').read()

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

# Map muniId(slug for url) to const name
MUNI_TO_CONST = {
    'reykjavik':'RVK','kopavogur':'KOP','hafnarfjordur':'HAF','gardabaer':'GAR',
    'mosfellsbaer':'MOS','akureyri':'AKU','seltjarnarnes':'SEL','reykjanesbaer':'RNB',
    'vogar':'VOG','grindavik':'GRN','sudurnesjabaer':'SNB','arborg':'ARB',
    'vestmannaeyjar':'VME','nordurping':'NPG','fjallabyggd':'FJB','fjardabyggd':'FJD',
    'hornafjordur':'HFJ','akranes':'AKR','borgarbyggd':'BBD','isafjordur':'ISF',
    'hveragerdi':'HVG','rangarthingeystra':'RTE','rangarthingytra':'RTY','olfus':'OLF',
    'skaftarhreppur':'SKR','myrdalshr':'MYR','blaskogabyggd':'BSG','floahreppur':'FHR',
    'hrunamannahreppur':'HMR','grimsnesgrafningur':'GGR','skeidagnup':'SGN',
    'dalvikurbyggd':'DVB','eyjafjardarsveit':'EJA','horgarsv':'HGS','hunabyggd':'HNB',
    'hunathing':'HNT','skagafjordur':'SFJ','skagastrond':'SST','stykkisholmur':'STK',
    'grundarfjordur':'GFJ','bolungarvik':'BLV','sudavik':'SDV','vesturbyggd':'VBG',
    'strandabyggd':'STD','reykholar':'RKH','mulathing':'MUT','thingeyjarsveit':'THV',
    'hvalfjardarsveit':'HVF','snaefellsbaer':'SNF','svalbardsstrond':'SVS',
    'kjosarhreppur':'KJO','vopnafjordur':'VPF','tjornes':'TJR','arneshr':'ARN',
}

# Approved IDs are like AKR.D.10  -> const=AKR, party=D, ballot=10
# Already aligned: "muniConst.partyCode.ballot"

def find_row(src, const_name, party_code, ballot):
    span = find_const_block(src, const_name)
    if not span:
        return None
    body_start, body_end = span
    pat = re.compile(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{')
    pm = pat.search(src, body_start, body_end)
    if not pm:
        return None
    party_close = src.find('\n  }', pm.end(), body_end)
    if party_close == -1:
        party_close = body_end
    # Find row [ballot, '...
    row_pat = re.compile(r'\n      \[\s*' + str(ballot) + r'\s*,')
    rm = row_pat.search(src, pm.end(), party_close)
    if not rm:
        return None
    # Walk to matching ]
    i = rm.end() - 1  # at ,
    # Actually start from the [ position
    bracket_start = src.rfind('[', pm.end(), rm.end())
    i = bracket_start
    depth = 0
    n = len(src)
    while i < n:
        c = src[i]
        if c in ("'", '"', '`'):
            q = c; i += 1
            while i < n:
                if src[i] == '\\': i += 2; continue
                if src[i] == q: i += 1; break
                i += 1
            continue
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return src[bracket_start:i+1]
        i += 1
    return None

# Extract bio text from a row string
def extract_bio(row_text):
    # Look for bio: '...'
    m = re.search(r"bio:\s*('[^']*(?:\\.[^']*)*'|null)", row_text, re.S)
    if not m:
        return None
    raw = m.group(1)
    if raw == 'null':
        return None
    # Remove surrounding quotes and unescape
    s = raw[1:-1].replace("\\'", "'").replace('\\\\', '\\').replace('\\n', '\n')
    return s

def extract_bio_v2(row_text):
    """Bio might be wrapped over multiple lines. Use bio: '...' until ', heimild' or another field."""
    m = re.search(r"bio:\s*'((?:[^'\\]|\\.)*)'", row_text, re.S)
    if m:
        return m.group(1).replace("\\'", "'").replace('\\\\', '\\')
    m = re.search(r'bio:\s*null', row_text)
    if m:
        return None
    return None

approved = json.load(open(ROOT / 'temp' / 'approved_resolved.json', encoding='utf-8'))
print(f'approved entries: {len(approved)}')

results = {'has_existing_longer': [], 'has_existing_short_or_eq': [], 'no_existing': [], 'no_rewrite': [], 'unmapped': []}

for aid, data in approved.items():
    parts = aid.split('.')
    if len(parts) != 3:
        results['unmapped'].append((aid, 'bad id'))
        continue
    const_name, party_code, ballot_s = parts
    try:
        ballot = int(ballot_s)
    except:
        results['unmapped'].append((aid, 'bad ballot'))
        continue
    row = find_row(src, const_name, party_code, ballot)
    if not row:
        results['unmapped'].append((aid, 'row not found'))
        continue
    existing = extract_bio_v2(row)
    entry = data['entry']
    rescue = entry.get('rescue') or entry.get('rewrite_payload') or {}
    rewrite = rescue.get('rewrite') or entry.get('rewrite') or entry.get('new_bio') or entry.get('bio')
    if not rewrite:
        results['no_rewrite'].append(aid)
        continue
    if existing is None:
        results['no_existing'].append(aid)
        continue
    el = len(existing)
    rl = len(rewrite)
    if el > rl + 50:  # existing meaningfully longer than rewrite
        results['has_existing_longer'].append({'id': aid, 'existing_len': el, 'rewrite_len': rl, 'existing': existing[:300], 'rewrite': rewrite[:300]})
    else:
        results['has_existing_short_or_eq'].append(aid)

for k, v in results.items():
    print(f'\n{k}: {len(v)}')
    if k == 'has_existing_longer':
        for r in v:
            print(f'  {r["id"]}  existing={r["existing_len"]}  rewrite={r["rewrite_len"]}')
    else:
        for it in v[:25]:
            print(f'  {it}')

json.dump(results, open(ROOT / 'temp' / 'compare_results.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('\nDetails in temp/compare_results.json')
