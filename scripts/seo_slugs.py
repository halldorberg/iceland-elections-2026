"""
seo_slugs.py — Python mirror of js/data/party_slugs.js.

Used by scripts/build_static_pages.py and scripts/generate_sitemap.py.
Keep in sync with the JS module.
"""
import re

PARTY_CODE_TO_SLUG = {
    'D':   'sjalfstaedisflokkurinn',
    'B':   'framsoknarflokkurinn',
    'S':   'samfylkingin',
    'V':   'vinstri-graen',
    'A':   'vinstrid',
    'P':   'piratar',
    'M':   'midflokkurinn',
    'F':   'flokkur-folksins',
    'C':   'vidreisn',
    'J':   'sosialistar',
    'GB':  'gardabaejarlistinn',
    'AL':  'akureyrarlistinn',
    'L':   'l-listinn',
    'K':   'kex-frambod',
    'E':   'eyjalisti',
    'H':   'h-listinn',
    'VM':  'vinir-mosfellsbaejar',
    'OKH': 'okkar-hveragerdi',
    'SCS': 'seltjarnarneslistinn',
    'BBL': 'borgarbyggdarlisti',
    'G':   'godan-daginn',
    'R':   'okkar-borg',
    # Per-muni local lists.
    'FYRS': 'fyrir-samfelagid',
    'VOE':  'e-listinn',
    'VOL':  'l-listinn',
    'NPM':  'm-listi-samfelagsins',
    'NBO':  'oskalistinn',
    'NPV':  'v-listi-velferdar',
    'NRE':  'nytt-sjalfstaett-frambod',
    'RYA':  'a-listinn',
    'SKO':  'oflugt-samfelag',
    'MYA':  'listi-allra',
    'MYZ':  'listi-samfelagsins',
    'BST':  't-listinn',
    'BSP':  'th-listinn',
    'FLI':  'framfaralistinn',
    'FLT':  't-listinn-floa',
    'HRL':  'l-listinn',
    'GGA':  'a-listinn',
    'GGO':  'o-listinn-betri-sveit',
    'SGE':  'uppbyggingarlistinn',
    'SGL':  'samvinnulistinn',
    'EJF':  'f-listinn',
    'EJK':  'k-listinn',
    'HGG':  'groska',
    'HGH':  'h-listinn',
    'HBA':  'oll-saman',
    'NHV':  'ny-ofl',
    'SFL':  'byggdalistinn',
    'HFJK': 'kex-frambod',
    'FLS':  'framfaralisti-stykkisholms',
    'IBU':  'ibualistinn',
    'GFB':  'framsokn-samfylking',
    'GFD':  'sjalfstaedi-ohadir',
    'MMM':  'mattur-meyja-og-manna',
    'BBK':  'betri-bolungarvik',
    'FJL':  'fjardarlistinn',
    'FTL':  'framtidarlistinn',
    'NYS':  'nyrra-synar',
    'STV':  'sterkari-vesturbyggd',
    'VGV':  'vegvisir',
    'SBD':  'strandabandalagid',
    'ROA':  'raddir-okkar-allra',
    'THVA': 'a-listinn',
    'THVL': 'l-listinn',
    'THVN': 'n-listinn',
    'HVA':  'samhent-sveit',
    'HVB':  'ibuahreyfingin',
    'SVSS': 's-listinn',
    'SVSH': 'strond-til-framtidar',
    'SVSO': 'strondungur',
    'KJA':  'ibuar-i-kjos',
    'VOP':  'eitt-frambod',
    'TJN':  'eitt-frambod',
    'ARNA': 'a-listinn',
    'ARNS': 's-listinn',
}


def party_slug(code: str) -> str:
    return PARTY_CODE_TO_SLUG.get(code, code.lower())


_TRANS = str.maketrans({
    'ð': 'd', 'þ': 'th', 'æ': 'ae',
    'ö': 'o', 'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ý': 'y',
    'Ð': 'd', 'Þ': 'th', 'Æ': 'ae',
    'Ö': 'o', 'Á': 'a', 'É': 'e', 'Í': 'i', 'Ó': 'o', 'Ú': 'u', 'Ý': 'y',
})


def slugify(s: str) -> str:
    """Mirror of js/data/party_slugs.js slugify()."""
    if not s:
        return ''
    # 'th' for þ doesn't fit in str.translate (single char → single char), do it manually
    s = s.replace('þ', 'th').replace('Þ', 'th').replace('æ', 'ae').replace('Æ', 'ae')
    s = s.lower().translate(_TRANS)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s
