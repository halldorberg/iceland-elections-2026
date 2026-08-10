"""Re-merge Vinir Mos draft bios in ruv_bios.json with the new vinirmos facts."""
import json, sys, io, os, re
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
env = ROOT / '.env'
if env.exists():
    for line in env.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI
client = OpenAI()
MODEL = 'gpt-5.4'

# Load existing ruv_bios
ruv = json.load(open(ROOT / 'scan_results' / 'ruv_bios.json', encoding='utf-8'))

# Load RÚV background-question data (has the original answers)
ruv_answers = json.load(open(ROOT / 'temp' / 'ruv_answers.json', encoding='utf-8'))
answers_by_id = {c['id']: c for c in ruv_answers['candidates']}

# Load current candidates.js to extract the new vinirmos bio
CJS = (ROOT / 'js' / 'data' / 'candidates.js').read_text(encoding='utf-8')

def get_current_bio(muni_const, party_code, ballot):
    m = re.search(r'^const ' + re.escape(muni_const) + r' = \{', CJS, re.M)
    if not m: return None, []
    start = m.end()
    pm = re.search(r'\n  ' + re.escape(party_code) + r'\s*:\s*\{', CJS[start:])
    if not pm: return None, []
    ps = start + pm.end()
    rm = re.search(r'\n      \[' + str(ballot) + r'\s*,', CJS[ps:])
    if not rm: return None, []
    pos = ps + rm.start()
    # walk to row close ]
    bracket_pos = CJS.find('[', pos)
    depth = 0; i = bracket_pos; in_str = None
    while i < len(CJS):
        c = CJS[i]
        if in_str:
            if c=='\\': i+=2; continue
            if c==in_str: in_str=None
            i+=1; continue
        if c in ("'",'"','`'): in_str=c; i+=1; continue
        if c=='[': depth+=1
        elif c==']':
            depth-=1
            if depth==0: break
        i+=1
    row = CJS[bracket_pos:i+1]
    bio_m = re.search(r"bio:\s*'((?:[^'\\\\]|\\\\.)*)'", row)
    bio = bio_m.group(1).replace("\\'","'").replace('\\\\','\\') if bio_m else None
    h_m = re.search(r"heimild:\s*\[((?:[^\[\]]|\[[^\]]*\])*)\]", row)
    heimild = []
    if h_m:
        for hu in re.finditer(r"\{\s*url:\s*'((?:[^'\\\\]|\\\\.)*)'\s*,\s*label:\s*'((?:[^'\\\\]|\\\\.)*)'\s*\}", h_m.group(1)):
            heimild.append({'url': hu.group(1), 'label': hu.group(2)})
    return bio, heimild

SYS = """Þú ert að taka saman æviágrip um íslenskan sveitarstjórnarframbjóðanda. Sameinaðu (a) núverandi æviágrip — ALLT efni þess þarf að vera áfram — við (b) nýjar staðreyndir úr svörum frambjóðandans á kosningaprófi RÚV. Skrifaðu samfellt í þriðju persónu á íslensku, 250–400 orð, í 2–4 málsgreinum. Notaðu fullt nafn í fyrstu setningu, eftir það "hann" eða "hún". Ekki finna upp staðreyndir.

Skilaðu JSON með nákvæmlega þessari skipan:
{
  "new_bio": "<merged paragraph(s)>",
  "fact_check": [
    {
      "statement": "<orðrétt setning úr nýja æviágripinu sem byggist á NÝJU efni úr RÚV>",
      "ruv_quote": "<beint orðrétta tilvitnun úr RÚV-svari sem styður þessa setningu>"
    }
  ]
}

fact_check skal aðeins innihalda nýjar staðreyndir sem koma úr RÚV (ekki úr gamla æviágripinu). Hver tilvitnun orðrétt eins og í RÚV svarinu."""

def build_user(name, muni_name, party_name, current_bio, ruv_bg):
    lines = [f'Frambjóðandi: {name}', f'Sveitarfélag: {muni_name}', f'Listi: {party_name}', '']
    lines.append('Núverandi æviágrip:')
    lines.append(current_bio)
    lines.append('')
    lines.append('Svör á kosningaprófi RÚV:')
    for q in ruv_bg:
        label = (q.get('label') or '').strip()
        value = (q.get('value') or '').strip()
        if value:
            lines.append(f'  • {label}  →  {value}')
    return '\n'.join(lines)

# Find Vinir Mos entries
updated = 0
for entry in ruv:
    if entry.get('muni_const') != 'MOS' or entry.get('party_code') != 'L':
        continue
    ballot = entry['ballot']
    name = entry['name']
    # Get the current vinirmos bio from candidates.js
    cur_bio, cur_heimild = get_current_bio('MOS', 'L', ballot)
    if not cur_bio:
        print(f'  [{ballot}] {name}: no current bio — skip')
        continue
    # RÚV background
    ruv_blob = answers_by_id.get(entry['ruv_id'])
    if not ruv_blob:
        print(f'  [{ballot}] {name}: no RÚV data — skip')
        continue
    bg = ruv_blob.get('backgroundQuestion', [])
    user = build_user(name, 'Mosfellsbær', 'L-listinn (Vinir Mosfellsbæjar)', cur_bio, bg)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{'role':'system','content':SYS},{'role':'user','content':user}],
            response_format={'type':'json_object'},
        )
        data = json.loads(resp.choices[0].message.content)
        # Update entry: new bio, fact_check, sources
        entry['old_bio'] = cur_bio  # the new "old" baseline is the vinirmos bio
        entry['new_bio'] = data.get('new_bio')
        entry['fact_check'] = data.get('fact_check', [])
        # Sources: union of cur_heimild + RÚV profile URL
        sources = list(cur_heimild)
        ruv_url = entry.get('ruv_profile_url')
        if ruv_url and not any(s.get('url') == ruv_url for s in sources):
            sources.append({'url': ruv_url, 'label': 'RÚV kosningapróf'})
        entry['sources'] = sources
        updated += 1
        print(f'  [{ballot}] {name}: updated ({len(data.get("new_bio",""))} chars, {len(data.get("fact_check",[]))} facts)')
    except Exception as e:
        print(f'  [{ballot}] {name}: ERR {e}')

# Save
json.dump(ruv, open(ROOT / 'scan_results' / 'ruv_bios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\nUpdated {updated} entries in ruv_bios.json')
