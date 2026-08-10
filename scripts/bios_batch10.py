#!/usr/bin/env python3
"""Batch 10: HFJ (Hornafjörður), HGS (Hörgársveit), HMR (Hrunamannahreppur),
              HNB (Húnabyggð), HNT (Húnaþing vestra)"""
import re

BIOS = {
    # === HFJ = Sveitarfélagið Hornafjörður ===
    # B-listi – Framsókn og stuðningsmenn
    'Ingibjörg Sveinsdóttir': (
        'Ingibjörg Sveinsdóttir er atvinnurekandi og grunnskólakennari og er á 2. sæti á B-lista Framsóknar og stuðningsmanna í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/27/frambodslisti-framsoknar-og-studningsmanna-i-sveitarfelaginu-hornafirdi/'
    ),
    'Björgvin Óskar Sigurjónsson': (
        'Björgvin Óskar Sigurjónsson er byggingatæknifræðingur og bæjarfulltrúi í Sveitarfélaginu Hornafirði og er á 3. sæti á B-lista Framsóknar og stuðningsmanna í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/27/frambodslisti-framsoknar-og-studningsmanna-i-sveitarfelaginu-hornafirdi/'
    ),
    'Kolbrún Þorbjörg Björnsdóttir': (
        'Kolbrún Þorbjörg Björnsdóttir er heilsuþjálfari og rekstrarstjóri og er á 4. sæti á B-lista Framsóknar og stuðningsmanna í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/27/frambodslisti-framsoknar-og-studningsmanna-i-sveitarfelaginu-hornafirdi/'
    ),
    'Gunnar Ásgeirsson': (
        'Gunnar Ásgeirsson er innkaupastjóri og varabæjarfulltrúi í Sveitarfélaginu Hornafirði og er á 5. sæti á B-lista Framsóknar og stuðningsmanna í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/27/frambodslisti-framsoknar-og-studningsmanna-i-sveitarfelaginu-hornafirdi/'
    ),
    # D-listi – Sjálfstæðisflokkurinn
    'Gauti Árnason': (
        'Gauti Árnason er verkstjóri hjá Vegagerðinni og forseti bæjarstjórnar Sveitarfélagsins Hornafjörðar; hann leiðir D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.',
        'https://xd.is/2026/03/14/gauti-arnason-oddviti-sveitarfelagsins-hornafjardar/'
    ),
    'Hjördís Edda Olgeirsdóttir': (
        'Hjördís Edda Olgeirsdóttir er bæjarfulltrúi í Sveitarfélaginu Hornafirði og er á 2. sæti á D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.',
        'https://xd.is/2026/03/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-a-hornafirdi/'
    ),
    'Ásta Steinunn Eiríksdóttir': (
        'Ásta Steinunn Eiríksdóttir er hagfræðingur og er á 3. sæti á D-lista Sjálfstæðisflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://xd.is/2026/03/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-a-hornafirdi/'
    ),
    'Ágústa Arnardóttir': (
        'Ágústa Arnardóttir er athafnamaður og er á 4. sæti á D-lista Sjálfstæðisflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://xd.is/2026/03/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-a-hornafirdi/'
    ),
    'Sindri Ragnarsson': (
        'Sindri Ragnarsson er íþróttafræðingur og er á 5. sæti á D-lista Sjálfstæðisflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://xd.is/2026/03/27/fullskipadur-frambodslisti-sjalfstaedisflokksins-a-hornafirdi/'
    ),
    # K-listi – Kex framboð
    'Guðrún Stefanía Vopnfjörð Ingólfsdóttir': (
        'Guðrún Stefanía Vopnfjörð Ingólfsdóttir er bæjarfulltrúi og sérfræðingur í Sveitarfélaginu Hornafirði og er á 2. sæti á K-lista Kex-framboðsins í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/28/frambodslisti-kex-frambods-i-sveitarfelaginu-hornafirdi/'
    ),
    'Elías Tjörvi Halldórsson': (
        'Elías Tjörvi Halldórsson er kokkur og hjúkrunarfræðinemi og er á 3. sæti á K-lista Kex-framboðsins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/28/frambodslisti-kex-frambods-i-sveitarfelaginu-hornafirdi/'
    ),
    'Wiktoria Anna Darnowska': (
        'Wiktoria Anna Darnowska er starfsmaður í félagsþjónustu og er á 4. sæti á K-lista Kex-framboðsins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/28/frambodslisti-kex-frambods-i-sveitarfelaginu-hornafirdi/'
    ),
    'Sigrún Sigurgeirsdóttir': (
        'Sigrún Sigurgeirsdóttir er sérfræðingur og er á 5. sæti á K-lista Kex-framboðsins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/02/28/frambodslisti-kex-frambods-i-sveitarfelaginu-hornafirdi/'
    ),
    # M-listi – Miðflokkurinn
    'Reynir Ásgeirsson': (
        'Reynir Ásgeirsson er framkvæmdastjóri og leiðir M-lista Miðflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026 — í fyrsta sinn sem Miðflokkurinn býður fram í sveitarfélaginu.',
        'https://kosningasaga.wordpress.com/2026/04/03/frambodslisti-midflokksins-i-svf-hornafirdi/'
    ),
    'Stefán Freyr Jónsson': (
        'Stefán Freyr Jónsson er bóndi og slökkviliðsmaður og er á 2. sæti á M-lista Miðflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/04/03/frambodslisti-midflokksins-i-svf-hornafirdi/'
    ),
    'Herdís I Waage': (
        'Herdís Ingólfsdóttir Waage er aðstoðarskólastjóri og kennari og er á 3. sæti á M-lista Miðflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/04/03/frambodslisti-midflokksins-i-svf-hornafirdi/'
    ),
    'Erlingur Ingi Brynjólfsson': (
        'Erlingur Ingi Brynjólfsson er verksmiðjustjóri og er á 4. sæti á M-lista Miðflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/04/03/frambodslisti-midflokksins-i-svf-hornafirdi/'
    ),
    'Valur Pálsson': (
        'Valur Pálsson er rekstrarstjóri og er á 5. sæti á M-lista Miðflokksins í Sveitarfélaginu Hornafirði í sveitarstjórnarkosningum 2026.',
        'https://kosningasaga.wordpress.com/2026/04/03/frambodslisti-midflokksins-i-svf-hornafirdi/'
    ),

    # === HGS = Hörgársveit ===
    # D-listi – Sjálfstæðismenn og óháðir (nýtt framboð)
    'Árni Rúnar Örvarsson': (
        'Árni Rúnar Örvarsson er framkvæmdastjóri og leiðir D-lista sjálfstæðismanna og óháðra í Hörgársveit, sem er nýtt framboð í sveitarfélaginu, í sveitarstjórnarkosningum 2026.',
        'https://www.vikubladid.is/is/moya/news/sveitarstjornarkosningar-2026-thrir-listar-i-kjori-i-horgarsveit'
    ),
    'Katrín Olsen Björnsdóttir': (
        'Katrín Olsen Björnsdóttir er hjúkrunarfræðingur og er á 2. sæti á D-lista sjálfstæðismanna og óháðra í Hörgársveit í sveitarstjórnarkosningum 2026.',
        'https://www.vikubladid.is/is/moya/news/sveitarstjornarkosningar-2026-thrir-listar-i-kjori-i-horgarsveit'
    ),
    # HGG – G-listi Gróska
    'Sunna María Jónasdóttir': (
        'Sunna María Jónasdóttir er sveitarstjórnarfulltrúi og hönnuður og leiðir G-lista Grósku í Hörgársveit í sveitarstjórnarkosningum 2026.',
        'https://www.vikubladid.is/is/moya/news/sveitarstjornarkosningar-2026-thrir-listar-i-kjori-i-horgarsveit'
    ),
    'Róbert Fanndal Jósavinsson': (
        'Róbert Fanndal Jósavinsson er bóndi og er á 2. sæti á G-lista Grósku í Hörgársveit í sveitarstjórnarkosningum 2026.',
        'https://www.vikubladid.is/is/moya/news/sveitarstjornarkosningar-2026-thrir-listar-i-kjori-i-horgarsveit'
    ),
    # HGH – H-listi Hörgársveitar
    'Bjarki Brynjólfsson': (
        'Bjarki Brynjólfsson er lögfræðingur og leiðir H-lista Hörgársveitar í sveitarstjórnarkosningum 2026.',
        'https://www.vikubladid.is/is/moya/news/sveitarstjornarkosningar-2026-thrir-listar-i-kjori-i-horgarsveit'
    ),
    'Ásta Hafberg': (
        'Ásta Hafberg er sölu- og markaðsstjóri og er á 2. sæti á H-lista Hörgársveitar í sveitarstjórnarkosningum 2026.',
        'https://www.vikubladid.is/is/moya/news/sveitarstjornarkosningar-2026-thrir-listar-i-kjori-i-horgarsveit'
    ),

    # === HMR = Hrunamannahreppur ===
    # D-listi – Sjálfstæðismenn og óháðir
    'Jón Bjarnason': (
        'Jón Bjarnason er verktaki og bóndi í Hvítárdal og leiðir D-lista sjálfstæðismanna og óháðra í Hrunamannahreppi í sveitarstjórnarkosningum 2026.',
        'https://www.sunnlenska.is/frettir/jon-leidir-d-listann-i-hrunamannahreppi/'
    ),
    'Bjarney Vignisdóttir': (
        'Bjarney Vignisdóttir er sveitarstjórnarfulltrúi og starfar í heilbrigðis- og garðyrkjugeiranum og er á 2. sæti á D-lista sjálfstæðismanna og óháðra í Hrunamannahreppi í sveitarstjórnarkosningum 2026.',
        'https://www.sunnlenska.is/frettir/jon-leidir-d-listann-i-hrunamannahreppi/'
    ),
    # HRL – L-listinn
    'Daði Geir Samúelsson': (
        'Daði Geir Samúelsson er verkfræðingur og sveitarstjórnarfulltrúi í Hrunamannahreppi og leiðir L-listann í sveitarstjórnarkosningum 2026.',
        'https://www.linkedin.com/in/dadigeir/'
    ),
    'Rakel Ósk Kristófersdóttir': (
        'Rakel Ósk Kristófersdóttir er á 2. sæti á L-lista í Hrunamannahreppi í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),

    # === HNB = Húnabyggð ===
    # HBA – A-listi Öll saman
    'Sara Björk Þorsteinsdóttir': (
        'Sara Björk Þorsteinsdóttir er á 2. sæti á A-lista „Öll saman" í Húnabyggð í sveitarstjórnarkosningum 2026.',
        'https://www.hunabyggd.is/is/mannlif/frettir-og-vidburdir/frettir-og-auglysingar/tilkynningar-og-frettir/frambod-til-sveitarstjornarkosninga-2026'
    ),
    # B-listi – Framsókn og aðrir framfarasinnar
    'Jenný Lind Gunnarsdóttir': (
        'Jenný Lind Gunnarsdóttir er á 2. sæti á B-lista Framsóknar og annarra framfarasinna í Húnabyggð í sveitarstjórnarkosningum 2026.',
        'https://www.hunabyggd.is/is/mannlif/frettir-og-vidburdir/frettir-og-auglysingar/tilkynningar-og-frettir/frambod-til-sveitarstjornarkosninga-2026'
    ),
    # D-listi – Sjálfstæðismenn og óháðir
    'Zophonías Ari Lárusson': (
        'Zophonías Ari Lárusson er á 2. sæti á D-lista sjálfstæðismanna og óháðra í Húnabyggð í sveitarstjórnarkosningum 2026.',
        'https://www.hunabyggd.is/is/mannlif/frettir-og-vidburdir/frettir-og-auglysingar/tilkynningar-og-frettir/frambod-til-sveitarstjornarkosninga-2026'
    ),

    # === HNT = Húnaþing vestra ===
    # B-listi – Framsókn og aðrir framfarasinnar
    'Sigurður Líndal Þórisson': (
        'Sigurður Líndal Þórisson er sviðsstjóri og leiðir B-lista Framsóknar og annarra framfarasinna í Húnaþingi vestra í sveitarstjórnarkosningum 2026.',
        'https://www.hunathing.is/is/mannlif/frettir-og-auglysingar/tilkynningar-og-frettir/auglysing-um-urskurd-kjorstjornar-hunathings-vestra'
    ),
    'Nína Axelsdóttir': (
        'Nína Axelsdóttir er á 2. sæti á B-lista Framsóknar og annarra framfarasinna í Húnaþingi vestra í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    # D-listi – Sjálfstæðismenn og óháðir
    'Örn Arnarson': (
        'Örn Arnarson er framkvæmdastjóri og leiðir D-lista sjálfstæðismanna og óháðra í Húnaþingi vestra í sveitarstjórnarkosningum 2026.',
        'https://www.hunathing.is/is/mannlif/frettir-og-auglysingar/tilkynningar-og-frettir/auglysing-um-urskurd-kjorstjornar-hunathings-vestra'
    ),
    'Sigríður Ólafsdóttir': (
        'Sigríður Ólafsdóttir er á 2. sæti á D-lista sjálfstæðismanna og óháðra í Húnaþingi vestra í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    # NHV – N-listi Nýtt afl í Húnaþingi vestra
    'Viktor Ingi Jónsson': (
        'Viktor Ingi Jónsson er leiðbeinandi í grunnskóla Húnaþings vestra og varamaður í sveitarstjórn frá 2022; hann leiðir N-lista „Nýtt afl í Húnaþingi vestra" í sveitarstjórnarkosningum 2026.',
        'https://www.hunathing.is/is/viktor-ingi-jonsson'
    ),
    'Magnús Vignir Eðvaldsson': (
        'Magnús Vignir Eðvaldsson er á 2. sæti á N-lista „Nýtt afl í Húnaþingi vestra" í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
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
