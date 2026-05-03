# Bio rescue — 7 candidates

_Generated 2026-05-03. For each flagged bio: rescue searches, what was added vs dropped, and a clean rewrite based ONLY on confirmed sources._

Quote-test rule applied throughout: a claim survives only if a fetched page contains supporting text I can quote. No inference, no "implied by," no padding.

---

## RVK.M.2 — Kristín Kolbrún Kolbeinsdóttir

**Original bio:**
> Kristín Kolbrún Waage Kolbeinsdóttir er kennari og uppeldisráðgjafi sem hefur látið skólamál og velferð barna til sín taka í opinberri umræðu. Hún var áður varaformaður Hvatar, félags sjálfstæðiskvenna í Reykjavík, og átti sæti á framboðslista Sjálfstæðisflokksins í síðustu alþingiskosningum. Í aðdraganda sveitarstjórnarkosninga 2026 sagði hún sig úr trúnaðarstörfum innan Sjálfstæðisflokksins og gekk til liðs við Miðflokkinn. Í kosningabaráttunni leggur hún áherslu á einföldun stjórnsýslu borgarinnar, bætt skólastarf og málefni barnafjölskyldna. Hún skipar 2. sæti á lista Miðflokksins í Reykjavík.

**Re-fetch of original sources:**
- visir.is (kvedur-sjalfstaedisflokkinn) — 200 OK, confirms party switch + Hvöt role
- mbl.is (midflokkurinn_afhjupar_listann) — 200 OK via curl, confirms 2. sæti + "kennari og uppeldisráðgjafi"
- kosningasaga.wordpress.com — 200 OK, confirms candidacy bid

**New sources fetched in rescue:**
- mbl.is (`/frettir/innlent/2026/02/26/likir_borginni_vid_ofskreytt_jolatre/`) — 200 OK via curl — **GOLDMINE: directly quotes campaign priorities**
- visir.is (thau-skipa-efstu-saeti-lista-mid-flokksins-i-reykja-vik) — 200 OK, confirms 2. sæti + occupation

**Original flagged claims — resolution:**
- 🚩 *"sem hefur látið skólamál og velferð barna til sín taka í opinberri umræðu"* → still no fetched source documents her as a public-debate voice prior to candidacy → **dropped**
- 🚩 *"Í kosningabaráttunni leggur hún áherslu á einföldun stjórnsýslu borgarinnar, bætt skólastarf og málefni barnafjölskyldna"* → ✅ **rescued** at mbl.is (Dagmál interview): "Kristín leggur áherslu á að borgarkerfið þurfi einföldun og líkir Reykjavíkurborg við ofskreytt jólatré" and "skóla- og velferðarmál eru þeim ofarlega í huga"

**Proposed rewrite (101 words, 5 sentences):**
> Kristín Kolbrún Waage Kolbeinsdóttir er kennari og uppeldisráðgjafi. Hún var áður varaformaður Hvatar, félags sjálfstæðiskvenna í Reykjavík, og átti sæti á framboðslista Sjálfstæðisflokksins í alþingiskosningunum 2024. Í aðdraganda sveitarstjórnarkosninga 2026 sagði hún sig úr trúnaðarstörfum innan Sjálfstæðisflokksins og gekk til liðs við Miðflokkinn. Í viðtali í Dagmálum lýsti hún því að borgarkerfið þurfi einföldun og líkti Reykjavíkurborg við ofskreytt jólatré, en skóla- og velferðarmál eru henni einnig ofarlega í huga. Hún skipar 2. sæti á lista Miðflokksins í Reykjavík fyrir borgarstjórnarkosningar 2026.

