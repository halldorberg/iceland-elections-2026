# -*- coding: utf-8 -*-
"""Batch A: SFJ candidates"""
import sys
sys.path.insert(0, r'F:\Claude Projects\iceland-elections\scan_results')
from _proc_14 import save

records = []

# SFJ.M.11 Karen Edda
records.append({
  "id": "SFJ.M.11",
  "bio": "Karen Edda Kristjánsdóttir er bóndi á Gilhaga í Skagafirði og skipar 11. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listinn er fyrsti framboðslisti Miðflokksins í sveitarfélaginu.",
  "sources": [
    "https://www.feykir.is/is/frettir/listi-midflokksins-i-skagafirdi",
    "https://www.mbl.is/frettir/innlent/2026/02/28/midflokkurinn_bydur_fram_i_skagafirdi/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"Karen Edda er bóndi","quotes":["Karen Edda Kristjánsdóttir, bóndi"]},
    {"n":2,"status":"rescued","claim":"á Gilhaga í Skagafirði","quotes":["Karen Edda Kristjánsdóttir 130698-2209, Bóndi, Gilhagi"]},
    {"n":3,"status":"verified","claim":"skipar 11. sæti á lista Miðflokksins í Skagafirði","quotes":["Lista Miðflokksins í Skagafirði skipa: Högni Elfar Gylfason, bóndi og vélfræðingur Jódís Helga Káradóttir ... Karen Edda Kristjánsdóttir, bóndi"]},
    {"n":4,"status":"rescued","claim":"sveitarstjórnarkosningarnar 16. maí 2026","quotes":["16. maí 2026"]},
    {"n":5,"status":"verified","claim":"fyrsti framboðslisti Miðflokksins í sveitarfélaginu","quotes":["Miðflokkurinn verður þar með framboð í vor, í fyrsta sinn","Hefur flokkurinn ekki verið með framboð áður í sveitarfélaginu"]}
  ],
  "summary": "3 verified, 2 rescued, 0 flagged",
  "rescue": {
    "rewrite": "Karen Edda Kristjánsdóttir er bóndi á Gilhaga í Skagafirði og skipar 11. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 16. maí 2026. Þetta er í fyrsta sinn sem Miðflokkurinn býður fram í sveitarfélaginu.",
    "rewrite_words": 36,
    "new_sources": ["https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026"],
    "resolutions": [
      {"kind":"rescued","text":"Gilhagi staðfest úr framboðsauglýsingu Skagafjarðar"},
      {"kind":"rescued","text":"Kjördagur 16. maí 2026 staðfestur úr framboðsauglýsingu"}
    ],
    "new_heimild": [
      {"url":"https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026","label":"Skagafjörður — auglýsing um framboð (16. maí 2026)"}
    ]
  }
})

