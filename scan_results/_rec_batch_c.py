# -*- coding: utf-8 -*-
"""Batch C: Suðurnesjabær (SNB) candidates"""
import sys
sys.path.insert(0, r'F:\Claude Projects\iceland-elections\scan_results')
from _proc_14 import save

records = []

# SNB.B.4 Sindri Lars Ómarsson — MAJOR FLAG: bio borrows Fríða Stefánsdóttir's bio (samfélagsfræði/leiklist 2008, Comenius, nemendaráðs umsjón).
records.append({
  "id": "SNB.B.4",
  "bio": "Sindri Lars Ómarsson skipar 4. sæti á lista Framsóknar og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026. Hann er grunnskólakennari og hefur starfað sem umsjónarkennari við Sandgerðisskóla allt frá árinu 2008. Sindri lauk B.Ed.-prófi frá Menntavísindasviði Háskóla Íslands árið 2008 með samfélagsfræði og leiklist sem kjörsvið. Innan skólans hefur hann meðal annars verið umsjónarmaður nemendaráðs og tekið þátt í evrópsku Comenius-samstarfsverkefni.",
  "sources": [
    "https://www.sandgerdisskoli.is/is/starfsfolk",
    "https://kosningasaga.wordpress.com/2026/03/04/frambodslisti-framsoknar-og-ohadra-i-sudurnesjabae/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"4. sæti á lista Framsóknar og óháðra í Suðurnesjabæ","quotes":["Sindri Lars í 4. sæti var á Bæjarlistanum í síðustu kosningum","Sindri Lars Ómarsson grunnskólakennari"]},
    {"n":2,"status":"verified","claim":"grunnskólakennari","quotes":["Sindri Lars Ómarsson grunnskólakennari","Sindri Lars Ómarsson Starfsheiti Umsjónarkennari 8. bekkjar"]},
    {"n":3,"status":"verified","claim":"umsjónarkennari við Sandgerðisskóla","quotes":["Sindri Lars Ómarsson Starfsheiti Umsjónarkennari 8. bekkjar Netfang sindri@sandgerdisskoli.is"]},
    {"n":4,"status":"flagged","claim":"hefur starfað við Sandgerðisskóla allt frá árinu 2008","notes":"Þetta er textinn úr bio-grein Fríðu Stefánsdóttur (Deildastjóra) sem situr beint fyrir aftan Sindra á starfsmannasíðunni. Sindra-spjaldið hefur engan bio-texta. Profession-aggregator scrape hallucination — bio Fríðu var ranglega tengd við Sindra."},
    {"n":5,"status":"flagged","claim":"B.Ed.-próf frá Menntavísindasviði Háskóla Íslands 2008 með samfélagsfræði og leiklist sem kjörsvið","notes":"Sami texti kemur úr biographi Fríðu Stefánsdóttur. Engin opinber heimild staðfestir þessar upplýsingar fyrir Sindra Lars."},
    {"n":6,"status":"flagged","claim":"umsjónarmaður nemendaráðs og tekið þátt í Comenius-samstarfsverkefni","notes":"Sömuleiðis úr bio Fríðu Stefánsdóttur — ekki Sindra Lars."}
  ],
  "summary": "3 verified, 0 rescued, 3 flagged (öll sömu uppruna — eitt rangtenging við bio annars starfsmanns)",
  "rescue": {
    "rewrite": "Sindri Lars Ómarsson er grunnskólakennari og umsjónarkennari 8. bekkjar við Sandgerðisskóla. Hann skipar 4. sæti á B-lista Framsóknar og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026 og var áður á Bæjarlistanum í síðustu kosningum.",
    "rewrite_words": 41,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"Að hafa starfað við Sandgerðisskóla frá 2008 — texti úr bio annars starfsmanns (Fríðu Stefánsdóttur) sem var rangtengdur"},
      {"kind":"dropped","text":"B.Ed.-próf 2008 í samfélagsfræði og leiklist — texti úr bio annars starfsmanns"},
      {"kind":"dropped","text":"Umsjón nemendaráðs og Comenius-verkefni — texti úr bio annars starfsmanns"}
    ],
    "new_heimild": []
  }
})

