#!/usr/bin/env python3
"""Batch 5: RTE, RTY, RVK, SDV, SEL"""
import re

BIOS = {
    # === RTE (Rangárþing eystra) ===
    # B-listi
    'Rafn Bergsson': ('Rafn Bergsson er bóndi og sveitarstjórnarfulltrúi í Rangárþingi eystra og leiðir B-listann í sveitarstjórnarkosningum 2026; hann hefur setið í sveitarstjórn sveitarfélagsins undanfarin átta ár.', 'https://www.sunnlenska.is/frettir/rafn-nyr-oddviti-b-listans-i-rangarthingi-eystra/'),
    'Bjarki Oddsson': ('Bjarki Oddsson er lögreglumaður og sveitarstjórnarfulltrúi í Rangárþingi eystra og er á 2. sæti B-listans í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/frambod-b-lista-i-rangathingi-eystra/'),
    'Gunnhildur Jónsdóttir': ('Gunnhildur Jónsdóttir er bóndi og heilbrigðisstarfsmaður í Rangárþingi eystra og er á 3. sæti B-listans í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/frambod-b-lista-i-rangathingi-eystra/'),
    'Harpa Sif Þorsteinsdóttir': ('Harpa Sif Þorsteinsdóttir er leikskólakennari í Rangárþingi eystra og er á 4. sæti B-listans í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/frambod-b-lista-i-rangathingi-eystra/'),
    'Jón Pétur Þorvaldsson': ('Jón Pétur Þorvaldsson er vörubílstjóri í Rangárþingi eystra og er á 5. sæti B-listans í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/frambod-b-lista-i-rangathingi-eystra/'),

    # D-listi
    'Anton Kári Halldórsson': ('Anton Kári Halldórsson er oddviti Rangárþings eystra og leiðir D-listann í sveitarstjórnarkosningum 2026; hann varð oddviti sveitarfélagsins fyrst eftir kosningarnar 2022.', 'https://xd.is/2026/02/14/anton-kari-oddviti-d-lista-i-rangarthingi-eystra/'),
    'Aðalbjörg Rún Ásgeirsdóttir': ('Aðalbjörg Rún Ásgeirsdóttir er bóndi í Stóru-Mörk í Rangárþingi eystra og er á 2. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/frambodslisti-d-listans-i-rangarthingi-eystra-samthykktur/'),
    'Andri Már Óskarsson': ('Andri Már Óskarsson er byggingarverkstjóri og íþróttaþjálfari á Hvolsvelli og er á 3. sæti D-listans í Rangárþingi eystra í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/frambodslisti-d-listans-i-rangarthingi-eystra-samthykktur/'),
    'Hulda Dóra Eysteinsdóttir': ('Hulda Dóra Eysteinsdóttir er sjálfstætt starfandi hrossaræktandi í Rangárþingi eystra og er á 4. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/frambodslisti-d-listans-i-rangarthingi-eystra-samthykktur/'),
    'Bjarki Freyr Sigurjónsson': ('Bjarki Freyr Sigurjónsson er rekstrarstjóri og sérfræðingur í kjötvinnslu í Rangárþingi eystra og er á 5. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/frambodslisti-d-listans-i-rangarthingi-eystra-samthykktur/'),

    # NRE-listi
    'Tómas Birgir Magnússon': ('Tómas Birgir Magnússon leiðir NRE-listann í Rangárþingi eystra í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tomas-og-inger-i-efstu-saetum-n-listans/'),
    'Inger Erla Thomsen': ('Inger Erla Thomsen er sérfræðingur hjá UNICEF á Íslandi og er á 2. sæti NRE-listans í Rangárþingi eystra í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tomas-og-inger-i-efstu-saetum-n-listans/'),
    'Anna Runólfsdóttir': ('Anna Runólfsdóttir er verkfræðingur og bóndi í Rangárþingi eystra og er á 3. sæti NRE-listans í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tomas-og-inger-i-efstu-saetum-n-listans/'),
    'Guðni Ragnarsson': ('Guðni Ragnarsson er ökukennari í Rangárþingi eystra og er á 4. sæti NRE-listans í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tomas-og-inger-i-efstu-saetum-n-listans/'),
    'Guðmundur Ólafsson': ('Guðmundur Ólafsson er bóndi í Rangárþingi eystra og er á 5. sæti NRE-listans í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tomas-og-inger-i-efstu-saetum-n-listans/'),

    # === RTY (Rangárþing ytra) ===
    # D-listi
    'Ingvar Pétur Guðbjörnsson': ('Ingvar Pétur Guðbjörnsson er upplýsingafulltrúi og sveitarstjórnarfulltrúi í Rangárþingi ytra og leiðir D-listann í sveitarstjórnarkosningum 2026; hann þjónaði sem aðstoðarmaður iðnaðarráðherra 2013–2017.', 'https://xd.is/ingvar-p-gudbjornsson/'),
    'Guðmar Aubertsson': ('Guðmar Aubertsson er dýralæknir í Rangárþingi ytra og er á 2. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/05/fullskipadur-frambodslisti-i-rangarthingi-ytra/'),
    'Þröstur Sigurðsson': ('Þröstur Sigurðsson er framkvæmdastjóri í Rangárþingi ytra og er á 3. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/05/fullskipadur-frambodslisti-i-rangarthingi-ytra/'),
    'Sóley Margeirsdóttir': ('Sóley Margeirsdóttir er íþróttavísindamaður og grunnskólakennari í Rangárþingi ytra og er á 4. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/05/fullskipadur-frambodslisti-i-rangarthingi-ytra/'),
    'Gyða Árný Helgadóttir': ('Gyða Árný Helgadóttir er framkvæmdastjóri í Rangárþingi ytra og er á 5. sæti D-listans í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/05/fullskipadur-frambodslisti-i-rangarthingi-ytra/'),

    # RYA-listi (Á-listinn)
    'Eggert Valur Guðmundsson': ('Eggert Valur Guðmundsson er sjálfstætt starfandi og leiðir Á-listann í Rangárþingi ytra í sveitarstjórnarkosningum 2026; hann hefur þjónað í sveitarstjórn í fimm kjörtímabil frá árinu 1998.', 'https://alisti.is/frambjodendur/'),
    'Margrét Harpa Guðsteinsdóttir': ('Margrét Harpa Guðsteinsdóttir er bóndi í Lambhaga og sveitarstjórnarfulltrúi í Rangárþingi ytra og er á 2. sæti Á-listans í sveitarstjórnarkosningum 2026.', 'https://alisti.is/frambjodendur/'),
    'Erla Sigríður Sigurðardóttir': ('Erla Sigríður Sigurðardóttir er sjúkraflutningamaður hjá Heilbrigðisstofnun Suðurlands og er á 3. sæti Á-listans í Rangárþingi ytra í sveitarstjórnarkosningum 2026.', 'https://alisti.is/frambjodendur/'),
    'Viðar Már Þorsteinsson': ('Viðar Már Þorsteinsson er tæknimaður og er á 4. sæti Á-listans í Rangárþingi ytra í sveitarstjórnarkosningum 2026.', 'https://alisti.is/frambjodendur/'),
    'Eiríkur Vilhelm Sigurðarson': ('Eiríkur Vilhelm Sigurðarson er sveitarstjóraefni Á-listans í Rangárþingi ytra í sveitarstjórnarkosningum 2026; hann hefur unnið sem markaðs- og kynningarfulltrúi sveitarfélagsins.', 'https://www.sunnlenska.is/frettir/a-listinn-samthykktur-og-eirikur-kynntur-sem-sveitarstjoraefni/'),

    # === RVK (Reykjavík - 4 candidates) ===
    'Andrea Edda Guðlaugsdóttir': ('Andrea Edda Guðlaugsdóttir er hagfræðinemi og er á 5. sæti B-listans (Framsóknarflokks) í borgarstjórnarkosningum í Reykjavík 2026.', 'https://www.framsokn.is/blog/frambodslisti-framsoknar-i-reykjavik-samthykktur'),
    'Jón L. Árnason': ('Jón L. Árnason er framkvæmdastjóri lífeyrissjóðsins Lífsverks og er á 5. sæti G-listans (Góðan daginn) í borgarstjórnarkosningum í Reykjavík 2026; hann varð heimsmeistari í skák undir 17 ára aldri árið 1977.', 'https://gdf.is/frambodslistinn'),
    'Hannes Pétursson': ('Hannes Pétursson er verslunarmaður og er á 3. sæti J-listans (Sósíalistaflokks Íslands) í borgarstjórnarkosningum í Reykjavík 2026.', 'https://www.mbl.is/frettir/innlent/2026/04/07/frambodslisti_sosialistaflokks_islands_i_borginni/'),
    'Kristín Kolbrún Kolbeinsdóttir': ('Kristín Kolbrún Kolbeinsdóttir er kennari og uppeldisráðgjafi og er á 2. sæti M-listans (Miðflokksins) í borgarstjórnarkosningum í Reykjavík 2026.', 'https://midflokkurinn.is/sveitarstjornarkosningar-2026/reykjavik'),

    # === SDV (Súðavíkurhreppur) ===
    # FJL-listi (Fjarðarlistinn)
    'Kristján Rúnar Kristjánsson': ('Kristján Rúnar Kristjánsson er verktaki og oddviti Súðavíkurhrepps og leiðir Fjarðalistann í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/sudavik-oddvitinn-leidir-fjardalistann/'),
    'Ingibjörg Ásdís Björnsdóttir': ('Ingibjörg Ásdís Björnsdóttir er á 2. sæti Fjarðalistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'Finnur Jónsson': ('Finnur Jónsson er á 3. sæti Fjarðalistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'María Lovísa Danium': ('María Lovísa Danium er á 4. sæti Fjarðalistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'Jónas Haukur Jónbjörnsson': ('Jónas Haukur Jónbjörnsson er á 5. sæti Fjarðalistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),

    # FTL-listi (Framtíðarlistinn)
    'Kjartan Geir Karlsson': ('Kjartan Geir Karlsson leiðir Framtíðarlistann í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'Birta Lind Garðarsdóttir': ('Birta Lind Garðarsdóttir er á 2. sæti Framtíðarlistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'Jónína Margrét Guðmundsdóttir': ('Jónína Margrét Guðmundsdóttir er á 3. sæti Framtíðarlistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'Jónþór Eiríksson': ('Jónþór Eiríksson er á 4. sæti Framtíðarlistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),
    'Egill Bjarni Vikse Helgason': ('Egill Bjarni Vikse Helgason er á 5. sæti Framtíðarlistans í Súðavíkurhreppi í sveitarstjórnarkosningum 2026.', 'https://www.sudavik.is/is/frettir/tvo-frambod-i-sudavikurhreppi'),

    # === SEL (Seltjarnarnes) ===
    # D-listi
    'Þór Sigurgeirsson': ('Þór Sigurgeirsson er bæjarstjóri Seltjarnarness og leiðir D-listann í sveitarstjórnarkosningum 2026; hann er menntaður í sölu og markaðsmálum og hefur þjónað sem bæjarstjóri frá 2022.', 'https://www.seltjarnarnes.is/is/ibuar/frettir/thor-sigurgeirsson-nyr-baejarstjori-a-seltjarnarnesi'),
    'Elísabet Ingunn Einarsdóttir': ('Elísabet Ingunn Einarsdóttir er framkvæmdastjóri og er á 2. sæti D-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/02/frambodslisti-sjalfstaedisflokksins-a-seltjarnarnesi-2/'),
    'Magnús Benediktsson': ('Magnús Benediktsson er hagfræðingur og er á 3. sæti D-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/02/frambodslisti-sjalfstaedisflokksins-a-seltjarnarnesi-2/'),
    'Björn Jóhannesson': ('Björn Jóhannesson er hagfræðingur og er á 4. sæti D-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/02/frambodslisti-sjalfstaedisflokksins-a-seltjarnarnesi-2/'),
    'Lárus Gunnarsson': ('Lárus Gunnarsson er forstöðumaður og er á 5. sæti D-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/02/frambodslisti-sjalfstaedisflokksins-a-seltjarnarnesi-2/'),

    # M-listi
    'Skafti Harðarson': ('Skafti Harðarson er framkvæmdastjóri og leiðir M-listann (Miðflokksins) á Seltjarnarnesi í sveitarstjórnarkosningum 2026; hann er fyrsti oddviti Miðflokksins á Seltjarnarnesi.', 'https://www.ruv.is/frettir/innlent/2026-04-09-skafti-fyrsti-oddviti-midflokksins-a-seltjarnarnesi-472317'),
    'Þóra Sif Friðriksdóttir': ('Þóra Sif Friðriksdóttir er viðskiptafræðingur og er á 2. sæti M-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://midflokkurinn.is/sveitarstjornarkosningar-2026/seltjarnarnes'),
    'Guðrún Jónsdóttir': ('Guðrún Jónsdóttir er grunnskólakennari og er á 3. sæti M-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://midflokkurinn.is/sveitarstjornarkosningar-2026/seltjarnarnes'),
    'Hannes Tryggvi Hafstein': ('Hannes Tryggvi Hafstein er framkvæmdastjóri og er á 4. sæti M-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://midflokkurinn.is/sveitarstjornarkosningar-2026/seltjarnarnes'),
    'Jóhanna Sigríður Sveinsdóttir': ('Jóhanna Sigríður Sveinsdóttir er mannauðs- og gæðastjóri og er á 5. sæti M-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://midflokkurinn.is/sveitarstjornarkosningar-2026/seltjarnarnes'),

    # SCS-listi
    'Kristinn Ólafsson': ('Kristinn Ólafsson er stjórnandi og ráðgjafi og leiðir SCS-listann (Samfylkingar, Viðreisnar og óháðra) á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://www.mbl.is/frettir/innlent/2026/03/08/kristinn_leidir_sameiginlegt_frambod_a_nesinu/'),
    'Sigurþóra Bergsdóttir': ('Sigurþóra Bergsdóttir er framkvæmdastjóri og fyrrverandi varaþingmaður Samfylkingar og er á 2. sæti SCS-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://www.althingi.is/altext/cv/is/?nfaerslunr=1543'),
    'Helgi Steinar Helgason': ('Helgi Steinar Helgason er arkitekt og er á 3. sæti SCS-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://www.mbl.is/frettir/innlent/2026/03/08/kristinn_leidir_sameiginlegt_frambod_a_nesinu/'),
    'Auður Halla Rögnvaldsdóttir': ('Auður Halla Rögnvaldsdóttir er háskólanemi og er á 4. sæti SCS-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://www.mbl.is/frettir/innlent/2026/03/08/kristinn_leidir_sameiginlegt_frambod_a_nesinu/'),
    'Egill Ö. Hermannsson': ('Egill Ö. Hermannsson er sérfræðingur og er á 5. sæti SCS-listans á Seltjarnarnesi í sveitarstjórnarkosningum 2026.', 'https://www.mbl.is/frettir/innlent/2026/03/08/kristinn_leidir_sameiginlegt_frambod_a_nesinu/'),
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
