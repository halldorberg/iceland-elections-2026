"""Update RVK candidate titles (and select names) for S, B, C, V, P lists
   to match each party's official website. Updates the first occurrence
   only; only touches the plain-row prefix `[N, 'name', 'occ', ...`."""
import re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

CJS = Path(r'F:\Claude Projects\iceland-elections\js\data\candidates.js')
src = CJS.read_text(encoding='utf-8')

# (party_letter, ballot, new_name_or_None, new_title_or_None)
UPDATES = [
    # ─── RVK.S Samfylking ──────────────────────────
    ('S', 1, 'Pétur H. Marteinsson', 'Rekstrarstjóri og fv. knattspyrnumaður'),
    ('S', 2, None, 'Borgarstjóri'),
    ('S', 3, 'Steinunn Gyðu- og Guðjónsdóttir', 'Ráðgjafi og fyrrum talskona Stígamóta'),
    ('S', 7, None, 'Fyrrverandi bæjarstjóri í Mosfellsbæ'),
    ('S', 9, 'Isabel Alejandra Díaz', 'Stjórnsýslufræðingur og fyrrum forseti Stúdentaráðs HÍ'),
    ('S', 10, None, 'Stjórnmála og stjórnýslufræðingur'),
    ('S', 11, None, 'Þroskaþjálfi og verkefnastjóri hjá Þroskahjálp'),
    ('S', 13, None, 'Forstöðukona Batahúss'),
    ('S', 14, None, 'öryrki og formaður Hjálparkokka'),
    ('S', 15, None, 'Doktor í faraldsfræði'),
    ('S', 18, None, 'Lyfjafræðingur og jógakennari'),
    ('S', 23, None, 'Húsasmiður og formaður Hallveigar'),
    ('S', 25, None, 'Rekstrarhagfræðingur'),
    ('S', 26, None, 'Leikskólastarfsmaður'),
    ('S', 29, None, 'Menntaskólanemi'),
    ('S', 30, None, 'Kvikmyndagerðarkona'),
    ('S', 31, None, 'Plötusali'),
    ('S', 37, None, 'Verslunarmaður'),
    ('S', 38, None, 'Tónlistarkennari og gítarleikari'),
    ('S', 39, None, 'Rauðsokka'),
    ('S', 41, None, 'Eldri borgari'),
    ('S', 42, None, 'Leiðsögumaður'),
    ('S', 44, None, 'Skrifstofustjóri skrifstofu jafnréttismála og fyrrum borgarstjóri'),
    ('S', 45, None, 'Alþingismaður, læknir og fyrrum borgarstjóri'),
    ('S', 46, None, 'Fyrrum borgarstjóri'),

    # ─── RVK.B Framsókn ────────────────────────────
    ('B', 1, None, 'Borgarfulltrúi'),
    ('B', 3, None, 'Varaborgarfulltrúi og framkvæmdastjóri Hjólakrafts'),
    ('B', 4, None, 'Kynningarstjóri'),
    ('B', 5, None, 'Hagfræðinemi og stúdentaráðsliði'),
    ('B', 6, None, 'Fíkniráðgjafi'),
    ('B', 7, None, 'Úkraínskumælandi brúarsmiður hjá Miðstöð menntunar og skólaþjónustu'),
    ('B', 9, None, 'Myndlistarmaður og hönnuður'),
    ('B', 10, None, 'Sviðsstjóri'),
    ('B', 12, 'Dagbjört Höskuldsdóttir', 'Formaður Sambands eldri Framsóknarmanna og fyrrum kaupmaður'),
    ('B', 14, None, 'Læknir'),
    ('B', 15, None, 'Náms- og starfsráðgjafi og kennari'),
    ('B', 16, None, 'Kennari og handboltaþjálfari'),
    ('B', 18, None, 'El Jefe'),
    ('B', 19, None, 'Tónlistarmaður og háskólanemi'),
    ('B', 20, None, 'Kennari og tónlistarkona'),
    ('B', 21, 'Gísli J Jónatansson', 'Fyrrverandi kaupfélagsstjóri'),
    ('B', 22, None, 'Móttökuritari'),
    ('B', 24, 'Hafsteinn Gunnarsson', 'Byggingafræðingur og forstöðumaður'),
    ('B', 26, None, 'Fjármálastjóri og hagfræðingur'),
    ('B', 27, None, 'Aðstoðarmaður framkvæmdastjóra'),
    ('B', 29, None, 'Aðstoðarforstöðukona á frístundaheimili'),
    ('B', 32, None, 'Atvinnubílstjóri'),
    ('B', 33, None, 'Deildarstjóri í grunnskóla'),
    ('B', 34, None, 'Námsmaður og stuðningsfulltrúi í grunnskóla'),
    ('B', 35, 'Inga Þyrí Kjartansdóttir', 'Formaður eldri borgara í Fossvogi'),
    ('B', 37, None, 'Eldri borgari'),
    ('B', 39, None, 'Kvikmynda- og sjónvarpsþáttaframleiðandi'),
    ('B', 40, None, 'Söngvari og lögmaður'),
    ('B', 41, None, 'Fyrrv. sérkennari'),
    ('B', 42, None, 'Framkvæmdastjóri og fráfarandi borgarfulltrúi'),
    ('B', 43, None, 'Dósent við HÍ og fráfarandi borgarfulltrúi'),
    ('B', 44, None, 'Fyrrv. skrifstofustjóri'),
    ('B', 45, 'Hjálmar Árnason', 'Fyrrv. þingmaður og skólameistari'),

    # ─── RVK.C Viðreisn ────────────────────────────
    ('C', 1, None, 'Fjölmiðlakona og handritshöfundur'),
    ('C', 4, None, 'Umhverfisfræðingur og framkvæmdastjóri Kolaportsins'),
    ('C', 5, None, 'Frumkvöðull og meðstofnandi Hopp'),
    ('C', 6, None, 'Náms- og starfsráðgjafi Borgarholtsskóla og formaður Félags náms- og starfsráðgjafa'),
    ('C', 7, None, 'Forseti Uppreisnar, ungliðahreyfingar Viðreisnar og laganemi'),
    ('C', 8, 'Monika Katarzyna Waleszczyńska', None),
    ('C', 9, None, 'Skipulagsverkfræðingur'),
    ('C', 10, None, 'Sálfræðikandídat, starfsmaður íbúðakjarna og formaður Viðreisnar í Reykjavík'),
    ('C', 12, None, 'Kennari og stjórnmálafræðingur'),
    ('C', 13, None, 'Hugbúnaðarverkfræðingur'),
    ('C', 15, None, 'Starfsmaður neyðarskýlis'),
    ('C', 16, None, 'Stjórnmálafræðinemi og frístundaleiðbeinandi'),
    ('C', 17, 'Jón Steindór Valdimarsson', None),
    ('C', 20, None, 'Fyrrv. varaborgarfulltrúi og sálgætir'),
    ('C', 21, None, 'Stofnandi og framkvæmdastjóri GRID'),
    ('C', 22, 'Emilía Björt Írisardóttir Bachmann', 'Starfsmaður þingflokks Viðreisnar'),
    ('C', 25, None, 'Fyrirtækjaráðgjafi'),
    ('C', 26, 'Ólöf Hugrún Valdimarsdóttir', 'Deildarfulltrúi og verkefnastjóri hjá Listaháskóla Íslands'),
    ('C', 31, 'Jakob Löve', 'Hagfræðinemi'),
    ('C', 32, None, 'Leiklistar- og tónlistarfræðingur'),
    ('C', 34, 'María Malmquist', 'Lögfræðinemi'),
    ('C', 35, None, 'Bókaútgefandi'),
    ('C', 36, None, 'Leikskólaleiðbeinandi'),
    ('C', 37, None, 'Hugbúnaðarsmiður og tækniráðgjafi'),
    ('C', 40, None, 'List- og safnafræðingur'),
    ('C', 41, None, 'Leikstjóri og leiðsögumaður'),
    ('C', 44, None, 'Aðstoðarmaður utanríkisráðherra'),
    ('C', 45, None, 'Þingmaður og fyrrv. borgarstjóri'),
    ('C', 46, None, 'Borgarfulltrúi og fráfarandi oddviti Viðreisnar í Reykjavík'),
]