# SNB.B.6 Gísli Jónatan Pálsson — bio says trésmiður; kosningasaga says húsamiður (likely typo for húsasmiður). VF gives no occupation.
records.append({
  "id": "SNB.B.6",
  "bio": "Gísli Jónatan Pálsson er trésmiður og íbúi í Sandgerði. Hann hefur áður lagt stund á nám í byggingariðn samhliða störfum sínum. Gísli skipar 6. sæti á B-lista Framsóknar og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026; oddviti listans er Anton Kristinn Guðmundsson, núverandi bæjarfulltrúi.",
  "sources": [
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae",
    "https://www.sudurnesjabaer.is/is/moya/news/frambodslistar-i-sveitarstjornarkosningum"
  ],
  "statements": [
    {"n":1,"status":"flagged","claim":"trésmiður","notes":"VF nefnir engan starfsheiti. Kosningasaga nefnir „húsamiður“ (líklega innsláttarvilla fyrir „húsasmiður“) — ekki „trésmiður“. Profession-mismatch."},
    {"n":2,"status":"verified","claim":"íbúi í Sandgerði","quotes":["Gísli Jónatan Pálsson (Sandgerði)"]},
    {"n":3,"status":"flagged","claim":"hefur áður lagt stund á nám í byggingariðn","notes":"Engin tilvitnun í neinni heimild fyrir námsferli."},
    {"n":4,"status":"verified","claim":"6. sæti á B-lista Framsóknar og óháðra í Suðurnesjabæ","quotes":["B-listinn: Framsókn og óháðir Anton Kristinn Guðmundsson (Sandgerði) Magnús Sigfús Magnússon (Sandgerði) Ólöf Ólafsdóttir (Sandgerði) Sindri Lars Ómarsson (Garður) Ewa Krysztopa (Sandgerði) Gísli Jónatan Pálsson (Sandgerði)"]},
    {"n":5,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]},
    {"n":6,"status":"verified","claim":"oddviti listans er Anton Kristinn Guðmundsson","quotes":["Oddvitinn Anton Kristinn Guðmundsson leiðir hópinn"]},
    {"n":7,"status":"rescued","claim":"Anton Kristinn er bæjarfulltrúi","quotes":["Anton Kristinn Guðmundsson bæjarfulltrúi og stjórnsýslufræðingur"]}
  ],
  "summary": "4 verified, 1 rescued, 2 flagged",
  "rescue": {
    "rewrite": "Gísli Jónatan Pálsson býr í Sandgerði og skipar 6. sæti á B-lista Framsóknar og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026. Oddviti listans er Anton Kristinn Guðmundsson, bæjarfulltrúi og stjórnsýslufræðingur.",
    "rewrite_words": 36,
    "new_sources": ["https://kosningasaga.wordpress.com/2026/03/04/frambodslisti-framsoknar-og-ohadra-i-sudurnesjabae/"],
    "resolutions": [
      {"kind":"contradicted","text":"Bio segir „trésmiður“ en eina starfsheitislýsing finnst í kosningasaga: „húsamiður“ (líklega innsláttarvilla fyrir húsasmiður). Drop „trésmiður“ vegna óvissu."},
      {"kind":"dropped","text":"Sjálfstæð fullyrðing um fyrri byggingariðnnám — engin staðfesting"}
    ],
    "new_heimild": [
      {"url":"https://kosningasaga.wordpress.com/2026/03/04/frambodslisti-framsoknar-og-ohadra-i-sudurnesjabae/","label":"Kosningasaga — Framboðslisti Framsóknar í Suðurnesjabæ"}
    ]
  }
})

