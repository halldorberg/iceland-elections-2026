"""Crop FB photos to 400x400, build candidate intros, apply to candidates.js
   (GRN.M) and merge into RUV drafts."""
import re, json, sys, io, hashlib
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')
SRC = ROOT / 'temp' / 'grn_m_bios'
DST_IMG = ROOT / 'images' / 'candidates'

# Mapping: ballot -> (name, fbid for raw image)
CANDS = [
    (2,  'Björn Steinar Brynjólfsson', '1295036816144875'),
    (3,  'Gunnar Már Gunnarsson',      '1294207819561108'),
    (4,  'Signý Lind Elíasdóttir',     '1293508779631012'),
    (5,  'Eydís Ármannsdóttir',        '1292549489726941'),
    (6,  'Aníta Sif Kristjánsdóttir',  '1291754473139776'),
    (7,  'Páll Gíslason',              '1290914969890393'),  # ballot 07 file = #7
    (8,  'Páll Árni Pétursson',        '1290255723289651'),
    (9,  'Hajie Flores Sicat',         '1289477556700801'),
    (10, 'Andri Hrafn Vilhelmsson',    '1288598036788753'),
    (11, 'Ragna Fossádal',             '1287929383522285'),
]


# ─── Parse FB post text into structured fields ─────────────────────────────
def parse_intro(text):
    """Extract fields from a FB candidate intro post."""
    fields = {}
    # Question→answer pairs we care about
    patterns = {
        'nafn':           r'Nafn:\s*(.+?)(?=\n\n|\n[A-ZÁÉÍÓÚÝÞÆÖ][a-záéíóúýþæö]+:|$)',
        'atvinna':        r'Atvinna:\s*(.+?)(?=\n\n|\n[A-ZÁÉÍÓÚÝÞÆÖ][a-záéíóúýþæö]+:|$)',
        'fjolskylda':     r'Fjölskylduhagir:\s*(.+?)(?=\n\n|\n[A-ZÁÉÍÓÚÝÞÆÖ][a-záéíóúýþæö]+:|Hvernig|Hvers|Hvað|Hver|Viltu|Eitthvað|$)',
        'framtid':        r'(?:Hvernig verður Grindav[íi]k eftir fjögur ár\??:?)\s*(.+?)(?=\n\n|\nHvers|\nHvað|\nViltu|\nEitthvað|All reactions|$)',
        'politik':        r'(?:Hvers vegna að taka þátt í pólitík\??:?)\s*(.+?)(?=\n\n|\nHvað|\nViltu|\nEitthvað|All reactions|$)',
        'elska':          r'(?:Hvað elska(?:r þú|ru|rðu) mest við Grindavik\??:?|Hvað elska(?:r þú|ru|rðu) mest við Grindavík\??:?)\s*(.+?)(?=\n\n|\nViltu|\nEitthvað|All reactions|$)',
        'lokum':          r'(?:Viltu segja (?:e-ð|eitthvað) að lokum\??:?|Eitthvað sem þú vilt segja að lokum\??:?)\s*(.+?)(?=\n\n|All reactions|$)',
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.S)
        if m:
            val = m.group(1).strip()
            # collapse multiple newlines
            val = re.sub(r'\n+', ' ', val).strip()
            fields[key] = val
    return fields


def first_sentence(s):
    if not s: return ''
    s = s.strip().split('\n')[0]
    m = re.match(r'(.+?[.!?])(\s|$)', s)
    return m.group(1) if m else s


def build_bio(ballot, name, fields):
    """Build a concise 2-4 sentence Icelandic bio from parsed fields."""
    parts = []
    # Sentence 1: name + atvinna
    occ = fields.get('atvinna', '').rstrip('.')
    if occ:
        parts.append(f'{name} starfar sem {occ.lower()[0]+occ[1:]}.' if occ[0].isupper() else f'{name} starfar sem {occ}.')
    else:
        parts.append(f'{name} býður sig fram fyrir Miðflokkinn í Grindavík.')
    # Sentence 2: fjölskylda (compressed)
    fj = fields.get('fjolskylda', '')
    if fj:
        # take up to first comma+couple clauses
        fj = re.sub(r'\s+', ' ', fj)[:240].rstrip(' ,;')
        if not fj.endswith('.'):
            fj += '.'
        parts.append(fj)
    # Sentence 3: motivation (first sentence)
    pol = first_sentence(fields.get('politik', ''))
    if pol:
        parts.append(pol)
    # Sentence 4: closing context
    parts.append(f'Hann/Hún skipar {ballot}. sæti á M-lista Miðflokksins í Grindavík fyrir sveitarstjórnarkosningarnar 16. maí 2026.')
    bio = ' '.join(parts)
    # Replace generic Hann/Hún with appropriate pronoun based on common patterns
    # Simple heuristic: feminine names end in 'a', 'ý', 'ína', 'íf', 'ís', 'in', 'dís', 'ur' (ambiguous)
    fem_endings = ('a', 'ý', 'ína', 'íf', 'ís', 'in', 'dís', 'ín', 'ja')
    masc_endings = ('ur', 'i', 'son')
    first = name.split()[0].lower()
    if any(first.endswith(e) for e in fem_endings) and not first.endswith('ur') and not first.endswith('son'):
        bio = bio.replace('Hann/Hún', 'Hún')
    else:
        bio = bio.replace('Hann/Hún', 'Hann')
    return bio


# ─── Crop image ────────────────────────────────────────────────────────────
def crop_to_400(src_path, dst_path):
    img = Image.open(src_path).convert('RGB')
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    if side > 400:
        img = img.resize((400, 400), Image.LANCZOS)
    img.save(dst_path, 'JPEG', quality=88, optimize=True)


# ─── Pipeline ──────────────────────────────────────────────────────────────
records = []
for ballot, name, fbid in CANDS:
    txt_fn = SRC / f'ballot_{ballot:02d}_{fbid}.txt'
    raw_fn = SRC / f'ballot_{ballot:02d}_{fbid}_raw.jpg'
    if not txt_fn.exists():
        print(f'  MISS: {txt_fn}')
        continue
    body = txt_fn.read_text(encoding='utf-8')
    fields = parse_intro(body)
    bio = build_bio(ballot, name, fields)

    # Crop image
    fn_hash = hashlib.md5(f'grn-m-{ballot}-{name}'.encode()).hexdigest()[:16]
    out_jpg = DST_IMG / f'{fn_hash}.jpg'
    if raw_fn.exists():
        try:
            crop_to_400(raw_fn, out_jpg)
        except Exception as e:
            print(f'  {ballot}: crop fail: {e}')

    records.append({
        'ballot': ballot,
        'name': name,
        'photo': out_jpg.name,
        'occupation': fields.get('atvinna', '').rstrip('.'),
        'bio': bio,
        'fields': fields,
    })
    print(f'  {ballot}: {name} -> {out_jpg.name}  ({len(bio)} chars)')

json.dump(records, open(SRC / 'parsed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\nWrote parsed.json ({len(records)} candidates)')
