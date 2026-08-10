# -*- coding: utf-8 -*-
"""Build output_01.json from carefully drafted bios."""
import json

ENTRIES = []

# 0: Þóra Sigrún Kjartansdóttir (1604-S-10)
ENTRIES.append({
    "ruv_id": "1604-S-10",
    "new_bio": (
        "Þóra Sigrún Kjartansdóttir er hárgreiðslukona, fædd árið 1996 á Íslandi. "
        "Hún hefur lokið sveinsprófi í sinni grein og hefur verið í Samfylkingunni í átta ár. "
        "Auk íslensku talar hún ensku.\n\n"
        "Þóra býr í íbúð í Mosfellsbæ. Hún er tveggja barna móðir og hundamamma, og segir "
        "fjölskylduna leggja áherslu á útivist og nýta sér náttúru og leikvelli bæjarins. "
        "Hún vill að Mosfellsbær haldi áfram að vera „sveit í borg“ á komandi árum.\n\n"
        "Meðal helstu áhugamála Þóru eru hárgreiðsla, bakstur, útivist og samvera með fjölskyldu. "
        "Í pólitík nefnir hún Ólaf Inga Óskarsson sem fyrirmynd. Hún heldur upp á tónlistarmanninn "
        "Justin Bieber, nefnir bækur eftir Yrsu Sigurðardóttur og Arnald sem eftirlætislesefni og "
        "kvikmyndina The Proposal sem uppáhaldsmynd. Ef hún þyrfti að flytja úr Mosfellsbæ yrði "
        "Skagaströnd fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Þóra Sigrún Kjartansdóttir er hárgreiðslukona, fædd árið 1996 á Íslandi.",
         "ruv_quote": "Hárgreiðslukona / 1996 / Íslandi"},
        {"statement": "Hún hefur lokið sveinsprófi í sinni grein og hefur verið í Samfylkingunni í átta ár.",
         "ruv_quote": "Sveinsbréf / 8 ár"},
        {"statement": "Auk íslensku talar hún ensku.", "ruv_quote": "Ensku"},
        {"statement": "Þóra býr í íbúð í Mosfellsbæ.", "ruv_quote": "Íbúð"},
        {"statement": "Hún er tveggja barna móðir og hundamamma, og segir fjölskylduna leggja áherslu á útivist og nýta sér náttúru og leikvelli bæjarins.",
         "ruv_quote": "Hárgreiðslukona , 2 barna móðir og hunda mamma. Okkur fynst útivist mjög mikilvæg og nýtum náttúru og leikvelli bæjarins."},
        {"statement": "Hún vill að Mosfellsbær haldi áfram að vera „sveit í borg“ á komandi árum.",
         "ruv_quote": "Haldi áfram að vera sveit í borg."},
        {"statement": "Meðal helstu áhugamála Þóru eru hárgreiðsla, bakstur, útivist og samvera með fjölskyldu.",
         "ruv_quote": "Hárgreiðsla, baka, útivist og samveru með fjölskildu"},
        {"statement": "Í pólitík nefnir hún Ólaf Inga Óskarsson sem fyrirmynd.", "ruv_quote": "Ólafur Ingi Óskarsson"},
        {"statement": "Hún heldur upp á tónlistarmanninn Justin Bieber, nefnir bækur eftir Yrsu Sigurðardóttur og Arnald sem eftirlætislesefni og kvikmyndina The Proposal sem uppáhaldsmynd.",
         "ruv_quote": "Justin Bieber / Allar eftir Yrsu Sigurðardóttir eða Arnald / The Proposal"},
        {"statement": "Ef hún þyrfti að flytja úr Mosfellsbæ yrði Skagaströnd fyrir valinu.", "ruv_quote": "Skagaströnd"},
    ]
})

# 1: Magnús Hlynur Haraldsson (1604-S-11)
ENTRIES.append({
    "ruv_id": "1604-S-11",
    "new_bio": (
        "Magnús Hlynur Haraldsson er framhaldsskólakennari og hefur verið í Samfylkingunni í fjögur ár. "
        "Hann er fæddur árið 1975 á Íslandi, hefur lokið MS-námi og talar ensku auk íslensku. "
        "Hann býr í sérbýli í Mosfellsbæ.\n\n"
        "Magnús segir að við búum í samfélagi og að því fleirum sem gengur vel og líður vel, "
        "því betur gangi samfélagið fyrir alla. Hann vill að Mosfellsbær verði eftir tíu ár "
        "fullur af yndislegum nágrönnum.\n\n"
        "Golf er aðaláhugamál Magnúsar. Hann nefnir Foo Fighters sem uppáhaldshljómsveit, "
        "Hobbitann sem eftirlætisbók og True Lies sem þá kvikmynd sem hann heldur mest upp á. "
        "Í pólitík lítur hann til Stefáns J. Hafstein sem fyrirmyndar. Ef hann þyrfti að flytja "
        "úr Mosfellsbæ yrðu Vestmannaeyjar fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Magnús Hlynur Haraldsson er framhaldsskólakennari og hefur verið í Samfylkingunni í fjögur ár.",
         "ruv_quote": "Framhaldsskólakennari / 4 ár"},
        {"statement": "Hann er fæddur árið 1975 á Íslandi, hefur lokið MS-námi og talar ensku auk íslensku.",
         "ruv_quote": "1975 / Íslandi / Ensku / MS"},
        {"statement": "Hann býr í sérbýli í Mosfellsbæ.", "ruv_quote": "Sérbíli"},
        {"statement": "Magnús segir að við búum í samfélagi og að því fleirum sem gengur vel og líður vel, því betur gangi samfélagið fyrir alla.",
         "ruv_quote": "Við búum í samfélagi og því fleirum sem gengur vel og líður vel, því betur gengur samfélagið fyrir alla."},
        {"statement": "Hann vill að Mosfellsbær verði eftir tíu ár fullur af yndislegum nágrönnum.",
         "ruv_quote": "Fullt af yndislegum nágrönnum 😀"},
        {"statement": "Golf er aðaláhugamál Magnúsar.", "ruv_quote": "Golf"},
        {"statement": "Hann nefnir Foo Fighters sem uppáhaldshljómsveit, Hobbitann sem eftirlætisbók og True Lies sem þá kvikmynd sem hann heldur mest upp á.",
         "ruv_quote": "Foo fighters / Hobbitinn / True lies"},
        {"statement": "Í pólitík lítur hann til Stefáns J. Hafstein sem fyrirmyndar.", "ruv_quote": "Stefán J Hafstein"},
        {"statement": "Ef hann þyrfti að flytja úr Mosfellsbæ yrðu Vestmannaeyjar fyrir valinu.", "ruv_quote": "Vestmannaeyjar"},
    ]
})

# 2: Þyrnir Hálfdan Þyrnisson (1604-S-15)
ENTRIES.append({
    "ruv_id": "1604-S-15",
    "new_bio": (
        "Þyrnir Hálfdan Þyrnisson er 22 ára Mosfellingur, fæddur árið 2003 á Íslandi, og býður sig "
        "fram fyrir Samfylkinguna í Mosfellsbæ. Hann hefur verið í flokknum í rúmlega eitt ár. "
        "Þyrnir segist mikill áhugamaður um stjórnmál, tónlist og list, og á nokkur fjölskyldutengsl "
        "norður á land sem hann ferðaðist oft til þegar hann var lítill.\n\n"
        "Þyrnir starfar við þjónustu og sölu hjá Sýn, hefur lokið námi á framhaldsstigi og talar, "
        "auk íslensku, ensku og örlitla dönsku. Hann býr í sérbýli. Hann vill að Mosfellsbær verði "
        "eftir tíu ár blómstrandi náttúruperla þar sem allir geta fundið sinn stað.\n\n"
        "Aðaláhugamál Þyrnis eru stjórnmál. Sem fyrirmyndir í pólitík nefnir hann Antony Gramsci og "
        "Einar Olgeirsson. Uppáhaldstónlistarmaður hans er Pete Seeger, eftirlætisbókin Blood Meridian "
        "og uppáhaldskvikmyndin Englar alheimsins. Ef hann þyrfti að flytja úr Mosfellsbæ yrði Norðurþing "
        "fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Þyrnir Hálfdan Þyrnisson er 22 ára Mosfellingur, fæddur árið 2003 á Íslandi, og býður sig fram fyrir Samfylkinguna í Mosfellsbæ.",
         "ruv_quote": "Ég er Þyrnir Hálfdan Þyrnisson, 22 ára Mosfellingur / 2003 / Ísland."},
        {"statement": "Hann hefur verið í flokknum í rúmlega eitt ár.", "ruv_quote": "Rúmlega 1 ár."},
        {"statement": "Þyrnir segist mikill áhugamaður um stjórnmál, tónlist og list, og á nokkur fjölskyldutengsl norður á land sem hann ferðaðist oft til þegar hann var lítill.",
         "ruv_quote": "ég er mikill áhugamaður um stjórnmál, tónlist og list. Ég á nokkur fjölskyldutengsl að norðan sem ég ferðaðist oft til þegar ég var lítill."},
        {"statement": "Þyrnir starfar við þjónustu og sölu hjá Sýn, hefur lokið námi á framhaldsstigi og talar, auk íslensku, ensku og örlitla dönsku.",
         "ruv_quote": "Þjónustu og Sölu hjá Sýn. / Framhaldsstig. / Íslensku, Ensku, og örlitla Dönsku."},
        {"statement": "Hann býr í sérbýli.", "ruv_quote": "Sérbýli"},
        {"statement": "Hann vill að Mosfellsbær verði eftir tíu ár blómstrandi náttúruperla þar sem allir geta fundið sinn stað.",
         "ruv_quote": "Blómstrandi náttúruperla sem allir geta fundið sinn stað."},
        {"statement": "Aðaláhugamál Þyrnis eru stjórnmál.", "ruv_quote": "Stjórnmál."},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hann Antony Gramsci og Einar Olgeirsson.",
         "ruv_quote": "Antony Gramsci og Einar Olgeirsson."},
        {"statement": "Uppáhaldstónlistarmaður hans er Pete Seeger, eftirlætisbókin Blood Meridian og uppáhaldskvikmyndin Englar alheimsins.",
         "ruv_quote": "Pete Seeger. / Blood Meridian. / Englar Alheimsins."},
        {"statement": "Ef hann þyrfti að flytja úr Mosfellsbæ yrði Norðurþing fyrir valinu.", "ruv_quote": "Norðurþing."},
    ]
})

# 3: Sigurður Vopni Vatnsdal (3000-S-1)
ENTRIES.append({
    "ruv_id": "3000-S-1",
    "new_bio": (
        "Sigurður Vopni Vatnsdal er ráðgjafi hjá Sjóvá-Almennum tryggingum á Akranesi. "
        "Hann leiðir lista Samfylkingarinnar á Akranesi í sveitarstjórnarkosningum 2026 og er í "
        "fyrsta skipti á framboðslista flokksins á Akranesi. Sigurður er fæddur árið 1996 á Íslandi "
        "og hefur verið í Samfylkingunni í rúman áratug. Hann ólst upp á Vopnafirði og er jafnan "
        "kallaður Vopni. Hann flutti á Akranes árið 2023 og lýsir því sem einni þeirri bestu "
        "ákvörðun sem hann hafi tekið.\n\n"
        "Sigurður býr í fjölbýli á Akranesi með sambýliskonu sinni, Rögnu Dís, og syni þeirra, "
        "Birni Reyr, sem fæddist í október á síðasta ári. Hann talar ensku auk íslensku. "
        "Hann segist vilja samfélag þar sem barnafjölskyldur finni fyrir stuðningi, eldra fólk "
        "njóti virðingar og íþróttalífið blómstri, og að það eigi alltaf að vera markmiðið á Akranesi.\n\n"
        "Meðal helstu áhugamála Sigurðar eru ferðalög innanlands og utan, skotveiði og smíðavinna. "
        "Aðspurður um fyrirmynd í pólitík nefnir hann vini sína í pólitíkinni og Guðmund Árna sérstaklega. "
        "Hann nefnir Bubba Morthens og Herra hnetusmjör sem uppáhaldstónlistarmenn, og Hafdísi Huld þegar "
        "kemur að því að svæfa. Af kvikmyndum heldur hann mest upp á Pulp Fiction og Nýtt líf, og mælir "
        "einnig með teiknimyndinni Tangled með íslensku tali. Ef hann þyrfti að flytja úr Akranesi yrði "
        "Hvalfjarðarsveit fyrir valinu, þá bara rétt fyrir utan Akranes."
    ),
    "fact_check": [
        {"statement": "Sigurður er fæddur árið 1996 á Íslandi og hefur verið í Samfylkingunni í rúman áratug.",
         "ruv_quote": "1996 / Íslandi / 10+ ár"},
        {"statement": "Hann ólst upp á Vopnafirði og er jafnan kallaður Vopni.",
         "ruv_quote": "Ég heiti Sigurður Vopni, alltaf kallaður Vopni og já...Ég ólst upp á Vopnafirði."},
        {"statement": "Hann flutti á Akranes árið 2023 og lýsir því sem einni þeirri bestu ákvörðun sem hann hafi tekið.",
         "ruv_quote": "Ég flutti á Akranes árið 2023 og það er ein besta ákvörðun sem ég hef tekið"},
        {"statement": "Sigurður býr í fjölbýli á Akranesi með sambýliskonu sinni, Rögnu Dís, og syni þeirra, Birni Reyr, sem fæddist í október á síðasta ári.",
         "ruv_quote": "Fjölbýli / Sambýliskona mín heitir Ragna Dís ... Birnir Reyr sonur okkar fæddist í október á síðasta ári."},
        {"statement": "Hann talar ensku auk íslensku.", "ruv_quote": "Ensku"},
        {"statement": "Hann segist vilja samfélag þar sem barnafjölskyldur finni fyrir stuðningi, eldra fólk njóti virðingar og íþróttalífið blómstri, og að það eigi alltaf að vera markmiðið á Akranesi.",
         "ruv_quote": "Ég vill samfélag þar sem barnafjölskyldur finna fyrir stuðningi, eldra fólk nýtur virðingar og íþróttalífið blómstrar. Það á alltaf að vera markmiðið á Akranesi."},
        {"statement": "Meðal helstu áhugamála Sigurðar eru ferðalög innanlands og utan, skotveiði og smíðavinna.",
         "ruv_quote": "Ferðalög innanlands og utan, skotveiði og smíðavinna"},
        {"statement": "Aðspurður um fyrirmynd í pólitík nefnir hann vini sína í pólitíkinni og Guðmund Árna sérstaklega.",
         "ruv_quote": "Klárlega vinir mínir sem eru í pólitíkinni, En Guðmundur Árni hefur alltaf verið góð fyrirmynd."},
        {"statement": "Hann nefnir Bubba Morthens og Herra hnetusmjör sem uppáhaldstónlistarmenn, og Hafdísi Huld þegar kemur að því að svæfa.",
         "ruv_quote": "Bubbi Morthens og Herra hnetusmjör ... Hafdís Huld er auðvitað mikilvæg þegar það kemur að því að svæfa."},
        {"statement": "Af kvikmyndum heldur hann mest upp á Pulp Fiction og Nýtt líf, og mælir einnig með teiknimyndinni Tangled með íslensku tali.",
         "ruv_quote": "Mér datt fyrst í hug Pulp Fiction ... Nýtt líf er líka mjög ofarlega. Annars mæli ég með teiknimyndinni Tangled en hún er extra fyndin með íslensku tali"},
        {"statement": "Ef hann þyrfti að flytja úr Akranesi yrði Hvalfjarðarsveit fyrir valinu, þá bara rétt fyrir utan Akranes.",
         "ruv_quote": "Hvalfjarðarsveit? Þá bara rétt fyrir utan Akranes."},
    ]
})

# 4: Kristinn Hallur Sveinsson (3000-S-3)
ENTRIES.append({
    "ruv_id": "3000-S-3",
    "new_bio": (
        "Kristinn Hallur Sveinsson er bæjarfulltrúi fyrir Samfylkinguna á Akranesi á kjörtímabilinu "
        "2022–2026 og sérfræðingur hjá Loftmyndum ehf., sem sérhæfir sig í loftljósmyndun og kortagerð. "
        "Hann hefur einnig gegnt trúnaðarmannahlutverki í Heilbrigðisnefnd Vesturlands. Kristinn er "
        "fæddur árið 1972 á Íslandi og hefur búið á Akranesi frá níu ára aldri, fyrir utan háskólaárin "
        "í Reykjavík. Hann hefur tekið þátt í bæjarmálum frá árinu 2014 og verið í starfi Samfylkingarinnar "
        "frá stofnun flokksins árið 2000.\n\n"
        "Kristinn er giftur Margréti Rós Jósefsdóttur og eiga þau þrjá drengi á aldrinum 18 til 27 ára. "
        "Hann hefur lokið BSc-prófi frá Háskóla Íslands og kennsluréttindum á framhalds- og grunnskólastigi "
        "frá Háskólanum á Akureyri. Hann talar ensku auk íslensku og býr í parhúsi. Yngsti sonur hans er "
        "með talsverða fötlun vegna genagalla, og Kristinn segir þá reynslu veita dýrmæta innsýn í mikilvægi "
        "öflugrar þjónustu og réttlæti í samfélaginu.\n\n"
        "Í svörum sínum vill Kristinn að innviðauppbygging hafi fylgt þeirri fjölgun sem framundan er, að "
        "tryggð verði byggingarsvæði fyrir áframhaldandi stækkun, að gatna- og stígakerfi sé fyrsta flokks, "
        "að atvinnulífið blómstri og leik- og grunnskólar bæjarins verði áfram í fararbroddi á landsvísu. "
        "Hann segir þó mikilvægast að þjónusta sveitarfélagsins við íbúa sé áfram til fyrirmyndar. Pabbi "
        "hans er fyrirmynd hans í pólitík. Þegar tími gefst nýtur hann þess að ferðast, taka ljósmyndir, "
        "hlusta á tónlist, fylgjast með fótbolta og NFL og verja tíma með fjölskyldu og vinum. Meðal "
        "uppáhaldshljómsveita hans eru Sonic Youth, The Cure, Massive Attack, HAM og Purrkur Pillnikk, "
        "og af bókum nefnir hann Þrúgur reiðinnar, Sláturhús 5 og Sextíu kíló af sólskini. Af kvikmyndum "
        "heldur hann meðal annars upp á Star Wars: The Empire Strikes Back, LOTR: Return of the King, "
        "Office Space og Monty Python and the Holy Grail. Ef hann þyrfti að flytja úr Akranesi yrði "
        "Hafnarfjörður líklega fyrir valinu, þar sem hluti fjölskyldunnar býr."
    ),
    "fact_check": [
        {"statement": "Kristinn er fæddur árið 1972 á Íslandi og hefur búið á Akranesi frá níu ára aldri, fyrir utan háskólaárin í Reykjavík.",
         "ruv_quote": "1972 / Íslandi / Hef búið á Akranesi frá 9 ára aldri, fyrir utan háskólaárin í Reykjavík."},
        {"statement": "Hann hefur tekið þátt í bæjarmálum frá árinu 2014 og verið í starfi Samfylkingarinnar frá stofnun flokksins árið 2000.",
         "ruv_quote": "Ég hef tekið þátt í bæjarmálum frá því 2014 og í starfi Samfylkingarinnar frá stofnun. / Frá stofnun Samfylkingarinnar árið 2000."},
        {"statement": "Kristinn er giftur Margréti Rós Jósefsdóttur og eiga þau þrjá drengi á aldrinum 18 til 27 ára.",
         "ruv_quote": "giftur Margréti Rós Jósefsdóttur, við eigum 3 drengi á aldrinum 18-27 ára."},
        {"statement": "Hann hefur lokið BSc-prófi frá Háskóla Íslands og kennsluréttindum á framhalds- og grunnskólastigi frá Háskólanum á Akureyri.",
         "ruv_quote": "BSc. frá Háskóla Íslands og hef einnig lokið kennsluréttindum á framhalds- og grunnskólastigi frá Háskólanum á Akureyri."},
        {"statement": "Hann talar ensku auk íslensku og býr í parhúsi.",
         "ruv_quote": "Ensku / Parhúsi"},
        {"statement": "Yngsti sonur hans er með talsverða fötlun vegna genagalla, og Kristinn segir þá reynslu veita dýrmæta innsýn í mikilvægi öflugrar þjónustu og réttlæti í samfélaginu.",
         "ruv_quote": "Yngsti sonur okkar er með talsverða fötlun vegna genagalla. Sú reynsla veitir dýrmæta innsýn í mikilvægi öflugrar þjónustu og réttlæti í samfélaginu."},
        {"statement": "Í svörum sínum vill Kristinn að innviðauppbygging hafi fylgt þeirri fjölgun sem framundan er, að tryggð verði byggingarsvæði fyrir áframhaldandi stækkun, að gatna- og stígakerfi sé fyrsta flokks, að atvinnulífið blómstri og leik- og grunnskólar bæjarins verði áfram í fararbroddi á landsvísu.",
         "ruv_quote": "Ég vil að innviðauppbygging hafi fylgt þeirri fjölgun sem er framundan. Að við séum búin að tryggja þau byggingarsvæði sem sveitarfélagið þarf til áframhaldandi stækkunar. Að gatna- og stígakerfi sé fyrsta flokks. Að atvinnulífið blómstri ... Að leik- og grunnskólar bæjarins séu áfram í fararbroddi á landsvísu."},
        {"statement": "Hann segir þó mikilvægast að þjónusta sveitarfélagsins við íbúa sé áfram til fyrirmyndar.",
         "ruv_quote": "Það mikilvægasta er samt að þjónusta sveitarfélagsins við íbúa sé áfram til fyrirmyndar."},
        {"statement": "Pabbi hans er fyrirmynd hans í pólitík.", "ruv_quote": "Pabbi"},
        {"statement": "Þegar tími gefst nýtur hann þess að ferðast, taka ljósmyndir, hlusta á tónlist, fylgjast með fótbolta og NFL og verja tíma með fjölskyldu og vinum.",
         "ruv_quote": "þegar tími gefst nýt ég þess að ferðast, taka ljósmyndir, hlusta á tónlist, fylgjast með fótbolta og NFL og ekki síst að verja tíma með fjölskyldu og vinum."},
        {"statement": "Meðal uppáhaldshljómsveita hans eru Sonic Youth, The Cure, Massive Attack, HAM og Purrkur Pillnikk, og af bókum nefnir hann Þrúgur reiðinnar, Sláturhús 5 og Sextíu kíló af sólskini.",
         "ruv_quote": "Sonic Youth, The Cure, Massive Attack, HAM, Purrkur Pillnikk / Þrúgur reiðinnar / Sláturhús 5 / Sextíu kíló af sólskyni"},
        {"statement": "Af kvikmyndum heldur hann meðal annars upp á Star Wars: The Empire Strikes Back, LOTR: Return of the King, Office Space og Monty Python and the Holy Grail.",
         "ruv_quote": "Star War The Empire Strikes Back / LOTR Return Of The King / Office Space / Monty Python and the Holy Grail"},
        {"statement": "Ef hann þyrfti að flytja úr Akranesi yrði Hafnarfjörður líklega fyrir valinu, þar sem hluti fjölskyldunnar býr.",
         "ruv_quote": "Sennilega Hafnarfjörð, þar sem hluti af fjölskyldunni býr."},
    ]
})

# 5: Jón Hjörvar Valgarðsson (3000-S-5)
ENTRIES.append({
    "ruv_id": "3000-S-5",
    "new_bio": (
        "Jón Hjörvar Valgarðsson er forstöðumaður Arnardals á Akranesi og háskólanemi við Háskóla "
        "Íslands. Hann var kjörinn formaður Snæfríðar, ungra félaga Samfylkingarinnar á Akranesi, "
        "árið 2021, og segist hafa verið virkur í starfi ungs jafnaðarfólks frá 2016. Jón Hjörvar "
        "er fæddur árið 1998 á Íslandi, talar góða ensku og getur reddað sér á dönsku. Hann býr "
        "í tveggja herbergja íbúð í fjölbýli og er í námi við Háskóla Íslands.\n\n"
        "Hann vill að íbúafjöldinn á Akranesi verði meiri eftir tíu ár, að nýr leikskóli verði "
        "kominn á neðri skaga, ásamt ungbarnaleikskóla, og að uppbygging nýs grunnskóla verði "
        "hafin. Hann vill jafnframt sjá öflugt og fjölbreytt atvinnulíf á Akranesi og í Flóahverfi, "
        "og að bærinn verði áfram í fremstu röð þegar kemur að rekstri sveitarfélagsins, íþrótta- "
        "og tómstundamálum barna og þjónustu við íbúa. Ef hann þyrfti að flytja úr Akranesi yrði "
        "Kaupmannahöfn eða annars staðar í Danmörku líklegast fyrir valinu, en hann segir að hann "
        "vilji hvergi annars staðar vera en á Akranesi.\n\n"
        "Áhugamál Jóns Hjörvars eru útivist, björgunarsveitarstarf og ferðalög innanlands og erlendis. "
        "Í pólitík nefnir hann að Olof Palme hafi vakið áhuga hans á stjórnmálum og að Jens Stoltenberg "
        "hafi gert góða hluti, og á Íslandi nefnir hann Loga Einarsson og Kristrúnu Frostadóttur. "
        "Tinnabækurnar eru í miklu uppáhaldi hjá honum, kvikmyndin Ferris Bueller's Day Off hefur "
        "lengi verið í uppáhaldi, og tónlistarsmekkurinn nær frá Herra Hnetusmjör til Gaddavírs, þótt "
        "country og hljómsveitin The Red Clay Strays séu á repeat þessa dagana."
    ),
    "fact_check": [
        {"statement": "Hann segist hafa verið virkur í starfi ungs jafnaðarfólks frá 2016.",
         "ruv_quote": "Ég hef verið virkur í starfi ungs jafnaðarfólks síðan 2016"},
        {"statement": "Jón Hjörvar er fæddur árið 1998 á Íslandi, talar góða ensku og getur reddað sér á dönsku.",
         "ruv_quote": "1998 / Íslandi / Tala góða ensku og redda mér á dönsku"},
        {"statement": "Hann býr í tveggja herbergja íbúð í fjölbýli og er í námi við Háskóla Íslands.",
         "ruv_quote": "Tveggja herbergja íbúð í fjölbýli / Er í námi við Háskóla Íslands"},
        {"statement": "Hann vill að íbúafjöldinn á Akranesi verði meiri eftir tíu ár, að nýr leikskóli verði kominn á neðri skaga, ásamt ungbarnaleikskóla, og að uppbygging nýs grunnskóla verði hafin.",
         "ruv_quote": "Íbúafjöldi meiri, kominn nýr leikskóli á neðri skaga og ungbarnaleikskóli, uppbygging á nýjum grunnskóla hafin"},
        {"statement": "Hann vill jafnframt sjá öflugt og fjölbreytt atvinnulíf á Akranesi og í Flóahverfi, og að bærinn verði áfram í fremstu röð þegar kemur að rekstri sveitarfélagsins, íþrótta- og tómstundamálum barna og þjónustu við íbúa.",
         "ruv_quote": "öflugt og fjölbreytt atvinnulíf á Akranesi og Flóahverfi. Bærinn verður enn í fremstu röð þegar kemur að rekstri sveitarfélagsins, íþrótta-og tómstundamálum barna og þjónustu við íbúa."},
        {"statement": "Ef hann þyrfti að flytja úr Akranesi yrði Kaupmannahöfn eða annars staðar í Danmörku líklegast fyrir valinu, en hann segir að hann vilji hvergi annars staðar vera en á Akranesi.",
         "ruv_quote": "Líklegast Kaupmannahöfn eða annarsstaðar í Danmörku. Vil hvergi annarstaðar vera en á Akranesi."},
        {"statement": "Áhugamál Jóns Hjörvars eru útivist, björgunarsveitarstarf og ferðalög innanlands og erlendis.",
         "ruv_quote": "Útivist, björgunarsveitar starf og ferðast bæði innanlands og erlendis"},
        {"statement": "Í pólitík nefnir hann að Olof Palme hafi vakið áhuga hans á stjórnmálum og að Jens Stoltenberg hafi gert góða hluti, og á Íslandi nefnir hann Loga Einarsson og Kristrúnu Frostadóttur.",
         "ruv_quote": "Olof Palmer byrjaði áhuga minn á stjórnmálum og Jens Stoltenberg hefur gert góða hluti. Á Íslandi eru það Logi Einars og Kristrún Frosta"},
        {"statement": "Tinnabækurnar eru í miklu uppáhaldi hjá honum, kvikmyndin Ferris Bueller's Day Off hefur lengi verið í uppáhaldi, og tónlistarsmekkurinn nær frá Herra Hnetusmjör til Gaddavírs, þótt country og hljómsveitin The Red Clay Strays séu á repeat þessa dagana.",
         "ruv_quote": "Tinna bækurnar eru í miklu uppáhaldi / Ferris Bueller's day off hefur lengi verið í uppáhaldi / Er í öllum senum frá Herra Hnetusmjör að Gaddavír! En þessa dagana er það country og the red clay strays á repeat."},
    ]
})