# SNB.D.16 Jón Kristinn Snæhólm — MANY claims, bio has dates 1993, 1996, varaborgarfulltrúi Kópavogi 1990 (mannlif says 1990 í Kópavogi), aðstoðarmaður Vilhjálms 2006-2008 (mannlif says "Vilhjálmi í þessi tvö ár"), innréttingar frá Úkraínu (V), ÍNN frá 2008 — let me check
records.append({
  "id": "SNB.D.16",
  "bio": "Jón Kristinn Snæhólm er sagnfræðingur og alþjóðastjórnmálafræðingur að mennt. Hann lauk BA-prófi í sögu frá Háskóla Íslands 1993 og meistaraprófi í evrópskum og alþjóðlegum stjórnmálum frá Háskólanum í Edinborg 1996. Jón Kristinn hefur lengi starfað í tengslum við Sjálfstæðisflokkinn, var meðal annars varaborgarfulltrúi í Kópavogi 1990 og aðstoðarmaður Vilhjálms Þ. Vilhjálmssonar borgarstjóra Reykjavíkur 2006–2008. Hann hefur einnig rekið innflutningsfyrirtæki sem flytur inn innréttingar frá Úkraínu og verið dagskrárgerðarmaður á sjónvarpsstöðinni ÍNN frá 2008. Hann skipar 16. sæti á lista Sjálfstæðisflokksins og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026.",
  "sources": [
    "https://gamla.mannlif.is/frettir/jon-kristinn-snaeholm-um-astina-sjalfstaedisflokkinn-og-ukrainu-vaknadi-halflamadur-haegra-megin/",
    "https://www.mannlif.is/veftv/mannlifid-jon-kristinn-snaeholm/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"sagnfræðingur og alþjóðastjórnmálafræðingur að mennt","quotes":["Jón Kristinn sem er sagnfræðingur og alþjóðastjórnmálafræðingur"]},
    {"n":2,"status":"flagged","claim":"BA-próf í sögu frá Háskóla Íslands 1993","notes":"Tilvitnun finnst ekki í tilteknum mannlif-greinum. Engin staðfest dagsetning eða stofnun fyrir gráðuna."},
    {"n":3,"status":"flagged","claim":"meistarapróf í evrópskum og alþjóðlegum stjórnmálum frá Háskólanum í Edinborg 1996","notes":"Sömuleiðis ekki í tilteknum mannlif-heimildum."},
    {"n":4,"status":"flagged","claim":"varaborgarfulltrúi í Kópavogi 1990","notes":"Mannlif segir „1990 í Kópavogi og starfaði með öndvegismönnum, Gunnari Birgissyni og Sigurði Geirdal, í tvö kjörtímabil og lærði mikið“ — en starfsheiti („varaborgarfulltrúi“) er ekki tekið fram í mannlif-grein. Kópavogur er ekki borg → „varabæjarfulltrúi“ væri rétt heiti. Title misframing."},
    {"n":5,"status":"verified","claim":"aðstoðarmaður Vilhjálms Þ. Vilhjálmssonar borgarstjóra Reykjavíkur","quotes":["Vilhjálmi í þessi tvö ár breytti mér mjög mikið; úr hörðu hægri yfir í milt hægri","Vilhjálms Þ. Vilhjálmssonar, þáverandi borgarstjóra"]},
    {"n":6,"status":"flagged","claim":"árin 2006–2008 (sjálfstæð dagsetning)","notes":"Vilhjálmur Þ. var borgarstjóri 2006–2007/2008, en mannlif segir aðeins „í þessi tvö ár“ án nákvæmra dagsetninga. Generelt verifyable utan grein."},
    {"n":7,"status":"verified","claim":"rekið innflutningsfyrirtæki sem flytur inn innréttingar frá Úkraínu","quotes":["hann rekur innflutningsfyrirtæki sem flytur meðal annars inn eldhúsinnréttingar, hurðir og skápa frá Úkraínu"]},
    {"n":8,"status":"flagged","claim":"dagskrárgerðarmaður á sjónvarpsstöðinni ÍNN frá 2008","notes":"Engin tilvitnun um ÍNN í tilteknum mannlif-heimildum."},
    {"n":9,"status":"flagged","claim":"skipar 16. sæti á lista Sjálfstæðisflokksins og óháðra í Suðurnesjabæ","notes":"Mannlif-greinarnar fjalla ekki um framboðið 2026. Kosningasaga D-listinn nefnir „Jón Kristinn Snæhólm, alþjóðastjórnmálafræðingur“ á eftir Gunnari Häsler — sætisnúmer er ekki tilgreint, en hann er á listanum."}
  ],
  "summary": "3 verified, 0 rescued, 6 flagged",
  "rescue": {
    "rewrite": "Jón Kristinn Snæhólm er sagnfræðingur og alþjóðastjórnmálafræðingur. Hann starfaði í tvö ár sem aðstoðarmaður Vilhjálms Þ. Vilhjálmssonar þáverandi borgarstjóra Reykjavíkur og hafði áður tekið þátt í sveitarstjórnarmálum í Kópavogi. Hann rekur innflutningsfyrirtæki sem flytur meðal annars inn eldhúsinnréttingar, hurðir og skápa frá Úkraínu. Jón Kristinn er á lista Sjálfstæðisflokksins og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026.",
    "rewrite_words": 70,
    "new_sources": ["https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/"],
    "resolutions": [
      {"kind":"dropped","text":"Nákvæmar gráðu-dagsetningar 1993/1996 og stofnanaheiti — ekki staðfest í tilteknum heimildum"},
      {"kind":"dropped","text":"„Varaborgarfulltrúi“ í Kópavogi — Kópavogur er ekki borg; engin staðfesting á starfsheiti, aðeins virkni 1990"},
      {"kind":"dropped","text":"Nákvæmu dagsetningar 2006–2008 fyrir aðstoðarmannsstöðu — ekki staðfest með nákvæmum dögum"},
      {"kind":"dropped","text":"ÍNN dagskrárgerðarmaður frá 2008 — ekki staðfest"}
    ],
    "new_heimild": [
      {"url":"https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/","label":"Kosningasaga — D-listi Suðurnesjabæjar"}
    ]
  }
})

