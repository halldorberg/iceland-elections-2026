# -*- coding: utf-8 -*-
"""Batch D: THV, VBG, VME"""
import sys
sys.path.insert(0, r'F:\Claude Projects\iceland-elections\scan_results')
from _proc_14 import save

records = []

# THV.THVA.12 Gísli Sigurðsson — Á-listi Ábyrgðar
# husavik confirms: Gísli Sigurðsson – sérfræðingur, Brekkukoti, Aðaldal; Á-listi Ábyrgðar Borgaralegt framboð með áherslu á að efla atvinnu og fjölga íbúum, þá sérstaklega barnafjölskyldum
# But position 12 — husavik lists names with positions implicit. Need to verify 12. sæti.
# Reading the husavik snippets: Á-listi Ábyrgðar starts: 1 Knútur Jónasson, 2 Nanna Marteinsdóttir, 3 Anna Bragadóttir, 4 Dóra Rún Kristjánsdóttir, 5 Hörður Sigurðsson, ...
# Need to count Gísli's position from full husavik list.
records.append({
  "id": "THV.THVA.12",
  "bio": "Gísli Sigurðsson er sérfræðingur og býr í Brekkukoti í Aðaldal í Þingeyjarsveit. Hann skipar 12. sæti á Á-lista Ábyrgðar fyrir sveitarstjórnarkosningarnar í Þingeyjarsveit 2026. Listinn er borgaralegt framboð sem leggur áherslu á að efla atvinnu og fjölga íbúum, einkum barnafjölskyldum.",
  "sources": [
    "https://www.husavik.com/2026/04/thrir-listar-i-thingeyjarsveit/",
    "https://www.thingeyjarsveit.is/is/frettir-tilkynningar/thrir-frambodslistar-stadfestir-fyrir-sveitarstjornarkosningar-2026"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"sérfræðingur","quotes":["Gísli Sigurðsson – sérfræðingur, Brekkukoti, Aðaldal"]},
    {"n":2,"status":"verified","claim":"býr í Brekkukoti í Aðaldal","quotes":["Gísli Sigurðsson – sérfræðingur, Brekkukoti, Aðaldal"]},
    {"n":3,"status":"flagged","claim":"skipar 12. sæti á Á-lista Ábyrgðar","notes":"Husavik birtir nöfn í lista en sætisnúmer 12 er ekki bein tilvitnun. Nafnaröðin var ekki fullbirt í útdrætti."},
    {"n":4,"status":"verified","claim":"sveitarstjórnarkosningar Þingeyjarsveit 2026","quotes":["Á-listi Ábyrgðar, L-listi Framfara og N-listinn","Þrír framboðslistar staðfestir fyrir sveitarstjórnarkosningar 2026"]},
    {"n":5,"status":"verified","claim":"Listinn er borgaralegt framboð sem leggur áherslu á að efla atvinnu og fjölga íbúum, einkum barnafjölskyldum","quotes":["L-listi Framfara Borgaralegt framboð með áherslu á að efla atvinnu og fjölga íbúum, þá sérstaklega barnafjölskyldum"]}
  ],
  "summary": "4 verified, 0 rescued, 1 flagged — VARÚÐ: lýsing borgaraleg framboð gæti verið rangtengd L-lista Framfara, ekki Á-lista Ábyrgðar",
  "rescue": {
    "rewrite": "Gísli Sigurðsson er sérfræðingur og býr í Brekkukoti í Aðaldal í Þingeyjarsveit. Hann er á Á-lista Ábyrgðar fyrir sveitarstjórnarkosningarnar í Þingeyjarsveit 2026.",
    "rewrite_words": 25,
    "new_sources": [],
    "resolutions": [
      {"kind":"contradicted","text":"Lýsingin „borgaralegt framboð sem leggur áherslu á að efla atvinnu og fjölga íbúum, einkum barnafjölskyldum“ er bein tilvitnun úr husavik-grein um L-lista FRAMFARA — ekki Á-lista Ábyrgðar. List-name distortion."},
      {"kind":"dropped","text":"Sætisnúmer 12 — ekki staðfest í tilteknum heimildum"}
    ],
    "new_heimild": []
  }
})

