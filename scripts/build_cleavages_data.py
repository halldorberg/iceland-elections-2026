"""Generate js/data/cleavages.js from temp/ruv_cleavages_by_muni.json.

For every muni found in the RÚV data:
  - Apply the floor: keep cleavages with score >= 0.8 (score = std × balance,
    where balance = 2·min(disagree,agree)/total). If fewer than 6 qualify,
    fill up to 6 from the next-highest-scoring topics.
  - Match the muni to its slug in our system (`municipalities.js`).
  - Match each RÚV party name to our party codes used in this muni.
  - Map each question title to an icon key via keyword rules; unknown
    topics fall back to a generic 'chat' icon.

Output: js/data/cleavages.js (overwrites whatever was there).
"""
from __future__ import annotations
import json, re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).parent.parent

# ─── Icon definitions ────────────────────────────────────────────────────
# Consistent line style: 24x24 viewBox, currentColor stroke, 1.6px,
# round caps + joins, transparent fill.
def svg(inner: str) -> str:
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        f'{inner}</svg>'
    )

ICONS: dict[str, str] = {
    # Core (already used in initial Reykjavík draft)
    'plane':      svg('<path d="M12 3v6.5l8.5 4.2v1.6l-8.5-2.4v4.4l2.5 2v1l-3.5-1-3.5 1v-1l2.5-2v-4.4L3.5 15.3v-1.6L12 9.5V3z"/>'),
    'bus':        svg('<rect x="3.5" y="5" width="17" height="13" rx="2"/><path d="M3.5 11h17"/><path d="M6 8h3M11 8h2M15 8h3"/><circle cx="7.5" cy="20" r="1.4"/><circle cx="16.5" cy="20" r="1.4"/>'),
    'cars':       svg('<rect x="2" y="4" width="8" height="5" rx="1"/><circle cx="4.5" cy="10" r="0.8"/><circle cx="7.5" cy="10" r="0.8"/><rect x="14" y="4" width="8" height="5" rx="1"/><circle cx="16.5" cy="10" r="0.8"/><circle cx="19.5" cy="10" r="0.8"/><rect x="8" y="14" width="8" height="5" rx="1"/><circle cx="10.5" cy="20" r="0.8"/><circle cx="13.5" cy="20" r="0.8"/>'),
    'busLane':    svg('<path d="M3 3v18M21 3v18"/><path d="M12 4v3M12 11v3M12 18v3"/><rect x="5" y="7" width="5" height="10" rx="0.8"/><path d="M5 12h5"/><circle cx="6.5" cy="18.5" r="0.6"/><circle cx="8.5" cy="18.5" r="0.6"/>'),
    'highway':    svg('<path d="M5 21 9 3M19 21 15 3"/><path d="M12 6v2M12 11v2M12 16v2"/>'),
    'briefcase':  svg('<rect x="3" y="7" width="18" height="13" rx="1.5"/><path d="M9 7V5h6v2"/><circle cx="9.5" cy="13" r="1"/><path d="M14.5 11.5l-5 5"/><circle cx="14.5" cy="16" r="1"/>'),
    'homeParent': svg('<path d="M3 11l9-7 9 7"/><path d="M5 9.5V20h14V9.5"/><circle cx="12" cy="13" r="1.6"/><path d="M8.5 20v-3a3.5 3.5 0 0 1 7 0v3"/>'),
    'schoolOut':  svg('<path d="M2 13l7-5 7 5"/><path d="M4 12v8h10v-8"/><rect x="7" y="14" width="4" height="6"/><path d="M16 8h6M19 5l3 3-3 3"/>'),
    'child':      svg('<circle cx="12" cy="6" r="3"/><path d="M12 9v9"/><path d="M8 13l4-1 4 1"/><path d="M9 21l3-3 3 3"/>'),

    # Newly added for the broader rollout
    'snow':       svg('<path d="M12 2v20M5 5l14 14M5 19L19 5M2 12h20"/><path d="M9 5l3-3 3 3M15 19l-3 3-3-3M5 9l-3 3 3 3M19 9l3 3-3 3"/>'),
    'recycle':    svg('<path d="M7 4h10l3 5"/><path d="M17 4l2 4-3 1"/><path d="M21 13l-3 5h-6"/><path d="M14 21l3-3-2-2"/><path d="M3 13l3-5 3 5"/><path d="M9 21H5l-2-3 4-2"/>'),
    'elderly':    svg('<circle cx="11" cy="5" r="2.5"/><path d="M11 7.5v5"/><path d="M8 12.5h6"/><path d="M9 12.5l-2 9M13 12.5l2 9"/><path d="M16 9.5v12"/>'),
    'vote':       svg('<rect x="3" y="9" width="18" height="11" rx="1.5"/><path d="M3 14h18"/><path d="M9 9V5l3-2 3 2v4"/><path d="M11 17h2"/>'),
    'pool':       svg('<path d="M3 17c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5"/><path d="M3 21c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5"/><path d="M7 14V6a2 2 0 0 1 4 0v8"/><path d="M7 9h4"/>'),
    'helpHand':   svg('<path d="M11 11l-3-3a1.5 1.5 0 1 1 2-2l3 3"/><path d="M11 11l3 3a1.5 1.5 0 0 0 2-2l-2-2"/><path d="M14 12h3a2 2 0 0 1 2 2v2a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4v-2"/><path d="M5 18l-2-2v-3a2 2 0 0 1 2-2h2"/>'),
    'tourism':    svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'),
    'culture':    svg('<path d="M5 9V7l3-2 4 2 4-2 3 2v2c0 6-5 11-7 11s-7-5-7-11z"/><circle cx="9" cy="11" r="0.8" fill="currentColor"/><circle cx="15" cy="11" r="0.8" fill="currentColor"/><path d="M10 14c1 1 3 1 4 0"/>'),
    'sport':      svg('<circle cx="13" cy="4.5" r="2"/><path d="M5 22l3-4 3 1 2-4 4 2 1 5"/><path d="M11 19l-3-1-2 3"/><path d="M9 12l4 1 2-3"/>'),
    'housing':    svg('<path d="M3 11l5-4 5 4"/><path d="M5 10v10h6v-5h2v-5"/><path d="M11 13l5-3 5 3"/><path d="M13 12v8h6v-8"/>'),
    'cruiseShip': svg('<path d="M3 18l1.5 3h15L21 18"/><path d="M5 18V12h14v6"/><path d="M5 12V9l7-2 7 2v3"/><path d="M9 7V4h6v3"/><path d="M9 12v6M15 12v6"/>'),
    'merge':      svg('<path d="M5 4v6c0 4 4 4 7 6 3-2 7-2 7-6V4"/><path d="M5 4h14"/><path d="M12 16v4"/><path d="M9 20h6"/>'),
    'nature':     svg('<path d="M12 2c-3 4-5 6-5 9a5 5 0 0 0 10 0c0-3-2-5-5-9z"/><path d="M12 14v8"/><path d="M9 19h6"/>'),
    'parking':    svg('<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M9 17V7h4a3 3 0 0 1 0 6h-4"/>'),
    'migrant':    svg('<circle cx="9" cy="6" r="2.5"/><circle cx="17" cy="7" r="2"/><path d="M5 21v-4a4 4 0 0 1 8 0v4"/><path d="M14 21v-3a3 3 0 0 1 6 0v3"/>'),
    'service':    svg('<path d="M4 21V9l8-6 8 6v12"/><path d="M9 21v-6h6v6"/><path d="M9 12h.01M15 12h.01"/><path d="M10 16q2 1.5 4 0"/>'),
    'ship':       svg('<path d="M3 16l1.5 3h15L21 16"/><path d="M5 16V9l14 1v6"/><path d="M12 7V4M9 5h6"/>'),
    'farm':       svg('<path d="M3 13l9-8 9 8"/><path d="M5 12v8h14v-8"/><path d="M10 20v-5h4v5"/>'),
    'water':      svg('<path d="M12 3c-3 5-6 8-6 12a6 6 0 0 0 12 0c0-4-3-7-6-12z"/>'),
    'fish':       svg('<path d="M3 12c4-7 11-7 15-2"/><path d="M3 12c4 7 11 7 15 2"/><path d="M18 10v4"/><path d="M18 12l3-2v4z"/><circle cx="6" cy="11" r="0.5" fill="currentColor"/>'),
    'monument':   svg('<path d="M9 21V8a3 3 0 0 1 6 0v13"/><path d="M7 21h10"/><path d="M11 5V3h2v2"/>'),
    'scooter':    svg('<circle cx="6" cy="18" r="2"/><circle cx="18" cy="18" r="2"/><path d="M6 18h11"/><path d="M17 18l-3-12h-2"/><path d="M14 5h-2"/>'),
    'health':     svg('<path d="M12 4l8 4v6c0 4-3 7-8 8-5-1-8-4-8-8V8z"/><path d="M12 9v6M9 12h6"/>'),
    'spa':        svg('<path d="M12 2v8M9 5l3-3 3 3M5 12h8M8 9l-3 3 3 3"/><path d="M3 17h18M3 21h18"/>'),
    'fund':       svg('<circle cx="12" cy="12" r="9"/><path d="M9 11h6M9 13h4"/><path d="M12 8v8M10 8h4"/>'),
    # Generic fallback — speech-bubble (debate)
    'chat':       svg('<path d="M4 5h16v11H8l-4 4z"/><path d="M9 11h6M9 14h4"/>'),
}