# 6: Þóranna Hildur Kjartansdóttir (3000-S-8)
ENTRIES.append({
    "ruv_id": "3000-S-8",
    "new_bio": (
        "Þóranna Hildur Kjartansdóttir er sjúkraliði og skipar 8. sæti á lista Samfylkingarinnar "
        "á Akranesi fyrir sveitarstjórnarkosningarnar 16. maí 2026. Hún situr sem varamaður í stjórn "
        "Heilbrigðisnefndar Vesturlands fyrir hönd Samfylkingarinnar. Þóranna er fædd árið 1973 á "
        "Íslandi og hefur búið á Akranesi í 49 ár. Hún starfar sem sjúkraliði á B-deild HVE á "
        "Akranesi, hefur lokið námi sem lyfjatæknir og sjúkraliði, og hefur verið í Samfylkingunni "
        "frá stofnun flokksins. Hún talar ensku auk íslensku og býr í raðhúsi.\n\n"
        "Þóranna á þrjú uppkomin börn og hefur verið í Kór Akraneskirkju í 26 ár. Hún elskar útivist, "
        "ferðalög, göngur, heitar og kaldar laugar, golf, bækur og tónlist af öllu tagi. Hún vill "
        "að Akranes verði eftir tíu ár barnvænt sveitarfélag þar sem vel sé búið að öldruðum, með "
        "nægu framboði húsnæðis og atvinnutækifæra, öflugri ferðaþjónustu og að bærinn verði "
        "sannkallaður íþrótta- og heilsubær.\n\n"
        "Aðaláhugamál Þórönnu eru golf og söngur, og að vera með skemmtilegu fólki. Sem fyrirmyndir "
        "í pólitík nefnir hún Kristrúnu Frostadóttur og Regínu Ástvaldsdóttur. Hún heldur upp á "
        "Queen, Pink og Teddy Swims, eftirlætisbókin er Rosie verkefnið og uppáhaldskvikmyndin "
        "Shawshank Redemption. Ef hún þyrfti að flytja úr Akranesi yrði Mosfellsbær fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Þóranna er fædd árið 1973 á Íslandi og hefur búið á Akranesi í 49 ár.",
         "ruv_quote": "1973 / Íslandi / Ég hef búið á Akranesi í 49 ár."},
        {"statement": "Hún starfar sem sjúkraliði á B-deild HVE á Akranesi, hefur lokið námi sem lyfjatæknir og sjúkraliði, og hefur verið í Samfylkingunni frá stofnun flokksins.",
         "ruv_quote": "Sjúkraliði á B deild HVE hérna á Akranesi / Lyfjatæknir og Sjúkraliði / Síðan hann var stofnaður"},
        {"statement": "Hún talar ensku auk íslensku og býr í raðhúsi.",
         "ruv_quote": "Ensku / Raðhúsi"},
        {"statement": "Þóranna á þrjú uppkomin börn og hefur verið í Kór Akraneskirkju í 26 ár.",
         "ruv_quote": "á 3 uppkomin börn / Hef verið í Kór Akraneskirkju í 26 ár"},
        {"statement": "Hún elskar útivist, ferðalög, göngur, heitar og kaldar laugar, golf, bækur og tónlist af öllu tagi.",
         "ruv_quote": "Elska útivist ferðalög ,göngur ,heitar og kaldar laugar, golf, bækur og tónlist af öllu tagi."},
        {"statement": "Hún vill að Akranes verði eftir tíu ár barnvænt sveitarfélag þar sem vel sé búið að öldruðum, með nægu framboði húsnæðis og atvinnutækifæra, öflugri ferðaþjónustu og að bærinn verði sannkallaður íþrótta- og heilsubær.",
         "ruv_quote": "Barnvænt og að vel sé búið að öldruðum. Nægt framboð af húsnæði og atvinnutækifærum. Að ferðaþjónusta verði öflugri og að við verðum sannkallaður íþrótta og heilsubær"},
        {"statement": "Aðaláhugamál Þórönnu eru golf og söngur, og að vera með skemmtilegu fólki.",
         "ruv_quote": "Golf og söngur og að vera með skemmtilegu fólki"},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hún Kristrúnu Frostadóttur og Regínu Ástvaldsdóttur.",
         "ruv_quote": "Kristrún Frostadóttir / Regína Ástvaldsd"},
        {"statement": "Hún heldur upp á Queen, Pink og Teddy Swims, eftirlætisbókin er Rosie verkefnið og uppáhaldskvikmyndin Shawshank Redemption.",
         "ruv_quote": "Queen Pink Teddy Swims / Rosie verkefnið / Shawshank Redemtion"},
        {"statement": "Ef hún þyrfti að flytja úr Akranesi yrði Mosfellsbær fyrir valinu.",
         "ruv_quote": "Mosfellsbær"},
    ]
})

# 7: Gunnþórunn Valsdóttir (3000-S-9)
ENTRIES.append({
    "ruv_id": "3000-S-9",
    "new_bio": (
        "Gunnþórunn Valsdóttir er leikskólakennari og skipar 9. sæti á lista Samfylkingarinnar á "
        "Akranesi fyrir sveitarstjórnarkosningarnar 16. maí 2026. Hún hefur tjáð sig opinberlega "
        "um leikskólamál á Akranesi og birti aðsenda grein í apríl 2026 um öryggi og gæði í "
        "leikskólum, þar sem hún benti á þróun í barnafjölda á starfsmann í nágrannasveitarfélögum.\n\n"
        "Gunnþórunn er fædd árið 1991 á Íslandi og starfar sem leikskólakennari og deildarstjóri "
        "í Teigaseli. Hún hefur lokið MT-gráðu í menntunarfræði leikskóla og hefur verið í "
        "Samfylkingunni síðan um 2009. Hún er gift Gísla og saman eiga þau þrjá drengi á aldrinum "
        "fimm til ellefu ára. Hún segist elska vinnuna sína. Hún talar ensku og dreymir um að "
        "verða góð í dönsku, bara upp á stemmninguna. Hún býr í raðhúsi.\n\n"
        "Gunnþórunn vill að Akranes verði sá staður þar sem öll vilji búa og að bærinn verði "
        "fjölskyldubær fyrir allskonar fjölskyldur. Hún vill öfluga leik- og grunnskóla með "
        "kennara í fremstu röð, og að fatlaðir einstaklingar finni að þeir tilheyri og fái þá "
        "þjónustu sem þeir þurfa. Sem fyrirmynd í pólitík nefnir hún Guðbjart Hannesson, sem hafði "
        "mikil áhrif á hana á unglingsárunum og var, að hennar sögn, rólegur, yfirvegaður, góður "
        "og traustur, og alvöru jafnaðarmaður.\n\n"
        "Helstu áhugamál hennar eru samvera með fjölskyldu og vinum, fótbolti (bæði fótboltamót sem "
        "börnin taka þátt í og ÍA í bestu deildinni), ferðalög innanlands og utan, og að spila á "
        "fiðlu með hljómsveitinni sinni Slitnum strengjum. Hún hlustar mest á Laufey þessa dagana "
        "og nefnir einnig hljómsveitina sína Slitna Strengi. Bókin Ríkisfang ekkert hafði mikil "
        "áhrif á hana, en Harry Potter-bækurnar eru kannski uppáhaldsbækurnar. Hún elskar svona "
        "týpískar stelpumyndir og getur horft aftur og aftur á Bridget Jones, og The Greatest "
        "Showman kemur sterk inn. Ef hún þyrfti að flytja úr Akranesi yrði Akureyri sennilega fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Gunnþórunn er fædd árið 1991 á Íslandi og starfar sem leikskólakennari og deildarstjóri í Teigaseli.",
         "ruv_quote": "1991 / Íslandi / Leikskólakennari - deildarstjóri í Teigaseli"},
        {"statement": "Hún hefur lokið MT-gráðu í menntunarfræði leikskóla og hefur verið í Samfylkingunni síðan um 2009.",
         "ruv_quote": "MT-gráða í menntunarfræði leikskóla / Lengi - síðan sirka 2009"},
        {"statement": "Hún er gift Gísla og saman eiga þau þrjá drengi á aldrinum fimm til ellefu ára.",
         "ruv_quote": "gift Gísla og saman eigum við þrjá drengi á aldrinum 5-11 ára."},
        {"statement": "Hún segist elska vinnuna sína.",
         "ruv_quote": "Ég er leikskólakennari og elska vinnuna mína."},
        {"statement": "Hún talar ensku og dreymir um að verða góð í dönsku, bara upp á stemmninguna.",
         "ruv_quote": "Ég get talað ensku. En draumurinn er að vera góð í dönsku - bara uppá stemmninguna."},
        {"statement": "Hún býr í raðhúsi.", "ruv_quote": "Raðhúsi"},
        {"statement": "Gunnþórunn vill að Akranes verði sá staður þar sem öll vilji búa og að bærinn verði fjölskyldubær fyrir allskonar fjölskyldur.",
         "ruv_quote": "Ég vil að að Akranes verði sá staður þar sem öll vilja búa á. Að bærinn okkar verði fjölskyldu bær fyrir allskonar fjölskyldur"},
        {"statement": "Hún vill öfluga leik- og grunnskóla með kennara í fremstu röð, og að fatlaðir einstaklingar finni að þeir tilheyri og fái þá þjónustu sem þeir þurfa.",
         "ruv_quote": "Ég vil öfluga leik- og grunnskóla, með kennara í fremstu röð. Fatlaðir einstaklingar eiga að finna að þeir tilheyri og séu hluti af samfélaginu, og þeir eiga að fá þá þjónustu sem að þeir þurfa hverju sinni."},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Guðbjart Hannesson, sem hafði mikil áhrif á hana á unglingsárunum og var, að hennar sögn, rólegur, yfirvegaður, góður og traustur, og alvöru jafnaðarmaður.",
         "ruv_quote": "Guðbjartur Hannesson hafði mikil áhrif á mig þegar ég var unglingur ... Hann var allt sem ég myndi vilja vera, rólegur, yfirvegaður, góður og traustur. Alvöru jafnaðarmaður."},
        {"statement": "Helstu áhugamál hennar eru samvera með fjölskyldu og vinum, fótbolti (bæði fótboltamót sem börnin taka þátt í og ÍA í bestu deildinni), ferðalög innanlands og utan, og að spila á fiðlu með hljómsveitinni sinni Slitnum strengjum.",
         "ruv_quote": "Samvera með fjölskyldu og vinum. Fótbolti (fótboltamót sem börnin taka þátt í og ÍA í bestu deildinni) Ferðalög, innan- og utanlands. Svo finnst mér ótrúlega gaman að spila á fiðluna mína með hljómsveitinni minni Slitnum strengjum."},
        {"statement": "Hún hlustar mest á Laufey þessa dagana og nefnir einnig hljómsveitina sína Slitna Strengi.",
         "ruv_quote": "þessa dagana hlusta ég mest á Laufeyju. Svo verð ég að nefna hljómsveitina mína Slitna Strengi"},
        {"statement": "Bókin Ríkisfang ekkert hafði mikil áhrif á hana, en Harry Potter-bækurnar eru kannski uppáhaldsbækurnar.",
         "ruv_quote": "“Ríkisfang ekkert” hafði mjög mikil áhrif á mig ... en Harry Potter bækurnar eru kannski frekar uppáhalds bækurnar mínar."},
        {"statement": "Hún elskar svona týpískar stelpumyndir og getur horft aftur og aftur á Bridget Jones, og The Greatest Showman kemur sterk inn.",
         "ruv_quote": "Ég elska svona týpískar stelpumyndir og get horft aftur og aftur á Bridget Jones. The Greatest showman kemur líka sterk inn"},
        {"statement": "Ef hún þyrfti að flytja úr Akranesi yrði Akureyri sennilega fyrir valinu.",
         "ruv_quote": "Það yrði sennilega Akureyri"},
    ]
})

# 8: Elvar Sigurjónsson (3000-S-14)
ENTRIES.append({
    "ruv_id": "3000-S-14",
    "new_bio": (
        "Elvar Sigurjónsson er frambjóðandi Samfylkingarinnar á Akranesi og skipar 14. sæti á lista "
        "flokksins. Hann er fæddur árið 1996 á Íslandi, hefur lokið stúdentsprófi og starfar sem "
        "starfsmaður Ölgerðarinnar. Hann hefur verið flokksbundinn í Samfylkingunni í þrjú ár en "
        "segist alla tíð hafa verið jafnaðarmaður, og býður sig fram því hann vill leggja sitt af "
        "mörkum fyrir samfélag þar sem jöfnuður er í fyrirrúmi. Auk íslensku talar hann ensku, "
        "sænsku og þýsku, og segist vilja trúa því að hann tali dönsku. Hann býr í blokkaríbúð á "
        "annarri hæð.\n\n"
        "Elvar vill að áfram verði haldið því frábæra starfi sem unnið hefur verið í grunn- og "
        "leikskólunum á Akranesi. Hann vonast til að skammtímadvöl fatlaðra og samfélagsmiðstöð "
        "verði risin, að uppbygging á Jaðarsbökkum verði kláruð með nýrri 50 metra innisundlaug, "
        "og að aðalvöllur knattspyrnufélagsins verði kominn á gervigras.\n\n"
        "Aðaláhugamál Elvars eru íþróttir. Hann spilaði körfubolta með meistaraflokki ÍA nokkur "
        "tímabil en stundar nú áhugabolta, og mætir á helst alla viðburði ÍA hjá karla- og "
        "kvennaflokki ef tíminn leyfir. Sem fyrirmynd í pólitík nefnir hann Bernie Sanders, og "
        "tekur fram að aldrei eigi að gefast upp sama hvað verkefnið virðist óyfirstíganlegt. "
        "Green Day eru í uppáhaldi, Söngur íss og elda eftir George R.R. Martin er stórkostleg "
        "og Dune-bækurnar eftir Frank Herbert veita henni samkeppni. Hann hefur sett Star Wars "
        "Episode V ótal sinnum í gang síðan hann náði í Disney+. Ef hann þyrfti að flytja úr "
        "Akranesi yrði Krosslandið í Hvalfjarðarsveit fyrir valinu, enda stutt heim."
    ),
    "fact_check": [
        {"statement": "Hann er fæddur árið 1996 á Íslandi, hefur lokið stúdentsprófi og starfar sem starfsmaður Ölgerðarinnar.",
         "ruv_quote": "1996 / Íslandi / Stúdent / Starfsmaður ölgerðarinnar"},
        {"statement": "Hann hefur verið flokksbundinn í Samfylkingunni í þrjú ár en segist alla tíð hafa verið jafnaðarmaður, og býður sig fram því hann vill leggja sitt af mörkum fyrir samfélag þar sem jöfnuður er í fyrirrúmi.",
         "ruv_quote": "3 ár flokksbundinn en alla tíð verið jafnaðarmaður / Ég bauð mig fram því að ég vil leggja mitt af mörkum fyrir samfélag þar sem jöfnuður er í fyrirrúmi."},
        {"statement": "Auk íslensku talar hann ensku, sænsku og þýsku, og segist vilja trúa því að hann tali dönsku.",
         "ruv_quote": "Enska / Sænska / Þýska / Langar að trúa því að ég tali dönsku"},
        {"statement": "Hann býr í blokkaríbúð á annarri hæð.", "ruv_quote": "Blokkar íbúð á 2.hæð"},
        {"statement": "Elvar vill að áfram verði haldið því frábæra starfi sem unnið hefur verið í grunn- og leikskólunum á Akranesi.",
         "ruv_quote": "Ég vil að við höldum áfram því frábæra starfi sem hefur verið unnið í grunn og leikskólunum hér á akranesi"},
        {"statement": "Hann vonast til að skammtímadvöl fatlaðra og samfélagsmiðstöð verði risin, að uppbygging á Jaðarsbökkum verði kláruð með nýrri 50 metra innisundlaug, og að aðalvöllur knattspyrnufélagsins verði kominn á gervigras.",
         "ruv_quote": "vonast ég til að skammtímadvöl fatlaðra og samfélagsmiðstöð verði risin. Uppbyggingin á Jaðarsbökkum verði lokið með nýja 50 metra innisundlaug bætt við svæðið og aðalvöllur knattspyrnufélagsins kominn á gervigras."},
        {"statement": "Aðaláhugamál Elvars eru íþróttir. Hann spilaði körfubolta með meistaraflokki ÍA nokkur tímabil en stundar nú áhugabolta, og mætir á helst alla viðburði ÍA hjá karla- og kvennaflokki ef tíminn leyfir.",
         "ruv_quote": "Íþróttir, ég spilaði körfubolta með meistaraflokki ÍA nokkur tímabil en stunda nú bara áhugabolta. Mæti á helst alla viðburði ÍA í karla og kvennaflokk ef tíminn leyfir."},
        {"statement": "Sem fyrirmynd í pólitík nefnir hann Bernie Sanders, og tekur fram að aldrei eigi að gefast upp sama hvað verkefnið virðist óyfirstíganlegt.",
         "ruv_quote": "Bernie Sanders er alvöru fyrirmynd, Aldrei gefast upp sama hvað verkefnið virðist óyfirstíganlegt."},
        {"statement": "Green Day eru í uppáhaldi, Söngur íss og elda eftir George R.R. Martin er stórkostleg og Dune-bækurnar eftir Frank Herbert veita henni samkeppni.",
         "ruv_quote": "Green Day hafa ekki klikkað ennþá fyrir mér / Söngur ís og elda serían hjá George R.R. Martin er stórkostleg / Dune og Dune Messiah eftir Frank Herbert veita alvöru samkeppni"},
        {"statement": "Hann hefur sett Star Wars Episode V ótal sinnum í gang síðan hann náði í Disney+.",
         "ruv_quote": "Ég get ekki talið hversu oft ég hef sett Star Wars Episode V í gang síðan ég náði í disney+."},
        {"statement": "Ef hann þyrfti að flytja úr Akranesi yrði Krosslandið í Hvalfjarðarsveit fyrir valinu, enda stutt heim.",
         "ruv_quote": "Krosslandið í hvalfjarðarsveit, stutt heim."},
    ]
})

# 9: Valgarður Lyngdal Jónsson (3000-S-18)
ENTRIES.append({
    "ruv_id": "3000-S-18",
    "new_bio": (
        "Valgarður Lyngdal Jónsson hefur verið bæjarfulltrúi fyrir Samfylkinguna á Akranesi síðustu "
        "tólf ár og oddviti listans síðustu tvö kjörtímabil. Hann skipar nú 18. sæti listans, sem er "
        "heiðurssæti hans. Valgarður er fæddur árið 1972 á Íslandi, starfar sem kennari og hefur "
        "lokið meistaraprófi frá háskóla. Hann talar ensku auk íslensku, hefur verið í Samfylkingunni "
        "í 25 ár og býr í einbýli.\n\n"
        "Valgarður vill að Akranes verði eftir tíu ár ennþá líflegra, skemmtilegra og fjölskylduvænna "
        "en í dag. Sem fyrirmyndir í pólitík nefnir hann marga góða og sterka sósíaldemókrata, en "
        "Olof Palme kemur fyrstur upp í hugann.\n\n"
        "Áhugamál Valgarðs eru útivist, ferðalög og samvera með fjölskyldunni. Eftirlætisbók hans "
        "er Sturlunga, sérstaklega Íslendinga saga Sturlu Þórðarsonar, og uppáhaldskvikmyndin Englar "
        "alheimsins. Hann nefnir The Beatles, The Pixies, Nick Cave og Tom Waits sem uppáhaldstónlist. "
        "Ef hann þyrfti að flytja úr Akranesi yrði Hvalfjarðarsveit fyrir valinu, en hann er alinn upp "
        "þar og segir heimtaugina sterka."
    ),
    "fact_check": [
        {"statement": "Valgarður er fæddur árið 1972 á Íslandi, starfar sem kennari og hefur lokið meistaraprófi frá háskóla.",
         "ruv_quote": "1972 / Ísland / Kennari / Meistarapróf frá háskóla"},
        {"statement": "Hann talar ensku auk íslensku, hefur verið í Samfylkingunni í 25 ár og býr í einbýli.",
         "ruv_quote": "Enska / 25 ár / Einbýli"},
        {"statement": "Valgarður vill að Akranes verði eftir tíu ár ennþá líflegra, skemmtilegra og fjölskylduvænna en í dag.",
         "ruv_quote": "Ennþá líflegra, skemmtilegra og fjölskylduvænna en í dag."},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hann marga góða og sterka sósíaldemókrata, en Olof Palme kemur fyrstur upp í hugann.",
         "ruv_quote": "Margir góðir og sterkir sósíaldemókratar. Olof Palme kemur fyrstur upp í hugann."},
        {"statement": "Áhugamál Valgarðs eru útivist, ferðalög og samvera með fjölskyldunni.",
         "ruv_quote": "Útivist, ferðalög og samvera með fjölskyldunni."},
        {"statement": "Eftirlætisbók hans er Sturlunga, sérstaklega Íslendinga saga Sturlu Þórðarsonar, og uppáhaldskvikmyndin Englar alheimsins.",
         "ruv_quote": "Sturlunga - sér í lagi Íslendinga saga Sturlu Þórðarsonar. / Engla Alheimsins"},
        {"statement": "Hann nefnir The Beatles, The Pixies, Nick Cave og Tom Waits sem uppáhaldstónlist.",
         "ruv_quote": "The Beatles, The Pixies, Nick Cave og Tom Waits."},
        {"statement": "Ef hann þyrfti að flytja úr Akranesi yrði Hvalfjarðarsveit fyrir valinu, en hann er alinn upp þar og segir heimtaugina sterka.",
         "ruv_quote": "Hvalfjarðarsveit - er alinn upp þar og heimtaugin er sterk."},
    ]
})

# 10: Svanfríður G. Bergvinsdóttir (4200-S-1)
ENTRIES.append({
    "ruv_id": "4200-S-1",
    "new_bio": (
        "Svanfríður Guðrún Bergvinsdóttir er viðskiptafræðinemi og formaður ASÍ-UNG, og leiðir "
        "S-listann (Samfylkingin) í Ísafjarðarbæ í sveitarstjórnarkosningum 2026. Þetta er í fyrsta "
        "skipti í 24 ár sem Samfylkingin keppir undir eigin merki í sveitarfélaginu. Hún er fædd "
        "árið 1994 á Íslandi, 32 ára, tveggja barna móðir og eiginkona, búsett í Hnífsdal í einbýlishúsi.\n\n"
        "Svanfríður hefur lokið stúdentsprófi, talar ensku auk íslensku og hefur verið í Samfylkingunni "
        "í eitt og hálft ár, eftir að hafa áður verið óflokksbundin. Hún vill að Ísafjarðarbær verði "
        "fjölbreytt og lifandi sveitarfélag.\n\n"
        "Sem fyrirmynd í pólitík nefnir hún Kristrúnu Frostadóttur. Helstu áhugamál hennar eru "
        "hreyfing, prjónaskapur og að læra nýja hluti. Hún hlustar mest á Alex Warren þessa dagana. "
        "Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Selfoss fyrir valinu, þar sem hún á fjölskyldu, "
        "svo hún þyrfti ekki að fara beint inn í borgina."
    ),
    "fact_check": [
        {"statement": "Hún er fædd árið 1994 á Íslandi, 32 ára, tveggja barna móðir og eiginkona, búsett í Hnífsdal í einbýlishúsi.",
         "ruv_quote": "Ég er 32 ára, tveggja barna móðir og eiginkona, búsett í Hnífsdal. / 1994 / Íslandi / Einbýlishúsi"},
        {"statement": "Svanfríður hefur lokið stúdentsprófi, talar ensku auk íslensku og hefur verið í Samfylkingunni í eitt og hálft ár, eftir að hafa áður verið óflokksbundin.",
         "ruv_quote": "Stúdentspróf / Ensku / 1,5 ár. Óflokksbundin allt fram að því."},
        {"statement": "Hún vill að Ísafjarðarbær verði fjölbreytt og lifandi sveitarfélag.",
         "ruv_quote": "Ég vil að sveitarfélagið sé fjölbreytt og lifandi."},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Kristrúnu Frostadóttur.", "ruv_quote": "Kristrún Frostadóttir"},
        {"statement": "Helstu áhugamál hennar eru hreyfing, prjónaskapur og að læra nýja hluti.",
         "ruv_quote": "Hreyfing, prjónaskapur og að læra nýja hluti."},
        {"statement": "Hún hlustar mest á Alex Warren þessa dagana.",
         "ruv_quote": "Þessa dagana er það Alex Warren"},
        {"statement": "Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Selfoss fyrir valinu, þar sem hún á fjölskyldu, svo hún þyrfti ekki að fara beint inn í borgina.",
         "ruv_quote": "Selfoss, ég á fjölskyldu þar og ég þyrfti ekki að fara beint inn í borgina (þar sem restin af fjölskyldunni er)"},
    ]
})

# 11: Finney Rakel Árnadóttir (4200-S-3)
ENTRIES.append({
    "ruv_id": "4200-S-3",
    "new_bio": (
        "Finney Rakel Árnadóttir er aðstoðarskólastjóri og hefur ritað fjölda greina á heimasíðu "
        "Tónlistarskóla Ísafjarðar. Hún skipar 3. sæti á framboðslista Samfylkingarinnar í Ísafjarðarbæ "
        "í sveitarstjórnarkosningunum 2026. Finney er fædd árið 1983 á Íslandi, hefur lokið "
        "háskólamenntun og starfar sem aðstoðarskólastjóri Tónlistarskóla Ísafjarðar. Hún hefur verið "
        "í Samfylkingunni í fjögur ár og talar ensku, dönsku, sænsku og þýsku auk íslensku. Hún býr "
        "í eigin húsnæði.\n\n"
        "Finney segist Vestfirðingur í húð og hár. Hún ólst upp á Suðureyri með rætur til Aðalvíkur, "
        "foreldrar hennar fluttu suður árið 1990, en hún hefur alltaf haft sterkar taugar vestur og "
        "vildi ala börnin sín upp þar. Hún hefur búið á Vestfjörðum í tólf ár. Börnin eru þrjú á "
        "aldrinum 16, 12 og 10 ára, og hún á tryggan vin í hundinum sínum Seif sem er fimm ára og sér "
        "um að viðra hana á hverjum degi. Hún hefur mikinn áhuga á samfélaginu og fólki og þörf fyrir "
        "að leggja sitt af mörkum, og finnst gott að syngja og ganga um fjöll og firnindi.\n\n"
        "Finney vill að í Ísafjarðarbæ verði skapandi og gott atvinnulíf, framboð af húsnæði og góðir "
        "og traustir innviðir. Hún vill að mynd sé komin á bæjarskipulagið, með nýjum og skemmtilegum "
        "miðbæ, viðhald sé sinnt í öllum kjörnum og skólastarf í blóma. Þá vill hún að þar verði "
        "starfrækt öflug menningarmiðstöð og að almenningssamgöngur milli kjarna séu virkar svo fólk "
        "njóti góðs af, sama hvar það býr. Helstu áhugamál hennar eru tónlist, sjálfsrækt og göngur. "
        "Hún á enga sérstaka fyrirmynd í pólitík, en lítur til þeirra sem ná til fólksins og gefa af "
        "sér. Radiohead er í uppáhaldi, og af kvikmyndum nefnir hún Star Wars-myndirnar og LOTR. "
        "Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Selfoss eflaust fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Finney er fædd árið 1983 á Íslandi, hefur lokið háskólamenntun og starfar sem aðstoðarskólastjóri Tónlistarskóla Ísafjarðar.",
         "ruv_quote": "1983 / Íslandi / Háskólamenntun / Aðstoðarskólastjóri Tónlistarskóla Ísafjarðar."},
        {"statement": "Hún hefur verið í Samfylkingunni í fjögur ár og talar ensku, dönsku, sænsku og þýsku auk íslensku.",
         "ruv_quote": "4 ár. / Ensku, dönsku, sænsku, þýsku."},
        {"statement": "Hún býr í eigin húsnæði.", "ruv_quote": "Eigin húsnæði."},
        {"statement": "Finney segist Vestfirðingur í húð og hár. Hún ólst upp á Suðureyri með rætur til Aðalvíkur, foreldrar hennar fluttu suður árið 1990, en hún hefur alltaf haft sterkar taugar vestur og vildi ala börnin sín upp þar. Hún hefur búið á Vestfjörðum í tólf ár.",
         "ruv_quote": "Ég er Vestfirðingur í húð og hár. Ólst upp á Suðureyri með rætur til Aðalvíkur. Foreldrar mínir fluttu suður 1990. Hef alltaf haft sterkar taugar vestur og vildi ala upp börnin mín hér og er búin að vera hér í 12 ár."},
        {"statement": "Börnin eru þrjú á aldrinum 16, 12 og 10 ára, og hún á tryggan vin í hundinum sínum Seif sem er fimm ára og sér um að viðra hana á hverjum degi.",
         "ruv_quote": "Börnin eru 3 á aldrinum 16, 12 og 10 ára. Ég á tryggan vin í hundinum mínum Seif sem er 5 ára og sér um að viðra mig á hverjum degi."},
        {"statement": "Hún hefur mikinn áhuga á samfélaginu og fólki og þörf fyrir að leggja sitt af mörkum, og finnst gott að syngja og ganga um fjöll og firnindi.",
         "ruv_quote": "Hef mikinn áhuga á samfélaginu og fólki og þörf fyrir að leggja mitt af mörkum. Finnst gott að syngja og ganga um fjöll og firnindi."},
        {"statement": "Finney vill að í Ísafjarðarbæ verði skapandi og gott atvinnulíf, framboð af húsnæði og góðir og traustir innviðir. Hún vill að mynd sé komin á bæjarskipulagið, með nýjum og skemmtilegum miðbæ, viðhald sé sinnt í öllum kjörnum og skólastarf í blóma. Þá vill hún að þar verði starfrækt öflug menningarmiðstöð og að almenningssamgöngur milli kjarna séu virkar svo fólk njóti góðs af, sama hvar það býr.",
         "ruv_quote": "Að hér verði skapandi og gott atvinnulíf. Framboð af húsnæði og góðir og traustir innviðir. Komin mynd á bæjarskipulagið, nýr og skemmtilegur miðbær. Að viðhaldi sé sinnt í öllum kjörnum og skólastarf sé í blóma. Hér sé starfrækt öflug menningarmiðstöð og almennissamgöngur milli kjarna séu virkar og fólk njóti góðs af í sveitarfélaginu sama hvar það býr."},
        {"statement": "Helstu áhugamál hennar eru tónlist, sjálfsrækt og göngur.", "ruv_quote": "Tónlist, sjálfsrækt, göngur."},
        {"statement": "Hún á enga sérstaka fyrirmynd í pólitík, en lítur til þeirra sem ná til fólksins og gefa af sér.",
         "ruv_quote": "Þeir sem ná til fólksins og gefa af sér. Á enga sérstaka sérstaka fyrirmynd."},
        {"statement": "Radiohead er í uppáhaldi, og af kvikmyndum nefnir hún Star Wars-myndirnar og LOTR.",
         "ruv_quote": "Radiohead / Starwars myndirnar og LOTR"},
        {"statement": "Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Selfoss eflaust fyrir valinu.", "ruv_quote": "Eflaust Selfoss"},
    ]
})