# SFJ.M.3 Elfa Björk Víðisdóttir
# Bio: fjármálafræðingur og fyrirtækjaeigandi (verified Feykir), 3. sæti M (verified Feykir order), meistaragráða í fjármálum (verified Skagafj 'Master í fjármálum'), opinber umfjöllun um rekstur sveitarfélagsins + greinar með Jódísi Helgu (verify midflokkurinn), Jódís Helga oddviti — but oddviti is Högni Elfar (1. sæti), not Jódís. WAIT — Jódís Helga is 2. sæti per feykir, not oddviti. The midflokk article credits "Jódís Helga og Elfa Björk skrifa". The midflokk page says "Jódís Helga og Elfa Björk skrifa" — co-authored. The bio says "ásamt Jódísi Helgu Káradóttur, oddvita Miðflokksins í Skagafirði" — that's WRONG. Jódís is 2nd, Högni is oddviti. FLAG.
records.append({
  "id": "SFJ.M.3",
  "bio": "Elfa Björk Víðisdóttir er fjármálafræðingur og fyrirtækjaeigandi og skipar 3. sæti á M-lista Miðflokksins í Skagafirði í sveitarstjórnarkosningum 2026. Hún er með meistaragráðu í fjármálum og hefur fjallað opinberlega um rekstur sveitarfélagsins. Í aðsendum greinum sem hún hefur skrifað ásamt Jódísi Helgu Káradóttur, oddvita Miðflokksins í Skagafirði, hefur hún gagnrýnt útgjöld sveitarfélagsins og talað fyrir aðhaldi í rekstri, skynsamlegum fjárfestingum og því að hagsmunir íbúa og komandi kynslóða séu í forgrunni. Þetta er fyrsta sveitarstjórnarframboð Miðflokksins í Skagafirði.",
  "sources": [
    "https://www.feykir.is/is/frettir/listi-midflokksins-i-skagafirdi",
    "https://midflokkurinn.is/yfir-milljon-a-dag-vid-getum-gert-betur"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"Elfa Björk er fjármálafræðingur og fyrirtækjaeigandi","quotes":["Elfa Björk Víðisdóttir, fjármálafræðingur og fyrirtækjaeigandi"]},
    {"n":2,"status":"verified","claim":"skipar 3. sæti á M-lista Miðflokksins í Skagafirði","quotes":["Lista Miðflokksins í Skagafirði skipa: Högni Elfar ... Jódís Helga ... Elfa Björk Víðisdóttir, fjármálafræðingur og fyrirtækjaeigandi"]},
    {"n":3,"status":"rescued","claim":"er með meistaragráðu í fjármálum","quotes":["Elfa Björk Víðisdóttir 170696-3449, Master í fjármálum"]},
    {"n":4,"status":"verified","claim":"hefur skrifað aðsendar greinar með Jódísi Helgu Káradóttur","quotes":["Jódís Helga og Elfa Björk skrifa"]},
    {"n":5,"status":"flagged","claim":"Jódís Helga er oddviti Miðflokksins í Skagafirði","notes":"Feykir og Skagafjörður sýna að Högni Elfar Gylfason er í 1. sæti (oddviti) og Jódís Helga er í 2. sæti. Þetta er rangt — Jódís Helga er ekki oddviti."},
    {"n":6,"status":"flagged","claim":"hefur fjallað opinberlega um rekstur sveitarfélagsins (sjálfstæð fullyrðing fyrir utan greinar með Jódísi)","notes":"Almenn fullyrðing sem ekki er sérstaklega studd; nákvæmar tilvísanir vantar. Drop sem sjálfstæð staðhæfing en greinin með Jódísi er staðfest."},
    {"n":7,"status":"verified","claim":"hefur gagnrýnt útgjöld sveitarfélagsins og talað fyrir aðhaldi í rekstri og skynsamlegum fjárfestingum","quotes":["Yfir milljón á dag — við getum gert betur","Fjárhagur sveitarfélags er ekki bara samansafn talna í ársreikningi. Hann er eign íbúanna og þannig grunnurinn að allri þjónustu sveitarfélagsins"]},
    {"n":8,"status":"verified","claim":"fyrsta sveitarstjórnarframboð Miðflokksins í Skagafirði","quotes":["Miðflokkurinn verður þar með framboð í vor, í fyrsta sinn","Hefur flokkurinn ekki verið með framboð áður í sveitarfélaginu"]}
  ],
  "summary": "5 verified, 1 rescued, 2 flagged",
  "rescue": {
    "rewrite": "Elfa Björk Víðisdóttir er fjármálafræðingur og fyrirtækjaeigandi með meistaragráðu í fjármálum og skipar 3. sæti á M-lista Miðflokksins í Skagafirði í sveitarstjórnarkosningum 2026. Í aðsendri grein á vef Miðflokksins, sem hún skrifaði ásamt Jódísi Helgu Káradóttur (2. sæti), hefur hún rætt fjárhag sveitarfélagsins og lagt áherslu á aðhald og skynsamlegar fjárfestingar í þágu íbúanna. Þetta er í fyrsta sinn sem Miðflokkurinn býður fram í Skagafirði.",
    "rewrite_words": 73,
    "new_sources": ["https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026","https://www.mbl.is/frettir/innlent/2026/02/28/midflokkurinn_bydur_fram_i_skagafirdi/"],
    "resolutions": [
      {"kind":"rescued","text":"Meistaragráða í fjármálum staðfest úr Skagafjarðarauglýsingu (Master í fjármálum)"},
      {"kind":"contradicted","text":"Jódís Helga er ekki oddviti — Högni Elfar Gylfason leiðir listann (1. sæti). Jódís Helga er í 2. sæti."},
      {"kind":"dropped","text":"Almenn fullyrðing um opinbera umfjöllun um rekstur sveitarfélagsins fyrir utan greinina"}
    ],
    "new_heimild": [
      {"url":"https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026","label":"Skagafjörður — framboðsauglýsing"},
      {"url":"https://www.mbl.is/frettir/innlent/2026/02/28/midflokkurinn_bydur_fram_i_skagafirdi/","label":"mbl.is — Miðflokkurinn býður fram í Skagafirði"}
    ]
  }
})