# ─── Topic-title → icon key ──────────────────────────────────────────────
# Order matters: first match wins.
ICON_RULES: list[tuple[str, str]] = [
    # Specific
    (r'flugv[öo]ll', 'plane'),
    (r'borgarl[ií]n', 'bus'),
    (r's[ée]rakrein|fyrir str[ae]t[oó]', 'busLane'),
    (r'einkab[ií]l|of margir', 'cars'),
    (r'su[dð]urlandsbraut|hringveg', 'highway'),
    (r'heimgrei[dð]sl', 'homeParent'),
    (r'leiksk[oó]lavist|t[oó]lf m[aá]na[dð]a', 'child'),
    (r'leiksk[oó]labarn|stytta vistunart', 'child'),
    (r'[uú]tvistun', 'schoolOut'),
    (r'fj[aá]rhagsleg|[ií]vilnan|fyrirt[ae]ki', 'briefcase'),
    (r'snj[oó]mokstur|g[oö]tus[oó]p', 'snow'),
    (r'flokka sorp|sorp', 'recycle'),
    (r'frístundastyrk|eldri borgur|aldra[dð]', 'elderly'),
    (r'[ií]b[uú]akosning|l[yý][dð]r[ae][dð]', 'vote'),
    (r'sundlaug', 'pool'),
    (r'f[aá]t[ae]kt|fj[aá]rhagsa[dð]sto[dð]', 'helpHand'),
    (r'fer[dð]aman|uppbygging', 'tourism'),
    (r'menningarl|menning', 'culture'),
    (r'[ií]þr[oó]tt|t[oó]mstund', 'sport'),
    (r'n[yý] hverfi|þ[ée]tting bygg[dð]', 'housing'),
    (r'b[ií]last[ae]', 'parking'),
    (r'h[ae]lisleitend', 'migrant'),
    (r'[áa]n[ae]g[dð]', 'service'),
    (r'skemmtifer[dð]askip|innvi[dð]agjald', 'cruiseShip'),
    (r'sameining', 'merge'),
    (r'hei[dð]m[oö]rk|[uú]tivist|vatnsvernd', 'nature'),
    (r'ferjusig|ferja', 'ship'),
    (r'fiskeldi|laxeldi|kv[ií]aeldi', 'fish'),
    (r'minnisvar', 'monument'),
    (r'rafhlaupahj[oó]l', 'scooter'),
    (r'heilsug[ae]sl|heilbrig', 'health'),
    (r'b[áa][dð]l[oó]n|heilsulind', 'spa'),
    (r'fj[aá]rm[aá]l|sj[oó][dð]', 'fund'),
    (r'd[yý]rahr[ae]|g[aá]masv[ae]', 'recycle'),
    (r'b[uú][dð]ardal|gun(narsh|narstún)', 'farm'),
    (r'akrein|umfer[dð]', 'cars'),
    (r'akranesvell|h[oó]tel', 'spa'),
    (r'biblio|b[oó]kasaf', 'culture'),
]