# 12: Hrafnhildur Hrönn Óðinsdóttir (4200-S-5)
ENTRIES.append({
    "ruv_id": "4200-S-5",
    "new_bio": (
        "Hrafnhildur Hrönn Óðinsdóttir er stjórnmálafræðingur og starfar sem skrifstofu- og fjármálastjóri "
        "Kampa ehf. Hún er fædd árið 1985 á Íslandi, 41 árs þriggja barna móðir, og hefur BA-próf að baki. "
        "Hún hefur verið skráð í Samfylkinguna síðan 2021 og lýsir sér jafnframt sem krata alla ævi. "
        "Hrafnhildur talar ensku og getur bjargað sér á dönsku, sænsku og íslensku táknmáli. Hún missti "
        "heyrn og fékk síðar nýja heyrn með ígræðslu. Hún býr í 130 ára timburhúsi.\n\n"
        "Hrafnhildur vill að Ísafjarðarbær verði eftir tíu ár með nóg framboð af fjölbreyttu húsnæði, "
        "samtengda göngustíga og ný og gróin hverfi með leikvöllum. Hún vill sjá sér skólahúsnæði "
        "fyrir unglingastig ásamt félagsmiðstöð, og samgöngur milli byggðakjarna sem henta daglegu lífi.\n\n"
        "Hrafnhildur hefur gaman af því að spila tölvuleiki og fara á námskeið til að læra eitthvað nýtt. "
        "Aðaláhugamál hennar er golf, eða að horfa á íþróttir í sjónvarpinu, eða að spila Terraria með "
        "sonum sínum. Fyrirmynd hennar í pólitík er amma hennar, Karítas Pálsdóttir. RHCP er í "
        "uppáhaldi, eftirlætisbókin er mögulega Inngangur að efnafræði eftir Bonnie Garmus, og hún "
        "heldur einnig mikið upp á eintak af Skólaljóðum sem mamma hennar átti. Uppáhaldskvikmyndin er "
        "Aliens. Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Fjallabyggð fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hún er fædd árið 1985 á Íslandi, 41 árs þriggja barna móðir, og hefur BA-próf að baki.",
         "ruv_quote": "1985 / Íslandi / Er 41 árs þriggja barna móðir / BA"},
        {"statement": "Hún hefur verið skráð í Samfylkinguna síðan 2021 og lýsir sér jafnframt sem krata alla ævi.",
         "ruv_quote": "Skráð síðan 2021, krati alla ævi."},
        {"statement": "Hrafnhildur talar ensku og getur bjargað sér á dönsku, sænsku og íslensku táknmáli.",
         "ruv_quote": "Ensku, get bjargað mér á dönsku, sænsku og íslensku táknmáli"},
        {"statement": "Hún missti heyrn og fékk síðar nýja heyrn með ígræðslu.",
         "ruv_quote": "Missti heyrn og fékk svo nýja heyrn með ígræðslu."},
        {"statement": "Hún býr í 130 ára timburhúsi.", "ruv_quote": "130 ára timburhúsi"},
        {"statement": "Hrafnhildur vill að Ísafjarðarbær verði eftir tíu ár með nóg framboð af fjölbreyttu húsnæði, samtengda göngustíga og ný og gróin hverfi með leikvöllum. Hún vill sjá sér skólahúsnæði fyrir unglingastig ásamt félagsmiðstöð, og samgöngur milli byggðakjarna sem henta daglegu lífi.",
         "ruv_quote": "Með nóg framboð af fjölbreyttu húsnæði, samtengda göngustíga, ný og gróin hverfi með leikvöllum. Sér skólahúsnæði fyrir unglingastig ásamt félagsmiðstöð. Að hér séu samgöngur milli byggðakjarna sem henta daglegu lífi."},
        {"statement": "Hrafnhildur hefur gaman af því að spila tölvuleiki og fara á námskeið til að læra eitthvað nýtt.",
         "ruv_quote": "Hef gaman af því að spila tölvuleiki og fara á námskeið til að læra eitthvað nýtt."},
        {"statement": "Aðaláhugamál hennar er golf, eða að horfa á íþróttir í sjónvarpinu, eða að spila Terraria með sonum sínum.",
         "ruv_quote": "Ætli það sé ekki bara golf eins og er. Eða horfa á íþróttir í sjónvarpinu. Eða spila Terraria með sonum mínum."},
        {"statement": "Fyrirmynd hennar í pólitík er amma hennar, Karítas Pálsdóttir.",
         "ruv_quote": "Amma mín hún Karítas Pálsdóttir."},
        {"statement": "RHCP er í uppáhaldi, eftirlætisbókin er mögulega Inngangur að efnafræði eftir Bonnie Garmus, og hún heldur einnig mikið upp á eintak af Skólaljóðum sem mamma hennar átti.",
         "ruv_quote": "RHCP / Mögulega er það Inngangur að efnafræði, eftir Bonnie Garmus. Annars held ég mikið upp á eintakinu af Skólaljóðum sem mamma átti."},
        {"statement": "Uppáhaldskvikmyndin er Aliens.", "ruv_quote": "Aliens"},
        {"statement": "Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Fjallabyggð fyrir valinu.", "ruv_quote": "Fjallabyggð"},
    ]
})

# 13: Inga María Guðmundsdóttir (4200-S-17)
ENTRIES.append({
    "ruv_id": "4200-S-17",
    "new_bio": (
        "Inga María Guðmundsdóttir er athafnakona og frumkvöðull, búsett á Ísafirði, og á og rekur "
        "fyrirtækið Dressupgames.com. Hún var áður frambjóðandi Í-listans í Ísafjarðarbæ í "
        "sveitarstjórnarkosningunum 2022. Inga María skipar 17. sæti á lista Samfylkingarinnar og "
        "óháðra í Ísafjarðarbæ fyrir sveitarstjórnarkosningarnar 2026. Hún er fædd árið 1969 á "
        "Íslandi, hefur lokið BA-prófi í bókasafns- og upplýsingafræði og talar ensku auk íslensku. "
        "Hún hefur lengi stutt Samfylkinguna og verið jafnaðarmaður frá því hún fór að hugsa um "
        "stjórnmál. Hún býr í fjölbýlishúsi.\n\n"
        "Inga María segir málefnin sem hún hefur mestan áhuga á vera menningarmál, enda sé "
        "Ísafjarðarbær mikill menningarbær. Henni finnst einnig fegrun og hreinsun bæjarins skipta "
        "miklu máli, sérstaklega á Suðurtanga þar sem upprunalega fjaran á eyrinni er. Hún vill að "
        "Ísafjarðarbær verði eftir tíu ár fjölmennari, með fleiri atvinnutækifærum, öflugu mannlífi "
        "og meira húsnæði sem hentar öllum.\n\n"
        "Aðaláhugamál Ingu Maríu eru bækur og bíó. Sem fyrirmyndir í pólitík nefnir hún ýmsar góðar "
        "konur, til dæmis Ingibjörgu Sólrúnu og Jóhönnu Sigurðardóttur. Eftirlætisbækur hennar eru "
        "Eyja- og Killiansbækurnar eftir Einar Kárason, uppáhaldskvikmyndin er Delicatessen, og "
        "í tónlist er Raye í uppáhaldi þessa dagana, þótt það breytist stöðugt."
    ),
    "fact_check": [
        {"statement": "Hún er fædd árið 1969 á Íslandi, hefur lokið BA-prófi í bókasafns- og upplýsingafræði og talar ensku auk íslensku.",
         "ruv_quote": "1969 / Íslandi / BA í bókasafns - og upplýsingafræði / Ensku"},
        {"statement": "Hún hefur lengi stutt Samfylkinguna og verið jafnaðarmaður frá því hún fór að hugsa um stjórnmál.",
         "ruv_quote": "Ég hef lengi stutt Samfylkinguna og verið jafnaðarmaður síðan ég fór að hugsa um stjórnmál."},
        {"statement": "Hún býr í fjölbýlishúsi.", "ruv_quote": "Í fjölbýlishúsi"},
        {"statement": "Inga María segir málefnin sem hún hefur mestan áhuga á vera menningarmál, enda sé Ísafjarðarbær mikill menningarbær.",
         "ruv_quote": "Þau málefni sem ég hef mestan áhuga á eru menningarmál enda er Ísafjarðarbær mikill menningarbær."},
        {"statement": "Henni finnst einnig fegrun og hreinsun bæjarins skipta miklu máli, sérstaklega á Suðurtanga þar sem upprunalega fjaran á eyrinni er.",
         "ruv_quote": "Einnig skiptir fegrun og hreinsun bæjarins mig miklu máli, sérstaklega á Suðurtanga þar sem er eins upprunalega fjaran á eyrinni."},
        {"statement": "Hún vill að Ísafjarðarbær verði eftir tíu ár fjölmennari, með fleiri atvinnutækifærum, öflugu mannlífi og meira húsnæði sem hentar öllum.",
         "ruv_quote": "Fjölmennara, með fleiri atvinnutækifærum, öflugu mannlífi og meira húsnæði sem hentar öllum."},
        {"statement": "Aðaláhugamál Ingu Maríu eru bækur og bíó.", "ruv_quote": "Bækur og bíó!"},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hún ýmsar góðar konur, til dæmis Ingibjörgu Sólrúnu og Jóhönnu Sigurðardóttur.",
         "ruv_quote": "Ýmsar góðar konur t.d. Ingibjörg Sólrún og Jóhanna Sigurðardóttir."},
        {"statement": "Eftirlætisbækur hennar eru Eyja- og Killiansbækurnar eftir Einar Kárason, uppáhaldskvikmyndin er Delicatessen, og í tónlist er Raye í uppáhaldi þessa dagana, þótt það breytist stöðugt.",
         "ruv_quote": "Eyja - og Killiansbækurnar eftir Einar Kárason. / Delicatessen / Það breytist stöðugt, núna er Raye í uppáhaldi."},
    ]
})

# 14: Bryndís G. Friðgeirsdóttir (4200-S-18)
ENTRIES.append({
    "ruv_id": "4200-S-18",
    "new_bio": (
        "Bryndís G. Friðgeirsdóttir skipar heiðurssæti á lista Samfylkingarinnar í Ísafjarðarbæ. "
        "Hún hefur verið bæjarfulltrúi í tólf ár, þó ekki á síðustu kjörtímabilum. Bryndís er fædd "
        "árið 1957 á Íslandi og hefur verið í Samfylkingunni frá stofnun flokksins. Hún er komin "
        "á eftirlaun og var áður grunnskólakennari, og hefur lokið háskólaprófi, B.Ed.-gráðu. Auk "
        "íslensku talar hún ensku, dönsku og sænsku, og býr í raðhúsi.\n\n"
        "Bryndís segir að sveitarfélag sitt eigi að bjóða íbúum öfluga velferðarþjónustu sem leggur "
        "áherslu á metnaðarfulla mennta- og menningarstefnu, og hafa nægt framboð af íbúðarhúsnæði "
        "sem hentar bæði ungum barnafjölskyldum og efnameiri fjölskyldum.\n\n"
        "Sem fyrirmyndir í pólitík nefnir Bryndís Ingibjörgu Sólrúnu Gísladóttur, fv. formann "
        "Samfylkingarinnar, Kristrúnu Frostadóttur forsætisráðherra, Svavar Gestsson og Ragnar "
        "Arnalds. Áhugamál hennar eru útivist, tónlist og siglingar. Hún heldur upp á Mugison og "
        "Sinfóníuhljómsveit Íslands, eftirlætisbókin er Sjálfstætt fólk og uppáhaldskvikmyndin "
        "Forrest Gump. Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Bolungarvík fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hún hefur verið bæjarfulltrúi í tólf ár, þó ekki á síðustu kjörtímabilum.",
         "ruv_quote": "Ég sit í heiðurssætinu á lista Samfylkingarinnar og hef verið bæjarfulltrúi í 12 ár, þó ekki á síðustu kjörtímabilum"},
        {"statement": "Bryndís er fædd árið 1957 á Íslandi og hefur verið í Samfylkingunni frá stofnun flokksins.",
         "ruv_quote": "1957 / Íslandi / Frá stofnun Samfylkingarinnar"},
        {"statement": "Hún er komin á eftirlaun og var áður grunnskólakennari, og hefur lokið háskólaprófi, B.Ed.-gráðu.",
         "ruv_quote": "Eftirlaunaþegi, fyrrverandi grunnskólakennari / Háskólapróf Bed gráða"},
        {"statement": "Auk íslensku talar hún ensku, dönsku og sænsku, og býr í raðhúsi.",
         "ruv_quote": "Ensku og dönsku og sænsku / Raðhúsi"},
        {"statement": "Bryndís segir að sveitarfélag sitt eigi að bjóða íbúum öfluga velferðarþjónustu sem leggur áherslu á metnaðarfulla mennta- og menningarstefnu, og hafa nægt framboð af íbúðarhúsnæði sem hentar bæði ungum barnafjölskyldum og efnameiri fjölskyldum.",
         "ruv_quote": "Sveitarfélagið mitt á að bjóða íbúum öfluga velferðarþjónustu sem leggur áherslu á metnaðarfulla mennta-  og menningarstefnu og hafa nægt framboð af íbúðarhúsnæði sem hentar bæði ungum barnafjölskyldum og efnameiri fjölskyldum"},
        {"statement": "Sem fyrirmyndir í pólitík nefnir Bryndís Ingibjörgu Sólrúnu Gísladóttur, fv. formann Samfylkingarinnar, Kristrúnu Frostadóttur forsætisráðherra, Svavar Gestsson og Ragnar Arnalds.",
         "ruv_quote": "Ingibjörg Sólrún Gísladóttir fv formaður Samfylkingarinnar og Kristrún Frostadóttir forsætisráðherra og Svavar Gestson og Ragnar Arnalds"},
        {"statement": "Áhugamál hennar eru útivist, tónlist og siglingar.", "ruv_quote": "Útivist, tónlist siglingar"},
        {"statement": "Hún heldur upp á Mugison og Sinfóníuhljómsveit Íslands, eftirlætisbókin er Sjálfstætt fólk og uppáhaldskvikmyndin Forrest Gump.",
         "ruv_quote": "Mugison og sinfoníuhljómsveit Íslands / Sjálfstætt fólk / Forrest Gump"},
        {"statement": "Ef hún þyrfti að flytja úr Ísafjarðarbæ yrði Bolungarvík fyrir valinu.", "ruv_quote": "Bolungarvík"},
    ]
})

# 15: Hanna Dóra Markúsdóttir (6000-S-2)
ENTRIES.append({
    "ruv_id": "6000-S-2",
    "new_bio": (
        "Hanna Dóra Markúsdóttir er grunnskólakennari og er í 2. sæti á lista Samfylkingarinnar á "
        "Akureyri í sveitarstjórnarkosningum 2026. Hún styður framtíðarsýn flokksins um sterkari "
        "skólabæ og betra menntakerfi. Hanna Dóra er fædd árið 1968 á Íslandi og hefur kennt við "
        "Brekkuskóla í 32 ár, einkum náttúruvísindi og samfélagsgreinar á unglingastigi. Hún "
        "útskrifaðist með B.Ed.-próf frá KHÍ árið 1994 og tók MA-próf í stjórnun og forystu frá HA "
        "árið 2023. Hún talar ensku og dönsku auk íslensku og býr á þriðju hæð í þriggja herbergja "
        "blokkaríbúð í þorpinu.\n\n"
        "Framan af starfsævinni starfaði Hanna Dóra í íþrótta- og félagsstarfi jafnhliða kennslunni, "
        "kenndi fimleika, sat í stjórn FSÍ og vann sjálfboðaliðastörf fyrir knattspyrnu kvenna bæði "
        "hjá KSÍ og Þór/KA. Hún hefur verið í Samfylkingunni síðan í febrúar 2026 og nefnir Jóhönnu "
        "Sigurðardóttur sem fyrirmynd í pólitík.\n\n"
        "Hanna Dóra vill að á Akureyri ríki jöfnuður og samkeppni um kennarastöður, og að risin verði "
        "félagsmiðstöð fyrir eldri borgara, því eftir tíu ár verði hún komin á eftirlaun. Aðaláhugamál "
        "hennar eru menntamál, íþróttir og félagsstörf. Í tónlist hlustar hún á íslenska poppið, þann "
        "sem er að spila í útvarpinu hverju sinni og hún getur sungið með. Hún á enga uppáhaldsbók, "
        "en las Kirkju hafsins fyrir skemmstu og fannst hún góð. Af kvikmyndum nefnir hún að í gamla "
        "daga hafi verið hörð samkeppni á milli Dirty Dancing og Top Gun, en núna sé það kannski "
        "frekar Shawshank Redemption og Holiday. Ef hún þyrfti að flytja úr Akureyri yrði Kópavogur "
        "eða Árborg fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hanna Dóra er fædd árið 1968 á Íslandi og hefur kennt við Brekkuskóla í 32 ár, einkum náttúruvísindi og samfélagsgreinar á unglingastigi.",
         "ruv_quote": "1968 / Íslandi / Ég er grunnskólakennari og kenni aðallega náttúruvísindi og samfélagsgreinar á unglingastigi við Brekkuskóla. Þar hef ég starfað í 32 ár."},
        {"statement": "Hún útskrifaðist með B.Ed.-próf frá KHÍ árið 1994 og tók MA-próf í stjórnun og forystu frá HA árið 2023.",
         "ruv_quote": "Ég útskrifaðist með B.Ed próf frá KHÍ 1994 og tók MA próf í stjórnun og forystu frá HA 2023."},
        {"statement": "Hún talar ensku og dönsku auk íslensku og býr á þriðju hæð í þriggja herbergja blokkaríbúð í þorpinu.",
         "ruv_quote": "Ensku og dönsku / Bý á þriðju hæð í 3ja herb. blokkaríbúð í þorpinu"},
        {"statement": "Framan af starfsævinni starfaði Hanna Dóra í íþrótta- og félagsstarfi jafnhliða kennslunni, kenndi fimleika, sat í stjórn FSÍ og vann sjálfboðaliðastörf fyrir knattspyrnu kvenna bæði hjá KSÍ og Þór/KA.",
         "ruv_quote": "Framan af starfsævinni starfaði ég í íþrótta og félagsstarfi jafnhliða kennslunni, kenndi fimleika, sat í stjórn FSÍ og vann sjálfboðaliðastörf fyrir knattspyrnu kvenna bæði hjá KSÍ og Þór/KA."},
        {"statement": "Hún hefur verið í Samfylkingunni síðan í febrúar 2026 og nefnir Jóhönnu Sigurðardóttur sem fyrirmynd í pólitík.",
         "ruv_quote": "Síðan í febrúar 2026 / Jóhanna Sigurðardóttir"},
        {"statement": "Hanna Dóra vill að á Akureyri ríki jöfnuður og samkeppni um kennarastöður, og að risin verði félagsmiðstöð fyrir eldri borgara, því eftir tíu ár verði hún komin á eftirlaun.",
         "ruv_quote": "Hér ríki jöfnuður og samkeppni um kennarastöður en einnig verði risin félagsmiðstöð fyrir eldri borgara því eftir 10 ár verð ég komin á eftirlaun."},
        {"statement": "Aðaláhugamál hennar eru menntamál, íþróttir og félagsstörf.",
         "ruv_quote": "Menntamál, íþróttir og félagsstörf"},
        {"statement": "Í tónlist hlustar hún á íslenska poppið, þann sem er að spila í útvarpinu hverju sinni og hún getur sungið með.",
         "ruv_quote": "Íslenski popparinn, sá sem er að spila í útvarpinu hverju sinni og ég get sungið með."},
        {"statement": "Hún á enga uppáhaldsbók, en las Kirkju hafsins fyrir skemmstu og fannst hún góð.",
         "ruv_quote": "Á enga uppáhalds en las Kirkju hafsins fyrir skemmstu. Hún var góð."},
        {"statement": "Af kvikmyndum nefnir hún að í gamla daga hafi verið hörð samkeppni á milli Dirty Dancing og Top Gun, en núna sé það kannski frekar Shawshank Redemption og Holiday.",
         "ruv_quote": "Það fer eftir árstíð en í gamla daga var hörð samkeppni á milli Dirty dancing og Top gun. Núna meira kannski Shawshank Redemption og Holiday"},
        {"statement": "Ef hún þyrfti að flytja úr Akureyri yrði Kópavogur eða Árborg fyrir valinu.",
         "ruv_quote": "Kópavogur eða Árborg"},
    ]
})

# 16: Sigrún Steinarsdóttir (6000-S-3)
ENTRIES.append({
    "ruv_id": "6000-S-3",
    "new_bio": (
        "Sigrún Steinarsdóttir er stofnandi Matargjafa Akureyrar og nágrennis, félagslegu "
        "úthlutunarverkefnis sem hefur safnað yfir 7 milljónum króna og aðstoðað yfir 200 fjölskyldur, "
        "og er í 3. sæti á lista Samfylkingarinnar. Með þessari hugmyndasemi hefur hún orðið þekkt "
        "persóna í baráttu gegn fátækt á Norðurlandi. Sigrún er fædd árið 1973 á Íslandi, talar ensku "
        "og hefur lokið framhaldsnámi í háskóla. Hún starfar við Matargjafir Akureyri og nágrenni "
        "og býr í fjölbýli.\n\n"
        "Sigrún hefur verið í Samfylkingunni í um tíu ár og nefnir Vigdísi Finnbogadóttur sem "
        "fyrirmynd í pólitík. Hún vill að Akureyri verði eftir tíu ár miklu stærra og betra "
        "sveitarfélag.\n\n"
        "Aðaláhugamál Sigrúnar er sjálfboðastarf. Hún heldur upp á Eric Clapton, eftirlætisbókin er "
        "Hann var kallaður þetta og uppáhaldskvikmyndin Lethal Weapon."
    ),
    "fact_check": [
        {"statement": "Sigrún er fædd árið 1973 á Íslandi, talar ensku og hefur lokið framhaldsnámi í háskóla.",
         "ruv_quote": "1973 / Ísland / Enska / Framhaldsnám í háskóla"},
        {"statement": "Hún starfar við Matargjafir Akureyri og nágrenni og býr í fjölbýli.",
         "ruv_quote": "Matargjafir Akureyri og nágrenni / Fjölbýli"},
        {"statement": "Sigrún hefur verið í Samfylkingunni í um tíu ár og nefnir Vigdísi Finnbogadóttur sem fyrirmynd í pólitík.",
         "ruv_quote": "Ca 10 ár / Vigdís Finnbogadóttir"},
        {"statement": "Hún vill að Akureyri verði eftir tíu ár miklu stærra og betra sveitarfélag.",
         "ruv_quote": "Miklu stærra og betra"},
        {"statement": "Aðaláhugamál Sigrúnar er sjálfboðastarf.", "ruv_quote": "Sjálfboðastarf"},
        {"statement": "Hún heldur upp á Eric Clapton, eftirlætisbókin er Hann var kallaður þetta og uppáhaldskvikmyndin Lethal Weapon.",
         "ruv_quote": "Eric Clapton / Hann var kallaður þetta / Lethal weapon"},
    ]
})

# 17: Jóhann Jónsson (6000-S-10)
ENTRIES.append({
    "ruv_id": "6000-S-10",
    "new_bio": (
        "Jóhann Jónsson er fæddur árið 1978 á Íslandi og er 47 ára fimm barna faðir. Hann hefur "
        "búið á Akureyri frá þriggja ára aldri, fyrir utan eitt ár í námi í Bretlandi. Jóhann hefur "
        "starfað hjá Dekkjahöllinni síðustu 19 ár sem innkaupastjóri og hefur séð bæinn stækka og "
        "dafna. Hann býr í tvíbýlishúsi, talar aðallega ensku auk íslensku og hefur lokið M.Sc. í "
        "Strategic Marketing.\n\n"
        "Jóhann hefur verið í Samfylkingunni síðan 2007. Hann vill að Akureyri verði eftir tíu ár "
        "lifandi, aðlaðandi fyrir allar fjölskyldur, með fjölbreytta atvinnumöguleika og öflugt "
        "millilandaflug.\n\n"
        "Fyrirmynd Jóhanns í pólitík er Jóhanna Sigurðardóttir. Kaleo og Mugison eru í uppáhaldi, "
        "auk þess sem Queen er í uppáhaldi. Af kvikmyndum heldur hann upp á jólamyndirnar Die Hard."
    ),
    "fact_check": [
        {"statement": "Jóhann er fæddur árið 1978 á Íslandi og er 47 ára fimm barna faðir.",
         "ruv_quote": "1978 / Íslandi / 47 ára fimm barna faðir"},
        {"statement": "Hann hefur búið á Akureyri frá þriggja ára aldri, fyrir utan eitt ár í námi í Bretlandi.",
         "ruv_quote": "hef búið á Akureyri síðan ég var þriggja ára fyrir utan eitt ár í námi í Bretlandi."},
        {"statement": "Jóhann hefur starfað hjá Dekkjahöllinni síðustu 19 ár sem innkaupastjóri og hefur séð bæinn stækka og dafna.",
         "ruv_quote": "Ég hef starfað hjá Dekkjahöllinni síðustu 19 ár og hef bæinn stækka og dafna. / Innkaupastjóri hjá Dekkjahöllinni"},
        {"statement": "Hann býr í tvíbýlishúsi, talar aðallega ensku auk íslensku og hefur lokið M.Sc. í Strategic Marketing.",
         "ruv_quote": "Tvíbýlishúsi / Ensku aðallega / M.Sc Strategic Marketing"},
        {"statement": "Jóhann hefur verið í Samfylkingunni síðan 2007.", "ruv_quote": "Síðan 2007"},
        {"statement": "Hann vill að Akureyri verði eftir tíu ár lifandi, aðlaðandi fyrir allar fjölskyldur, með fjölbreytta atvinnumöguleika og öflugt millilandaflug.",
         "ruv_quote": "Lifandi, aðlaðandi fyrir allar fjölskyldur með fjölbreytta atvinnumöguleika og öflugt millilandaflug"},
        {"statement": "Fyrirmynd Jóhanns í pólitík er Jóhanna Sigurðardóttir.", "ruv_quote": "Jóhanna Sigurðardóttir"},
        {"statement": "Kaleo og Mugison eru í uppáhaldi, auk þess sem Queen er í uppáhaldi.",
         "ruv_quote": "Kaleo og Mugison. Síðan er Queen í uppáhaldi"},
        {"statement": "Af kvikmyndum heldur hann upp á jólamyndirnar Die Hard.",
         "ruv_quote": "Jólamyndirnar Die Hard"},
    ]
})

