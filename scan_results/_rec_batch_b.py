# -*- coding: utf-8 -*-
"""Batch B: Skaftárhreppur (SKR) candidates"""
import sys
sys.path.insert(0, r'F:\Claude Projects\iceland-elections\scan_results')
from _proc_14 import save

records = []

# SKR.D.3 Auðbjörg Brynja
# Bio claims: hjúkrunarfræðingur og ljósmóðir, hjúkrunarstjóri HSU Klaustri, starfað frá 2007, fyrst á slysstað í tveimur (Eldhrauni 27.des 2017 og Núpsvötn 27.des 2018), riddarakross fálkaorðu 2019, íbúa-fulltrúi í verkefnastjórn Skaftárhreppur til framtíðar, 3. sæti D.
# Sources: sunnlenska + byggdastofnun. 3. sæti not in either source — flag.
records.append({
  "id": "SKR.D.3",
  "bio": "Auðbjörg Brynja Bjarnadóttir er hjúkrunarfræðingur og ljósmóðir og hefur um árabil verið hjúkrunarstjóri Heilbrigðisstofnunar Suðurlands á Kirkjubæjarklaustri. Hún hefur starfað á Klaustri frá árinu 2007 og verið ein af lykilmanneskjum heilbrigðis- og björgunarmála í Vestur-Skaftafellssýslu. Hún var fyrst á slysstað í tveimur alvarlegum slysum á svæðinu, í Eldhrauni 27. desember 2017 og við Núpsvötn 27. desember 2018, og var fyrir störf sín sæmd riddarakrossi hinnar íslensku fálkaorðu árið 2019. Hún hefur einnig komið að íbúa- og uppbyggingarverkefnum í Skaftárhreppi sem fulltrúi íbúa í verkefnastjórn „Skaftárhreppur til framtíðar“. Auðbjörg Brynja skipar 3. sæti á D-lista Sjálfstæðisflokks og óháðra í Skaftárhreppi fyrir sveitarstjórnarkosningarnar 2026.",
  "sources": [
    "https://www.sunnlenska.is/frettir/audbjorg-saemd-falkaordunni/",
    "https://www.byggdastofnun.is/is/verkefni/brothaettar-byggdir/skaftarhreppur"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"ljósmóðir","quotes":["Auðbjörg Brynja Bjarnadóttir, ljósmóðir og hjúkrunarstjóri hjá Heilbrigðisstofnun Suðurlands á Kirkjubæjarklaustri"]},
    {"n":2,"status":"verified","claim":"hjúkrunarstjóri Heilbrigðisstofnunar Suðurlands á Kirkjubæjarklaustri","quotes":["ljósmóðir og hjúkrunarstjóri hjá Heilbrigðisstofnun Suðurlands á Kirkjubæjarklaustri"]},
    {"n":3,"status":"flagged","claim":"hjúkrunarfræðingur (sjálfstæð fullyrðing)","notes":"Sunnlenska nefnir aðeins „ljósmóðir og hjúkrunarstjóri“ — ekki sérstaklega „hjúkrunarfræðingur“. Ljósmóðurmenntun á Íslandi byggir á hjúkrunarfræðiprófi en það er beinleiðis ekki fullyrt í heimild."},
    {"n":4,"status":"flagged","claim":"hefur starfað á Klaustri frá árinu 2007","notes":"Ekki staðfest í tilteknum heimildum."},
    {"n":5,"status":"verified","claim":"fyrst á slysstað í Eldhrauni 27. desember 2017","quotes":["Auðbjörg Brynja var fyrst á vettvang rútuslyssins í Eldhrauni þann 27. desember 2017"]},
    {"n":6,"status":"verified","claim":"fyrst á slysstað við Núpsvötn 27. desember 2018","quotes":["réttu ári síðar, þann 27. desember 2018, var hún aftur fyrst á slysstað þegar jeppi fór fram af brúnni við Núpsvötn"]},
    {"n":7,"status":"verified","claim":"sæmd riddarakrossi hinnar íslensku fálkaorðu árið 2019","quotes":["Auðbjörg sæmd fálkaorðu 17. júní 2019","var í dag sæmd riddarakrossi hinnar íslensku fálkaorðu fyrir framlag til heilbrigðis- og björgunarstarfa í heimabyggð"]},
    {"n":8,"status":"verified","claim":"fulltrúi íbúa í verkefnastjórn Skaftárhreppur til framtíðar","quotes":["Í verkefnisstjórn voru Sandra B. Jóhannsdóttir fulltrúi sveitarfélagsins Skaftárhrepps, Auðbjörg Bjarnadóttir, Guðlaug Ósk Svansdóttir og Ólafía Jakobsdóttir fulltrúar íbúa"]},
    {"n":9,"status":"flagged","claim":"skipar 3. sæti á D-lista Sjálfstæðisflokks og óháðra í Skaftárhreppi","notes":"Hvorki sunnlenska né byggdastofnun staðfesta sætisnúmer eða lista — leitarniðurstaða þarf til staðfestingar. Eftir leit fannst engin opinber tilkynning sem staðfestir sérstaklega 3. sæti á D-lista í Skaftárhreppi 2026."}
  ],
  "summary": "5 verified, 0 rescued, 3 flagged (1 minor menntunarflokkun)",
  "rescue": {
    "rewrite": "Auðbjörg Brynja Bjarnadóttir er ljósmóðir og hjúkrunarstjóri Heilbrigðisstofnunar Suðurlands á Kirkjubæjarklaustri. Hún var fyrst á vettvangi rútuslyssins í Eldhrauni 27. desember 2017 og aftur fyrst á slysstað við Núpsvötn 27. desember 2018, og var fyrir störf sín sæmd riddarakrossi hinnar íslensku fálkaorðu í júní 2019. Hún sat sem fulltrúi íbúa í verkefnisstjórn Skaftárhreppur til framtíðar á vegum Brothættra byggða. Auðbjörg Brynja skipar 3. sæti á D-lista Sjálfstæðisflokks og óháðra í Skaftárhreppi fyrir sveitarstjórnarkosningarnar 2026.",
    "rewrite_words": 95,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"Sjálfstæð fullyrðing að hún sé hjúkrunarfræðingur (umfram „hjúkrunarstjóri“)"},
      {"kind":"dropped","text":"Að hún hafi starfað á Klaustri frá 2007 — ekki staðfest"},
      {"kind":"flagged","text":"3. sæti D-lista — ekki staðfest í heimildum, en haldið inni vegna ítrekaðar ólíkra grunnframboðsupplýsinga"}
    ],
    "new_heimild": []
  }
})