def title_to_icon(title: str) -> str:
    s = title.lower()
    for pat, key in ICON_RULES:
        if re.search(pat, s, re.IGNORECASE):
            return key
    return 'chat'

# ─── Muni mapping (RÚV muni_slug → our muni id) ──────────────────────────
MUNI_RUV_TO_OUR = {
    'reykjavik': 'reykjavik',
    'kopavogur': 'kopavogur',
    'hafnarfjordur': 'hafnarfjordur',
    'reykjanesbaer': 'reykjanesbaer',
    'gardabaer': 'gardabaer',
    'akureyri': 'akureyri',
    'mosfellsbaer': 'mosfellsbaer',
    'sveitarfelagid-arborg': 'arborg',
    'akranes': 'akranes',
    'mulathing': 'mulathing',
    'fjardabyggd': 'fjardabyggd',
    'seltjarnarnes': 'seltjarnarnes',
    'vestmannaeyjar': 'vestmannaeyjar',
    'skagafjordur': 'skagafjordur',
    'sudurnesjabaer': 'sudurnesjabaer',
    'borgarbyggd': 'borgarbyggd',
    'isafjardarbaer': 'isafjordur',
    'sveitarfelagid-hornafjordur': 'hornafjordur',
    'sveitarfelagid-vogar': 'vogar',
    'sveitarfelagid-olfus-s': 'olfus',
    'hveragerdi': 'hveragerdi',
    'grindavik': 'grindavik',
    'rangarthing-eystra': 'rangarthingeystra',
    'rangarthing-ytra': 'rangarthingytra',
    'nordurthing': 'nordurping',
    'fjallabyggd': 'fjallabyggd',
    'hunabyggd': 'hunabyggd',
    'dalvikurbyggd': 'dalvikurbyggd',
    'snaefellsbaer': 'snaefellsbaer',
    'vesturbyggd': 'vesturbyggd',
    'bolungarvik': 'bolungarvik',
    'sveitarfelagid-stykkisholmur': 'stykkisholmur',
    'hunathing-vestra': 'hunathing',
    'hvalfjardarsveit': 'hvalfjardarsveit',
    'hrunamannahreppur': 'hrunamannahreppur',
    'blaskogabyggd': 'blaskogabyggd',
    'grundarfjardarbaer': 'grundarfjordur',
    'ingeyjarsveit': 'thingeyjarsveit',
    'horgarsveit': 'horgarsv',
    'reykholahreppur': 'reykholar',
    'eyjafjardarsveit': 'eyjafjardarsveit',
    'sveitarfelagid-skagastrond': 'skagastrond',
    'myrdalshreppur': 'myrdalshr',
    'skaftarhreppur': 'skaftarhreppur',
    'kjosarhreppur': 'kjosarhreppur',
    'svalbardsstrandarhreppur-s': 'svalbardsstrond',
    'sudavikurhreppur-f': 'sudavik',
    'strandabyggd': 'strandabyggd',
    'floahreppur': 'floahreppur',
    'kaldrananeshreppur': 'kaldrananes',
    'arneshreppur': 'arneshr',
    'tjorneshreppur': 'tjornes',
    'vopnafjardarhreppur': 'vopnafjordur',
    'skeida-og-gnupverjahreppur': 'skeidagnup',
    'grimsnes-og-grafningshreppur': 'grimsnesgrafningur',
}