# 18: Hallur Gunnarsson (6000-S-14)
ENTRIES.append({
    "ruv_id": "6000-S-14",
    "new_bio": (
        "Hallur Gunnarsson er fjármálastjóri (CFO) hjá ferðaþjónustufyrirtækinu Saga Travel á "
        "Akureyri, sem sérhæfir sig í dagsferðum og einkaleiðsögn um Norðurland frá Akureyri og "
        "Mývatni. Hann hefur starfað hjá fyrirtækinu frá árinu 2021 og sinnir fjármálum og rekstri "
        "þess. Hallur skipar 14. sæti á lista Samfylkingarinnar á Akureyri við sveitarstjórnar"
        "kosningarnar 2026. Hann er fæddur árið 1976 á Íslandi, hefur lokið BSc-prófi og talar "
        "ensku, dönsku og smá þýsku auk íslensku. Hann hefur verið í Samfylkingunni í sjö ár og "
        "býr í einbýlishúsi.\n\n"
        "Hallur ól dætur sínar upp á Akureyri og þekkir háskólasamfélagið vel; hann var formaður "
        "SHA þegar hann var nemandi við Háskólann á Akureyri. Hann sat í stjórn KEA í fjölda ára "
        "og starfaði lengi í tölvugeiranum áður en hann sneri sér að ferðaþjónustu, og hann segist "
        "elska að renna sér á snjóbretti.\n\n"
        "Hallur vill að Akureyri verði eftir tíu ár fjölbreytt og skemmtilegt sveitarfélag og gott "
        "fyrir ungar fjölskyldur. Áhugamál hans eru ferðalög og snjóbretti. Fyrirmynd hans í pólitík "
        "er Logi Einarsson. Uppáhaldstónlistarmaður hans er Kae Tempest, eftirlætisbókin How to be "
        "Idle og uppáhaldskvikmyndin Idiocracy. Ef hann þyrfti að flytja úr Akureyri yrði Reykjavík "
        "fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hann er fæddur árið 1976 á Íslandi, hefur lokið BSc-prófi og talar ensku, dönsku og smá þýsku auk íslensku.",
         "ruv_quote": "1976 / Íslandi / BSc / Ensku, dönsku og smá þýsku"},
        {"statement": "Hann hefur verið í Samfylkingunni í sjö ár og býr í einbýlishúsi.",
         "ruv_quote": "7 ár / Einbýlishúsi"},
        {"statement": "Hallur ól dætur sínar upp á Akureyri og þekkir háskólasamfélagið vel; hann var formaður SHA þegar hann var nemandi við Háskólann á Akureyri.",
         "ruv_quote": "Hann ól dætur sínar upp á Akureyri, hann þekkir háskólasamfélagið vel og var formaður SHA þegar hann var nemandi í Háskólanum á Akureyri."},
        {"statement": "Hann sat í stjórn KEA í fjölda ára og starfaði lengi í tölvugeiranum áður en hann sneri sér að ferðaþjónustu, og hann segist elska að renna sér á snjóbretti.",
         "ruv_quote": "Hann var í stjórn KEA í fjölda ára auk þess sem hann starfaði lengi í tölvugeiranum en rekur nú ferðaþjónustufyrirtæki á Akureyri. / elskar að renna sér á snjóbretti"},
        {"statement": "Hallur vill að Akureyri verði eftir tíu ár fjölbreytt og skemmtilegt sveitarfélag og gott fyrir ungar fjölskyldur.",
         "ruv_quote": "Fjölbreytt og skemmtilegt og gott fyrir ungar fjölskyldur"},
        {"statement": "Áhugamál hans eru ferðalög og snjóbretti.", "ruv_quote": "Ferðalög og snjóbretti"},
        {"statement": "Fyrirmynd hans í pólitík er Logi Einarsson.", "ruv_quote": "Loge Einarsson"},
        {"statement": "Uppáhaldstónlistarmaður hans er Kae Tempest, eftirlætisbókin How to be Idle og uppáhaldskvikmyndin Idiocracy.",
         "ruv_quote": "Kae Tempest / How to be idle / Idiocracy"},
        {"statement": "Ef hann þyrfti að flytja úr Akureyri yrði Reykjavík fyrir valinu.",
         "ruv_quote": "Reykjavík"},
    ]
})

# 19: Sigríður Huld Jónsdóttir (6000-S-19)
ENTRIES.append({
    "ruv_id": "6000-S-19",
    "new_bio": (
        "Sigríður Huld Jónsdóttir er hjúkrunarfræðingur, kennari og verkefnastjóri með BS-próf í "
        "hjúkrunarfræði, kennsluréttindi á framhaldsskólastigi og diplóma í opinberri stjórnsýslu. "
        "Hún var aðstoðarskólameistari Verkmenntaskólans á Akureyri (VMA) frá árinu 2006 og var "
        "skipuð skólameistari skólans frá 1. janúar 2016 til fimm ára. Sigríður Huld er fyrrverandi "
        "bæjarfulltrúi Samfylkingarinnar á Akureyri og skipar 19. sæti á lista flokksins fyrir "
        "sveitarstjórnarkosningarnar 2026.\n\n"
        "Sigríður Huld er fædd árið 1969 á Íslandi, talar ensku og starfar nú sem verkefnastjóri. "
        "Hún hefur lokið meistaragráðu á háskólastigi og hefur verið í Samfylkingunni í tólf ár. "
        "Hún býr í einbýlishúsi.\n\n"
        "Sigríður Huld vill að henni finnist eins gott að búa á Akureyri eftir tíu ár og henni finnst "
        "í dag. Hún vill að áfram sé samfélag þar sem hún býr í öryggi, getur fengið þá þjónustu "
        "frá bænum sem hún þarf á að halda, og að börn hafi góðar aðstæður til að vaxa og dafna. "
        "Fyrirmynd hennar í pólitík er Ingibjörg Sólrún Gísladóttir.\n\n"
        "Aðaláhugamál Sigríðar Huldar er að horfa yfir útsýnið sem hún hefur á hverjum tíma. Hún "
        "heldur upp á U2 og les oftast bækur eftir íslenska höfunda. Af kvikmyndum nefnir hún "
        "Grease, og Mamma Mia sé alveg að ná því líka. Ef hún þyrfti að flytja úr Akureyri yrði "
        "Akranes eða Mosfellsbær fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Sigríður Huld er fædd árið 1969 á Íslandi, talar ensku og starfar nú sem verkefnastjóri.",
         "ruv_quote": "1969 / Íslandi / ensku / Verkefnastjóri"},
        {"statement": "Hún hefur lokið meistaragráðu á háskólastigi og hefur verið í Samfylkingunni í tólf ár.",
         "ruv_quote": "Meistaragráða í háskóla / 12 ár"},
        {"statement": "Hún býr í einbýlishúsi.", "ruv_quote": "Einbýlishúsi"},
        {"statement": "Sigríður Huld vill að henni finnist eins gott að búa á Akureyri eftir tíu ár og henni finnst í dag. Hún vill að áfram sé samfélag þar sem hún býr í öryggi, getur fengið þá þjónustu frá bænum sem hún þarf á að halda, og að börn hafi góðar aðstæður til að vaxa og dafna.",
         "ruv_quote": "Að mér finnist eins gott að búa á Akureyri þá og mér finnst í dag. Hér haldi áfram að vera samfélag þar sem ég bý í öryggi, get fengið þá þjónustu frá bænum sem ég þarf á að halda og að börn hafi góðar aðstæður til að vaxa og dafna."},
        {"statement": "Fyrirmynd hennar í pólitík er Ingibjörg Sólrún Gísladóttir.",
         "ruv_quote": "Ingibjörg Sólrún Gísladóttir"},
        {"statement": "Aðaláhugamál Sigríðar Huldar er að horfa yfir útsýnið sem hún hefur á hverjum tíma.",
         "ruv_quote": "Að horfa yfir útsýnið sem ég hef á hverjum tíma."},
        {"statement": "Hún heldur upp á U2 og les oftast bækur eftir íslenska höfunda.",
         "ruv_quote": "U2 / les oftast bækur eftir íslenska höfunda."},
        {"statement": "Af kvikmyndum nefnir hún Grease, og Mamma Mia sé alveg að ná því líka.",
         "ruv_quote": "Grease, Mamma mia alveg að ná því líka."},
        {"statement": "Ef hún þyrfti að flytja úr Akureyri yrði Akranes eða Mosfellsbær fyrir valinu.",
         "ruv_quote": "Akranes eða Mosfellsbær"},
    ]
})

# 20: Ragnar Sverrisson (6000-S-22)
ENTRIES.append({
    "ruv_id": "6000-S-22",
    "new_bio": (
        "Ragnar Sverrisson er kaupmaður á Akureyri. Hann er þekktastur fyrir starf sitt í "
        "herrafataversluninni JMJ á Akureyri, einni elstu starfandi verslun bæjarins, sem var "
        "stofnuð árið 1956 af Jóni M. Jónssyni, tengdaföður Ragnars. Ragnar starfaði hjá JMJ í "
        "um 51 ár og lét af störfum við áramótin 2016/2017, þegar börn hans tóku við rekstrinum. "
        "Hann skipar 22. sæti (heiðurssæti) á lista Samfylkingarinnar á Akureyri fyrir "
        "sveitarstjórnarkosningarnar 2026.\n\n"
        "Ragnar er fæddur árið 1949 á Íslandi og er klæðskeri að mennt. Hann býr í einbýlishúsi. "
        "Aðaláhugamál hans er útivist, og hann vill að Akureyri verði fullkomið sveitarfélag eftir "
        "tíu ár."
    ),
    "fact_check": [
        {"statement": "Ragnar er fæddur árið 1949 á Íslandi og er klæðskeri að mennt.",
         "ruv_quote": "1949 / Íslandi / Klæðskeri"},
        {"statement": "Hann býr í einbýlishúsi.", "ruv_quote": "einbýlishúsi"},
        {"statement": "Aðaláhugamál hans er útivist, og hann vill að Akureyri verði fullkomið sveitarfélag eftir tíu ár.",
         "ruv_quote": "útivist / Fullkomið"},
    ]
})

# 21: Rebekka Ásgeirsdóttir (6100-S-2)
ENTRIES.append({
    "ruv_id": "6100-S-2",
    "new_bio": (
        "Rebekka Ásgeirsdóttir er fædd árið 1986 á Íslandi og að mestu uppalin á Húsavík, en á "
        "rætur að rekja í Tjörneshrepp og Öxarfjörð. Hún hefur lokið námi frá Húsmæðraskólanum á "
        "Hallormsstað og BS-námi. Rebekka starfar sem hjúkrunarfræðingur hjá Heilbrigðisstofnun "
        "Norðurlands. Hún er móðir tveggja dætra og eiginkona, býr í einbýlishúsi og talar ensku "
        "auk íslensku. Hún hefur verið í Samfylkingunni í átta ár.\n\n"
        "Rebekka vill öflugt atvinnulíf, menningarlíf og góða þjónustu fyrir öll sem vilja koma og "
        "búa í Norðurþingi, og að sveitarfélagið verði áfram ákjósanlegur staður fyrir fólk að velja "
        "sér til framtíðarbúsetu. Sem fyrirmynd í pólitík nefnir hún Kristrúnu Frostadóttur.\n\n"
        "Aðaláhugamál Rebekku er líkamsrækt og hún stundar crossfit af kappi. Hún heldur upp á "
        "Bríeti, eftirlætisbókin er Bókaþjófurinn og uppáhaldskvikmyndin The Greatest Showman, þótt "
        "hún segist eiga mjög illa við að eira við sjónvarp og því séu þær ekki margar bíómyndirnar "
        "sem hún hefur horft á. Ef hún þyrfti að flytja úr Norðurþingi yrði Akureyri fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Rebekka er fædd árið 1986 á Íslandi og að mestu uppalin á Húsavík, en á rætur að rekja í Tjörneshrepp og Öxarfjörð.",
         "ruv_quote": "1986 / Íslandi / Fædd og uppalin að mestu á Húsavík, á rætur að rekja í Tjörneshrepp og Öxarfjörð."},
        {"statement": "Hún hefur lokið námi frá Húsmæðraskólanum á Hallormsstað og BS-námi.",
         "ruv_quote": "Húsmæðraskólagenginn frá Hallormstað. / Bs nám"},
        {"statement": "Rebekka starfar sem hjúkrunarfræðingur hjá Heilbrigðisstofnun Norðurlands.",
         "ruv_quote": "Hjúkrunarfræðingur hjá Heilbrigðisstofnun Norðurlands."},
        {"statement": "Hún er móðir tveggja dætra og eiginkona, býr í einbýlishúsi og talar ensku auk íslensku.",
         "ruv_quote": "Móðir tveggja dætra og eiginkona. / Einbýlishúsi / Ensku"},
        {"statement": "Hún hefur verið í Samfylkingunni í átta ár.", "ruv_quote": "8 ár"},
        {"statement": "Rebekka vill öflugt atvinnulíf, menningarlíf og góða þjónustu fyrir öll sem vilja koma og búa í Norðurþingi, og að sveitarfélagið verði áfram ákjósanlegur staður fyrir fólk að velja sér til framtíðarbúsetu.",
         "ruv_quote": "Ég vil öflugt atvinnulíf, menningarlíf og góða þjónustu fyrir öll sem hér vilja koma og búa.  Norðurþing verði áfram ákjósanlegur staður fyrir fólk að velja sér til framtíðarbúsetu."},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Kristrúnu Frostadóttur.",
         "ruv_quote": "Kristrún Frostadóttir"},
        {"statement": "Aðaláhugamál Rebekku er líkamsrækt og hún stundar crossfit af kappi.",
         "ruv_quote": "Líkamsrækt. Stunda crossfit af kappi"},
        {"statement": "Hún heldur upp á Bríeti, eftirlætisbókin er Bókaþjófurinn og uppáhaldskvikmyndin The Greatest Showman, þótt hún segist eiga mjög illa við að eira við sjónvarp og því séu þær ekki margar bíómyndirnar sem hún hefur horft á.",
         "ruv_quote": "Bríet / Bókaþjófurinn. / The greatest showman. Annars eiri ég mjög illa við sjónvarp og því eru þær ekki margar bíómyndirnar sem ég hef horft á."},
        {"statement": "Ef hún þyrfti að flytja úr Norðurþingi yrði Akureyri fyrir valinu.",
         "ruv_quote": "Akureyri"},
    ]
})

# 22: Ísak Már Aðalsteinsson (6100-S-3)
ENTRIES.append({
    "ruv_id": "6100-S-3",
    "new_bio": (
        "Ísak Már Aðalsteinsson býður sig fram fyrir Samfylkinguna í Norðurþingi í annað sinn fyrir "
        "S-listann. Hann er fæddur árið 1992 á Akureyri og hefur verið í flokknum í fjögur ár. Ísak "
        "Már starfar sem framkvæmdastjóri HSÞ og verkefnastjóri samþættingarverkefnis, og hefur lokið "
        "BSc-gráðu í íþrótta- og heilsufræði. Hann talar, auk íslensku, ensku og þýsku. Hann býr í "
        "tvíbýli.\n\n"
        "Ísak Már segir margt hafa verið vel gert í sveitarfélaginu en að víða megi gera betur, og "
        "kveðst tilbúinn í frekari áskoranir í sínu víðferma sveitarfélagi. Hann vill að Norðurþing "
        "verði eftir tíu ár blómlegt og líflegt, með fjölbreyttum atvinnu- og búsetutækifærum.\n\n"
        "Aðaláhugamál Ísaks Más eru iðkun alls konar íþrótta og að spila tónlist, en hann getur ekki "
        "gert upp á milli. Sem fyrirmyndir í pólitík nefnir hann Kristrúnu Frostadóttur og Bernie "
        "Sanders. Hann hlustar á alls konar tónlist, allt frá diskói til þungarokks, og á sér því "
        "ekki uppáhaldshljómsveit. Lord of the Rings eru alltaf góðar. Ef hann þyrfti að flytja úr "
        "Norðurþingi yrði Þingeyjarsveit fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Ísak Már Aðalsteinsson býður sig fram fyrir Samfylkinguna í Norðurþingi í annað sinn fyrir S-listann.",
         "ruv_quote": "Ég býð mig fram í annað skipti fyrir S-lista Samfylkingarinnar"},
        {"statement": "Hann er fæddur árið 1992 á Akureyri og hefur verið í flokknum í fjögur ár.",
         "ruv_quote": "1992 / Akureyri / 4 ár"},
        {"statement": "Ísak Már starfar sem framkvæmdastjóri HSÞ og verkefnastjóri samþættingarverkefnis, og hefur lokið BSc-gráðu í íþrótta- og heilsufræði.",
         "ruv_quote": "Framkvæmdastjóri HSÞ, verkefnastjóri samþættingarverkefnis. / Bs.C Íþrótta- og heilsufræði"},
        {"statement": "Hann talar, auk íslensku, ensku og þýsku.", "ruv_quote": "Íslenska, enska, þýska"},
        {"statement": "Hann býr í tvíbýli.", "ruv_quote": "Tvíbýli"},
        {"statement": "Ísak Már segir margt hafa verið vel gert í sveitarfélaginu en að víða megi gera betur, og kveðst tilbúinn í frekari áskoranir í sínu víðferma sveitarfélagi.",
         "ruv_quote": "tilbúinn í frekari áskoranir í okkar víðferma sveitarfélagi. Margt hefur verið vel gert, en víða má gera betur"},
        {"statement": "Hann vill að Norðurþing verði eftir tíu ár blómlegt og líflegt, með fjölbreyttum atvinnu- og búsetutækifærum.",
         "ruv_quote": "Blómlegt, líflegt, með fjölbreyttum atvinnu- og búsetutækifærum."},
        {"statement": "Aðaláhugamál Ísaks Más eru iðkun alls konar íþrótta og að spila tónlist, en hann getur ekki gert upp á milli.",
         "ruv_quote": "Iðkun alls konar íþrótta og að spila tónlist, get ekki gert upp á milli."},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hann Kristrúnu Frostadóttur og Bernie Sanders.",
         "ruv_quote": "Kristrún Frosta og Bernie Sanders"},
        {"statement": "Hann hlustar á alls konar tónlist, allt frá diskói til þungarokks, og á sér því ekki uppáhaldshljómsveit.",
         "ruv_quote": "Ég hlusta á alls konar tónlist, allt frá diskó til þungarokks. Á mér því ekki uppáhalds hljómsveit."},
        {"statement": "Lord of the Rings eru alltaf góðar.", "ruv_quote": "Lord of the Rings alltaf góðar."},
        {"statement": "Ef hann þyrfti að flytja úr Norðurþingi yrði Þingeyjarsveit fyrir valinu.",
         "ruv_quote": "Þingeyjarsveit"},
    ]
})

# 23: Reynir Ingi Reinhardsson (6100-S-5)
ENTRIES.append({
    "ruv_id": "6100-S-5",
    "new_bio": (
        "Reynir Ingi Reinhardsson er fæddur árið 1989 á Íslandi. Hann er 36 ára, uppalinn á Þórshöfn "
        "og síðar á Húsavík þar sem hann býr í dag ásamt eiginkonu sinni, Sirilin Keskla. Hann er "
        "menntaður lögfræðingur og starfar hjá Skattinum á Akureyri. Reynir Ingi er mikill áhugamaður "
        "um byggðamál og vill leggja sitt af mörkum til þess að samfélagið í Norðurþingi sé öflugt "
        "og eftirsóknarvert fyrir ungt fjölskyldufólk. Hann býr í íbúð, talar spænsku og ensku auk "
        "íslensku og hefur lokið meistaragráðu. Hann hefur verið í Samfylkingunni í fjögur ár.\n\n"
        "Reynir Ingi vill að í Norðurþingi verði öflugt menningar- og atvinnulíf sem laðar ungt fólk "
        "að sveitarfélaginu, hvort sem fólk er að snúa aftur heim á æskuslóðirnar eða aðrir sem vilja "
        "búa í blómlegu og lifandi samfélagi. Sem fyrirmynd í pólitík nefnir hann Olof Palme.\n\n"
        "Áhugamál Reynis Inga eru íþróttir og ferðalög. Eftirlætisbókin er Englar alheimsins og "
        "uppáhaldskvikmyndin Ace Ventura: Pet Detective. Tónlistarsmekkurinn er breytilegur frá degi "
        "til dags, en núna er Matt Berry sennilega í uppáhaldi. Ef hann þyrfti að flytja úr Norðurþingi "
        "yrði Reykjavíkurborg fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Reynir Ingi Reinhardsson er fæddur árið 1989 á Íslandi.",
         "ruv_quote": "1989 / Íslandi"},
        {"statement": "Hann er 36 ára, uppalinn á Þórshöfn og síðar á Húsavík þar sem hann býr í dag ásamt eiginkonu sinni, Sirilin Keskla.",
         "ruv_quote": "Ég 36 ára, uppalinn á Þórshöfn og svo á Húsavík þar sem ég bý í dag ásamt eiginkonu minni Sirilin Keskla."},
        {"statement": "Hann er menntaður lögfræðingur og starfar hjá Skattinum á Akureyri.",
         "ruv_quote": "Ég er menntaður lögfræðingur og starfa hjá Skattinum á Akureyri."},
        {"statement": "Reynir Ingi er mikill áhugamaður um byggðamál og vill leggja sitt af mörkum til þess að samfélagið í Norðurþingi sé öflugt og eftirsóknarvert fyrir ungt fjölskyldufólk.",
         "ruv_quote": "Ég er mikilli áhugamaður um byggðamál og vill leggja mitt að mörkum til þess að samfélagið hér sé öflugt og eftirsóknarvert fyrir ungt fjölskyldufólk."},
        {"statement": "Hann býr í íbúð, talar spænsku og ensku auk íslensku og hefur lokið meistaragráðu.",
         "ruv_quote": "Íbúð / Spænsku og ensku. / Meistaragráða"},
        {"statement": "Hann hefur verið í Samfylkingunni í fjögur ár.", "ruv_quote": "4 ár"},
        {"statement": "Reynir Ingi vill að í Norðurþingi verði öflugt menningar- og atvinnulíf sem laðar ungt fólk að sveitarfélaginu, hvort sem fólk er að snúa aftur heim á æskuslóðirnar eða aðrir sem vilja búa í blómlegu og lifandi samfélagi.",
         "ruv_quote": "Ég vil að hér verði öflugt menningar- og atvinnulíf sem laðar ungt fólk að sveitarfélaginu okkar, hvort sem fólk er að snúa aftur heim á æskuslóðirnar eða aðrir sem vilja búa í blómlegu og lifandi samfélagi."},
        {"statement": "Sem fyrirmynd í pólitík nefnir hann Olof Palme.", "ruv_quote": "Olof Palme"},
        {"statement": "Áhugamál Reynis Inga eru íþróttir og ferðalög.", "ruv_quote": "Íþróttir og ferðalög."},
        {"statement": "Eftirlætisbókin er Englar alheimsins og uppáhaldskvikmyndin Ace Ventura: Pet Detective.",
         "ruv_quote": "Englar alheimsins / Ace Ventura: Pet Detective"},
        {"statement": "Tónlistarsmekkurinn er breytilegur frá degi til dags, en núna er Matt Berry sennilega í uppáhaldi.",
         "ruv_quote": "Það er breytilegt frá degi til dags en núna er það sennilega Matt Berry."},
        {"statement": "Ef hann þyrfti að flytja úr Norðurþingi yrði Reykjavíkurborg fyrir valinu.",
         "ruv_quote": "Reykjavíkurborg"},
    ]
})

# 24: Regína Sigurðardóttir (6100-S-6)
ENTRIES.append({
    "ruv_id": "6100-S-6",
    "new_bio": (
        "Regína Sigurðardóttir er félagslynd og hefur áhuga á samfélagsmálum. Hún er fædd árið 1953 "
        "á Íslandi og hefur verið í Samfylkingunni frá stofnun flokksins árið 1999. Regína er komin "
        "á eftirlaun og vinnur sem verktaki við bókhald Dvalarheimilis aldraðra og Hvamms á Húsavík, "
        "auk þess sem hún er formaður Félags eldri borgara á Húsavík og nágrenni. Hún talar ensku "
        "og dönsku og er með þrjár diplómagráður frá endurmenntun HÍ: í heilsuhagfræði, stjórnun og "
        "rekstri í heilbrigðisþjónustu og mannauðsstjórnun. Hún býr í eigin íbúð á neðri hæð í tvíbýli. "
        "Hún er amma fimm stelpna á aldrinum níu til átján ára.\n\n"
        "Regína vill að Norðurþing verði eftir tíu ár fjölskylduvænt samfélag þar sem þjónusta við "
        "alla aldurshópa er í fyrirrúmi. Hún vill atvinnuöryggi sem byggir á nokkrum traustum "
        "fyrirtækjum í meirihlutaeigu Íslendinga. Uppbygging byggðar eigi að taka mið af þörfum "
        "allra aldurshópa, meðal annars með blandaðri byggð og húsnæði fyrir alla aldurshópa í sama "
        "hverfi. Hún vill að sveitarfélagið verði í raun ein heild og að öllum íbúum þess finnist "
        "þeir sitja við sama borð.\n\n"
        "Aðaláhugamál Regínu er prjónaskapur. Sem fyrirmyndir í pólitík nefnir hún Jóhönnu "
        "Sigurðardóttur, Sólrúnu Gísladóttur og Kristrúnu Frostadóttur. Hún heldur upp á Bruce "
        "Springsteen, eftirlætisbókin er Svipting eftir Svein Skorra Höskuldsson og uppáhalds"
        "kvikmyndin Kramer vs. Kramer. Ef hún þyrfti að flytja úr Norðurþingi yrði Hörgárbyggð fyrir "
        "valinu."
    ),
    "fact_check": [
        {"statement": "Regína Sigurðardóttir er félagslynd og hefur áhuga á samfélagsmálum.",
         "ruv_quote": "Eg er félagslynd hef áhuga á samfélagsmálum"},
        {"statement": "Hún er fædd árið 1953 á Íslandi og hefur verið í Samfylkingunni frá stofnun flokksins árið 1999.",
         "ruv_quote": "1953 / Ísland / Úpps... fra stofnun Samfylkingarinnar 1999"},
        {"statement": "Regína er komin á eftirlaun og vinnur sem verktaki við bókhald Dvalarheimilis aldraðra og Hvamms á Húsavík, auk þess sem hún er formaður Félags eldri borgara á Húsavík og nágrenni.",
         "ruv_quote": "Ég er a eftirlaunum. Vinna sem verktaki við bókhald Dvalarheimikis aldraðra og Hvamms á Húsavík auk þess sem ég er formaður Félags eldri borgara a Húsavík og nágrennis"},
        {"statement": "Hún talar ensku og dönsku og er með þrjár diplómagráður frá endurmenntun HÍ: í heilsuhagfræði, stjórnun og rekstri í heilbrigðisþjónustu og mannauðsstjórnun.",
         "ruv_quote": "Ensku og Dönsku / Eg er með 3 diploma gráður frá endurmenntun HÍ: Heilsuhagfræði,  stjórnun og rekstur í heilbrigðisþjónustu og mannauðsstjórnun"},
        {"statement": "Hún býr í eigin íbúð á neðri hæð í tvíbýli.",
         "ruv_quote": "Eigin íbúð á neðri hæð í tvíbýli..."},
        {"statement": "Hún er amma fimm stelpna á aldrinum níu til átján ára.",
         "ruv_quote": "Ég er amma fimm stelpna á aldrinum 9 til 18 ára."},
        {"statement": "Regína vill að Norðurþing verði eftir tíu ár fjölskylduvænt samfélag þar sem þjónusta við alla aldurshópa er í fyrirrúmi. Hún vill atvinnuöryggi sem byggir á nokkrum traustum fyrirtækjum í meirihlutaeigu Íslendinga. Uppbygging byggðar eigi að taka mið af þörfum allra aldurshópa, meðal annars með blandaðri byggð og húsnæði fyrir alla aldurshópa í sama hverfi. Hún vill að sveitarfélagið verði í raun ein heild og að öllum íbúum þess finnist þeir sitja við sama borð.",
         "ruv_quote": "Fjölskylduvænt samfélag þar sem þjónusta við alla aldurshópa er í fyrirrúmi. Atvinnuöryggi sem byggir á nokkrum traustum fyrirtækjum í meirihluta eigu íslendinga. Uppbygging byggðar hafi tekið mið af þörfum allra aldurshópa m.a. með uppbyggingu íbúðarbyggðar þar sem gert er ráð fyrir blandaðri byggð, húsnæði fyrir alla aldurshópa í sama hverfi.  Sveitarfélagið verði í raun ein heild og að öllum íbúum sveitarfélagsins finnist þeir sitja við sama borð"},
        {"statement": "Aðaláhugamál Regínu er prjónaskapur.", "ruv_quote": "Prjónaskapur"},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hún Jóhönnu Sigurðardóttur, Sólrúnu Gísladóttur og Kristrúnu Frostadóttur.",
         "ruv_quote": "Jóhanna Sigurðardóttir, Sólrún Gísladóttir, Kristrún Frostadóttir..."},
        {"statement": "Hún heldur upp á Bruce Springsteen, eftirlætisbókin er Svipting eftir Svein Skorra Höskuldsson og uppáhaldskvikmyndin Kramer vs. Kramer.",
         "ruv_quote": "Bruce Springsteen / Svipting eftir Svein Skorra Höskuldsson / Kamerún vs Kramer"},
        {"statement": "Ef hún þyrfti að flytja úr Norðurþingi yrði Hörgárbyggð fyrir valinu.",
         "ruv_quote": "Hörgárbyggð"},
    ]
})

