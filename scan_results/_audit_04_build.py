# -*- coding: utf-8 -*-
import json
import sys
from pathlib import Path

OUT = Path(r"F:\Claude Projects\iceland-elections\scan_results\audit_results_04.json")

results = []

# ---------- BBD.D.16 ----------
results.append({
    "id": "BBD.D.16",
    "bio": "Jónína Erna Arnarsdóttir skipar 16. sæti á lista Sjálfstæðisflokksins í Borgarbyggð og Skorradalshreppi fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listinn var samþykktur 8. apríl 2026 og er Sigurður Guðmundsson, fjármálastjóri og bæjarfulltrúi, oddviti hans. Sjálfstæðisflokkurinn býður fram sameiginlegan lista í nýju sameinuðu sveitarfélagi Borgarbyggðar og Skorradalshrepps.",
    "sources": ["https://xd.is/2026/04/08/frambodslisti-sjalfstaedisflokksins-i-borgarbyggd-samthykktur/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "Jónína Erna Arnarsdóttir skipar 16. sæti á lista Sjálfstæðisflokksins í Borgarbyggð og Skorradalshreppi", "quotes": ["sæti – Jónína Erna Arnarsdóttir", "Framboðslisti Sjálfstæðisflokksins í sveitarfélaginu Borgarbyggð og Skorradalshrepp fyrir sveitarstjórnarkosningarnar 2026 var samþykktur"]},
        {"n": 2, "status": "flagged", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "notes": "Source says 'sveitarstjórnarkosningarnar 2026' without 16. maí date."},
        {"n": 3, "status": "flagged", "claim": "Listinn var samþykktur 8. apríl 2026", "notes": "Source dated 8. apríl 2026 says 'samþykktur á fundi í gær' i.e. 7. apríl 2026."},
        {"n": 4, "status": "flagged", "claim": "Sigurður Guðmundsson, fjármálastjóri og bæjarfulltrúi, oddviti hans", "notes": "Source says 'fjármálastjóri og sveitarstjórnarfulltrúi', not bæjarfulltrúi."},
        {"n": 5, "status": "verified", "claim": "Sjálfstæðisflokkurinn býður fram sameiginlegan lista í Borgarbyggð og Skorradalshreppi", "quotes": ["Framboðslisti Sjálfstæðisflokksins í sveitarfélaginu Borgarbyggð og Skorradalshrepp"]},
    ],
    "summary": "2 verified, 3 flagged",
    "rescue": {
        "rewrite": "Jónína Erna Arnarsdóttir skipar 16. sæti á sameiginlegum lista Sjálfstæðisflokksins í Borgarbyggð og Skorradalshreppi fyrir sveitarstjórnarkosningarnar 2026. Framboðslistinn var samþykktur á fundi 7. apríl 2026 og kynntur daginn eftir. Oddviti listans er Sigurður Guðmundsson, fjármálastjóri og sveitarstjórnarfulltrúi.",
        "rewrite_words": 49,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "Specific 16. maí date dropped, kept generic 2026."},
            {"kind": "contradicted", "text": "Samþykktardagsetningu leiðrétt í 7. apríl (article says samþykkt 'í gær' og dagsett 8. apríl)."},
            {"kind": "contradicted", "text": "'bæjarfulltrúi' leiðrétt í 'sveitarstjórnarfulltrúi'."}
        ],
        "new_heimild": [{"url": "https://xd.is/2026/04/08/frambodslisti-sjalfstaedisflokksins-i-borgarbyggd-samthykktur/", "label": "Sjálfstæðisflokkurinn — Framboðslisti í Borgarbyggð og Skorradalshreppi (2026-04-08)"}]
    }
})

# ---------- BBD.M.8 ----------
results.append({
    "id": "BBD.M.8",
    "bio": "Sigurjón Helgason er bóndi í Borgarbyggð og skipar 8. sæti á lista Miðflokksins í Borgarbyggð og Skorradalshreppi við sveitarstjórnarkosningarnar 2026. Listinn var kynntur í apríl 2026.",
    "sources": ["https://skessuhorn.is/2026/04/11/midflokkurinn-kynnti-frambodslista-sinn-i-borgarbyggd"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "Sigurjón Helgason er bóndi", "quotes": ["Nr. 8 Sigurjón Helgason, bóndi"]},
        {"n": 2, "status": "verified", "claim": "skipar 8. sæti á lista Miðflokksins", "quotes": ["Nr. 8 Sigurjón Helgason, bóndi", "listi Miðflokksins í Borgarbyggð kynntur"]},
        {"n": 3, "status": "flagged", "claim": "í Borgarbyggð og Skorradalshreppi", "notes": "Source headline says 'í Borgarbyggð' only; does not mention Skorradalshreppi."},
        {"n": 4, "status": "verified", "claim": "Listinn var kynntur í apríl 2026", "quotes": ["11.04.2026", "Í gærkvöldi var listi Miðflokksins í Borgarbyggð kynntur á Hótel Vesturlandi"]}
    ],
    "summary": "3 verified, 1 flagged",
    "rescue": {
        "rewrite": "Sigurjón Helgason er bóndi og skipar 8. sæti á lista Miðflokksins í Borgarbyggð fyrir sveitarstjórnarkosningarnar 2026. Listinn var kynntur á Hótel Vesturlandi í apríl 2026 og er undir forystu Hauks Þórs Haukssonar rekstrarhagfræðings.",
        "rewrite_words": 38,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'og Skorradalshreppi' fjarlægt; heimild nefnir aðeins Borgarbyggð."}
        ],
        "new_heimild": [{"url": "https://skessuhorn.is/2026/04/11/midflokkurinn-kynnti-frambodslista-sinn-i-borgarbyggd", "label": "Skessuhorn — Miðflokkurinn kynnti framboðslista sinn í Borgarbyggð (2026-04-11)"}]
    }
})

