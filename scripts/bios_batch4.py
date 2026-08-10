#!/usr/bin/env python3
"""Batch 4: HVG, ISF, KJO, HVF"""
import re

BIOS = {
    # === HVG (Hveragerðisbær) ===
    # B-listi (Framsóknarflokkur)
    'Marta Rut Ólafsdóttir': ('Marta Rut Ólafsdóttir er rekstrarverkfræðingur og viðskiptaþróunarstjóri sem leiðir B-listann (Framsókn) í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/marta-leidir-b-listann-i-hveragerdi/'),
    'Einar Alexander K. Haraldsson': ('Einar Alexander K. Haraldsson er varðstjóri hjá Lögreglunni á Suðurlandi og er á 2. sæti á B-lista Framsóknar í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.ruv.is/frettir/innlent/2026-03-20-marta-rut-efst-hja-framsokn-i-hveragerdi-470416'),
    'Thelma Rún Runólfsdóttir': ('Thelma Rún Runólfsdóttir er á 3. sæti á framboðslista B í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', ''),
    'Atli Örn Egilsson': ('Atli Örn Egilsson er á 4. sæti á framboðslista B í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', ''),
    'Sæbjörg L. Másdóttir': ('Sæbjörg L. Másdóttir er á 5. sæti á framboðslista B í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', ''),

    # D-listi (Sjálfstæðisflokkur)
    'Ingimar Guðmundsson': ('Ingimar Guðmundsson er sérfræðingur hjá Sambandi íslenskra sveitarfélaga, fæddur og uppalinn í Hveragerði þar sem hann býr með fjölskyldu sinni, og er sveitarstjóraefni D-listans í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/ingimar-gudmundsson-verdur-baejarstjoraefni-d-listans-i-hveragerdi/'),
    'María Rún Þorsteinsdóttir': ('María Rún Þorsteinsdóttir er ráðgjafi hjá Vinnumálastofnun og meðstofnandi CrossFit Hengil í Hveragerði og er á 2. sæti á D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/saman-byggjum-vid-samfelag/'),
    'Sigmar Karlsson': ('Sigmar Karlsson er deildarstjóri og er á 3. sæti á D-lista Sjálfstæðisflokksins í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hveragerdi/'),
    'Hjalti Helgason': ('Hjalti Helgason er múrarameistari og er á 4. sæti á D-lista Sjálfstæðisflokksins í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hveragerdi/'),
    'Karitas Róbertsdóttir': ('Karitas Róbertsdóttir er líffræðingur og er á 5. sæti á D-lista Sjálfstæðisflokksins í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/03/04/frambodslisti-sjalfstaedisflokksins-i-hveragerdi/'),

    # OKH-listi (Okkar Hveragerðis)
    'Dagný Sif Sigurbjörnsdóttir': ('Dagný Sif Sigurbjörnsdóttir er lögfræðingur og tónlistarmaður; hún er bæjarfulltrúi og varaformaður bæjarstjórnar Hveragerðisbæjar og er á 2. sæti á OKH-lista í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/okkar-hveragerdi-kynnir-lista-til-baejarstjornarkostninga-2026/'),
    'Jónas Guðnason': ('Jónas Guðnason er jarðfræðingur, eldfjallafræðingur og vatnafræðimaður og er á 3. sæti á OKH-lista (Okkar Hveragerðis) í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/okkar-hveragerdi-kynnir-lista-til-baejarstjornarkostninga-2026/'),
    'Sandra Lind Brynjardóttir': ('Sandra Lind Brynjardóttir er grunnskólakennari og deildarstjóri á stuðningsheimili fyrir börn og er á 4. sæti á OKH-lista í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/okkar-hveragerdi-kynnir-lista-til-baejarstjornarkostninga-2026/'),
    'Ívar Dagur B. Sævarsson': ('Ívar Dagur B. Sævarsson er tónlistarmaður og nemandi og er á 5. sæti á OKH-lista (Okkar Hveragerðis) í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/okkar-hveragerdi-kynnir-lista-til-baejarstjornarkostninga-2026/'),

    # S-listi (Samfylkingin og óháðir)
    'Birgitta Ragnarsdóttir': ('Birgitta Ragnarsdóttir er tollamiðlari og leiðir S-listann (Samfylkingin og óháðir) í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/kynning-a-s-listanum-i-hveragerdi/'),
    'Þorsteinn Hjartarson': ('Þorsteinn Hjartarson er fyrrverandi menntamálastjóri og er á 2. sæti á S-lista Samfylkingarinnar í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/kynning-a-s-listanum-i-hveragerdi/'),
    'Maria de Araceli Quintana': ('Maria de Araceli Quintana er dans- og sviðslistakennari og er á 3. sæti á S-lista Samfylkingarinnar í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/kynning-a-s-listanum-i-hveragerdi/'),
    'Guðmundur Benóný Baldvinsson': ('Guðmundur Benóný Baldvinsson er vörugeymslumaður og er á 4. sæti á S-lista Samfylkingarinnar í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/kynning-a-s-listanum-i-hveragerdi/'),
    'Berglind Ósk Guttormsdóttir': ('Berglind Ósk Guttormsdóttir er ferðaleiðsögumaður og er á 5. sæti á S-lista Samfylkingarinnar í Hveragerðisbæ í sveitarstjórnarkosningum 2026.', 'https://www.dfs.is/frettir/kosningar/kynning-a-s-listanum-i-hveragerdi/'),

    # === ISF (Ísafjarðarbær) ===
    # B-listi (Framsókn og óháðir)
    'Elísabet Samúelsdóttir': ('Elísabet Samúelsdóttir er fjármálastjóri og er á 2. sæti á B-lista Framsóknar og óháðra í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Stefán Hannibal Hafberg': ('Stefán Hannibal Hafberg er sjávarútvegsvísindamaður og er á 3. sæti á B-lista Framsóknar og óháðra í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Tinna Rún Snorradóttir': ('Tinna Rún Snorradóttir er verkfræðingur og er á 4. sæti á B-lista Framsóknar og óháðra í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Elísabet Margrét Jónasdóttir': ('Elísabet Margrét Jónasdóttir er bóndi og er á 5. sæti á B-lista Framsóknar og óháðra í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),

    # C-listi (Viðreisn)
    'Magnús Einar Magnússon': ('Magnús Einar Magnússon er skrifstofustjóri og málmsmíðamaður og er á 3. sæti á C-lista Viðreisnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Arnheiður Steinþórsdóttir': ('Arnheiður Steinþórsdóttir er sagnfræðingur og bókasafnsfræðingur og er á 4. sæti á C-lista Viðreisnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Valur Richter': ('Valur Richter er pípur, trésmiður og meindýraeyðir og er á 5. sæti á C-lista Viðreisnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),

    # D-listi (Sjálfstæðisflokkur)
    'Jónas Þór Birgisson': ('Jónas Þór Birgisson er lyfjafræðingur sem hefur starfað á apóteki á Ísafirði síðan árið 2000 og leiðir D-listann (Sjálfstæðisflokkur) í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/02/isafjardarbaer-jonas-thor-i-efsta-saeti/'),
    'Þóra Marý Arnórsdóttir': ('Þóra Marý Arnórsdóttir er deildarstjóri þjónustu við fatlaða hjá Ísafjarðarbæ og er á 2. sæti á D-lista Sjálfstæðisflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Martha Kristín Pálmadóttir': ('Martha Kristín Pálmadóttir er fjarnámsstjóri og er á 3. sæti á D-lista Sjálfstæðisflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Grétar Örn Eiríksson': ('Grétar Örn Eiríksson er verkefnastjóri og er á 4. sæti á D-lista Sjálfstæðisflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Þorvaldur Óli Ragnarsson': ('Þorvaldur Óli Ragnarsson er endurskoðunarsérfræðingur og er á 5. sæti á D-lista Sjálfstæðisflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),

    # M-listi (Miðflokkurinn)
    'Sævar Óli Hjörvarsson': ('Sævar Óli Hjörvarsson er iðnaðarmaður og leiðir M-listann (Miðflokkurinn) í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/04/isafjardarbaer-saevar-oli-efstur-a-lista-midflokksins/'),
    'Jón Auðun Auðunarson': ('Jón Auðun Auðunarson er verkefnastjóri og er á 2. sæti á M-lista Miðflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Þorbjörn Halldór Jóhannesson': ('Þorbjörn Halldór Jóhannesson er bóndi og er á 3. sæti á M-lista Miðflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Karlotta Dúfa Markan': ('Karlotta Dúfa Markan er verkefnastjóri og er á 4. sæti á M-lista Miðflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),
    'Hákon Sturla Unnsteinsson': ('Hákon Sturla Unnsteinsson er bóndi og er á 5. sæti á M-lista Miðflokksins í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://www.isafjordur.is/is/stjornsysla/stjornsyslan/kosningar-2026'),

    # S-listi (Samfylkingin)
    'Svanfríður Guðrún Bergvinsdóttir': ('Svanfríður Guðrún Bergvinsdóttir er viðskiptafræðinemi og formaður ASÍ-UNG og leiðir S-listann (Samfylkingin) í Ísafjarðarbæ í sveitarstjórnarkosningum 2026; þetta er í fyrsta skipti í 24 ár sem Samfylkingin keppir undir eigin merki í sveitarfélaginu.', 'https://xs.is/frettir/2026/04/frambodslisti-samfylkingarinnar-i-isafjardarbae'),
    'Helgi Karl Guðmundsson': ('Helgi Karl Guðmundsson er rafmagnsverkfræðingur og er á 2. sæti á S-lista Samfylkingarinnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://xs.is/frettir/2026/04/frambodslisti-samfylkingarinnar-i-isafjardarbae'),
    'Finney Rakel Árnadóttir': ('Finney Rakel Árnadóttir er aðstoðarskólastjóri í Ísafirði og er á 3. sæti á S-lista Samfylkingarinnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://xs.is/frettir/2026/04/frambodslisti-samfylkingarinnar-i-isafjardarbae'),
    'Sigurður Jón Hreinsson': ('Sigurður Jón Hreinsson er vélaverkfræðingur og er á 4. sæti á S-lista Samfylkingarinnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://xs.is/frettir/2026/04/frambodslisti-samfylkingarinnar-i-isafjardarbae'),
    'Hrafnhildur Hrönn Óðinsdóttir': ('Hrafnhildur Hrönn Óðinsdóttir er stjórnmálafræðingur og er á 5. sæti á S-lista Samfylkingarinnar í Ísafjarðarbæ í sveitarstjórnarkosningum 2026.', 'https://xs.is/frettir/2026/04/frambodslisti-samfylkingarinnar-i-isafjardarbae'),

    # === KJO (Kjósarhreppur) ===
    'Sigurður Gunnar Sigurðsson': ('Sigurður Gunnar Sigurðsson er á 1. sæti á framboðslista KJA í Kjósarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Guðrún Björk Guðmundsdóttir': ('Guðrún Björk Guðmundsdóttir er á 2. sæti á framboðslista KJA í Kjósarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Þorsteinn Freyr Þorsteinsson': ('Þorsteinn Freyr Þorsteinsson er á 3. sæti á framboðslista KJA í Kjósarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Helga Rún Helgadóttir': ('Helga Rún Helgadóttir er á 4. sæti á framboðslista KJA í Kjósarhreppi í sveitarstjórnarkosningum 2026.', ''),
    'Kristján Óskar Kristjánsson': ('Kristján Óskar Kristjánsson er á 5. sæti á framboðslista KJA í Kjósarhreppi í sveitarstjórnarkosningum 2026.', ''),

    # === HVF (Hvalfjarðarsveit) ===
    'Sigurður Örn Sigurðsson': ('Sigurður Örn Sigurðsson er á 1. sæti á framboðslista HVA í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Þóra Björk Þórðardóttir': ('Þóra Björk Þórðardóttir er á 2. sæti á framboðslista HVA í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Gunnar Páll Gunnarsson': ('Gunnar Páll Gunnarsson er á 3. sæti á framboðslista HVA í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Guðrún Sigríður Guðnadóttir': ('Guðrún Sigríður Guðnadóttir er á 4. sæti á framboðslista HVA í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Jónas Freyr Jónasson': ('Jónas Freyr Jónasson er á 5. sæti á framboðslista HVA í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Ragnheiður Sigríður Ragnarsdóttir': ('Ragnheiður Sigríður Ragnarsdóttir er á 1. sæti á framboðslista HVB í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Þorsteinn Óskar Þorsteinsson': ('Þorsteinn Óskar Þorsteinsson er á 2. sæti á framboðslista HVB í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Sigrún Björk Sigurjónsdóttir': ('Sigrún Björk Sigurjónsdóttir er á 3. sæti á framboðslista HVB í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Magnús Freyr Magnússon': ('Magnús Freyr Magnússon er á 4. sæti á framboðslista HVB í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
    'Elín Helga Einarsdóttir': ('Elín Helga Einarsdóttir er á 5. sæti á framboðslista HVB í Hvalfjarðarsveit í sveitarstjórnarkosningum 2026.', ''),
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