# VBG.STV.14 Ásgeir Sveinsson — bóndi og framkvæmdastjóri (V), 14. sæti V-lista (V), Hlynur Ársælsson framkvæmdastjóri leiðir (V), bæjarfulltrúi yfirstandandi kjörtímabili (V via bb 2022), annar varaforseti (V via bb 2022). Vatnsdalsvirkjun stuðningur — ekki staðfest.
records.append({
  "id": "VBG.STV.14",
  "bio": "Ásgeir Sveinsson er bóndi og framkvæmdastjóri í Vesturbyggð. Hann hefur setið í bæjarstjórn Vesturbyggðar á yfirstandandi kjörtímabili og gegnt embætti annars varaforseta bæjarstjórnar. Ásgeir skipar 14. sæti, heiðurssæti listans, á framboðslista Sterkari Vesturbyggðar (V-lista) fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listinn er nýtt óháð framboð í Vesturbyggð, leitt af Hlyni Ársælssyni framkvæmdastjóra, sem leggur meðal annars áherslu á atvinnuuppbyggingu og hefur lýst yfir stuðningi við uppbyggingu Vatnsdalsvirkjunar.",
  "sources": [
    "https://bb.is/2026/04/v-listi-sterkari-vesturbyggd/",
    "https://vesturbyggd.is/stjornsysla/baejarstjorn-og-nefndir/baejarstjorn/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"bóndi og framkvæmdastjóri","quotes":["14 Ásgeir Sveinsson Bóndi og framkvæmdastjóri"]},
    {"n":2,"status":"flagged","claim":"hefur setið í bæjarstjórn Vesturbyggðar á yfirstandandi kjörtímabili","notes":"Núverandi bæjarstjórnarsíða Vesturbyggðar (eftir kosningar 2022) listar ekki Ásgeir sem bæjarfulltrúa né varamann. En BB-grein frá 13.6.2022 um fyrsta fund nýrrar bæjarstjórnar listar Ásgeir sem bæjarfulltrúa. Þetta þýðir að hann tók sæti í kjölfar kosninga 2022 en kann að hafa hætt fyrir vorið 2026."},
    {"n":3,"status":"rescued","claim":"gegnt embætti annars varaforseta bæjarstjórnar","quotes":["Á fundinum var Jón Árnason var kjörin forseti bæjarstjórnar, Friðbjörn Steinar Ottósson var kjörinn fyrsti varaforseti og Ásgeir Sveinsson annar varaforseti"]},
    {"n":4,"status":"verified","claim":"14. sæti á framboðslista Sterkari Vesturbyggðar (V-lista)","quotes":["13 Silja Björg Ísafoldardóttir Ferðaþjónustubóndi 14 Ásgeir Sveinsson Bóndi og framkvæmdastjóri"]},
    {"n":5,"status":"flagged","claim":"„heiðurssæti listans“","notes":"BB nefnir sætisnúmer en orðar ekki „heiðurssæti“ sérstaklega. Almennt eru efstu og neðstu sæti óformlega kölluð heiðurssæti — en ekki bein tilvitnun."},
    {"n":6,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]},
    {"n":7,"status":"verified","claim":"Listinn er nýtt framboð í Vesturbyggð, leitt af Hlyni Ársælssyni framkvæmdastjóra","quotes":["Í dag var samþykkt í kjörstjórn Vesturbyggðar framboð nýs lista V lista – Sterkari Vesturbyggð","1 Hlynur Ársælsson Framkvæmdastjóri"]},
    {"n":8,"status":"flagged","claim":"hefur lýst yfir stuðningi við uppbyggingu Vatnsdalsvirkjunar","notes":"Engin tilvitnun í tilteknum heimildum (bb-grein um listann nefnir ekki Vatnsdalsvirkjun). Engin staðfest leitarniðurstaða fannst."},
    {"n":9,"status":"flagged","claim":"leggur meðal annars áherslu á atvinnuuppbyggingu","notes":"BB-grein lýsir ekki málefnum listans nema einungis nöfnum og störfum. Ekki bein tilvitnun."}
  ],
  "summary": "4 verified, 1 rescued, 4 flagged",
  "rescue": {
    "rewrite": "Ásgeir Sveinsson er bóndi og framkvæmdastjóri í Vesturbyggð. Hann tók sæti í bæjarstjórn Vesturbyggðar eftir sveitarstjórnarkosningarnar 2022 og gegndi embætti annars varaforseta bæjarstjórnar. Ásgeir skipar 14. sæti á framboðslista nýs lista, V-lista Sterkari Vesturbyggðar, fyrir sveitarstjórnarkosningarnar 16. maí 2026; listinn er leiddur af Hlyni Ársælssyni framkvæmdastjóra.",
    "rewrite_words": 50,
    "new_sources": ["https://www.bb.is/2022/06/baejarstjorn-vesturbyggdar-med-fyrsta-fund-9-juni/"],
    "resolutions": [
      {"kind":"rescued","text":"Annar varaforseti bæjarstjórnar staðfest úr BB-grein 13.6.2022"},
      {"kind":"dropped","text":"„Heiðurssæti“ — ekki bein tilvitnun"},
      {"kind":"dropped","text":"Stuðningur við Vatnsdalsvirkjun — engin staðfesting"},
      {"kind":"dropped","text":"„Áhersla á atvinnuuppbyggingu“ — engin bein tilvitnun"}
    ],
    "new_heimild": [
      {"url":"https://www.bb.is/2022/06/baejarstjorn-vesturbyggdar-med-fyrsta-fund-9-juni/","label":"BB — Bæjarstjórn Vesturbyggðar með fyrsta fund 9. júní 2022"}
    ]
  }
})

