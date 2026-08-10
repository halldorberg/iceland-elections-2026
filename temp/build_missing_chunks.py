"""For each list without agenda, extract leader name + current heimild/sources
+ FB-page URL if any, then split into 6 chunks for agent research."""
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
data = json.load(open(ROOT / 'temp' / 'coverage_breakdown.json', encoding='utf-8'))
without = data['without_agenda']

CJS = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')

MUNI_NAMES = {
    'reykjavik':'Reykjavík','kopavogur':'Kópavogur','hafnarfjordur':'Hafnarfjörður',
    'gardabaer':'Garðabær','mosfellsbaer':'Mosfellsbær','akureyri':'Akureyri',
    'seltjarnarnes':'Seltjarnarnes','reykjanesbaer':'Reykjanesbær','vogar':'Vogar',
    'grindavik':'Grindavík','sudurnesjabaer':'Suðurnesjabær','arborg':'Árborg',
    'vestmannaeyjar':'Vestmannaeyjar','nordurping':'Norðurþing','fjallabyggd':'Fjallabyggð',
    'fjardabyggd':'Fjarðabyggð','hornafjordur':'Hornafjörður','akranes':'Akranes',
    'borgarbyggd':'Borgarbyggð','isafjordur':'Ísafjarðarbær','hveragerdi':'Hveragerði',
    'rangarthingeystra':'Rangárþing eystra','rangarthingytra':'Rangárþing ytra',
    'olfus':'Sveitarfélagið Ölfus','skaftarhreppur':'Skaftárhreppur','myrdalshr':'Mýrdalshreppur',
    'blaskogabyggd':'Bláskógabyggð','floahreppur':'Flóahreppur',
    'hrunamannahreppur':'Hrunamannahreppur','grimsnesgrafningur':'Grímsnes- og Grafningshreppur',
    'skeidagnup':'Skeiða- og Gnúpverjahreppur','dalvikurbyggd':'Dalvíkurbyggð',
    'eyjafjardarsveit':'Eyjafjarðarsveit','horgarsv':'Hörgársveit','hunabyggd':'Húnabyggð',
    'hunathing':'Húnaþing vestra','skagafjordur':'Skagafjörður','skagastrond':'Sveitarfélagið Skagaströnd',
    'stykkisholmur':'Sveitarfélagið Stykkishólmur','grundarfjordur':'Grundarfjörður','bolungarvik':'Bolungarvík',
    'sudavik':'Súðavíkurhreppur','vesturbyggd':'Vesturbyggð','strandabyggd':'Strandabyggð',
    'reykholar':'Reykhólahreppur','mulathing':'Múlaþing','thingeyjarsveit':'Þingeyjarsveit',
    'hvalfjardarsveit':'Hvalfjarðarsveit','snaefellsbaer':'Snæfellsbær',
    'svalbardsstrond':'Svalbarðsstrandarhreppur','kjosarhreppur':'Kjósarhreppur',
    'vopnafjordur':'Vopnafjarðarhreppur','tjornes':'Tjörneshreppur','arneshr':'Árneshreppur',
}

def find_const_block(src, const):
    m = re.search(r'^const ' + re.escape(const) + r'\s*=\s*\{', src, re.M)
    if not m: return None
    open_pos = m.end() - 1
    depth=0; i=open_pos
    while i < len(src):
        c=src[i]
        if c in ("'", '"', '`'):
            q=c; i+=1
            while i<len(src):
                if src[i]=='\\': i+=2; continue
                if src[i]==q: i+=1; break
                i+=1
            continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: return open_pos+1, i
        i+=1

def get_party(const, code):
    span = find_const_block(CJS, const)
    if not span: return None
    bs, be = span
    pat = re.compile(r'\n  ' + re.escape(code) + r'\s*:\s*\{')
    m = pat.search(CJS, bs, be)
    if not m: return None
    i = m.end() - 1; depth=0; in_str=None
    while i<be:
        c=CJS[i]
        if in_str:
            if c=='\\': i+=2; continue
            if c==in_str: in_str=None
            i+=1; continue
        if c in ("'",'"','`'): in_str=c; i+=1; continue
        if c=='{': depth+=1
        elif c=='}':
            depth-=1
            if depth==0: break
        i+=1
    return CJS[m.end()-1:i+1]

enriched = []
for muni_id, const, code, tagline in without:
    block = get_party(const, code) or ''
    # leader name from first row
    nm = re.search(r"\[\s*1\s*,\s*'([^']+)'", block)
    leader = nm.group(1) if nm else ''
    leader_occ = ''
    nm2 = re.search(r"\[\s*1\s*,\s*'[^']+',\s*'([^']+)'", block)
    if nm2: leader_occ = nm2.group(1)
    # existing platformUrl (if any, but these all lack agendas)
    pu = re.search(r"platformUrl:\s*'([^']+)'", block)
    plat = pu.group(1) if pu else ''
    # any FB/heimild URLs in the first few candidates
    urls = list(set(re.findall(r"url:\s*'(https?://[^']+)'", block[:8000])))
    # First 5 candidates names (helpful for searching specifically)
    names = re.findall(r"\[\s*\d+\s*,\s*'([^']+)'", block)[:5]
    enriched.append({
        'muni_id': muni_id, 'muni_name': MUNI_NAMES.get(muni_id, muni_id),
        'const': const, 'code': code, 'tagline': tagline,
        'leader': leader, 'leader_occ': leader_occ,
        'top5_names': names, 'sources_in_data': urls[:6],
    })

# Sort by muni name then code
enriched.sort(key=lambda x: (x['muni_name'], x['code']))

# Split into 6 chunks
N = 6
chunks = [enriched[i::N] for i in range(N)]
for i, ch in enumerate(chunks):
    json.dump(ch, open(ROOT / 'temp' / f'missing_agenda_chunk_{i:02d}.json','w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'  chunk_{i:02d}.json: {len(ch)} lists')
print(f'\nTotal: {len(enriched)} across {N} chunks')
