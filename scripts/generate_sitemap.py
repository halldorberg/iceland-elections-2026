#!/usr/bin/env python3
"""
Generate sitemap.xml covering:
  - Homepage (/)
  - All 61 municipality pages          /<muni>/
  - All party-in-muni pages            /<muni>/<party-slug>/
  - All candidate profile pages        /<muni>/<party-slug>/<candidate-slug>/

Each URL gets hreflang IS/EN/PL/x-default annotations. Phase 2 path-based
URL scheme (no more ?id=&party=&candidate=).
"""
import re, json, sys
from pathlib import Path

BASE = 'https://lydraedisveislan.is'
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from scripts.seo_slugs import party_slug, slugify  # noqa: E402

# ── Load municipalities ───────────────────────────────────────────────────────
muni_src = (ROOT / 'js/data/municipalities.js').read_text(encoding='utf-8')

munis = []
for m in re.finditer(
    r"\{\s*id:\s*'(\w+)'.*?name:\s*'([^']+)'.*?population:\s*(\d+).*?partyIds:\s*(\[[^\]]*\])",
    muni_src, re.DOTALL
):
    muni_id    = m.group(1)
    name       = m.group(2)
    population = int(m.group(3))
    party_ids  = re.findall(r"'([^']+)'", m.group(4))
    munis.append({'id': muni_id, 'name': name, 'pop': population, 'partyIds': party_ids})

# ── Load candidates ───────────────────────────────────────────────────────────
cand_src = (ROOT / 'js/data/candidates.js').read_text(encoding='utf-8')

# Build muni_id → var_name map from REAL_DATA
real_data = re.search(r'const REAL_DATA\s*=\s*\{([^}]+)\}', cand_src, re.DOTALL).group(1)
muni_var_map = {}
for m in re.finditer(r'(\w+):\s*([A-Z]+)\b', real_data):
    muni_var_map[m.group(1)] = m.group(2)

# Parse each var block → party → list of ballot numbers
var_data = {}
for cb in re.finditer(r'\bconst\s+([A-Z]{2,4})\s*=\s*\{', cand_src):
    var_name = cb.group(1)
    if var_name == 'REAL_DATA':
        continue
    start = cb.end() - 1
    depth, pos = 0, start
    while pos < len(cand_src):
        if cand_src[pos] == '{': depth += 1
        elif cand_src[pos] == '}':
            depth -= 1
            if depth == 0: break
        pos += 1
    block = cand_src[start:pos+1]
    party_data = {}
    for pm in re.finditer(r'\b([A-Z]{1,5})\s*:\s*\{', block):
        pc = pm.group(1)
        p_start = pm.end() - 1
        d2, pp = 0, p_start
        while pp < len(block):
            if block[pp] == '{': d2 += 1
            elif block[pp] == '}':
                d2 -= 1
                if d2 == 0: break
            pp += 1
        pb = block[p_start:pp+1]
        lm = re.search(r'\blist\s*:\s*\[', pb)
        if lm:
            ls = lm.end() - 1
            d3, lp = 0, ls
            while lp < len(pb):
                if pb[lp] == '[': d3 += 1
                elif pb[lp] == ']':
                    d3 -= 1
                    if d3 == 0: break
                lp += 1
            # Extract (ballot, name) so we can slugify candidate names for URLs.
            rows = re.findall(
                r"\[\s*(\d+)\s*,\s*'((?:[^'\\\\]|\\\\.)*)'",
                pb[ls:lp+1],
            )
            party_data[pc] = [(int(n), name.replace("\\\\'", "'")) for n, name in rows]
    if party_data:
        var_data[var_name] = party_data

# ── Priority helper ───────────────────────────────────────────────────────────
def muni_priority(pop):
    if pop >= 100000: return '1.0'
    if pop >= 20000:  return '0.9'
    if pop >= 5000:   return '0.8'
    if pop >= 1000:   return '0.7'
    return '0.6'

# ── Build XML ────────────────────────────────────────────────────────────────
def hreflang_block(base_url):
    """Build an hreflang block. base_url is the IS-default URL (path-based).
    EN and PL variants are derived by inserting /en/ or /pl/ after BASE."""
    # base_url looks like https://lydraedisveislan.is/<path>
    # Insert /en/ or /pl/ after the host.
    if base_url == BASE + '/':
        en_url = f'{BASE}/en/'
        pl_url = f'{BASE}/pl/'
    else:
        path = base_url[len(BASE):]  # starts with /
        en_url = f'{BASE}/en{path}'
        pl_url = f'{BASE}/pl{path}'
    return [
        f'    <xhtml:link rel="alternate" hreflang="is" href="{base_url}" />',
        f'    <xhtml:link rel="alternate" hreflang="en" href="{en_url}" />',
        f'    <xhtml:link rel="alternate" hreflang="pl" href="{pl_url}" />',
        f'    <xhtml:link rel="alternate" hreflang="x-default" href="{base_url}" />',
    ]


lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    '',
    '  <!-- ── Homepage ─────────────────────────────────────────────── -->',
    '  <url>',
    f'    <loc>{BASE}/</loc>',
    '    <changefreq>weekly</changefreq>',
    '    <priority>1.0</priority>',
    *hreflang_block(f'{BASE}/'),
    '  </url>',
    '',
]

n_munis = n_lists = n_candidates = 0

for muni in munis:
    mid      = muni['id']
    pop      = muni['pop']
    pids     = muni['partyIds']
    var_name = muni_var_map.get(mid)
    parties  = var_data.get(var_name, {}) if var_name else {}
    mp       = muni_priority(pop)

    lines.append(f'  <!-- ── {muni["name"]} ──────────────────────────────────── -->')

    # Municipality page  →  /<muni>/
    muni_url = f'{BASE}/{mid}/'
    lines += [
        '  <url>',
        f'    <loc>{muni_url}</loc>',
        '    <changefreq>weekly</changefreq>',
        f'    <priority>{mp}</priority>',
        *hreflang_block(muni_url),
        '  </url>',
    ]
    n_munis += 1

    # Party list pages  →  /<muni>/<party-slug>/
    for pid in pids:
        rows = parties.get(pid, [])  # list of (ballot, name) tuples
        pslug = party_slug(pid)
        party_url = f'{BASE}/{mid}/{pslug}/'
        lines += [
            '  <url>',
            f'    <loc>{party_url}</loc>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>0.6</priority>',
            *hreflang_block(party_url),
            '  </url>',
        ]
        n_lists += 1

        # Candidate profile pages  →  /<muni>/<party-slug>/<candidate-slug>/
        # Limit to top-6 ballot positions — bottom-of-list candidates have no
        # bio and won't rank anyway.
        for bn, name in rows:
            if bn > 6:
                continue
            cslug = slugify(name)
            cand_url = f'{BASE}/{mid}/{pslug}/{cslug}/'
            lines += [
                '  <url>',
                f'    <loc>{cand_url}</loc>',
                '    <changefreq>weekly</changefreq>',
                '    <priority>0.5</priority>',
                *hreflang_block(cand_url),
                '  </url>',
            ]
            n_candidates += 1

    lines.append('')

lines += ['</urlset>', '']

out = ROOT / 'sitemap.xml'
out.write_text('\n'.join(lines), encoding='utf-8')

total = 1 + n_munis + n_lists + n_candidates
print(f'Sitemap written: {out}')
print(f'  Homepage:        1')
print(f'  Municipality pages: {n_munis}')
print(f'  Party list pages:   {n_lists}')
print(f'  Candidate pages:    {n_candidates}')
print(f'  Total URLs:         {total}')