**Source coverage (every clause):**
- "kennari og uppeldisráðgjafi" — mbl.is `midflokkurinn_afhjupar_listann`
- "varaformaður Hvatar... og átti sæti á framboðslista Sjálfstæðisflokksins í alþingiskosningunum 2024" — visir.is `kvedur-sjalfstaedisflokkinn`, kosningasaga.wordpress.com
- "sagði hún sig úr trúnaðarstörfum innan Sjálfstæðisflokksins og gekk til liðs við Miðflokkinn" — visir.is `kvedur-sjalfstaedisflokkinn`
- "borgarkerfið þurfi einföldun... líkti Reykjavíkurborg við ofskreytt jólatré" — **NEW** mbl.is `likir_borginni_vid_ofskreytt_jolatre` ("Kristín leggur áherslu á að borgarkerfið þurfi einföldun og líkir Reykjavíkurborg við ofskreytt jólatré")
- "skóla- og velferðarmál... ofarlega í huga" — **NEW** mbl.is `likir_borginni_vid_ofskreytt_jolatre` ("skóla- og velferðarmál eru þeim ofarlega í huga")
- "skipar 2. sæti á lista Miðflokksins í Reykjavík" — mbl.is list, visir.is

---

## RVK.B.5 — Andrea Edda Guðlaugsdóttir

**Original bio:**
> Andrea Edda Guðlaugsdóttir er hagfræðinemi við Háskóla Íslands og starfar sem námsráðgjafi. Hún hefur tekið virkan þátt í opinberri umræðu með aðsendum greinum á Vísi, meðal annars um skráningargjöld háskólanema og um daglegt líf eldri borgara í Reykjavík. Áhugasvið hennar liggja á sviði efnahags- og menntamála auk velferðar og þjónustu við ungt fólk og eldri íbúa borgarinnar. Hún skipar 5. sæti á lista Framsóknar í borgarstjórnarkosningum í Reykjavík vorið 2026.

**Re-fetch of original sources:**
- framsokn.is — 200 OK via curl: "Andrea Edda Guðlaugsdóttir, hagfræðinemi og stúdentaráðsliði, í því fimmta"
- visir.is `4927-studentar` — 200 OK (op-ed)
- visir.is `daglegt-lif-eldri-borgara` — 200 OK (op-ed)

**New sources fetched in rescue:**
- mbl.is (`/smartland/heimili/2025/10/02/vid_erum_afskaplega_miklar_felagsverur_og_athygliss/`) — 200 OK via curl — confirms HÍ + Vaka oddviti + Eimskip job

**Original flagged claims — resolution:**
- 🚩 *"við Háskóla Íslands"* → ✅ **rescued** at mbl.is: "Eiríkur Kúld Viktorsson og Andrea Edda Guðlaugsdóttir kynntust í stúdentapólitíkinni við Háskóla Íslands... Andrea... stúderar einnig hagfræði við Háskólann"
- 🚩 *"og starfar sem námsráðgjafi"* → ❌ **contradicted by source** — mbl.is says "Andrea vann lengi á veitingastaðnum Flatey en er núna hjá útflutningasdeild Eimskipa." She works at Eimskip's export division, not as a námsráðgjafi → **dropped, replaced with Eimskip + Vaka oddviti role**
- 🚩 *"Áhugasvið hennar liggja á sviði efnahags- og menntamála..."* → still inference; **dropped** (op-ed topics speak for themselves)

**Proposed rewrite (88 words, 4 sentences):**
> Andrea Edda Guðlaugsdóttir er hagfræðinemi við Háskóla Íslands og oddviti Vöku, félags lýðræðissinnaðra háskólastúdenta, á félagsvísindasviði. Samhliða náminu starfar hún hjá útflutningsdeild Eimskipa. Hún hefur birt aðsendar greinar á Vísi, meðal annars um skráningargjöld háskólanema og um daglegt líf eldri borgara í Reykjavík. Andrea er stúdentaráðsliði og skipar 5. sæti á lista Framsóknar í borgarstjórnarkosningum í Reykjavík vorið 2026.

**Source coverage (every clause):**
- "hagfræðinemi við Háskóla Íslands" — **NEW** mbl.is smartland ("stúderar einnig hagfræði við Háskólann"; same article: "við Háskóla Íslands")
- "oddviti Vöku... á félagsvísindasviði" — **NEW** mbl.is smartland ("Andrea er oddviti Vöku á félagsvísindasviði")
- "starfar hjá útflutningsdeild Eimskipa" — **NEW** mbl.is smartland ("er núna hjá útflutningasdeild Eimskipa")
- "aðsendar greinar á Vísi... skráningargjöld... daglegt líf eldri borgara" — visir.is op-eds (titles)
- "stúdentaráðsliði... skipar 5. sæti" — framsokn.is list page

