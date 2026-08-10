"""Apply AKU.AL agenda rewrite + 19 candidate photos."""
import re, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'F:\Claude Projects\iceland-elections')
JS = ROOT / 'js' / 'data' / 'candidates.js'

PHOTOS = {
    1:  ('Þórhallur Jónsson',             '5a4632ee006e5582'),
    2:  ('Karen Sigurbjörnsdóttir',       '26ad89451d30d874'),
    3:  ('Helgi Steinar Halldórsson',     '6e89ca5725f65706'),
    4:  ('Kristrún María Björnsdóttir',   '8eb1d04471dfa250'),
    5:  ('Darri Rafn Hólmarsson',         '85b1936841b19c42'),
    6:  ('Dana Rán Jónsdóttir',           'a6a715b732662eda'),
    7:  ('Vilmundur Aðalsteinn Árnason',  '05b6f28d433b6cfa'),
    8:  ('Guðjón Andri Gylfason',         '4542206f4ed2113e'),
    9:  ('Elfa Ágústsdóttir',             '5e071e3e0f3147f3'),
    10: ('Pavel Víking Landa',            '0369b48bf233392c'),
    11: ('Rannveig Hansen Jónsdóttir',    '6db55f784a49cd98'),
    12: ('Hilmar Friðjónsson',            'cb52b258635a6180'),
    13: ('Fríða Kristín Hreiðarsdóttir',  'cc1dc3fdee7c0707'),
    14: ('Friðbjörn Benediktsson',        'de03d0bb8c3f9049'),
    15: ('Harpa Þórey Sigurðardóttir',    '8d1bf3e44e8344d0'),
    16: ('Elvar Freyr Pálsson',           'c834c2704fae2bdc'),
    17: ('Axel Darri Þórhallsson',        'eeadd23654a8da7a'),
    19: ('Rúnar Þór Björnsson',           '65eeff1df1e6d56f'),
    20: ('Ingibjörg Margrét Þórhallsdóttir', '8df478d4b15dfae6'),
}

NEW_AGENDA = """    agenda: [
      {
        icon: '💼',
        title: 'Atvinnulífið',
        text: 'Sterkt atvinnulíf er forsenda velferðar. Vinnum með fyrirtækjum til að ýta undir vöxt; einföldum regluverk og lækkum fasteignagjöld til að styðja lítil og meðalstór fyrirtæki. Fjölgum atvinnulóðum í bænum. Akureyri verður að vera sterkt mótvægi við höfuðborgarsvæðið.',
        source_quote: 'Sterkt atvinnulíf er forsenda velferðar. Við viljum vinna með fyrirtækjum til að ýta undir vöxt og ný tækifæri á svæðinu. Við ætlum að einfalda regluverk og lækka fasteignagjöld til að styðja lítil og meðalstór fyrirtæki.',
      },
      {
        icon: '🏗️',
        title: 'Uppbygging',
        text: 'Höldum uppbyggingu áfram og bætum í. Fjölgum íbúðum í öllum verðflokkum með sérstaka áherslu á fyrstu kaupendur. Komum af stað íbúðauppbyggingu á Oddeyri, fjölgum bílastæðum í miðbænum og byggjum búsetukjarna fyrir eldra fólk sem vill minnka við sig. Dreifum gjöldum yfir byggingartímann til að auðvelda fólki að byggja sér hús.',
        source_quote: 'Við höldum uppbyggingu áfram og bætum í. Við fjölgum íbúðum í öllum verðflokkum með sérstaka áherslu á fyrstu kaupendur.',
      },
      {
        icon: '📚',
        title: 'Menntun',
        text: 'Akureyri á að vera besti staðurinn til að ala upp börn. Afnemum „fengitímann" á Akureyri — fólk á ekki að þurfa að horfa á dagatalið til að búa til börn — og tökum inn á leikskóla tvisvar á ári. Aukum sveigjanleika í vistunartíma og sumarleyfum leikskóla í samvinnu við starfsfólk. Bætum sértækan stuðning við nemendur og kennara, styrkjum tónlistarkennslu og þrýstum á að Háskóli allra landsmanna bjóði upp á fjarnám.',
        source_quote: 'Akureyri á að vera besti staðurinn til að ala upp börn. Afnemum fengitímann á Akureyri! Fólk á ekki að þurfa að horfa á dagatalið til að búa til börn. Tökum inn á leikskóla tvisvar á ári.',
      },
      {
        icon: '✈️',
        title: 'Samgöngur',
        text: 'Betri samgöngur skila sér margfalt til baka í auknum hagvexti. Akureyrarflugvöllur á að vera önnur gátt inn í landið — aukin tíðni og samfella í flugi eflir ferðaþjónustu og lífsgæði. Bætum göngu- og hjólaleiðir til að auka lýðheilsu og draga úr kolefnisspori. Tölum fyrir styttingu leiðarinnar milli Akureyrar og Reykjavíkur.',
        source_quote: 'Betri samgöngur skila sér margfalt til baka í auknum hagvexti. Akureyrarflugvöllur er ekki bara varaflugvöllur. Hann á að vera önnur gátt inn í landið.',
      },
      {
        icon: '🤝',
        title: 'Eldra fólk',
        text: 'Heilbrigði og félagslíf aldraðra í fyrirrúmi. Byggjum samkomusal sem uppfyllir þarfir eldri borgara og lífsgæðakjarna með glatvarma frá gagnaverunum. Berjumst gegn félagslegri einangrun, meðal annars með „Karlar í skúrum"-verkefninu.',
        source_quote: 'Heilbrigði og félagslíf aldraðra í fyrirrúmi. Byggjum samkomusal sem uppfyllir þarfir eldri borgara. Lífsgæðakjarni með glatvarma frá gagnaverunum.',
      },
      {
        icon: '🎭',
        title: 'Menning, íþróttir og mannlíf',
        text: 'Akureyri sem menningarhöfuðborg Norðurlands. Klárum frágang á KA-svæðinu, hefjum íþróttahús á Þórs-svæðinu og styðjum við uppbyggingu Bílaklúbbs Akureyrar. Nýr 9-holu golfvöllur á Jaðri og undirbúningur fyrir nýjan golfvöll á Skjaldarvík. Eflum Akureyri sem Vetraríþróttamiðstöð Íslands með nýrri stólalyftu í Hlíðarfjalli (í stað Fjarkans) og stærra bílastæði. Reglulegir sumartónleikar, 50 metra yfirbyggð keppnissundlaug og nýtt geymsluhúsnæði Minjasafnsins.',
        source_quote: 'Markmiðið er skýrt: Akureyri sem menningarhöfuðborg Norðurlands.',
      },
      {
        icon: '📉',
        title: 'Lækkun skatta',
        text: 'Fasteignagjöld hafa hækkað óhóflega — við breytum þessu. Nýtum svigrúmið til að lækka fasteignagjöld á íbúa og fyrirtæki. Hagræðum í stjórnsýslunni til að fjármagna metnaðarfulla þjónustu, höldum aftur af verðhækkunum og förum yfir fasteignir bæjarins til að hámarka nýtingu.',
        source_quote: 'Fasteignagjöld hafa hækkað óhóflega. Við breytum þessu. Svigrúmið sem er til staðar verður nýtt til að lækka fasteignagjöld á íbúa og fyrirtæki.',
      },
      {
        icon: '🏛️',
        title: 'Ríkið',
        text: 'Vinnum markvisst með ríkisstjórninni: stækkun og efling Sjúkrahússins á Akureyri, ný þyrlusveit Landhelgisgæslunnar staðsett á Akureyri, stækkun VMA og hröðun uppbyggingar hjúkrunarheimila. Þrýstum á samgöngubætur að Skógarböðum. Nei takk við sjókvíaeldi í Eyjafirði.',
        source_quote: 'Við vinnum markvisst með ríkisstjórninni. Stækkun og efling Sjúkrahússins á Akureyri er lykilatriði fyrir byggð á Norðausturlandi.',
      },
    ],"""