# 25: Óskar Páll Davíðsson (6100-S-11)
ENTRIES.append({
    "ruv_id": "6100-S-11",
    "new_bio": (
        "Óskar Páll Davíðsson er frambjóðandi Samfylkingarinnar í Norðurþingi. Hann er fæddur árið "
        "1997 á Íslandi og starfar sem kennari. Hann hefur lokið BEd-gráðu og talar ensku auk "
        "íslensku. Hann hefur verið í flokknum í eitt ár. Óskar Páll býr í íbúð í einbýlishúsi.\n\n"
        "Óskar Páll vill að Norðurþing verði menningarmiðstöð eftir tíu ár. Sem fyrirmynd í pólitík "
        "nefnir hann heiðarlegt fólk.\n\n"
        "Áhugamál Óskars Páls eru spil, fótbolti, útivist og hlaup. Hann heldur upp á Ágúst og "
        "Bríeti, eftirlætisbókin er Tár, bros og takkaskór og uppáhaldskvikmyndin Batman. Ef hann "
        "þyrfti að flytja úr Norðurþingi yrði Reykjavík fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hann er fæddur árið 1997 á Íslandi og starfar sem kennari.",
         "ruv_quote": "1997 / Íslandi / Kennari"},
        {"statement": "Hann hefur lokið BEd-gráðu og talar ensku auk íslensku.",
         "ruv_quote": "Bed gráða / Ensku"},
        {"statement": "Hann hefur verið í flokknum í eitt ár.", "ruv_quote": "1 ár"},
        {"statement": "Óskar Páll býr í íbúð í einbýlishúsi.", "ruv_quote": "Íbúð í einbýlishúsi"},
        {"statement": "Óskar Páll vill að Norðurþing verði menningarmiðstöð eftir tíu ár.",
         "ruv_quote": "Menningarmiðstöð"},
        {"statement": "Sem fyrirmynd í pólitík nefnir hann heiðarlegt fólk.",
         "ruv_quote": "Heiðarlegt fólk"},
        {"statement": "Áhugamál Óskars Páls eru spil, fótbolti, útivist og hlaup.",
         "ruv_quote": "Spil, fótbolti, útivist, hlaup"},
        {"statement": "Hann heldur upp á Ágúst og Bríeti, eftirlætisbókin er Tár, bros og takkaskór og uppáhaldskvikmyndin Batman.",
         "ruv_quote": "Ágúst Bríet / Tár bros og takkaskór / Batman"},
        {"statement": "Ef hann þyrfti að flytja úr Norðurþingi yrði Reykjavík fyrir valinu.",
         "ruv_quote": "Reykjavík"},
    ]
})

# 26: Skúli Helgason (0000-S-4)
ENTRIES.append({
    "ruv_id": "0000-S-4",
    "new_bio": (
        "Skúli Helgason er fæddur 15. apríl 1965 á Íslandi og er stjórnmálafræðingur með MPA-gráðu "
        "frá University of Minnesota. Hann var framkvæmdastjóri Samfylkingarinnar 2006–2009 og "
        "þingmaður 2009–2013. Hann hefur setið í borgarstjórn Reykjavíkur síðan 2014 og er formaður "
        "menningar- og íþróttaráðs. Hann starfar sem borgarfulltrúi í Reykjavík og situr í stjórn "
        "Orkuveitunnar. Hann hefur verið í Samfylkingunni frá stofnun hennar árið 2000.\n\n"
        "Skúli lýsir sér sem eldheitum jafnaðarmanni og miklum áhugamanni um bætt menntakerfi, öflugt "
        "menningarlíf, umhverfismál og sjálfbærni og uppbyggingu hagkvæms húsnæðis. Hann er fimm "
        "barna faðir í Vesturbænum, kvæntur, og býr í eigin húsnæði. Auk íslensku talar hann ensku, "
        "dönsku, þýsku og frönsku.\n\n"
        "Skúli vill að Reykjavík verði eftir tíu ár sterkt samfélag jöfnuðar, mannréttinda og "
        "menningar. Áhugamál hans eru íþróttir, menning og fjölbreytt útivist. Fyrirmynd hans í "
        "pólitík er Nelson Mandela. Hann heldur upp á The Beatles, eftirlætisbókin er Himnaríki "
        "og helvíti eftir Jón Kalman Stefánsson og uppáhaldskvikmyndin Pulp Fiction. Ef hann þyrfti "
        "að flytja úr Reykjavík yrði Hafnarfjörður fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hann starfar sem borgarfulltrúi í Reykjavík og situr í stjórn Orkuveitunnar.",
         "ruv_quote": "Borgarfulltrúi í Reykjavík.  Sit í stjórn Orkuveitunnar"},
        {"statement": "Hann hefur verið í Samfylkingunni frá stofnun hennar árið 2000.",
         "ruv_quote": "Frá stofnun árið 2000"},
        {"statement": "Skúli lýsir sér sem eldheitum jafnaðarmanni og miklum áhugamanni um bætt menntakerfi, öflugt menningarlíf, umhverfismál og sjálfbærni og uppbyggingu hagkvæms húsnæðis.",
         "ruv_quote": "Ég er eldheitur jafnaðarmaður og mikill áhugamaður um bætt menntakerfi, öflugt menningarlíf, umhverfismál og sjálfbærni og uppbyggingu hagkvæms húsnæðis."},
        {"statement": "Hann er fimm barna faðir í Vesturbænum, kvæntur, og býr í eigin húsnæði.",
         "ruv_quote": "Ég er fimm barna faðir í Vesturbænum kvæntur / Eigin húsnæði"},
        {"statement": "Auk íslensku talar hann ensku, dönsku, þýsku og frönsku.",
         "ruv_quote": "Ensku, dönsku, þýsku, frönsku"},
        {"statement": "Skúli vill að Reykjavík verði eftir tíu ár sterkt samfélag jöfnuðar, mannréttinda og menningar.",
         "ruv_quote": "Sterkt samfélag jöfnuðar, mannréttinda og menningar!"},
        {"statement": "Áhugamál hans eru íþróttir, menning og fjölbreytt útivist.",
         "ruv_quote": "Íþróttir, menning og fjölbreytt útivist"},
        {"statement": "Fyrirmynd hans í pólitík er Nelson Mandela.", "ruv_quote": "Nelson Mandela"},
        {"statement": "Hann heldur upp á The Beatles, eftirlætisbókin er Himnaríki og helvíti eftir Jón Kalman Stefánsson og uppáhaldskvikmyndin Pulp Fiction.",
         "ruv_quote": "The Beatles / Himnaríki og helvíti eftir Jón Kalman Stefánsson / Pulp Fiction"},
        {"statement": "Ef hann þyrfti að flytja úr Reykjavík yrði Hafnarfjörður fyrir valinu.",
         "ruv_quote": "Hafnarfjörður"},
    ]
})

# 27: Birkir Ingibjartsson (0000-S-8)
ENTRIES.append({
    "ruv_id": "0000-S-8",
    "new_bio": (
        "Birkir Ingibjartsson er arkitekt, fæddur árið 1986 á Íslandi, sem hefur starfað sjálfstætt "
        "hjá TÓ arkitektum og áður sem verkefnisstjóri í borgarskipulagi hjá Reykjavíkurborg. Hann "
        "fékk löggildingu sem arkitekt árið 2019 og hefur einkum sérhæft sig í borgarhönnun, "
        "almenningsrýmum og samgöngum. Birkir hefur setið sem varaborgarfulltrúi Samfylkingarinnar "
        "í Reykjavík frá 2022 og átt sæti í umhverfis- og skipulagsráði. Hann hefur verið virkur í "
        "umræðu um þéttingu byggðar, samgönguskipulag og takmörkun á einkabílaumferð í borginni. "
        "Birkir tók þátt í flokksvali Samfylkingarinnar í janúar 2026 og hlaut þar 8. sæti á lista "
        "flokksins fyrir komandi borgarstjórnarkosningar.\n\n"
        "Birkir er með mastersgráðu í arkitektúr, starfar sem sjálfstætt starfandi arkitekt og "
        "varaborgarfulltrúi, og talar auk íslensku ensku, sænsku, smá dönsku og þýsku. Hann er 39 "
        "ára gamall og býr í Safamýri, í sérhæð í þríbýli. Hann er giftur og á þrjú börn á aldrinum "
        "fimm til 21 árs. Hann hefur verið í Samfylkingunni í 4–5 ár.\n\n"
        "Birkir vill að Reykjavík verði eftir tíu ár öflugt, sjálfbært og fjölbreytt borgarsamfélag "
        "þar sem gott er að vaxa, dafna, læra, búa, starfa og njóta lífsins. Sem fyrirmyndir í pólitík "
        "nefnir hann öfluga borgarstjóra Samfylkingarinnar í gegnum tíðina, Dag B. Eggertsson og "
        "Ingibjörgu Sólrúnu Gísladóttur, sem hann lýsir sem öflugu fólki með skýra sýn á hvernig "
        "borgarsamfélag eigi að byggja upp og óhrætt við að leiða breytingar í þágu borgarbúa.\n\n"
        "Aðaláhugamál Birkis eru að mestu arkitektúr og skipulagsmál, og þar fyrir utan almenn "
        "útivist, hreyfing, ferðalög og að fylgjast með boltanum. Hann hefur verið dálítið á Birnis-"
        "vagninum undanfarið, en Bubbi er svo góð og áhugaverð týpa að hann hendir oft Blindskeri á "
        "fóninn til að peppa sig í gang. Hann á enga eina sérstaka eftirlætisbók en finnst skemmtilegast "
        "að lesa nýlegar íslenskar skáldsögur sem fjalla á opinn hátt um íslenskt samfélag, og nefnir "
        "að Dauði skógar og Ungfrú Ísland hafi setið lengi í honum. Af kvikmyndum nefnir hann að 2001: "
        "A Space Odyssey sé enn toppurinn í framtíðar-sci-fi. Ef hann þyrfti að flytja úr Reykjavík "
        "yrði Kópavogur, gamli heimabær hans, fyrir valinu, og þá við hliðina á Fossvogsbrúnni til að "
        "vera snöggur yfir í Vatnsmýrina."
    ),
    "fact_check": [
        {"statement": "Birkir er með mastersgráðu í arkitektúr, starfar sem sjálfstætt starfandi arkitekt og varaborgarfulltrúi, og talar auk íslensku ensku, sænsku, smá dönsku og þýsku.",
         "ruv_quote": "Mastersgráða í arkitektúr / Sjálfstætt starfandi arkitekt og varaborgarfulltrúi / Enska, sænska, smá dönsku og þýsku"},
        {"statement": "Hann er 39 ára gamall og býr í Safamýri, í sérhæð í þríbýli.",
         "ruv_quote": "Ég er 39 ára gamall og bý í Safamýri. / Sérhæð í þríbýli"},
        {"statement": "Hann er giftur og á þrjú börn á aldrinum fimm til 21 árs.",
         "ruv_quote": "Er giftur og á þrjú börn á aldrinum 5 til 21 árs."},
        {"statement": "Hann hefur verið í Samfylkingunni í 4–5 ár.", "ruv_quote": "4-5 ár"},
        {"statement": "Birkir vill að Reykjavík verði eftir tíu ár öflugt, sjálfbært og fjölbreytt borgarsamfélag þar sem gott er að vaxa, dafna, læra, búa, starfa og njóta lífsins.",
         "ruv_quote": "Öflugt, sjálfbært og fjölbreytt borgarsamfélag þar sem gott er að vaxa, dafna, læra, búa, starfa og njóta lífsins."},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hann öfluga borgarstjóra Samfylkingarinnar í gegnum tíðina, Dag B. Eggertsson og Ingibjörgu Sólrúnu Gísladóttur, sem hann lýsir sem öflugu fólki með skýra sýn á hvernig borgarsamfélag eigi að byggja upp og óhrætt við að leiða breytingar í þágu borgarbúa.",
         "ruv_quote": "Ætli það séu ekki helst öflugir borgarstjórar Samfylkingarinnar í gegnum tíðina, Dagur B. Eggertsson og Ingibjörg Sólrún Gísladóttir. Öflugt fólk með skýra sýn á hvernig borgarsamfélag hér ætti að byggja upp og óhrætt við að leiða breytingar í þágu borgarbúa."},
        {"statement": "Aðaláhugamál Birkis eru að mestu arkitektúr og skipulagsmál, og þar fyrir utan almenn útivist, hreyfing, ferðalög og að fylgjast með boltanum.",
         "ruv_quote": "ætli arkitektúr og skipulagsmál sé ekki dáldið það sem líf manns og áhugamál hverfist um. Þess utan bara almenn útivist, hreyfing, ferðalög og að fylgjast boltanum."},
        {"statement": "Hann hefur verið dálítið á Birnis-vagninum undanfarið, en Bubbi er svo góð og áhugaverð týpa að hann hendir oft Blindskeri á fóninn til að peppa sig í gang.",
         "ruv_quote": "Ég hef verið dáldið á Birnis vagninum undanfarið en svo er Bubbi svo góð og áhugaverð týpa, hendi oft Blindsker á fóninn til að peppa mig í gang"},
        {"statement": "Hann á enga eina sérstaka eftirlætisbók en finnst skemmtilegast að lesa nýlegar íslenskar skáldsögur sem fjalla á opinn hátt um íslenskt samfélag, og nefnir að Dauði skógar og Ungfrú Ísland hafi setið lengi í honum.",
         "ruv_quote": "á enga eina sérstaka eftirlætisbók - finnst samt yfirleitt skemmtilegast að lesa nýlegar íslenskar skáldsögur sem fjalla á opinn hátt um íslenskt samfélag ... Dauði skógar og Ungrú Ísland sátu t.d lengi í mér af mjög ólíkum ástæðum."},
        {"statement": "Af kvikmyndum nefnir hann að 2001: A Space Odyssey sé enn toppurinn í framtíðar-sci-fi.",
         "ruv_quote": "Ég er sökker fyrir svona framtíðar sci-fi, þar er 2001: A Space Odyssey ennþá toppurinn"},
        {"statement": "Ef hann þyrfti að flytja úr Reykjavík yrði Kópavogur, gamli heimabær hans, fyrir valinu, og þá við hliðina á Fossvogsbrúnni til að vera snöggur yfir í Vatnsmýrina.",
         "ruv_quote": "Það væri að sjálfsögðu minn gamli heimabær Kópavogur, myndi flytja við hliðina á Fossvogsbrúnni til að vera snöggur yfir í Vatnsmýrina."},
    ]
})

# 28: Sara Björg Sigurðardóttir (0000-S-10)
ENTRIES.append({
    "ruv_id": "0000-S-10",
    "new_bio": (
        "Sara Björg Sigurðardóttir er íbúi í Breiðholti til fjölda ára þar sem hún býr ásamt "
        "fjölskyldu sinni. Hún hefur verið varaborgarfulltrúi Samfylkingarinnar í Reykjavík frá "
        "árinu 2019 og fyrsti varaborgarfulltrúi með sérstaka stöðu á yfirstandandi kjörtímabili. "
        "Sara leiddi íbúaráð Breiðholts í fimm ár og hefur verið formaður öldungaráðs Reykjavíkur"
        "borgar frá 2022. Á þessu kjörtímabili situr hún í menningar- og íþróttaráði, velferðarráði "
        "og innkauparáði borgarinnar og fer fyrir samstarfsnefnd skíðasvæðanna á höfuðborgarsvæðinu. "
        "Hún átti frumkvæði að verkefninu „Frístundir í Breiðholti“ árið 2020 sem nýtir frístundatengla "
        "til að ná til barna í viðkvæmri stöðu. Hún er móðir þriggja barna og hefur talað skýrt um "
        "reglur Jöfnunarsjóðs sveitarfélaga sem mismuni Reykvíkingum á grundvelli búsetu og uppruna.\n\n"
        "Sara er fædd árið 1977 í Reykjavík, gift og þriggja barna móðir, búsett í Breiðholti og "
        "býr í sérbýli. Hún hefur lokið meistaraprófi í opinberri stjórnsýslu (MPA) og talar ensku, "
        "dönsku og spænsku auk íslensku. Hún starfar sem borgarfulltrúi fyrir Samfylkinguna og gekk "
        "til liðs við flokkinn árið 2018.\n\n"
        "Sara á sér draum um að Reykjavík verði minni bílaborg, meiri hjólaborg og borgarlínan verði "
        "farin að flytja fólk milli staða. Hún vill að 30% íbúða séu byggðar í blandaðri byggð af "
        "óhagnaðardrifnum félögum sem byggja í þágu almannahags. Þá vill hún að líðan barna verði "
        "betri og að fleiri börn nái að tilheyra, sérstaklega börn af erlendum uppruna; best væri ef "
        "frístundastyrkurinn yrði nýttur að fullu og ekkert barn sæti eftir, og að öll hefðu fundið "
        "sinn stað til að blómstra og dafna. Fyrirmynd hennar í pólitík er Vigdís Finnbogadóttir.\n\n"
        "Aðaláhugamál Söru eru að rækta garðinn sinn, hjóla og fara í sund- og sjósundferðir. Hún "
        "heldur upp á GusGus, eftirlætisbókin er Ekki gleyma mér eftir Kristínu Jóhannesdóttur og "
        "uppáhaldskvikmyndin Forrest Gump. Ef hún þyrfti að flytja myndi hún vilja flytja til "
        "fólksins síns á Akureyri."
    ),
    "fact_check": [
        {"statement": "Sara er fædd árið 1977 í Reykjavík, gift og þriggja barna móðir, búsett í Breiðholti og býr í sérbýli.",
         "ruv_quote": "1977 / Reykjavík / Gift, þriggja barna móðir búsett í Breiðholti. / Sérbýli"},
        {"statement": "Hún hefur lokið meistaraprófi í opinberri stjórnsýslu (MPA) og talar ensku, dönsku og spænsku auk íslensku.",
         "ruv_quote": "Meistapróf í opinberri stjórnsýslu - MPA / Ensku, dönsku og spænsku."},
        {"statement": "Hún starfar sem borgarfulltrúi fyrir Samfylkinguna og gekk til liðs við flokkinn árið 2018.",
         "ruv_quote": "Borgarfulltrúi fyrir Samfylkinguna. / Ég gekk til liðs við Samfylkinguna 2018."},
        {"statement": "Sara á sér draum um að Reykjavík verði minni bílaborg, meiri hjólaborg og borgarlínan verði farin að flytja fólk milli staða. Hún vill að 30% íbúða séu byggðar í blandaðri byggð af óhagnaðardrifnum félögum sem byggja í þágu almannahags. Þá vill hún að líðan barna verði betri og að fleiri börn nái að tilheyra, sérstaklega börn af erlendum uppruna; best væri ef frístundastyrkurinn yrði nýttur að fullu og ekkert barn sæti eftir, og að öll hefðu fundið sinn stað til að blómstra og dafna.",
         "ruv_quote": "Ég á mér draum um að Reykjavík verði minni bílaborg, meiri hjólaborg og borgarlínan verði farin að flytja fólk milli staða. Að 30% íbúða séu byggðar í blandraði byggð af óhagnardrifnum félögum sem byggja í þágu almannahags. Ég vil að líðan barna verði betri, fleiri börn hafa náð að tilheyra sérstaklega börn af erlendum uppruna, best væri að frístundastyrkurinn væri nýttur að fullu og ekkert barn sitji eftir - öll hafi fundið sinn stað til blómstra og dafna."},
        {"statement": "Fyrirmynd hennar í pólitík er Vigdís Finnbogadóttir.", "ruv_quote": "Vigdís Finnbogadóttir"},
        {"statement": "Aðaláhugamál Söru eru að rækta garðinn sinn, hjóla og fara í sund- og sjósundferðir.",
         "ruv_quote": "Rækta garðinn minn, hjóla og sund/sjósundferðir."},
        {"statement": "Hún heldur upp á GusGus, eftirlætisbókin er Ekki gleyma mér eftir Kristínu Jóhannesdóttur og uppáhaldskvikmyndin Forrest Gump.",
         "ruv_quote": "GusGus / Ekki gleyma mér eftir Krisínu Jóhannesdóttir / Forest Gump"},
        {"statement": "Ef hún þyrfti að flytja myndi hún vilja flytja til fólksins síns á Akureyri.",
         "ruv_quote": "Ég myndi vilja flytja til fólksins míns á Akureyri."},
    ]
})

# 29: Arnar Ingi Ingason (0000-S-12)
ENTRIES.append({
    "ruv_id": "0000-S-12",
    "new_bio": (
        "Arnar Ingi Ingason er tónlistarmaður og hefur haft það að atvinnu undanfarin 11 ár. Hann "
        "er fæddur árið 1996, fæddur og uppalinn á Íslandi, og er aðfluttur Reykvíkingur, "
        "upprunalega úr Kópavogi og stoltur Bliki. Hann hefur síðastliðin tæp 10 ár gert Vesturbæ "
        "Reykjavíkur að heimili sínu, með stuttu stoppi í Berlín, og býr í leiguíbúð í Vesturbænum. "
        "Hann á yndislega unnustu sem er að ljúka arkitektúrnámi í Brussel, sem þýðir að hann hefur "
        "undanfarin tvö ár verið tíður gestur þar í borg. Engin tenging við Evrópusambandið, enn.\n\n"
        "Arnar talar ensku og getur reddað sér á dönsku og þýsku. Hann tók eitt ár í grafískri "
        "hönnun við LHÍ, lét þá staðar numið og fór á fullu inn í tónlistina. Hann hefur verið "
        "félagi í Samfylkingunni síðan 2018.\n\n"
        "Arnar Ingi hefur brennandi áhuga á öllu sem viðkemur tónlist, knattspyrnu og pólitík. Eftir "
        "tíu ár langar hann að sjá borg sem heldur áfram að blómstra og iða af mannlífi. Helst "
        "væri hann til í að sjá Borgarlínuna í fullu fjöri og að byrjað væri að leggja drög að lest "
        "sem lægi beint úr hjarta borgarinnar í átt að Keflavíkurflugvelli. Eftir tíu ár myndi hann "
        "einnig vilja að menningarlíf borgarinnar væri blómlegra sem aldrei fyrr, að borgin væri "
        "útbúin tónleikastöðum fyrir allar stærðir og gerðir tónleika og að í það minnsta væri til "
        "einn alvöru technóklúbbur.\n\n"
        "Aðaláhugamál Arnars Inga eru tónlist, matargerð, knattspyrna og pólitík, og hann segist "
        "vera „semi unplayable“ ef hann fái þessa flokka í Bezzerwisser. Sem fyrirmyndir í pólitík "
        "nefnir hann Olof Palme, Kristrúnu Frostadóttur, Vilmund Gylfason og Willy Brandt. Í "
        "grunninn eru Kanye West og Daft Punk uppáhaldstónlistarmenn hans. Eftirlætisbókin er Úr "
        "fjötrum – Saga Alþýðuflokksins, og af kvikmyndum síðustu ára nefnir hann One Battle After "
        "Another og The Banshees of Inisherin. Ef hann þyrfti að flytja úr Reykjavík yrði Kópavogur "
        "fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Arnar Ingi Ingason er tónlistarmaður og hefur haft það að atvinnu undanfarin 11 ár.",
         "ruv_quote": "Ég heiti Arnar, ég er tónlistarmaður og hef haft það að atvinnu undanfarin 11 ár."},
        {"statement": "Hann er fæddur árið 1996, fæddur og uppalinn á Íslandi, og er aðfluttur Reykvíkingur, upprunalega úr Kópavogi og stoltur Bliki.",
         "ruv_quote": "1996 / Fæddur og uppalinn á Íslandi. / Ég er aðfluttur Reykvíkingur, upprunalega úr Kópavoginum og stoltur Bliki"},
        {"statement": "Hann hefur síðastliðin tæp 10 ár gert Vesturbæ Reykjavíkur að heimili sínu, með stuttu stoppi í Berlín, og býr í leiguíbúð í Vesturbænum.",
         "ruv_quote": "hef síðastliðin tæp 10 ár gert Vesturbæ Reykjavíkur að heimili mínu - með stuttu stoppi í Berlín. / Ég bý í leiguíbúð í Vesturbænum."},
        {"statement": "Hann á yndislega unnustu sem er að ljúka arkitektúrnámi í Brussel, sem þýðir að hann hefur undanfarin tvö ár verið tíður gestur þar í borg. Engin tenging við Evrópusambandið, enn.",
         "ruv_quote": "Á yndislega unnustu sem er að ljúka arkitektúrnámi í Brussel, sem þýðir að ég hef undanfarin 2 ár verið tíður gestur þar í borg. Engin tenging við Evrópusambandið, enn."},
        {"statement": "Arnar talar ensku og getur reddað sér á dönsku og þýsku.",
         "ruv_quote": "Ensku - get reddað mér á Dönsku og Þýsku."},
        {"statement": "Hann tók eitt ár í grafískri hönnun við LHÍ, lét þá staðar numið og fór á fullu inn í tónlistina.",
         "ruv_quote": "Ég tók eitt ár í grafískri hönnun við LHÍ, lét þá staðar numið og fór á fullu inn í tónlistina."},
        {"statement": "Hann hefur verið félagi í Samfylkingunni síðan 2018.",
         "ruv_quote": "Ég hef verið félagi í Samfylkingunni síðan 2018."},
        {"statement": "Arnar Ingi hefur brennandi áhuga á öllu sem viðkemur tónlist, knattspyrnu og pólitík.",
         "ruv_quote": "Ég hef brennandi áhuga á öllu sem við kemur tónlist, knattspyrnu og pólitík."},
        {"statement": "Eftir tíu ár langar hann að sjá borg sem heldur áfram að blómstra og iða af mannlífi. Helst væri hann til í að sjá Borgarlínuna í fullu fjöri og að byrjað væri að leggja drög að lest sem lægi beint úr hjarta borgarinnar í átt að Keflavíkurflugvelli. Eftir tíu ár myndi hann einnig vilja að menningarlíf borgarinnar væri blómlegra sem aldrei fyrr, að borgin væri útbúin tónleikastöðum fyrir allar stærðir og gerðir tónleika og að í það minnsta væri til einn alvöru technóklúbbur.",
         "ruv_quote": "Eftir 10 ár langar mig að sjá borg sem heldur áfram að blómstra og iða af mannlífi. Helst væri ég til í að sjá Borgarlínuna í fullu fjöri og að byrjað væri að leggja drög að lest sem lægi beint úr hjarta borgarinnar í átt að Keflavíkurflugvelli. Eftir 10 ár myndi ég einnig vilja að menningarlíf borgarinnar væri blómlegra sem aldrei fyrr.  Að borgin væri útbúin tónleikastöðum fyrir allar stærðir og gerðir tónleika og í það minnsta einum alvöru techno-klúbbi!"},
        {"statement": "Aðaláhugamál Arnars Inga eru tónlist, matargerð, knattspyrna og pólitík, og hann segist vera „semi unplayable“ ef hann fái þessa flokka í Bezzerwisser.",
         "ruv_quote": "Tónlist, matargerð, knattspyrna, pólitík. Er semi unplayable ef ég fæ þessa flokka í Bezzerwisser."},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hann Olof Palme, Kristrúnu Frostadóttur, Vilmund Gylfason og Willy Brandt.",
         "ruv_quote": "Olof Palme, Kristrún Frostadóttir, Vilmundur Gylfason & Willy Brandt."},
        {"statement": "Í grunninn eru Kanye West og Daft Punk uppáhaldstónlistarmenn hans.",
         "ruv_quote": "Í grunninn eru það Kanye West og Daft Punk."},
        {"statement": "Eftirlætisbókin er Úr fjötrum – Saga Alþýðuflokksins, og af kvikmyndum síðustu ára nefnir hann One Battle After Another og The Banshees of Inisherin.",
         "ruv_quote": "Úr fjötrum – Saga Alþýðuflokksins. / Á síðustu árum eru það One Battle After Another og The Banshees of Inisherin."},
        {"statement": "Ef hann þyrfti að flytja úr Reykjavík yrði Kópavogur fyrir valinu.",
         "ruv_quote": "Kópavogur."},
    ]
})