# ─── Party name normaliser ───────────────────────────────────────────────
# (lowercased substring, our-party-code) — first match wins. Designed to
# catch both formal national names and the many local-list variants like
# "Framsókn og frjálsir", "Sjálfstæðismenn og óháðir".
NATIONAL_PARTY_RULES: list[tuple[str, str]] = [
    ('sjálfstæðis',   'D'),
    ('framsókn',      'B'),
    ('framsóknar',    'B'),
    ('samfylking',    'S'),
    ('jafnaðar',      'S'),  # "Jafnaðarmannafélag…"
    ('viðreisn',      'C'),
    ('píratar',       'P'),
    ('miðflokk',      'M'),
    ('flokkur fólks', 'F'),
    ('sósíalist',     'J'),
    ('vinstrið',      'A'),  # Reykjavík: VG + Vor til vinstri merged list
    ('vinstrihreyf',  'V'),
    ('vinstri græn',  'V'),
    ('vg ',           'V'),
    (' vg',           'V'),
    # Letter-prefix list shorthands ("D-listinn og óháðir" etc.)
    ('d-list', 'D'),
    ('s-list', 'S'),
    ('b-list', 'B'),
    ('m-list', 'M'),
    ('c-list', 'C'),
    ('p-list', 'P'),
    ('f-list', 'F'),
    ('j-list', 'J'),
    ('v-list', 'V'),
    ('a-list', 'A'),
    ('l-list', 'L'),
]

