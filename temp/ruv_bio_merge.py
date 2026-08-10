"""For each matched RÚV candidate, generate a merged bio and a fact-check
list using OpenAI.

Inputs:
  - temp/ruv_to_js_mapping.json   (mapping of RÚV id -> existing bio + heimild)
  - temp/ruv_answers.json          (full RÚV profile data)

Output:
  - scan_results/ruv_bios.json    (one entry per matched candidate)

Schema (per entry):
  {
    "ruv_id": "2505-B-17",
    "muni_const": "SNB", "party_code": "B", "ballot": 17,
    "name": "Haraldur Hinriksson",
    "muni_name": "Suðurnesjabær",
    "old_bio": "..." | null,
    "new_bio": "...",
    "fact_check": [
      { "statement": "...substring of new_bio...", "ruv_quote": "verbatim from RÚV answer" }
    ],
    "sources": [ {"url":..., "label":...}, ..., {"url": ruv_profile_url, "label": "RÚV kosningapróf"} ],
    "ruv_profile_url": "https://kosningaprof.ruv.is/frambjodandi/.../"
  }

Usage:
  python temp/ruv_bio_merge.py --limit 5         # pilot
  python temp/ruv_bio_merge.py                   # full run
"""
from __future__ import annotations
import argparse, json, os, sys, io, time
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(r'F:\Claude Projects\iceland-elections')

# Load .env
env = ROOT / '.env'
if env.exists():
    for line in env.read_text(encoding='utf-8').splitlines():
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI
MODEL = 'gpt-5.4'  # match translation script
client = OpenAI()

SYSTEM = """\
Þú ert að taka saman æviágrip um íslenskan sveitarstjórnarframbjóðanda. Skrifaðu
samfellt málsgrein á íslensku (250–400 orð) sem sameinar (a) núverandi
æviágrip ef það er til staðar — ALLT efni úr því skal halda sér — við (b) ný
atriði úr svörum frambjóðandans á kosningaprófi RÚV.

Mikilvægt:
- Notaðu þriðju persónu, formlegan tón.
- Ef gamla æviágripið inniheldur staðreynd, skal hún birtast aftur í nýju
  útgáfunni (orðalagi má breyta), aldrei taka hana út.
- Ekki finna upp neinar staðreyndir. Notaðu eingöngu efni úr gamla æviágripinu
  og RÚV-svörunum.
- RÚV-svörin innihalda persónulegar upplýsingar (fæðingarár, menntunarstig,
  starf, áhugamál, uppáhaldsbók/-kvikmynd, fyrirmynd í pólitík, framtíðarsýn
  fyrir sveitarfélagið o.s.frv.). Veldu áhugaverðustu og mest viðeigandi
  atriðin og fléttaðu þeim náttúrulega inn í samhengi við pólitíska þátttöku.
- Forðastu hluti á borð við „eldri borgari" sem starfsheiti — segðu fremur
  „kominn á eftirlaun" eða „fyrrverandi <starf>".
- Ekki nefna númerið á listanum nema gamla æviágripið hafi gert það.
- Skiptu textanum upp í 2–4 málsgreinar fyrir læsileika.

Skilaðu JSON með nákvæmlega þessari skipan:
{
  "new_bio": "<merged paragraph(s)>",
  "fact_check": [
    {
      "statement": "<orðrétt setning úr nýja æviágripinu sem byggist á NÝJU efni úr RÚV>",
      "ruv_quote": "<beint orðrétta tilvitnun úr RÚV-svörum sem styður þessa setningu>"
    }
  ]
}

Listinn fact_check skal aðeins ná yfir nýjar staðreyndir sem koma úr RÚV
(ekki staðreyndir sem voru þegar í gamla æviágripinu). Hver tilvitnun skal
vera orðrétt, sama orðalag og er í RÚV-svari (notaðu spurningarmerki/punkta
eins og í upprunalega svarinu).
"""

def build_user_prompt(name, muni_name, party_name, old_bio, ruv_bg):
    lines = []
    lines.append(f'Frambjóðandi: {name}')
    lines.append(f'Sveitarfélag: {muni_name}')
    if party_name:
        lines.append(f'Listi/flokkur: {party_name}')
    lines.append('')
    if old_bio:
        lines.append('Núverandi æviágrip:')
        lines.append(old_bio)
        lines.append('')
    lines.append('Svör frambjóðandans á kosningaprófi RÚV:')
    for q in ruv_bg:
        label = q.get('label', '').strip()
        value = (q.get('value') or '').strip()
        if not value:
            continue
        lines.append(f'  • {label}  →  {value}')
    return '\n'.join(lines)