src = JS.read_text(encoding='utf-8')

# 1. Replace agenda block inside AKU.AL
# Find AKU.AL block by searching for the tagline that precedes it
ag_pattern = re.compile(
    r"(  AL:\s*\{\s*tagline:\s*'[^']+',\s*platformUrl:\s*'[^']+',\s*)"
    r"agenda:\s*\[[^\]]+\],",
    re.S
)
m = ag_pattern.search(src)
if not m:
    print('AGENDA pattern not found')
    sys.exit(1)
src = src[:m.start()] + m.group(1) + NEW_AGENDA + src[m.end():]
print('Agenda block replaced')

# 2. Photos
# Find AKU.AL block range
m = re.search(r'const AKU\s*=\s*\{', src)
i = m.end() - 1; d = 0
while i < len(src):
    c = src[i]
    if c == '{': d += 1
    elif c == '}':
        d -= 1
        if d == 0: break
    i += 1
aku_end_abs = i + 1
aku_start_abs = m.end() - 1

al_match = re.search(r'\n  AL:\s*\{', src[aku_start_abs:aku_end_abs])
al_start = aku_start_abs + al_match.start()
j = aku_start_abs + al_match.end() - 1
d2 = 0; ins = None
while j < aku_end_abs:
    c = src[j]
    if ins:
        if c == '\\': j += 2; continue
        if c == ins: ins = None
        j += 1; continue
    if c in ("'", '"', '`'): ins = c; j += 1; continue
    if c == '{': d2 += 1
    elif c == '}':
        d2 -= 1
        if d2 == 0: break
    j += 1
al_end = j + 1

al_block = src[al_start:al_end]
new_block = al_block

for seat, (name, hash_) in PHOTOS.items():
    path = f"'images/candidates/{hash_}.jpg'"
    # Try to replace existing photo path
    p1 = re.compile(
        r"(\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'[^']*',\s*)"
        r"'images/candidates/[^']+'", re.S)
    m1 = p1.search(new_block)
    if m1:
        new_block = p1.sub(lambda mm: mm.group(1) + path, new_block, count=1)
        print(f'  {seat:>2}  {name:<35}  photo REPLACED')
        continue
    # null in photo slot
    p2 = re.compile(
        r"(\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'[^']*',\s*)null", re.S)
    m2 = p2.search(new_block)
    if m2:
        new_block = p2.sub(lambda mm: mm.group(1) + path, new_block, count=1)
        print(f'  {seat:>2}  {name:<35}  null REPLACED')
        continue
    # Bare row [seat, name, occ]
    p3 = re.compile(
        r"\[" + str(seat) + r",\s*'" + re.escape(name) + r"',\s*'([^']*)'\]")
    m3 = p3.search(new_block)
    if m3:
        new_block = p3.sub(f"[{seat}, '{name}', '{m3.group(1)}', {path}]", new_block, count=1)
        print(f'  {seat:>2}  {name:<35}  bare row → with photo')
        continue
    print(f'  {seat:>2}  {name:<35}  NO MATCH')

if new_block != al_block:
    src = src[:al_start] + new_block + src[al_end:]

braces = src.count('{') - src.count('}')
brackets = src.count('[') - src.count(']')
print(f'\nbraces: {braces}, brackets: {brackets}')
if braces == 0 and brackets == 0:
    JS.write_text(src, encoding='utf-8')
    print('Written.')
else:
    print('NOT WRITTEN — bracket sanity failed.')