# ---------- BBD.M.9 ----------
results.append({
    "id": "BBD.M.9",
    "bio": "Einar Ólafsson starfar sem vélaverktaki, smiður og refaskytta í Borgarbyggð. Hann skipar 9. sæti á lista Miðflokksins í Borgarbyggð og Skorradalshreppi við sveitarstjórnarkosningarnar 2026, en framboðslistinn var kynntur í Skessuhorni í apríl 2026.",
    "sources": ["https://skessuhorn.is/2026/04/11/midflokkurinn-kynnti-frambodslista-sinn-i-borgarbyggd"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "Einar Ólafsson starfar sem vélaverktaki, smiður og refaskytta", "quotes": ["Nr. 9 Einar Ólafsson, vélaverktaki, smiður og refaskytta"]},
        {"n": 2, "status": "verified", "claim": "skipar 9. sæti á lista Miðflokksins", "quotes": ["Nr. 9 Einar Ólafsson"]},
        {"n": 3, "status": "flagged", "claim": "í Borgarbyggð og Skorradalshreppi", "notes": "Source says only 'Borgarbyggð'."},
        {"n": 4, "status": "verified", "claim": "framboðslistinn var kynntur í Skessuhorni í apríl 2026", "quotes": ["11.04.2026", "Miðflokkurinn kynnti framboðslista sinn í Borgarbyggð"]}
    ],
    "summary": "3 verified, 1 flagged",
    "rescue": {
        "rewrite": "Einar Ólafsson er vélaverktaki, smiður og refaskytta og skipar 9. sæti á lista Miðflokksins í Borgarbyggð fyrir sveitarstjórnarkosningarnar 2026. Framboðslistinn var kynntur á Hótel Vesturlandi og birtur í Skessuhorni í apríl 2026.",
        "rewrite_words": 38,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'og Skorradalshreppi' fjarlægt; heimild styður aðeins Borgarbyggð."}
        ],
        "new_heimild": [{"url": "https://skessuhorn.is/2026/04/11/midflokkurinn-kynnti-frambodslista-sinn-i-borgarbyggd", "label": "Skessuhorn — Miðflokkurinn kynnti framboðslista sinn í Borgarbyggð (2026-04-11)"}]
    }
})

