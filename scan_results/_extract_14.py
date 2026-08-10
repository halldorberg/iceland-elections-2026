# -*- coding: utf-8 -*-
import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
from html.parser import HTMLParser

class S(HTMLParser):
    def __init__(s):
        super().__init__()
        s.txt=[]
        s.skip=0
    def handle_starttag(s,t,a):
        if t in ('script','style','noscript'): s.skip+=1
    def handle_endtag(s,t):
        if t in ('script','style','noscript') and s.skip>0: s.skip-=1
    def handle_data(s,d):
        if not s.skip: s.txt.append(d)

def text(path):
    raw=open(path,'rb').read()
    m=re.search(rb'charset=["\']?([\w-]+)',raw[:3000])
    enc='utf-8'
    if m:
        cand=m.group(1).decode('ascii','ignore').lower()
        if cand in ('iso-8859-1','windows-1252','latin1','latin-1','iso-8859-15'):
            enc=cand
    try:
        h=raw.decode(enc)
    except:
        h=raw.decode('iso-8859-1','replace')
    sp=S(); sp.feed(h)
    return re.sub(r'\s+',' ',' '.join(sp.txt))

CACHE = r'F:\Claude Projects\iceland-elections\scan_results\source_cache'
manifest = json.load(open(os.path.join(CACHE,'_manifest.json'),encoding='utf-8'))

def fetch(url):
    m = manifest.get(url)
    if m and m.get('status') == 200:
        return text(os.path.join(CACHE, m['file']))
    return None

# Source URLs to extract
urls = [
    'https://www.feykir.is/is/frettir/listi-midflokksins-i-skagafirdi',
    'https://www.facebook.com/HrossaraektarbuidTunguhals2/',
    'https://midflokkurinn.is/yfir-milljon-a-dag-vid-getum-gert-betur',
    'https://www.skagafjordur.is/is/frettir/auglysing-um-fram-komin-frambod-vegna-sveitarstjornarkosninga-16-mai-2026',
    'https://www.sunnlenska.is/frettir/audbjorg-saemd-falkaordunni/',
    'https://www.byggdastofnun.is/is/verkefni/brothaettar-byggdir/skaftarhreppur',
    'https://www.kbs.is/is/skolinn/starfsmenn',
    'https://www.visir.is/g/20161024935d',
    'https://www.sandgerdisskoli.is/is/starfsfolk',
    'https://kosningasaga.wordpress.com/2026/03/04/frambodslisti-framsoknar-og-ohadra-i-sudurnesjabae/',
    'https://www.vf.is/frettir/hvar-bua-thau-sem-aetla-ad-gaeta-hagsmuna-ibua-i-sudurnesjabae',
    'https://www.sudurnesjabaer.is/is/moya/news/frambodslistar-i-sveitarstjornarkosningum',
    'https://gamla.mannlif.is/frettir/jon-kristinn-snaeholm-um-astina-sjalfstaedisflokkinn-og-ukrainu-vaknadi-halflamadur-haegra-megin/',
    'https://www.mannlif.is/veftv/mannlifid-jon-kristinn-snaeholm/',
    'https://kosningasaga.wordpress.com/2026/02/27/einar-jon-haettir-i-sudurnesjabae/',
    'https://kosningasaga.wordpress.com/2026/03/27/frambodslisti-sjalfstaedisflokks-og-ohadra-i-sudurnesjabae/',
    'https://vatnsidnadur.net/2022/08/24/arnar-geir-gestsson/',
    'https://www.skolamatur.is/',
    'https://midflokkurinn.is/midflokksdeild-sudurnesjabaejar-stofnud',
    'https://xs.is/sveitarstjornarfolk',
    'https://www.sudurnesjabaer.is/is/stjornsysla/mannaudur/starfsmenn',
    'https://www.husavik.com/2026/04/thrir-listar-i-thingeyjarsveit/',
    'https://www.thingeyjarsveit.is/is/frettir-tilkynningar/thrir-frambodslistar-stadfestir-fyrir-sveitarstjornarkosningar-2026',
    'https://bb.is/2026/04/v-listi-sterkari-vesturbyggd/',
    'https://vesturbyggd.is/stjornsysla/baejarstjorn-og-nefndir/baejarstjorn/',
    'https://eyjafrettir.is/spurt-og-svarad-hannes-kristinn-fra-sjalfstaedisflokknum/',
    'https://xd.is/2026/03/31/frambodslisti-sjalfstaedisflokksins-i-vestmannaeyjum/',
    'https://eyjafrettir.is/efri-arin-skipta-mali/',
    'https://eyjafrettir.is/sterkari-grunnskoli-og-oflugri-framtid/',
]

OUT = r'F:\Claude Projects\iceland-elections\scan_results\_tmp14'
os.makedirs(OUT, exist_ok=True)
for u in urls:
    t = fetch(u)
    if t:
        # safe file name from URL last segment
        name = re.sub(r'[^a-z0-9]+','_', u.lower()).strip('_')[-100:]
        open(os.path.join(OUT, name + '.txt'),'w',encoding='utf-8').write(t)
        print('OK', name, len(t))
    else:
        print('MISS', u)
