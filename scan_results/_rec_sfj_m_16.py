# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r'F:\Claude Projects\iceland-elections\scan_results')
from _proc_14 import save

rec = {
  "id": "SFJ.M.16",
  "bio": "Líney María Hjálmarsdóttir er tamningamaður og bóndi á Tunguhálsi II í Skagafirði, þar sem fjölskylda hennar rekur hrossaræktarbú. Hún hefur tekið þátt í hestamótum og kynbótasýningum og keppt á hrossum frá búinu á Tunguhálsi. Líney María skipar 16. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 16. maí 2026, þar sem Högni Elfar Gylfason leiðir listann.",
  "sources": [
    "https://www.feykir.is/is/frettir/listi-midflokksins-i-skagafirdi",
    "https://www.facebook.com/HrossaraektarbuidTunguhals2/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"Líney María er tamningamaður og bóndi","quotes":["Líney María Hjálmarsdóttir, tamningamaður og bóndi"]},
    {"n":2,"status":"rescued","claim":"á Tunguhálsi II í Skagafirði","quotes":["Líney María Hjálmarsdóttir 280279-3239, Tamningamaður, Tunguhálsi II"]},
    {"n":3,"status":"verified","claim":"þar er hrossaræktarbú","quotes":["Tunguháls 2 • Tölthólar • Icelandic Horses"]},
    {"n":4,"status":"flagged","claim":"hún hefur tekið þátt í hestamótum og kynbótasýningum og keppt á hrossum frá búinu","notes":"Ekkert í Feykir-grein né á Facebook-síðu (aðeins titill var sóttur). Engin staðfest tilvitnun fannst. DROP."},
    {"n":5,"status":"verified","claim":"skipar 16. sæti á lista Miðflokksins í Skagafirði","quotes":["Lista Miðflokksins í Skagafirði skipa: ... Líney María Hjálmarsdóttir, tamningamaður og bóndi"]},
    {"n":6,"status":"rescued","claim":"sveitarstjórnarkosningarnar 16. maí 2026","quotes":["sveitarstjórnarkosninga 16. maí 2026"]},
    {"n":7,"status":"verified","claim":"Högni Elfar Gylfason leiðir listann","quotes":["Lista Miðflokksins í Skagafirði skipa: Högni Elfar Gylfason, bóndi og vélfræðingur"]}
  ],
  "summary": "3 verified, 3 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Líney María Hjálmarsdóttir er tamningamaður og bóndi á Tunguhálsi II í Skagafirði, þar sem rekið er hrossaræktarbúið Tunguháls 2 — Tölthólar. Hún skipar 16. sæti á lista Miðflokksins í Skagafirði fyrir sveitarstjórnarkosningarnar 16. maí 2026, þar sem Högni Elfar Gylfason leiðir listann.",
    "rewrite_words": 49,
    "new_sources": [
      "https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026"
    ],
    "resolutions": [
      {"kind":"rescued","text":"Tunguhálsi II staðfest úr framboðsauglýsingu Skagafjarðar"},
      {"kind":"rescued","text":"16. maí 2026 staðfest úr Skagafjarðarauglýsingu"},
      {"kind":"dropped","text":"Þátttaka í hestamótum og kynbótasýningum / keppni á hrossum frá búinu — ekki staðfest í tilteknum né leitarheimildum"}
    ],
    "new_heimild": [
      {"url":"https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026","label":"Skagafjörður — auglýsing um framboð (16. maí 2026)"}
    ]
  }
}
save(rec)