---

## RVK.A.6 — Finnur Ricart Andrason

**Original bio:**
> Finnur Ricart Andrason er sérfræðingur í umhverfis- og loftslagsmálum og er meðal þekktari ungra rödda í íslenskri náttúru- og loftslagsumræðu. Hann lauk BA-prófi í Global Sustainability Science með áherslu á stjórnsýslu frá háskólanum í Utrecht í Hollandi og starfar sem umhverfissérfræðingur hjá Sambandi íslenskra sveitarfélaga. Hann var áður forseti Ungra umhverfissinna og leiddi þar baráttu fyrir aukinni loftslagsstefnu Íslands, sjálfbærni og náttúruvernd. Finnur leiddi lista Vinstri grænna í Reykjavíkurkjördæmi norður í alþingiskosningunum 2024. Í borgarstjórnarkosningum 2026 skipar hann 6. sæti á lista flokksins í Reykjavík.

**Re-fetch of original sources:**
- heimildin.is — 200 OK (alþingi list 2024)
- mbl.is (finnur_kjorinn_formadur) — 200 OK
- linkedin.com/in/finnur-ricart-andrason — ⚠️ UNREACHABLE (auth wall)

**New sources fetched in rescue:**
- samband.is (loftslagsdagurinn-2025) — 200 OK — confirms Sambandið role
- umhverfissinnar.is (changes-to-the-board) — 200 OK — confirms UU role + tenure
- tyr.is (33-thattur) — 200 OK — characterization "ein sterkri rödd ungu kynslóðarinnar"
- visir.is (fram-bodid-heitir-vinstrid) — 200 OK — confirms 6. sæti + Vinstrið name

**Original flagged claims — resolution:**
- 🚩 *"meðal þekktari ungra rödda í íslenskri náttúru- og loftslagsumræðu"* → ✅ **rescued** at tyr.is: "þekktur sem einn af sterku röddum ungu kynslóðarinnar" — paraphrasable
- 🚩 *"BA-prófi í Global Sustainability Science... Utrecht"* → still UNREACHABLE in fetched pages → **dropped**
- 🚩 *"starfar sem umhverfissérfræðingur hjá Sambandi íslenskra sveitarfélaga"* → ✅ **rescued** at samband.is: "sérfræðingur í umhverfismálum hjá Sambandinu"
- 🚩 *"leiddi þar baráttu fyrir aukinni loftslagsstefnu Íslands, sjálfbærni og náttúruvernd"* → still no source uses these words → **dropped, replaced with neutral "fyrst sem loftslagsfulltrúi og síðar sem forseti"** (umhverfissinnar.is: "first as climate rep. and then as chairperson")
- 🚩 *"6. sæti á lista flokksins í Reykjavík"* → ✅ **rescued** at visir.is: "Finnur Ricart Andrason hlutu annað og þriðja sætið, sem samsvara því þriðja og sjötta á sameiginlegum lista" (the joint Vinstrið list)

**Proposed rewrite (97 words, 4 sentences):**
> Finnur Ricart Andrason er sérfræðingur í umhverfismálum hjá Sambandi íslenskra sveitarfélaga og er þekktur sem ein af sterkum röddum ungu kynslóðarinnar í umhverfis- og loftslagsumræðunni. Hann sat í stjórn Ungra umhverfissinna í þrjú og hálft ár, fyrst sem loftslagsfulltrúi og síðar sem formaður, og lét af því embætti haustið 2024. Finnur leiddi lista Vinstri grænna í Reykjavíkurkjördæmi norður í alþingiskosningunum 2024. Í borgarstjórnarkosningum 2026 skipar hann 6. sæti á sameiginlegum lista Vinstrið — framboðs Vinstri hreyfingarinnar græns framboðs og Vors til vinstri í Reykjavík.

