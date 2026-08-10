#!/usr/bin/env python3
"""Batch 7: SST, STD, STK, SVS, THV"""
import re

BIOS = {
    # === SST (Skagaströnd) ===
    # SST.B - Framsókn og óháðir
    'Eydís Inga Sigurjónsdóttir': ('Eydís Inga Sigurjónsdóttir er deildarstjóri hjúkrunar og leiðir framboðslista Framsóknar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Guðlaugur Siggi Hannesson': ('Guðlaugur Siggi Hannesson er viðskiptalögmaður og er á 2. sæti á framboðslista Framsóknar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Sæmundur Þór Hafsteinsson': ('Sæmundur Þór Hafsteinsson er fyrrverandi sjómaður og er á 3. sæti á framboðslista Framsóknar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    # SST.S - Samfylking og óháðir
    'Ragnheiður Erla Stefánsdóttir': ('Ragnheiður Erla Stefánsdóttir er lögfræðingur og leiðir framboðslista Samfylkingar og óháðra í Skagaströnd; þetta er í fyrsta sinn sem Samfylkingin myndar lista í sveitarfélaginu.', 'https://kosningasaga.wordpress.com/2026/03/31/frambodslisti-samfylkingar-og-ohadra-a-skagastrond/'),
    'Davíð Birkir Tryggvason': ('Davíð Birkir Tryggvason er lögmaður og er á 2. sæti á framboðslista Samfylkingar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Hugrún Sif Hallgrímsdóttir': ('Hugrún Sif Hallgrímsdóttir er skólastjóri og er á 3. sæti á framboðslista Samfylkingar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Stefán Sveinsson': ('Stefán Sveinsson er sjómaður og er á 4. sæti á framboðslista Samfylkingar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Ingimar Vignisson': ('Ingimar Vignisson er trésmiður og er á 5. sæti á framboðslista Samfylkingar og óháðra í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    # SST.SKSK - K-listi
    'Ragnar Rögnvaldsson': ('Ragnar Rögnvaldsson er sjálfstætt starfandi og er á 2. sæti á K-lista í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Ástrós Elísdóttir': ('Ástrós Elísdóttir er kennari og leikhúsfræðingur og er á 3. sæti á K-lista í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Jóhann Guðbjartur Sigurjónsson': ('Jóhann Guðbjartur Sigurjónsson er frumkvöðull og er á 4. sæti á K-lista í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),
    'Halla María Þórðardóttir': ('Halla María Þórðardóttir er kennari og er á 5. sæti á K-lista í Skagaströnd í sveitarstjórnarkosningum 2026.', 'https://www.skagastrond.is/is/moya/news/sveitarstjornakosningar-2026'),

    # === STD (Strandabyggð) ===
    # STD.B - Framsókn og óháðir
    'Sigurbjörn Rafn Úlfarsson': ('Sigurbjörn Rafn Úlfarsson er framkvæmdastjóri og leiðir framboðslista Framsóknar og óháðra í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/strandabyggd-framsokn-og-ohadir-bjoda-fram/'),
    'Kristín Anna Oddsdóttir': ('Kristín Anna Oddsdóttir er grunnskólakennari og er á 2. sæti á framboðslista Framsóknar og óháðra í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/03/07/fimm-efstu-hja-framsokn-og-ohadum-i-strandabyggd/'),
    'Valgeir Örn Kristjánsson': ('Valgeir Örn Kristjánsson er trésmiður og er á 3. sæti á framboðslista Framsóknar og óháðra í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/03/07/fimm-efstu-hja-framsokn-og-ohadum-i-strandabyggd/'),
    'Ragnheiður Ingimundardóttir': ('Ragnheiður Ingimundardóttir er á 4. sæti á framboðslista Framsóknar og óháðra í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/03/07/fimm-efstu-hja-framsokn-og-ohadum-i-strandabyggd/'),
    'Röfn Friðriksdóttir': ('Röfn Friðriksdóttir er fótaaðgerðafræðingur og er á 5. sæti á framboðslista Framsóknar og óháðra í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/03/07/fimm-efstu-hja-framsokn-og-ohadum-i-strandabyggd/'),
    # STD.SBD - Strandabandalagið
    'Þorgeir Pálsson': ('Þorgeir Pálsson er hagfræðingur og oddviti Strandabyggðar; hann leiðir Strandabandalagið sem hlaut hreinn meirihluta í sveitarstjórnarkosningum 2022.', 'https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/'),
    'Grettir Örn Ásmundsson': ('Grettir Örn Ásmundsson er byggingarfulltrúi Strandabyggðar og er á 2. sæti á framboðslista Strandabandalagisins í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/'),
    'Marta Sigvaldadóttir': ('Marta Sigvaldadóttir er bóndi og varamaður í sveitarstjórn Strandabyggðar og er á 3. sæti á framboðslista Strandabandalagisins í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/'),
    'Aleksandra Pilugina': ('Aleksandra Pilugina er barþjónn og rektarkona og er á 4. sæti á framboðslista Strandabandalagisins í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/'),
    'Þórdís Karlsdóttir': ('Þórdís Karlsdóttir er dýralæknir og varamaður í sveitarstjórn Strandabyggðar og er á 5. sæti á framboðslista Strandabandalagisins í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/strandabandalagid-kynnir-frambodslistann/'),
    # STD.VGV - Vegvísir
    'Hrafnhildur Þorsteinsdóttir': ('Hrafnhildur Þorsteinsdóttir leiðir Vegvísir, nýjan framboðslista í Strandabyggð sem leggur áherslu á samvinnu og traust í uppbyggingu samfélagsins.', 'https://bb.is/2026/03/vegvisir-nyr-frambodslisti-i-strandabyggd/'),
    'Jón Örn Haraldsson': ('Jón Örn Haraldsson er á 2. sæti á framboðslista Vegvísir í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/vegvisir-nyr-frambodslisti-i-strandabyggd/'),
    'Kjartan Jónsson': ('Kjartan Jónsson er á 3. sæti á framboðslista Vegvísir í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/vegvisir-nyr-frambodslisti-i-strandabyggd/'),
    'Laufey Heiða Reynisdóttir': ('Laufey Heiða Reynisdóttir er á 4. sæti á framboðslista Vegvísir í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/vegvisir-nyr-frambodslisti-i-strandabyggd/'),
    'Andri Freyr Arnarson': ('Andri Freyr Arnarson er á 5. sæti á framboðslista Vegvísir í Strandabyggð í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/vegvisir-nyr-frambodslisti-i-strandabyggd/'),

    # === STK (Stykkishólmsbær) ===
    # STK.FLS - H-listi (Framfarasinnar)
    'Björn Ásgeir Sumarliðason': ('Björn Ásgeir Sumarliðason er lögreglumaður og leiðir H-lista framfarasinna í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://www.ruv.is/frettir/innlent/2026-04-08-logreglumadur-leidir-lista-framfarasinna-i-stykkisholmi-472188'),
    'Steinunn Ingibjörg Magnúsdóttir': ('Steinunn Ingibjörg Magnúsdóttir er framhaldsskólakennari og er á 2. sæti á H-lista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/08/h-listi-kynntur-til-leiks-i-stykkisholmi-2'),
    'Mattías Arnar Þorgrímsson': ('Mattías Arnar Þorgrímsson er skipstjóri og er á 3. sæti á H-lista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/08/h-listi-kynntur-til-leiks-i-stykkisholmi-2'),
    'Þórhildur Eyþórsdóttir': ('Þórhildur Eyþórsdóttir er grunnskólakennari og er á 4. sæti á H-lista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/08/h-listi-kynntur-til-leiks-i-stykkisholmi-2'),
    'Viktoría Líf V. Ingibergsdóttir': ('Viktoría Líf V. Ingibergsdóttir er þjónustufulltrúi í banka og er á 5. sæti á H-lista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/08/h-listi-kynntur-til-leiks-i-stykkisholmi-2'),
    # STK.IBU - Íbúalistinn
    'Rannveig Tenchi Ernudóttir': ('Rannveig Tenchi Ernudóttir er á 2. sæti á Íbúalista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://www.stykkisholmur.is/is/frettir/tvo-frambod-skiludu-frambodslistum-til-kjorstjornar'),
    'Kristján Hildibrandsson': ('Kristján Hildibrandsson er á 3. sæti á Íbúalista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://www.stykkisholmur.is/is/frettir/tvo-frambod-skiludu-frambodslistum-til-kjorstjornar'),
    'Ólöf Inga Stefánsdóttir': ('Ólöf Inga Stefánsdóttir er á 4. sæti á Íbúalista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://www.stykkisholmur.is/is/frettir/tvo-frambod-skiludu-frambodslistum-til-kjorstjornar'),
    'Skarphéðinn Berg Steinarsson': ('Skarphéðinn Berg Steinarsson er á 5. sæti á Íbúalista í Stykkishólmi í sveitarstjórnarkosningum 2026.', 'https://www.stykkisholmur.is/is/frettir/tvo-frambod-skiludu-frambodslistum-til-kjorstjornar'),

    # === SVS (Sveitarfélagið Skagafjörður) ===
    # SVS.SVSH
    'Ólafur Rúnar Ólafsson': ('Ólafur Rúnar Ólafsson er hæstaréttarlögmaður sem rekur Lögmannsstofu Norðurlands á Akureyri og hefur áður gegnt starfi oddvita í Eyjafjarðarsveit; hann er á 1. sæti á framboðslista SVSH í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', 'https://www.legalnorth.is/'),
    'Gréta María Halldórsdóttir': ('Gréta María Halldórsdóttir er á 2. sæti á framboðslista SVSH í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Eiríkur Haukur Hauksson': ('Eiríkur Haukur Hauksson er á 3. sæti á framboðslista SVSH í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Birgir Ingason': ('Birgir Ingason er á 4. sæti á framboðslista SVSH í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Dagbjört Beck': ('Dagbjört Beck er á 5. sæti á framboðslista SVSH í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    # SVS.SVSO
    'Bjarni Þór Guðmundsson': ('Bjarni Þór Guðmundsson er á 1. sæti á framboðslista SVSO í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Árný Þóra Ágústsdóttir': ('Árný Þóra Ágústsdóttir er á 2. sæti á framboðslista SVSO í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Harpa Barkardóttir': ('Harpa Barkardóttir er á 3. sæti á framboðslista SVSO í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Sigurður Halldórsson': ('Sigurður Halldórsson er á 4. sæti á framboðslista SVSO í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Svala Einarsdóttir': ('Svala Einarsdóttir er á 5. sæti á framboðslista SVSO í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    # SVS.SVSS
    'Sigríður Ingi Stefánsdóttir': ('Sigríður Ingi Stefánsdóttir er á 1. sæti á framboðslista SVSS í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Hafrún Helga Arnardóttir': ('Hafrún Helga Arnardóttir er á 2. sæti á framboðslista SVSS í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Halldóra Dögg Sigurðardóttir': ('Halldóra Dögg Sigurðardóttir er á 3. sæti á framboðslista SVSS í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Sigrún Rósa Kjartansdóttir': ('Sigrún Rósa Kjartansdóttir er á 4. sæti á framboðslista SVSS í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),
    'Elísabet Inga Ásgrímsdóttir': ('Elísabet Inga Ásgrímsdóttir er á 5. sæti á framboðslista SVSS í Sveitarfélaginu Skagafirði í sveitarstjórnarkosningum 2026.', ''),

    # === THV (Þórshafnarhreppur) ===
    # THV.THVA
    'Knútur Jónasson': ('Knútur Jónasson er á 1. sæti á framboðslista THVA í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Nanna Marteinsdóttir': ('Nanna Marteinsdóttir er á 2. sæti á framboðslista THVA í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Anna Bragadóttir': ('Anna Bragadóttir er á 3. sæti á framboðslista THVA í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Dóra Rún Kristjánsdóttir': ('Dóra Rún Kristjánsdóttir er á 4. sæti á framboðslista THVA í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Hörður Sigurðsson': ('Hörður Sigurðsson er á 5. sæti á framboðslista THVA í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    # THV.THVL
    'Freydís Anna Ingvarsdóttir': ('Freydís Anna Ingvarsdóttir er á 2. sæti á framboðslista THVL í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Snæþór Haukur Sveinbjörnsson': ('Snæþór Haukur Sveinbjörnsson er á 3. sæti á framboðslista THVL í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Snorri Már Snorrason': ('Snorri Már Snorrason er á 4. sæti á framboðslista THVL í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Jón Sverrir Sigtryggsson': ('Jón Sverrir Sigtryggsson er á 5. sæti á framboðslista THVL í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    # THV.THVN
    'Bylgja Dögg Sigurbjörnsdóttir': ('Bylgja Dögg Sigurbjörnsdóttir er á 2. sæti á framboðslista THVN í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Jónas Þórólfsson': ('Jónas Þórólfsson er á 3. sæti á framboðslista THVN í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Hermann Aðalsteinsson': ('Hermann Aðalsteinsson er á 4. sæti á framboðslista THVN í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Garðar Finnsson': ('Garðar Finnsson er á 5. sæti á framboðslista THVN í Þórshafnarhreppi í sveitarstjórnarkosningum 2026.', ''),
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