# SNB.D.18 Einar Jón Pálsson — many claims, lots flagged
records.append({
  "id": "SNB.D.18",
  "bio": "Einar Jón Pálsson er forseti bæjarstjórnar Suðurnesjabæjar og oddviti Sjálfstæðisflokksins og óháðra í sveitarfélaginu. Hann er fæddur 1967 í Keflavík og uppalinn í Garði þar sem hann hefur búið mestan hluta ævinnar. Einar Jón lauk sveinsprófi í rafvirkjun frá Fjölbrautaskóla Suðurnesja 1989 og meistaraprófi frá sama skóla 1994. Hann starfaði í tíu ár sem rafvirki hjá Sigurði Ingvarssyni rafverktaka í Garði og síðan í tvö ár hjá Varnarliðinu við verkáætlanagerð. Einar Jón hefur lengi tekið þátt í sveitarstjórnarmálum, var áður oddviti í Sveitarfélaginu Garði og hefur leitt lista sjálfstæðismanna í Suðurnesjabæ frá sameiningu sveitarfélaganna 2018. Hann tilkynnti í febrúar 2026 að hann sæktist ekki eftir oddvitasæti aftur en skipar nú heiðurssætið, 18. sæti á lista Sjálfstæðisflokksins og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026.",
  "sources": [
    "https://kosningasaga.wordpress.com/2026/02/27/einar-jon-haettir-i-sudurnesjabae/",
    "https://svgardur.is/einar-j%C3%B3n-p%C3%A1lsson"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"forseti bæjarstjórnar Suðurnesjabæjar og oddviti Sjálfstæðisflokksins og óháðra","quotes":["Einar Jón Pálsson forseti bæjarstjórnar í Suðurnesjabæ og oddviti Sjálfstæðisflokksins og óháðra"]},
    {"n":2,"status":"flagged","claim":"fæddur 1967 í Keflavík","notes":"svgardur.is hleðst ekki upp (status 0 í cache, 404 við endurfetch). Engin opinber heimild staðfestir í tilteknum heimildum."},
    {"n":3,"status":"flagged","claim":"uppalinn í Garði","notes":"Sömu ástæða — heimildir hleðast ekki."},
    {"n":4,"status":"flagged","claim":"sveinspróf í rafvirkjun frá FS 1989","notes":"Engin staðfest tilvitnun (svgardur ófáanlegt)."},
    {"n":5,"status":"flagged","claim":"meistarapróf frá FS 1994","notes":"Sömuleiðis."},
    {"n":6,"status":"flagged","claim":"starfaði í tíu ár sem rafvirki hjá Sigurði Ingvarssyni rafverktaka í Garði","notes":"Engin staðfest heimild í tilteknum heimildum."},
    {"n":7,"status":"flagged","claim":"tvö ár hjá Varnarliðinu við verkáætlanagerð","notes":"Engin staðfest heimild."},
    {"n":8,"status":"flagged","claim":"var áður oddviti í Sveitarfélaginu Garði","notes":"Engin staðfest tilvitnun, en má álykta út frá VF: „setið í bæjarstjórn í 24 ár, þar af verið oddviti listans síðustu 16 ár“."},
    {"n":9,"status":"flagged","claim":"hefur leitt lista sjálfstæðismanna í Suðurnesjabæ frá sameiningu sveitarfélaganna 2018","notes":"Sameining Garðs og Sandgerðis varð 2018. VF: oddviti í 16 ár — sem væri frá ~2010, þ.e.a.s. fyrir sameiningu. Misframing — hann var oddviti í Garði fyrir 2018, og leiddi sameinaða listann eftir 2018."},
    {"n":10,"status":"verified","claim":"tilkynnti í febrúar 2026 að hann sæktist ekki eftir oddvitasæti aftur","quotes":["Einar Jón Pálsson forseti bæjarstjórnar í Suðurnesjabæ og oddviti Sjálfstæðisflokksins og óháðra hefur tilkynnt uppstillingarnefnd að hann gefi ekki kost á sér til að leiða listinn í komandi sveitarstjórnarkosningum","Birt þann 27. febrúar 2026"]},
    {"n":11,"status":"rescued","claim":"skipar 18. sæti á lista Sjálfstæðisflokksins og óháðra","quotes":["Einar Jón Pálsson, forseti bæjarstjórnar"]}
  ],
  "summary": "2 verified, 1 rescued, 8 flagged",
  "rescue": {
    "rewrite": "Einar Jón Pálsson er forseti bæjarstjórnar Suðurnesjabæjar og oddviti Sjálfstæðisflokksins og óháðra. Hann tilkynnti í febrúar 2026 uppstillingarnefnd að hann gæfi ekki kost á sér til að leiða listann að nýju og hefur að eigin sögn setið í bæjarstjórn í 24 ár, þar af 16 ár sem oddviti og 14 ár sem forseti bæjarstjórnar. Einar Jón skipar nú heiðurssætið, 18. sæti, á lista Sjálfstæðisflokksins og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026.",
    "rewrite_words": 76,
    "new_sources": [
      "https://www.vf.is/frettir/einar-jon-palsson-gefur-ekki-kost-a-ser-sem-oddviti-d-listans-i-sudurnesjabae",
      "https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/"
    ],
    "resolutions": [
      {"kind":"dropped","text":"Fæðingardagur, námsferill, atvinnusaga (Sigurður Ingvarsson, Varnarliðið) — heimildin svgardur.is óaðgengileg, engin staðfesting í öðrum heimildum"},
      {"kind":"contradicted","text":"„Leitt lista frá sameiningu 2018“ er misvísandi — VF segir hann hafi verið oddviti í 16 ár (þ.e. frá ~2010), m.a. í Garði fyrir sameiningu og í Suðurnesjabæ eftir 2018"}
    ],
    "new_heimild": [
      {"url":"https://www.vf.is/frettir/einar-jon-palsson-gefur-ekki-kost-a-ser-sem-oddviti-d-listans-i-sudurnesjabae","label":"Víkurfréttir — Einar Jón gefur ekki kost á sér"},
      {"url":"https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/","label":"Kosningasaga — D-listi Suðurnesjabæjar"}
    ]
  }
})

# SNB.D.6 Margrét Edda — verified
records.append({
  "id": "SNB.D.6",
  "bio": "Margrét Edda Arnardóttir er atvinnurekandi og íþróttaþjálfari og býr í Garði. Hún skipar 6. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026; oddviti listans er Haukur Andreasson.",
  "sources": [
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae",
    "https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"atvinnurekandi og íþróttaþjálfari","quotes":["Margrét Edda Arnardóttir, atvinnurekandi og íþróttaþjálfari"]},
    {"n":2,"status":"verified","claim":"býr í Garði","quotes":["Margrét Edda Arnardóttir (Garður)"]},
    {"n":3,"status":"verified","claim":"6. sæti á D-lista Sjálfstæðisflokks og óháðra","quotes":["D-listinn: D-listinn og óháðir Haukur Andreasson (Sandgerði) Haraldur Helgason (Garður) Oddný Kristrún Ásgeirsdóttir (Garður) María Kjartansdóttir (Garður) Berglind Lára Haraldsdóttir (Sandgerði) Margrét Edda Arnardóttir (Garður)"]},
    {"n":4,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]},
    {"n":5,"status":"verified","claim":"oddviti listans er Haukur Andreasson","quotes":["Oddvitinn Haukur Andreasson býr í Sandgerði"]}
  ],
  "summary": "5 verified, 0 rescued, 0 flagged",
  "rescue": None
})

