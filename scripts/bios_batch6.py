#!/usr/bin/env python3
"""Batch 6: MOS, MUT, MYR, OLF, RKH"""
import re

BIOS = {
    # === MOS (Mosfellsbær) ===
    # B-listi (Framsókn)
    'Halla Karen Kristjánsdóttir': ('Halla Karen Kristjánsdóttir er formaður bæjarráðs Mosfellsbæjar og situr á 2. sæti framboðslista Framsóknar í sveitarstjórnarkosningum 2026; hún leggur áherslu á heilbrigðisþjónustu, skólamál og velferð barna og ungmenna.', 'https://framsoknmos.is/author/hallak/'),
    'Leifur Ingi Eysteinsson': ('Leifur Ingi Eysteinsson er tómstunda- og félagsmálafræðingur og er á 3. sæti á framboðslista Framsóknar í Mosfellsbæ í sveitarstjórnarkosningum 2026; hann flutti aftur til Mosfellsbæjar eftir dvöl í Svíþjóð.', 'https://mosfellingur.is/algjor-endurnyjun-a-lista-framsoknar/'),
    'Elín Guðný Hlöðversdóttir': ('Elín Guðný Hlöðversdóttir er eigandi kökuverslunarinnar Kökur & Konfekt og er á 4. sæti á framboðslista Framsóknar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/algjor-endurnyjun-a-lista-framsoknar/'),
    'Ýmir Örn Hafsteinsson': ('Ýmir Örn Hafsteinsson er á 5. sæti á framboðslista Framsóknar í Mosfellsbæ í sveitarstjórnarkosningum 2026 og hefur fjallað um samfélagsmál í bænum í greinum til Mosfellinga.', 'https://mosfellingur.is/heilbrigt-og-fjolskylduvaent-samfelag/'),

    # C-listi (Viðreisn)
    'Valdimar Birgisson': ('Valdimar Birgisson er rekstrarráðgjafi og stofnandi Viðreisnarfélags í Mosfellsbæ; hann situr í sveitarstjórn bæjarins og er á 2. sæti á lista Viðreisnar í sveitarstjórnarkosningum 2026.', 'https://vidreisn.is/hofundur/valdimar/'),
    'Elín Anna Gísladóttir': ('Elín Anna Gísladóttir er verkfræðingur og hefur þjónað sem fulltrúi Viðreisnar í skólanefnd Mosfellsbæjar; hún er á 3. sæti á lista Viðreisnar í sveitarstjórnarkosningum 2026.', 'https://vidreisn.is/2026/02/gylfi-thor-thorsteinsson-leidir-lista-vidreisnar-i-mosfellsbae/'),
    'Berglind Robertson Grétarsdóttir': ('Berglind Robertson Grétarsdóttir er leikskólastjóri og sjálfboðaliði í slysavarnarliði Rauða krossins; hún er á 4. sæti á lista Viðreisnar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://vidreisn.is/2026/02/gylfi-thor-thorsteinsson-leidir-lista-vidreisnar-i-mosfellsbae/'),
    'Haukur Skúlason': ('Haukur Skúlason er meðstofnandi og fyrrverandi forstjóri Indó og er á 5. sæti á lista Viðreisnar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://vidreisn.is/2026/02/gylfi-thor-thorsteinsson-leidir-lista-vidreisnar-i-mosfellsbae/'),

    # D-listi (Sjálfstæðisflokkur)
    'Jana Katrín Knútsdóttir': ('Jana Katrín Knútsdóttir er hjúkrunarfræðingur og sveitarstjórnarfulltrúi; hún fæddist og ólst upp í Mosfellsbæ og er á 2. sæti á lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-i-mosfellsbae/'),
    'Elísabet S. Ólafsdóttir': ('Elísabet S. Ólafsdóttir er sáttamiðlari og er á 3. sæti á lista Sjálfstæðisflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-i-mosfellsbae/'),
    'Hjörtur Örn Arnarson': ('Hjörtur Örn Arnarson er landfræðingur og er á 4. sæti á lista Sjálfstæðisflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-i-mosfellsbae/'),
    'Þórarinn Örn Andrésson': ('Þórarinn Örn Andrésson er tölvunarfræðingur og forstjóri hugbúnaðarfyrirtækisins Oxstone; hann er á 5. sæti á lista Sjálfstæðisflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-i-mosfellsbae/'),

    # M-listi (Miðflokkur)
    'Ingibjörg Einarsdóttir': ('Ingibjörg Einarsdóttir er tannlæknir og aðjúnkt við Háskóla Íslands; hún er á 2. sæti á lista Miðflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/mikilvaegt-ad-hlusta-a-folkid-i-baenum/'),
    'Hjalti Árnason': ('Hjalti Árnason er á 3. sæti á framboðslista Miðflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/mikilvaegt-ad-hlusta-a-folkid-i-baenum/'),
    'Sóley Sævarsdóttir Meyer': ('Sóley Sævarsdóttir Meyer er á 4. sæti á framboðslista Miðflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/mikilvaegt-ad-hlusta-a-folkid-i-baenum/'),
    'Kristján Davíð Sigurjónsson': ('Kristján Davíð Sigurjónsson er á 5. sæti á framboðslista Miðflokksins í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/mikilvaegt-ad-hlusta-a-folkid-i-baenum/'),

    # S-listi (Samfylkingin)
    'Guðný Maja Riba': ('Guðný Maja Riba er kennari og fyrrverandi borgarfulltrúi í Reykjavík; hún er á 2. sæti á lista Samfylkingarinnar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/framtidarsyn-mosfellsbaejar-i-ithrottum-og-tomstundum/'),
    'Ómar Ingþórsson': ('Ómar Ingþórsson er landslagsarkitekt og náttúrufræðingur og er á 3. sæti á lista Samfylkingarinnar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/03/09/frambodslisti-samfylkingarinnar-i-mosfellsbae/'),
    'Auður Einarsdóttir': ('Auður Einarsdóttir er lögfræðinemi og er á 4. sæti á lista Samfylkingarinnar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/03/09/frambodslisti-samfylkingarinnar-i-mosfellsbae/'),
    'Guðlaugur Bjarki Lúðvíksson': ('Guðlaugur Bjarki Lúðvíksson er efnaverkfræðingur og er á 5. sæti á lista Samfylkingarinnar í Mosfellsbæ í sveitarstjórnarkosningum 2026.', 'https://mosfellingur.is/framtidarsyn-mosfellsbaejar-i-ithrottum-og-tomstundum/'),

    # === MUT (Múlaþing) ===
    # B-listi (Framsókn)
    'Eiður Ragnarsson': ('Eiður Ragnarsson er ferðaþjónustubóndi og er á 2. sæti á lista Framsóknar í Múlaþingi í sveitarstjórnarkosningum 2026; hann hefur verið virkur í eftirliti með ákvörðunum sveitarstjórnar.', 'https://austurfrett.is/frettir/ny-noefn-ofarlega-a-bladhi-hja-framsokn-i-mulathingi'),
    'Þórey Birna Jónsdóttir': ('Þórey Birna Jónsdóttir er sauðfjárbóndi og er á 3. sæti á lista Framsóknar í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/ny-noefn-ofarlega-a-bladhi-hja-framsokn-i-mulathingi'),
    'Björg Eyþórsdóttir': ('Björg Eyþórsdóttir er hjúkrunarfræðingur og sveitarstjórnarfulltrúi; hún er á 4. sæti á lista Framsóknar í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/ny-noefn-ofarlega-a-bladhi-hja-framsokn-i-mulathingi'),
    'Guðmundur Bj. Hafþórsson': ('Guðmundur Bj. Hafþórsson er brunavarnareftirlit og er á 5. sæti á lista Framsóknar í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/ny-noefn-ofarlega-a-bladhi-hja-framsokn-i-mulathingi'),

    # D-listi (Sjálfstæðisflokkur)
    'Þórhildur Katrín Stefánsdóttir': ('Þórhildur Katrín Stefánsdóttir er lögfræðingur og varaformaður Landssambands hrossabænda; hún er á 2. sæti á lista Sjálfstæðisflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/28/berglind-harpa-afram-oddviti-i-mulathingi-thorhildur-katrin-i-2-saeti/'),
    'Ívar Karl Hafliðason': ('Ívar Karl Hafliðason er forstjóri og sveitarstjórnarfulltrúi; hann er á 3. sæti á lista Sjálfstæðisflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/28/berglind-harpa-afram-oddviti-i-mulathingi-thorhildur-katrin-i-2-saeti/'),
    'Einar Freyr Guðmundsson': ('Einar Freyr Guðmundsson er lögfræðinemi og sveitarstjórnarfulltrúi; hann er á 4. sæti á lista Sjálfstæðisflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/28/berglind-harpa-afram-oddviti-i-mulathingi-thorhildur-katrin-i-2-saeti/'),
    'Oddný Björk Daníelsdóttir': ('Oddný Björk Daníelsdóttir er rekstrarstjóri og fyrrverandi sveitarstjórnarfulltrúi frá Seyðisfirði; hún er á 5. sæti á lista Sjálfstæðisflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/02/28/berglind-harpa-afram-oddviti-i-mulathingi-thorhildur-katrin-i-2-saeti/'),

    # L-listi (Austurlistinn og Viðreisn)
    'Eyþór Stefánsson': ('Eyþór Stefánsson er verkefnastjóri og sveitarstjórnarfulltrúi frá Borgarfirði og er á 2. sæti á lista Austurlistans og Viðreisnar í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurlistinn.is/index.php/frambjodhendur'),
    'Urður Arna Ómarsdóttir': ('Urður Arna Ómarsdóttir er aðstoðarleikskólastjóri á Seyðisfjarðarskóla og meðlimur í stjórn Viðreisnar í Múlaþingi; hún er á 3. sæti á lista Austurlistans og Viðreisnar í sveitarstjórnarkosningum 2026.', 'https://vidreisn.is/felogin/mulathing/'),
    'Jóhann Hjalti Þorsteinsson': ('Jóhann Hjalti Þorsteinsson er umsjónarmaður á heimavist Menntaskólans á Egilsstöðum og skjalaritari á skrifstofu Múlaþings; hann er á 4. sæti á lista Austurlistans og Viðreisnar í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurlistinn.is/index.php/frambjodhendur'),
    'Hrafnhildur Margrét Vídalín Áslaugardóttir': ('Hrafnhildur Margrét Vídalín Áslaugardóttir er á 5. sæti á framboðslista Austurlistans og Viðreisnar í Múlaþingi í sveitarstjórnarkosningum 2026.', ''),

    # M-listi (Miðflokkur)
    'Hannes Karl Hilmarsson': ('Hannes Karl Hilmarsson er afgreiðslustjóri og fyrrverandi sveitarstjórnarfulltrúi; hann er á 2. sæti á lista Miðflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/fyrrum-syslumadhur-leidhir-midhflokkinn-i-mulathingi'),
    'Stefán Bragi Birgisson': ('Stefán Bragi Birgisson er bóndi og er á 3. sæti á lista Miðflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/fyrrum-syslumadhur-leidhir-midhflokkinn-i-mulathingi'),
    'Jóhann Halldór Harðarson': ('Jóhann Halldór Harðarson er ráðgjafi og er á 4. sæti á lista Miðflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/fyrrum-syslumadhur-leidhir-midhflokkinn-i-mulathingi'),
    'Guðmunda Vala Jónasdóttir': ('Guðmunda Vala Jónasdóttir er leikskólastjóri og er á 5. sæti á lista Miðflokksins í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://austurfrett.is/frettir/fyrrum-syslumadhur-leidhir-midhflokkinn-i-mulathingi'),

    # V-listi (VG og óháðir)
    'Helgi Hlynur Ásgrímsson': ('Helgi Hlynur Ásgrímsson er fiskeldisbóndi og sveitarstjórnarfulltrúi Múlaþings; hann er á 2. sæti á lista VG og óháðra í Múlaþingi í sveitarstjórnarkosningum 2026.', 'https://hskolinn.is/helgi-hlynur-asgrimsson'),
    'Glúmur Björnsson': ('Glúmur Björnsson er á 3. sæti á framboðslista VG og óháðra í Múlaþingi í sveitarstjórnarkosningum 2026.', ''),
    'Guðrún Ásta Tryggvadóttir': ('Guðrún Ásta Tryggvadóttir er kennari frá Seyðisfirði og er á 4. sæti á lista VG og óháðra í Múlaþingi í sveitarstjórnarkosningum 2026.', ''),
    'Sigríður Lára Sigurjónsdóttir': ('Sigríður Lára Sigurjónsdóttir er á 5. sæti á framboðslista VG og óháðra í Múlaþingi í sveitarstjórnarkosningum 2026.', ''),

    # === MYR (Mýrdalshreppur) ===
    # MYA-listi (Allir)
    'Anna Huld Óskarsdóttir': ('Anna Huld Óskarsdóttir er hótelstjóri og leiðir A-lista Mýrdalshrepps – Allir – í sveitarstjórnarkosningum 2026; hún situr sem sveitarstjórnarfulltrúi í núverandi sveitarstjórn.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Salóme Svandís Þórhildardóttir': ('Salóme Svandís Þórhildardóttir er kennari og er á 2. sæti á A-lista Mýrdalshrepps í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Brynjar Ögmundsson': ('Brynjar Ögmundsson er sjúkraflutningamaður og er á 3. sæti á A-lista Mýrdalshrepps í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Kristína Hajniková': ('Kristína Hajniková er rekstrarstjóri og er á 4. sæti á A-lista Mýrdalshrepps í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Michal Ladaczek': ('Michal Ladaczek er fyrirtækjaeigandi og er á 5. sæti á A-lista Mýrdalshrepps í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),

    # MYZ-listi (Samfélagið)
    'Björn Þór Ólafsson': ('Björn Þór Ólafsson er verslunarstjóri og fyrrverandi bæjarstjóri Mýrdalshrepps; hann leiðir Z-lista Samfélagsins í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Þórey Richardt Úlfarsdóttir': ('Þórey Richardt Úlfarsdóttir er sjálfstætt starfandi og er á 2. sæti á Z-lista Samfélagsins í Mýrdalshreppi í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Daníel Óliver Sveinsson': ('Daníel Óliver Sveinsson er rekstrarstjóri og er á 3. sæti á Z-lista Samfélagsins í Mýrdalshreppi í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Magnús Örn Sigurjónsson': ('Magnús Örn Sigurjónsson er bóndi og er á 4. sæti á Z-lista Samfélagsins í Mýrdalshreppi í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),
    'Hjördís Rut Jónsdóttir': ('Hjördís Rut Jónsdóttir er kennari og er á 5. sæti á Z-lista Samfélagsins í Mýrdalshreppi í sveitarstjórnarkosningum 2026.', 'https://www.vik.is/is/frettir/sveitarstjornarkosningar-16-mai-2026'),

    # === OLF (Sveitarfélagið Ölfus) ===
    # D-listi (Sjálfstæðisflokkur)
    'Grétar Ingi Erlendsson': ('Grétar Ingi Erlendsson er verkefnastjóri og formaður bæjarráðs Sveitarfélagsins Ölfuss; hann leiðir D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/04/d-listi-sjalfstaedisfelagsins-i-olfusi-samthykktur-einroma/'),
    'Sigurbjörg Jenný Jónsdóttir': ('Sigurbjörg Jenný Jónsdóttir er viðskiptafræðingur og er á 2. sæti á D-lista Sjálfstæðisflokksins í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.olfus.is/is/frettir/auglysing-um-frambodslista-vid-sveitarstjornarkosningarnar-i-sveitarfelaginu-olfusi-16mai-2026'),
    'Gestur Þór Kristjánsson': ('Gestur Þór Kristjánsson er húsasmíðameistari og forseti bæjarstjórnar Ölfuss; hann er á 3. sæti á D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.', 'https://xd.is/2022/03/02/gestur-thor-kristjansson-afram-oddviti-d-listans-i-svf-olfusi/'),
    'Erla Sif Markúsdóttir': ('Erla Sif Markúsdóttir er deildarstjóri grunnskóla og er á 4. sæti á D-lista Sjálfstæðisflokksins í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.olfus.is/is/frettir/auglysing-um-frambodslista-vid-sveitarstjornarkosningarnar-i-sveitarfelaginu-olfusi-16mai-2026'),
    'Guðlaug Einarsdóttir': ('Guðlaug Einarsdóttir er deildarstjóri grunnskóla og er á 5. sæti á D-lista Sjálfstæðisflokksins í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.olfus.is/is/frettir/auglysing-um-frambodslista-vid-sveitarstjornarkosningarnar-i-sveitarfelaginu-olfusi-16mai-2026'),

    # S-listi (Samfylkingin og félagar)
    'Berglind Friðriksdóttir': ('Berglind Friðriksdóttir er sálfræðingur og sveitarstjórnarfulltrúi; hún er á 2. sæti á S-lista Samfylkingarinnar og félaga í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/samfylkingin-bydur-fram-i-fyrsta-sinn-i-20-ar-i-olfusinu/'),
    'Pálmi Þór Ásbergsson': ('Pálmi Þór Ásbergsson er aðstoðarforstjóri og er á 3. sæti á S-lista Samfylkingarinnar og félaga í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.olfus.is/is/frettir/auglysing-um-frambodslista-vid-sveitarstjornarkosningarnar-i-sveitarfelaginu-olfusi-16mai-2026'),
    'Bryndís Sigurðardóttir': ('Bryndís Sigurðardóttir er bókhaldari og er á 4. sæti á S-lista Samfylkingarinnar og félaga í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.olfus.is/is/frettir/auglysing-um-frambodslista-vid-sveitarstjornarkosningarnar-i-sveitarfelaginu-olfusi-16mai-2026'),
    'Sigurður Freyr Vestmann Sigurvinsson': ('Sigurður Freyr Vestmann Sigurvinsson er ráðgjafi og er á 5. sæti á S-lista Samfylkingarinnar og félaga í Sveitarfélaginu Ölfusi í sveitarstjórnarkosningum 2026.', 'https://www.olfus.is/is/frettir/auglysing-um-frambodslista-vid-sveitarstjornarkosningarnar-i-sveitarfelaginu-olfusi-16mai-2026'),

    # === RKH (Reykhólahreppur) ===
    # ROA-listi (Raddir okkar allra)
    'Árný Huld Haraldsdóttir': ('Árný Huld Haraldsdóttir er verslunar- og veitingamaður á Reykhólum og fyrrverandi íbúi ársins í hreppnum; hún leiðir R-lista Raddir okkar allra í sveitarstjórnarkosningum 2026.', 'https://www.reykholar.is/is/frettir/arny-huld-ibui-arsins'),
    'Embla Dögg Bachmann Jóhannsdóttir': ('Embla Dögg Bachmann Jóhannsdóttir er verkefnastjóri hjá Vestfjarðastofu og framkvæmdastjóri Reykhóladaga 2026; hún er á 2. sæti á R-lista Raddir okkar allra í sveitarstjórnarkosningum 2026.', 'https://www.reykholar.is/is/frettir/embla-dogg-framkvaemdastjori-reykholadaga-2026'),
    'Kjartan Þór Ragnarsson': ('Kjartan Þór Ragnarsson er tannlæknir og er á 3. sæti á R-lista Raddir okkar allra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', 'https://www.reykholar.is/is/frettir/tveir-frambodslistar-i-reykholahreppi'),
    'Indiana Svala Ólafsdóttir': ('Indiana Svala Ólafsdóttir er á 4. sæti á framboðslista Raddir okkar allra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', ''),
    'Matthías Óli Gústafsson': ('Matthías Óli Gústafsson er á 5. sæti á framboðslista Raddir okkar allra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', ''),

    # S-listi (Samfylking og óháðir)
    'Hrefna Jónsdóttir': ('Hrefna Jónsdóttir er kennari og leiðir S-lista Samfylkingar og óháðra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/reykholahreppur-tveir-listar-i-frambodi/'),
    'Þorleifur Jóhann Guðjónsson': ('Þorleifur Jóhann Guðjónsson er á 2. sæti á S-lista Samfylkingar og óháðra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', ''),
    'Jóhanna Ösp Einarsdóttir': ('Jóhanna Ösp Einarsdóttir er á 3. sæti á S-lista Samfylkingar og óháðra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', ''),
    'Ólafur Þór Ólafsson': ('Ólafur Þór Ólafsson er sveitarstjóri Reykhólahrepps og er á 4. sæti á S-lista Samfylkingar og óháðra í sveitarstjórnarkosningum 2026.', 'https://www.reykholar.is/is/frettir/tveir-frambodslistar-i-reykholahreppi'),
    'Margrét Dögg Sigurbjörnsdóttir': ('Margrét Dögg Sigurbjörnsdóttir er á 5. sæti á framboðslista Samfylkingar og óháðra í Reykhólahreppi í sveitarstjórnarkosningum 2026.', ''),
}


def main():
    with open('js/data/candidates.js', 'r', encoding='utf-8') as f:
        content = f.read()

    updated = 0
    skipped = 0

    for name, (bio_text, source_url) in BIOS.items():
        bio_escaped = bio_text.replace("'", "\\'")
        pattern = re.compile(re.escape(name) + r'([^}]*?bio: )null', re.DOTALL)
        def replacer(m, be=bio_escaped):
            return name + m.group(1) + "'" + be + "'"
        new_content, n = pattern.subn(replacer, content, count=1)
        if n > 0:
            content = new_content
            updated += 1
        else:
            skipped += 1

    with open('js/data/candidates.js', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f'Updated: {updated}, Skipped (already has bio or not found): {skipped}')


if __name__ == '__main__':
    main()