# SFJ.M.5 Hreiðar Örn — bio: 5. sæti M (V), slökkviliðs/sjúkraflutninga (V), ökukennari (V Feykir), Sauðárkróki (need verify — Drekahlíð 5)
records.append({
  "id": "SFJ.M.5",
  "bio": "Hreiðar Örn Steinþórsson skipar 5. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 2026. Hann starfar hjá slökkviliði og sjúkraflutningum á svæðinu og er jafnframt ökukennari. Hreiðar Örn býr á Sauðárkróki.",
  "sources": [
    "https://www.feykir.is/is/frettir/listi-midflokksins-i-skagafirdi",
    "https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"skipar 5. sæti á lista Miðflokksins í Skagafirði","quotes":["Lista Miðflokksins í Skagafirði skipa: Högni Elfar ... Hreiðar Örn Steinþórsson, ökukennari, slökkviliðs- og sjúkraflutningamaður"]},
    {"n":2,"status":"verified","claim":"sveitarstjórnarkosningarnar 2026","quotes":["sveitarstjórnarkosninga 16. maí 2026"]},
    {"n":3,"status":"verified","claim":"starfar hjá slökkviliði og sjúkraflutningum","quotes":["Hreiðar Örn Steinþórsson 130477-5939, Slökkviliðs- og sjúkraflutningamaður","Hreiðar Örn Steinþórsson, ökukennari, slökkviliðs- og sjúkraflutningamaður"]},
    {"n":4,"status":"verified","claim":"er jafnframt ökukennari","quotes":["Hreiðar Örn Steinþórsson, ökukennari, slökkviliðs- og sjúkraflutningamaður"]},
    {"n":5,"status":"verified","claim":"býr á Sauðárkróki","quotes":["Hreiðar Örn Steinþórsson 130477-5939, Slökkviliðs- og sjúkraflutningamaður, Drekahlíð 5"]}
  ],
  "summary": "5 verified, 0 rescued, 0 flagged",
  "rescue": None
})

# SFJ.M.6 Helga Rósa — fædd 1985 (kt 131185), bóndi og slökkviliðsmaður (V), Höskuldsstöðum (V), 6. sæti (V), 16. maí 2026 (V), listinn staðfestur í apríl 2026 — verify
records.append({
  "id": "SFJ.M.6",
  "bio": "Helga Rósa Pálsdóttir Þormar er bóndi og slökkviliðsmaður og er búsett á Höskuldsstöðum í Skagafirði. Hún er fædd árið 1985 og skipar 6. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listinn var staðfestur af yfirkjörstjórn í apríl 2026.",
  "sources": [
    "https://www.feykir.is/is/frettir/listi-midflokksins-i-skagafirdi",
    "https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"bóndi og slökkviliðsmaður","quotes":["Helga Rósa Pálsdóttir Þormar 131185-2279, Bóndi og slökkviliðsmaður","Helga Rósa Pálsdóttir, bóndi og slökkviliðsmaður"]},
    {"n":2,"status":"verified","claim":"búsett á Höskuldsstöðum","quotes":["Helga Rósa Pálsdóttir Þormar 131185-2279, Bóndi og slökkviliðsmaður, Höskuldsstaðir"]},
    {"n":3,"status":"verified","claim":"fædd árið 1985","quotes":["Helga Rósa Pálsdóttir Þormar 131185-2279"]},
    {"n":4,"status":"verified","claim":"skipar 6. sæti á lista Miðflokksins í Skagafirði","quotes":["Lista Miðflokksins í Skagafirði skipa: Högni Elfar ... Helga Rósa Pálsdóttir, bóndi og slökkviliðsmaður"]},
    {"n":5,"status":"verified","claim":"sveitarstjórnarkosningarnar 16. maí 2026","quotes":["sveitarstjórnarkosninga 16. maí 2026"]},
    {"n":6,"status":"flagged","claim":"Listinn var staðfestur af yfirkjörstjórn í apríl 2026","notes":"Skagafjörður-auglýsingin staðfestir framkomna lista en sérstök dagsetning eða nákvæmt staðfestingarferli í apríl er ekki bein tilvitnun. Drop sem ónákvæmt."}
  ],
  "summary": "5 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Helga Rósa Pálsdóttir Þormar er bóndi og slökkviliðsmaður á Höskuldsstöðum í Skagafirði, fædd 1985. Hún skipar 6. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "rewrite_words": 33,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"Sérstök dagsetning um staðfestingu yfirkjörstjórnar í apríl 2026 — ekki bein tilvitnun"}
    ],
    "new_heimild": []
  }
})

for r in records:
    save(r)