# ---------- FJD.D.6 ----------
results.append({
    "id": "FJD.D.6",
    "bio": "Friðrik Júlíus Jósefsson er byggingaiðnfræðingur að mennt og skipar 6. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð fyrir sveitarstjórnarkosningarnar 2026. Listinn var samþykktur í febrúar 2026 og er leiddur af Ragnari Sigurðssyni framkvæmdastjóra.",
    "sources": ["https://xd.is/2026/02/23/frambodslisti-sjalfstaedisflokksins-i-fjardabyggd-samthykktur-2/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "byggingaiðnfræðingur að mennt", "quotes": ["6 Friðrik Júlíus Jósefsson, byggingaiðnfræðingur"]},
        {"n": 2, "status": "verified", "claim": "skipar 6. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð", "quotes": ["6 Friðrik Júlíus Jósefsson", "Framboðslisti Sjálfstæðisflokksins í Fjarðabyggð samþykktur"]},
        {"n": 3, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 2026", "quotes": ["sveitarstjórnarkosningarnar í Fjarðabyggð sem fram fara þann 16. maí 2026"]},
        {"n": 4, "status": "verified", "claim": "Listinn var samþykktur í febrúar 2026", "quotes": ["samþykkti á fundi sínum þann 21. febrúar 2026 tillögu kjörnefndar að framboðslista"]},
        {"n": 5, "status": "verified", "claim": "leiddur af Ragnari Sigurðssyni framkvæmdastjóra", "quotes": ["Ragnar Sigurðsson sjálfkjörinn sem oddviti listans", "1 Ragnar Sigurðsson, framkvæmdastjóri og formaður bæjarráðs"]}
    ],
    "summary": "5 verified, 0 flagged",
    "rescue": None
})

# ---------- FJD.D.7 ----------
results.append({
    "id": "FJD.D.7",
    "bio": "Bryngeir Ágúst Margeirsson skipar 7. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð fyrir sveitarstjórnarkosningarnar 2026. Á opinberri kynningu listans í febrúar 2026 er hann tilgreindur sem afgreiðslustjóri. Listinn er leiddur af Ragnari Sigurðssyni framkvæmdastjóra og var samþykktur 21. febrúar 2026.",
    "sources": ["https://xd.is/2026/02/23/frambodslisti-sjalfstaedisflokksins-i-fjardabyggd-samthykktur-2/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "skipar 7. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð", "quotes": ["7 Bryngeir Ágúst Margeirsson, afgreiðslustjóri"]},
        {"n": 2, "status": "verified", "claim": "tilgreindur sem afgreiðslustjóri", "quotes": ["7 Bryngeir Ágúst Margeirsson, afgreiðslustjóri"]},
        {"n": 3, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 2026 (16. maí)", "quotes": ["sveitarstjórnarkosningarnar í Fjarðabyggð sem fram fara þann 16. maí 2026"]},
        {"n": 4, "status": "verified", "claim": "Listinn er leiddur af Ragnari Sigurðssyni framkvæmdastjóra", "quotes": ["Ragnar Sigurðsson sjálfkjörinn sem oddviti", "1 Ragnar Sigurðsson, framkvæmdastjóri"]},
        {"n": 5, "status": "verified", "claim": "samþykktur 21. febrúar 2026", "quotes": ["samþykkti á fundi sínum þann 21. febrúar 2026"]}
    ],
    "summary": "5 verified, 0 flagged",
    "rescue": None
})

# ---------- FJD.D.8 ----------
results.append({
    "id": "FJD.D.8",
    "bio": "Hildur Ósk Pétursdóttir er leikskólastjóri í Fjarðabyggð og skipar 8. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð fyrir sveitarstjórnarkosningarnar 2026. Listinn var samþykktur 21. febrúar 2026 og er leiddur af Ragnari Sigurðssyni framkvæmdastjóra.",
    "sources": ["https://xd.is/2026/02/23/frambodslisti-sjalfstaedisflokksins-i-fjardabyggd-samthykktur-2/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "leikskólastjóri", "quotes": ["8 Hildur Ósk Pétursdóttir, leikskólastjóri"]},
        {"n": 2, "status": "flagged", "claim": "í Fjarðabyggð (sem starfsstaður leikskólastjóra)", "notes": "Source listar starfstitil án staðsetningar leikskólans; Fjarðabyggð er listinn, ekki vinnustaður."},
        {"n": 3, "status": "verified", "claim": "skipar 8. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð", "quotes": ["8 Hildur Ósk Pétursdóttir, leikskólastjóri"]},
        {"n": 4, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 2026", "quotes": ["sveitarstjórnarkosningarnar í Fjarðabyggð sem fram fara þann 16. maí 2026"]},
        {"n": 5, "status": "verified", "claim": "samþykktur 21. febrúar 2026", "quotes": ["samþykkti á fundi sínum þann 21. febrúar 2026"]},
        {"n": 6, "status": "verified", "claim": "leiddur af Ragnari Sigurðssyni framkvæmdastjóra", "quotes": ["Ragnar Sigurðsson sjálfkjörinn sem oddviti listans"]}
    ],
    "summary": "5 verified, 1 flagged",
    "rescue": {
        "rewrite": "Hildur Ósk Pétursdóttir er leikskólastjóri og skipar 8. sæti á framboðslista Sjálfstæðisflokksins í Fjarðabyggð fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listinn var samþykktur 21. febrúar 2026 og er leiddur af Ragnari Sigurðssyni framkvæmdastjóra og formanni bæjarráðs.",
        "rewrite_words": 41,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "Staðsetning leikskóla (Fjarðabyggð) ekki tilgreind í heimild; almennt leikskólastjóri."}
        ],
        "new_heimild": [{"url": "https://xd.is/2026/02/23/frambodslisti-sjalfstaedisflokksins-i-fjardabyggd-samthykktur-2/", "label": "Sjálfstæðisflokkurinn — Framboðslisti í Fjarðabyggð (2026-02-23)"}]
    }
})

# ---------- FJD.S.8 — Esther Ösp Gunnarsdóttir ----------
results.append({
    "id": "FJD.S.8",
    "bio": "Esther Ösp Gunnarsdóttir er hönnuður og starfar sem vefumsjónarmaður hjá Austurbrú á Reyðarfirði, þar sem hún sinnir vefumsjón, hönnun og grafík. Hún hefur B.A.-próf í íslensku, M.A.-próf í ritstjórn og útgáfu og diplómanám í grafískri hönnun. Esther Ösp skipar 8. sæti á sameiginlegum lista Samfylkingar og félagshyggjufólks í Fjarðabyggð fyrir sveitarstjórnarkosningarnar 2026.",
    "sources": ["https://austurbru.is/starfsmadur/esther-osp-gunnarsdottir/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "starfar hjá Austurbrú á Reyðarfirði og sinnir vefumsjón, hönnun og grafík", "quotes": ["Vinnustaður: Reyðarfjörður", "Helstu verkefni: Vefumsjón, hönnun og grafík."]},
        {"n": 2, "status": "flagged", "claim": "starfsheiti 'vefumsjónarmaður'", "notes": "Heimild segir aðeins 'Helstu verkefni: Vefumsjón, hönnun og grafík.' Engin tiltekin starfsheitun."},
        {"n": 3, "status": "verified", "claim": "B.A. í íslensku, M.A. í ritstjórn og útgáfu og diplóma í grafískri hönnun", "quotes": ["Menntun: B.A. í íslensku, M.A. í ritstjórn og útgáfu og diplóma í grafískri hönnun."]},
        {"n": 4, "status": "flagged", "claim": "skipar 8. sæti á sameiginlegum lista Samfylkingar og félagshyggjufólks í Fjarðabyggð 2026", "notes": "Austurbrú-síðan styður engar pólitískar fullyrðingar. Þarfnast sérstakrar heimildar."},
        {"n": 5, "status": "flagged", "claim": "er hönnuður", "notes": "Austurbrú-síðan nefnir ekki 'hönnuður' sem starfsheiti."}
    ],
    "summary": "2 verified, 3 flagged",
    "rescue": {
        "rewrite": "Esther Ösp Gunnarsdóttir er hönnuður og starfar hjá Austurbrú á Reyðarfirði þar sem hún sinnir vefumsjón, hönnun og grafík. Hún er með B.A.-próf í íslensku, M.A.-próf í ritstjórn og útgáfu og diplómanám í grafískri hönnun. Esther Ösp skipar 8. sæti á framboðslista Samfylkingarinnar og annars félagshyggjufólks í Fjarðabyggð fyrir sveitarstjórnarkosningarnar 2026.",
        "rewrite_words": 60,
        "new_sources": ["https://www.austurfrett.is/frettir/stefan-og-hjoerdis-efst-hja-samfylkingunni-i-fjardhabyggdh"],
        "resolutions": [
            {"kind": "rescued", "text": "Sætisetning og listanafn staðfest af Austurfrétt: '8. Esther Ösp Gunnarsdóttir, hönnuður' á 'Framboðslista Samfylkingarinnar og annars félagshyggjufólks í Fjarðabyggð 2026'."},
            {"kind": "rescued", "text": "Starfsheitið 'hönnuður' staðfest af Austurfrétt-listanum."},
            {"kind": "dropped", "text": "'vefumsjónarmaður' fjarlægt; heimild segir aðeins verkefni, ekki starfsheiti."}
        ],
        "new_heimild": [
            {"url": "https://austurbru.is/starfsmadur/esther-osp-gunnarsdottir/", "label": "Austurbrú — Esther Ösp Gunnarsdóttir"},
            {"url": "https://www.austurfrett.is/frettir/stefan-og-hjoerdis-efst-hja-samfylkingunni-i-fjardhabyggdh", "label": "Austurfrétt — Stefán og Hjördís efst hjá Samfylkingunni í Fjarðabyggð (2026)"}
        ]
    }
})

# ---------- HAF.D.16 ----------
results.append({
    "id": "HAF.D.16",
    "bio": "Guðjón Óskar Guðmundsson er framhaldsskólakennari og skipar 16. sæti á lista Sjálfstæðisflokksins í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026. Framboðslistinn var kynntur í mars 2026 og er leiddur af bæjarfulltrúum flokksins í Hafnarfirði.",
    "sources": ["https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hafnarfirdi/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "framhaldsskólakennari", "quotes": ["16. Guðjón Óskar Guðmundsson, framhaldsskólakennari"]},
        {"n": 2, "status": "verified", "claim": "skipar 16. sæti á lista Sjálfstæðisflokksins í Hafnarfirði", "quotes": ["16. Guðjón Óskar Guðmundsson, framhaldsskólakennari", "Framboðslisti Sjálfstæðisflokksins í Hafnarfirði 2026"]},
        {"n": 3, "status": "verified", "claim": "kynntur í mars 2026", "quotes": ["4. mars 2026 Framboðslisti Sjálfstæðisflokksins í Hafnarfirði", "samþykktur á fjölmennum fundi fulltrúaráðs sjálfstæðisfélaganna í Hafnarfirði þriðjudagskvöldið 3. mars"]},
        {"n": 4, "status": "verified", "claim": "leiddur af bæjarfulltrúum flokksins í Hafnarfirði", "quotes": ["1. Orri Björnsson, bæjarfulltrúi og formaður bæjarráðs", "2. Kristín María Thoroddsen, bæjarfulltrúi og formaður fræðsluráðs"]}
    ],
    "summary": "4 verified, 0 flagged",
    "rescue": None
})

# ---------- HAF.D.17 ----------
results.append({
    "id": "HAF.D.17",
    "bio": "Paula Wiszniewska er hársnyrtir í Hafnarfirði og skipar 17. sæti á lista Sjálfstæðisflokksins í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026. Framboðslistinn var kynntur í mars 2026.",
    "sources": ["https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hafnarfirdi/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "hársnyrtir", "quotes": ["17. Paula Wiszniewska, hársnyrtir"]},
        {"n": 2, "status": "flagged", "claim": "í Hafnarfirði (sem starfsstaður)", "notes": "Heimild gefur aðeins starfsheiti; engin staðsetning starfsstöðvar."},
        {"n": 3, "status": "verified", "claim": "skipar 17. sæti á lista Sjálfstæðisflokksins í Hafnarfirði", "quotes": ["17. Paula Wiszniewska, hársnyrtir", "Framboðslisti Sjálfstæðisflokksins í Hafnarfirði 2026"]},
        {"n": 4, "status": "verified", "claim": "kynntur í mars 2026", "quotes": ["4. mars 2026 Framboðslisti Sjálfstæðisflokksins í Hafnarfirði"]}
    ],
    "summary": "3 verified, 1 flagged",
    "rescue": {
        "rewrite": "Paula Wiszniewska er hársnyrtir og skipar 17. sæti á lista Sjálfstæðisflokksins í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026. Framboðslistinn var samþykktur á fundi fulltrúaráðs sjálfstæðisfélaganna 3. mars 2026 og er leiddur af Orra Björnssyni, formanni bæjarráðs.",
        "rewrite_words": 41,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "Tiltekin staðsetning hársnyrtistarfs ('í Hafnarfirði') ekki í heimild."}
        ],
        "new_heimild": [{"url": "https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hafnarfirdi/", "label": "Sjálfstæðisflokkurinn — Framboðslisti í Hafnarfirði (2026-03-04)"}]
    }
})

