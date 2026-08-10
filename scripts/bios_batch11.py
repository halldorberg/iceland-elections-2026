#!/usr/bin/env python3
"""Batch 11: VME (Vestmannaeyjabær), VOG (Vogar), SNF (Snæfellsbær)"""
import re

BIOS = {
    # === VME = Vestmannaeyjabær ===
    # D-listi – Sjálfstæðisflokkurinn, seat 2
    'Trausti Hjaltason': (
        'Trausti Hjaltason er áhættustjóri, fæddur og uppalinn í Vestmannaeyjum, og er á 2. sæti á D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026; hann var fyrr framkvæmdastjóri knattspyrnudeildar ÍBV.',
        'https://xd.is/2026/03/31/frambodslisti-sjalfstaedisflokksins-i-vestmannaeyjum/'
    ),
    # E-listi – Eyjalistinn, seat 2
    'Anton Örn Björnsson': (
        'Anton Örn Björnsson er grunnskólakennari við Barnaskóla Vestmannaeyja og er á 2. sæti á lista Eyjalistans í sveitarstjórnarkosningum 2026; hann leggur áherslu á menntamál og þjónustu við ungt fólk.',
        'https://eyjafrettir.is/spurt-og-svarad-anton-orn-fra-eyjalistanum/'
    ),
    # M-listi – Miðflokkurinn, seat 2
    'Sæunn Magnúsdóttir': (
        'Sæunn Magnúsdóttir er lögfræðingur og er á 2. sæti á M-lista Miðflokksins í Vestmannaeyjum í sveitarstjórnarkosningum 2026; hún hefur setið í framkvæmdar- og hafnarráði sveitarfélagsins.',
        'https://eyjafrettir.is/spurt-og-svarad-saeunn-fra-midflokknum/'
    ),

    # === VOG = Sveitarfélagið Vogar ===
    # FYRS – Fyrir samfélagið
    'Gunnar J. Helgason': (
        'Gunnar Júlíus Helgason er pípari og leiðir listann Fyrir samfélagið (FYRS) í Sveitarfélaginu Vogum í sveitarstjórnarkosningum 2026; hann þekkist vel til íþróttamála og félagslífs í sveitarfélaginu.',
        'https://www.vf.is/frettir/segir-samskiptin-i-vogum-komin-i-ruslflokk'
    ),
    'Áslaug Fjóla Magnúsdóttir': (
        'Áslaug Fjóla Magnúsdóttir starfar hjá Útfaraþjónustu Suðurnesja og er á 2. sæti á lista FYRS (Fyrir samfélagið) í Sveitarfélaginu Vogum í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    # D-listi – Sjálfstæðisflokkurinn
    'Björg Ásta Þórðardóttir': (
        'Björg Ásta Þórðardóttir er lögfræðingur og gegndi stöðu framkvæmdastjóra Sjálfstæðisflokksins árið 2025; hún lét af þeirri stöðu til að bjóða fram í heimasveit sinni Vogum og leiðir D-listann í sveitarstjórnarkosningum 2026.',
        'https://www.mbl.is/frettir/innlent/2025/11/25/akvedinn_tregi_sem_eg_finn_vid_thessa_akvordun/'
    ),
    'Guðmann Rúnar Lúðvíksson': (
        'Guðmann Rúnar Lúðvíksson er sérfræðingur hjá Landhelgisgæslunni og varabæjarfulltrúi í Sveitarfélaginu Vogum; hann er á 2. sæti á D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    # VOE – E-listinn
    'Birgir Örn Ólafsson': (
        'Birgir Örn Ólafsson er deildarstjóri og forseti bæjarstjórnar Sveitarfélagsins Voga; hann leiðir E-listann (VOE) í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    'Eva Björk Jónsdóttir': (
        'Eva Björk Jónsdóttir er deildarstjóri og bæjarfulltrúi í Sveitarfélaginu Vogum; hún er á 2. sæti á E-lista (VOE) í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    # VOL – L-listinn
    'Kristinn Björgvinsson': (
        'Kristinn Björgvinsson er verkefnastjóri og leiðir L-listann (VOL) í Sveitarfélaginu Vogum í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    'Eðvarð Atli Bjarnason': (
        'Eðvarð Atli Bjarnason er á 2. sæti á L-lista (VOL) í Sveitarfélaginu Vogum í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),

    # === SNF = Snæfellsbær ===
    # D-listi – Sjálfstæðisflokkurinn
    'Ásgeir Jónsson': (
        'Ásgeir Jónsson er bæjarstjóri Snæfellsbæjar og leiðir D-lista Sjálfstæðisflokksins í sveitarstjórnarkosningum 2026.',
        'https://island.is/v/sveitarstjornarkosningar-2026/frambodslistar-i-sveitarfeloegum'
    ),
    'Þóra Björk Þórarinsdóttir': (
        'Þóra Björk Þórarinsdóttir er kennari og er á 2. sæti á D-lista Sjálfstæðisflokksins í Snæfellsbæ í sveitarstjórnarkosningum 2026.',
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