# 30: Stefán Þór Eysteinsson (7300-S-1)
ENTRIES.append({
    "ruv_id": "7300-S-1",
    "new_bio": (
        "Stefán Þór Eysteinsson er fæddur og uppalinn á Neskaupstað og starfar sem sérfræðingur "
        "og deildarstjóri hjá Matís ohf. á Neskaupstað. Hann lauk BA-prófi í líffræði frá Gonzaga "
        "University í Bandaríkjunum, meistaragráðu í matvælafræðum og doktorsprófi frá Háskóla "
        "Íslands. Stefán hefur verið virkur í sveitarstjórnarmálum Fjarðabyggðar og leiðir framboðs"
        "lista Samfylkingar og jafnaðarmanna í kosningum 2026. Hann leggur áherslu á jafnrétti á "
        "milli byggðakjarna, samráð við íbúa og uppbyggingu grunnþjónustu.\n\n"
        "Stefán er fæddur árið 1987 á Íslandi og býr í einbýlishúsi í Neskaupstað ásamt kærustu og "
        "tveimur börnum. Hann er matvælafræðingur og starfar sem fagstjóri hjá Matís. Hann talar "
        "ensku auk íslensku. Hann hefur setið í bæjarstjórn fyrir Fjarðalistann í fjögur ár og verið "
        "skráður í Samfylkinguna í þrjú ár.\n\n"
        "Stefán vill sjá Fjarðabyggð eftir tíu ár með sterka grunnþjónustu, raunverulegt jafnræði "
        "milli byggðarkjarna og fjölbreytt atvinnulíf — samfélag sem laðar að fólk vegna lífsgæða. "
        "Fyrirmynd hans í pólitík er Vigdís Finnbogadóttir.\n\n"
        "Áhugamál Stefáns eru útivist og að verja tíma með fjölskyldunni. Snow Patrol er í miklu "
        "uppáhaldi, eftirlætisbókin er Thinking, Fast and Slow eftir Daniel Kahneman og uppáhalds"
        "kvikmyndin Garden State. Ef hann þyrfti að flytja úr Fjarðabyggð yrði Akureyri fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Stefán er fæddur árið 1987 á Íslandi og býr í einbýlishúsi í Neskaupstað ásamt kærustu og tveimur börnum.",
         "ruv_quote": "1987 / Íslandi / Einbýlishúsi / Fæddur og uppalinn í Neskaupstað þar sem ég bý nú ásamt kærustu og tveimur börnum."},
        {"statement": "Hann er matvælafræðingur og starfar sem fagstjóri hjá Matís.",
         "ruv_quote": "Matvælafræðingur og starfa sem Fagstjóri hjá Matís"},
        {"statement": "Hann talar ensku auk íslensku.", "ruv_quote": "Ensku"},
        {"statement": "Hann hefur setið í bæjarstjórn fyrir Fjarðalistann í fjögur ár og verið skráður í Samfylkinguna í þrjú ár.",
         "ruv_quote": "Setið í bæjarstjórn fyrir Fjarðalistann í 4 ár og verið skráður í Samfylkinguna í 3 ár"},
        {"statement": "Stefán vill sjá Fjarðabyggð eftir tíu ár með sterka grunnþjónustu, raunverulegt jafnræði milli byggðarkjarna og fjölbreytt atvinnulíf — samfélag sem laðar að fólk vegna lífsgæða.",
         "ruv_quote": "Eftir tíu ár vil ég sjá Fjarðabyggð með sterka grunnþjónustu, raunverulegt jafnræði milli byggðarkjarna og fjölbreytt atvinnulíf. Samfélag sem laðar að fólk vegna lífsgæða"},
        {"statement": "Fyrirmynd hans í pólitík er Vigdís Finnbogadóttir.", "ruv_quote": "Vigdís Finnbogadóttir"},
        {"statement": "Áhugamál Stefáns eru útivist og að verja tíma með fjölskyldunni.",
         "ruv_quote": "Útivist og að verja tíma með fjölskyldunni"},
        {"statement": "Snow Patrol er í miklu uppáhaldi, eftirlætisbókin er Thinking, Fast and Slow eftir Daniel Kahneman og uppáhaldskvikmyndin Garden State.",
         "ruv_quote": "Snow Patrol er í miklu uppáhaldi / Thinking, fast and slow eftir Daniel Kahneman / Garden State"},
        {"statement": "Ef hann þyrfti að flytja úr Fjarðabyggð yrði Akureyri fyrir valinu.",
         "ruv_quote": "Akureyri"},
    ]
})

# 31: Valborg Ösp Á. Warén (7300-S-3)
ENTRIES.append({
    "ruv_id": "7300-S-3",
    "new_bio": (
        "Valborg Ösp Á. Warén er verkefnastjóri sem skipar 3. sæti á S-lista Fjarðalistans í "
        "Fjarðabyggð 2026. Hún kemur með reynslu í verkefnastjórnun og skipulagi. Valborg er fædd "
        "árið 1982 á Íslandi, er 43 ára og býr á Stöðvarfirði með tveimur börnum og hundi. Hún býr "
        "í einbýli og hefur lokið B.A.-prófi í stjórnmálafræði. Hún starfar sem verkefnisstjóri hjá "
        "Austurbrú og stýrir Brothættum byggðum á Stöðvarfirði. Hún talar ensku og getur reddað sér "
        "á skandinavísku, og man eftir að hafa skráð sig í flokkinn 2007.\n\n"
        "Valborg flutti aftur austur árið 2022 eftir tuttugu ára búsetu á ýmsum stöðum, bæði "
        "innanlands og erlendis. Hún er mjög sátt við að búa í Fjarðabyggð, en ef hún þyrfti að "
        "flytja annað yrði það í eitthvert annað sveitarfélag á Austurlandi.\n\n"
        "Valborg vill sveitarfélag þar sem daglegt líf gangi vel upp, með góða og aðgengilega "
        "þjónustu, jöfn tækifæri óháð búsetu, öflugt atvinnulíf og lifandi samfélag þar sem íbúar "
        "finna að á þá er hlustað. Sem fyrirmynd í pólitík nefnir hún Jóhönnu Sigurðardóttur fyrir "
        "skýra sýn á jafnræði, heiðarleika og hugrekki í stjórnmálum, og lítur helst til þeirra sem "
        "setja jafnræði, traust og velferð íbúa í forgang og byggja ákvarðanir á samtali við fólk.\n\n"
        "Valborg er ósvikinn Taylor Swift fan en algjör alæta á tónlist. Í frítíma sínum nýtur hún "
        "þess að vera með börnunum sínum, fara á kayak, hjóla og stunda snjóbretti, auk þess að hitta "
        "vini yfir góðum kaffibolla."
    ),
    "fact_check": [
        {"statement": "Valborg er fædd árið 1982 á Íslandi, er 43 ára og býr á Stöðvarfirði með tveimur börnum og hundi.",
         "ruv_quote": "1982 / Ísland / Ég er 43 ára og bý á Stöðvarfirði með tveimur börnum og hundi."},
        {"statement": "Hún býr í einbýli og hefur lokið B.A.-prófi í stjórnmálafræði.",
         "ruv_quote": "Einbýli / B.A í stjórnmálafræði"},
        {"statement": "Hún starfar sem verkefnisstjóri hjá Austurbrú og stýrir Brothættum byggðum á Stöðvarfirði.",
         "ruv_quote": "Verkefnisstjóri hjá Austurbrú og er stýri Brothættum byggðum á Stöðvarfirði"},
        {"statement": "Hún talar ensku og getur reddað sér á skandinavísku, og man eftir að hafa skráð sig í flokkinn 2007.",
         "ruv_quote": "ensku og get reddað mér á skandinavísku / Minnir að ég hafi skráð mig í flokkinn 2007"},
        {"statement": "Valborg flutti aftur austur árið 2022 eftir tuttugu ára búsetu á ýmsum stöðum, bæði innanlands og erlendis.",
         "ruv_quote": "Ég  flutti aftur austur árið 2022 eftir 20 ára búsetu á ýmsum stöðum, bæði hér innanlands og erlendis."},
        {"statement": "Hún er mjög sátt við að búa í Fjarðabyggð, en ef hún þyrfti að flytja annað yrði það í eitthvert annað sveitarfélag á Austurlandi.",
         "ruv_quote": "Ég er mjög sátt við að búa í Fjarðabyggð en ef ég þyrfti að flytja annað þá væri það í eitthvað annað sveitarfélag á Austurlandi"},
        {"statement": "Valborg vill sveitarfélag þar sem daglegt líf gangi vel upp, með góða og aðgengilega þjónustu, jöfn tækifæri óháð búsetu, öflugt atvinnulíf og lifandi samfélag þar sem íbúar finna að á þá er hlustað.",
         "ruv_quote": "Sveitarfélag þar sem daglegt líf gengur vel upp, með góða og aðgengilega þjónustu, jöfn tækifæri óháð búsetu, öflugt atvinnulíf og lifandi samfélag þar sem íbúar finna að á þá er hlustað."},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Jóhönnu Sigurðardóttur fyrir skýra sýn á jafnræði, heiðarleika og hugrekki í stjórnmálum, og lítur helst til þeirra sem setja jafnræði, traust og velferð íbúa í forgang og byggja ákvarðanir á samtali við fólk.",
         "ruv_quote": "Jóhanna Sigurðardóttir fyrir skýra sýn á jafnræði, heiðarleika og hugrekki í stjórnmálum. Ég lít helst til þeirra sem setja jafnræði, traust og velferð íbúa í forgang og byggja ákvarðanir á samtali við fólk."},
        {"statement": "Valborg er ósvikinn Taylor Swift fan en algjör alæta á tónlist.",
         "ruv_quote": "er algjör alæta á tónlist en er ósvikin Taylor Swift fan"},
        {"statement": "Í frítíma sínum nýtur hún þess að vera með börnunum sínum, fara á kayak, hjóla og stunda snjóbretti, auk þess að hitta vini yfir góðum kaffibolla.",
         "ruv_quote": "frítíma mínum nýt ég þess að vera með börnunum mínum, fara á kayak, hjóla og stunda snjóbretti, auk þess að hitta vini yfir góðum kaffibolla."},
    ]
})

# 32: Adam Ingi Guðlaugsson (7300-S-4)
ENTRIES.append({
    "ruv_id": "7300-S-4",
    "new_bio": (
        "Adam Ingi Guðlaugsson er á 4. sæti á S-lista Fjarðalistans í Fjarðabyggð í sveitarstjórnar"
        "kosningum 2026. Listinn samanstendur af meðlimum Fjarðalistans og Samfylkingar sem hafa "
        "starfað saman í bæjarstjórn. Hann er fæddur árið 2002 á Íslandi og hefur búið á Eskifirði "
        "nær allt sitt líf.\n\n"
        "Adam Ingi er vélfræðingur og rafvirki, og starfar sem vélstjóri og rafvirki í vaktavinnu. "
        "Hann hefur lokið iðnámi, talar ensku og býr í einbýlishúsi. Hann hefur verið skráður í "
        "flokknum í um tvö ár en tekið virkan þátt lengur. Hann hefur gaman af hreyfingu og að bæta "
        "sig á öllum sviðum, og hreyfing er aðaláhugamál hans.\n\n"
        "Adam Ingi vill að Fjarðabyggð verði öflugt sveitarfélag í atvinnulífi og menningu, sem "
        "fólk treystir þegar kemur að jöfnuði fyrir alla í samfélaginu. Sem fyrirmynd í pólitík "
        "nefnir hann Jóhann Pál Jóhannsson sem fyrsta nafnið sem poppi upp. Uppáhaldstónlistarmaður "
        "hans er Birnir, eftirlætisbókin Víti í Vestmannaeyjum eftir Gunna Helga og uppáhaldskvikmyndin "
        "Forrest Gump. Ef hann þyrfti að flytja úr Fjarðabyggð yrði Akureyri líklegast fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hann er fæddur árið 2002 á Íslandi og hefur búið á Eskifirði nær allt sitt líf.",
         "ruv_quote": "Er fæddur árið 2002 / Er fæddur á íslandi / hef búið á Eskifirði nær allt mitt líf."},
        {"statement": "Adam Ingi er vélfræðingur og rafvirki, og starfar sem vélstjóri og rafvirki í vaktavinnu.",
         "ruv_quote": "Ég er Vélfræðingur og Rafvirki / Ég starfa sem vélstjóri og Rafvirki í vaktavinnu"},
        {"statement": "Hann hefur lokið iðnámi, talar ensku og býr í einbýlishúsi.",
         "ruv_quote": "Iðnám / Ég tala ensku / Bý í einbýlishúsi"},
        {"statement": "Hann hefur verið skráður í flokknum í um tvö ár en tekið virkan þátt lengur.",
         "ruv_quote": "Skráður sirka 2 ár en tekið virkan þátt lengur"},
        {"statement": "Hann hefur gaman af hreyfingu og að bæta sig á öllum sviðum, og hreyfing er aðaláhugamál hans.",
         "ruv_quote": "Hef gaman að hreyfingu og að bæta mig á öllum sviðum! / Hreyfing"},
        {"statement": "Adam Ingi vill að Fjarðabyggð verði öflugt sveitarfélag í atvinnulífi og menningu, sem fólk treystir þegar kemur að jöfnuði fyrir alla í samfélaginu.",
         "ruv_quote": "Ég vill að Fjarðabyggð verði öflugt sveitarfélag í atvinnulífi og menningu sem fólk treystir þegar kemur að jöfnuði fyrir alla í þessu flotta samfélagi"},
        {"statement": "Sem fyrirmynd í pólitík nefnir hann Jóhann Pál Jóhannsson sem fyrsta nafnið sem poppi upp.",
         "ruv_quote": "Jóhann Páll Jóhannsson er fyrsta nafnið sem poppar upp"},
        {"statement": "Uppáhaldstónlistarmaður hans er Birnir, eftirlætisbókin Víti í Vestmannaeyjum eftir Gunna Helga og uppáhaldskvikmyndin Forrest Gump.",
         "ruv_quote": "Minn uppáhalds tónlistarmaður er Birnir / Víti í Vestmannaeyjum eftir Gunna Helga / Forrest Gump"},
        {"statement": "Ef hann þyrfti að flytja úr Fjarðabyggð yrði Akureyri líklegast fyrir valinu.",
         "ruv_quote": "Ég myndi líklegast flytja til Akureyrar"},
    ]
})

# 33: Joanna Katarzyna Mrowiec (7300-S-12)
ENTRIES.append({
    "ruv_id": "7300-S-12",
    "new_bio": (
        "Joanna Katarzyna Mrowiec, kölluð Asia, er 31 árs og býr á Eskifirði ásamt eiginmanni sínum. "
        "Hún er fædd árið 1994 í Póllandi og starfar sem enskukennari við Verkmenntaskóla "
        "Austurlands. Hún hefur lokið mastersgráðu (MA) og hefur fjölbreytta menntun og reynslu af "
        "kennslu. Auk íslensku talar hún ensku, pólsku, frönsku, ítölsku og arabísku. Hún býr í "
        "tvíbýli og hefur verið í Samfylkingunni og öðru félagshyggjufólki í nokkra mánuði.\n\n"
        "Joanna brennur fyrir skólamálum, náttúruvernd og jafnrétti og vill stuðla að jöfnum "
        "tækifærum fyrir alla. Hún býður sig fram til að vera rödd fólks af erlendum uppruna og "
        "styrkja samfélagið í Fjarðabyggð.\n\n"
        "Eftir tíu ár vill Joanna að sveitarfélagið sé sterkt og samheldið samfélag þar sem allir "
        "hafa jöfn tækifæri, óháð uppruna. Hún vill sjá öflugt skólakerfi, meiri áherslu á náttúru"
        "vernd og sjálfbærni og góð atvinnutækifæri fyrir íbúa. Þetta á að vera öruggt, opið og "
        "lifandi samfélag þar sem fólki líður vel og vill búa til framtíðar.\n\n"
        "Aðaláhugamál Joönnu eru tungumál og náttúran. Sem fyrirmyndir í pólitík nefnir hún Kristrúnu "
        "Frostadóttur og Eydísi Ásbjörnsdóttur. Uppáhaldstónlistarmenn hennar eru Hipsumhaps. "
        "Eftirlætisbókin er The Golden Notebook eftir Doris Lessing, sem fjallar á djúpan og "
        "margbrotinn hátt um sjálfsmynd, sköpun og líf kvenna. Uppáhaldskvikmynd hennar er Into "
        "the Wild (2007) eftir Sean Penn, sem heillar hana með fallegri náttúru, sterku ferðalagi "
        "og leit að merkingu í lífinu. Ef hún þyrfti að flytja úr Fjarðabyggð yrði Múlaþing fyrir "
        "valinu."
    ),
    "fact_check": [
        {"statement": "Joanna Katarzyna Mrowiec, kölluð Asia, er 31 árs og býr á Eskifirði ásamt eiginmanni sínum.",
         "ruv_quote": "Ég heiti Joanna Katarzyna Mrowiec (Asia), er 31 árs og bý á Eskifirði með eiginmanni mínum."},
        {"statement": "Hún er fædd árið 1994 í Póllandi og starfar sem enskukennari við Verkmenntaskóla Austurlands.",
         "ruv_quote": "1994 / Póllandi / Ég starfa sem enskukennari við Verkmenntaskóla Austurlands"},
        {"statement": "Hún hefur lokið mastersgráðu (MA) og hefur fjölbreytta menntun og reynslu af kennslu.",
         "ruv_quote": "Masters gráða (MA) / hef fjölbreytta menntun og reynslu í kennslu."},
        {"statement": "Auk íslensku talar hún ensku, pólsku, frönsku, ítölsku og arabísku.",
         "ruv_quote": "Ensku, pólsku, frönsku, ítölsku og arabísku"},
        {"statement": "Hún býr í tvíbýli og hefur verið í Samfylkingunni og öðru félagshyggjufólki í nokkra mánuði.",
         "ruv_quote": "Tvíbýli / Nokkra mánuði"},
        {"statement": "Joanna brennur fyrir skólamálum, náttúruvernd og jafnrétti og vill stuðla að jöfnum tækifærum fyrir alla.",
         "ruv_quote": "Ég brenn fyrir skólamálum, náttúruvernd og jafnrétti og vil stuðla að jöfnum tækifærum fyrir alla."},
        {"statement": "Hún býður sig fram til að vera rödd fólks af erlendum uppruna og styrkja samfélagið í Fjarðabyggð.",
         "ruv_quote": "Ég býð mig fram til að vera rödd fólks af erlendum uppruna og styrkja samfélagið í Fjarðabyggð."},
        {"statement": "Eftir tíu ár vill Joanna að sveitarfélagið sé sterkt og samheldið samfélag þar sem allir hafa jöfn tækifæri, óháð uppruna. Hún vill sjá öflugt skólakerfi, meiri áherslu á náttúruvernd og sjálfbærni og góð atvinnutækifæri fyrir íbúa. Þetta á að vera öruggt, opið og lifandi samfélag þar sem fólki líður vel og vill búa til framtíðar.",
         "ruv_quote": "Eftir tíu ár vil ég að sveitarfélagið mitt sé sterkt og samheldið samfélag þar sem allir hafa jöfn tækifæri, óháð uppruna. Ég vil sjá öflugt skólakerfi, meiri áherslu á náttúruvernd og sjálfbærni og góð atvinnutækifæri fyrir íbúa. Þetta á að vera öruggt, opið og lifandi samfélag þar sem fólki líður vel og vill búa til framtíðar."},
        {"statement": "Aðaláhugamál Joönnu eru tungumál og náttúran.", "ruv_quote": "Tungumál og náttúran"},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hún Kristrúnu Frostadóttur og Eydísi Ásbjörnsdóttur.",
         "ruv_quote": "Kristrún Frostadóttir, Eydís Ásbjörnsdóttir"},
        {"statement": "Uppáhaldstónlistarmenn hennar eru Hipsumhaps.", "ruv_quote": "Hipsumhaps"},
        {"statement": "Eftirlætisbókin er The Golden Notebook eftir Doris Lessing, sem fjallar á djúpan og margbrotinn hátt um sjálfsmynd, sköpun og líf kvenna.",
         "ruv_quote": "Eftirlætisbókin mín er The Golden Notebook eftir Doris Lessing, sem fjallar á djúpan og margbrotinn hátt um sjálfsmynd, sköpun og líf kvenna."},
        {"statement": "Uppáhaldskvikmynd hennar er Into the Wild (2007) eftir Sean Penn, sem heillar hana með fallegri náttúru, sterku ferðalagi og leit að merkingu í lífinu.",
         "ruv_quote": "Kvikmyndin sem ég held mest upp á er Into the Wild (2007) eftir Sean Penn, sem heillar mig með fallegri náttúru, sterku ferðalagi og leit að merkingu í lífinu."},
        {"statement": "Ef hún þyrfti að flytja úr Fjarðabyggð yrði Múlaþing fyrir valinu.", "ruv_quote": "Múlaþing"},
    ]
})

# 34: Anna Sigrún Jóhönnudóttir (7300-S-15)
ENTRIES.append({
    "ruv_id": "7300-S-15",
    "new_bio": (
        "Anna Sigrún Jóhönnudóttir er fædd árið 1983 á Íslandi og býr með manni sínum, þremur "
        "börnum og hundi á Reyðarfirði. Hún er öryrki og verslunareigandi og rekur básaleiguverslun "
        "í samvinnu við aðra. Anna Sigrún brennur fyrir mannréttindum og skólamálum. Hún býr í "
        "einbýli, talar ensku og smá dönsku, og hefur lokið starfsnámi. Hún hefur verið í sínum "
        "flokki þetta ár.\n\n"
        "Sem fyrirmynd í pólitík nefnir hún Hjördísi Helgu Seljan. Aðaláhugamál hennar er allskonar "
        "handverk, og uppáhaldstónlistarmenn hennar eru Fugees. Ef hún þyrfti að flytja úr "
        "Fjarðabyggð yrði Dalvíkurbyggð fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Anna Sigrún Jóhönnudóttir er fædd árið 1983 á Íslandi og býr með manni sínum, þremur börnum og hundi á Reyðarfirði.",
         "ruv_quote": "1983 / Íslandi / Ég er bý með manninum mínum, 3 börnum og hundi á Reyðarfirði."},
        {"statement": "Hún er öryrki og verslunareigandi og rekur básaleiguverslun í samvinnu við aðra.",
         "ruv_quote": "Öryrki og verslunareigandi / rek básaleiguverslun í samvinnu við aðra."},
        {"statement": "Anna Sigrún brennur fyrir mannréttindum og skólamálum.",
         "ruv_quote": "Ég brenn fyrir mannréttindi og skólamál."},
        {"statement": "Hún býr í einbýli, talar ensku og smá dönsku, og hefur lokið starfsnámi.",
         "ruv_quote": "Einbýli / Ensku, smá dönsku / Starfsnám"},
        {"statement": "Hún hefur verið í sínum flokki þetta ár.", "ruv_quote": "Þetta ár"},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Hjördísi Helgu Seljan.",
         "ruv_quote": "Hjördís Helga Seljan"},
        {"statement": "Aðaláhugamál hennar er allskonar handverk, og uppáhaldstónlistarmenn hennar eru Fugees.",
         "ruv_quote": "Allskonar handverk / Fugees"},
        {"statement": "Ef hún þyrfti að flytja úr Fjarðabyggð yrði Dalvíkurbyggð fyrir valinu.",
         "ruv_quote": "Dalvíkurbyggð"},
    ]
})

# 35: Birgitta Ragnarsdóttir (8716-S-1)
ENTRIES.append({
    "ruv_id": "8716-S-1",
    "new_bio": (
        "Birgitta Ragnarsdóttir er tollamiðlari og oddviti S-listans í Hveragerði, sameiginlegs "
        "framboðs Samfylkingarinnar og óháðra. Hún hefur verið virk í starfi Samfylkingarfélagsins "
        "á svæðinu og leiddi sömuleiðis sameiginlegt framboð flokksins í Hveragerði í sveitar"
        "stjórnarkosningunum 2022. Á yfirstandandi kjörtímabili hefur hún meðal annars beitt sér í "
        "húsnæðismálum og talað fyrir samstarfi við óhagnaðardrifin húsnæðisfélög, betri nýtingu "
        "skipulagsvalds sveitarfélagsins við lóðir fyrir hagkvæmt húsnæði og þátttöku í almenna "
        "íbúðakerfinu. Birgitta hefur einnig verið virk í umræðu um skipulag bæjarins og tækifæri "
        "ungs fólks til að festa rætur í Hveragerði. Hún leggur áherslu á að gera bæinn að "
        "fjölskylduvænum stað þar sem venjulegt fólk hafi raunhæfa möguleika á að koma sér upp "
        "heimili.\n\n"
        "Birgitta er fædd árið 1989 á Íslandi og vinnur sem tollmiðlari, ásamt því að sitja í stjórn "
        "VR og stjórn LÍV. Hún hefur lokið framhaldsskólaprófi og ýmsum námskeiðum, talar ensku og "
        "norsku, og býr í eigin húsnæði — einbýli. Hún segist vera samviskusöm og jákvæð manneskja "
        "sem leggur áherslu á heiðarleika og góð samskipti, og hefur mikinn áhuga á samfélaginu sínu "
        "og vill leggja sitt af mörkum til að gera það enn betra. Hún hefur lengi verið fylgjandi "
        "Samfylkingarinnar en skráði sig formlega í flokkinn snemma á þessu ári.\n\n"
        "Birgittu langar að sjá Hveragerði í fullum blóma eftir tíu ár, með fjölbreytt húsnæði sem "
        "hentar ólíkum þörfum — hvort sem um ræðir leiguhúsnæði, félagslegt húsnæði, íbúðir eða "
        "séreignir. Hún vill einnig að öll helsta grunnþjónusta sé aðgengileg innan bæjarins svo "
        "íbúar þurfi ekki að sækja þjónustu til nágrannasveitarfélaga, og sér fyrir sér samheldið og "
        "öflugt samfélag þar sem fólki líður vel, og að rekstur bæjarins sé kominn í traustan og "
        "sjálfbæran farveg.\n\n"
        "Birgitta á sér enga fyrirmynd í pólitík, en segir að góð fyrirmynd væri manneskja sem "
        "vinnur að heilindum, sýnir ábyrgð og virðingu í samskiptum og hefur kjark til að taka "
        "erfiðar ákvarðanir þegar þörf krefur. Una Torfa er í miklu uppáhaldi þessa dagana. Eftir"
        "lætisbókin sem stóð upp úr á síðasta ári var Áttunda undur veraldar eftir Lilju Rós "
        "Agnarsdóttur, og uppáhaldskvikmyndin er Sound of Music. Aðaláhugamál hennar eru lestur og "
        "prjón, en svo var hún á fullu að hlaupa áður en pólitíkin tók yfir allt líf hennar. Ef hún "
        "þyrfti að flytja úr Hveragerði yrði Ölfus fyrir valinu, og þá helst í húsnæði sem hún myndi "
        "byggja sjálf og vera með hesta og geitur í garðinum."
    ),
    "fact_check": [
        {"statement": "Birgitta er fædd árið 1989 á Íslandi og vinnur sem tollmiðlari, ásamt því að sitja í stjórn VR og stjórn LÍV.",
         "ruv_quote": "1989 / Íslandi / Vinn sem tollmiðlari ásamt því að sitja í stjórn VR og stjórn LÍV"},
        {"statement": "Hún hefur lokið framhaldsskólaprófi og ýmsum námskeiðum, talar ensku og norsku, og býr í eigin húsnæði — einbýli.",
         "ruv_quote": "Framhaldsskólapróf, en hef þó lokið ýmsum námskeiðum. / Ensku og norsku / Eigið húsnæði - einbýli"},
        {"statement": "Hún segist vera samviskusöm og jákvæð manneskja sem leggur áherslu á heiðarleika og góð samskipti, og hefur mikinn áhuga á samfélaginu sínu og vill leggja sitt af mörkum til að gera það enn betra.",
         "ruv_quote": "Ég er samviskusöm og jákvæð manneskja sem legg áherslu á heiðarleika og góð samskipti. Ég hef mikinn áhuga á samfélaginu mínu og vil leggja mitt af mörkum til að gera það enn betra."},
        {"statement": "Hún hefur lengi verið fylgjandi Samfylkingarinnar en skráði sig formlega í flokkinn snemma á þessu ári.",
         "ruv_quote": "Hef lengi verið fylgjandi Samfylkingarinnar en skráði mig formlega í flokkinn snemma á þessu ári."},
        {"statement": "Birgittu langar að sjá Hveragerði í fullum blóma eftir tíu ár, með fjölbreytt húsnæði sem hentar ólíkum þörfum — hvort sem um ræðir leiguhúsnæði, félagslegt húsnæði, íbúðir eða séreignir. Hún vill einnig að öll helsta grunnþjónusta sé aðgengileg innan bæjarins svo íbúar þurfi ekki að sækja þjónustu til nágrannasveitarfélaga, og sér fyrir sér samheldið og öflugt samfélag þar sem fólki líður vel, og að rekstur bæjarins sé kominn í traustan og sjálfbæran farveg.",
         "ruv_quote": "Mig langar að sjá Hveragerði í fullum blóma eftir tíu ár, þar sem fjölbreytt húsnæði er í boði sem hentar ólíkum þörfum – hvort sem um ræðir leiguhúsnæði, félagslegt húsnæði, íbúðir eða séreignir. Einnig vil ég sjá að öll helsta grunnþjónusta sé aðgengileg innan bæjarins, svo íbúar þurfi ekki að sækja þjónustu til nágrannasveitarfélaga. Ég sé fyrir mér samheldið og öflugt samfélag þar sem fólki líður vel, og að rekstur bæjarins sé kominn í traustan og sjálfbæran farveg."},
        {"statement": "Birgitta á sér enga fyrirmynd í pólitík, en segir að góð fyrirmynd væri manneskja sem vinnur að heilindum, sýnir ábyrgð og virðingu í samskiptum og hefur kjark til að taka erfiðar ákvarðanir þegar þörf krefur.",
         "ruv_quote": "Ég á mér enga fyrirmynd í pólitík en ég myndi segja að góð fyrirmynd í pólitík væri manneskja sem vinnur að heilindum, sýnir ábyrgð og virðingu í samskiptum og hefur kjark til að taka erfiðar ákvarðanir þegar þörf krefur."},
        {"statement": "Una Torfa er í miklu uppáhaldi þessa dagana.", "ruv_quote": "Una Torfa er í miklu uppháldi þessa daganna."},
        {"statement": "Eftirlætisbókin sem stóð upp úr á síðasta ári var Áttunda undur veraldar eftir Lilju Rós Agnarsdóttur, og uppáhaldskvikmyndin er Sound of Music.",
         "ruv_quote": "sú bók sem stóð upp úr á seinasta ári var Áttunda undur veraldar eftir  Lilju Rós Agnarsdóttir. / Sound of music"},
        {"statement": "Aðaláhugamál hennar eru lestur og prjón, en svo var hún á fullu að hlaupa áður en pólitíkin tók yfir allt líf hennar.",
         "ruv_quote": "Lestur og prjón svona helst en svo var ég á fullu að hlaupa áður en pólitíkin tók yfir allt líf mitt."},
        {"statement": "Ef hún þyrfti að flytja úr Hveragerði yrði Ölfus fyrir valinu, og þá helst í húsnæði sem hún myndi byggja sjálf og vera með hesta og geitur í garðinum.",
         "ruv_quote": "Ölfus yrði fyrir valinu, og þá helst í húsnæði sem ég myndi byggja sjálf og vera með hesta og geitur í garðinum."},
    ]
})