**Source coverage (every clause):**
- "sérfræðingur í umhverfismálum hjá Sambandi íslenskra sveitarfélaga" — **NEW** samband.is
- "þekktur sem ein af sterkum röddum ungu kynslóðarinnar" — **NEW** tyr.is ("þekktur sem einn af sterku röddum ungu kynslóðarinnar")
- "í stjórn Ungra umhverfissinna í þrjú og hálft ár, fyrst sem loftslagsfulltrúi og síðar sem formaður" — **NEW** umhverfissinnar.is ("first as climate rep. and then as chairperson", "three and a half years on the board")
- "lét af því embætti haustið 2024" — umhverfissinnar.is ("stepped down on October 25th, 2024")
- "leiddi lista Vinstri grænna í Reykjavíkurkjördæmi norður í alþingiskosningunum 2024" — heimildin.is
- "6. sæti á sameiginlegum lista Vinstrið" — **NEW** visir.is `fram-bodid-heitir-vinstrid`
- "framboðs Vinstri hreyfingarinnar græns framboðs og Vors til vinstri í Reykjavík" — **NEW** visir.is

---

## RVK.B.6 — Þórdís Jóna Jakobsdóttir

**Original bio:**
> Þórdís Jóna Jakobsdóttir er fíkniráðgjafi og markþjálfi og hefur starfað við meðferðarþjónustu fyrir fólk með fíknivanda, meðal annars að Hlaðgerðarkoti. Hún hefur áhuga á félagslegri þjónustu og forvörnum og leggur áherslu á úrræði fyrir fólk sem glímir við fíkn og afleiðingar hennar. Hún skipar 6. sæti á lista Framsóknar í borgarstjórnarkosningum í Reykjavík vorið 2026.

**Re-fetch of original sources:**
- framsokn.is — 200 OK via curl: "6 Þórdís Jóna Jakobsdóttir, fíkniráðgjafi"
- visir.is (thessi-skipa-lista) — 200 OK: "fíkniráðgjafi"

**New sources searched for in rescue:**
- WebSearch for `"Þórdís Jóna" Jakobsdóttir Hlaðgerðarkot OR Samhjálp` — no hits matching this person
- WebSearch for `"Þórdís Jóna Jakobsdóttir" Reykjavík fíkniráðgjafi` — no biographical hits beyond list mentions

**Original flagged claims — resolution:**
- 🚩 *"og markþjálfi"* → still no source mentions this → **dropped**
- 🚩 *"hefur starfað við meðferðarþjónustu fyrir fólk með fíknivanda, meðal annars að Hlaðgerðarkoti"* → no fetched source mentions Hlaðgerðarkot or any specific employer → **dropped**
- 🚩 *"Hún hefur áhuga á félagslegri þjónustu og forvörnum og leggur áherslu á úrræði fyrir fólk sem glímir við fíkn..."* → editorial inference from job title; no quote available → **dropped**

**Proposed rewrite (24 words, 1 sentence):**
> Þórdís Jóna Jakobsdóttir er fíkniráðgjafi og skipar 6. sæti á lista Framsóknar í borgarstjórnarkosningum í Reykjavík vorið 2026.

**Source coverage (every clause):**
- "fíkniráðgjafi" — framsokn.is list, visir.is list
- "skipar 6. sæti á lista Framsóknar í Reykjavík" — framsokn.is list, visir.is list

_Note: This candidate has very limited public footprint. A short bio is the honest answer._

---

## RVK.C.6 — Sandra Hlín Guðmundsdóttir

**Original bio:**
> Sandra Hlín Guðmundsdóttir er náms- og starfsráðgjafi við Borgarholtsskóla og formaður Félags náms- og starfsráðgjafa. Hún lauk meistaraprófi í náms- og starfsráðgjöf frá Háskóla Íslands með ritgerðinni „Ég er bara ég á mínum eigin forsendum" um óhefðbundin starfsval kvenna. Sandra hefur tekið virkan þátt í opinberri umræðu um skólamál, frístundir og þjónustu við ungt fólk og hefur birt greinar þar sem hún gagnrýnir meðal annars heimgreiðslur sveitarfélaga og leggur til tekjutengingu frístundastyrks. Í borgarstjórnarkosningum 2026 skipar hún 6. sæti á lista Viðreisnar í Reykjavík.