# Per-muni explicit overrides for local lists that don't fit the heuristic.
# Map RÚV party-name → our muni code.
MANUAL_PARTY_OVERRIDES: dict[tuple[str, str], str] = {
    ('akureyri', 'Bæjarlisti Akureyrar'):           'L',
    ('mulathing', 'Austurlistinn/Viðreisn Múlaþingi'): 'L',
    ('borgarbyggd', 'Borgarbyggðarlistinn'):        'A',
    ('dalvikurbyggd', 'Byggðalistinn'):             'B',
    ('dalvikurbyggd', 'K-listi Dalvíkurbyggðar'):   'K',
    ('fjallabyggd',  'Fyrir heildina'):             'H',
    ('hveragerdi',   'Okkar Hveragerði'):           'OKH',
    ('mosfellsbaer', 'Vinir Mosfellsbæjar'):        'L',
    ('hornafjordur', 'Kex framboðið'):              'HFJK',
    ('rangarthingeystra', 'D-listinn og aðrir lýðræðissinnar'): 'D',
    ('sudurnesjabaer', 'D-listinn og óháðir'):      'D',
    ('hornafjordur', 'Framsókn og stuðningsmenn'):  'B',
    ('akranes', 'Framsókn og frjálsir'):            'B',
    ('akranes', 'Sjálfstæðisflokkurinn á Akranesi'):'D',
    ('myrdalshr', 'A fyrir alla'):                  'A',
    ('myrdalshr', 'Samfélagið'):                    'Z',
    ('grimsnesgrafningur', 'Betri sveit - fyrir okkur öll'): 'Z',
    ('horgarsv', 'Gróska'):                         'HGH',
    ('hunathing', 'Nýtt afl'):                      'NHV',
    ('thingeyjarsveit', 'Á listi Ábyrgðar'):        'A',
    ('thingeyjarsveit', 'L listi Framfara'):        'L',
    ('thingeyjarsveit', 'N listinn'):               'N',
    ('vesturbyggd', 'Ný sýn'):                      'STV',
    ('skagastrond', 'Fyrir Skagaströnd'):           'F',
    ('stykkisholmur', 'Listi framfarasinna'):       'L',
    ('tjornes', 'Tjörneslistinn'):                  'T',
    ('bolungarvik', 'Máttur meyja og manna'):       'MMM',
}

