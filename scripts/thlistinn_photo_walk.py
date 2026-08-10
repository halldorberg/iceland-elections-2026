"""Walk the 14 Þ-listinn candidate photos on FB via Edge CDP, expand
each "See more", capture full caption + largest image, save to disk
and write a JSON manifest mapping photo→candidate.
"""
from __future__ import annotations
import json, sys, io, time, urllib.request, hashlib, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import edge_cdp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TAB = 'F2882071'
OUT_DIR = Path('temp/thlistinn_photos')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 14 candidate photos identified by visual inspection — fbids in posting order
PHOTO_FBIDS = [
    '1259530399630942',  # Gylfi Þorkelsson (confirmed)
    '1259530382964277',
    '1259530322964283',
    '1259530306297618',
    '1259530296297619',
    '1259530216297627',
    '1259530199630962',
    '1259530189630963',
    '1259530129630969',
    '1259530109630971',
    '1259530099630972',
    '1259530042964311',
    '1259530029630979',
    '1259530019630980',
]

tab = edge_cdp.find_tab(TAB)
ws = edge_cdp.attach(tab)
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def expand_see_more(ws):
    expr = """
        (() => {
            const btns = [...document.querySelectorAll('div[role=\"button\"], span')]
                .filter(e => /^see more$/i.test((e.innerText || '').trim()));
            if (btns.length === 0) return 'no-button';
            btns[0].click();
            return 'clicked';
        })()
    """
    return edge_cdp.evaluate(ws, expr)

def grab(ws):
    expr = """
        (() => {
            const imgs = [...document.querySelectorAll('img')]
                .filter(i => i.src && i.src.includes('scontent') && i.naturalWidth >= 600);
            imgs.sort((a, b) => (b.naturalWidth * b.naturalHeight) - (a.naturalWidth * a.naturalHeight));
            const img = imgs[0];
            return JSON.stringify({
                src: img ? img.src : null,
                w: img ? img.naturalWidth : 0,
                h: img ? img.naturalHeight : 0,
                text: document.body.innerText
            });
        })()
    """
    raw = edge_cdp.evaluate(ws, expr)
    return json.loads(raw) if raw else None

results = []
for fbid in PHOTO_FBIDS:
    url = f'https://www.facebook.com/photo.php?fbid={fbid}&set=pb.100067219820385.-2207520000&type=3'
    edge_cdp.send(ws, 'Page.navigate', {'url': url})
    time.sleep(3.5)
    expand_see_more(ws)
    time.sleep(1.0)
    data = grab(ws)
    if not data:
        print(f'  ✗ {fbid}: no data')
        continue
    img_src = data['src']
    text = data['text']
    # Extract just the caption portion: everything after "Þ-listinn\nMonth ##\n ·" up to "See more" or "All reactions"
    m = re.search(r'Þ-listinn\s*\n[^\n]+\n\s*·\s*\n([\s\S]+?)(?=\nSee more|\nAll reactions|\nLike\nComment|\Z)', text)
    caption = m.group(1).strip() if m else text[:500]
    # Download image
    img_path = None
    if img_src:
        img_data = urllib.request.urlopen(urllib.request.Request(img_src, headers=HEADERS), timeout=30).read()
        h = hashlib.sha256(img_data).hexdigest()[:10]
        # Detect ext
        if img_data[:3] == b'\xff\xd8\xff': ext = 'jpg'
        elif img_data[:8] == b'\x89PNG\r\n\x1a\n': ext = 'png'
        else: ext = 'jpg'
        img_path = OUT_DIR / f'{fbid}_{h}.{ext}'
        img_path.write_bytes(img_data)
        print(f'  ✓ {fbid} -> {img_path.name} ({len(img_data)} bytes, {data["w"]}x{data["h"]})')
    # Find candidate name in caption — first comma or first newline
    name_m = re.match(r'([^,\n]+)', caption)
    name = name_m.group(1).strip() if name_m else '?'
    print(f'    name guess: {name}')
    print(f'    caption: {caption[:150]}')
    print()
    results.append({
        'fbid': fbid,
        'name_guess': name,
        'caption': caption,
        'img_path': str(img_path) if img_path else None,
        'img_w': data['w'], 'img_h': data['h'],
        'img_src': img_src,
    })

manifest = OUT_DIR / 'manifest.json'
manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'\nWrote {len(results)} entries → {manifest}')
