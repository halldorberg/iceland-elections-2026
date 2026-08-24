# coding: utf-8
"""Build translated ESB assets: js/esb-data.{en,pl}.js, js/esb-motrok.{en,pl}.js,
and en/index.html + pl/index.html from the Icelandic front page."""
import io, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SHY = '­'

DATA = json.loads(subprocess.run(
    ['node', '-e', "const fs=require('fs');const src=fs.readFileSync('js/esb-data.js','utf8');const DATA=new Function(src+';return DATA;')();process.stdout.write(JSON.stringify(DATA))"],
    capture_output=True, text=True, encoding='utf-8', cwd=str(ROOT)).stdout)
MOTROK = {}
for name in ('motrok_ja1', 'motrok_ja2', 'motrok_nei1', 'motrok_nei2', 'motrok_new', 'motrok_new2'):
    MOTROK.update(json.load(io.open(ROOT / 'scripts' / f'{name}.json', encoding='utf-8')))

# Hand-authored UI string replacements for the front page (is → en / pl)
UI = [
 ('<html lang="is">', '<html lang="{L}">'),
 ('Þjóðaratkvæðagreiðsla · Ísland', {'en': 'National referendum · Iceland', 'pl': 'Referendum krajowe · Islandia'}),
 ('🗳️<span class="archive-btn-text"> Eldri kosningar</span>', {'en': '🗳️<span class="archive-btn-text"> Past elections</span>', 'pl': '🗳️<span class="archive-btn-text"> Poprzednie wybory</span>'}),
 ('🗺️ Sveitarstjórnarkosningar <span class="archive-menu-year">maí 2026</span>', {'en': '🗺️ Municipal elections <span class="archive-menu-year">May 2026</span>', 'pl': '🗺️ Wybory samorządowe <span class="archive-menu-year">maj 2026</span>'}),
 ('<span>Þjóðaratkvæðagreiðsla um ESB ·&nbsp;<span style="white-space:nowrap">29. ágúst 2026</span></span>',
  {'en': '<span>EU referendum ·&nbsp;<span style="white-space:nowrap">29 August 2026</span></span>', 'pl': '<span>Referendum ws. UE ·&nbsp;<span style="white-space:nowrap">29 sierpnia 2026</span></span>'}),
 ('Velkomin í <span>lýðræðisveisluna!</span>', {'en': 'Welcome to <span>the democracy feast!</span>', 'pl': 'Witamy na <span>święcie demokracji!</span>'}),
 ('Sjálfvirk greining á umræðunni um þjóðaratkvæðagreiðsluna um ESB-aðildarviðræður 29. ágúst 2026.\n      Rök og mótrök JÁ- og NEI-hliðarinnar, helstu hreyfingar, talsmenn og greinar — í einu yfirliti.',
  {'en': 'Automated analysis of the debate around the 29 August 2026 referendum on resuming EU accession talks.\n      Arguments and counter-arguments of the YES and NO sides, key movements, spokespeople and articles — in one overview.',
   'pl': 'Automatyczna analiza debaty wokół referendum z 29 sierpnia 2026 r. w sprawie wznowienia negocjacji akcesyjnych z UE.\n      Argumenty i kontrargumenty stron TAK i NIE, główne ruchy, rzecznicy i artykuły — w jednym przeglądzie.'}),
 ('Greinar JÁ-megin', {'en': 'Articles YES side', 'pl': 'Artykuły strony TAK'}),
 ('Greinar NEI-megin', {'en': 'Articles NO side', 'pl': 'Artykuły strony NIE'}),
 ('Greind atriði alls', {'en': 'Items analysed', 'pl': 'Przeanalizowane pozycje'}),
 ('JÁ — Halda viðræðum áfram', {'en': 'YES — Continue the talks', 'pl': 'TAK — Kontynuować negocjacje'}),
 ('NEI — Ekki halda viðræðum áfram', {'en': 'NO — Do not continue the talks', 'pl': 'NIE — Nie kontynuować negocjacji'}),
 ('Helstu hreyfingar', {'en': 'Key movements', 'pl': 'Główne ruchy'}),
 ('Dæmi um helstu talsmenn', {'en': 'Examples of key spokespeople', 'pl': 'Przykłady głównych rzeczników'}),
 ('Helstu rök (eftir tíðni)', {'en': 'Main arguments (by frequency)', 'pl': 'Główne argumenty (wg częstości)'}),
 ('Nýjustu greinarnar', {'en': 'Latest articles', 'pl': 'Najnowsze artykuły'}),
 ('Skoða allar greinarnar →', {'en': 'See all articles →', 'pl': 'Zobacz wszystkie artykuły →'}),
 # JS template strings
 ('× í greinum', {'en': '× in articles', 'pl': '× w artykułach'}),
 ("Helstu mótrök ${other === 'ja' ? 'JÁ' : 'NEI'}-hliðar", {'en': "Main counter-arguments (${other === 'ja' ? 'YES' : 'NO'} side)", 'pl': "Główne kontrargumenty (strona ${other === 'ja' ? 'TAK' : 'NIE'})"}),
 ('Nánar um þessi rök →', {'en': 'More about this argument →', 'pl': 'Więcej o tym argumencie →'}),
 ('Skoða allar ${total} greinarnar →', {'en': 'See all ${total} articles →', 'pl': 'Zobacz wszystkie ${total} artykuły →'}),
 ("const sideLbl = a.side === 'ja' ? 'JÁ' : 'NEI';", {'en': "const sideLbl = a.side === 'ja' ? 'YES' : 'NO';", 'pl': "const sideLbl = a.side === 'ja' ? 'TAK' : 'NIE';"}),
 ('▶ Horfa á öll video', {'en': '▶ Watch all videos', 'pl': '▶ Obejrzyj wszystkie filmy'}),
 ('Fyrirvari', {'en': 'Disclaimer', 'pl': 'Zastrzeżenie'}),
 ('Efnið er tekið saman með aðstoð gervigreindar úr opinberum heimildum á netinu. Við getum ekki ábyrgst fulla nákvæmni og mælum með að staðfesta mikilvægar upplýsingar í frumheimildum.',
  {'en': 'Content is compiled with AI assistance from public online sources. We cannot guarantee full accuracy and recommend verifying important information in the original sources.',
   'pl': 'Treści są zestawiane z pomocą AI ze źródeł publicznie dostępnych w internecie. Nie możemy zagwarantować pełnej dokładności i zalecamy weryfikację ważnych informacji w źródłach.'}),
 # head: title/description/canonical/data files
 ('<title>Þjóðaratkvæðagreiðsla um ESB 2026 – Lýðræðisveislan</title>',
  {'en': '<title>Iceland EU referendum 2026 – Lýðræðisveislan</title>', 'pl': '<title>Referendum UE na Islandii 2026 – Lýðræðisveislan</title>'}),
 ('content="Greining á umræðunni um þjóðaratkvæðagreiðsluna um ESB-aðildarviðræður 29. ágúst 2026. Rök og mótrök beggja hliða í einu yfirliti."',
  {'en': 'content="Analysis of the debate around Iceland\\u2019s 29 August 2026 referendum on resuming EU accession talks. Arguments of both sides in one overview."'.replace('\\u2019', '’'),
   'pl': 'content="Analiza debaty wokół islandzkiego referendum z 29 sierpnia 2026 r. w sprawie negocjacji akcesyjnych z UE. Argumenty obu stron w jednym przeglądzie."'}),
 ('<link rel="canonical" href="https://lydraedisveislan.is/" />', '<link rel="canonical" href="https://lydraedisveislan.is/{L}/" />'),
 ('js/esb-data.js?v=8', '/js/esb-data.{L}.js?v=7'),
 ('js/esb-motrok.js?v=3', '/js/esb-motrok.{L}.js?v=4'),
 ('src="js/esb', 'src="/js/esb'),  # safety for relative refs from /en/
 ("from './js/i18n.js?v=4'", "from '/js/i18n.js?v=4'"),
 ('href="css/', 'href="/css/'),
 ("url('images/bg-hero2.jpg')", "url('/images/bg-hero2.jpg')"),
 ('href="favicon.svg"', 'href="/favicon.svg"'),
]