# SNB.D.7 Fannar Logi — bio: nýstúdent — útskrifaður á tveimur og hálfu ári — og skógarmaður, býr í Garði, 7. sæti D 16. maí
records.append({
  "id": "SNB.D.7",
  "bio": "Fannar Logi Waldorff Sigurðsson er nýstúdent — útskrifaður á tveimur og hálfu ári — og skógarmaður og býr í Garði. Hann skipar 7. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
  "sources": [
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae",
    "https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"nýstúdent — útskrifaður á tveimur og hálfu ári","quotes":["Fannar Logi Waldorff Sigurðsson, nýstúdent á 2"]},
    {"n":2,"status":"flagged","claim":"skógarmaður","notes":"Tilvitnun fyrir „skógarmaður“ finnst ekki — kosningasaga slítur textann af við „nýstúdent á 2…“. VF nefnir engan starfsheiti."},
    {"n":3,"status":"verified","claim":"býr í Garði","quotes":["Fannar Logi Waldorff Sigurðsson (Garður)"]},
    {"n":4,"status":"verified","claim":"7. sæti á D-lista Sjálfstæðisflokks og óháðra","quotes":["Margrét Edda Arnardóttir (Garður) Fannar Logi Waldorff Sigurðsson (Garður) Arnar Geir Gestsson (Sandgerði)"]},
    {"n":5,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]}
  ],
  "summary": "4 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Fannar Logi Waldorff Sigurðsson er nýstúdent — útskrifaður á tveimur og hálfu ári — og býr í Garði. Hann skipar 7. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
    "rewrite_words": 35,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"„Skógarmaður“ — engin staðfesting"}
    ],
    "new_heimild": []
  }
})

# SNB.D.8 Arnar Geir — verified through vatnsidnadur + kosningasaga
records.append({
  "id": "SNB.D.8",
  "bio": "Arnar Geir Gestsson er löggiltur pípulagningameistari og rekur eigið fyrirtæki, Pípulagnir Arnar Geirs ehf. (AG pípulagnir), í Sandgerði þar sem hann býr. Hann hlaut meistarabréf í pípulagningum árið 2022 og er skráður á opinberum lista löggiltra pípulagningameistara hjá Vatnsiðnaði. Arnar Geir skipar 8. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
  "sources": [
    "https://vatnsidnadur.net/2022/08/24/arnar-geir-gestsson/",
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"löggiltur pípulagningameistari","quotes":["Arnar Geir Gestsson eftir Vatnsidnadur · ágúst 24, 2022 Grein/Linkur: LÖGGILTUR PÍPULAGNINGAMEISTARI","löggiltir pípulagningameistara Arnar Geir Gestsson"]},
    {"n":2,"status":"verified","claim":"rekur eigið fyrirtæki Pípulagnir Arnar Geirs ehf.","quotes":["Fyrirtæki/vinnustaður Pípulagnir Arnar Geirs ehf"]},
    {"n":3,"status":"flagged","claim":"AG pípulagnir (vörumerki)","notes":"Vatnsidnadur skráir aðeins „Pípulagnir Arnar Geirs ehf“. „AG pípulagnir“ er sérstakt vörumerki/styttingarheiti sem ekki er staðfest í tilteknum heimildum."},
    {"n":4,"status":"verified","claim":"í Sandgerði þar sem hann býr","quotes":["Arnar Geir Gestsson Búseta Sandgerði","Arnar Geir Gestsson (Sandgerði)"]},
    {"n":5,"status":"rescued","claim":"hlaut meistarabréf 2022","quotes":["Arnar Geir Gestsson eftir Vatnsidnadur · ágúst 24, 2022 Grein/Linkur: LÖGGILTUR PÍPULAGNINGAMEISTARI"]},
    {"n":6,"status":"verified","claim":"skráður á opinberum lista löggiltra pípulagningameistara hjá Vatnsiðnaði","quotes":["Vatnsiðnaður Leita að: Fróðleikur A-Ö Löggiltir Pípulagningameistarar"]},
    {"n":7,"status":"verified","claim":"8. sæti á D-lista Sjálfstæðisflokks og óháðra","quotes":["Margrét Edda Arnardóttir (Garður) Fannar Logi Waldorff Sigurðsson (Garður) Arnar Geir Gestsson (Sandgerði) Sólmundur Ingi Einvarðsson (Garður)"]},
    {"n":8,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]}
  ],
  "summary": "6 verified, 1 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Arnar Geir Gestsson er löggiltur pípulagningameistari og rekur eigið fyrirtæki, Pípulagnir Arnar Geirs ehf., í Sandgerði þar sem hann býr. Hann hlaut meistarabréf í pípulagningum í ágúst 2022 og er skráður á opinberum lista löggiltra pípulagningameistara hjá Vatnsiðnaði. Arnar Geir skipar 8. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
    "rewrite_words": 60,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"„AG pípulagnir“ vörumerki — ekki staðfest í Vatnsiðnaði"}
    ],
    "new_heimild": []
  }
})