# ---------- HAF.D.18 ----------
results.append({
    "id": "HAF.D.18",
    "bio": "Þórhallur Guðmundsson er viðskiptafræðingur og skipar 18. sæti á lista Sjálfstæðisflokksins í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026. Framboðslistinn var kynntur í mars 2026.",
    "sources": ["https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hafnarfirdi/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "viðskiptafræðingur", "quotes": ["18. Þórhallur Guðmundsson, viðskiptafræðingur"]},
        {"n": 2, "status": "verified", "claim": "skipar 18. sæti á lista Sjálfstæðisflokksins í Hafnarfirði", "quotes": ["18. Þórhallur Guðmundsson, viðskiptafræðingur", "Framboðslisti Sjálfstæðisflokksins í Hafnarfirði 2026"]},
        {"n": 3, "status": "verified", "claim": "kynntur í mars 2026", "quotes": ["4. mars 2026 Framboðslisti Sjálfstæðisflokksins í Hafnarfirði"]}
    ],
    "summary": "3 verified, 0 flagged",
    "rescue": None
})

# ---------- HAF.S.19 ----------
results.append({
    "id": "HAF.S.19",
    "bio": "Ragnar Már Jónsson er saxófónleikari og tónlistarkennari og hefur áralanga reynslu af tónlistarstarfi og kennslu. Hann skipar 19. sæti á lista Samfylkingarinnar í Hafnarfirði í sveitarstjórnarkosningum 2026.",
    "sources": ["https://xs.is/frambjodendur-i-hafnarfirdi-2026"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "saxófónleikari og tónlistarkennari", "quotes": ["19. Ragnar Már Jónsson Saxafónleikari og tónlistarkennari"]},
        {"n": 2, "status": "flagged", "claim": "hefur áralanga reynslu af tónlistarstarfi og kennslu", "notes": "Heimild gefur aðeins starfsheiti; engin athugasemd um reynslu."},
        {"n": 3, "status": "verified", "claim": "skipar 19. sæti á lista Samfylkingarinnar í Hafnarfirði 2026", "quotes": ["19. Ragnar Már Jónsson", "Frambjóðendur í Hafnarfirði 2026"]}
    ],
    "summary": "2 verified, 1 flagged",
    "rescue": {
        "rewrite": "Ragnar Már Jónsson er saxófónleikari og tónlistarkennari og skipar 19. sæti á lista Samfylkingarinnar í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026. Listann leiðir Guðmundur Árni Stefánsson, bæjarfulltrúi og varaformaður Samfylkingarinnar.",
        "rewrite_words": 35,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'áralanga reynslu' fjarlægt; engin heimildastoð."}
        ],
        "new_heimild": [{"url": "https://xs.is/frambjodendur-i-hafnarfirdi-2026", "label": "Samfylkingin — Frambjóðendur í Hafnarfirði 2026"}]
    }
})

# ---------- HAF.S.20 ----------
results.append({
    "id": "HAF.S.20",
    "bio": "Sigrid Foss er eftirlaunaþegi og fyrrverandi fótaaðgerðafræðingur í Hafnarfirði. Hún hefur lengi verið virk í starfi Samfylkingarinnar í bænum og leggur áherslu á málefni eldri borgara og velferðarþjónustu. Sigrid skipar 20. sæti á lista Samfylkingarinnar í Hafnarfirði í sveitarstjórnarkosningum 2026.",
    "sources": ["https://xs.is/frambjodendur-i-hafnarfirdi-2026"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "eftirlaunaþegi", "quotes": ["20. Sigrid Foss Eftirlaunaþegi"]},
        {"n": 2, "status": "flagged", "claim": "fyrrverandi fótaaðgerðafræðingur í Hafnarfirði", "notes": "Heimild segir aðeins 'Eftirlaunaþegi'; ekkert um fyrri starfsferil eða Hafnarfjörð sem starfsstöð."},
        {"n": 3, "status": "flagged", "claim": "lengi verið virk í starfi Samfylkingarinnar í bænum", "notes": "Heimild styður ekki sögulega virkni."},
        {"n": 4, "status": "flagged", "claim": "leggur áherslu á málefni eldri borgara og velferðarþjónustu", "notes": "Heimild gefur engin sérstök áhersluatriði."},
        {"n": 5, "status": "verified", "claim": "skipar 20. sæti á lista Samfylkingarinnar í Hafnarfirði 2026", "quotes": ["20. Sigrid Foss", "Frambjóðendur í Hafnarfirði 2026"]}
    ],
    "summary": "2 verified, 3 flagged",
    "rescue": {
        "rewrite": "Sigrid Foss er eftirlaunaþegi og skipar 20. sæti á lista Samfylkingarinnar í Hafnarfirði fyrir sveitarstjórnarkosningarnar 2026. Oddviti listans er Guðmundur Árni Stefánsson, bæjarfulltrúi og varaformaður Samfylkingarinnar.",
        "rewrite_words": 31,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'fyrrverandi fótaaðgerðafræðingur' fjarlægt; ekki í heimild."},
            {"kind": "dropped", "text": "Áralanga virkni í Samfylkingunni og áhersluatriði (eldri borgarar, velferð) fjarlægð; engin heimildastoð."}
        ],
        "new_heimild": [{"url": "https://xs.is/frambjodendur-i-hafnarfirdi-2026", "label": "Samfylkingin — Frambjóðendur í Hafnarfirði 2026"}]
    }
})