def apply_translations(lang):
    T = json.load(io.open(ROOT / 'translations' / f'esb_{lang}.json', encoding='utf-8'))
    d = json.loads(json.dumps(DATA))
    d['note'] = T.get('note', d['note'])
    for side in ('ja', 'nei'):
        for i, m in enumerate(d['movements'][side]):
            m['description'] = T.get(f'mv.{side}.{i}.description', m['description'])
        for i, sp in enumerate(d['spokes'][side]):
            sp['role'] = T.get(f'spoke.{side}.{i}.role', sp['role'])
        for a in d['arguments'][side]:
            a['title'] = T.get(f'arg.{a["key"]}.title', a['title'])
            a['text'] = T.get(f'arg.{a["key"]}.text', a['text'])
    for i, art in enumerate(d['articles']):
        art['title'] = T.get(f'art.{i}.title', art['title'])
        art['summary'] = T.get(f'art.{i}.summary', art['summary'])
    mo = json.loads(json.dumps(MOTROK))
    for k, items in mo.items():
        for i, m in enumerate(items):
            m['title'] = T.get(f'motrok.{k}.{i}.title', m['title'])
            m['text'] = T.get(f'motrok.{k}.{i}.text', m['text'])
    with io.open(ROOT / 'js' / f'esb-data.{lang}.js', 'w', encoding='utf-8', newline='') as f:
        f.write('const DATA = ' + json.dumps(d, ensure_ascii=False, indent=1) + ';\n')
    with io.open(ROOT / 'js' / f'esb-motrok.{lang}.js', 'w', encoding='utf-8', newline='') as f:
        f.write('const MOTROK = ' + json.dumps(mo, ensure_ascii=False, indent=1) + ';\n')


def build_front(lang):
    c = io.open(ROOT / 'index.html', encoding='utf-8', newline='').read()
    missing = []
    for pair in UI:
        old, new = pair
        if isinstance(new, dict):
            new = new[lang]
        new = new.replace('{L}', lang)
        if old in c:
            c = c.replace(old, new)
        else:
            missing.append(old[:60])
    # hreflang: point alternates correctly
    c = c.replace('<link rel="alternate" hreflang="is" href="https://lydraedisveislan.is/" />',
                  '<link rel="alternate" hreflang="is" href="https://lydraedisveislan.is/" />\n  <link rel="alternate" hreflang="en" href="https://lydraedisveislan.is/en/" />\n  <link rel="alternate" hreflang="pl" href="https://lydraedisveislan.is/pl/" />')
    out = ROOT / lang / 'index.html'
    out.parent.mkdir(exist_ok=True)
    with io.open(out, 'w', encoding='utf-8', newline='') as f:
        f.write(c)
    return missing


for lang in ('en', 'pl'):
    apply_translations(lang)
    missing = build_front(lang)
    print(f'[{lang}] data+motrok+front built; unmatched replacements: {len(missing)}')
    for m in missing:
        print('  MISS:', m)