# SNB.D.9 Sólmundur Ingi — bio: framkvæmdastjóri rekstrarsviðs Skólamatar, fjölskyldufyrirtæki Reykjanesbæ, leik- og grunnskóla
records.append({
  "id": "SNB.D.9",
  "bio": "Sólmundur Ingi Einvarðsson er framkvæmdastjóri rekstrarsviðs hjá Skólamat ehf., fjölskyldufyrirtæki með aðsetur í Reykjanesbæ sem framleiðir og þjónustar mat fyrir leik- og grunnskóla víða um land. Hann er búsettur í Garði og skipar 9. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
  "sources": [
    "https://www.skolamatur.is/",
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae"
  ],
  "statements": [
    {"n":1,"status":"rescued","claim":"framkvæmdastjóri rekstrarsviðs hjá Skólamat ehf.","quotes":["Sólmundur Ingi Einvarðsson, framkvæmdastjóri rekstrarsviðs Skólamatar"]},
    {"n":2,"status":"flagged","claim":"fjölskyldufyrirtæki","notes":"Skólamatur-vefur nefnir ekki „fjölskyldufyrirtæki“ beint."},
    {"n":3,"status":"verified","claim":"aðsetur í Reykjanesbæ","quotes":["Reykjanesbær Afgreiðslutími 8:00–16:00"]},
    {"n":4,"status":"verified","claim":"framleiðir og þjónustar mat fyrir leik- og grunnskóla","quotes":["leik- og grunnskólaaldri"]},
    {"n":5,"status":"flagged","claim":"„víða um land“","notes":"Skólamatur listi sýnir mörg sveitarfélög en orðalagið „víða um land“ er ekki bein tilvitnun."},
    {"n":6,"status":"verified","claim":"búsettur í Garði","quotes":["Sólmundur Ingi Einvarðsson (Garður)"]},
    {"n":7,"status":"verified","claim":"9. sæti á D-lista Sjálfstæðisflokks og óháðra","quotes":["Arnar Geir Gestsson (Sandgerði) Sólmundur Ingi Einvarðsson (Garður)"]},
    {"n":8,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]}
  ],
  "summary": "5 verified, 1 rescued, 2 flagged",
  "rescue": {
    "rewrite": "Sólmundur Ingi Einvarðsson er framkvæmdastjóri rekstrarsviðs hjá Skólamat ehf., fyrirtæki með aðsetur í Reykjanesbæ sem framreiðir mat fyrir leik- og grunnskóla. Hann er búsettur í Garði og skipar 9. sæti á D-lista Sjálfstæðisflokks og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
    "rewrite_words": 49,
    "new_sources": ["https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/"],
    "resolutions": [
      {"kind":"dropped","text":"„Fjölskyldufyrirtæki“ — ekki staðfest"},
      {"kind":"dropped","text":"„Víða um land“ — ekki bein tilvitnun"}
    ],
    "new_heimild": [
      {"url":"https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/","label":"Kosningasaga — D-listi Suðurnesjabæjar"}
    ]
  }
})

# SNB.M.8 Brynjar Þór
records.append({
  "id": "SNB.M.8",
  "bio": "Brynjar Þór Kristinsson er íbúi í Garði og skipar 8. sæti á M-lista Miðflokksins í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026. Oddviti listans er Daði Bergþórsson. Miðflokksdeild Suðurnesjabæjar var stofnuð í mars 2026, en flokkurinn býður nú fram í fyrsta sinn í sveitarfélaginu.",
  "sources": [
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae",
    "https://midflokkurinn.is/midflokksdeild-sudurnesjabaejar-stofnud"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"íbúi í Garði","quotes":["Brynjar Þór Kristinsson (Garður)"]},
    {"n":2,"status":"verified","claim":"8. sæti á M-lista Miðflokksins í Suðurnesjabæ","quotes":["M-listinn: Miðflokkurinn Daði Bergþórsson (Sandgerði) Sigrún Harpa Sigurjónsd. Heide (Garður) Erla Jóhannsdóttir (Garður) Sigríður Rós Jónatansdóttir (Garður) Ólafur Fannar Þórhallsson (Sandgerði) Birgitta Sædís Eymundsdóttir (Garður) Elmar Aron Gunnarsson (Sandgerði) Brynjar Þór Kristinsson (Garður)"]},
    {"n":3,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]},
    {"n":4,"status":"verified","claim":"Oddviti listans er Daði Bergþórsson","quotes":["Oddvitinn Daði Bergþórsson býr þó í Sandgerði"]},
    {"n":5,"status":"verified","claim":"Miðflokksdeild Suðurnesjabæjar var stofnuð í mars 2026","quotes":["Miðflokksdeild Suðurnesjabæjar var stofnuð 4. mars 2026 og stjórn kosin"]},
    {"n":6,"status":"flagged","claim":"flokkurinn býður nú fram í fyrsta sinn í sveitarfélaginu","notes":"Miðflokk-greinin nefnir aðeins stofnun deildar, ekki sérstaklega „í fyrsta sinn“. VF segir flokkurinn er með nýjan lista í Suðurnesjabæ — en orðalagið „í fyrsta sinn“ er ekki bein tilvitnun."}
  ],
  "summary": "5 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Brynjar Þór Kristinsson býr í Garði og skipar 8. sæti á M-lista Miðflokksins í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026. Oddviti listans er Daði Bergþórsson. Miðflokksdeild Suðurnesjabæjar var stofnuð 4. mars 2026.",
    "rewrite_words": 36,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"„Í fyrsta sinn“ — ekki bein tilvitnun"}
    ],
    "new_heimild": []
  }
})

