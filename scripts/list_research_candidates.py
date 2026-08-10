"""Extract candidates needing news research, in population priority order."""
import re

content = open(r'F:\Claude Projects\iceland-elections\js\data\candidates.js', encoding='utf-8').read()

VAR_TO_MUNI = {
    'RVK': 'reykjavik', 'KOP': 'kopavogur', 'HAF': 'hafnarfjordur',
    'RNB': 'reykjanesbaer', 'GAR': 'gardabaer', 'AKU': 'akureyri',
    'MOS': 'mosfellsbaer', 'ARB': 'arborg', 'AKR': 'akranes',
    'MUT': 'mulathing', 'FJD': 'fjardabyggd', 'SEL': 'seltjarnarnes',
    'VME': 'vestmannaeyjar', 'SGN': 'skagafjordur', 'SNB': 'sudurnesjabaer',
    'BBD': 'borgarbyggd', 'ISF': 'isafjordur', 'HVG': 'hveragerdi',
    'NPG': 'nordurping', 'OLF': 'olfus', 'HFJ': 'hornafjordur',
    'RTE': 'rangarthingeystra', 'FJB': 'fjallabyggd', 'RTY': 'rangarthingytra',
    'DVB': 'dalvikurbyggd', 'VOG': 'vogar', 'GRN': 'grindavik',
    'GFJ': 'grundarfjordur', 'SKR': 'skaftarhreppur', 'BLV': 'blaskogabyggd',
    'GGR': 'grimsnes', 'SFJ': 'skeidgnup', 'HMR': 'hrunamannahreppur',
    'FHR': 'flohreppur', 'EJA': 'eyjafjardarsveit', 'HNB': 'horgarsveit',
    'STK': 'strandabyggd', 'SVS': 'skagabyggd', 'THV': 'thingeyjarsyslur',
    'HVF': 'hverfishreppur', 'SNF': 'snafellsbaer', 'VBG': 'vesturbyggd',
    'STD': 'strandir', 'RKH': 'rangarhreppur', 'ARN': 'arneshreppur',
    'KJO': 'kjosarhreppur', 'MYR': 'myrdal', 'HGS': 'hgos', 'SST': 'ssthing',
    'HNT': 'hunaping', 'VPF': 'vatnsnes', 'TJR': 'tjornes',
}

POP_ORDER = [
    'reykjavik','kopavogur','hafnarfjordur','reykjanesbaer','gardabaer','akureyri',
    'mosfellsbaer','arborg','akranes','mulathing','fjardabyggd','seltjarnarnes',
    'vestmannaeyjar','skagafjordur','sudurnesjabaer','borgarbyggd','isafjordur',
    'hveragerdi','nordurping','olfus','hornafjordur','rangarthingeystra',
    'fjallabyggd','rangarthingytra','dalvikurbyggd',
]
seen = set(POP_ORDER)
for muni in VAR_TO_MUNI.values():
    if muni not in seen:
        POP_ORDER.append(muni)
        seen.add(muni)

def depth(muni_id):
    if muni_id == 'reykjavik': return 5
    if muni_id in ('kopavogur', 'hafnarfjordur'): return 3
    if muni_id in ('gardabaer', 'reykjanesbaer'): return 2
    return 1

def extract_balanced(text, start, open_ch, close_ch):
    """Return content between balanced open/close chars starting at start."""
    d = 0
    for i in range(start, len(text)):
        if text[i] == open_ch:
            d += 1
        elif text[i] == close_ch:
            d -= 1
            if d == 0:
                return text[start+1:i]
    return ''

muni_to_var = {v: k for k, v in VAR_TO_MUNI.items()}
cand_pat = re.compile(r"\[\s*(\d+)\s*,\s*'([^']+)'")

results = []
for muni_id in POP_ORDER:
    var = muni_to_var.get(muni_id)
    if not var:
        continue
    d = depth(muni_id)
    # Find the const block for this var
    m = re.search(rf'^const {var}\s*=\s*\{{', content, re.MULTILINE)
    if not m:
        continue
    block_content = extract_balanced(content, m.end() - 1, '{', '}')

    # Find each party sub-block: lines like "  XX: {"
    for pm in re.finditer(r'\n  (\w+)\s*:\s*\{', block_content):
        party = pm.group(1)
        if party in ('tagline', 'agenda', 'platformUrl', 'name', 'list'):
            continue
        party_pos = pm.end() - 1  # position of '{'
        party_content = extract_balanced(block_content, party_pos, '{', '}')

        # Find list: [...]
        lm = re.search(r'\blist\s*:\s*\[', party_content)
        if not lm:
            continue
        list_start = party_content.index('[', lm.start())
        list_content = extract_balanced(party_content, list_start, '[', ']')

        for cm in cand_pat.finditer(list_content):
            seat = int(cm.group(1))
            name = cm.group(2)
            if seat <= d:
                results.append((muni_id, party, seat, name))

print(f'Total: {len(results)}')
for row in results:
    print('\t'.join(str(x) for x in row))
