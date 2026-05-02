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
    },
}


def parse_munis():
    """Return list of (muni_id, muni_name, party_codes_in_order) tuples."""
    src = MUNICIPALITIES_JS.read_text(encoding='utf-8')
    out = []
    for m in re.finditer(
        r"\{\s*id:\s*'(\w+)'.*?name:\s*'([^']+)'.*?partyIds:\s*\[([^\]]*)\]",
        src, re.DOTALL
    ):
        muni_id = m.group(1)
        muni_name = m.group(2)
        party_codes = re.findall(r"'([^']+)'", m.group(3))
        out.append((muni_id, muni_name, party_codes))
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
        'BBL': 'Borgarbyggðarlisti', 'G': 'Góðir Reykjavík',
        'R': 'Röðull',
    }
    return NATIONAL.get(code, code + '-listinn')


def stub_html(template: str, *, locale: dict, title: str, desc: str, canonical: str,
              hreflang_map: dict, og_image: str = None) -> str:
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
        # Reuse stub_html — but pass home_template instead of municipality template
        html = stub_html(home_template, locale=hloc, title=hloc['title'], desc=hloc['desc'],
                         canonical=canonical, hreflang_map=hreflang_map)
        out_dir = ROOT / lang
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / 'index.html'
        existing = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
        if existing != html:
            out_path.write_text(html, encoding='utf-8')
            written += 1
        else:
            skipped += 1

    for muni_id, muni_name, party_codes in munis:
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

            html = stub_html(template, locale=loc, title=title, desc=desc,
                             canonical=canonical, hreflang_map=hreflang_map)
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

                html = stub_html(template, locale=loc, title=title, desc=desc,
                                 canonical=canonical, hreflang_map=hreflang_map)
                existing = out_path.read_text(encoding='utf-8') if out_path.exists() else ''
                if existing != html:
                    out_path.write_text(html, encoding='utf-8')
                    written += 1
                else:
                    skipped += 1

    print(f'Wrote {written} stubs ({skipped} unchanged) across {len(munis)} munis.')


if __name__ == '__main__':
    main()