# ─── Read inputs ─────────────────────────────────────────────────────────
ruv = json.loads((ROOT / 'temp' / 'ruv_cleavages_by_muni.json').read_text(encoding='utf-8'))
muni_src = (ROOT / 'js' / 'data' / 'municipalities.js').read_text(encoding='utf-8')
party_src = (ROOT / 'js' / 'data' / 'parties.js').read_text(encoding='utf-8')

# Parse municipalities to get id → (name, population, partyIds)
muni_re = re.compile(
    r"id:\s*'([^']+)',\s*name:\s*'([^']+)'[\s\S]*?"
    r"population:\s*(\d+)[\s\S]*?"
    r"partyIds:\s*\[([^\]]+)\]",
    re.DOTALL,
)
munis: dict[str, dict] = {}
for m in muni_re.finditer(muni_src):
    pids = [p.strip().strip("'\"") for p in m.group(4).split(',') if p.strip()]
    munis[m.group(1)] = {'id': m.group(1), 'name': m.group(2), 'population': int(m.group(3)), 'partyIds': pids}

# Parse parties.js for code → name (just the obvious fields)
party_name_re = re.compile(
    r"\b([A-Z]{1,4}):\s*\{[^{}]*?name:\s*'([^']+)'", re.DOTALL,
)
party_names: dict[str, str] = {m.group(1): m.group(2) for m in party_name_re.finditer(party_src)}

