"""Download Samfylking candidate images for Suðurnesjabaer and save locally."""
import sys, os, hashlib, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join('images', 'candidates')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def safe_url(url):
    """Percent-encode non-ASCII characters in a URL."""
    parts = urllib.parse.urlsplit(url)
    # Encode path and query separately, preserving already-encoded chars
    safe_path = urllib.parse.quote(parts.path, safe='/%')
    safe_query = urllib.parse.quote(parts.query, safe='=&,%')
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, safe_path, safe_query, parts.fragment))

# Candidate index (position) -> image URL (None = no image available)
CANDIDATES = [
    (1,  'Svavar Grétarsson',              'https://images.prismic.io/samfylkingin/afDE5MBOoF08xYHt_Svavar.png?auto=format,compress'),
    (2,  'Bergný Jóna Sævarsdóttir',       'https://images.prismic.io/samfylkingin/afDE3cBOoF08xYHs_Bergný.png?auto=format,compress'),
    (3,  'Egill Rúnar Sigurðsson',          'https://images.prismic.io/samfylkingin/afDE2MBOoF08xYHp_Egill.png?auto=format,compress'),
    (4,  'Önundur S. Björnsson',            'https://images.prismic.io/samfylkingin/afDE0MBOoF08xYHo_Önundur.png?auto=format,compress'),
    (5,  'Thelma Dís Eggertsdóttir',        "https://images.prismic.io/samfylkingin/afDExcBOoF08xYHm_ThelmaD'is.png?auto=format,compress"),
    (6,  'Bára Kristín Þórisdóttir',        'https://images.prismic.io/samfylkingin/afDEvMBOoF08xYHl_Bára.png?auto=format,compress'),
    (7,  'Agnes Helgadóttir',               'https://images.prismic.io/samfylkingin/afDEtcBOoF08xYHj_Agnes.png?auto=format,compress'),
    (8,  'Jón Þór Jónsson Hansen',          'https://images.prismic.io/samfylkingin/afDEscBOoF08xYHi_JónÞór.png?auto=format,compress'),
    (9,  'Benóný Þórhallsson',              'https://images.prismic.io/samfylkingin/afDEpsBOoF08xYHh_Benóný.png?auto=format,compress'),
    (10, 'Przemyslaw Antoni Szymajda',      'https://images.prismic.io/samfylkingin/afDEnMBOoF08xYHc_Przemyslaw.png?auto=format,compress'),
    (11, 'Magnús Orri Arnarson',            'https://images.prismic.io/samfylkingin/afDElcBOoF08xYHb_MagnúsOrri.png?auto=format,compress'),
    (12, 'Hildur Guðný Björnsdóttir',       None),
    (13, 'Guðmundur Fannar Sigurbjörnsson', 'https://images.prismic.io/samfylkingin/afDEgsBOoF08xYHP_G.Fannar.png?auto=format,compress'),
    (14, 'Sigurbjörg Ragnarsdóttir',        'https://images.prismic.io/samfylkingin/afDEd8BOoF08xYHF_Sigurbjörg.png?auto=format,compress'),
    (15, 'Jón Snævar Jónsson',              None),
    (16, 'Sigursveinn Bjarni Jónsson',      'https://images.prismic.io/samfylkingin/afDEY8BOoF08xYG8_Sigursveinn.png?auto=format,compress'),
    (17, 'Elín Frímannsdóttir',             'https://images.prismic.io/samfylkingin/afDEVsBOoF08xYG5_Elín.png?auto=format,compress'),
    (18, 'Jórunn Alda Guðmundsdóttir',     'https://images.prismic.io/samfylkingin/afDEUcBOoF08xYG4_JórunnAlda.png?auto=format,compress'),
]

results = []

for pos, name, url in CANDIDATES:
    if url is None:
        print(f'  {pos:2d}. {name}: no image')
        results.append((pos, name, None))
        continue

    try:
        encoded_url = safe_url(url)
        req = urllib.request.Request(encoded_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            content_type = resp.headers.get('Content-Type', '')

        ext = 'png' if ('png' in content_type or url.split('?')[0].lower().endswith('.png')) else 'jpg'
        fname = hashlib.md5(data).hexdigest()[:16] + '.' + ext
        fpath = os.path.join(OUTPUT_DIR, fname)

        with open(fpath, 'wb') as f:
            f.write(data)

        local_path = 'images/candidates/' + fname
        print(f'  {pos:2d}. {name}: {local_path} ({len(data)//1024}KB)')
        results.append((pos, name, local_path))

    except Exception as e:
        print(f'  {pos:2d}. {name}: ERROR - {e}')
        results.append((pos, name, None))

print()
print('=== Results ===')
for pos, name, path in results:
    print(f'  {pos:2d}. {name}: {path or "no image"}')