# ---------- HMR.D.3 ----------
results.append({
    "id": "HMR.D.3",
    "bio": "Ragnar Lúðvík Jónsson er viðskiptafræðingur og leiðsögumaður búsettur við Ásastíg 12b á Flúðum í Hrunamannahreppi. Hann skipar 3. sæti á D-lista Sjálfstæðisflokks og óháðra fyrir sveitarstjórnarkosningarnar í Hrunamannahreppi 16. maí 2026. Listinn er leiddur af Jóni Bjarnasyni og Bjarney Vignisdóttir skipar annað sætið. Hrunamannahreppur er sveitarfélag á Suðurlandi með kjarnabyggð á Flúðum, þekkt fyrir öflugan landbúnað, gróðurhúsarækt og ferðaþjónustu með náttúruperlum á borð við Hrunalaug og Gullfoss.",
    "sources": ["https://www.fludir.is/is/frettir/auglysing-fra-kjorstjorn-hrunamannahrepps-sveitarstjornarkosningar-i-hrunamannahreppi-16-mai-2027"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "viðskiptafræðingur og leiðsögumaður", "quotes": ["Ragnar Lúðvík Jónsson Ásastíg 12 b. Viðskiptafræðingur/leiðsögumaður."]},
        {"n": 2, "status": "verified", "claim": "búsettur við Ásastíg 12b á Flúðum", "quotes": ["Ragnar Lúðvík Jónsson Ásastíg 12 b."]},
        {"n": 3, "status": "verified", "claim": "skipar 3. sæti á D-lista Sjálfstæðismanna og óháðra", "quotes": ["D-Listi Sjálfstæðismanna og óháðra. Jón Bjarnason ... Bjarney Vignisdóttir ... Ragnar Lúðvík Jónsson"]},
        {"n": 4, "status": "verified", "claim": "í Hrunamannahreppi 16. maí 2026", "quotes": ["Sveitarstjórnarkosningar í Hrunamannahreppi 16. maí 2026"]},
        {"n": 5, "status": "verified", "claim": "leiddur af Jóni Bjarnasyni; Bjarney Vignisdóttir skipar annað sætið", "quotes": ["Jón Bjarnason Skipholti 3. Bóndi/oddviti.", "Bjarney Vignisdóttir Auðsholti 6. Hjúkrunarfræðingur."]},
        {"n": 6, "status": "flagged", "claim": "Hrunamannahreppur er sveitarfélag á Suðurlandi með kjarnabyggð á Flúðum, þekkt fyrir öflugan landbúnað, gróðurhúsarækt og ferðaþjónustu með náttúruperlum á borð við Hrunalaug og Gullfoss", "notes": "Almennur svæðislýsingartexti; ekki í þeirri tilteknu heimild (kjörstjórnar-auglýsing). Slíkt er almenn vitneskja en ekki rakið til nefndrar heimildar."}
    ],
    "summary": "5 verified, 1 flagged",
    "rescue": {
        "rewrite": "Ragnar Lúðvík Jónsson er viðskiptafræðingur og leiðsögumaður, búsettur við Ásastíg 12b á Flúðum. Hann skipar 3. sæti á D-lista Sjálfstæðismanna og óháðra fyrir sveitarstjórnarkosningarnar í Hrunamannahreppi 16. maí 2026. Listann leiðir Jón Bjarnason, bóndi og oddviti, og Bjarney Vignisdóttir hjúkrunarfræðingur skipar annað sætið.",
        "rewrite_words": 49,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "Sveitarfélagslýsing (Suðurland, gróðurhús, Hrunalaug, Gullfoss) fjarlægð; ekki í tilvísaðri heimild."}
        ],
        "new_heimild": [{"url": "https://www.fludir.is/is/frettir/auglysing-fra-kjorstjorn-hrunamannahrepps-sveitarstjornarkosningar-i-hrunamannahreppi-16-mai-2027", "label": "Hrunamannahreppur — Auglýsing kjörstjórnar (16. maí 2026)"}]
    }
})

# ---------- HMR.D.6 ----------
results.append({
    "id": "HMR.D.6",
    "bio": "Elísabet Finnbjörnsdóttir er rútubílstjóri, búsett að Ásastíg 4a á Flúðum. Hún skipar 6. sæti á D-lista Sjálfstæðisflokksins og óháðra í Hrunamannahreppi fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://www.fludir.is/is/frettir/auglysing-fra-kjorstjorn-hrunamannahrepps-sveitarstjornarkosningar-i-hrunamannahreppi-16-mai-2027"],
    "statements": [
        {"n": 1, "status": "flagged", "claim": "rútubílstjóri", "notes": "Heimild segir aðeins 'Bílstjóri' — ekki sérstaklega rútubílstjóri."},
        {"n": 2, "status": "verified", "claim": "búsett að Ásastíg 4a á Flúðum", "quotes": ["Elísabet Finnbjörnsdóttir Ásastíg 4a. Bílstjóri."]},
        {"n": 3, "status": "verified", "claim": "skipar 6. sæti á D-lista Sjálfstæðismanna og óháðra í Hrunamannahreppi", "quotes": ["D-Listi Sjálfstæðismanna og óháðra. ... Elísabet Finnbjörnsdóttir Ásastíg 4a. Bílstjóri."]},
        {"n": 4, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "quotes": ["Sveitarstjórnarkosningar í Hrunamannahreppi 16. maí 2026"]}
    ],
    "summary": "3 verified, 1 flagged",
    "rescue": {
        "rewrite": "Elísabet Finnbjörnsdóttir er bílstjóri, búsett að Ásastíg 4a á Flúðum. Hún skipar 6. sæti á D-lista Sjálfstæðismanna og óháðra í Hrunamannahreppi fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
        "rewrite_words": 32,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'rútu-' forskeyti fjarlægt; heimild segir aðeins 'Bílstjóri'."}
        ],
        "new_heimild": [{"url": "https://www.fludir.is/is/frettir/auglysing-fra-kjorstjorn-hrunamannahrepps-sveitarstjornarkosningar-i-hrunamannahreppi-16-mai-2027", "label": "Hrunamannahreppur — Auglýsing kjörstjórnar (16. maí 2026)"}]
    }
})

# ---------- HMR.D.8 ----------
results.append({
    "id": "HMR.D.8",
    "bio": "María Magnúsdóttir er verslunarstjóri, búsett að Vesturbrún 23 á Flúðum. Hún skipar 8. sæti á D-lista Sjálfstæðisflokksins og óháðra í Hrunamannahreppi fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://www.fludir.is/is/frettir/auglysing-fra-kjorstjorn-hrunamannahrepps-sveitarstjornarkosningar-i-hrunamannahreppi-16-mai-2027"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "verslunarstjóri", "quotes": ["María Magnúsdóttir Vesturbrún 23. Verslunarstjóri."]},
        {"n": 2, "status": "verified", "claim": "búsett að Vesturbrún 23 á Flúðum", "quotes": ["María Magnúsdóttir Vesturbrún 23."]},
        {"n": 3, "status": "verified", "claim": "skipar 8. sæti á D-lista Sjálfstæðismanna og óháðra í Hrunamannahreppi", "quotes": ["D-Listi Sjálfstæðismanna og óháðra. ... María Magnúsdóttir Vesturbrún 23. Verslunarstjóri."]},
        {"n": 4, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "quotes": ["Sveitarstjórnarkosningar í Hrunamannahreppi 16. maí 2026"]}
    ],
    "summary": "4 verified, 0 flagged",
    "rescue": None
})