# SNB.M.9 Gréta Ágústsdóttir
records.append({
  "id": "SNB.M.9",
  "bio": "Gréta Ágústsdóttir er búsett í Sandgerði og skipar 9. sæti á M-lista Miðflokksins í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026. Oddviti listans er Daði Bergþórsson. Miðflokksdeild Suðurnesjabæjar var stofnuð í mars 2026 og býður flokkurinn nú fram í fyrsta sinn í sveitarfélaginu.",
  "sources": [
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae",
    "https://midflokkurinn.is/midflokksdeild-sudurnesjabaejar-stofnud"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"búsett í Sandgerði","quotes":["Gréta Ágústsdóttir (Sandgerði)"]},
    {"n":2,"status":"verified","claim":"9. sæti á M-lista Miðflokksins","quotes":["Brynjar Þór Kristinsson (Garður) Gréta Ágústsdóttir (Sandgerði)"]},
    {"n":3,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]},
    {"n":4,"status":"verified","claim":"Oddviti listans er Daði Bergþórsson","quotes":["Oddvitinn Daði Bergþórsson býr þó í Sandgerði"]},
    {"n":5,"status":"verified","claim":"Miðflokksdeild Suðurnesjabæjar var stofnuð í mars 2026","quotes":["Miðflokksdeild Suðurnesjabæjar var stofnuð 4. mars 2026 og stjórn kosin"]},
    {"n":6,"status":"flagged","claim":"býður flokkurinn nú fram í fyrsta sinn í sveitarfélaginu","notes":"Sömu ástæða og hjá SNB.M.8 — ekki bein tilvitnun."}
  ],
  "summary": "5 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Gréta Ágústsdóttir er búsett í Sandgerði og skipar 9. sæti á M-lista Miðflokksins í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026. Oddviti listans er Daði Bergþórsson. Miðflokksdeild Suðurnesjabæjar var stofnuð 4. mars 2026.",
    "rewrite_words": 36,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"„Í fyrsta sinn“ — ekki bein tilvitnun"}
    ],
    "new_heimild": []
  }
})

# SNB.S.18 Jórunn Alda — leikskólastjóri (NOT verified), öldungaráð (V via mbl), Sandgerði (V)
records.append({
  "id": "SNB.S.18",
  "bio": "Jórunn Alda Guðmundsdóttir er fyrrverandi leikskólastjóri og eldri borgari, búsett í Sandgerði. Hún hefur setið í stjórn öldungaráðs Suðurnesja og tekur þátt í félagsstarfi eldri borgara í Suðurnesjabæ. Jórunn Alda skipar 18. sæti, heiðurssætið, á lista Samfylkingarinnar og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026.",
  "sources": [
    "https://xs.is/frambjodendur-sudurnesjabae",
    "https://xs.is/sveitarstjornarfolk"
  ],
  "statements": [
    {"n":1,"status":"flagged","claim":"fyrrverandi leikskólastjóri","notes":"xs.is/frambjodendur-sudurnesjabae er 404. xs.is/sveitarstjornarfolk hefur ekki Jórunn. Engin önnur staðfest heimild fyrir leikskólastjórastöðu fannst."},
    {"n":2,"status":"flagged","claim":"eldri borgari","notes":"Tilvitnun ekki í tilteknum heimildum, en má rökstyðja út frá Mbl-Tímarit-skráningu (kt. 091241 → fædd 1941)."},
    {"n":3,"status":"verified","claim":"búsett í Sandgerði","quotes":["Jórunn Alda Guðmundsdóttir, kt. 091241-2429, stjórnarmaður öldungaráðs Suðurnesja, Hlíðargötu 31, Sandgerði"]},
    {"n":4,"status":"rescued","claim":"setið í stjórn öldungaráðs Suðurnesja","quotes":["Jórunn Alda Guðmundsdóttir, kt. 091241-2429, stjórnarmaður öldungaráðs Suðurnesja","Jórunn Alda Guðmundsdóttir varafomaður FEB á Suðurnesjum"]},
    {"n":5,"status":"flagged","claim":"tekur þátt í félagsstarfi eldri borgara í Suðurnesjabæ (sjálfstæð fullyrðing)","notes":"Almenn fullyrðing — má rökstyðja út frá FEBS-veru. Drop sem of óljóst."},
    {"n":6,"status":"flagged","claim":"18. sæti, heiðurssætið, á lista Samfylkingarinnar og óháðra","notes":"Heimildirnar tvær gefa þetta ekki — frambjóðendalisti Samfylkingar í Suðurnesjabæ var 404 í cache. VF birtir aðeins efstu 9 sæti, þar er hún ekki. Engin staðfest tilvitnun fyrir 18. sæti."}
  ],
  "summary": "1 verified, 1 rescued, 4 flagged",
  "rescue": {
    "rewrite": "Jórunn Alda Guðmundsdóttir er búsett í Sandgerði og hefur setið sem stjórnarmaður í öldungaráði Suðurnesja, og hefur einnig verið varaformaður FEB á Suðurnesjum. Hún skipar sæti á S-lista Samfylkingarinnar og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026.",
    "rewrite_words": 38,
    "new_sources": [
      "https://timarit.is/page/6958687",
      "https://www.facebook.com/SudurnesOldungarad/posts/aðalfundur-öldungaráðs-suðurnesja-var-haldinn-á-nesvöllum-laugardaginn-23-septem/1639777576093501/"
    ],
    "resolutions": [
      {"kind":"dropped","text":"„Fyrrverandi leikskólastjóri“ — engin staðfesting"},
      {"kind":"dropped","text":"Sjálfstætt sætisnúmer „18.“ — heimildin xs.is/frambjodendur-sudurnesjabae er 404; ekki staðfest"}
    ],
    "new_heimild": [
      {"url":"https://timarit.is/page/6958687","label":"Morgunblaðið 18.10.2017 — Jórunn Alda stjórnarmaður öldungaráðs Suðurnesja"}
    ]
  }
})

