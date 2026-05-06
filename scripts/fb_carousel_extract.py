"""Drive a FB photo lightbox via Edge CDP, click 'Next items' through every
slide, capture the largest image src + its dimensions per stop, dedup.

Usage:
  python scripts/fb_carousel_extract.py <tab_id_prefix> [--max=20] [--out=...]

Tab must already be open at a FB photo lightbox URL.
"""
import argparse, json, sys, io, time, urllib.request, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import edge_cdp
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ap = argparse.ArgumentParser()
ap.add_argument('tab', help='tab id prefix')
ap.add_argument('--max', type=int, default=22)
ap.add_argument('--out', default='temp/fb_carousel')
args = ap.parse_args()

out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
seen_srcs = []
seen_set = set()
HEADERS = {'User-Agent': 'Mozilla/5.0'}

tab = edge_cdp.find_tab(args.tab)
if not tab:
    print(f'tab {args.tab} not found'); sys.exit(1)
ws = edge_cdp.attach(tab)

def grab_current():
    """Capture the largest displayed scontent img src."""
    expr = """
        (() => {
            const imgs = [...document.querySelectorAll('img')]
                .filter(i => i.src && i.src.includes('scontent') && i.naturalWidth >= 400);
            imgs.sort((a, b) => (b.naturalWidth * b.naturalHeight) - (a.naturalWidth * a.naturalHeight));
            return imgs[0] ? JSON.stringify({src: imgs[0].src, w: imgs[0].naturalWidth, h: imgs[0].naturalHeight}) : 'null';
        })()
    """
    raw = edge_cdp.evaluate(ws, expr)
    if raw == 'null' or raw is None:
        return None
    return json.loads(raw)

def click_next():
    # Prefer "Next photo" (within-set) over "Next items" (next post entirely)
    expr = """
        (() => {
            let next = [...document.querySelectorAll('[aria-label]')]
                .find(e => /^Next photo/i.test(e.getAttribute('aria-label')));
            if (!next) {
                next = [...document.querySelectorAll('[aria-label]')]
                    .find(e => /^Next/i.test(e.getAttribute('aria-label')));
            }
            if (!next) return 'no-next';
            next.click();
            return 'clicked';
        })()
    """
    return edge_cdp.evaluate(ws, expr)

for i in range(args.max):
    info = grab_current()
    if not info:
        print(f'  [{i}] no large image found')
        time.sleep(1); continue
    src = info['src']
    src_key = src.split('?')[0].split('/')[-1]
    if src_key in seen_set:
        print(f'  [{i}] DUP {src_key} (already seen — carousel wrapped)')
        break
    seen_set.add(src_key)
    seen_srcs.append((src, info['w'], info['h']))
    # Download
    try:
        req = urllib.request.Request(src, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        h = hashlib.sha256(data).hexdigest()[:10]
        ext = '.jpg'
        out_path = out_dir / f'slide_{i:02d}_{h}{ext}'
        out_path.write_bytes(data)
        print(f'  [{i}] {info["w"]}x{info["h"]}  {len(data)//1024} KB  →  {out_path.name}')
    except Exception as e:
        print(f'  [{i}] download failed: {e}')
    # Advance
    r = click_next()
    if r != 'clicked':
        print(f'  [{i}] no next button; stopping')
        break
    time.sleep(1.0)

print(f'\nTotal: {len(seen_srcs)} unique slides downloaded → {out_dir}')
