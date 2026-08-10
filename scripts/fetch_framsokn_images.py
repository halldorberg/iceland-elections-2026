"""Fetch Framsókn Suðurnesjabaer candidate page and extract image URLs."""
import sys, urllib.request, re
sys.stdout.reconfigure(encoding='utf-8')

PAGES = [
    ('Anton Kristinn Guðmundsson',      'https://www.framsokn.is/anton-kristinn-gudmundsson'),
    ('Magnús Sigfús Magnússon',         'https://www.framsokn.is/magnus-sigfus-magnusson'),
    ('Ólöf Ólafsdóttir',               'https://www.framsokn.is/olof-olafsdottir'),
    ('Sindri Lars Ómarsson',            'https://www.framsokn.is/sindri-lars-omarsson'),
    ('Ewa Krysztopa',                   'https://www.framsokn.is/ewa-krysztopa'),
    ('Gísli Jónatan Pálsson',          'https://www.framsokn.is/gisli-jonatan-palsson'),
    ('Óskar Helgason',                  'https://www.framsokn.is/oskar-helgason'),
    ('Þórsteina Þöll Árnadóttir',      'https://www.framsokn.is/thorsteina-tholl-arnadottir'),
    ('Guðrún Sif Pétursdóttir',        'https://www.framsokn.is/gudrun-sif-petursdottir'),
    ('Gissur Þór Grétarsson',          'https://www.framsokn.is/gissur-thor-gretarsson'),
    ('Bjarki Dagsson',                  'https://www.framsokn.is/bjarki-dagsson'),
    ('Gunnlaug María Óskarsdóttir',    'https://www.framsokn.is/gunnlaug-maria-oskarsdottir'),
    ('Róbert Páll Arason',              'https://www.framsokn.is/robert-pall-arason'),
    ('Bylgja Dröfn Olsen Jónsdóttir', 'https://www.framsokn.is/bylgja-drofn-olsen-jonsdottir'),
    ('Hallur Jónas Gunnarsson',        'https://www.framsokn.is/hallur-jonas-gunnarsson'),
    ('Guðrún Elva Friðriksdóttir',     'https://www.framsokn.is/gudrun-elva-fridriksdottir'),
    ('Haraldur Hinriksson',             'https://www.framsokn.is/haraldur-hinriksson'),
    ('Guðjón Ólafsson',                'https://www.framsokn.is/gudjon-olafsson'),
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

for name, url in PAGES:
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')

        # Look for image URLs — Squarespace/framsokn.is uses static.squarespace.com or similar
        imgs = re.findall(r'https://[^"\'>\s]+\.(?:jpg|jpeg|png|webp)(?:\?[^"\'>\s]*)?', html)
        # Filter out icons/logos — look for candidate-sized images
        candidate_imgs = [i for i in imgs if not any(x in i for x in ['logo', 'icon', 'favicon', 'sprite'])]
        # Deduplicate
        seen = set()
        unique = []
        for i in candidate_imgs:
            base = i.split('?')[0]
            if base not in seen:
                seen.add(base)
                unique.append(i)

        if unique:
            print(f'{name}:')
            for u in unique[:3]:
                print(f'  {u}')
        else:
            print(f'{name}: NO IMAGE FOUND')

    except Exception as e:
        print(f'{name}: ERROR - {e}')