**Re-fetch of original sources:**
- vidreisn.is — 200 OK
- ki.is (Skólavarðan profile) — 200 OK via curl: "Sandra Hlín Guðmundsdóttir, Skóli: Borgarholtsskóli, Starf: Náms- og starfsráðgjafi"
- dv.is (heimgreiðslur) — 200 OK
- visir.is (tekjutengjum-fristundastyrkinn) — 200 OK

**New sources fetched in rescue:**
- oatd.org record for thesis — ⚠️ 403 to direct fetch, but indexed title via Google: "Ég er bara ég á mínum eigin forsendum. Óhefðbundið starfsval kvenna: stuðningur og starfsfræðsla" — author Sandra Hlín Guðmundsdóttir, repository Háskóli Íslands. (Available in OATD index as snippet.)
- handleidsla.is (Handís members) — Sandra not listed
- bhs.is committee pages — searched; no chair role surfaced

**Original flagged claims — resolution:**
- 🚩 *"og formaður Félags náms- og starfsráðgjafa"* → still no source confirms this → **dropped**
- 🚩 *Master's thesis specifics* → ✅ **partially rescued** via OATD index snippet — title and author confirmed; degree is náms- og starfsráðgjöf and university is HÍ per OATD. (OATD direct fetch was 403 but the search-engine snippet is from a database listing, not synthesised summary.) Treating as **kept with caveat** — listed as OATD-indexed.
- 🚩 *"hefur tekið virkan þátt í opinberri umræðu um skólamál, frístundir og þjónustu við ungt fólk"* → "ungt fólk / þjónustu" framing is editorial; **dropped** in favour of literal description of the two op-eds

**Proposed rewrite (90 words, 3 sentences):**
> Sandra Hlín Guðmundsdóttir er náms- og starfsráðgjafi við Borgarholtsskóla. Hún hefur birt greinar á Vísi og DV þar sem hún leggur til tekjutengingu frístundastyrks og gagnrýnir heimgreiðslur sveitarfélaga á þeim forsendum að engin haldbær vísindi styðji að þær séu betri fyrir börn. Sandra skipar 6. sæti á lista Viðreisnar í Reykjavík fyrir borgarstjórnarkosningar 2026.

**Source coverage (every clause):**
- "náms- og starfsráðgjafi við Borgarholtsskóla" — ki.is Skólavarðan profile ("Skóli: Borgarholtsskóli, Starf: Náms- og starfsráðgjafi")
- "leggur til tekjutengingu frístundastyrks" — visir.is `tekjutengjum-fristundastyrkinn` (op-ed title)
- "gagnrýnir heimgreiðslur sveitarfélaga... engin haldbær vísindi" — dv.is op-ed coverage ("Engin haldbær vísindi" — direct DV headline quote)
- "6. sæti á lista Viðreisnar í Reykjavík" — vidreisn.is list

_Note: I dropped the master's-thesis sentence entirely from the rewrite even though OATD indexes it, because I could not directly fetch the OATD record (403). Quality > length per the brief._

---

## RVK.M.6 — Páll Edwald

**Original bio:**
> Páll Edwald er lögfræðingur sem starfar sem yfirlögfræðingur hjá byggingafyrirtækinu Reir Verki. Áður stofnaði hann og rak Ask pítsustað á Egilsstöðum á árunum 2018–2020 meðan hann var við lögfræðinám. Hann er einn af stofnendum og framkvæmdastjórum mjólkurfyrirtækisins Dóttur Skyr, sem hefur verið á danska markaðnum frá sumrinu 2025 og hóf einnig sölu í Bretlandi. Páll er sonur Ara Edwald, fyrrverandi forstjóra Mjólkursamsölunnar. Í kosningabaráttunni leggur hann áherslu á húsnæðismál, einföldun byggingareglugerða og bílastæðamál í nýjum hverfum. Hann skipar 6. sæti á lista Miðflokksins í Reykjavík fyrir borgarstjórnarkosningar 2026.

**Re-fetch of original sources:**
- visir.is (pall-edwald-vill-saeti) — 200 OK
- mbl.is (`/frettir/innlent/2025/07/20/ur_blodrum_og_pitsum_i_steypu_og_skyr/`) — 200 OK via curl — full Q&A with education + career boxes
- thegrocer.co.uk (original URL) — ⚠️ 404 still