# ─── Per-muni cleavage selection + party mapping ─────────────────────────
def normalise(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').lower().strip())

unmapped_parties: list[tuple[str, str]] = []  # (muni, ruv_name) — for diagnostics
unmapped_munis: list[str] = []                # RÚV slugs we couldn't map

result: dict[str, list[dict]] = {}

# Sort munis by population (largest first) to write them in size order
muni_order = sorted(munis.values(), key=lambda x: -x['population'])

# Build a reverse lookup from RÚV slug to its parties
ruv_by_slug = {m['muni_slug']: m for m in ruv}

for our_muni in muni_order:
    our_id = our_muni['id']
    # Find the RÚV slug for this muni
    ruv_slug = next((s for s, oid in MUNI_RUV_TO_OUR.items() if oid == our_id), None)
    if not ruv_slug:
        unmapped_munis.append(our_id)
        continue
    ruv_muni = ruv_by_slug.get(ruv_slug)
    if not ruv_muni:
        unmapped_munis.append(f'{our_id} → {ruv_slug} (not found)')
        continue

    # Build party-name → our-code mapping for this muni
    our_party_codes = set(our_muni['partyIds'])
    our_party_name_to_code = {normalise(party_names.get(c, '')): c for c in our_party_codes if party_names.get(c)}
    name_to_code: dict[str, str] = {}  # ruv_party_name → our_code
    for ruv_party in ruv_muni.get('parties', []) or []:
        rname = normalise(ruv_party['name'])
        code: str | None = None
        # 0) Manual per-muni override — for unique local lists
        manual = MANUAL_PARTY_OVERRIDES.get((our_id, ruv_party['name']))
        if manual and manual in our_party_codes:
            code = manual
        # 1) Substring rule — handles "Sjálfstæðismenn og óháðir",
        #    "Framsókn og frjálsir", etc.
        if not code:
            for pat, c in NATIONAL_PARTY_RULES:
                if pat in rname and c in our_party_codes:
                    code = c
                    break
        # 2) Exact match against our-roster name
        if not code:
            code = our_party_name_to_code.get(rname)
        # 3) Substring against our-roster name (e.g. local list whose
        #    formal name contains a recognisable token)
        if not code or code not in our_party_codes:
            for our_n, c in our_party_name_to_code.items():
                if our_n and (our_n in rname or rname in our_n):
                    code = c
                    break
        if code and code in our_party_codes:
            name_to_code[ruv_party['name']] = code
        else:
            unmapped_parties.append((our_id, ruv_party['name']))

    # Pick cleavages: ≥ 0.8, min 6
    items = []
    for c in ruv_muni.get('cleavages', []):
        d, a = c['disagree_count'], c['agree_count']
        bal = (2 * min(d, a)) / (d + a) if (d + a) else 0
        score = c['std'] * bal
        items.append((score, c))
    items.sort(key=lambda x: -x[0])
    selected = [c for s, c in items if s >= 0.80]
    if len(selected) < 6:
        selected = [c for _, c in items[:6]]

    if not selected:
        continue

    topics = []
    for c in selected:
        stances: dict[str, str | None] = {pid: None for pid in our_party_codes}
        for p in c.get('parties', []) or []:
            code = name_to_code.get(p['name'])
            if not code: continue
            stances[code] = p['value']
        topics.append({
            'icon_key': title_to_icon(c['question_title']),
            'title':    c['question_title'],
            'stances':  stances,
        })
    result[our_id] = topics

# ─── Render JS file ──────────────────────────────────────────────────────
def js_string(s: str) -> str:
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"

lines = [
    '// AUTO-GENERATED by scripts/build_cleavages_data.py',
    '// Cleavage topics from RÚV kosningapróf, per muni.',
    '// Filter rule: cleavage_score (std × balance) >= 0.8, min 6 topics.',
    '// Each topic: { icon (SVG markup), title (Icelandic), stances: {<partyCode>: A/B/C/D | null} }',
    '',
    '// Smiley map for stance values. A is "most disagree" — uses the dark',
    "// 'angry face' rather than the more aggressive red 'pouting face'.",
    'export const STANCE_SMILEYS = {',
    "  A: '😠',  // mjög ósammála",
    "  B: '🙁',  // ósammála",
    "  C: '🙂',  // sammála",
    "  D: '😄',  // mjög sammála",
    '};',
    'export const STANCE_LABELS_IS = {',
    "  A: 'Mjög ósammála',",
    "  B: 'Ósammála',",
    "  C: 'Sammála',",
    "  D: 'Mjög sammála',",
    '};',
    '',
    '// Custom-drawn line icons — consistent style across all keys:',
    '// 24x24 viewBox, currentColor stroke, 1.6px round caps + joins,',
    '// transparent fill. New topics that don\'t match any keyword fall',
    "// back to ICONS.chat.",
    'const ICONS = {',
]
for key, body in ICONS.items():
    lines.append(f'  {key}: {js_string(body)},')
lines.append('};')
lines.append('')
lines.append('export const CLEAVAGES = {')
for our_id, topics in result.items():
    if not topics: continue
    lines.append(f'  {our_id}: [')
    for t in topics:
        stances_lit = ', '.join(
            f'{k}: {("null" if v is None else js_string(v))}' for k, v in t['stances'].items()
        )
        lines.append(f'    {{ icon: ICONS.{t["icon_key"]}, title: {js_string(t["title"])}, stances: {{ {stances_lit} }} }},')
    lines.append('  ],')
lines.append('};')

(ROOT / 'js' / 'data' / 'cleavages.js').write_text('\n'.join(lines) + '\n', encoding='utf-8')

# ─── Diagnostics ─────────────────────────────────────────────────────────
print(f'Munis written: {len(result)}')
print(f'Total topics:  {sum(len(t) for t in result.values())}')
if unmapped_munis:
    print(f'\n⚠ Unmapped munis (no RÚV slug or no data): {len(unmapped_munis)}')
    for u in unmapped_munis:
        print(f'   - {u}')
if unmapped_parties:
    # Group by muni
    from collections import defaultdict
    by_muni = defaultdict(list)
    for muni, name in unmapped_parties:
        by_muni[muni].append(name)
    print(f'\n⚠ Unmapped parties (RÚV name didn\'t match our roster):')
    for muni, names in sorted(by_muni.items()):
        print(f'   {muni}: {", ".join(names)}')
