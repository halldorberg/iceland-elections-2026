#!/usr/bin/env python3
"""
Generate sitemap.xml covering:
  - Homepage
  - All 61 municipality pages
  - All party list pages  (?id=X&party=Y)
  - All candidate profile pages (?id=X&party=Y&candidate=N)
"""
import re, json
from pathlib import Path

BASE = 'https://lydraedisveislan.is'
ROOT = Path(__file__).parent.parent

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
            ballot_nos = re.findall(r'\[\s*(\d+)\s*,', pb[ls:lp+1])
            party_data[pc] = [int(n) for n in ballot_nos]
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
    """Build an hreflang block for a URL. base_url is the IS-default URL.
    Generates EN and PL variants by appending lang param."""
    sep = '&amp;' if '?' in base_url else '?'
    en_url = f'{base_url}{sep}lang=en'
    pl_url = f'{base_url}{sep}lang=pl'
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

    # Municipality page
    muni_url = f'{BASE}/municipality.html?id={mid}'
    lines += [
        '  <url>',
        f'    <loc>{muni_url}</loc>',
        '    <changefreq>weekly</changefreq>',
        f'    <priority>{mp}</priority>',
        *hreflang_block(muni_url),
        '  </url>',
    ]
    n_munis += 1

    # Party list pages
    for pid in pids:
        ballot_nos = parties.get(pid, [])
        party_url = f'{BASE}/municipality.html?id={mid}&amp;party={pid}'
        lines += [
            '  <url>',
            f'    <loc>{party_url}</loc>',
            '    <changefreq>weekly</changefreq>',
            '    <priority>0.6</priority>',
            *hreflang_block(party_url),
            '  </url>',
        ]
        n_lists += 1

        # Candidate profile pages
        for bn in ballot_nos:
            cand_url = f'{BASE}/municipality.html?id={mid}&amp;party={pid}&amp;candidate={bn}'
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