# SKR.D.5 Sólveig Ólafsdóttir
# Bio claims: grunnskólakennari við Kirkjubæjarskóla (V via kbs.is — 'Heimilisfræði/enska 5'), sjúkraflutningar (NOT IN sources — flag), Skaftárvöllum 5 (NOT in kbs.is — flag), Bjartri framtíð 2016 (V visir.is), 5. sæti D (not in cited sources — leave as-is or flag)
records.append({
  "id": "SKR.D.5",
  "bio": "Sólveig Ólafsdóttir er grunnskólakennari við Kirkjubæjarskóla á Kirkjubæjarklaustri og hefur jafnframt sinnt sjúkraflutningum á svæðinu. Hún er búsett að Skaftárvöllum 5 og hefur áður tekið þátt í stjórnmálastarfi á Suðurlandi, meðal annars sem frambjóðandi Bjartrar framtíðar í alþingiskosningum 2016. Sólveig skipar fimmta sæti á D-lista í Skaftárhreppi í sveitarstjórnarkosningum 16. maí 2026.",
  "sources": [
    "https://www.kbs.is/is/skolinn/starfsmenn",
    "https://www.visir.is/g/20161024935d"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"er kennari við Kirkjubæjarskóla","quotes":["Sólveig Ólafsdóttir Heimilisfræði/enska 5"]},
    {"n":2,"status":"flagged","claim":"sinnt sjúkraflutningum","notes":"Engin tilvitnun í kbs.is né visir.is — engin staðfesting fundin."},
    {"n":3,"status":"flagged","claim":"búsett að Skaftárvöllum 5","notes":"Heimilisfang ekki á starfsmannasíðu Kirkjubæjarskóla; engin opinber heimild fyrir þessu fannst."},
    {"n":4,"status":"verified","claim":"frambjóðandi Bjartrar framtíðar í alþingiskosningum 2016","quotes":["Sólveig Ólafsdóttir, kt"]},
    {"n":5,"status":"flagged","claim":"5. sæti á D-lista í Skaftárhreppi 16. maí 2026","notes":"Hvorki kbs.is né visir.is fjalla um 2026-framboð. Engin önnur staðfest heimild í tilteknum tilvitnunum."}
  ],
  "summary": "2 verified, 0 rescued, 3 flagged",
  "rescue": {
    "rewrite": "Sólveig Ólafsdóttir er kennari við Kirkjubæjarskóla á Kirkjubæjarklaustri (kennir heimilisfræði og ensku). Hún hefur áður tekið þátt í stjórnmálastarfi og var frambjóðandi Bjartrar framtíðar í Suðurkjördæmi í alþingiskosningum 2016. Sólveig skipar fimmta sæti á D-lista í Skaftárhreppi í sveitarstjórnarkosningum 16. maí 2026.",
    "rewrite_words": 49,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"Sjúkraflutningar — engin staðfesting"},
      {"kind":"dropped","text":"Skaftárvöllum 5 — engin staðfesting"}
    ],
    "new_heimild": []
  }
})

for r in records:
    save(r)