# Find RVK const block
m = re.search(r'^const RVK\s*=\s*\{', src, re.M)
RVK_START = m.end() - 1
depth = 0; i = RVK_START; in_str = None
while i < len(src):
    c = src[i]
    if in_str:
        if c == '\\': i += 2; continue
        if c == in_str: in_str = None
        i += 1; continue
    if c in ("'",'"','`'): in_str = c; i += 1; continue
    if c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: break
    i += 1
RVK_END = i


def find_party_block(src, party_letter):
    m = re.search(r'\n  ' + party_letter + r'\s*:\s*\{', src[RVK_START:RVK_END])
    if not m:
        return None
    p_start = RVK_START + m.end() - 1
    depth = 0; i = p_start; in_str = None
    while i < RVK_END:
        c = src[i]
        if in_str:
            if c == '\\': i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c in ("'",'"','`'): in_str = c; i += 1; continue
        if c == '{': depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return p_start, i
        i += 1


def esc(s):
    return s.replace('\\', '\\\\').replace("'", "\\'")


# Build edits in REVERSE position order
edits = []
party_ranges = {}

for letter, ballot, new_name, new_title in UPDATES:
    if letter not in party_ranges:
        party_ranges[letter] = find_party_block(src, letter)
    ps, pe = party_ranges[letter]
    # Find row `[BALLOT, 'OLD_NAME', 'OLD_OCC', ...`
    row_pat = re.compile(r"\n(\s+)\[\s*" + str(ballot) + r"\s*,\s*'((?:[^'\\]|\\.)+)'\s*,\s*'((?:[^'\\]|\\.)*)'")
    m = row_pat.search(src, ps, pe)
    if not m:
        print(f'  RVK.{letter}.{ballot}: row not found')
        continue
    old_name = m.group(2)
    old_occ = m.group(3)
    final_name = new_name if new_name else old_name
    final_occ = new_title if new_title else old_occ
    if final_name == old_name and final_occ == old_occ:
        continue
    # Replace the matched prefix
    replacement = f"\n{m.group(1)}[{ballot}, '{esc(final_name)}', '{esc(final_occ)}'"
    edits.append((m.start(), m.end(), replacement, f'RVK.{letter}.{ballot}'))

# Sort by start descending
edits.sort(key=lambda x: x[0], reverse=True)
print(f'Applying {len(edits)} edits...')
for s, e, repl, label in edits:
    src = src[:s] + repl + src[e:]

CJS.write_text(src, encoding='utf-8')
print('Wrote candidates.js')