# ---------- HNB.D.10 ----------
results.append({
    "id": "HNB.D.10",
    "bio": "Friðrún Fanný Guðmundsdóttir er dýralæknir, búsett að Bergsstöðum í Húnabyggð. Hún skipar 10. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://huni.is/index.php?cid=22686&pid=32"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "dýralæknir", "quotes": ["10. Friðrún Fanný Guðmundsdóttir, Bergsstöðum – dýralæknir"]},
        {"n": 2, "status": "verified", "claim": "búsett að Bergsstöðum", "quotes": ["10. Friðrún Fanný Guðmundsdóttir, Bergsstöðum"]},
        {"n": 3, "status": "verified", "claim": "skipar 10. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð", "quotes": ["10. Friðrún Fanný Guðmundsdóttir", "Sjálfstæðismenn og óháðir í Húnabyggð hafa samþykkt tillögu uppstillingarnefndar um framboðslista"]},
        {"n": 4, "status": "flagged", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "notes": "Heimild segir 'sveitarstjórnarkosningarnar í vor' (mars 2026 fréttin); 16. maí ekki nefnt í þessari heimild."}
    ],
    "summary": "3 verified, 1 flagged",
    "rescue": {
        "rewrite": "Friðrún Fanný Guðmundsdóttir er dýralæknir á Bergsstöðum í Húnabyggð og skipar 10. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 2026. Listann leiðir Guðmundur Haukur Jakobsson, forseti sveitarstjórnar.",
        "rewrite_words": 33,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'16. maí' fjarlægt; ekki í þessari heimild."}
        ],
        "new_heimild": [{"url": "https://huni.is/index.php?cid=22686&pid=32", "label": "Húnahornið — Sjálfstæðismenn og óháðir samþykkja framboðslista (Húnabyggð, 2026)"}]
    }
})

# ---------- HNB.D.14 ----------
results.append({
    "id": "HNB.D.14",
    "bio": "Anna Margrét Jónsdóttir er bóndi á Sölvabakka í Húnabyggð. Hún skipar 14. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 2026.",
    "sources": ["https://huni.is/index.php?cid=22686&pid=32"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "bóndi á Sölvabakka", "quotes": ["14. Anna Margrét Jónsdóttir, Sölvabakka – bóndi"]},
        {"n": 2, "status": "verified", "claim": "skipar 14. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð", "quotes": ["14. Anna Margrét Jónsdóttir", "Sjálfstæðismenn og óháðir í Húnabyggð hafa samþykkt tillögu uppstillingarnefndar um framboðslista"]},
        {"n": 3, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 2026", "quotes": ["sveitarstjórnarkosningarnar í vor", "21. mars 2026"]}
    ],
    "summary": "3 verified, 0 flagged",
    "rescue": None
})

# ---------- HNB.D.3 ----------
results.append({
    "id": "HNB.D.3",
    "bio": "Kolbrún Ágústa Guðnadóttir er sérfræðingur og viðskiptafræðingur frá Mánaskál í Húnabyggð. Hún skipar 3. sæti á sameiginlegum lista Sjálfstæðisflokks og óháðra (D-lista) í Húnabyggð fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listann leiðir Guðmundur Haukur Jakobsson, sitjandi sveitarstjórnarmaður, og Zophonías Ari Lárusson skipar annað sætið. Kolbrún Ágústa býr og starfar á Mánaskál sem er bær í gamla Vindhælishreppi á Skagaströnd, en Húnabyggð er stórt sveitarfélag á Norðurlandi vestra sem varð til með sameiningu Blönduósbæjar og Húnavatnshrepps árið 2022.",
    "sources": ["https://huni.is/index.php?cid=22686&pid=32"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "sérfræðingur og viðskiptafræðingur frá Mánaskál", "quotes": ["3. Kolbrún Ágústa Guðnadóttir, Mánaskál – sérfræðingur & viðskiptafræðingur"]},
        {"n": 2, "status": "verified", "claim": "skipar 3. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð", "quotes": ["í þriðja sæti er Kolbrún Ágústa Guðnadóttir", "Sjálfstæðismenn og óháðir í Húnabyggð hafa samþykkt tillögu uppstillingarnefndar um framboðslista"]},
        {"n": 3, "status": "flagged", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "notes": "Heimild segir 'sveitarstjórnarkosningarnar í vor'; 16. maí ekki nefnt."},
        {"n": 4, "status": "verified", "claim": "Listann leiðir Guðmundur Haukur Jakobsson", "quotes": ["Oddviti listans er Guðmundur Haukur Jakobsson", "1. Guðmundur Haukur Jakobsson, Blönduósi – forseti sveitarstjórnar"]},
        {"n": 5, "status": "flagged", "claim": "sitjandi sveitarstjórnarmaður", "notes": "Heimild segir nákvæmlega 'forseti sveitarstjórnar' — bio orðar þetta lauslega; rétt en óprýtt."},
        {"n": 6, "status": "verified", "claim": "Zophonías Ari Lárusson skipar annað sætið", "quotes": ["í öðru sæti er Zophonías Ari Lárusson"]},
        {"n": 7, "status": "flagged", "claim": "Mánaskál er bær í gamla Vindhælishreppi á Skagaströnd", "notes": "Almenn landfræðileg staðreynd ekki í þessari heimild; heimild segir aðeins 'Mánaskál'."},
        {"n": 8, "status": "flagged", "claim": "Húnabyggð varð til með sameiningu Blönduósbæjar og Húnavatnshrepps árið 2022", "notes": "Sögulegt almennt fróðleiks-statement ekki í þessari heimild."}
    ],
    "summary": "4 verified, 4 flagged",
    "rescue": {
        "rewrite": "Kolbrún Ágústa Guðnadóttir er sérfræðingur og viðskiptafræðingur frá Mánaskál og skipar 3. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 2026. Listinn er leiddur af Guðmundi Hauki Jakobssyni, forseta sveitarstjórnar Húnabyggðar, og Zophonías Ari Lárusson skipar annað sætið.",
        "rewrite_words": 47,
        "new_sources": [],
        "resolutions": [
            {"kind": "contradicted", "text": "'sitjandi sveitarstjórnarmaður' uppfært í 'forseti sveitarstjórnar' (orðalag heimildar)."},
            {"kind": "dropped", "text": "Landfræðilegur og sögulegur fróðleikur (Vindhælishreppur, Skagaströnd, sameining 2022) fjarlægður; ekki í þessari heimild."},
            {"kind": "dropped", "text": "'16. maí' fjarlægt; aðeins 'í vor' í heimild."}
        ],
        "new_heimild": [{"url": "https://huni.is/index.php?cid=22686&pid=32", "label": "Húnahornið — Sjálfstæðismenn og óháðir samþykkja framboðslista (Húnabyggð, 2026)"}]
    }
})

