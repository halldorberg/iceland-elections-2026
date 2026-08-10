#!/usr/bin/env python3
"""One-shot: upgrade 3 plain candidate rows to extended rows with news."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
CANDIDATES_JS = ROOT / "js" / "data" / "candidates.js"

missing = ['Auður Kjartansdóttir', 'Haraldur Benediktsson', 'Íris Edda Jónsdóttir']

arts_by_name = {}
for p in sorted((ROOT / 'scan_results').glob('news_2026-05-01_*.json')):
    d = json.load(open(p, encoding='utf-8'))
    for r in d.get('results', []):
        if r['name'] in missing:
            arts_by_name[r['name']] = r.get('new_articles', [])


def escape_js(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")


src = CANDIDATES_JS.read_text(encoding='utf-8')

for name, articles in arts_by_name.items():
    name_re = re.escape(escape_js(name))
    pattern = re.compile(
        r"^(\s+)\[(\d+),\s*'(" + name_re + r")',\s*'((?:[^'\\]|\\.)*)'\],$",
        re.MULTILINE
    )
    m = pattern.search(src)
    if not m:
        print(f'SKIP — could not match plain row for {name}')
        continue
    indent = m.group(1)
    ballot = m.group(2)
    nm = m.group(3)
    occ = m.group(4)

    news_lines = '\n'.join(
        f"{indent}    {{ title: '{escape_js(a['title'])}', url: '{a['url']}', source: '{escape_js(a.get('source', ''))}' }},"
        for a in articles
    )

    replacement = (
        f"{indent}[{ballot}, '{nm}', '{occ}', null, {{\n"
        f"{indent}  age: null,\n"
        f"{indent}  bio: null,\n"
        f"{indent}  heimild: [],\n"
        f"{indent}  interests: [],\n"
        f"{indent}  social: [],\n"
        f"{indent}  news: [\n"
        f"{news_lines}\n"
        f"{indent}  ],\n"
        f"{indent}}}],"
    )
    src = src[:m.start()] + replacement + src[m.end():]
    print(f'OK — upgraded {name} ({len(articles)} article(s))')

CANDIDATES_JS.write_text(src, encoding='utf-8')
print('Wrote candidates.js')