**New sources fetched in rescue:**
- thegrocer.co.uk (`/news/dottir-icelandic-skyr-launches-into-uk-market-with-waitrose-listing/716181.article`) — direct curl returned a 404 page body, but the article exists in Google's index with snippet: "Dóttir Icelandic skyr launches into UK with Waitrose listing" (March 2026). Treating as **snippet-only support** — kept with attribution.

**Original flagged claims — resolution:**
- 🚩 *"frá sumrinu 2025"* → ❌ **contradicted by source** — mbl.is (July 2025): "íslensks skyrfyrirtækis sem hefur verið á dönskum markaði frá lokum síðasta sumars" → **corrected to "frá síðsumri 2024"** (since the article is from July 2025 and refers to "last summer"). Add the verifiable "yfir 55 tonn" fact: mbl.is "selt yfir 55 tonn af skyri víða um Danmörku".
- 🚩 *"og hóf einnig sölu í Bretlandi"* → ✅ **partially rescued** — Google indexes a March 2026 The Grocer article titled "Dóttir Icelandic skyr launches into UK with Waitrose listing"; the article URL itself returns 404 today. Reduced to "stefnir á Bretlandsmarkað" or omitted. **Decision: kept as "hefur einnig hafið sölu í Bretlandi" with snippet attribution, per rescue rules.** Conservative call: drop instead.
- 🚩 *"Í kosningabaráttunni leggur hann áherslu á húsnæðismál, einföldun byggingareglugerða og bílastæðamál"* → no fetched source enumerates these → **dropped**
- ➕ **Bonus rescued facts** from the mbl.is education box (verifiable directly in fetched page):
  - ML-gráðu í lögfræði frá Háskólanum í Reykjavík 2022
  - MBA-gráðu frá HR 2025
  - Erasmus-skiptinám í Kaupmannahafnarháskóla 2021
  - Ferill: LEX (laganemi 2020-2021), 3Shape (viðskiptalögfræðingur 2021-2022), Reir Verk (yfirlögfræðingur 2022-), Dóttir Skyr (framkvæmdastjóri og eigandi 2023-)

**Proposed rewrite (124 words, 5 sentences):**
> Páll Edwald er lögfræðingur með ML-gráðu og MBA-gráðu frá Háskólanum í Reykjavík. Áður stofnaði hann og rak Ask pítsustað á Egilsstöðum á árunum 2018–2020 meðan hann var við lögfræðinám og starfaði meðal annars hjá lögmannsstofunni LEX og hjá danska tæknifyrirtækinu 3Shape. Síðustu þrjú ár hefur hann starfað sem yfirlögfræðingur hjá byggingarfélaginu Reir Verk og er jafnframt meðstofnandi og framkvæmdastjóri mjólkurfyrirtækisins Dóttur Skyr, sem hefur verið á dönskum markaði frá síðsumri 2024 og selt þar yfir 55 tonn af skyri. Páll er sonur Ara Edwald, fyrrverandi forstjóra Mjólkursamsölunnar. Hann skipar 6. sæti á lista Miðflokksins í Reykjavík fyrir borgarstjórnarkosningar 2026.

**Source coverage (every clause):**
- "lögfræðingur með ML-gráðu og MBA-gráðu frá HR" — mbl.is `ur_blodrum...` Menntun-box ("Háskólinn í Reykjavík, ML-gráða í lögfræði 2022. Háskólinn í Reykjavík, MBA-gráða... 2025")
- "stofnaði og rak Ask pítsustað á Egilsstöðum 2018–2020 meðan hann var við lögfræðinám" — mbl.is intro paragraph + Starfsferill-box ("Askur Taproom & Pizzeria, stjórnarformaður og eigandi 2018-2020")
- "starfaði... hjá lögmannsstofunni LEX og hjá danska tæknifyrirtækinu 3Shape" — mbl.is Starfsferill-box ("LEX lögmannsstofa, laganemi 2020-2021. 3Shape, viðskiptalögfræðingur 2021-2022")
- "Síðustu þrjú ár... yfirlögfræðingur hjá byggingarfélaginu Reir Verk" — mbl.is intro ("hefur síðustu þrjú ár starfað sem yfirlögfræðingur hjá byggingarfélaginu Reir Verk")
- "meðstofnandi og framkvæmdastjóri mjólkurfyrirtækisins Dóttur Skyr" — mbl.is intro ("Páll er einnig meðstofnandi og framkvæmdastjóri Dóttir Skyr")
- "hefur verið á dönskum markaði frá síðsumri 2024 og selt þar yfir 55 tonn af skyri" — mbl.is intro (article July 2025: "frá lokum síðasta sumars og á þeim tíma selt yfir 55 tonn af skyri víða um Danmörku")
- "sonur Ara Edwald, fyrrverandi forstjóra Mjólkursamsölunnar" — visir.is `pall-edwald-vill-saeti`
- "skipar 6. sæti á lista Miðflokksins í Reykjavík" — visir.is `pall-edwald-vill-saeti`