# ---------- HNB.D.8 ----------
results.append({
    "id": "HNB.D.8",
    "bio": "Magnús Sigurjónsson er bóndi og skrifstofustjóri að Syðri-Brekku í fyrrum Húnavatnshreppi, sem nú tilheyrir sveitarfélaginu Húnabyggð. Magnús skipar 8. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://huni.is/index.php?cid=22686&pid=32"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "bóndi (að Syðri-Brekku)", "quotes": ["8. Magnús Sigurjónsson, Syðri-Brekku – bóndi & skrifstofumaður"]},
        {"n": 2, "status": "flagged", "claim": "skrifstofustjóri", "notes": "Heimild segir 'skrifstofumaður' — ekki '-stjóri'."},
        {"n": 3, "status": "verified", "claim": "að Syðri-Brekku", "quotes": ["8. Magnús Sigurjónsson, Syðri-Brekku"]},
        {"n": 4, "status": "flagged", "claim": "í fyrrum Húnavatnshreppi, sem nú tilheyrir sveitarfélaginu Húnabyggð", "notes": "Sögulegur fróðleikur ekki í heimild."},
        {"n": 5, "status": "verified", "claim": "skipar 8. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð", "quotes": ["8. Magnús Sigurjónsson", "Sjálfstæðismenn og óháðir í Húnabyggð hafa samþykkt tillögu uppstillingarnefndar um framboðslista"]},
        {"n": 6, "status": "flagged", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "notes": "Heimild segir 'í vor'; 16. maí ekki nefnt."}
    ],
    "summary": "3 verified, 3 flagged",
    "rescue": {
        "rewrite": "Magnús Sigurjónsson er bóndi og skrifstofumaður að Syðri-Brekku í Húnabyggð. Hann skipar 8. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 2026.",
        "rewrite_words": 27,
        "new_sources": [],
        "resolutions": [
            {"kind": "contradicted", "text": "'skrifstofustjóri' leiðrétt í 'skrifstofumaður'."},
            {"kind": "dropped", "text": "'fyrrum Húnavatnshreppur ... sameining' fjarlægt; ekki í heimild."},
            {"kind": "dropped", "text": "'16. maí' fjarlægt; aðeins 'í vor' í heimild."}
        ],
        "new_heimild": [{"url": "https://huni.is/index.php?cid=22686&pid=32", "label": "Húnahornið — Sjálfstæðismenn og óháðir samþykkja framboðslista (Húnabyggð, 2026)"}]
    }
})

# ---------- HNB.D.9 ----------
results.append({
    "id": "HNB.D.9",
    "bio": "Anton Haraldsson er rafvirki og kennari, búsettur á Blönduósi. Hann skipar 9. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://huni.is/index.php?cid=22686&pid=32"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "rafvirki", "quotes": ["9. Anton Haraldsson, Blönduósi – leiðbeinandi & rafvirki"]},
        {"n": 2, "status": "flagged", "claim": "kennari", "notes": "Heimild segir 'leiðbeinandi'; 'kennari' er þrengri og ekki í heimild."},
        {"n": 3, "status": "verified", "claim": "búsettur á Blönduósi", "quotes": ["9. Anton Haraldsson, Blönduósi"]},
        {"n": 4, "status": "verified", "claim": "skipar 9. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð", "quotes": ["9. Anton Haraldsson", "Sjálfstæðismenn og óháðir í Húnabyggð hafa samþykkt tillögu uppstillingarnefndar um framboðslista"]},
        {"n": 5, "status": "flagged", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "notes": "Heimild segir 'í vor'; 16. maí ekki nefnt."}
    ],
    "summary": "3 verified, 2 flagged",
    "rescue": {
        "rewrite": "Anton Haraldsson er leiðbeinandi og rafvirki, búsettur á Blönduósi. Hann skipar 9. sæti á D-lista Sjálfstæðismanna og óháðra í Húnabyggð fyrir sveitarstjórnarkosningarnar 2026.",
        "rewrite_words": 26,
        "new_sources": [],
        "resolutions": [
            {"kind": "contradicted", "text": "'kennari' breytt í 'leiðbeinandi' eins og heimild."},
            {"kind": "dropped", "text": "'16. maí' fjarlægt; aðeins 'í vor' í heimild."}
        ],
        "new_heimild": [{"url": "https://huni.is/index.php?cid=22686&pid=32", "label": "Húnahornið — Sjálfstæðismenn og óháðir samþykkja framboðslista (Húnabyggð, 2026)"}]
    }
})

# ---------- HNT.D.10 ----------
results.append({
    "id": "HNT.D.10",
    "bio": "Dagný Sigurlaug Ragnarsdóttir er bóndi að Bakka í Húnaþingi vestra. Hún skipar 10. sæti á D-lista Sjálfstæðisflokksins og óháðra í Húnaþingi vestra fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://www.hunathing.is/is/mannlif/frettir-og-auglysingar/tilkynningar-og-frettir/auglysing-um-urskurd-kjorstjornar-hunathings-vestra"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "bóndi að Bakka", "quotes": ["Dagný Sigurlaug Ragnarsdóttir, kt. 070777-5179, Bakka , bóndi"]},
        {"n": 2, "status": "verified", "claim": "skipar 10. sæti á D-lista Sjálfstæðismanna og óháðra í Húnaþingi vestra", "quotes": ["D-listi – Sjálfstæðismanna og óháðra ... Dagný Sigurlaug Ragnarsdóttir, kt. 070777-5179, Bakka , bóndi"]},
        {"n": 3, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "quotes": ["Kjörstjórn Húnaþings vestra hefur farið yfir framboð til sveitarstjórnarkosninga sem fram fara laugardaginn 16. maí 2026"]}
    ],
    "summary": "3 verified, 0 flagged",
    "rescue": None
})

