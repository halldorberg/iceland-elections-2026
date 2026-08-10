"""Rewrite Vinir Mos bios from 1st person to concise 3rd-person."""
import json, sys, io, os
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')

env = ROOT / '.env'
if env.exists():
    for line in env.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI
client = OpenAI()
MODEL = 'gpt-5.4'

SYS = """Endurskrifaðu eftirfarandi sjálfslýsingu frambjóðanda úr fyrstu persónu yfir í þriðju persónu, samfellt í 2-4 málsgreinar (~80-150 orð). Notaðu fullt nafn frambjóðandans í fyrstu setningu, eftir það "hann" eða "hún" eftir kyni. Haltu öllum staðreyndum úr upprunalegri lýsingu — starfsheiti, menntun, fyrri störf, fjölskylda, áhugamál, hverju þeir eru þátttakendur í. Ekki finna upp staðreyndir. Bættu við í lokin: "Hann/hún skipar X. sæti á lista Vina Mosfellsbæjar (L-lista) fyrir sveitarstjórnarkosningarnar 2026."  Skilaðu aðeins æviágripi án gæsalappa eða annars formgerðar."""

cands = json.load(open(ROOT / 'temp' / 'vinirmos_processed.json', encoding='utf-8'))
out = []
for c in cands:
    bio = c['bio'].strip()
    if not bio:
        c['bio_3p'] = ''
        out.append(c)
        continue
    user = f"Frambjóðandi: {c['name']}\nSæti: {c['ballot']}\nStarf: {c['occupation']}\n\nLýsing í fyrstu persónu:\n{bio}"
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{'role':'system','content':SYS},{'role':'user','content':user}],
        )
        new = resp.choices[0].message.content.strip()
        c['bio_3p'] = new
        print(f'  [{c["ballot"]:2d}] {c["name"]}: ok ({len(new)} chars)')
    except Exception as e:
        print(f'  [{c["ballot"]:2d}] {c["name"]}: ERR {e}')
        c['bio_3p'] = ''
    out.append(c)

json.dump(out, open(ROOT / 'temp' / 'vinirmos_processed.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('\nupdated temp/vinirmos_processed.json')