# 36: Þorsteinn Hjartarson (8716-S-2)
ENTRIES.append({
    "ruv_id": "8716-S-2",
    "new_bio": (
        "Þorsteinn Hjartarson er fyrrverandi fræðslustjóri og skipar 2. sæti á S-lista Samfylkingar "
        "og óflokksbundinna í Hveragerðisbæ fyrir sveitarstjórnarkosningarnar 2026. Hann er fæddur "
        "árið 1957 á Íslandi og ólst upp í Hveragerði. Þorsteinn er giftur Ernu Ingvarsdóttur "
        "kennara, og þau eiga fjögur uppkomin börn og sex barnabörn. Hann er kominn á eftirlaun, en "
        "starfaði lengi í skóla- og velferðarmálum, m.a. sem fræðslustjóri og sviðsstjóri "
        "fjölskyldusviðs Árborgar. Hann er með M.Ed.-próf í stjórnun menntastofnana, talar ensku og "
        "dönsku og hrafl í sænsku, og hefur verið í Samfylkingunni frá stofnun hennar árið 2000. "
        "Hann býr í einbýlishúsi.\n\n"
        "Á yngri árum var Þorsteinn í fremstu röð í sundi, stundaði dýfingar, spilaði fótbolta með "
        "Hveragerði í 3. deild og landaði einum Íslandsmeistaratitli í blaki með HK. Hestamennska og "
        "tónlist hafa alltaf skipað stóran sess hjá honum. Á námsárunum bjó hann í Sønderborg, á "
        "Laugarvatni, í Kaupmannahöfn og Reykjavík.\n\n"
        "Þorsteinn vill að Hveragerði verði heilsubær sem stendur undir nafni, þar sem passað er upp "
        "á grænu svæðin og náttúruna sem umlykur bæinn. Hann vill að skólar og öll þjónusta við fólk "
        "á öllum aldri verði til fyrirmyndar og að mikið samráð verði haft við íbúa um hin ýmsu mál. "
        "Aðstaða fyrir íþróttir og tómstundir verði einnig til fyrirmyndar, með áherslu á fjölbreytt "
        "íþróttatilboð og blómlegt starf eins og hjá skátum, hestamönnum og golfurum, og að "
        "heilsuefling eldri borgara verði enn öflugri.\n\n"
        "Aðaláhugamál Þorsteins eru pólitík og tónlist. Hann hefur einnig gaman af hestum, útivist, "
        "íþróttum, ferðalögum og góðri samveru með skemmtilegu fólki. Fyrirmynd hans í pólitík er "
        "Olof Palme. Uppáhaldstónlistarmaður hans er Chick Corea, eftirlætisbókin Atómstöðin og "
        "uppáhaldskvikmyndin Snerting. Ef hann þyrfti að flytja úr Hveragerði yrði Hafnarfjörður "
        "fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hann er fæddur árið 1957 á Íslandi og ólst upp í Hveragerði.",
         "ruv_quote": "1957 / Íslandi / Ég ólst upp í Hveragerði"},
        {"statement": "Þorsteinn er giftur Ernu Ingvarsdóttur kennara, og þau eiga fjögur uppkomin börn og sex barnabörn.",
         "ruv_quote": "Ég giftur Ernu Ingvarsdóttur, kennara, og eigum við fjögur uppkomin börn og sex barnabörn."},
        {"statement": "Hann er kominn á eftirlaun, en starfaði lengi í skóla- og velferðarmálum, m.a. sem fræðslustjóri og sviðsstjóri fjölskyldusviðs Árborgar.",
         "ruv_quote": "Eldri borgari. Starfaði lengi í skóla- og velferðarmálum, m.a. sem fræðslustjóri og sviðsstjóri fjölskyldusviðs Árborgar."},
        {"statement": "Hann er með M.Ed.-próf í stjórnun menntastofnana, talar ensku og dönsku og hrafl í sænsku, og hefur verið í Samfylkingunni frá stofnun hennar árið 2000.",
         "ruv_quote": "Er með M.Ed.-próf í stjórnun menntastofnana / Ensku og dönsku og hrafl í sænsku. / Hef verið í Samfylkingunni frá stofnun hennar árið 2000."},
        {"statement": "Hann býr í einbýlishúsi.", "ruv_quote": "Einbýlishúsi."},
        {"statement": "Á yngri árum var Þorsteinn í fremstu röð í sundi, stundaði dýfingar, spilaði fótbolta með Hveragerði í 3. deild og landaði einum Íslandsmeistaratitli í blaki með HK.",
         "ruv_quote": "á yngri árum var ég í fremstu röð í sundi, stundaði dýfingar, spilaði fótbolta með Hveragerði í 3. deild og landaði einum Íslandsmeistaratitli í blaki með HK."},
        {"statement": "Hestamennska og tónlist hafa alltaf skipað stóran sess hjá honum.",
         "ruv_quote": "Einnig hafa hestamennska og tónlist alltaf skipað stóran sess."},
        {"statement": "Á námsárunum bjó hann í Sønderborg, á Laugarvatni, í Kaupmannahöfn og Reykjavík.",
         "ruv_quote": "Á námsárunum bjó ég í Sønderborg, Laugarvatni, Kaupmannahöfn og Reykjavík."},
        {"statement": "Þorsteinn vill að Hveragerði verði heilsubær sem stendur undir nafni, þar sem passað er upp á grænu svæðin og náttúruna sem umlykur bæinn. Hann vill að skólar og öll þjónusta við fólk á öllum aldri verði til fyrirmyndar og að mikið samráð verði haft við íbúa um hin ýmsu mál. Aðstaða fyrir íþróttir og tómstundir verði einnig til fyrirmyndar, með áherslu á fjölbreytt íþróttatilboð og blómlegt starf eins og hjá skátum, hestamönnum og golfurum, og að heilsuefling eldri borgara verði enn öflugri.",
         "ruv_quote": "Að Hveragerði verði heilsubær sem stendur undir nafni. Það er passað upp á grænu svæðin og náttúruna sem umlykur bæinn. Skólar og öll þjónusta við fólk á öllum aldri er til fyrirmyndar og mikið samráð er við íbúana um hin ýmsu mál. Aðstaða fyrir íþróttir og tómstundir er einnig til fyrirmyndar. Áhersla verði lögð á fjölbreytt íþróttatilboð og starf eins og skáta, hestamanna og golfara verði blómlegt. Heilsuefling eldri borgara enn öflugri"},
        {"statement": "Aðaláhugamál Þorsteins eru pólitík og tónlist. Hann hefur einnig gaman af hestum, útivist, íþróttum, ferðalögum og góðri samveru með skemmtilegu fólki.",
         "ruv_quote": "Pólitík og tónlist. Hef einnig gaman af hestum, útivist, íþróttum, ferðalögum og góðri samveru með skemmtilegu fólki."},
        {"statement": "Fyrirmynd hans í pólitík er Olof Palme.", "ruv_quote": "Olof Palme."},
        {"statement": "Uppáhaldstónlistarmaður hans er Chick Corea, eftirlætisbókin Atómstöðin og uppáhaldskvikmyndin Snerting.",
         "ruv_quote": "Chick Corea / Atómstöðin / Snerting"},
        {"statement": "Ef hann þyrfti að flytja úr Hveragerði yrði Hafnarfjörður fyrir valinu.",
         "ruv_quote": "Hafnarfjörður."},
    ]
})

# 37: Maria de Araceli Quintana (8716-S-3)
ENTRIES.append({
    "ruv_id": "8716-S-3",
    "new_bio": (
        "Maria Araceli er dans- og leiklistarkennari og skipar 3. sæti á S-lista Samfylkingarinnar "
        "og óflokksbundinna í Hveragerði fyrir sveitarstjórnarkosningarnar 2026. Hún er fædd árið "
        "1990 á Íslandi og talar spænsku og ensku auk íslensku. Maria starfar sem vinnustaðaeftirlits"
        "fulltrúi hjá stéttarfélagi og dans- og leiklistarkennari. Hún hefur lokið BS-prófi í "
        "viðskiptafræði með áherslu á verkefnastjórnun og býr í eigin húsnæði.\n\n"
        "Maria vill að Hveragerði verði eftir tíu ár með ábyrgri stjórnsýslu sem leggur málefni "
        "barna og ungmenna í forgang. Hún vill einnig að ásýnd bæjarins haldist að miklu leyti "
        "óbreytt, þ.e. að bærinn stækki ekki um of á stuttum 10 árum heldur í takt við innviði.\n\n"
        "Aðaláhugamál Maríu eru hreyfing, ferðalög, dans og góð matarboð. Sem fyrirmynd í pólitík "
        "nefnir hún Ásu Berglind. Hún heldur upp á Guns and Roses og GDRN, eftirlætisbókin er Ég "
        "fremur en þú og uppáhaldskvikmyndirnar Moulin Rouge og Harry Potter. Ef hún þyrfti að "
        "flytja úr Hveragerði yrði Akureyri fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hún er fædd árið 1990 á Íslandi og talar spænsku og ensku auk íslensku.",
         "ruv_quote": "1990 / Íslandi / Spænsku og ensku"},
        {"statement": "Maria starfar sem vinnustaðaeftirlitsfulltrúi hjá stéttarfélagi og dans- og leiklistarkennari.",
         "ruv_quote": "Vinnustaðaeftirlitsfulltrúi hjá stéttarfélagi og dans- og leiklistarkennari"},
        {"statement": "Hún hefur lokið BS-prófi í viðskiptafræði með áherslu á verkefnastjórnun og býr í eigin húsnæði.",
         "ruv_quote": "BS próf í Viðskiptafræði með áherslu á verkefnastjórnun / Eigin húsnæði"},
        {"statement": "Maria vill að Hveragerði verði eftir tíu ár með ábyrgri stjórnsýslu sem leggur málefni barna og ungmenna í forgang. Hún vill einnig að ásýnd bæjarins haldist að miklu leyti óbreytt, þ.e. að bærinn stækki ekki um of á stuttum 10 árum heldur í takt við innviði.",
         "ruv_quote": "Með ábyrgri stjórnsýslu sem leggur málefni barna og ungmenna í forgunn. Eg vil einnig að ásýnd bæjarins haldist að miklu leyti óbreytt, þ.e. að bærinn stækki ekki um of á stuttum 10 árum heldur í takt við innviði."},
        {"statement": "Aðaláhugamál Maríu eru hreyfing, ferðalög, dans og góð matarboð.",
         "ruv_quote": "Hreyfing, ferðalög, dans og góð matarboð"},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Ásu Berglind.",
         "ruv_quote": "Ása Berglind"},
        {"statement": "Hún heldur upp á Guns and Roses og GDRN, eftirlætisbókin er Ég fremur en þú og uppáhaldskvikmyndirnar Moulin Rouge og Harry Potter.",
         "ruv_quote": "Guns and Roses og GDRN / Ég fremur en þú / Moulin Rouge og Harry Potter"},
        {"statement": "Ef hún þyrfti að flytja úr Hveragerði yrði Akureyri fyrir valinu.",
         "ruv_quote": "Akureyri"},
    ]
})

# 38: Arnar Hannes Halldórsson (8716-S-6)
ENTRIES.append({
    "ruv_id": "8716-S-6",
    "new_bio": (
        "Arnar Hannes Halldórsson er kvæntur tveggja barna faðir, fæddur árið 1966 á Íslandi. Hann "
        "er byggingarverkfræðingur og verkefnisstjóri og vinnur í Hafnarfirði. Hann hefur lokið "
        "meistaraprófi í verkfræði, diplom-Ingenieur, og talar þýsku nokkuð vel auk íslensku, en "
        "babblar ensku ef þarf. Hann býr í raðhúsi.\n\n"
        "Arnar vill að Hveragerði verði aðeins stærra eftir tíu ár og með alla innviði í góðum "
        "málum. Ef hann þyrfti að flytja úr Hveragerði yrði Hafnarfjörður fyrir valinu.\n\n"
        "Áhugamál Arnars eru tónlist, veiði og ýmis garðverk. Eftirlætisbók hans er Góði dátinn Svejk."
    ),
    "fact_check": [
        {"statement": "Arnar Hannes Halldórsson er kvæntur tveggja barna faðir, fæddur árið 1966 á Íslandi.",
         "ruv_quote": "Kvæntur tveggja barna faðir. / 1966 / Íslandi"},
        {"statement": "Hann er byggingarverkfræðingur og verkefnisstjóri og vinnur í Hafnarfirði.",
         "ruv_quote": "Er byggingarverkfræðingur og vinn í Hafnarfirði. / Byggingarverkfræðingur,  verkefnisstjóri."},
        {"statement": "Hann hefur lokið meistaraprófi í verkfræði, diplom-Ingenieur, og talar þýsku nokkuð vel auk íslensku, en babblar ensku ef þarf.",
         "ruv_quote": "Master í verkfræði, diplom Ingenieur / Þýsku nokkuð vel en babbla ensku ef þarf."},
        {"statement": "Hann býr í raðhúsi.", "ruv_quote": "Raðhúsi."},
        {"statement": "Arnar vill að Hveragerði verði aðeins stærra eftir tíu ár og með alla innviði í góðum málum.",
         "ruv_quote": "Aðeins stærra og með alla innviði í góðum málum."},
        {"statement": "Ef hann þyrfti að flytja úr Hveragerði yrði Hafnarfjörður fyrir valinu.",
         "ruv_quote": "Hafnarfjörður"},
        {"statement": "Áhugamál Arnars eru tónlist, veiði og ýmis garðverk.",
         "ruv_quote": "Tónlist, veiði, garðverk ýmis."},
        {"statement": "Eftirlætisbók hans er Góði dátinn Svejk.",
         "ruv_quote": "Góði dátinn Svejk."},
    ]
})

# 39: Árný Fjóla Ásmundsdóttir (8716-S-7)
ENTRIES.append({
    "ruv_id": "8716-S-7",
    "new_bio": (
        "Árný Fjóla Ásmundsdóttir er óflokksbundinn frambjóðandi á lista Samfylkingarinnar og "
        "óflokksbundinna í Hveragerði. Hún er fædd árið 1991 á Íslandi og lýsir sér sem sveitastúlku "
        "frá Skeiðum. Hún hefur búið í Hveragerði í eitt ár, eftir að hafa búið í Þýskalandi í 11 ár, "
        "og hefur farið víða erlendis. Hún kemur inn í bæinn með ferskan hug og víðsýni.\n\n"
        "Árný talar þýsku, ensku og dönsku, hefur lokið námi á framhaldsskólastigi og starfar sem "
        "listakona. Hún býr í einbýli.\n\n"
        "Árný vill að Hveragerði verði bær sem einkennist af náttúru, list og nágrannakærleik. Ef "
        "hún þyrfti að flytja úr sveitarfélaginu myndi hún flytja erlendis.\n\n"
        "Aðaláhugamál Árnýjar er að mála náttúrumyndir. Uppáhaldstónlistarmaður hennar er Daði Freyr "
        "Pétursson, eftirlætisbókin Sagan af Pí og uppáhaldskvikmyndin Lion King."
    ),
    "fact_check": [
        {"statement": "Hún er fædd árið 1991 á Íslandi og lýsir sér sem sveitastúlku frá Skeiðum.",
         "ruv_quote": "1991 / Ísland / Sveitastúlka frá Skeiðum."},
        {"statement": "Hún hefur búið í Hveragerði í eitt ár, eftir að hafa búið í Þýskalandi í 11 ár, og hefur farið víða erlendis.",
         "ruv_quote": "Hef búið í Hveragerði í eitt ár eftir að hafa búið í Þýskalandi í 11ár. Hef  farið víða erlendis"},
        {"statement": "Hún kemur inn í bæinn með ferskan hug og víðsýni.",
         "ruv_quote": "kem inn í bæinn með ferskan hug og víðsýni."},
        {"statement": "Árný talar þýsku, ensku og dönsku, hefur lokið námi á framhaldsskólastigi og starfar sem listakona.",
         "ruv_quote": "Þýsku. Ensku. Dönsku / Framhaldsskóli / Listakona"},
        {"statement": "Hún býr í einbýli.", "ruv_quote": "Einbýli"},
        {"statement": "Árný vill að Hveragerði verði bær sem einkennist af náttúru, list og nágrannakærleik.",
         "ruv_quote": "Bær sem einkennist af náttúru, list og nágrannakærleik."},
        {"statement": "Ef hún þyrfti að flytja úr sveitarfélaginu myndi hún flytja erlendis.",
         "ruv_quote": "Myndi flytja erlendis"},
        {"statement": "Aðaláhugamál Árnýjar er að mála náttúrumyndir.", "ruv_quote": "Ég mála náttúrumyndir"},
        {"statement": "Uppáhaldstónlistarmaður hennar er Daði Freyr Pétursson, eftirlætisbókin Sagan af Pí og uppáhaldskvikmyndin Lion King.",
         "ruv_quote": "Daði Freyr Pétursson / Sagan af Pí / Lion King"},
    ]
})

# 40: Kristín Lilja Th. Björnsdóttir (8716-S-9)
ENTRIES.append({
    "ruv_id": "8716-S-9",
    "new_bio": (
        "Kristín Lilja Thorlacius Björnsdóttir er bókasafns- og upplýsingafræðingur og gegnir starfi "
        "gæðastjóra bókasafnskerfis hjá Landsbókasafni Íslands – Háskólabókasafni. Hún skipar 9. "
        "sæti á S-lista Samfylkingarinnar og óflokksbundinna í Hveragerði fyrir sveitarstjórnar"
        "kosningarnar 2026. Kristín er fædd árið 1990 á Íslandi og hefur lokið MIS-prófi í "
        "upplýsingafræði. Hún býr með eiginmanni sínum, Gunnlaugi Bjarnasyni, og þremur börnum "
        "þeirra. Hún leggur áherslu á málefni barna og ungmenna, menningarmál og vel ígrundaða "
        "uppbyggingu bæjarins.\n\n"
        "Kristín vonar að Hveragerði haldi áfram að vera blómlegur menningarbær og að bærinn stækki "
        "hæfilega mikið þannig að innviðir geti haldið í við íbúafjölda.\n\n"
        "Aðaláhugamál Kristínar er súrdeigsbakstur. Hún elskar söngleiki og hefur undanfarið verið "
        "að hlusta mikið á Hadestown, og er svo alltaf hrifin af Fleetwood Mac. Erfitt er að velja "
        "eina bók en sú besta sem hún hefur lesið nýlega er Huldukonan eftir Fríðu Ísberg, og "
        "uppáhaldskvikmyndin er Little Shop of Horrors. Ef hún þyrfti að flytja úr Hveragerði yrði "
        "Stykkishólmur fyrir valinu, sem henni hefur alltaf þótt einstaklega fallegur bær."
    ),
    "fact_check": [
        {"statement": "Kristín er fædd árið 1990 á Íslandi og hefur lokið MIS-prófi í upplýsingafræði.",
         "ruv_quote": "1990 / Íslandi / MIS- próf í Upplysingafræði"},
        {"statement": "Hún býr með eiginmanni sínum, Gunnlaugi Bjarnasyni, og þremur börnum þeirra.",
         "ruv_quote": "Ég bý með eiginmanni mínum, Gunnlaugi Bjarnasyni og þremur börnum okkar."},
        {"statement": "Hún leggur áherslu á málefni barna og ungmenna, menningarmál og vel ígrundaða uppbyggingu bæjarins.",
         "ruv_quote": "Ég legg áherslu á málefni barna og ungmenna, menningarmál og vel ígrundaða uppbyggingu bæjarins."},
        {"statement": "Kristín vonar að Hveragerði haldi áfram að vera blómlegur menningarbær og að bærinn stækki hæfilega mikið þannig að innviðir geti haldið í við íbúafjölda.",
         "ruv_quote": "Ég vona að Hveragerði haldi áfram að vera blómlegur menningarbær og að bærinn stækki hæfilega mikið þannig að innviðir geti haldið í við íbúafjölda."},
        {"statement": "Aðaláhugamál Kristínar er súrdeigsbakstur.", "ruv_quote": "Súrdeigsbakstur"},
        {"statement": "Hún elskar söngleiki og hefur undanfarið verið að hlusta mikið á Hadestown, og er svo alltaf hrifin af Fleetwood Mac.",
         "ruv_quote": "Ég elska söngleiki og hef undanfarið verið að hlusta mikið á Hadestown. Svo er ég alltaf hrifin af Fleetwood Mac"},
        {"statement": "Erfitt er að velja eina bók en sú besta sem hún hefur lesið nýlega er Huldukonan eftir Fríðu Ísberg, og uppáhaldskvikmyndin er Little Shop of Horrors.",
         "ruv_quote": "Erfitt að velja bara eina en sú besta sem ég hef lesið nýlega er Huldukonan eftir Fríðu Ísberg. / Little shop of horrors"},
        {"statement": "Ef hún þyrfti að flytja úr Hveragerði yrði Stykkishólmur fyrir valinu, sem henni hefur alltaf þótt einstaklega fallegur bær.",
         "ruv_quote": "Mér hefur alltaf þótt Stykkishólmur einstaklega fallegur bær."},
    ]
})

# 41: Halldór Grétar Einarsson (8716-S-10)
ENTRIES.append({
    "ruv_id": "8716-S-10",
    "new_bio": (
        "Halldór Grétar Einarsson er fæddur árið 1966 á Íslandi og býður sig fram fyrir Samfylkinguna "
        "og óflokksbundin í Hveragerði. Hann starfar sem tækni- og þjónustustjóri hjá Advania og "
        "hefur lokið námi í rafeindavirkjun. Halldór talar ensku auk íslensku og hefur verið í "
        "sínum flokki í um þrjú ár. Hann er giftur Hrönn Pétursdóttur, á þrjú uppkomin börn með "
        "fyrri eiginkonu sinni og tvö barnabörn, og býr í raðhúsi.\n\n"
        "Halldór vonast til að stækkun Hveragerðis verði lágstemmd og að haldið verði í sérkenni "
        "bæjarins sem lágreistrar íbúðabyggðar þar sem flest er í göngu- eða hjólafæri.\n\n"
        "Aðaláhugamál Halldórs er skák, og eftirlætisbók hans er skákbókin Chess Structures. "
        "Fyrirmynd hans í pólitík í dag er Kristrún Frostadóttir. Uppáhaldstónlistarmaður hans er "
        "Jónas Sigurðsson og ritvélar framtíðarinnar, og uppáhaldskvikmyndin er Snerting. Ef hann "
        "þyrfti að flytja úr Hveragerði yrði Bolungarvík fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Halldór Grétar Einarsson er fæddur árið 1966 á Íslandi og býður sig fram fyrir Samfylkinguna og óflokksbundin í Hveragerði.",
         "ruv_quote": "1966 / Íslandi"},
        {"statement": "Hann starfar sem tækni- og þjónustustjóri hjá Advania og hefur lokið námi í rafeindavirkjun.",
         "ruv_quote": "Tækni- og þjónustustjóri hjá Advania. / Rafeindavirkjun"},
        {"statement": "Halldór talar ensku auk íslensku og hefur verið í sínum flokki í um þrjú ár.",
         "ruv_quote": "Ensku / 3 ár minnir mig"},
        {"statement": "Hann er giftur Hrönn Pétursdóttur, á þrjú uppkomin börn með fyrri eiginkonu sinni og tvö barnabörn, og býr í raðhúsi.",
         "ruv_quote": "Giftur Hrönn Pétursdóttur. Ég á þrjú uppkomin börn með fyrri eiginkonu minni og tvö barnabörn. / Raðhúsi"},
        {"statement": "Halldór vonast til að stækkun Hveragerðis verði lágstemmd og að haldið verði í sérkenni bæjarins sem lágreistrar íbúðabyggðar þar sem flest er í göngu- eða hjólafæri.",
         "ruv_quote": "Von mín er að stækkun bæjarins verði lágstemmd og að haldið verði í sérkenni hans sem lágreistrar íbúðabyggðar þar sem flest er í göngu- eða hjólafæri."},
        {"statement": "Aðaláhugamál Halldórs er skák, og eftirlætisbók hans er skákbókin Chess Structures.",
         "ruv_quote": "Skák / Chess Structures (skákbók!)"},
        {"statement": "Fyrirmynd hans í pólitík í dag er Kristrún Frostadóttir.",
         "ruv_quote": "Í dag er það Kristrún Frostadóttir"},
        {"statement": "Uppáhaldstónlistarmaður hans er Jónas Sigurðsson og ritvélar framtíðarinnar, og uppáhaldskvikmyndin er Snerting.",
         "ruv_quote": "Jónas Sigurðsson og ritvélar framtíðarinnar / Snerting"},
        {"statement": "Ef hann þyrfti að flytja úr Hveragerði yrði Bolungarvík fyrir valinu.",
         "ruv_quote": "Bolungarvík"},
    ]
})

