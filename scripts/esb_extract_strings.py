# coding: utf-8
"""Extract all translatable ESB content strings into translations/esb_is.json."""
import io, json, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SHY = '­'

src = io.open(ROOT / 'js' / 'esb-data.js', encoding='utf-8').read()
# Evaluate the JS object literal via json-ish conversion is fragile; use node instead.
import subprocess
data_json = subprocess.run(
    ['node', '-e', "const fs=require('fs');const src=fs.readFileSync('js/esb-data.js','utf8');const DATA=new Function(src+';return DATA;')();process.stdout.write(JSON.stringify(DATA))"],
    capture_output=True, text=True, encoding='utf-8', cwd=str(ROOT)).stdout
DATA = json.loads(data_json)

out = {}
out['note'] = DATA['note']
for side in ('ja', 'nei'):
    for m_i, m in enumerate(DATA['movements'][side]):
        out[f'mv.{side}.{m_i}.description'] = m['description']
    for sp_i, sp in enumerate(DATA['spokes'][side]):
        out[f'spoke.{side}.{sp_i}.role'] = sp['role']
    for a in DATA['arguments'][side]:
        out[f'arg.{a["key"]}.title'] = a['title'].replace(SHY, '')
        out[f'arg.{a["key"]}.text'] = a['text']
for i, art in enumerate(DATA['articles']):
    out[f'art.{i}.title'] = art['title']
    out[f'art.{i}.summary'] = art['summary']

for name in ('details_ja', 'details_nei'):
    d = json.load(io.open(ROOT / 'scripts' / f'{name}.json', encoding='utf-8'))
    for k, paras in d.items():
        for p_i, p in enumerate(paras):
            out[f'detail.{k}.{p_i}'] = p

for name in ('motrok_ja1', 'motrok_ja2', 'motrok_nei1', 'motrok_nei2'):
    d = json.load(io.open(ROOT / 'scripts' / f'{name}.json', encoding='utf-8'))
    for k, items in d.items():
        for m_i, m in enumerate(items):
            out[f'motrok.{k}.{m_i}.title'] = m['title']
            out[f'motrok.{k}.{m_i}.text'] = m['text']

(ROOT / 'translations').mkdir(exist_ok=True)
with io.open(ROOT / 'translations' / 'esb_is.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f'{len(out)} strings extracted')