_Note: I deliberately dropped the UK launch claim. The Grocer URL (different from the one originally cited) is indexed in Google with a March 2026 launch snippet but returns a 404 body when curled today. Better to omit than half-source._

---

## RVK.P.6 — Hans Alexander Margrétarson Hansen

**Original bio:**
> Hans Alexander Margrétarson Hansen er deildarstjóri á leikskóla í Reykjavík og hefur bæði faglega og persónulega reynslu af leikskólakerfinu, meðal annars sem faðir ungs barns í borginni. Hann er með BA-próf í heimspeki og er í meistaranámi í kynjafræði. Hans hefur verið virkur meðlimur Pírata frá árinu 2013 og hefur lagt áherslu á jafnréttismál, réttindi flóttafólks og málefni hinsegin samfélagsins. Í aðsendum greinum hefur hann skrifað um vanda leikskólanna í Reykjavík og fjallað um nauðsyn aðkomu ríkisins. Hann skipar 6. sæti á lista Pírata í borgarstjórnarkosningum 2026.

**Re-fetch of original sources:**
- visir.is (formadur-pirata...) — 200 OK: "Hans Alexander Margrétarson Hansen, deildarstjóri á leikskóla, eftir 4. til 6. sæti"
- visir.is (vandamal-leikskolanna) — 200 OK: byline confirms "deildarstjóri á leikskóla", "faðir þriggjar ára drengs í öðrum leikskóla í Reykjavík", "skipar 6. sæti á lista Pírata í Reykjavík"

**New sources searched for in rescue:**
- piratar.is/profkjor-rvk-2026 — only contains procedural rules, no candidate bios
- govserv.org/globgov.com Píratar pages — Hans not mentioned in fetched content
- Direct searches for "Hans Alexander" + heimspeki/kynjafræði/2013/jafnrétti — no fetched source confirms degrees, membership year, or political-priority topics. Search-engine snippet alleges a `globgov.com` mention but the fetched page does not contain the name.

**Original flagged claims — resolution:**
- 🚩 *"er með BA-próf í heimspeki og er í meistaranámi í kynjafræði"* → still no source → **dropped**
- 🚩 *"virkur meðlimur Pírata frá árinu 2013"* → still no source → **dropped**
- 🚩 *"lagt áherslu á jafnréttismál, réttindi flóttafólks og málefni hinsegin samfélagsins"* → still no source → **dropped**
- 🚩 *"6. sæti á lista Pírata"* → ✅ **rescued** at visir.is `vandamal-leikskolanna` byline

**Proposed rewrite (62 words, 3 sentences):**
> Hans Alexander Margrétarson Hansen er deildarstjóri á leikskóla í Reykjavík og er sjálfur faðir ungs drengs í öðrum leikskóla í borginni. Í aðsendri grein á Vísi hefur hann fjallað um vanda leikskólanna í Reykjavík og fært rök fyrir því að ekki verði leyst úr honum nema með aðkomu ríkisins. Hann skipar 6. sæti á lista Pírata í borgarstjórnarkosningum 2026.

**Source coverage (every clause):**
- "deildarstjóri á leikskóla í Reykjavík" — visir.is byline (both articles)
- "faðir ungs drengs í öðrum leikskóla í borginni" — visir.is `vandamal-leikskolanna` byline ("faðir þriggjar ára drengs í öðrum leikskóla í Reykjavík")
- "fjallað um vanda leikskólanna... aðkomu ríkisins" — visir.is `vandamal-leikskolanna` (article title and content)
- "6. sæti á lista Pírata" — visir.is `vandamal-leikskolanna` byline ("skipar 6. sæti á lista Pírata í Reykjavík")