def merge_one(client, name, muni_name, party_name, old_bio, ruv_bg, retries=2):
    user = build_user_prompt(name, muni_name, party_name, old_bio, ruv_bg)
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': SYSTEM},
                    {'role': 'user', 'content': user},
                ],
                response_format={'type': 'json_object'},
            )
            txt = resp.choices[0].message.content
            data = json.loads(txt)
            return data
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f'merge_one failed after retries: {last_err}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=0, help='only do first N matched')
    ap.add_argument('--out', type=str, default=str(ROOT / 'scan_results' / 'ruv_bios.json'))
    ap.add_argument('--start', type=int, default=0, help='resume from index')
    args = ap.parse_args()

    mapping = json.load(open(ROOT / 'temp' / 'ruv_to_js_mapping.json', encoding='utf-8'))
    answers_blob = json.load(open(ROOT / 'temp' / 'ruv_answers.json', encoding='utf-8'))
    answers_by_id = {c['id']: c for c in answers_blob['candidates']}

    matched = [m for m in mapping if m.get('match_status') == 'matched']
    print(f'matched: {len(matched)}')

    out_path = Path(args.out)
    existing = []
    if out_path.exists():
        try:
            existing = json.load(open(out_path, encoding='utf-8'))
        except Exception:
            existing = []
    done_ids = {e['ruv_id'] for e in existing}

    todo = matched[args.start:]
    if args.limit:
        todo = todo[:args.limit]

    todo = [m for m in todo if m['ruv_id'] not in done_ids]
    print(f'pending after dedupe: {len(todo)}')

    # Filter: only candidates with non-trivial RÚV profile content.
    # We require at least one of the substantive background answers to be
    # filled (excluding Q21 birth year / Q22 birth country which are nearly
    # always present but say nothing about the candidate). If the candidate
    # has nothing more than skeleton info, skip — we have no story to tell.
    SUBSTANTIVE_LABELS = (
        'Fáein orð um þig',
        'Við hvað starfar þú',
        'Hvert er hæsta menntunarstig',
        'Hvernig viltu að þitt sveitarfélag',
        'Hver er þín fyrirmynd',
        'Hver er uppáhaldstónlistarmaðurinn',
        'Hver er þín eftirlætisbók',
        'Hvaða kvikmynd heldurðu mest',
        'Hvert er þitt aðaláhugamál',
    )
    def has_profile(ruv):
        bg = ruv.get('backgroundQuestion') or []
        for q in bg:
            label = (q.get('label') or '').strip()
            value = (q.get('value') or '').strip()
            if not value:
                continue
            if any(label.startswith(L) for L in SUBSTANTIVE_LABELS):
                return True
        return False

    skipped_empty = 0
    filtered = []
    for m in todo:
        ruv = answers_by_id.get(m['ruv_id'])
        if not ruv or not has_profile(ruv):
            skipped_empty += 1
            continue
        filtered.append(m)
    todo = filtered
    print(f'after profile filter: {len(todo)} (skipped {skipped_empty} empty profiles)')

    for i, m in enumerate(todo, 1):
        ruv = answers_by_id.get(m['ruv_id'])
        if not ruv:
            print(f'  [{i}] {m["ruv_id"]}: no RÚV data')
            continue
        bg = ruv.get('backgroundQuestion', [])
        ruv_profile_url = f'https://kosningaprof.ruv.is/frambjodandi/{ruv.get("slug")}/'
        try:
            data = merge_one(client, m['ruv_name'], m['muni_name'], ruv.get('partyName',''), m.get('existing_bio'), bg)
        except Exception as e:
            print(f'  [{i}] {m["ruv_id"]} ERR: {e}')
            continue

        # Build sources: existing heimild + RÚV
        sources = list(m.get('existing_heimild') or [])
        sources.append({'url': ruv_profile_url, 'label': 'RÚV kosningapróf'})

        entry = {
            'ruv_id': m['ruv_id'],
            'muni_const': m['muni_const'],
            'party_code': m['party_code_in_js'],
            'ballot': m['ballot'],
            'name': m['ruv_name'],
            'js_name': m.get('js_name'),
            'muni_name': m['muni_name'],
            'old_bio': m.get('existing_bio'),
            'new_bio': data.get('new_bio'),
            'fact_check': data.get('fact_check', []),
            'sources': sources,
            'ruv_profile_url': ruv_profile_url,
        }
        existing.append(entry)
        if i % 10 == 0:
            json.dump(existing, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            print(f'  [{i}/{len(todo)}] saved checkpoint')
    json.dump(existing, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'\nDone. Wrote {len(existing)} entries to {out_path}')

if __name__ == '__main__':
    main()