# VME.D.10 Hannes Kristinn — many claims; bio says "fyrrv. formaður framkvæmda- og hafnarráðs" but Eyjafréttir says "varaformaður"
records.append({
  "id": "VME.D.10",
  "bio": "Hannes Kristinn Sigurðsson er 41 árs innkaupastjóri og skipar 10. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum fyrir sveitarstjórnarkosningarnar 16. maí 2026. Hann er fyrrverandi formaður framkvæmda- og hafnarráðs Vestmannaeyjabæjar og hefur setið í stjórn Sjálfstæðisflokksins í Eyjum frá árinu 2011, þegar hann gekk í stjórn ungliðahreyfingarinnar Eyverja. Hannes Kristinn tók einnig þátt í prófkjöri flokksins fyrir fjórum árum. Meðal áherslumála hans eru innviðauppbygging, einkum stórskipahöfn við Eiðið, endurbætur á aðstöðu Herjólfs og fjölgun íbúa í Vestmannaeyjum. Eiginkona hans er Fanney Finnbogadóttir og eiga þau tvo syni, Elías Agnar (f. 2014) og Eyvar Boga (f. 2021).",
  "sources": [
    "https://eyjafrettir.is/spurt-og-svarad-hannes-kristinn-fra-sjalfstaedisflokknum/",
    "https://xd.is/2026/03/31/frambodslisti-sjalfstaedisflokksins-i-vestmannaeyjum/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"41 árs","quotes":["Hannes Kristinn Sigurðsson Aldur: 41 árs","Hannes Kristinn Sigurðsson, 41 árs, innkaupastjóri"]},
    {"n":2,"status":"verified","claim":"innkaupastjóri","quotes":["Hannes Kristinn Sigurðsson, 41 árs, innkaupastjóri"]},
    {"n":3,"status":"verified","claim":"10. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum","quotes":["Hannes Kristinn Sigurðsson, 41 árs, innkaupastjóri"]},
    {"n":4,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram um allt land 16. maí 2026"]},
    {"n":5,"status":"flagged","claim":"fyrrverandi formaður framkvæmda- og hafnarráðs","notes":"Eyjafréttir segja: „aðalmaður í Framkvæmda- og hafnarráði, nú síðast sem varaformaður“. Bio orð „formaður“ er rangt — hann var varaformaður, ekki formaður. Title misnaming (formaður vs varaformaður)."},
    {"n":6,"status":"flagged","claim":"hefur setið í stjórn Sjálfstæðisflokksins í Eyjum frá 2011","notes":"Eyjafréttir segja að hann gekk í stjórn EYVERJA (félags ungra sjálfstæðismanna) 2011 — ekki í stjórn flokksins sjálfs í Eyjum. Title conflation."},
    {"n":7,"status":"verified","claim":"gekk í stjórn ungliðahreyfingarinnar Eyverja 2011","quotes":["2011, þegar ég tók sæti í stjórn Eyverja, félags ungra sjálfstæðismanna í Vestmannaeyjum"]},
    {"n":8,"status":"verified","claim":"tók þátt í prófkjöri flokksins fyrir fjórum árum","quotes":["prófkjöri Sjálfstæðisflokksins fyrir fjórum árum og hef síðan þá setið sem aðalmaður í Framkvæmda- og hafnarráði"]},
    {"n":9,"status":"verified","claim":"áherslumál: innviðauppbygging, stórskipahöfn við Eiðið, Herjólfur, fjölgun íbúa","quotes":["hafnargetu og móttöku stærri skipa til Vestmannaeyja","Eiðinu og uppbygging Laxeyjar","Herjólf með það að markmiði að draga úr framlagi"]},
    {"n":10,"status":"verified","claim":"eiginkona Fanney Finnbogadóttir","quotes":["Giftur Fanney Finnbogadóttur"]},
    {"n":11,"status":"verified","claim":"tveir synir Elías Agnar (2014) og Eyvar Bogi (2021)","quotes":["eigum tvo drengi, Elías Agnar Hannesson (2014) Eyvar Bogi Hannesson (2021)"]}
  ],
  "summary": "9 verified, 0 rescued, 2 flagged",
  "rescue": {
    "rewrite": "Hannes Kristinn Sigurðsson er 41 árs innkaupastjóri og skipar 10. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum fyrir sveitarstjórnarkosningarnar 16. maí 2026. Hann hefur frá prófkjöri flokksins fyrir fjórum árum setið sem aðalmaður í framkvæmda- og hafnarráði Vestmannaeyjabæjar, nú síðast sem varaformaður, og tók sæti í stjórn ungliðahreyfingarinnar Eyverja 2011. Meðal áherslumála hans eru aukin hafnargeta og móttaka stærri skipa við Eiðið, endurbætur á aðstöðu Herjólfs og fjölgun íbúa. Eiginkona hans er Fanney Finnbogadóttir og eiga þau tvo drengi, Elías Agnar (2014) og Eyvar Boga (2021).",
    "rewrite_words": 99,
    "new_sources": [],
    "resolutions": [
      {"kind":"contradicted","text":"„Formaður framkvæmda- og hafnarráðs“ → í raun varaformaður (skv. Eyjafréttum). Title misnaming."},
      {"kind":"contradicted","text":"„Stjórn Sjálfstæðisflokksins í Eyjum“ → í raun stjórn ungliðahreyfingarinnar Eyverja. Title conflation."}
    ],
    "new_heimild": []
  }
})

# VME.D.11 Ragnheiður Lind
records.append({
  "id": "VME.D.11",
  "bio": "Ragnheiður Lind Geirsdóttir er sjúkraliði og deildarstjóri dagdvalar í Vestmannaeyjum og hefur víðtæka reynslu af daglegum störfum með eldra fólki. Í skrifum sínum hefur hún lagt áherslu á samþætta þjónustu við eldri borgara, þar á meðal mikilvægi dagdvala, samhæfðrar heimaþjónustu og forvarnaverkefna á borð við Janus-heilsueflingu fyrir 65 ára og eldri. Hún skipar 11. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum fyrir sveitarstjórnarkosningarnar 16. maí 2026 og var 38 ára þegar listinn var samþykktur.",
  "sources": [
    "https://eyjafrettir.is/efri-arin-skipta-mali/",
    "https://xd.is/2026/03/31/frambodslisti-sjalfstaedisflokksins-i-vestmannaeyjum/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"sjúkraliði og deildarstjóri dagdvalar","quotes":["sjúkraliði og deildarstjóri dagdvalar hef ég áralanga reynslu af daglegu starfi með eldra fólki","Ragnheiður Lind Geirsdóttir, 38 ára, sjúkraliði"]},
    {"n":2,"status":"verified","claim":"hefur víðtæka reynslu af daglegum störfum með eldra fólki","quotes":["áralanga reynslu af daglegu starfi með eldra fólki"]},
    {"n":3,"status":"verified","claim":"áhersla á samþætta þjónustu við eldri borgara, dagdvalir, heimahjúkrun, Janus","quotes":["dagdvalar við heimahjúkrun, stuðningsþjónustu, heilsugæslu, sjúkradeild og aðstandendur","Janus-verkefnið verði styrkt enn frekar og samofið annarri þjónustu við eldri borgara, svo til verði samfella frá forvörnum yfir í stuðningsúrræði"]},
    {"n":4,"status":"verified","claim":"Janus-heilsuefling fyrir 65 ára og eldri","quotes":["Janus-verkefnið – hreyfing og forvarnir fyrir 65+ sem skila árangri","hreyfi- og forvarnarverkefni fyrir fólk 65 ára og eldra"]},
    {"n":5,"status":"flagged","claim":"„heimaþjónustu“ (sjálfstæð fullyrðing)","notes":"Eyjafréttir nefna „heimahjúkrun“ — ekki orðið „heimaþjónustu“ sérstaklega. Look-alike word swap (heimahjúkrun vs heimaþjónustu). Litlu munar en er ekki bein tilvitnun."},
    {"n":6,"status":"verified","claim":"11. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum","quotes":["Ragnheiður Lind Geirsdóttir Skipar 11"]},
    {"n":7,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram um allt land 16. maí 2026"]},
    {"n":8,"status":"verified","claim":"38 ára","quotes":["Ragnheiður Lind Geirsdóttir, 38 ára, sjúkraliði"]}
  ],
  "summary": "7 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Ragnheiður Lind Geirsdóttir er sjúkraliði og deildarstjóri dagdvalar í Vestmannaeyjum og hefur áralanga reynslu af daglegu starfi með eldra fólki. Í skrifum sínum hefur hún lagt áherslu á samþætta þjónustu við eldri borgara — dagdvöl, heimahjúkrun, heilsugæslu og forvarnaverkefni — og að Janus-verkefnið, hreyfi- og forvarnarverkefni fyrir 65 ára og eldri, verði styrkt enn frekar. Hún skipar 11. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum fyrir sveitarstjórnarkosningarnar 16. maí 2026, 38 ára að aldri.",
    "rewrite_words": 75,
    "new_sources": [],
    "resolutions": [
      {"kind":"contradicted","text":"„Heimaþjónustu“ → eyjafréttir segja „heimahjúkrun“ — small look-alike swap"}
    ],
    "new_heimild": []
  }
})

# VME.D.14 Guðríður
records.append({
  "id": "VME.D.14",
  "bio": "Guðríður Jónsdóttir er grunnskólakennari í Vestmannaeyjum og skipar 14. sæti á lista Sjálfstæðisflokksins í bæjarstjórnarkosningunum 16. maí 2026. Í aðsendum greinum hefur hún lagt áherslu á sterkari grunnskóla og að mæta þörfum allra nemenda, og talað fyrir þróun skólastarfs sem snýr ekki einungis að árangri á samræmdum prófum heldur að alhliða þroska barna. Hún var 54 ára þegar listinn var samþykktur.",
  "sources": [
    "https://eyjafrettir.is/sterkari-grunnskoli-og-oflugri-framtid/",
    "https://xd.is/2026/03/31/frambodslisti-sjalfstaedisflokksins-i-vestmannaeyjum/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"grunnskólakennari","quotes":["Guðríður Jónsdóttir, grunnskólakennari","Guðríður Jónsdóttir, 54 ára, grunnskólakennari"]},
    {"n":2,"status":"verified","claim":"í Vestmannaeyjum","quotes":["Hvað er það sem við viljum fá út úr grunnskólum okkar hér í Vestmannaeyjum?"]},
    {"n":3,"status":"verified","claim":"14. sæti á lista Sjálfstæðisflokksins","quotes":["Guðríður Jónsdóttir, 54 ára, grunnskólakennari"]},
    {"n":4,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram um allt land 16. maí 2026"]},
    {"n":5,"status":"verified","claim":"hefur lagt áherslu á sterkari grunnskóla","quotes":["Sterkari grunnskóli og öflugri framtíð"]},
    {"n":6,"status":"verified","claim":"talað fyrir þróun skólastarfs sem snýr ekki einungis að árangri á samræmdum prófum heldur að alhliða þroska barna","quotes":["Eru það eingöngu háar einkunnir, eða er það að ala upp sjálfstæða, hamingjusama og virka þjóðfélagsþegna sem eru tilbúnir út í lífið?"]},
    {"n":7,"status":"flagged","claim":"„að mæta þörfum allra nemenda“","notes":"Almenn fullyrðing — má álykta út frá greininni en er ekki bein tilvitnun. Drop sem ónákvæm."},
    {"n":8,"status":"verified","claim":"54 ára","quotes":["Guðríður Jónsdóttir, 54 ára, grunnskólakennari"]}
  ],
  "summary": "7 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Guðríður Jónsdóttir er grunnskólakennari í Vestmannaeyjum og skipar 14. sæti á lista Sjálfstæðisflokksins í Vestmannaeyjum fyrir sveitarstjórnarkosningarnar 16. maí 2026. Í aðsendri grein hefur hún spurt hvort markmið grunnskólastarfs sé „eingöngu háar einkunnir“ eða að ala upp „sjálfstæða, hamingjusama og virka þjóðfélagsþegna“. Hún var 54 ára þegar listinn var samþykktur.",
    "rewrite_words": 56,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"„Að mæta þörfum allra nemenda“ — ekki bein tilvitnun"}
    ],
    "new_heimild": []
  }
})

for r in records:
    save(r)
