"""Re-merge RÚV bios with stricter prompt: no editorializing.
Keeps natural tone but forbids inferences not anchored in source.

Usage:
  python temp/remerge_strict.py --pilot 5         # test on 5 candidates
  python temp/remerge_strict.py                   # full re-run
  python temp/remerge_strict.py --only "0000-C-20"  # specific RÚV ID
"""
from __future__ import annotations
import argparse, json, sys, io, os, re, time
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

SYSTEM = """\
Þú ert að taka saman æviágrip um íslenskan sveitarstjórnarframbjóðanda. Skrifaðu
samfellt málsgreinar á íslensku (250–400 orð, 2–4 málsgreinar) sem sameinar
(a) núverandi æviágrip ef það er til staðar — ALLT efni úr því skal halda sér —
við (b) ný atriði úr svörum frambjóðandans á kosningaprófi RÚV.

ALGJÖR REGLA: notaðu eingöngu staðreyndir sem koma orðrétt fram í heimildinni.
Ef RÚV-svarið segir aðeins "Ensku og hollensku" þá skaltu skrifa "talar ensku
og hollensku auk íslensku" — EKKI bæta við „sem endurspeglar víðsýni" eða
"sem ber vott um fjölbreytta reynslu" eða öðru slíku innskoti.

BANNAÐ er að:
  - draga ályktanir um persónueinkenni (víðsýn, framsýn, reynd, kraftmikil,
    ástríðufull, þjálfað leiðtogahæfni, sterk skuldbinding o.s.frv.) nema
    nákvæmlega það orð birtist í heimildinni.
  - skrifa setningar sem byrja á "...sem endurspeglar/sýnir/varpar ljósi á/
    ber vott um/gefur til kynna/segir okkur að..." (engin túlkun á því HVAÐ
    staðreyndir þýða).
  - skrifa "...sem hún nýtir í...", "...sem skipar stóran sess í...",
    "...sem henni er hjartans mál" o.s.frv. nema slíkt orðalag birtist
    í heimildinni.
  - búa til metnaðar- eða framtíðarsýnar-yfirlýsingar sem ekki standa
    í svörunum.
  - bæta við lýsingarorðum eins og "ástríðufullur", "framsækin", "víðsýn",
    "sterk", "tryggur", "öflug", "kraftmikill", o.s.frv. nema þau standi
    skýrt í heimildinni.

LEYFILEGT er:
  - hlýr, eðlilegur og persónulegur tónn ef hann lifir aðeins af staðreyndum
    sem standa beint í svörunum (t.d. ef frambjóðandi nefnir „uppáhaldsbók"
    má segja „heldur sérstaklega upp á bókina X").
  - að nota þriðju persónu (hann/hún) og fullt nafn í fyrstu setningu.
  - að flétta saman starfi, fjölskyldu, áhugamálum, framtíðarsýn fyrir
    sveitarfélagið og fyrirmynd í pólitík eins og þau koma fram í svörunum.

Mikilvægt:
  - Allar staðreyndir úr gamla æviágripinu þurfa að birtast aftur í þeirri
    nýju (orðalagi má breyta), aldrei taka neitt út.
  - Forðastu „eldri borgari" sem starfsheiti — segðu „kominn á eftirlaun"
    eða „fyrrverandi <starf>".
  - Skiptu textanum upp í 2–4 málsgreinar.

Skilaðu JSON með nákvæmlega þessari skipan:
{
  "new_bio": "<merged paragraph(s)>",
  "fact_check": [
    {
      "statement": "<orðrétt setning úr nýja æviágripinu sem byggist á NÝJU efni úr RÚV>",
      "ruv_quote": "<beint orðrétta tilvitnun úr RÚV-svari sem styður þessa setningu>"
    }
  ]
}

fact_check skal aðeins ná yfir nýjar staðreyndir úr RÚV (ekki úr gamla
æviágripinu). Hver tilvitnun skal vera orðrétt eins og hún stendur í RÚV.
"""

def build_user(name, muni_name, party_name, old_bio, ruv_bg):
    lines = [f'Frambjóðandi: {name}', f'Sveitarfélag: {muni_name}']
    if party_name: lines.append(f'Listi/flokkur: {party_name}')
    lines.append('')
    if old_bio:
        lines.append('Núverandi æviágrip:')
        lines.append(old_bio)
        lines.append('')
    lines.append('Svör frambjóðandans á kosningaprófi RÚV:')
    for q in ruv_bg:
        label = (q.get('label') or '').strip()
        value = (q.get('value') or '').strip()
        if value:
            lines.append(f'  • {label}  →  {value}')
    return '\n'.join(lines)

def merge_one(name, muni, party, old_bio, ruv_bg, retries=2):
    user = build_user(name, muni, party, old_bio, ruv_bg)
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{'role':'system','content':SYSTEM},{'role':'user','content':user}],
                response_format={'type':'json_object'},
            )
            return json.loads(resp.choices[0].message.content)
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f'merge failed: {last_err}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot', type=int, default=0, help='only do first N')
    ap.add_argument('--only', type=str, default='', help='comma-separated RÚV ids to process')
    ap.add_argument('--start', type=int, default=0)
    args = ap.parse_args()

    ruv_bios = json.load(open(ROOT / 'scan_results' / 'ruv_bios.json', encoding='utf-8'))
    answers_blob = json.load(open(ROOT / 'temp' / 'ruv_answers.json', encoding='utf-8'))
    answers_by_id = {c['id']: c for c in answers_blob['candidates']}

    if args.only:
        target_ids = set(args.only.split(','))
        todo = [e for e in ruv_bios if e['ruv_id'] in target_ids]
    else:
        todo = ruv_bios[args.start:]
    if args.pilot:
        todo = todo[:args.pilot]

    print(f'will re-merge {len(todo)} entries\n', file=sys.stderr)

    for i, entry in enumerate(todo, 1):
        ruv = answers_by_id.get(entry['ruv_id'])
        if not ruv:
            print(f'  [{i}/{len(todo)}] {entry["name"]}: no RÚV data — skip')
            continue
        bg = ruv.get('backgroundQuestion', [])
        try:
            data = merge_one(entry['name'], entry.get('muni_name', ''),
                             ruv.get('partyName', ''), entry.get('old_bio'), bg)
            entry['new_bio'] = data.get('new_bio')
            entry['fact_check'] = data.get('fact_check', [])
            if i % 20 == 0:
                json.dump(ruv_bios, open(ROOT / 'scan_results' / 'ruv_bios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
                print(f'  [{i}/{len(todo)}] saved checkpoint')
            elif i <= 5 or i % 50 == 0:
                print(f'  [{i}/{len(todo)}] {entry["name"]}: ok ({len(data.get("new_bio",""))} ch)')
        except Exception as e:
            print(f'  [{i}/{len(todo)}] {entry["name"]}: ERR {e}')

    json.dump(ruv_bios, open(ROOT / 'scan_results' / 'ruv_bios.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\nDone — {len(todo)} entries re-merged.')

if __name__ == '__main__':
    main()
