#!/usr/bin/env python3
"""Batch 8: BBD (Borgarbyggð), BLV (Bolungarvík), BSG (Bláskógabyggð), DVB (Dalvíkurbyggð)"""
import re

BIOS = {
    # === BBD (Borgarbyggð) ===
    # B = Framsóknarflokkur
    'Sonja Lind Eyglóardóttir': ('Sonja Lind Eyglóardóttir er lögfræðingur og fyrrverandi verkefnastjóri þingflokks Framsóknarflokksins; hún er formaður Framsóknarfélags Borgarfjarðar og Mýra og er á 2. sæti á framboðslista Framsóknarflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://www.mbl.is/frettir/innlent/2023/01/24/sonja_lind_verkefnastjori_thingflokks_framsoknar/'),
    'Jón Eiríkur Einarsson': ('Jón Eiríkur Einarsson er bóndi og fyrrverandi oddviti Skorradalshrepps; hann er á 3. sæti á framboðslista Framsóknarflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/02/frambodslisti-framsoknar-i-borgarbyggd/'),
    'Guðdís Jónsdóttir': ('Guðdís Jónsdóttir er bóndi og ritari grunnskóla á Borgarnesi; hún er á 4. sæti á framboðslista Framsóknarflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/02/frambodslisti-framsoknar-i-borgarbyggd/'),
    'Jón Theodór Jónsson': ('Jón Theodór Jónsson er á 5. sæti á framboðslista Framsóknarflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', ''),

    # BBL = Borgarbyggðarlistinn
    'Jovana Pavlović': ('Jovana Pavlović er stjórnmálafræðingur og mannfræðingur búsett á Borgarnesi; hún leiðir Borgarbyggðarlistann, lista félagshyggjufólks, í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/09/borgarbyggdarlistinn-listi-felagshyggjufolks-bydur-fram'),
    'Hermann B. Valsson': ('Hermann B. Valsson er sérfræðingur í lýðheilsu og grunnskólakennari á Hvanneyri; hann er á 2. sæti á lista Borgarbyggðarlistans í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/09/borgarbyggdarlistinn-listi-felagshyggjufolks-bydur-fram'),
    'Guðrún Vala Elísdóttir': ('Guðrún Vala Elísdóttir er framkvæmdastjóri á Borgarnesi; hún er á 3. sæti á lista Borgarbyggðarlistans í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/09/borgarbyggdarlistinn-listi-felagshyggjufolks-bydur-fram'),
    'Bjarni Bequette': ('Bjarni Bequette er framkvæmdastjóri á Borgarnesi; hann er á 4. sæti á lista Borgarbyggðarlistans í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/09/borgarbyggdarlistinn-listi-felagshyggjufolks-bydur-fram'),
    'Friðrik Aspelund': ('Friðrik Aspelund er skógfræðingur og ferðaleiðsögumaður á Hvanneyri; hann er á 5. sæti á lista Borgarbyggðarlistans í sveitarstjórnarkosningum 2026.', 'https://skessuhorn.is/2026/04/09/borgarbyggdarlistinn-listi-felagshyggjufolks-bydur-fram'),

    # D = Sjálfstæðisflokkur
    'Ragnhildur Eva Jónsdóttir': ('Ragnhildur Eva Jónsdóttir er lögfræðingur og bæjarfulltrúi; hún er á 2. sæti á framboðslista Sjálfstæðisflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/04/08/frambodslisti-sjalfstaedisflokksins-i-borgarbyggd-samthykktur/'),
    'Kristján Ágúst Magnússon': ('Kristján Ágúst Magnússon er bóndi og varabæjarfulltrúi; hann er á 3. sæti á framboðslista Sjálfstæðisflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/04/08/frambodslisti-sjalfstaedisflokksins-i-borgarbyggd-samthykktur/'),
    'Birgir Heiðar Andrésson': ('Birgir Heiðar Andrésson er framleiðslustjóri; hann er á 4. sæti á framboðslista Sjálfstæðisflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/04/08/frambodslisti-sjalfstaedisflokksins-i-borgarbyggd-samthykktur/'),
    'Svana Hrönn Jóhannsdóttir': ('Svana Hrönn Jóhannsdóttir er fjármálaráðgjafi; hún er á 5. sæti á framboðslista Sjálfstæðisflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://xd.is/2026/04/08/frambodslisti-sjalfstaedisflokksins-i-borgarbyggd-samthykktur/'),

    # M = Miðflokkur
    'Þórður Brynjarsson': ('Þórður Brynjarsson er verkamaður; hann er á 2. sæti á framboðslista Miðflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-midflokksins-i-borgarbyggd/'),
    'Tinna Rut Þórarinsdóttir': ('Tinna Rut Þórarinsdóttir er hótelstjóri og hárgreiðslumaður; hún er á 3. sæti á framboðslista Miðflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-midflokksins-i-borgarbyggd/'),
    'Helena Rós Helgadóttir': ('Helena Rós Helgadóttir er starfsmaður hjá JGR stofunni; hún er á 4. sæti á framboðslista Miðflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-midflokksins-i-borgarbyggd/'),
    'Hafsteinn Ingi Gunnarsson': ('Hafsteinn Ingi Gunnarsson er byggingameistari; hann er á 5. sæti á framboðslista Miðflokksins í Borgarbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-midflokksins-i-borgarbyggd/'),

    # === BLV (Bolungarvík) ===
    # BBK = Betri Bolungarvík
    'Kristján Jón Guðmundsson': ('Kristján Jón Guðmundsson er skrifstofustjóri og fyrrverandi fjármálastjóri hjá rækjuvinnslufélaginu Kampa ehf; hann leiðir lista Betri Bolungarvíkur í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/betri-bolungarvik-kynnir-frambodslistann/'),
    'Jóhanna Ósk Halldórsdóttir': ('Jóhanna Ósk Halldórsdóttir er svæðisstjóri; hún er á 2. sæti á lista Betri Bolungarvíkur í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/betri-bolungarvik-kynnir-frambodslistann/'),
    'Þorbergur Haraldsson': ('Þorbergur Haraldsson er bæjarfulltrúi og bókari; hann er á 3. sæti á lista Betri Bolungarvíkur í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/betri-bolungarvik-kynnir-frambodslistann/'),
    'Baldur Smári Einarsson': ('Baldur Smári Einarsson er fjármálastjóri og fyrrverandi bæjarfulltrúi; hann er á 4. sæti á lista Betri Bolungarvíkur í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/betri-bolungarvik-kynnir-frambodslistann/'),
    'Margrét Hildur Eiðsdóttir': ('Margrét Hildur Eiðsdóttir er á 5. sæti á framboðslista Betri Bolungarvíkur í sveitarstjórnarkosningum 2026.', ''),

    # MMM = Máttur meyja og manna (K-listinn)
    'Guðfinnur Ragnar Jóhannsson': ('Guðfinnur Ragnar Jóhannsson er vélaverkfræðingur og rafvirki og varabæjarfulltrúi; hann leiðir K-lista Máttar meyja og manna í Bolungarvík í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/bolungavik-mattur-manna-og-meyja-birtir-frambodslista/'),
    'Magnús Ingi Jónsson': ('Magnús Ingi Jónsson er sérfræðingur í fiskeldi hjá MAST og bæjarfulltrúi; hann er á 2. sæti á lista K-listans í Bolungarvík í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/bolungavik-mattur-manna-og-meyja-birtir-frambodslista/'),
    'Rebekka Líf Karlsdóttir': ('Rebekka Líf Karlsdóttir er tannsmiður; hún er á 3. sæti á framboðslista K-listans Máttar meyja og manna í Bolungarvík í sveitarstjórnarkosningum 2026.', 'https://bb.is/2026/03/bolungavik-mattur-manna-og-meyja-birtir-frambodslista/'),
    'Karen Arna Hannesdóttir': ('Karen Arna Hannesdóttir er á 4. sæti á framboðslista K-listans Máttar meyja og manna í Bolungarvík í sveitarstjórnarkosningum 2026.', ''),
    'Hjörtur Traustason': ('Hjörtur Traustason er á 5. sæti á framboðslista K-listans Máttar meyja og manna í Bolungarvík í sveitarstjórnarkosningum 2026.', ''),

    # === BSG (Bláskógabyggð) ===
    # BSP = Þ-listinn
    'Anna Greta Ólafsdóttir': ('Anna Greta Ólafsdóttir er leikskólastjóri og bæjarfulltrúi; hún leiðir Þ-listann í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Valdís María Smáradóttir': ('Valdís María Smáradóttir er ráðgjafi; hún er á 2. sæti á Þ-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Óli Björn Finnsson': ('Óli Björn Finnsson er grænmetisbóndi; hann er á 3. sæti á Þ-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Hildur Hálfdanardóttir': ('Hildur Hálfdanardóttir er fulltrúi í skólaráði; hún er á 4. sæti á Þ-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Stephanie Elizabeth May Langridge': ('Stephanie Elizabeth May Langridge er kennari og ferðaleiðsögumaður; hún er á 5. sæti á Þ-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),

    # BST = T-listinn
    'Helgi Kjartansson': ('Helgi Kjartansson er íþróttakennari og oddviti Bláskógabyggðar; hann leiðir T-listann í sveitarstjórnarkosningum í Bláskógabyggð 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Stefanía Hákonardóttir': ('Stefanía Hákonardóttir er verkfræðingur; hún er á 2. sæti á T-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Áslaug Alda Þórarinsdóttir': ('Áslaug Alda Þórarinsdóttir er í meistaranámi í félagsráðgjöf; hún er á 3. sæti á T-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Ísak Eyfjörð Arnarson': ('Ísak Eyfjörð Arnarson er viðskiptafræðingur; hann er á 4. sæti á T-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),
    'Kristján Einir Traustason': ('Kristján Einir Traustason er lögfræðingur í viðskiptarétti; hann er á 5. sæti á T-listanum í Bláskógabyggð í sveitarstjórnarkosningum 2026.', 'https://www.sunnlenska.is/frettir/tveir-frambodslistar-i-blaskogabyggd/'),

    # === DVB (Dalvíkurbyggð) ===
    # B = Framsóknarflokkur og óháðir
    'Monika Margrét Stefánsdóttir': ('Monika Margrét Stefánsdóttir er framkvæmdastjóri og bæjarfulltrúi; hún leiðir lista Framsóknar og óháðra í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kaffid.is/monika-leidir-lista-framsoknar-og-ohadra-i-dalvikurbyggd/'),
    'María Björk Stefánsdóttir': ('María Björk Stefánsdóttir er hjúkrunarfræðingur; hún er á 2. sæti á lista Framsóknar og óháðra í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kaffid.is/monika-leidir-lista-framsoknar-og-ohadra-i-dalvikurbyggd/'),
    'Sigvaldi Gunnlaugsson': ('Sigvaldi Gunnlaugsson er bifvélavirki; hann er á 3. sæti á lista Framsóknar og óháðra í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kaffid.is/monika-leidir-lista-framsoknar-og-ohadra-i-dalvikurbyggd/'),
    'Sigurlaug Dóra Ingimundardóttir': ('Sigurlaug Dóra Ingimundardóttir er á 4. sæti á framboðslista Framsóknar og óháðra í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', ''),
    'Kristinn Bogi Antonsson': ('Kristinn Bogi Antonsson er á 5. sæti á framboðslista Framsóknar og óháðra í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', ''),

    # D = Sjálfstæðisflokkur
    'Bessi Ragúels Víðisson': ('Bessi Ragúels Víðisson er eigandi Fincafresh; hann er á 2. sæti á framboðslista Sjálfstæðisflokksins í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-sjalfstaedisflokksins-i-dalvikurbyggd/'),
    'Auður Olga Arnarsdóttir': ('Auður Olga Arnarsdóttir er á 3. sæti á framboðslista Sjálfstæðisflokksins í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-sjalfstaedisflokksins-i-dalvikurbyggd/'),
    'Sindri Ólafsson': ('Sindri Ólafsson er á 4. sæti á framboðslista Sjálfstæðisflokksins í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', ''),
    'Birta Dís Jónsdóttir': ('Birta Dís Jónsdóttir er á 5. sæti á framboðslista Sjálfstæðisflokksins í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', ''),

    # DVA = Byggðalistinn
    'Börkur Þór Ottósson': ('Börkur Þór Ottósson leiðir Byggðalistann í Dalvíkurbyggð; hann er fyrstur á lista nýs staðbundins flokks sem tekur þátt í sveitarstjórnarkosningum 2026 í fyrsta sinn.', 'https://kosningasaga.wordpress.com/2026/04/13/frambodslisti-byggdalistans-i-dalvikurbyggd/'),
    'Erla Björk Jónsdóttir': ('Erla Björk Jónsdóttir er á 2. sæti á framboðslista Byggðalistans í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/13/frambodslisti-byggdalistans-i-dalvikurbyggd/'),
    'Elín Björk Unnarsdóttir': ('Elín Björk Unnarsdóttir er á 3. sæti á framboðslista Byggðalistans í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/13/frambodslisti-byggdalistans-i-dalvikurbyggd/'),
    'Garðar Hrafn Sigurjónsson': ('Garðar Hrafn Sigurjónsson er á 4. sæti á framboðslista Byggðalistans í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/13/frambodslisti-byggdalistans-i-dalvikurbyggd/'),
    'Tryggvi K. Guðmundsson': ('Tryggvi K. Guðmundsson er á 5. sæti á framboðslista Byggðalistans í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/13/frambodslisti-byggdalistans-i-dalvikurbyggd/'),

    # DVK = K-listinn
    'Helgi Einarsson': ('Helgi Einarsson er rekstraraðili og bæjarfulltrúi; hann leiðir K-listann í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-k-lista-dalvikurbyggdar/'),
    'Katrín Sif Ingvarsdóttir': ('Katrín Sif Ingvarsdóttir er kennari og bæjarfulltrúi; hún er á 2. sæti á K-listanum í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-k-lista-dalvikurbyggdar/'),
    'Magni Þór Óskarsson': ('Magni Þór Óskarsson er á 3. sæti á K-listanum í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', 'https://kosningasaga.wordpress.com/2026/04/11/frambodslisti-k-lista-dalvikurbyggdar/'),
    'Dominique Sigrúnardóttir': ('Dominique Sigrúnardóttir er á 4. sæti á K-listanum í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', ''),
    'Hörður Snævar Jónsson': ('Hörður Snævar Jónsson er á 5. sæti á K-listanum í Dalvíkurbyggð í sveitarstjórnarkosningum 2026.', ''),
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