# ---------- HNT.D.6 ----------
results.append({
    "id": "HNT.D.6",
    "bio": "Stella Dröfn Bjarnadóttir er bóndi á Efri-Fitjum í Húnaþingi vestra, fædd árið 1997. Hún skipar 6. sæti á D-lista Sjálfstæðisflokksins og óháðra í Húnaþingi vestra fyrir sveitarstjórnarkosningarnar 16. maí 2026. Listinn er undir forystu Arnar Arnarsonar.",
    "sources": ["https://www.hunathing.is/is/mannlif/frettir-og-auglysingar/tilkynningar-og-frettir/auglysing-um-urskurd-kjorstjornar-hunathings-vestra"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "bóndi á Efri-Fitjum", "quotes": ["Stella Dröfn Bjarnadóttir, kt. 010797-3579, Efri-Fitjum, bóndi"]},
        {"n": 2, "status": "verified", "claim": "fædd árið 1997", "quotes": ["Stella Dröfn Bjarnadóttir, kt. 010797-3579"]},
        {"n": 3, "status": "verified", "claim": "skipar 6. sæti á D-lista Sjálfstæðismanna og óháðra í Húnaþingi vestra", "quotes": ["D-listi – Sjálfstæðismanna og óháðra ... Stella Dröfn Bjarnadóttir, kt. 010797-3579, Efri-Fitjum, bóndi"]},
        {"n": 4, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "quotes": ["sveitarstjórnarkosninga sem fram fara laugardaginn 16. maí 2026"]},
        {"n": 5, "status": "verified", "claim": "Listinn er undir forystu Arnar Arnarsonar", "quotes": ["D-listi – Sjálfstæðismanna og óháðra Örn Arnarson, kt. 180870-4319, Skeggjagötu 1, framkvæmdastjóri"]}
    ],
    "summary": "5 verified, 0 flagged",
    "rescue": None
})

# ---------- HNT.D.8 ----------
results.append({
    "id": "HNT.D.8",
    "bio": "Stefán Páll Böðvarsson er bóndi að Mýrum 2 í Húnaþingi vestra. Hann skipar 8. sæti á D-lista Sjálfstæðisflokksins og óháðra í Húnaþingi vestra fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://www.hunathing.is/is/mannlif/frettir-og-auglysingar/tilkynningar-og-frettir/auglysing-um-urskurd-kjorstjornar-hunathings-vestra"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "bóndi að Mýrum 2", "quotes": ["Stefán Páll Böðvarsson, kt. 290802-2880, Mýrum 2, bóndi"]},
        {"n": 2, "status": "verified", "claim": "skipar 8. sæti á D-lista Sjálfstæðismanna og óháðra í Húnaþingi vestra", "quotes": ["D-listi – Sjálfstæðismanna og óháðra ... Stefán Páll Böðvarsson, kt. 290802-2880, Mýrum 2, bóndi"]},
        {"n": 3, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "quotes": ["sveitarstjórnarkosninga sem fram fara laugardaginn 16. maí 2026"]}
    ],
    "summary": "3 verified, 0 flagged",
    "rescue": None
})

# ---------- HNT.D.9 ----------
results.append({
    "id": "HNT.D.9",
    "bio": "Abdulwahab Abd Alhaji er verkamaður búsettur að Hvammstangabraut 31 á Hvammstanga. Hann skipar 9. sæti á D-lista Sjálfstæðisflokksins og óháðra í Húnaþingi vestra fyrir sveitarstjórnarkosningarnar 16. maí 2026.",
    "sources": ["https://www.hunathing.is/is/mannlif/frettir-og-auglysingar/tilkynningar-og-frettir/auglysing-um-urskurd-kjorstjornar-hunathings-vestra"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "verkamaður", "quotes": ["Abdulwahab Abd Alhaji, kt. 140688-5339, Hvammstangabraut 31, verkamaður"]},
        {"n": 2, "status": "verified", "claim": "búsettur að Hvammstangabraut 31", "quotes": ["Abdulwahab Abd Alhaji, kt. 140688-5339, Hvammstangabraut 31"]},
        {"n": 3, "status": "verified", "claim": "skipar 9. sæti á D-lista Sjálfstæðismanna og óháðra í Húnaþingi vestra", "quotes": ["D-listi – Sjálfstæðismanna og óháðra ... Abdulwahab Abd Alhaji, kt. 140688-5339, Hvammstangabraut 31, verkamaður"]},
        {"n": 4, "status": "verified", "claim": "fyrir sveitarstjórnarkosningarnar 16. maí 2026", "quotes": ["sveitarstjórnarkosninga sem fram fara laugardaginn 16. maí 2026"]}
    ],
    "summary": "4 verified, 0 flagged",
    "rescue": None
})

# ---------- HVG.D.4 ----------
results.append({
    "id": "HVG.D.4",
    "bio": "Hjalti Helgason er múrarameistari og starfar við viðhald mannvirkja í Hveragerði og nágrenni. Hann skipar 4. sæti á framboðslista Sjálfstæðisflokksins í Hveragerði í sveitarstjórnarkosningum 2026. Listinn var samþykktur einróma á fjölmennum félagsfundi 3. mars 2026 og er undir forystu Ingimars Guðmundssonar, sérfræðings hjá Sambandi íslenskra sveitarfélaga.",
    "sources": ["https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hveragerdi/"],
    "statements": [
        {"n": 1, "status": "verified", "claim": "múrarameistari", "quotes": ["4. Hjalti Helgason, múrarameistari"]},
        {"n": 2, "status": "flagged", "claim": "starfar við viðhald mannvirkja í Hveragerði og nágrenni", "notes": "Heimild gefur aðeins starfsheiti; engin lýsing á starfsstöð eða svæði."},
        {"n": 3, "status": "verified", "claim": "skipar 4. sæti á framboðslista Sjálfstæðisflokksins í Hveragerði 2026", "quotes": ["4. Hjalti Helgason, múrarameistari", "Framboðslisti Sjálfstæðisflokksins í Hveragerði"]},
        {"n": 4, "status": "verified", "claim": "samþykktur einróma á fjölmennum félagsfundi 3. mars 2026", "quotes": ["Framboðslisti D-listans í Hveragerði var samþykktur samhljóða á fjölmennum félagsfundi þriðjudaginn 3. mars"]},
        {"n": 5, "status": "verified", "claim": "leiddur af Ingimar Guðmundssyni, sérfræðings hjá Sambandi íslenskra sveitarfélaga", "quotes": ["Ingimar Guðmundsson, sérfræðingur hjá sambandi íslenskra sveitarfélaga mun koma til með að leiða listann"]}
    ],
    "summary": "4 verified, 1 flagged",
    "rescue": {
        "rewrite": "Hjalti Helgason er múrarameistari og skipar 4. sæti á framboðslista Sjálfstæðisflokksins í Hveragerði í sveitarstjórnarkosningunum 2026. Listinn var samþykktur samhljóða á fjölmennum félagsfundi 3. mars 2026 og er undir forystu Ingimars Guðmundssonar, sérfræðings hjá Sambandi íslenskra sveitarfélaga.",
        "rewrite_words": 42,
        "new_sources": [],
        "resolutions": [
            {"kind": "dropped", "text": "'starfar við viðhald mannvirkja í Hveragerði og nágrenni' fjarlægt; engin heimildastoð."}
        ],
        "new_heimild": [{"url": "https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hveragerdi/", "label": "Sjálfstæðisflokkurinn — Framboðslisti í Hveragerði (2026-03-04)"}]
    }
})

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"batch": 4, "results": results}, f, ensure_ascii=False, indent=2)

print(f"Wrote {len(results)} results")
