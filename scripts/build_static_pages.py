#!/usr/bin/env python3
"""
build_static_pages.py — generate per-route stub HTML files for SEO.

For each (lang, muni) and (lang, muni, party) combination, emit a tiny HTML
file with the right <title>, <meta>, <link rel=canonical>, hreflang and
JSON-LD structured data. The body is the SAME shell as municipality.html;
the existing JS hydrates the page on top.

Output structure (~3 KB per file, ~730 files total):

  /<muni>/index.html                          IS muni page
  /en/<muni>/index.html                       EN muni page
  /pl/<muni>/index.html                       PL muni page
  /<muni>/<party-slug>/index.html             IS muni-party page
  /en/<muni>/<party-slug>/index.html          EN
  /pl/<muni>/<party-slug>/index.html          PL

Run after data changes (or whenever party lookups change). Idempotent —
safe to re-run; only writes files that change.

  python scripts/build_static_pages.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from scripts.seo_slugs import party_slug, slugify  # noqa: E402

CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"
MUNICIPALITIES_JS = ROOT / "js" / "data" / "municipalities.js"
TEMPLATE = ROOT / "municipality.html"
BASE = "https://lydraedisveislan.is"

# Text strings per language — kept in this file to avoid shipping them with the
# main JS bundle. Mirror the i18n keys used in municipality.js updatePageMeta.
LOCALES = {
    'is': {
        'lang_html': 'is',
        'og_locale': 'is_IS',
        'election_phrase': 'Kosningar 2026',
        'compare_lead': lambda m: (
            f'{m} — sjá öll framboð, frambjóðendur og stefnumál fyrir '
            f'sveitarstjórnarkosningarnar 16. maí 2026. Berðu saman flokka og kjóstu upplýst.'
        ),
        'party_lead': lambda p, m: (
            f'{p} — {m} — stefnumál og frambjóðendur fyrir sveitarstjórnarkosningar 2026. '
            f'Berðu listann saman við önnur framboð.'
        ),
        'candidate_lead': lambda n, occ, p, m: (
            f'{n} — {p} — {m}. {occ}. Frambjóðandi í sveitarstjórnarkosningum 2026. '
            f'Sjá æviágrip, áherslur og fréttir.'
        ),
    },
    'en': {
        'lang_html': 'en',
        'og_locale': 'en_US',
        'election_phrase': '2026 Local Elections',
        'compare_lead': lambda m: (
            f'{m} — see every party, candidate and platform for the May 16, 2026 local elections. '
            f'Compare them in one place.'
        ),
        'party_lead': lambda p, m: (
            f'{p} — {m} — platform and candidates for the 2026 local elections. '
            f'Compare with other parties on the ballot.'
        ),
        'candidate_lead': lambda n, occ, p, m: (
            f'{n} — {p} — {m}. {occ}. Candidate in the 2026 local elections. '
            f'See bio, focus areas and news.'
        ),
    },
    'pl': {
        'lang_html': 'pl',
        'og_locale': 'pl_PL',
        'election_phrase': 'Wybory samorządowe 2026',
        'compare_lead': lambda m: (
            f'{m} — zobacz wszystkie partie, kandydatów i programy przed wyborami samorządowymi '
            f'16 maja 2026. Porównaj je w jednym miejscu.'
        ),
        'party_lead': lambda p, m: (
            f'{p} — {m} — program i kandydaci w wyborach samorządowych 2026. '
            f'Porównaj z innymi listami.'
        ),
        'candidate_lead': lambda n, occ, p, m: (
            f'{n} — {p} — {m}. {occ}. Kandydat w wyborach samorządowych 2026. '
            f'Zobacz biografię, priorytety i aktualności.'
        ),
    },
}


def parse_candidates_top_n(n: int = 6) -> dict:
    """Walk candidates.js and return:
        { (muni_slug, party_code) : [ {ballot, name, occupation, photo, bio_first_sentence}, ... ] }
    Limited to ballot positions 1..n. Photo paths are normalised to root-absolute.
    """
    src = CANDIDATES_JS.read_text(encoding='utf-8')
    real_data = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', src, re.DOTALL).group(1)
    var_to_slug = {const_id: slug for slug, const_id
                   in re.findall(r'(\w+)\s*:\s*([A-Z_]+)\s*,', real_data)}
    out = {}
    for cb in re.finditer(r'\bconst\s+([A-Z][A-Z0-9_]+)\s*=\s*\{', src):
        var_name = cb.group(1)
        if var_name == 'REAL_DATA':
            continue
        muni_slug = var_to_slug.get(var_name)
        if not muni_slug:
            continue
        # Walk to end of var block
        start, depth = cb.end() - 1, 0
        pos = start
        while pos < len(src):
            if src[pos] == '{':
                depth += 1
            elif src[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = src[start:pos + 1]
        # Walk parties
        for pm in re.finditer(r'\b([A-Z][A-Z0-9]{0,3})\s*:\s*\{', block):
            pc = pm.group(1)
            p_start, d2 = pm.end() - 1, 0
            pp = p_start
            while pp < len(block):
                if block[pp] == '{':
                    d2 += 1
                elif block[pp] == '}':
                    d2 -= 1
                    if d2 == 0:
                        break
                pp += 1
            pb = block[p_start:pp + 1]
            lm = re.search(r'\blist\s*:\s*\[', pb)
            if not lm:
                continue
            ls, d3 = lm.end() - 1, 0
            lp = ls
            while lp < len(pb):
                if pb[lp] == '[':
                    d3 += 1
                elif pb[lp] == ']':
                    d3 -= 1
                    if d3 == 0:
                        break
                lp += 1
            list_block = pb[ls:lp + 1]
            # Walk each candidate row by bracket-balancing — extended blocks
            # contain nested {} and [] which a flat regex can't span.
            rows = []
            i = 0
            while i < len(list_block):
                # Find next "[<digit>" at row depth — capture the [ as group 1 so
                # row_start points at it.
                m = re.search(r"\n\s+(\[)(\d+)\s*,\s*'", list_block[i:])
                if not m:
                    break
                row_start = i + m.start(1)  # position of '['
                ballot = int(m.group(2))
                # Walk brackets to find matching ']'
                d, k = 0, row_start
                while k < len(list_block):
                    ch = list_block[k]
                    if ch == "'":
                        # Skip string literal (handle escaped ')
                        k += 1
                        while k < len(list_block):
                            if list_block[k] == "\\":
                                k += 2
                                continue
                            if list_block[k] == "'":
                                break
                            k += 1
                    elif ch == '[':
                        d += 1
                    elif ch == ']':
                        d -= 1
                        if d == 0:
                            break
                    k += 1
                row_text = list_block[row_start:k + 1]
                i = k + 1  # advance past this row
                if ballot > n:
                    continue
                # Within row_text, parse name + occupation + photo + bio
                fm = re.match(
                    r"\[\s*\d+\s*,\s*"
                    r"'((?:[^'\\]|\\.)*?)'\s*,\s*"
                    r"'((?:[^'\\]|\\.)*?)'"
                    r"(?:\s*,\s*(null|'(?:[^'\\]|\\.)*?'))?",
                    row_text, re.DOTALL,
                )
                if not fm:
                    continue
                name = fm.group(1).replace("\\'", "'")
                occupation = fm.group(2).replace("\\'", "'")
                photo_raw = fm.group(3)
                photo = None
                if photo_raw and photo_raw != 'null':
                    photo = photo_raw.strip("'").replace("\\'", "'")
                # Bio anywhere in the row's extended block — truncated to 160
                # chars at word boundary. Avoid first-sentence splitting because
                # Icelandic dates like "23. maí 1984" trip a naive regex.
                bio = None
                bm = re.search(r"bio\s*:\s*'((?:[^'\\]|\\.)*)'", row_text, re.DOTALL)
                if bm:
                    bio_full = bm.group(1).replace("\\'", "'")
                    if len(bio_full) <= 160:
                        bio = bio_full
                    else:
                        cut = bio_full[:157]
                        # Trim back to last word boundary
                        sp = cut.rfind(' ')
                        bio = (cut[:sp] if sp > 100 else cut) + '…'
                rows.append({
                    'ballot': ballot, 'name': name, 'occupation': occupation,
                    'photo': photo, 'bio': bio,
                })
            if rows:
                out[(muni_slug, pc)] = sorted(rows, key=lambda r: r['ballot'])
    return out


def parse_munis():
    """Return list of dicts: {id, name, region, population, lat, lng, party_codes}."""
    src = MUNICIPALITIES_JS.read_text(encoding='utf-8')
    out = []
    pat = re.compile(
        r"\{\s*id:\s*'(\w+)'\s*,"
        r"\s*name:\s*'([^']+)'\s*,"
        r"\s*region:\s*'([^']+)'\s*,"
        r"\s*population:\s*(\d+)\s*,"
        r"\s*coords:\s*\{\s*lat:\s*([\d\.-]+)\s*,\s*lng:\s*([\d\.-]+)\s*\}\s*,"
        r"\s*partyIds:\s*\[([^\]]*)\]",
        re.DOTALL,
    )
    for m in pat.finditer(src):
        out.append({
            'id': m.group(1),
            'name': m.group(2),
            'region': m.group(3),
            'population': int(m.group(4)),
            'lat': float(m.group(5)),
            'lng': float(m.group(6)),
            'party_codes': re.findall(r"'([^']+)'", m.group(7)),
        })
    return out


def party_display_name(code: str) -> str:
    """Best-effort party display name. Local lists fall back to their tagline
    or just the code prefixed."""
    NATIONAL = {
        'D': 'Sjálfstæðisflokkurinn', 'B': 'Framsóknarflokkurinn',
        'S': 'Samfylkingin', 'V': 'Vinstri Græn',
        'A': 'Vinstrið', 'P': 'Píratar', 'M': 'Miðflokkurinn',
        'F': 'Flokkur fólksins', 'C': 'Viðreisn', 'J': 'Sósíalistar',
        'GB': 'Garðabæjarlistinn', 'AL': 'Akureyrarlistinn',
        'L': 'L-listinn', 'K': 'Kex framboð', 'E': 'Eyjalisti',
        'H': 'H-listinn', 'VM': 'Vinir Mosfellsbæjar',
        'OKH': 'Okkar Hveragerði', 'SCS': 'Seltjarnarneslistinn',
        'BBL': 'Borgarbyggðarlisti', 'G': 'Góðan daginn',
        'R': 'Okkar borg',
    }
    return NATIONAL.get(code, code + '-listinn')


import json as json_mod  # avoid shadowing if someone adds `json` lookups


# ── JSON-LD generators ────────────────────────────────────────────────────────

ELECTION_DATE = "2026-05-16"  # ISO date
ELECTION_NAME_BY_LANG = {
    'is': 'Sveitarstjórnarkosningar 2026',
    'en': '2026 Icelandic Local Elections',
    'pl': 'Wybory samorządowe na Islandii 2026',
}


def _ld(obj):
    """Serialize JSON-LD compactly."""
    return json_mod.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def jsonld_block(obj):
    """Wrap an object (or list) in a JSON-LD <script>."""
    return f'<script type="application/ld+json">{_ld(obj)}</script>'


def jsonld_website(lang: str) -> str:
    return jsonld_block({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": BASE + ('/' if lang == 'is' else f'/{lang}/'),
        "name": "Lýðræðisveislan",
        "inLanguage": {'is': 'is-IS', 'en': 'en-US', 'pl': 'pl-PL'}[lang],
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": f"{BASE}/?q={{search_term_string}}",
            },
            "query-input": "required name=search_term_string",
        },
    })


def jsonld_breadcrumbs(items):
    """items: list of {name, url}. Position 1 is root."""
    return jsonld_block({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": it["name"],
                "item": it["url"],
            }
            for i, it in enumerate(items)
        ],
    })


def jsonld_muni(muni: dict, lang: str) -> str:
    return jsonld_block({
        "@context": "https://schema.org",
        "@type": "Place",
        "name": muni["name"],
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": muni["lat"],
            "longitude": muni["lng"],
        },
        "containedInPlace": {
            "@type": "Country",
            "name": "Ísland" if lang == 'is' else 'Iceland' if lang == 'en' else 'Islandia',
        },
        "additionalProperty": {
            "@type": "PropertyValue",
            "name": {'is': 'Íbúafjöldi', 'en': 'Population', 'pl': 'Liczba mieszkańców'}[lang],
            "value": muni["population"],
        },
    })


def jsonld_party(party_name: str, muni_name: str, party_url: str, lang: str) -> str:
    return jsonld_block({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": f"{party_name} — {muni_name}",
        "url": party_url,
        "subOrganizationOf": {
            "@type": "Organization",
            "name": party_name,
        },
        "areaServed": {
            "@type": "Place",
            "name": muni_name,
        },
    })


def jsonld_person(name: str, occupation: str, party_name: str, party_url: str,
                  muni_name: str, photo_url: str = None, bio: str = None) -> str:
    obj = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": name,
        "jobTitle": occupation,
        "affiliation": {
            "@type": "Organization",
            "name": f"{party_name} — {muni_name}",
            "url": party_url,
        },
        "homeLocation": {
            "@type": "Place",
            "name": muni_name,
        },
    }
    if photo_url:
        obj["image"] = photo_url
    if bio:
        obj["description"] = bio
    return jsonld_block(obj)


def jsonld_event(muni_name: str, lang: str) -> str:
    return jsonld_block({
        "@context": "https://schema.org",
        "@type": "Event",
        "name": ELECTION_NAME_BY_LANG[lang] + f" — {muni_name}",
        "startDate": ELECTION_DATE,
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {
            "@type": "Place",
            "name": muni_name,
            "address": {
                "@type": "PostalAddress",
                "addressLocality": muni_name,
                "addressCountry": "IS",
            },
        },
        "organizer": {
            "@type": "GovernmentOrganization",
            "name": "Landskjörstjórn",
            "url": "https://island.is/v/sveitarstjornarkosningar-2026",
        },
    })


def stub_html(template: str, *, locale: dict, title: str, desc: str, canonical: str,
              hreflang_map: dict, og_image: str = None,
              jsonld_blocks: list = None) -> str:
    """Build an HTML stub by rewriting the head of municipality.html."""
    # Replace <html lang="...">
    html = re.sub(r'<html\s+lang="[^"]*"', f'<html lang="{locale["lang_html"]}"', template, count=1)

    # Replace <title>
    html = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', html, count=1)

    # Replace meta description
    html = re.sub(
        r'<meta\s+name="description"\s+content="[^"]*"\s*/>',
        f'<meta name="description" content="{desc}" />',
        html, count=1,
    )

    # Strip any existing canonical/hreflang stubs (the template ships placeholders).
    # [^>]* not [^/]* — URLs contain slashes.
    html = re.sub(r'\s*<link\s+rel="canonical"[^>]*/>', '', html)
    html = re.sub(r'\s*<link\s+rel="alternate"\s+hreflang="[^"]*"[^>]*/>', '', html)
    # Strip the explanatory comment too (only on the line above the template canonical)
    html = re.sub(r'\s*<!--\s*Canonical \(overridden[^>]*-->', '', html)
    html = re.sub(r'\s*<!--\s*hreflang language alternates[^>]*-->', '', html)

    # Insert canonical + hreflang block after <title>
    head_inject = f'\n  <link rel="canonical" id="canonical-link" href="{canonical}" />'
    for lang_code, alt_url in hreflang_map.items():
        head_inject += f'\n  <link rel="alternate" hreflang="{lang_code}" id="hreflang-{lang_code}" href="{alt_url}" />'
    head_inject += f'\n  <link rel="alternate" hreflang="x-default" id="hreflang-default" href="{hreflang_map["is"]}" />'
    html = html.replace('</title>', f'</title>{head_inject}', 1)

    # Replace OG title/description/url/locale  ([^>]* — URLs contain slashes)
    html = re.sub(r'<meta\s+property="og:title"[^>]*/>', f'<meta property="og:title" content="{title}" />', html, count=1)
    html = re.sub(r'<meta\s+property="og:description"[^>]*/>', f'<meta property="og:description" content="{desc}" />', html, count=1)
    html = re.sub(r'<meta\s+property="og:url"[^>]*/>', f'<meta property="og:url" content="{canonical}" />', html, count=1)
    html = re.sub(r'<meta\s+property="og:locale"\s+content="[^"]*"\s*/>', f'<meta property="og:locale" content="{locale["og_locale"]}" />', html, count=1)
    if og_image:
        html = re.sub(r'<meta\s+property="og:image"[^>]*/>', f'<meta property="og:image" content="{og_image}" />', html, count=1)

    # Fix relative resource paths — stubs live in subdirectories so all asset
    # paths in the original municipality.html (which is at /) need to be made
    # absolute (root-relative).
    html = re.sub(r'href="(?!/|https?://|#|data:|mailto:)([^"]+)"', r'href="/\1"', html)
    html = re.sub(r'src="(?!/|https?://|data:)([^"]+)"', r'src="/\1"', html)

    # Inject JSON-LD blocks before </head>
    if jsonld_blocks:
        ld = '\n  '.join(jsonld_blocks)
        html = html.replace('</head>', f'  {ld}\n</head>', 1)

    return html


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    template = TEMPLATE.read_text(encoding='utf-8')
    home_template = (ROOT / 'index.html').read_text(encoding='utf-8')
    munis = parse_munis()

    written = 0
    skipped = 0

    # ── Home page locale variants /en/ and /pl/ ───────────────────
    # The IS home is already at /index.html. Generate EN and PL copies
    # whose <html lang>, head meta, and OG match the locale. The body
    # is identical; map.js's locale detection handles dynamic UI text.
    HOME_LOCALES = {
        'en': {
            'title': "Lýðræðisveislan 2026 — Iceland's Local Elections",
            'desc':  "Find every party, candidate and platform for Iceland's 2026 local elections on May 16. Compare them all in one place — in English, Icelandic or Polish.",
            'lang_html': 'en', 'og_locale': 'en_US',
        },
        'pl': {
            'title': 'Lýðræðisveislan 2026 — Wybory samorządowe w Islandii',
            'desc':  'Wszystkie partie, kandydaci i programy w wyborach samorządowych 16 maja 2026 w Islandii. W jednym miejscu — po polsku, islandzku lub angielsku.',
            'lang_html': 'pl', 'og_locale': 'pl_PL',
        },
    }
    for lang, hloc in HOME_LOCALES.items():
        hreflang_map = {
            'is': f'{BASE}/',
            'en': f'{BASE}/en/',
            'pl': f'{BASE}/pl/',
        }
        canonical = hreflang_map[lang]
        ld_blocks = [jsonld_website(lang)]
        html = stub_html(home_template, locale=hloc, title=hloc['title'], desc=hloc['desc'],
                         canonical=canonical, hreflang_map=hreflang_map,
                         jsonld_blocks=ld_blocks)
        out_dir = ROOT / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'index.html'
        existing = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
        if existing != html:
            out_path.write_text(html, encoding='utf-8')
            written += 1
        else:
            skipped += 1

    for muni_dict in munis:
        muni_id = muni_dict['id']
        muni_name = muni_dict['name']
        party_codes = muni_dict['party_codes']
        # ── Per-language muni page stubs ─────────────────────────
        for lang in ('is', 'en', 'pl'):
            loc = LOCALES[lang]
            title = f'{muni_name} — {loc["election_phrase"]}'
            if len(title) > 60:
                title = title[:57] + '…'
            desc = loc['compare_lead'](muni_name)

            # hreflang absolute URLs
            hreflang_map = {
                'is': f'{BASE}/{muni_id}/',
                'en': f'{BASE}/en/{muni_id}/',
                'pl': f'{BASE}/pl/{muni_id}/',
            }
            canonical = hreflang_map[lang]
            out_dir = ROOT / (lang if lang != 'is' else '') / muni_id
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / 'index.html'

            ld_blocks = [
                jsonld_breadcrumbs([
                    {"name": {'is': 'Heim', 'en': 'Home', 'pl': 'Strona główna'}[lang],
                     "url": f'{BASE}/' + ('' if lang == 'is' else f'{lang}/')},
                    {"name": muni_name, "url": canonical},
                ]),
                jsonld_muni(muni_dict, lang),
                jsonld_event(muni_name, lang),
            ]
            html = stub_html(template, locale=loc, title=title, desc=desc,
                             canonical=canonical, hreflang_map=hreflang_map,
                             jsonld_blocks=ld_blocks)
            existing = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
            if existing != html:
                out_path.write_text(html, encoding='utf-8')
                written += 1
            else:
                skipped += 1

        # ── Per-language muni-party stubs ───────────────────────
        for code in party_codes:
            slug = party_slug(code)
            party_name = party_display_name(code)
            for lang in ('is', 'en', 'pl'):
                loc = LOCALES[lang]
                title = f'{party_name} — {muni_name} — {loc["election_phrase"]}'
                if len(title) > 60:
                    title = title[:57] + '…'
                desc = loc['party_lead'](party_name, muni_name)

                hreflang_map = {
                    'is': f'{BASE}/{muni_id}/{slug}/',
                    'en': f'{BASE}/en/{muni_id}/{slug}/',
                    'pl': f'{BASE}/pl/{muni_id}/{slug}/',
                }
                canonical = hreflang_map[lang]
                out_dir = ROOT / (lang if lang != 'is' else '') / muni_id / slug
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / 'index.html'

                muni_url = f'{BASE}/{muni_id}/' if lang == 'is' else f'{BASE}/{lang}/{muni_id}/'
                ld_blocks = [
                    jsonld_breadcrumbs([
                        {"name": {'is': 'Heim', 'en': 'Home', 'pl': 'Strona główna'}[lang],
                         "url": f'{BASE}/' + ('' if lang == 'is' else f'{lang}/')},
                        {"name": muni_name, "url": muni_url},
                        {"name": party_name, "url": canonical},
                    ]),
                    jsonld_party(party_name, muni_name, canonical, lang),
                ]
                html = stub_html(template, locale=loc, title=title, desc=desc,
                                 canonical=canonical, hreflang_map=hreflang_map,
                                 jsonld_blocks=ld_blocks)
                existing = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
                if existing != html:
                    out_path.write_text(html, encoding='utf-8')
                    written += 1
                else:
                    skipped += 1

    # ── Per-candidate stubs (top-6 ballot positions per party) ──────────
    # These give Google a 200 status + route-specific Person JSON-LD + portrait
    # og:image instead of the 404.html SPA fallback. Adds ~1k × 3 = ~3k stubs.
    candidates_by_party = parse_candidates_top_n(n=6)
    for muni_dict in munis:
        muni_id = muni_dict['id']
        muni_name = muni_dict['name']
        for code in muni_dict['party_codes']:
            party_slug_str = party_slug(code)
            party_name = party_display_name(code)
            rows = candidates_by_party.get((muni_id, code), [])
            for cand in rows:
                cname = cand['name']
                cslug = slugify(cname)
                if not cslug:
                    continue
                photo_abs = None
                if cand['photo']:
                    p = cand['photo']
                    if not (p.startswith('http') or p.startswith('/')):
                        p = '/' + p
                    photo_abs = (BASE + p) if not p.startswith('http') else p
                for lang in ('is', 'en', 'pl'):
                    loc = LOCALES[lang]
                    title = f'{cname} — {party_name} — {muni_name}'
                    if len(title) > 60:
                        title = title[:57] + '…'
                    desc = loc['candidate_lead'](cname, cand['occupation'], party_name, muni_name)
                    if cand.get('bio'):
                        desc = cand['bio']  # use real bio first sentence as description if present
                    if len(desc) > 160:
                        desc = desc[:157] + '…'
                    hreflang_map = {
                        'is': f'{BASE}/{muni_id}/{party_slug_str}/{cslug}/',
                        'en': f'{BASE}/en/{muni_id}/{party_slug_str}/{cslug}/',
                        'pl': f'{BASE}/pl/{muni_id}/{party_slug_str}/{cslug}/',
                    }
                    canonical = hreflang_map[lang]
                    party_url = f'{BASE}/{muni_id}/{party_slug_str}/' if lang == 'is' \
                        else f'{BASE}/{lang}/{muni_id}/{party_slug_str}/'
                    muni_url = f'{BASE}/{muni_id}/' if lang == 'is' \
                        else f'{BASE}/{lang}/{muni_id}/'
                    home_url = f'{BASE}/' if lang == 'is' else f'{BASE}/{lang}/'
                    ld_blocks = [
                        jsonld_breadcrumbs([
                            {"name": {'is': 'Heim', 'en': 'Home', 'pl': 'Strona główna'}[lang],
                             "url": home_url},
                            {"name": muni_name, "url": muni_url},
                            {"name": party_name, "url": party_url},
                            {"name": cname, "url": canonical},
                        ]),
                        jsonld_person(
                            name=cname,
                            occupation=cand['occupation'],
                            party_name=party_name,
                            party_url=party_url,
                            muni_name=muni_name,
                            photo_url=photo_abs,
                            bio=cand.get('bio'),
                        ),
                    ]
                    out_dir = ROOT / (lang if lang != 'is' else '') / muni_id / party_slug_str / cslug
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_path = out_dir / 'index.html'
                    html = stub_html(template, locale=loc, title=title, desc=desc,
                                     canonical=canonical, hreflang_map=hreflang_map,
                                     og_image=photo_abs, jsonld_blocks=ld_blocks)
                    existing = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
                    if existing != html:
                        out_path.write_text(html, encoding='utf-8')
                        written += 1
                    else:
                        skipped += 1

    print(f'Wrote {written} stubs ({skipped} unchanged) across {len(munis)} munis.')


if __name__ == '__main__':
    main()
