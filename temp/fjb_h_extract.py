"""Extract FJB.H existing bios + clean kynning texts for merging."""
import re, json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
JS = ROOT / 'js' / 'data' / 'candidates.js'
KYNN_DIR = ROOT / 'temp' / 'hlistinn_fjb'

src = JS.read_text(encoding='utf-8')

# Find FJB.H block
m = re.search(r'const FJB\s*=\s*\{', src)
i = m.end() - 1; d = 0
while i < len(src):
    c = src[i]
    if c == '{': d += 1
    elif c == '}':
        d -= 1
        if d == 0: break
    i += 1
fjb = src[m.end()-1:i+1]

hm = re.search(r'\n  H:\s*\{', fjb)
j = hm.end() - 1; d2 = 0; ins = None
while j < len(fjb):
    c = fjb[j]
    if ins:
        if c == '\\': j += 2; continue
        if c == ins: ins = None
        j += 1; continue
    if c in ("'", '"', '`'): ins = c; j += 1; continue
    if c == '{': d2 += 1
    elif c == '}':
        d2 -= 1
        if d2 == 0: break
    j += 1
hb = fjb[hm.end()-1:j+1]

# (seat, kynning_filename)
KYNN_MAP = {
    1:  'Kynning_1_Helgi.txt',
    2:  'Kynning_2_Kristinn.txt',
    3:  'Kynning_3_Asgeir_Logi.txt',
    4:  'Kynning_4_Audur_Osp.txt',
    5:  'Kynning_5_Gudlaugur_Magnus.txt',
    6:  'Kynning_6_Thorfinna_Ellen.txt',
    7:  'Kynning_7_Thorgeir.txt',
    8:  'Kynning_8_Klara_Mist.txt',
    9:  'Kynning_9_Jon_Valgeir.txt',
    10: 'Kynning_10_Andri_Vidar.txt',
    11: 'Kynning_11_Adalbjorg.txt',
    13: 'Kynning_13_Katrin.txt',
    14: 'Kynning_14_Arni_Helgason.txt',
}

# Strip Drive viewer chrome (top menu + page footer)
CHROME_LINES = {
    'File', 'View', 'Insert', 'Tools', 'Help',
    'Open with Google Docs', 'Share', 'Page', '/',
    '1', '2', '3',
    'Download', 'Print', 'Printing not yet available',
    'Zoom out', 'Zoom in', 'Comment', 'Hide file header',
    'Page 1 of 1', 'Page 2 of 2', 'Page 1 of 2', '',
}

def clean_kynning(text):
    lines = text.split('\n')
    out = []
    for ln in lines:
        s = ln.strip()
        if not s: continue
        if s in CHROME_LINES: continue
        if s.startswith('Kynning ') and s.endswith('.docx'): continue
        if s.startswith('Displaying '): continue
        if s.startswith('Page ') and 'of' in s: continue
        if re.match(r'^Page \d+ of \d+$', s): continue
        out.append(s)
    joined = ' '.join(out).strip()
    # Collapse multi-space
    joined = re.sub(r'\s+', ' ', joined)
    return joined


def extract_seat_bio(seat, name):
    p = re.compile(
        r"\[" + str(seat) + r",\s*'" + re.escape(name) + r"'.*?bio:\s*'((?:[^'\\]|\\.)+)'", re.S)
    mm = p.search(hb)
    if mm:
        return mm.group(1).replace('\\n', '\n').replace("\\'", "'")
    return None


NAMES = {
    1:  'Helgi Jóhannsson',
    2:  'Kristinn Kristjánsson',
    3:  'Ásgeir Logi Ásgeirsson',
    4:  'Auður Ösp H. Magnúsdóttir',
    5:  'Guðlaugur Magnús Ingason',
    6:  'Þorfinna Þrastardóttir',
    7:  'Þorgeir Bjarnason',
    8:  'Klara Mist Pálsdóttir',
    9:  'Jón Valgeir Baldursson',
    10: 'Andri Viðar Víglundsson',
    11: 'Aðalbjörg Snorradóttir',
    13: 'Katrín Freysdóttir',
    14: 'Árni Helgason',
}

data = []
for seat, fn in KYNN_MAP.items():
    name = NAMES[seat]
    bio = extract_seat_bio(seat, name) or ''
    kyn_path = KYNN_DIR / fn
    kyn_clean = clean_kynning(kyn_path.read_text(encoding='utf-8')) if kyn_path.exists() else ''
    data.append({
        'seat': seat,
        'name': name,
        'existing_bio': bio,
        'kynning_clean': kyn_clean,
    })

out = ROOT / 'temp' / 'fjb_h_merge_input.json'
out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {out}')
print(f'Entries: {len(data)}')
for d in data:
    print(f"  seat {d['seat']:>2}  {d['name']:<35}  bio={len(d['existing_bio'])} chars, kyn={len(d['kynning_clean'])} chars")