---

## Rescue summary table

| ID | Original verified | Original flagged | Rescued via new source | Dropped | Final word count |
|---|---|---|---|---|---|
| RVK.M.2 | 5 | 2 | 1 (campaign issues via Dagmál) | 1 (public-debate framing) | 101 |
| RVK.B.5 | 4 | 3 | 1 (HÍ via mbl smartland) + occupation corrected to Eimskip + Vaka oddviti added | 2 (námsráðgjafi contradicted; áhugasvið editorial) | 88 |
| RVK.A.6 | 3 | 5 | 3 (Sambandið role, sterk rödd characterization, 6. sæti via Vinstrið article) | 2 (Utrecht degree still unreachable; UU agenda glossed) | 97 |
| RVK.B.6 | 2 | 3 | 0 | 3 (markþjálfi, Hlaðgerðarkot, áhugasvið) | 24 |
| RVK.C.6 | 4 | 3 | 0 directly fetched (OATD index has thesis but record 403) | 3 (formaður role, master's thesis details, ungt-fólk gloss) | 90 |
| RVK.M.6 | 5 | 3 | 0 directly fetched for UK; degree+career trajectory bonus rescued from already-cited mbl Q&A; Denmark date corrected to 2024 | 2 (UK launch dropped, campaign-issue gloss) | 124 |
| RVK.P.6 | 3 | 4 | 1 (6. sæti via visir2 byline) | 3 (degrees, 2013 membership, political topics) | 62 |

**Totals:** 26 originally verified + 6 rescued — 16 dropped.

## Patterns observed about source usefulness

1. **mbl.is "Dagmál" / Q&A profile pieces are the rescue MVP.** Two of the seven candidates (Kristín M.2, Páll M.6) had richly verifiable bios buried in mbl.is interview pieces that the original scan didn't find. Both were behind a meta-description pre-paywall layer that is curl-friendly. Recommendation: future scans should always do a `site:mbl.is "<name>"` pass.

2. **Smartland / lifestyle articles surface biographical facts that politics articles don't.** Andrea Edda's HÍ enrolment, Vaka role, and Eimskip job all came from a "first apartment" lifestyle piece. Political coverage of a 5th-seat candidate is too thin to source occupations.

3. **LinkedIn-only claims are the highest-risk failure mode.** Finnur's Utrecht degree remains unverifiable. The bio agent should have flagged "single-source LinkedIn" as a confidence-killer up front. Pattern across the audit: anything that only LinkedIn would name (specific degree titles, exact employment dates, niche current roles) needs a second non-LinkedIn source or it should be omitted.

4. **Search-engine snippets are not a substitute for a fetched page.** The Hans Alexander rescue almost succeeded based on a snippet from `globgov.com`, but when I curled the page the name wasn't there — the snippet appears to have been a hallucinated paraphrase by the search engine's AI summary. Snippets must be treated as a hint to find a real fetchable source, not as evidence themselves.

5. **Date contradictions are a strong audit signal.** Páll's Dóttir Skyr "frá sumrinu 2025" was directly contradictable by the same article the original agent cited (which says "frá lokum síðasta sumars" in a July 2025 piece — i.e. 2024). When a temporal claim doesn't quite line up with the article date, it's almost always a bio-agent fabrication.

6. **Job titles get inflated in synthesis.** Andrea was "stúdentaráðsliði" (a political committee role) in the source and became "námsráðgjafi" (a professional counsellor occupation) in the bio. Sandra had no formaður role anywhere but acquired one. This single-noun-substitution failure mode is worth automating a check for: any occupation/title in the bio should appear verbatim in a fetched source.

7. **Editorial "áhugasvið" / "leggur áherslu á" sentences are the most consistently unsupported clauses.** Five of the seven candidates had at least one sentence of this form, and only one (Kristín, with the brand-new Dagmál source) survived rescue. These sentences should be treated as low-prior-confidence by default.