# 42: Ingibjörg Sigmundsdóttir (8716-S-14)
ENTRIES.append({
    "ruv_id": "8716-S-14",
    "new_bio": (
        "Ingibjörg Sigmundsdóttir er borin og barnfædd Hvergerðingur. Hún er fædd árið 1956 á "
        "Íslandi og býr í einbýli í Hveragerði. Ingibjörg er leikskólakennari að mennt en rak "
        "garðplöntustöð mest allan sinn starfsaldur, og nýtur nú efri áranna. Hún talar ensku og "
        "hrafl í dönsku. Hún hefur verið í sínum flokki í 50 ár.\n\n"
        "Ingibjörg vill að Hveragerði verði eftir tíu ár fjölskyldu- og umhverfisvænt samfélag. Hún "
        "getur ekki hugsað sér að búa annars staðar en í Hveragerði.\n\n"
        "Áhugamál Ingibjargar eru garðrækt og handavinna. Sem fyrirmyndir í pólitík nefnir hún "
        "foreldra sína sem voru miklir sósíalistar. Uppáhaldstónlistin er Queen og eftirlætisbókin "
        "Salka Valka."
    ),
    "fact_check": [
        {"statement": "Ingibjörg Sigmundsdóttir er borin og barnfædd Hvergerðingur.",
         "ruv_quote": "Ég er borin og barnfæddur Hvergerðingur."},
        {"statement": "Hún er fædd árið 1956 á Íslandi og býr í einbýli í Hveragerði.",
         "ruv_quote": "1956 / Íslandi / Einbýli"},
        {"statement": "Ingibjörg er leikskólakennari að mennt en rak garðplöntustöð mest allan sinn starfsaldur, og nýtur nú efri áranna.",
         "ruv_quote": "Leikskólakennari að mennt en rak garðplöntustöð mest allan minn starfsaldur, nú nýr ég efri áranna."},
        {"statement": "Hún talar ensku og hrafl í dönsku.", "ruv_quote": "Ensku og hrafl í dönsku."},
        {"statement": "Hún hefur verið í sínum flokki í 50 ár.", "ruv_quote": "50 ár"},
        {"statement": "Ingibjörg vill að Hveragerði verði eftir tíu ár fjölskyldu- og umhverfisvænt samfélag.",
         "ruv_quote": "Fjölskyldu og umhverfisvænt samfélag."},
        {"statement": "Hún getur ekki hugsað sér að búa annars staðar en í Hveragerði.",
         "ruv_quote": "Ég get ekki hugsað mér að búa annarsstaðar en í Hveragerði."},
        {"statement": "Áhugamál Ingibjargar eru garðrækt og handavinna.",
         "ruv_quote": "Garðrækt og handavinna."},
        {"statement": "Sem fyrirmyndir í pólitík nefnir hún foreldra sína sem voru miklir sósíalistar.",
         "ruv_quote": "Foreldrar mínir sem voru miklir sósíalistar."},
        {"statement": "Uppáhaldstónlistin er Queen og eftirlætisbókin Salka Valka.",
         "ruv_quote": "Queen / Salka Valka"},
    ]
})

# 43: Egill Rúnar Sigurðsson (2505-S-3)
ENTRIES.append({
    "ruv_id": "2505-S-3",
    "new_bio": (
        "Egill Rúnar Sigurðsson er stjórnmálafræðingur, atvinnurekandi og ökukennari, búsettur í "
        "Garði, og skipar 3. sæti á S-lista Samfylkingarinnar og óháðra í Suðurnesjabæ í sveitar"
        "stjórnarkosningum 2026. Hann hefur verið virkur í þjóðfélagsumræðunni um árabil og rekur "
        "bloggið „Pólitík og pælingar“ þar sem hann hefur skrifað um atvinnumál, sjávarútveg og "
        "samfélagsmál á Suðurnesjum. Egill er fæddur árið 1967 á Íslandi og er 58 ára. Hann er með "
        "BA-próf í stjórnmálafræði og starfar sem ökukennari í eigin ökuskóla til aukinna ökuréttinda. "
        "Hann talar ensku auk íslensku og hefur verið í sínum flokki í 27 ár. Hann býr í einbýlishúsi.\n\n"
        "Egill vill að Suðurnesjabær verði framúrskarandi sveitarfélag sem eftirsóknarvert er að búa "
        "í eftir tíu ár.\n\n"
        "Aðaláhugamál Egils er fótbolti. Fyrirmynd hans í pólitík er Kristrún Frostadóttir. Uppáhalds"
        "tónlistarmaður hans er Bubbi Morthens, eftirlætisbókin Draumalandið og uppáhaldskvikmyndin "
        "Shawshank Redemption. Ef hann þyrfti að flytja úr Suðurnesjabæ yrði Reykjavík fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Egill er fæddur árið 1967 á Íslandi og er 58 ára.",
         "ruv_quote": "1967 / Íslandi / Er 58 ára gamall"},
        {"statement": "Hann er með BA-próf í stjórnmálafræði og starfar sem ökukennari í eigin ökuskóla til aukinna ökuréttinda.",
         "ruv_quote": "BA próf / stjórnmálafræðingur að mennt en starfa sem ökukennari í eigin Ökuskóla til aukinna ökuréttinda."},
        {"statement": "Hann talar ensku auk íslensku og hefur verið í sínum flokki í 27 ár.",
         "ruv_quote": "Ensku / 27 ár"},
        {"statement": "Hann býr í einbýlishúsi.", "ruv_quote": "Einbýlishúsi"},
        {"statement": "Egill vill að Suðurnesjabær verði framúrskarandi sveitarfélag sem eftirsóknarvert er að búa í eftir tíu ár.",
         "ruv_quote": "Framúrskarandi sveitarfélag sem eftirsóknavert er að búa í."},
        {"statement": "Aðaláhugamál Egils er fótbolti.", "ruv_quote": "Fótbolti"},
        {"statement": "Fyrirmynd hans í pólitík er Kristrún Frostadóttir.", "ruv_quote": "Kristrún Frostadóttir"},
        {"statement": "Uppáhaldstónlistarmaður hans er Bubbi Morthens, eftirlætisbókin Draumalandið og uppáhaldskvikmyndin Shawshank Redemption.",
         "ruv_quote": "Bubbi Morthens / Draumalandið / shawshank redemption"},
        {"statement": "Ef hann þyrfti að flytja úr Suðurnesjabæ yrði Reykjavík fyrir valinu.",
         "ruv_quote": "Reykjavík"},
    ]
})

# 44: Bára Kristín Þórisdóttir (2505-S-6)
ENTRIES.append({
    "ruv_id": "2505-S-6",
    "new_bio": (
        "Bára Kristín Þórisdóttir er búsett í Sandgerði og skipar 6. sæti á S-lista Samfylkingarinnar "
        "og óháðra í Suðurnesjabæ við sveitarstjórnarkosningarnar 2026. Hún er fædd árið 1998 á "
        "Íslandi, tveggja barna móðir og býr í raðhúsi. Bára Kristín starfar sem leiðbeinandi í "
        "grunnskóla, nánar tiltekið í Gerðaskóla, og er meistaranemi við Háskóla Íslands. Hún hefur "
        "lokið BA-gráðu í uppeldis- og menntunarfræði og talar ensku auk íslensku.\n\n"
        "Pólitísk þátttaka Báru Kristínar er nýtilkomin; hún er nýbyrjuð í flokknum, kannski í mánuð. "
        "Hún vill að Suðurnesjabær verði eftir tíu ár draumastaður fyrir fjölskyldur með börn, með "
        "nóg af leiksvæðum, vel sé stutt við skólana, nemendur og kennara, frítt verði í sund og að "
        "rígurinn verði farinn burt.\n\n"
        "Aðaláhugamál Báru Kristínar er allt sem viðkemur menntun, börnum og þannig pælingum. "
        "Fyrirmynd hennar í pólitík er Ingibjörg Sólrún. Uppáhaldstónlistarmaður hennar er Hnetan, "
        "eftirlætisbækurnar Lubbi finnur málbein og Greppikló koma sterkar inn, og uppáhalds"
        "kvikmyndin er Ocean's 11. Ef hún þyrfti að flytja úr Suðurnesjabæ yrði Reykjanesbær fyrir "
        "valinu."
    ),
    "fact_check": [
        {"statement": "Hún er fædd árið 1998 á Íslandi, tveggja barna móðir og býr í raðhúsi.",
         "ruv_quote": "1998 / Íslandi / 2 barna mamma / Raðhúsi"},
        {"statement": "Bára Kristín starfar sem leiðbeinandi í grunnskóla, nánar tiltekið í Gerðaskóla, og er meistaranemi við Háskóla Íslands.",
         "ruv_quote": "Leiðbeinandi í grunnskóla / leiðbeinandi í Gerðaskóla og meistaranemi í HÍ."},
        {"statement": "Hún hefur lokið BA-gráðu í uppeldis- og menntunarfræði og talar ensku auk íslensku.",
         "ruv_quote": "BA gráða í uppeldis og menntunarfræði / Ensku"},
        {"statement": "Pólitísk þátttaka Báru Kristínar er nýtilkomin; hún er nýbyrjuð í flokknum, kannski í mánuð.",
         "ruv_quote": "Nýbyrjuð - mánuð kannski."},
        {"statement": "Hún vill að Suðurnesjabær verði eftir tíu ár draumastaður fyrir fjölskyldur með börn, með nóg af leiksvæðum, vel sé stutt við skólana, nemendur og kennara, frítt verði í sund og að rígurinn verði farinn burt.",
         "ruv_quote": "Draumastaður fyrir fjölskyldur með börn. Nóg af leiksvæðum, stutt vel við skólana okkar, nemendur og kennara, frítt í sund og að rígurinn verði farinn burt."},
        {"statement": "Aðaláhugamál Báru Kristínar er allt sem viðkemur menntun, börnum og þannig pælingum.",
         "ruv_quote": "Allt sem viðkemur menntun, börnum og þannig pælingum"},
        {"statement": "Fyrirmynd hennar í pólitík er Ingibjörg Sólrún.", "ruv_quote": "Ingibjörg Sólrún"},
        {"statement": "Uppáhaldstónlistarmaður hennar er Hnetan, eftirlætisbækurnar Lubbi finnur málbein og Greppikló koma sterkar inn, og uppáhaldskvikmyndin er Ocean's 11.",
         "ruv_quote": "Hnetan / Lubbi finnur málbein eða Greppikló koma sterkar inn / Ocean’s 11"},
        {"statement": "Ef hún þyrfti að flytja úr Suðurnesjabæ yrði Reykjanesbær fyrir valinu.",
         "ruv_quote": "Reykjanesbær"},
    ]
})

# 45: Jón Þór Jónsson Hansen (2505-S-8)
ENTRIES.append({
    "ruv_id": "2505-S-8",
    "new_bio": (
        "Jón Þór Jónsson Hansen er búsettur í Sandgerði og uppalinn þar. Hann er meðstjórnandi í "
        "Björgunarsveitinni Sigurvon í Sandgerði — elstu sjóbjörgunarsveit landsins, stofnaðri 1928 "
        "— og hefur sinnt unglingastarfi innan sveitarinnar í um áratug. Jón Þór er háskólanemi og "
        "starfar sem stuðningsfulltrúi við Sandgerðisskóla og í eftirskólaúrræði, og samhliða því "
        "vinnur hann sem frístundaleiðbeinandi í félagsmiðstöðinni Skýjaborg í Sandgerði á kvöldin "
        "og hefur gert það síðustu tíu ár. Hann skipar 8. sæti á S-lista Samfylkingarinnar og óháðra "
        "í Suðurnesjabæ við sveitarstjórnarkosningarnar 16. maí 2026.\n\n"
        "Jón Þór er fæddur árið 1998 á Íslandi, talar ensku auk íslensku og hefur lokið vélstjórnar- "
        "og skipstjórnarmenntun ásamt stúdentsprófi. Hann býr í einbýlishúsi.\n\n"
        "Jón Þór segir framtíðarsýn sína fyrir Suðurnesjabæ vera sameinað samfélag. Aðaláhugamál "
        "hans er útivist. Sem fyrirmynd í pólitík segist hann líklega nefna forsætisráðherrann. "
        "Uppáhaldstónlistarmaður hans er Kaleo, eftirlætisbækurnar Útkallsbækurnar eftir Óttar "
        "Sveinsson og uppáhaldskvikmyndin Jumanji. Ef hann þyrfti að flytja úr Suðurnesjabæ yrði "
        "Þorlákshöfn líklega fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Jón Þór Jónsson Hansen er búsettur í Sandgerði og uppalinn þar.",
         "ruv_quote": "Ég heiti Jón Þór Jónsson Hansen og er uppalinn í Sandgerði."},
        {"statement": "Hann hefur sinnt unglingastarfi innan sveitarinnar í um áratug.",
         "ruv_quote": "ég sinnt unglingastarfi í björgunarsveitinni Sigurvon í um tíu ár."},
        {"statement": "Jón Þór er háskólanemi og starfar sem stuðningsfulltrúi við Sandgerðisskóla og í eftirskólaúrræði, og samhliða því vinnur hann sem frístundaleiðbeinandi í félagsmiðstöðinni Skýjaborg í Sandgerði á kvöldin og hefur gert það síðustu tíu ár.",
         "ruv_quote": "Ég starfa í Sandgerðisskóla sem stuðningsfulltrúi og í eftirskólaúrræði. Samhliða því vinn ég í félagsmiðstöðinni Skýjaborg í Sandgerði á kvöldin og hef gert það síðustu tíu ár. / Stuðningsfulltrúi við Sandgerðisskóla, frístundaleiðbeinandi félagsmiðstöðvarinnar Skýjaborgar og háskólanemi"},
        {"statement": "Jón Þór er fæddur árið 1998 á Íslandi, talar ensku auk íslensku og hefur lokið vélstjórnar- og skipstjórnarmenntun ásamt stúdentsprófi.",
         "ruv_quote": "1998 / Íslandi / Ensku / Með vélstjórnar- og skipstjórnarmenntun ásamt stúdentspróf"},
        {"statement": "Hann býr í einbýlishúsi.", "ruv_quote": "einbýlishúsi"},
        {"statement": "Jón Þór segir framtíðarsýn sína fyrir Suðurnesjabæ vera sameinað samfélag.",
         "ruv_quote": "Sameinað samfélag"},
        {"statement": "Aðaláhugamál hans er útivist.", "ruv_quote": "Útivist"},
        {"statement": "Sem fyrirmynd í pólitík segist hann líklega nefna forsætisráðherrann.",
         "ruv_quote": "Þetta er erfitt, ætli það sé ekki  ætli það sé ekki bara forsætisráðherrann okkar"},
        {"statement": "Uppáhaldstónlistarmaður hans er Kaleo, eftirlætisbækurnar Útkallsbækurnar eftir Óttar Sveinsson og uppáhaldskvikmyndin Jumanji.",
         "ruv_quote": "Kaleo / Útkallsbækurnar eftir Óttar Sveinsson / jumanji"},
        {"statement": "Ef hann þyrfti að flytja úr Suðurnesjabæ yrði Þorlákshöfn líklega fyrir valinu.",
         "ruv_quote": "Ætli það yrði ekki Þorlákshöfn?"},
    ]
})

# 46: Benóný Þórhallsson (2505-S-9)
ENTRIES.append({
    "ruv_id": "2505-S-9",
    "new_bio": (
        "Benóný Þórhallsson er í framboði fyrir Samfylkinguna og óháða í Suðurnesjabæ. Hann er "
        "fæddur árið 1993 á Íslandi, 32 ára og þriggja barna faðir. Benóný er fæddur og uppalinn í "
        "Grindavík en á ættir að rekja í Suðurnesjabæ.\n\n"
        "Benóný vinnur sem smiður og kemur jafnframt að knattspyrnuþjálfun. Hann hefur lokið "
        "grunnskólaprófi og þetta eru hans fyrstu skref í flokksstarfi. Hann býr í eigin húsnæði.\n\n"
        "Benóný vill að Suðurnesjabær verði eftir tíu ár sterkt sameinað samfélag sem hafi nýtt þau "
        "gífurlegu tækifæri sem til staðar eru. Sem fyrirmynd í pólitík segist hann sækja innblástur "
        "úr öllum áttum.\n\n"
        "Áhugamál Benónýs eru ljósmyndun og knattspyrna. Hann heldur upp á Unu Torfa, eftirlætisbókin "
        "er eflaust Eragon þótt hann mætti vera duglegri að lesa, og uppáhaldskvikmyndin er Pitch "
        "Perfect. Ef hann þyrfti að flytja úr Suðurnesjabæ yrði Grindavík eða Höfn í Hornafirði "
        "fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Hann er fæddur árið 1993 á Íslandi, 32 ára og þriggja barna faðir.",
         "ruv_quote": "1993 / Íslandi / Ég er 32 ára, þriggja barna faðir."},
        {"statement": "Benóný er fæddur og uppalinn í Grindavík en á ættir að rekja í Suðurnesjabæ.",
         "ruv_quote": "Ég er fæddur og uppalinn í Grindavík en á ættir að rekja í Suðurnesjabæ."},
        {"statement": "Benóný vinnur sem smiður og kemur jafnframt að knattspyrnuþjálfun.",
         "ruv_quote": "Ég vinn sem smiður auk þess að gera viðloðandi við knattspyrnuþjálfun."},
        {"statement": "Hann hefur lokið grunnskólaprófi og þetta eru hans fyrstu skref í flokksstarfi.",
         "ruv_quote": "Grunnskólapróf / Þetta eru mín fyrstu skref"},
        {"statement": "Hann býr í eigin húsnæði.", "ruv_quote": "Mínu eigin"},
        {"statement": "Benóný vill að Suðurnesjabær verði eftir tíu ár sterkt sameinað samfélag sem hafi nýtt þau gífurlegu tækifæri sem til staðar eru.",
         "ruv_quote": "Sterkt sameinað samfélag sem er búið að nýta þessi gífurlegu tækifæri sem eru til staðar."},
        {"statement": "Sem fyrirmynd í pólitík segist hann sækja innblástur úr öllum áttum.",
         "ruv_quote": "Það er úr öllum áttum."},
        {"statement": "Áhugamál Benónýs eru ljósmyndun og knattspyrna.",
         "ruv_quote": "Ljósmyndun og knattspyrna"},
        {"statement": "Hann heldur upp á Unu Torfa, eftirlætisbókin er eflaust Eragon þótt hann mætti vera duglegri að lesa, og uppáhaldskvikmyndin er Pitch Perfect.",
         "ruv_quote": "Una Torfa 😍 / Mætti vera duglegur að lesa en það er eflaust Eragon / Pitch Perfect"},
        {"statement": "Ef hann þyrfti að flytja úr Suðurnesjabæ yrði Grindavík eða Höfn í Hornafirði fyrir valinu.",
         "ruv_quote": "Grindavík eða Höfn í Hornafirði"},
    ]
})

# 47: Przemyslaw Antoni Szymajda (2505-S-10)
ENTRIES.append({
    "ruv_id": "2505-S-10",
    "new_bio": (
        "Przemyslaw Antoni Szymajda er fæddur árið 1986 í Póllandi og talar pólsku og ensku auk "
        "íslensku. Hann starfar sem verkstjóri hjá Ný-Fisk og hefur verið verkstjóri í yfir tíu ár. "
        "Hann hefur lokið menntaskólanámi, býr í einbýlishúsi og hefur verið í sínum flokki í mánuð.\n\n"
        "Przemyslaw vill að Suðurnesjabær þróist sterklega og jákvætt á næstu tíu árum. Sem fyrirmynd "
        "í pólitík segist hann hafa áhuga á stefnu sem snertir samþættingu innflytjenda og hlutverki "
        "íþrótta í félagslegri þróun.\n\n"
        "Aðaláhugamál Przemyslaws er íþróttaskotfimi, og hann hefur sérstakan áhuga á skotleikjum, "
        "knattspyrnu og ýmis skemmtilegum ferðum. Hann heldur upp á U2, les ævisögur og uppáhalds"
        "kvikmyndaflokkur hans er gamanleikur. Ef hann þyrfti að flytja úr Suðurnesjabæ yrði "
        "Reykjanesbær fyrir valinu."
    ),
    "fact_check": [
        {"statement": "Przemyslaw Antoni Szymajda er fæddur árið 1986 í Póllandi og talar pólsku og ensku auk íslensku.",
         "ruv_quote": "1986 / Pólland / Pólska og enska"},
        {"statement": "Hann starfar sem verkstjóri hjá Ný-Fisk og hefur verið verkstjóri í yfir tíu ár.",
         "ruv_quote": "Verkstjóri í Ný-Fisk / Verkstjóri í yfir tíu ár."},
        {"statement": "Hann hefur lokið menntaskólanámi, býr í einbýlishúsi og hefur verið í sínum flokki í mánuð.",
         "ruv_quote": "menntaskóli / einbýlishús / mánuð"},
        {"statement": "Przemyslaw vill að Suðurnesjabær þróist sterklega og jákvætt á næstu tíu árum.",
         "ruv_quote": "sterklega og jákvætt"},
        {"statement": "Sem fyrirmynd í pólitík segist hann hafa áhuga á stefnu sem snertir samþættingu innflytjenda og hlutverki íþrótta í félagslegri þróun.",
         "ruv_quote": "Ég hef áhuga á stefnu sem snertir samþættingu innflytjenda og hlutverki íþrótta í félagslegri þróun."},
        {"statement": "Aðaláhugamál Przemyslaws er íþróttaskotfimi, og hann hefur sérstakan áhuga á skotleikjum, knattspyrnu og ýmis skemmtilegum ferðum.",
         "ruv_quote": "íþróttaskotfimi / Hef sérstakan áhuga á skotleikjum, knattspyrnu og ýmis skemmtilegum ferðum."},
        {"statement": "Hann heldur upp á U2, les ævisögur og uppáhaldskvikmyndaflokkur hans er gamanleikur.",
         "ruv_quote": "U2 / ævisögur / gamanleikur"},
        {"statement": "Ef hann þyrfti að flytja úr Suðurnesjabæ yrði Reykjanesbær fyrir valinu.",
         "ruv_quote": "Reykjanesbær"},
    ]
})

# 48: Sigurbjörg Ragnarsdóttir (2505-S-14)
ENTRIES.append({
    "ruv_id": "2505-S-14",
    "new_bio": (
        "Sigurbjörg Ragnarsdóttir er fædd árið 1955 á Íslandi og hefur verið í Samfylkingunni frá "
        "stofnun flokksins. Hún er komin á eftirlaun og býr í leiguhúsnæði hjá sveitarfélaginu í "
        "Suðurnesjabæ. Hún hefur gagnfræðamenntun að baki og talar ensku auk íslensku.\n\n"
        "Sigurbjörg vill að Suðurnesjabær verði framúrskarandi sveitarfélag, með góð samskipti og "
        "vel rekið eftir tíu ár. Sem fyrirmynd í pólitík nefnir hún Kristrúnu.\n\n"
        "Aðaláhugamál Sigurbjargar eru fræðslu- og velferðarmál. Hún heldur upp á Mána, eftirlætis"
        "bókin er Secret og uppáhaldskvikmyndin Mamma Mia. Þótt hún myndi ekki vilja flytja yrði "
        "Eyrarbakki valinn ef til þess kæmi."
    ),
    "fact_check": [
        {"statement": "Sigurbjörg Ragnarsdóttir er fædd árið 1955 á Íslandi og hefur verið í Samfylkingunni frá stofnun flokksins.",
         "ruv_quote": "1955 / Íslandi / frá því hann var stofnaður"},
        {"statement": "Hún er komin á eftirlaun og býr í leiguhúsnæði hjá sveitarfélaginu í Suðurnesjabæ.",
         "ruv_quote": "ellilíferisþegi / leiguhúsnæði hjá sveitafélaginu"},
        {"statement": "Hún hefur gagnfræðamenntun að baki og talar ensku auk íslensku.",
         "ruv_quote": "gagnfæðingur / ensku"},
        {"statement": "Sigurbjörg vill að Suðurnesjabær verði framúrskarandi sveitarfélag, með góð samskipti og vel rekið eftir tíu ár.",
         "ruv_quote": "framúrskarandi ,góð samskipti, og vel rekið"},
        {"statement": "Sem fyrirmynd í pólitík nefnir hún Kristrúnu.", "ruv_quote": "Kristrún"},
        {"statement": "Aðaláhugamál Sigurbjargar eru fræðslu- og velferðarmál.",
         "ruv_quote": "fræðsu og velferðarmál"},
        {"statement": "Hún heldur upp á Mána, eftirlætisbókin er Secret og uppáhaldskvikmyndin Mamma Mia.",
         "ruv_quote": "Mánar / Secret / amma mia"},
        {"statement": "Þótt hún myndi ekki vilja flytja yrði Eyrarbakki valinn ef til þess kæmi.",
         "ruv_quote": "myndi ekki vilja flytja en Eyrarbakki væri valið"},
    ]
})

# 49: Elín Frímannsdóttir (2505-S-17)
ENTRIES.append({
    "ruv_id": "2505-S-17",
    "new_bio": (
        "Elín Frímannsdóttir er fædd árið 1988 á Íslandi og hefur verið í Samfylkingunni frá árinu "
        "2010. Hún starfar sem löggiltur fasteignasali og hefur lokið löggildingu til fasteignasala "
        "sem hæsta menntunarstigi. Hún talar ensku auk íslensku og býr í eigin húsnæði.\n\n"
        "Elín vill að Suðurnesjabær verði eftir tíu ár gott samfélag fyrir öll, með góða "
        "rekstrarafkomu til að halda áfram uppbyggingu. Fyrirmynd hennar í pólitík er Kristrún "
        "Frostadóttur.\n\n"
        "Aðaláhugamál Elínar eru útilegur, enda elskar hún að ferðast um Ísland. Hún heldur upp á "
        "Jón Jónsson og Teddy Swims, eftirlætisbókin er 9 nóvember og uppáhaldskvikmyndin Englar "
        "alheimsins. Henni hefur alltaf þótt Hveragerði og Selfoss heillandi, en ef hún þyrfti að "
        "flytja úr Suðurnesjabæ færi hún þó frekar í Reykjanesbæ til að vera sem næst fjölskyldu og "
        "vinum."
    ),
    "fact_check": [
        {"statement": "Elín Frímannsdóttir er fædd árið 1988 á Íslandi og hefur verið í Samfylkingunni frá árinu 2010.",
         "ruv_quote": "1988 / Íslandi / Frá 2010"},
        {"statement": "Hún starfar sem löggiltur fasteignasali og hefur lokið löggildingu til fasteignasala sem hæsta menntunarstigi.",
         "ruv_quote": "Löggiltur fasteignasali / Löggilding til fasteignasala"},
        {"statement": "Hún talar ensku auk íslensku og býr í eigin húsnæði.",
         "ruv_quote": "Ensku / Eigin húsnæði"},
        {"statement": "Elín vill að Suðurnesjabær verði eftir tíu ár gott samfélag fyrir öll, með góða rekstrarafkomu til að halda áfram uppbyggingu.",
         "ruv_quote": "Gott samfélag fyrir öll, með góða rekstrarafkomu til að halda áfram uppbyggingu."},
        {"statement": "Fyrirmynd hennar í pólitík er Kristrún Frostadóttur.", "ruv_quote": "Kristrún Frostadóttir"},
        {"statement": "Aðaláhugamál Elínar eru útilegur, enda elskar hún að ferðast um Ísland.",
         "ruv_quote": "Ég elska að ferðast um Ísland og ég myndi segja að mitt helsta áhugamál sé útilegur"},
        {"statement": "Hún heldur upp á Jón Jónsson og Teddy Swims, eftirlætisbókin er 9 nóvember og uppáhaldskvikmyndin Englar alheimsins.",
         "ruv_quote": "Jón Jónsson og Teddy Swims / 9 nóvember. / Englar Alheimsins"},
        {"statement": "Henni hefur alltaf þótt Hveragerði og Selfoss heillandi, en ef hún þyrfti að flytja úr Suðurnesjabæ færi hún þó frekar í Reykjanesbæ til að vera sem næst fjölskyldu og vinum.",
         "ruv_quote": "Mig hefur alltaf þótt Hveragerði og Selfoss heillandi en ætli ég færi þó ekki í Reykjanesbæ til að vera sem næst fjölskyldu og vinum."},
    ]
})

if __name__ == "__main__":
    with open(r"F:/Claude Projects/iceland-elections/temp/ruv_chunks/output_01.json", "w", encoding="utf-8") as f:
        json.dump(ENTRIES, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(ENTRIES)} entries")