# SNB.S.5 Thelma Dís Eggertsdóttir
records.append({
  "id": "SNB.S.5",
  "bio": "Thelma Dís Eggertsdóttir skipar 5. sæti á lista Samfylkingarinnar og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026. Hún er grunnskólakennari og starfar sem umsjónarkennari í yngri bekkjum við Sandgerðisskóla, og hefur einnig sinnt leiðbeinandastörfum í kennaranámi.",
  "sources": [
    "https://www.sandgerdisskoli.is/is/starfsfolk",
    "https://xs.is/frambjodendur-sudurnesjabae"
  ],
  "statements": [
    {"n":1,"status":"verified","claim":"5. sæti á S-lista Samfylkingarinnar og óháðra","quotes":["S-listinn: Samfylkingin og óháðir Svavar Grétarsson (Sandgerði) Bergný Jóna Sævarsdóttir (Sandgerði) Egill Rúnar Sigurðsson (Garður) Önundur S. Björnsson (Garður) Thelma Dís Eggertsdóttir (Sandgerði)"]},
    {"n":2,"status":"verified","claim":"grunnskólakennari","quotes":["Thelma Dís Eggertsdóttir Starfsheiti Umsjónarkennari 1. bekkjar"]},
    {"n":3,"status":"verified","claim":"umsjónarkennari í yngri bekkjum við Sandgerðisskóla (1. bekkur)","quotes":["Thelma Dís Eggertsdóttir Umsjónarkennari 1. bekkjar Netfang thelmadis@sandgerdisskoli"]},
    {"n":4,"status":"flagged","claim":"hefur einnig sinnt leiðbeinandastörfum í kennaranámi","notes":"Engin tilvitnun á starfsmannasíðu Sandgerðisskóla. xs.is/frambjodendur-sudurnesjabae er 404."}
  ],
  "summary": "3 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Thelma Dís Eggertsdóttir skipar 5. sæti á S-lista Samfylkingarinnar og óháðra í Suðurnesjabæ fyrir sveitarstjórnarkosningarnar 2026. Hún er grunnskólakennari og starfar sem umsjónarkennari 1. bekkjar við Sandgerðisskóla.",
    "rewrite_words": 30,
    "new_sources": ["https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae"],
    "resolutions": [
      {"kind":"dropped","text":"„Leiðbeinandastörf í kennaranámi“ — engin staðfesting"}
    ],
    "new_heimild": [
      {"url":"https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae","label":"Víkurfréttir — Hvar búa frambjóðendur í Suðurnesjabæ"}
    ]
  }
})

# SNB.S.7 Agnes Helgadóttir
records.append({
  "id": "SNB.S.7",
  "bio": "Agnes Helgadóttir er uppeldis- og menntunarfræðingur og íbúi í Sandgerði og starfar hjá Suðurnesjabæ. Hún skipar 7. sæti á S-lista Samfylkingarinnar og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
  "sources": [
    "https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae",
    "https://www.sudurnesjabaer.is/is/stjornsysla/mannaudur/starfsmenn"
  ],
  "statements": [
    {"n":1,"status":"flagged","claim":"uppeldis- og menntunarfræðingur","notes":"Starfsmannasíða Suðurnesjabæjar lýsir starfsheiti hennar „Sérfræðingur í stoðþjónustu“. Menntunarflokkun „uppeldis- og menntunarfræðingur“ er ekki á starfsmannasíðu."},
    {"n":2,"status":"verified","claim":"íbúi í Sandgerði","quotes":["Agnes Helgadóttir (Sandgerði)"]},
    {"n":3,"status":"verified","claim":"starfar hjá Suðurnesjabæ","quotes":["Agnes Helgadóttir Sérfræðingur í stoðþjónustu Mennta- og tómstundasvið"]},
    {"n":4,"status":"verified","claim":"7. sæti á S-lista Samfylkingarinnar og óháðra","quotes":["Thelma Dís Eggertsdóttir (Sandgerði) Bára Kristín Þórisdóttir (Sandgerði) Agnes Helgadóttir (Sandgerði)"]},
    {"n":5,"status":"verified","claim":"sveitarstjórnarkosningar 16. maí 2026","quotes":["Sveitarstjórnarkosningar fara fram 16.maí 2026"]}
  ],
  "summary": "4 verified, 0 rescued, 1 flagged",
  "rescue": {
    "rewrite": "Agnes Helgadóttir býr í Sandgerði og starfar sem sérfræðingur í stoðþjónustu á mennta- og tómstundasviði Suðurnesjabæjar. Hún skipar 7. sæti á S-lista Samfylkingarinnar og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.",
    "rewrite_words": 33,
    "new_sources": [],
    "resolutions": [
      {"kind":"dropped","text":"„Uppeldis- og menntunarfræðingur“ menntun — ekki staðfest"}
    ],
    "new_heimild": []
  }
})

for r in records:
    save(r)
